# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.core.language_detect import (
    get_language_number,
    LanguageData,
    LanguageDetect,
    MobileLanguageData,
)
from passport.backend.core.test.cookiemy_for_language import cookiemy_for_language
from passport.backend.core.test.test_utils import with_settings


language_detect = LanguageDetect()

detect_languages = {
    'yandex.ru': {'all': ['ru', 'uk', 'be'], 'default': 'ru'},
    'yandex.ua': {'all': ['uk', 'ru'], 'default': 'uk'},
    'yandex.com': {'all': ['en'], 'default': 'en'},
    'yandex.com.tr': {'all': ['tr'], 'default': 'tr'},
}


@with_settings(
    DETECT_LANGUAGES=detect_languages,
    ALL_SUPPORTED_LANGUAGES={'all': ['en'], 'default': 'en'},
    MOBILE_FALLBACKS={'kk': 'kk', 'ky': 'ru', 'ru': 'ru'},
    DISPLAY_LANGUAGES=['en', 'tr'],
)
class TestLinguaDetect(unittest.TestCase):
    ips = {
        'ru': '213.180.195.32',
        'uk': '62.149.23.243',
        'en': '8.8.8.8',
        'tr': '31.192.215.244',
    }

    def test_get_language(self):
        eq_(LanguageData(**{'ip': self.ips['ru']}).language, 'ru')

    def test_get_language2(self):
        eq_(LanguageData(**{'ip': self.ips['uk']}).language, 'ru')

    def test_get_language3(self):
        eq_(LanguageData(**{'ip': self.ips['uk'], 'host': 'yandex.com'}).language, 'en')

    def test_get_language4(self):
        eq_(LanguageData(**{'ip': self.ips['uk'], 'accept_language': 'uk', 'host': 'yandex.ua'}).language, 'uk')

    def test_get_language5(self):
        eq_(LanguageData(**{'ip': self.ips['ru'], 'host': 'yandex.ru', 'cookiemy': cookiemy_for_language('uk')}).language, 'uk')

    def test_get_language6(self):
        eq_(LanguageData(**{}).language, 'ru')

    def test_get_language7(self):
        eq_(LanguageData(**{'host': 'yandex.com.tr'}).language, 'tr')

    def test_get_language8(self):
        eq_(LanguageData(**{'host': 'yandex.com', 'accept_language': 'ru'}).language, 'en')

    def test_get_mobile_language(self):
        eq_(MobileLanguageData(**{'accept_language': 'ru'}).language, 'ru')
        eq_(MobileLanguageData(**{'accept_language': 'en'}).language, 'en')
        eq_(MobileLanguageData(**{'accept_language': 'kk'}).language, 'kk')
        eq_(MobileLanguageData(**{'accept_language': 'ky'}).language, 'ru')
        eq_(MobileLanguageData(**{'accept_language': 'tr'}).language, 'tr')

        eq_(MobileLanguageData(**{'accept_language': 'tlh', 'default_fallback': 'en'}).language, 'en')
        eq_(MobileLanguageData(**{'accept_language': 'tlh'}).language, 'en')
        eq_(MobileLanguageData(**{'accept_language': 'tlh', 'default_fallback': 'ru'}).language, 'ru')

        eq_(MobileLanguageData(**{'ip': self.ips['en']}).language, 'en')
        eq_(MobileLanguageData(**{'ip': self.ips['tr']}).language, 'tr')

    def test_get_language_unicode_cookiemy(self):
        eq_(
            LanguageData(**{
                'ip': self.ips['ru'],
                'host': 'yandex.ru',
                'cookiemy': unicode(cookiemy_for_language('uk')),
            }).language,
            'uk',
        )

    def test_host_not_in_detect_languages(self):
        eq_(LanguageData(host='abracadabra').language, 'en')

    def test_get_language_bad_cookiemy(self):
        data = LanguageData(**{'host': 'yandex.ru', 'cookiemy': 'bad_cookie'})
        eq_(data.get_lang_from_cookiemy(), '0')

    def test_get_language_current_location(self):
        data = LanguageData(host='yandex.ru')
        data.yandex_gid = '3'
        eq_(data.current_location, '3')

    def test_get_language_current_location_localhost_ip(self):
        data = LanguageData(ip='127.0.0.1')
        # В 6 геобазе изменилось поведение для локалхоста, вместо пустой строки возвращается 10000
        eq_(data.current_location, '10000')

    def test_get_language_current_location_invalid_ip(self):
        data = LanguageData(ip='127.0.0.1000')
        eq_(data.current_location, '')


class TestGetLanguageNumber(unittest.TestCase):
    def test_get_language_number(self):
        for ln, num in (('ru', 1), (u'ru', 1), ('en', 3), (u'tr', 8)):
            eq_(get_language_number(ln), num)
