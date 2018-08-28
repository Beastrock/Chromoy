# -*- coding: utf-8 -*-
from selenium.common.exceptions import WebDriverException


class WebDriverModuleException(WebDriverException):
    pass


class WebDriverOverMaxAttempts(WebDriverModuleException):
    """
    Количество попыток получить страницу исчерпано
    """
    message = 'WebDriverOverMaxAttempts exception'


class WebDriverNoSuchElement(WebDriverModuleException):
    """
    Не смог найти элемент на странице по айди, классу или xpath
    """
    message = 'WebDriverNoSuchElement exception'


class WebDriverConnectionError(WebDriverModuleException):
    """
    Что-то с коннектом
    """
    message = 'WebDriverConnectionExcetion exception'


class WebDriverAnotherException(WebDriverModuleException):
    """
    При таком exception надо ставить save_logs_locally true и смотреть selenium.log
    """
    message = 'WebDriverAnotherException exception'


class WebDriverAuthIsBrokenException(WebDriverModuleException):
    """
    Не удалось с полученными селекторами залогиниться на платформе
    """
    message = 'WebDriverAuthIsBrokenException exception'


class WebDriverPageIsNotReceived(WebDriverModuleException):
    """
    Не смогли получить страницу
    """
    message = 'WebDriverPageIsNotRecieved exception'
