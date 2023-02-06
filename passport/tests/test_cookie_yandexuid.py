# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.cookies.yandexuid import (
    CookieYandexuidUnpackError,
    parse_yandexuid_timestamp,
)


TEST_YANDEXUID = '3281059040000000099'


class CookieYandexuidTestCase(unittest.TestCase):
    def test_parse_timestamp_ok(self):
        eq_(parse_yandexuid_timestamp(TEST_YANDEXUID), 99)

    @raises(CookieYandexuidUnpackError)
    def test_parse_timestamp_no_cookie(self):
        parse_yandexuid_timestamp(None)

    @raises(CookieYandexuidUnpackError)
    def test_parse_timestamp_empty_cookie(self):
        parse_yandexuid_timestamp('')

    @raises(CookieYandexuidUnpackError)
    def test_parse_timestamp_bad_cookie(self):
        parse_yandexuid_timestamp('hello')

    @raises(CookieYandexuidUnpackError)
    def test_parse_timestamp_bad_timestamp(self):
        parse_yandexuid_timestamp(TEST_YANDEXUID.replace('99', 'ff'))
