# -*- coding: utf-8 -*-
from collections import namedtuple
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.cookies.cookie_my import (
    CookieMy,
    CookieMyPackError,
    CookieMyUnpackError,
    CookieMyValueError,
    CookieMyWrapper,
)
import six


EXPECTED_VALUES = {
    'empty': 'YwA=',

    'lang_auto': 'YycCAAAA',
    'lang_ru': 'YycCAAEA',
    'lang_en': 'YycCAAMA',

    'long_session_no': 'YzYBAAA=',
    'long_session_yes': 'YzYBAQA=',
}


class CookieWrapperTestCase(unittest.TestCase):
    """
    Проверим обертку над модулем cookiemy
    """

    def setUp(self):
        self.wrapper = CookieMyWrapper()

    def test_empty(self):
        """Парсим пустую строчку без ошибок"""
        self.wrapper.unpack('')
        eq_(self.wrapper.keys(), [])

    def test_pack_empty(self):
        """Пустая кука сериализуется в непустую строчку"""
        value = self.wrapper.pack()
        eq_(value, EXPECTED_VALUES['empty'])

    def test_unpack_unicode(self):
        self.wrapper.unpack(six.text_type(EXPECTED_VALUES['empty']))

    def test_language_block(self):
        self.wrapper.language = [0, 0]  # 'auto'
        value = self.wrapper.pack()
        eq_(value, EXPECTED_VALUES['lang_auto'])

        self.wrapper.language = [0, 1]  # 'ru'
        value = self.wrapper.pack()
        eq_(value, EXPECTED_VALUES['lang_ru'])

        self.wrapper.language = [0, 3]  # 'en'
        value = self.wrapper.pack()
        eq_(value, EXPECTED_VALUES['lang_en'])

    def test_long_session_block(self):
        self.wrapper.long_session = [0]
        value = self.wrapper.pack()
        eq_(value, EXPECTED_VALUES['long_session_no'])

        self.wrapper.long_session = [1]
        value = self.wrapper.pack()
        eq_(value, EXPECTED_VALUES['long_session_yes'])

    @raises(CookieMyUnpackError)
    def test_error_unpack(self):
        """
        Если передается невалидное значение куки, обрабатывается RuntimeError-исключение из библиотеки cookiemy
        """
        self.wrapper.unpack('abc')

    @raises(CookieMyUnpackError)
    def test_error_unpack_unicode(self):
        """
        Если передается невалидное значение куки, обрабатывается RuntimeError-исключение из библиотеки cookiemy
        """
        self.wrapper.unpack(u'абв')

    @raises(CookieMyValueError)
    def test_error_value(self):
        """Блок куки не может содержать отрицательных чисел"""
        self.wrapper.language = [0, -1]

    @raises(CookieMyValueError)
    def test_error_key(self):
        """Номер блока куки не может быть отрицательным"""
        patch = mock.patch(
            'passport.backend.core.cookies.cookie_my.CookieMyBlock',
            namedtuple('CookieMyBlock', 'invalid test')._make([-1, 0])
        )
        with patch:
            # атрибут invalid будет записывать данные в блок куки с номером "-1"
            self.wrapper.invalid = [1]

    @raises(CookieMyPackError)
    def test_error_pack(self):
        """Если в процессе упаковки куки произошло RuntimeError-исключение, мы его обработаем"""
        with mock.patch.object(self.wrapper, 'cookie_to_string') as tostring_mock:
            tostring_mock.side_effect = RuntimeError
            self.wrapper.pack()


class CookieMyTestCase(unittest.TestCase):
    """
    Проверим класс для работы с кукой my
    """

    def setUp(self):
        self.cookie = CookieMy()

    def test_language(self):
        ok_(self.cookie.language is None)

        self.cookie.language = 'ru'
        value = self.cookie.pack()
        eq_(self.cookie.language, 'ru')
        eq_(value, EXPECTED_VALUES['lang_ru'])

        self.cookie.language = 'en'
        value = self.cookie.pack()
        eq_(self.cookie.language, 'en')
        eq_(value, EXPECTED_VALUES['lang_en'])

    def test_long_session(self):
        ok_(self.cookie.long_session is None)

        self.cookie.long_session = True
        value = self.cookie.pack()
        eq_(self.cookie.long_session, True)
        eq_(value, EXPECTED_VALUES['long_session_yes'])

        self.cookie.long_session = False
        value = self.cookie.pack()
        eq_(self.cookie.long_session, False)
        eq_(value, EXPECTED_VALUES['long_session_no'])
