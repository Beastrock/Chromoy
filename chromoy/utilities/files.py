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

