from __future__ import absolute_import, division, print_function

import sys

from sandbox.projects.yabs.sandbox_task_tracing.info import symbol_info


def test_symbol_info_function():

    def some_function():
        pass

    result = symbol_info(some_function)
    assert result['name'] == 'some_function'
    assert result['module'] == __name__
    if sys.version_info[0] >= 3:
        assert result['qualname'] == '{}.<locals>.some_function'.format(test_symbol_info_function.__name__)


def test_symbol_info_class():

    class SomeClass(object):
        pass

    result = symbol_info(SomeClass)
    assert result['name'] == 'SomeClass'
    assert result['module'] == __name__
    if sys.version_info[0] >= 3:
        assert result['qualname'] == '{}.<locals>.SomeClass'.format(test_symbol_info_class.__name__)
