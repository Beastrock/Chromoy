# -*- coding: utf-8 -*-
import logging
import socket
import traceback
from urllib.error import URLError

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.remote.webdriver import Command

from chromoy.exceptions import WebDriverConnectionError, WebDriverPageIsNotReceived
from chromoy.settings import MAX_ATTEMPTS_TO_GET_PAGE
from chromoy.utilities import processes

LOGGER = logging.getLogger('chromoy')

RemoteConnection.set_timeout(60.0)

___all___ = ["ConnectionMixin"]


class ConnectionMixin(Chrome):
    immortal_processes = []
    # все родительские процессы за всю сессию переиспользований класса
    all_session_processes = []
    init_kwargs = {}
    main_process_pid = None

    def _get(self, url):
        self.execute(Command.GET, {'url': url})

        page_source = self.page_source
        chrome_error_code = self.parse_page_to_get_chrome_error_code(page_source)

        if not page_source or (chrome_error_code is not None):
            message = "Chrome status code: __%s__" % chrome_error_code
            LOGGER.error(message)
            page_not_received_exception = WebDriverPageIsNotReceived(message)
            page_not_received_exception.message = message
            raise page_not_received_exception

        return page_source

    @staticmethod
    def parse_page_to_get_chrome_error_code(page_source):
        if isinstance(page_source, str):
            soup = BeautifulSoup(page_source, "lxml")
        else:
            soup = None

        try:
            error_code = soup.find("div",
                                   {
                                       "class": "error-code",
                                       "jscontent": "errorCode"
                                   }).text
        except (AttributeError, ValueError):
            error_code = None

        return error_code

    def get(self, url):
        """
        "Переметод" get, который ловит исключения, связанные с потерей подключения chrome driver'a.
        """

        sleep_seconds = 60
        error_name = ''
        status_code = None

        error_message = 'Can\'t connect to %s' % url

        for attempt in range(MAX_ATTEMPTS_TO_GET_PAGE):
            try:
                html_source = self._get(url)
                current_url = self.current_url
                LOGGER.info("current url: %s", current_url)
            except (TimeoutException, ConnectionRefusedError,
                    URLError, socket.timeout, WebDriverPageIsNotReceived) as connection_error:
                if connection_error:
                    error_name = connection_error.__class__.__name__

                try:
                    status_code = connection_error.message
                except AttributeError:
                    status_code = None

                LOGGER.warning(
                    'Attempt %s, got %s while getting page: %s,'
                    '\nconnection error sleep for %d sec',
                    attempt, error_name, url, sleep_seconds)
                LOGGER.exception(traceback.format_exc())
                # sleep(sleep_seconds)

                # спустя половину неудачных попыток идёт пересоздание драйвера
                if attempt == MAX_ATTEMPTS_TO_GET_PAGE / 2:
                    LOGGER.warning('still got the connection error after a half of max'
                                   ' connection attempts - redeclare driver to refresh socket')
                    self.redeclare()

            else:
                return html_source
        else:
            if status_code:
                error_message += '\n status_code: %s ' % status_code
            self.quit()
            raise WebDriverConnectionError(error_message)

    def redeclare(self):
        """
        Завершает все процессы драйвера, а затем переинициализирует родительский класс,
         создавая этим новый instance хрома
        :return:
        """
        self.kill_instance_processes()
        super().__init__(**self.init_kwargs)
        # replace main_process_pid with new driver pid
        self.main_process_pid = self.service.process.pid
        self.all_session_processes.append(self.main_process_pid)

    def quit(self):
        self.kill_all_processes()

    # noinspection PyUnusedLocal
    def kill_all_processes(self, *args):

        def is_first_iteration(num):
            return num == 0

        process_list = self.all_session_processes + self.immortal_processes

        for number, process in enumerate(process_list):
            # Обнулить список всех незавершенных процессов и пройтись по всем ним и всем
            #  когда-либо созданным ещё раз, положив актуальные незавершенные в список.
            if is_first_iteration(number):
                self.immortal_processes = []
            alive_processes = processes.kill_pid_tree(process)

            if alive_processes:
                self.immortal_processes.append(alive_processes)

    def kill_instance_processes(self):
        # убивает процесс одного инстанса, если что осталось,
        # то кладёт в immortal_processes

        alive_processes = processes.kill_pid_tree(self.main_process_pid)
        if alive_processes:
            self.immortal_processes.append(alive_processes)
            LOGGER.info(
                "There are immortal processes: {}".format(self.immortal_processes)
            )
