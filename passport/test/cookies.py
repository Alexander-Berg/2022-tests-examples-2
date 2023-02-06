# coding: utf-8

import re

from nose.tools import eq_
from passport.backend.core.cookies.cookie_l import CookieL
from passport.backend.core.cookies.cookie_y import (
    PermanentCookieY,
    SessionCookieY,
)
from passport.backend.core.test.test_utils import iterdiff


_cookie_value_re = re.compile(r'^[_A-z][_A-z0-9]*=([^;]*?);')


def get_cookie_value(name, cookies):
    """
    Берёт значение куки name из списка кук

    Пример,
        get_cookie_value(
            'L',
            [
                'yp=1724404405.udn.; Domain=.yandex.ru; expires=Tue, '
                '19 Jan 2038 03:14:07 GMT; Path=/',

                'L=AlV8CX5ye0NTfHpTX157YnoCBWl6UVBx.1409044405.1002323.350330.'
                '155452b3c88e61c51221f815173a1106; Domain=.yandex.ru; '
                'expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/',
            ]
        )

        вернёт 'AlV8CX5ye0NTfHpTX157YnoCBWl6UVBx.1409044405.1002323.350330.'
               '155452b3c88e61c51221f815173a1106'.
    """
    for c in cookies:
        if c.startswith('%s=' % name):
            cookie = c
            break
    else:
        raise KeyError(name)
    m = _cookie_value_re.match(cookie)
    return m.group(1)


def assert_l_cookie_equals(cookies, uid, login):
    """
    Сравнивает uid и login с L-кукой.

    cookies -- список кук.


    Замечание

    Перед использованием подмените blackbox.lrandoms.
    """
    try:
        value = get_cookie_value('L', cookies)
    except KeyError:
        raise AssertionError('L-cookie not found')
    dict_ = CookieL().unpack(value)
    eq_(dict_['uid'], uid)
    eq_(dict_['login'], login)


def assert_yp_cookie_contain(cookies, expected_values):
    """
    Сравнивает список словарей expected_values со значениями yp-куки.

    cookies -- список кук.
    """
    try:
        value = get_cookie_value('yp', cookies)
    except KeyError:
        raise AssertionError('yp-cookie not found')
    actual_values, tail = PermanentCookieY().unpack(value)
    iterdiff(eq_)(actual_values, expected_values)
    eq_(tail, '')


def assert_ys_cookie_contain(cookies, expected_values):
    """
    Сравнивает список словарей expected_values со значениями ys-куки.

    cookies -- список кук.
    """
    try:
        value = get_cookie_value('ys', cookies)
    except KeyError:
        raise AssertionError('ys-cookie not found')
    actual_values, tail = SessionCookieY().unpack(value)
    iterdiff(eq_)(actual_values, expected_values)
    eq_(tail, '')


def assert_cookie_equals(cookies, cookie_name, expected_value):
    """
    Сравнивает значение куки cookie_name с expected_value.

    cookies -- список кук.

    Например,
        assert_cookie_equals(
            [
                'yandex_login=test_login; Domain=.yandex.ru; Path=/',

                'yp=1724404405.udn.; Domain=.yandex.ru; expires=Tue, '
                '19 Jan 2038 03:14:07 GMT; Path=/',

                'L=AlV8CX5ye0NTfHpTX157YnoCBWl6UVBx.1409044405.1002323.350330.'
                '155452b3c88e61c51221f815173a1106; Domain=.yandex.ru; '
                'expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/',
            ],
            'yandex_login',
            'test_login',
        )
        Примет истинное значение.
    """
    try:
        actual_value = get_cookie_value(cookie_name, cookies)
    except KeyError:
        raise AssertionError('%s-cookie not found' % cookie_name)
    eq_(actual_value, expected_value)
