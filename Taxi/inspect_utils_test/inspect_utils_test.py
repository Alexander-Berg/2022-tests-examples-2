# coding: utf-8
import inspect
import os
import re

import pytest

from dmp_suite.inspect_utils import (
    path_to_module_name,
    get_table_defined_in_module,
    callable_with_no_arguments,
    positional_parameters,
)
from test_dmp_suite.inspect_utils_test import modules


modules_path = os.path.dirname(modules.__file__)

def replace_pyc_with_py(path):
    # Эта функция нам нужна для того, чтобы при параллельном запуске тестов
    # pytest не жаловался на то, что параметры теста отличаются. Различие
    # случалось из-за того, что первый процесс компилировал модуль и при запуске второго
    # он загружался уже из .pyc файла.
    return re.sub(r'\.pyc$', '.py', path)

@pytest.mark.parametrize('module_path, module_name', [
    # test package
    (modules_path, 'test_dmp_suite.inspect_utils_test.modules'),
    (os.path.join(modules_path, 'no_exist_package'), None),
    # test module
    (replace_pyc_with_py(modules.single_defined_table.__file__),
     'test_dmp_suite.inspect_utils_test.modules.single_defined_table'),
    (os.path.join(modules_path, 'no_exist_module.py'), None)
])
def test_path_to_module_name(module_path, module_name):
    if module_name:
        assert module_name == path_to_module_name(module_path)
    else:
        with pytest.raises(ValueError):
            path_to_module_name(module_path)


def test_get_table_defined_in_module_single_defined_table():
    assert (
        get_table_defined_in_module(modules.single_defined_table)
        is modules.single_defined_table.TableA
    )


def test_get_table_defined_in_module_two_defined_tables():
    with pytest.raises(RuntimeError):
        get_table_defined_in_module(modules.two_defined_tables)


def test_get_table_defined_in_module_no_defined_tables():
    with pytest.raises(RuntimeError):
        get_table_defined_in_module(modules.no_defined_tables)


def test_get_table_defined_in_module_single_defined_table_and_import():
    assert (
        get_table_defined_in_module(modules.single_defined_table_and_import)
        is modules.single_defined_table_and_import.TableD
    )


@pytest.mark.parametrize('func, res', [
    (lambda: 51, True),
    (lambda x: 51, False),
    (lambda x, y: 51, False),
])
def test_callable_with_no_arguments(func, res):
    assert callable_with_no_arguments(func) is res


@pytest.mark.parametrize('func, args', [
    (lambda: 51, 0),
    (lambda x: 51, 1),
    (lambda x, y: 51, 2),
])
def test_positional_parameters(func, args):
    assert len(positional_parameters(func)) == args
    assert len(positional_parameters(inspect.signature(func))) == args
