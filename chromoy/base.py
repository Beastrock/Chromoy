# -*- coding: utf-8 -*-
import logging
import signal

from selenium import webdriver

from chromoy.mixins import ConnectionMixin, ParsingMixin, AuthMixin
from chromoy.utilities import processes

LOGGER = logging.getLogger('chromoy')


class Chromoy(ConnectionMixin, ParsingMixin, AuthMixin):

    def __init__(
            self,
            driver_file_path,
            cookies=None,
            debug=False,
            proxy=None,
            chrome_log_file_path=None,
            browser_window_size=(1024, 768),
            page_load_timeout=60,
            screenshot_and_source_directory=None,
            **kwargs
    ):
        """
        :param debug
        :param proxy: example of proxy arg format "socks5://proxy.gibdev.ru:10001"
        :param cookies:
        :param is_file_logging: true пишет в файл, false соотвественно.
        """
        # процессы, которые не смогли завершиться (зомби или другие зависшие процессы)
        self.immortal_processes = []
        # все родительские процессы за всю сессию переиспользований класса
        self.all_session_processes = []

        self.screenshot_and_source_directory = screenshot_and_source_directory
        self.init_kwargs = kwargs
        self.proxy = proxy
        self.is_debug_mode = debug

        if not chrome_log_file_path:
            chrome_log_file_path = '/dev/null'

        chrome_options = webdriver.ChromeOptions()

        if not debug:
            chrome_options.add_argument('--headless')

        if proxy:
            chrome_options.add_argument('--proxy-server=%s' % proxy)

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')

        self.init_kwargs = {
            "executable_path": driver_file_path,
            "chrome_options": chrome_options,
            "service_log_path": chrome_log_file_path,
            **kwargs
        }

        super().__init__(**self.init_kwargs)

        self.set_page_load_timeout(page_load_timeout)
        self.set_window_size(*browser_window_size)

        self.main_process_pid = self.service.process.pid
        self.all_session_processes.append(self.main_process_pid)
        processes.check_pid_status(self.main_process_pid)

        if cookies is not None:
            self.load_cookies_to_web_driver_cookie_jar(cookies)
