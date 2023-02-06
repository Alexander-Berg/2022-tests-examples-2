# coding=utf-8
from __future__ import unicode_literals

import datetime

import collections
import pytest

from taxi.util import dates
from taxi.core.log import tskv


@pytest.mark.parametrize('tskv_format,add_header,result_template', [
    (None, True, 'tskv\ttskv_format=\ta=b\td=5\tt=%d\tк\\=люч=знач=ение'),
    (None, False, 'a=b\td=5\tt=%d\tк\\=люч=знач=ение'),
    ('test-format-log', True,
     'tskv\ttskv_format=test-format-log\ta=b\td=5\tt=%d\tк\\=люч=знач=ение')
])
@pytest.mark.filldb(_fill=False)
def test_formatter(tskv_format, add_header, result_template):
    now = datetime.datetime.utcnow()
    d = collections.OrderedDict()
    d['a'] = 'b'
    d['d'] = 5
    d['t'] = now
    d['к=люч'] = 'знач=ение'

    if tskv_format is not None:
        result = tskv.dict_to_tskv(
            d, tskv_format=tskv_format, add_header=add_header
        )
    else:
        result = tskv.dict_to_tskv(d, add_header=add_header)

    result = result.decode('utf-8')
    assert result == result_template % dates.timestamp(now)


@pytest.mark.parametrize('data, expected_log', [
    # phones
    (
        {'phone': '+79876543210'},
        'phone=***',
    ),
    (
        {'phone_short': '+123456', 'phone_long': '+986543210987'},
        'phone_short=***\tphone_long=***',
    ),
    (
        {'list': ['+79876543210', '+79123456789']},
        'list=[u\'***\', u\'***\']',
    ),
    (
        {'val': {'a': '+7987654', 'b': '+79123456789'}},
        'val={u\'a\': u\'***\', u\'b\': u\'***\'}',
    ),
    # emails
    (
        {'value': 'my.super_box777@yandex.ru'},
        'value=***',
    ),
    (
        {'value': 'email=my.super+spam@yandex.ru;'},
        'value=email=***;',
    ),
    (
        {'value': 'send to my.super_box777@sub.yandex.ru'},
        'value=send to ***',
    ),
])
def test_clear_pd(data, expected_log):
    result = tskv.dict_to_tskv(data, add_header=False)
    result = result.decode('utf-8')
    assert result == expected_log
