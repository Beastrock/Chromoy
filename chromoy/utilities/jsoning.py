# -*- coding: utf-8 -*-
"""
Работа с json
"""

import json
import logging
from os.path import join

from .files import save_file

MAIN_LOGGER = logging.getLogger('main.log')


def dump(data, pretty_print=False):
    if pretty_print:
        dumped_json = json.dumps(
            data,
            ensure_ascii=False,
            sort_keys=True,
            indent=2
        )
    else:
        dumped_json = json.dumps(data, ensure_ascii=False)

    return dumped_json


def load(data):
    try:
        json_data = json.loads(data, encoding='UTF-8')
    except (json.JSONDecodeError, TypeError) as error:
        try:
            error_name = error.__name__
        except AttributeError:
            error_name = ''
        MAIN_LOGGER.error('failed to load json: %s', error_name)
        json_data = None
    return json_data


def save_to_file(
        data,
        file_path=None,
        output_directory=None,
        name='',
        pretty_print=False
):
    """
    You can pass file_path parameter OR output_directory and name parameters to function.

    notice that:
        :param data: json data
        :param file_path: absolute or relative path for json
        :param output_directory: output directory. Always is passed with name
        :param name: without ".json." prefix
        :param pretty_print: set it to True for pretty print json output
    """

    if name is None:
        name = 'undefined'
    if output_directory:
        file_path = join(output_directory, '%s.json' % name.replace(' ', '_'))

    save_file(dump(data, pretty_print=pretty_print), file_path)
