import datetime
import logging
from os import mkdir
from os.path import join, isdir
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
# noinspection PyPep8Naming
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chromoy import settings as stg
from chromoy import utilities

MAIN_LOGGER = logging.getLogger("chromoy")

___all___ = ["ParsingMixin"]


class ParsingMixin(Chrome):
    screenshot_and_source_directory = ""

    def _get_element_by(self, identify_type, value: str, multiple=False):
        """
        Берёт элемент со страницы по селекторам.

        :param By identify_type: By.ID , By.CLASS_NAME, By.CSS_SELECTOR
        :param str value: selector value
        :param bool multiple: True for getting multiple elements, False - first element
        :return: list of elements (if _multiple) /  element
        """

        type_and_value = (identify_type, value)

        wait = WebDriverWait(self, 20)  # TODO: КОНФИГ

        if not multiple:
            condition = EC.presence_of_element_located(type_and_value)
        else:
            condition = EC.presence_of_all_elements_located(type_and_value)

        try:
            element = wait.until(condition)
        except TimeoutException:
            element = None

        return element

    def get_element_by(self, identify_type, value):
        return self._get_element_by(identify_type, value)

    def get_elements_by(self, identify_type, value):
        """
        Берёт элементы со страницы по селекторам.

        :param identify_type:
        :param value:
        :return:
        """
        return self._get_element_by(identify_type, value, multiple=True)

    def click_element_and_sleep(
            self,
            value,
            identify_type=By.CSS_SELECTOR,
            sleeping=True,
            sleep_seconds=stg.DEFAULT_SLEEP_SECONDS
    ):
        """
        Кликает по элементу с указанным селектором и спит self.sleep_seconds

        :param identify_type:
        :param value:
        :param sleeping:
        :param sleep_seconds:
        :return: возвращает найденный элемент
        """

        element = self._get_element_by(identify_type, value)

        element.click()

        if sleeping:
            sleep(sleep_seconds)

        return element

    def wait_until_disappearing(
            self, value,
            identify_type=By.CSS_SELECTOR
    ):
        def driver_find_element(driver):
            return driver.find_element(identify_type, value)

        wait = WebDriverWait(self, stg.MAX_SECONDS_TO_GET_ELEMENT)

        try:
            wait.until_not(driver_find_element)
            is_disappeared = True
        except TimeoutException:
            is_disappeared = False

        return is_disappeared

    def save_error_page_information(self):
        MAIN_LOGGER.info('save error page info: make screen shot and save page source')

        if not self.screenshot_and_source_directory:
            return

        if not (isdir(self.screenshot_and_source_directory)):
            mkdir(self.screenshot_and_source_directory)

        date = str(datetime.datetime.now()).replace(' ', '_')

        self.get_screenshot_as_file(
            join(self.screenshot_and_source_directory, 'img_%s.png' % date)
        )

        utilities.files.save_file(
            self.page_source,
            join(self.screenshot_and_source_directory,
                 'page_%s.html' % date)
        )
