# -*- coding: utf-8 -*-
import logging
from os.path import exists

MAIN_LOGGER = logging.getLogger('main.log')


def save_file(data, file_path):
    with open(file_path, 'w') as file_handler:
        file_handler.write(data)


def read(file_path):
    if not exists(file_path):
        return None

    with open(file_path, 'r') as file_handler:
        return file_handler.read()


def save_sample_to_unique_logger_directory(name, file_path):
    """
    Если папка не найдена или строка None, то пишет warning в logger и не сохраняет ничего.

    :param file_path: строку, которую надо сохранить
    :param name: имя сохраняемого файла
    :return:
    """

    if exists(file_path):
        save_file(name, file_path)
        return

    raise NotADirectoryError(
        'Saving sample not performed.\nDirectory %s not found.\n' % file_path
    )
