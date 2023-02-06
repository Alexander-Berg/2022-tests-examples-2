# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
)

from passport.test.utils import settings_context

from common.utils import *


def test_normpath():
    cases = [
        ('https://domain.com', 'https://domain.com'),
        ('https://en.domain.com', 'https://en.domain.com'),
        ('en.domain.com', 'http://en.domain.com'),
        ('ftp://en.domain.com', 'ftp://en.domain.com'),
        ('mp://en.domain.com', 'mp://en.domain.com'),
        ('domain-//', 'http://domain-//'),
    ]

    for test, expected in cases:
        yield eq_, normpath(test), expected


def test_soft_unicode():
    cases = [
        ('abc', u'abc'),
        ('тест', u'тест'),
        (u'тест', u'тест'),
    ]

    for test, expected in cases:
        yield eq_, soft_unicode(test), expected


def test_soft_str():
    cases = [
        (u'abc', 'abc'),
        (u'тест', 'тест'),
    ]

    for test, expected in cases:
        yield eq_, soft_str(test), expected


def test_get_domain():
    cases = [
        ('https://domain.com', 'domain.com'),
        ('domain.com', 'domain.com'),
        ('domain.com:5000', 'domain.com'),
    ]

    cases_with_level = [
        ('https://domain.com', 'domain.com'),
        ('en.domain.com', 'com'),
        ('https://test.domain.com:5000', 'domain.com'),
        ('https://test.domain.com:5000', 'test.domain.com'),
    ]

    for test, expected in cases:
        yield eq_, get_domain(test), expected

    for i, (test, expected) in enumerate(cases_with_level):
        yield eq_, get_domain(test, level=i), expected


def test_get_path():
    cases = [
        ('https://domain.com/test/test/?q=1', '/test/test/'),
        ('http://domain.com/abc/--', '/abc/--'),
        ('ftp://domain.com:5000/?', '/'),
        ('http://domain.com/#', '/'),
    ]

    for test, expected in cases:
        yield eq_, get_path(test), expected


def test_strip_port():
    cases = [
        ('domain.com:5000/?q=1', 'domain.com'),
        ('ftp://domain.com:0:0:0', 'ftp'),
    ]

    for test, expected in cases:
        yield eq_, strip_port(test), expected


def test_validate_url():
    cases = [
        (u'https://окна.рф:80/q=1?', 'https://xn--80atjc.xn--p1ai:80/q%3D1'),
        ('ftp://domain.com:0:0:0', 'ftp://domain.com:0:0:0'),
    ]

    for test, expected in cases:
        yield eq_, validate_url(test), expected


def test_get_safe_url():
    with settings_context(
        SAFETY={
            'client_id': 'clck',
            'key': '111',
            'url': 'https://sba.yandex.net/redirect?url={url}&client={client}&sign={sign}',
        },
    ):
        cases = [
            ('domain.com', 'https://sba.yandex.net/redirect?url=domain.com&client=clck&sign=b94c9b7ed3fdf25809725b7db2657d4a'),
            ('https://xn--80atjc.xn--p1ai:80/q%3D1', 'https://sba.yandex.net/redirect?url=https%3A%2F%2Fxn--80atjc.xn--p1ai%3A80%2Fq%253D1&client=clck&sign=b6616e97ff628fab26becba239a2140e'),
        ]

        for test, expected in cases:
            yield eq_, get_safe_url(test), expected
