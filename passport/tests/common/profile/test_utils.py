# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.api.common.profile.utils import (
    browser_grouper,
    get_host,
    parse_uatraits_bool_missing,
    probability,
    Version,
)


def test_get_host():
    hosts_parts_results = (
        (None, None, None),
        ('missing-netloc', None, ''),
        ('http://yandex.ru', None, 'yandex.ru'),
        ('http://service.yandex.ru:1000/?mode=passport', None, 'service.yandex.ru'),
        ('http://yandex.ru', 1, 'ru'),
        ('http://yandex.ru', 2, 'yandex.ru'),
        ('http://yandex.ru', 30, 'yandex.ru'),
        ('http://[123', None, None),
    )

    for host, parts, result in hosts_parts_results:
        eq_(get_host(host, parts), result)


def test_browser_grouper():
    for value, expected_count in (
        ('OperaMini 6.5', 1),
        ('OperaMini 6.6.1', 1),
        ('OperaMini 6.7', 2),
        ('OperaMini 6.7.XXX', 0),
        ('OperaMini ', 0),
        ('OperaMini', 0),
        ('  ', 0),
    ):
        count = browser_grouper(
            value,
            [
                [u'OperaMini 6.5', 1],
                [u'OperaMini 6.7', 1],
                [u'  ', 0],
            ],
        )
        eq_(count, expected_count)


def test_probability():
    for args, result in (
        ((None, None), 0),
        (
            (
                'unknown',
                [
                    ['val1', 1],
                    ['val2', 2],
                ],
            ),
            0,
        ),
        (
            (
                'val1',
                [
                    ['val1', 4],
                    ['val2', 6],
                ],
            ),
            0.4,
        ),
        (
            (
                ['v1', 'v2'],
                [
                    ['v1', 1],
                    ['v3', 1],
                ],
            ),
            0.5,
        ),
        (
            (
                ['v1', 'v2'],
                [
                    ['v1', 1],
                    ['v2', 1],
                    ['v3', 1],
                ],
            ),
            0.6667,
        ),
        (
            (
                'OperaMini 6.5',
                [
                    [u'OperaMini 6.5', 1],
                    [u'OperaMini 6.7', 1],
                ],
                browser_grouper,
            ),
            0.5,
        ),
    ):
        eq_(probability(*args), result)


def test_parse_uatraits_bool_missing():
    for value, result in (
        ('', 0),
        ('True', 1),
        ('Unknown', -1),
    ):
        eq_(parse_uatraits_bool_missing(value), result)


class VersionTestCase(unittest.TestCase):

    def test_parse(self):
        for args, result in (
            ('', None),
            ('1', Version([1])),
            ('1.2', Version([1, 2])),
            ('1.x.3', None),
        ):
            eq_(Version.parse(args), result)

    def test_compare(self):
        ok_(Version.parse('1') == Version.parse('1'))
        ok_(Version.parse('1.1') == Version.parse('1.1'))
        ok_(Version.parse('1.1') > Version.parse('1'))
        ok_(Version.parse('1.1') > Version.parse('1.0'))
        ok_(Version.parse('1') < Version.parse('2'))
        ok_(Version.parse('1.1.4') < Version.parse('1.2.1'))

    @raises(ValueError)
    def test_compare_to_other_type(self):
        Version.parse('1.1') == 1.1
