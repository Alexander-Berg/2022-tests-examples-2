# -*- coding: utf-8 -*-
import re
import sys

from django.test.utils import override_settings
import mock
from nose.tools import eq_


def set_side_effect_errors(mock_, errors):
    """
    Устанавливает заданный список ошибок в качестве поочерёдных сайд-эффектов для заданного мока.
    При исчерпании списка будет вызываться сам мок.
    """
    errors = iter(errors)

    def side_effect_func(*args, **kwargs):
        try:
            raise next(errors)
        except StopIteration:
            mock_.side_effect = None
            return mock.DEFAULT

    mock_.side_effect = side_effect_func


def with_setting_sets(*setting_sets):
    """Декоратор для Testcase. Создаёт копии класса со всеми нужными наборами настроек."""
    def decorator(cls):
        original_class_name = cls.__name__
        for i, setting_set in enumerate(setting_sets):
            new_class_name = '%s__with_setting_set_%d' % (original_class_name, i)
            decorated_class = override_settings(**setting_set)(cls)
            decorated_class.__name__ = new_class_name
            setattr(sys.modules[cls.__module__], new_class_name, decorated_class)
    return decorator


def uniq(src, filter_):
    return [i for i in src if i not in filter_]


def iter_eq(a, b, msg=''):
    if a == b:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        a_items = a.items()
        b_items = b.items()
        in_a = uniq(a_items, b_items)
        in_b = uniq(b_items, a_items)
    elif isinstance(a, (list, set, tuple)) and isinstance(b, (list, set, tuple)):
        in_a = uniq(a, b)
        in_b = uniq(b, a)
    else:
        raise AssertionError('%s%s != %s' % (msg, a, b))
    raise AssertionError('%s%s != %s\n\nIn first: %s\n\nIn second: %s' % (msg, a, b, in_a, in_b))


def parse_tskv_log_entry(logger_handler_mock, entry_index):
    call_arg = logger_handler_mock.call_args_list[entry_index]
    line = re.sub(r'^tskv\t', '', call_arg[0][0]).strip().split('\t')
    result_line = dict()
    for field in line:
        name, value = field.split('=', 1)
        result_line.update({name: value})
    return result_line


def check_tskv_log_entry(logger_handler_mock, tskv_line, entry_index=-1):
    result_line = parse_tskv_log_entry(logger_handler_mock, entry_index)
    iter_eq(result_line, tskv_line)


def assert_params_in_tskv_log_entry(logger_handler_mock, tskv_params, entry_index=-1):
    result_line = parse_tskv_log_entry(logger_handler_mock, entry_index)
    for key, value in tskv_params.items():
        eq_(result_line.get(key), value)


def check_tskv_log_entries(logger_handler_mock, tskv_lines):
    if len(tskv_lines) != logger_handler_mock.call_count:
        raise AssertionError(
            '%d tskv log entries expected, %d found:\n%s\n  vs\n%s' % (
                len(tskv_lines),
                logger_handler_mock.call_count,
                tskv_lines,
                logger_handler_mock.call_args_list,
            ),
        )  # pragma: no cover
    for index, tskv_line in enumerate(tskv_lines):
        check_tskv_log_entry(logger_handler_mock, tskv_line, entry_index=index)
