# -*- coding: utf-8 -*-
import logging

from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.remote_connection import RemoteConnection

from chromoy.utilities import jsoning

LOGGER = logging.getLogger('chromoy')

RemoteConnection.set_timeout(60.0)

___all___ = ["AuthMixin"]


class AuthMixin(Chrome):

    def login(
            self,
            login=None,
            login_selector=None,
            password=None,
            password_selector=None,
            submit_selector=None
    ):
        """
        Осуществляет логин на текущей странице.

        :param login: логин
        :param login_selector: селектор input формы, в которую вводится login
        :param password: пароль
        :param password_selector: селектор input формы, в которую вводится password
        :param submit_selector: селектор кнопки отправки формы
        :return:
        """
        if login and login_selector:
            email_field = self.find_element_by_css_selector(login_selector)
            email_field.send_keys(login)

        if password and password_selector:
            password_field = self.find_element_by_css_selector(password_selector)
            password_field.send_keys(password)

        if submit_selector:
            self.find_element_by_css_selector(submit_selector).click()
        else:
            LOGGER.info('Push enter to submit form')
            ActionChains(self).send_keys(Keys.ENTER).perform()

    def save_cookies_json_from_driver_session(self, output_directory):
        LOGGER.info('saving cookies from web driver session')
        cookies_dict = {}
        for cookie in self.get_cookies():
            cookies_dict.update({(str(cookie['name'])): str(cookie['value'])})

        jsoning.save_to_file(
            cookies_dict,
            output_directory=output_directory,
            name="cookies",
            pretty_print=True
        )

    def load_cookies_to_web_driver_cookie_jar(self, cookies):
        if isinstance(cookies, list):
            LOGGER.info('set %s cookies to web driver', len(cookies))
            for cookie in cookies:
                self.add_cookie({'name': str(cookie['name']), 'value': str(cookie['value'])})
        elif isinstance(cookies, dict):
            LOGGER.info('set %s cookies to web driver', len(cookies.keys()))
            for cookie_name, cookies_value in cookies.items():
                self.add_cookie({'name': cookie_name, 'value': cookies_value})
        else:
            LOGGER.warning('set 0 cookies to session')
