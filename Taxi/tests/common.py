# coding: utf-8

import os
import pandas as pd
from business_models.databases import greenplum
from business_models.botolib import bot
from business_models.util import data_from_file, data_to_file, change_index, Timer, get_list
from business_models.queries import queries_config, runner
from functools import wraps
import yt.wrapper as yt
import re
import pytest

__all__ = ['read_data', 'write_data', 'make_path', 'check_df', 'print_test_fails']

_DATA_PATH = 'data'
DATA_DIRECTORY = os.path.abspath(os.path.dirname(__file__)) + "/data"


def make_path(*sufficies):
    return os.path.join(DATA_DIRECTORY, *sufficies)


def check_df(df1, df2, index=None, check_dtype=False, **kwargs):
    pd.testing.assert_frame_equal(change_index(df1, index),
                                  change_index(df2, index),
                                  check_dtype=check_dtype, **kwargs)


def get_filename(filename, tests_name):
    """Собирает путь к файлу для тестов"""
    tests_name = tests_name.rstrip('.py').rstrip('.pyc')
    if '/' in tests_name:
        tests_name = tests_name.split('/')[-1]
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(cur_dir, _DATA_PATH, tests_name)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return os.path.join(directory, filename)


def read_data(tests_name, filename, determine_type=True, **kwargs):
    """Чтение файла необходимого для тестов

    :param tests_name: название теста/папки с тестами или __file__ (в папке с этим названиям сложатся данные
    :param filename: название файла с данными
    :param kwargs: передается в метод чтения data_from_file
    :return: результат работы data_from_file или None, если указанный файл не сущетвует
    """
    path = get_filename(filename, tests_name)
    if os.path.exists(path):
        return data_from_file(path, determine_type=determine_type, **kwargs)
    return None


def write_data(data, tests_name, filename, determine_type=True, **kwargs):
    """Аналогично read_data, но запись данных"""
    path = get_filename(filename, tests_name)
    return data_to_file(data, path, determine_type=determine_type, **kwargs)


def folder_subsampling(func):
    """
    Обертка создающая папку со срезом всех прод таблиц для перечисленных городов, подставляющая этот путь впрефикс для
        последующих вычислений и подчищающая за собой в конце
    :param new_base: str - путь, по которому лежат файлы для теста (в случае их наличия)
    :param remove: bool - если True, то в случае успешного прохождения теста копия данных,
        на которых он запускался удалятся. Иначе вернется путь к месту, где они хранятся
    :param cities: tuple(str) - список городов, в которых
    :param date_to: str - с какого момента начинать прогнозировать (скопирует данные так,
        как будто факт закончился перед date_to)
    :return:
    """
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        yt_new_base = kwargs.pop('new_base', None)
        gp_new_base = kwargs.pop('gp_new_base', None)
        cities = get_list(kwargs.pop('cities', ('Казань', 'Калининград', 'Минск', 'Архангельск')))
        date_to = kwargs.get('date_to', None)
        remove = kwargs.pop('remove', True)
        runner_kwargs = kwargs.pop('runner_kwargs', {})
        if yt_new_base is None:
            with Timer("Make mini version for cities {}".format(','.join(cities)), raise_exceptions=True):
                yt_new_base, gp_new_base = runner.get_small_forecast_input(cities, date_to=date_to, **runner_kwargs)
        elif gp_new_base is None:
            gp_new_base = queries_config._default_prefix['greenplum'] + '_tests'
        queries_config.set_prefix(yt_new_base)
        queries_config.set_prefix(gp_new_base, database='greenplum')
        result = func(yt_new_base, *args, **kwargs)
        queries_config.reset_prefix()
        queries_config.reset_prefix('greenplum')
        if remove:
            yt.remove('//' + yt_new_base.lstrip('/'), recursive=True)
            for table in ['_replica_normalized',
                           '_replica_hierarchy',
                           '_replica_hierarchy_with_all_agglomerations']:
                greenplum.remove(gp_new_base+table)
        return result
    return wrapped_func


def print_test_fails(filename='business_models_tests.txt'):
    i = 0
    for line in data_from_file(filename, determine_type=True).strip().split('\n'):
        if re.findall('\[gw[0-9]\] \[ [ 0-9]*%\] FAILED', line) \
            or re.findall('FAILED \[ [ 0-9]*%\]', line) \
            or 'ERROR collecting' in line:
            print(line)
            i += 1
    print(line)  # последняя строка со статусом
    print("print_test_fails detected {} errors".format(i))  # кроссчек


def reset_to_defaults():
    queries_config.reset_prefix()
    bot.enable()
