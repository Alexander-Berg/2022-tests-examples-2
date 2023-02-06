# -*- coding: utf-8 -*-
from collections import OrderedDict

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.logs import format_parameters_for_log
import pytest


@pytest.mark.parametrize(('params', 'expected'), [
        (
            OrderedDict([
                (u'foo', u'bar'),
                (u'number', 42),
                (u'empty', None),
            ]),
            u'foo=bar, number=42, empty=None',
        ),
        (
            OrderedDict([
                (u'это', u'кириллица'),
            ]),
            u'это=кириллица',
        ),
        (
            OrderedDict([
                (u'\\\t\r\n\0', 42),
            ]),
            u'\\\\' + r'\t' + r'\r' + r'\n' + r'\0=42',
        ),
    ],
)
def test__format_parameters_for_log(params, expected):
    eq_(format_parameters_for_log(params), expected)


def test__format_parameters_for_log_special():
    # https://st.yandex-team.ru/PASSP-20823
    # тест очень чувствителен к реализации passport.logging_utils.helpers.trim_message
    # чувствителен к числовым константам, которые там используются
    ok_(format_parameters_for_log({u'это': u'абв' * 1000}, trim=True))
