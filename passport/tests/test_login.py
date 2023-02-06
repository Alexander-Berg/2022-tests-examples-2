# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.types.login.login import (
    extract_clean_login_from_email,
    extract_phonenumber_alias_candidate_from_login,
    generate_kiddish_login,
    generate_kolonkish_login,
    generate_neophonish_login,
    generate_phonish_login,
    generate_social_login,
    generate_yambot_login,
    KOLONKISH_LOGIN_PREFIX,
    login_is_kiddish,
    login_is_kolonkish,
    login_is_neophonish,
    login_is_phonish,
    login_is_scholar,
    login_is_social,
    login_is_yambot,
    masked_login,
    NEOPHONISH_LOGIN_PREFIX,
    normalize_login,
    PHONISH_LOGIN_PREFIX,
    SOCIAL_LOGIN_PREFIX,
    strongly_masked_login,
    YAMBOT_LOGIN_PREFIX,
)
from passport.backend.utils.string import smart_text
import pytest


def test_login_is_social():
    ok_(login_is_social('uid-aqweqweqwe'))
    ok_(not login_is_social('asd-zxczxcxz'))


def test_login_is_phonish():
    ok_(login_is_phonish('phne-zczxczxc'))
    ok_(not login_is_phonish('phneeeeeeee'))


def test_login_is_neophonish():
    ok_(login_is_neophonish('nphne-zczxczxc'))
    ok_(not login_is_neophonish('nphneeeeeeee'))


def test_login_is_yambot():
    ok_(login_is_yambot('yambot-zczxczxc'))
    ok_(not login_is_yambot('yambotttt'))


def test_login_is_kolonkish():
    ok_(login_is_kolonkish('kolonkish-zczxczxc'))
    ok_(not login_is_yambot('kolonkeck'))


def test_login_is_kiddish():
    ok_(login_is_kiddish('kid-zczxczxc'))


def test_login_is_scholar():
    ok_logins = [
        'ы',
        'ы7',
        'Ы',
        'ы7ы',
    ]
    for ok_login in ok_logins:
        assert login_is_scholar(ok_login), ok_login
        assert login_is_scholar(smart_text(ok_login)), ok_login

    wrong_logins = [
        '1',
        '1ы',
        's',
        'S',
        'ы-ы',
        'ы.ы',
        'ы_ы',
        'ыs',
    ]
    for wrong_login in wrong_logins:
        assert not login_is_scholar(wrong_login), wrong_login


class TestLogin(unittest.TestCase):
    def test_normalization(self):
        eq_(normalize_login('good.lo-Gin'), 'good-lo-gin')

    def test_email_normalization(self):
        eq_(normalize_login('good.login@ya.ru'), 'good.login@ya.ru')

    def test_none_normalization(self):
        eq_(normalize_login(None), None)


class TestGenerateSocialLogin(unittest.TestCase):
    def test_generate_social_login(self):
        login = generate_social_login()
        ok_(login.startswith(SOCIAL_LOGIN_PREFIX))
        eq_(len(login), 12)

    def test_generate_social_login_with_fixed_env(self):
        with mock.patch('os.urandom') as urandom:
            urandom.return_value = b'\xf1:&V\x9e'
            eq_(generate_social_login(), 'uid-6e5cmvu6')


class TestGeneratePhonishLogin(unittest.TestCase):
    def test_generate_phonish_login(self):
        login = generate_phonish_login()
        ok_(login.startswith(PHONISH_LOGIN_PREFIX))
        eq_(len(login), 13)

    def test_generate_phonish_login_with_fixed_env(self):
        with mock.patch('os.urandom') as urandom:
            urandom.return_value = b'\xf1:&V\x9e'
            eq_(generate_phonish_login(), 'phne-6e5cmvu6')


class TestGenerateNeohonishLogin(unittest.TestCase):
    def test_generate_neophonish_login(self):
        login = generate_neophonish_login()
        ok_(login.startswith(NEOPHONISH_LOGIN_PREFIX))
        eq_(len(login), 14)

    def test_generate_neophonish_login_with_fixed_env(self):
        with mock.patch('os.urandom') as urandom:
            urandom.return_value = b'\xf1:&V\x9e'
            eq_(generate_neophonish_login(), 'nphne-6e5cmvu6')


class TestGenerateYambotLogin(unittest.TestCase):
    def test_generate_yambot_login(self):
        login = generate_yambot_login()
        ok_(login.startswith(YAMBOT_LOGIN_PREFIX))
        eq_(len(login), 15)

    def test_generate_yambot_login_with_fixed_env(self):
        with mock.patch('os.urandom') as urandom:
            urandom.return_value = b'\xf1:&V\x9e'
            eq_(generate_yambot_login(), 'yambot-6e5cmvu6')


class TestGenerateKolonkishLogin(unittest.TestCase):
    def test_generate_kolonkish_login(self):
        login = generate_kolonkish_login()
        ok_(login.startswith(KOLONKISH_LOGIN_PREFIX))
        eq_(len(login), 18)

    def test_generate_kolonkish_login_with_fixed_env(self):
        with mock.patch('os.urandom') as urandom:
            urandom.return_value = b'\xf1:&V\x9e'
            eq_(generate_kolonkish_login(), 'kolonkish-6e5cmvu6')


class TestGenerateKiddishLogin(unittest.TestCase):
    def test_generate_kiddish_login_with_fixed_env(self):
        with mock.patch('os.urandom') as urandom:
            urandom.return_value = b'\xf1:&V\x9e'
            eq_(generate_kiddish_login(), 'kid-6e5cmvu6')


@pytest.mark.parametrize(
    ('actual', 'expected'),
    [
        ('foo@bar', 'foo'),
        ('123foo@bar', 'foo'),
        ('foo___bar@zar', 'foo-bar'),
        ('+foo@bar', ''),
        ('foo+bar@zar', 'foo'),
        (u'fooАБВbar@zar', 'foo.bar'),
        ('foo.....bar@zar', 'foo.bar'),
        ('.foo.bar.@zar', 'foo.bar'),
        ('--foo--@bar', 'foo'),
        (u'--fooАБВ___bar....+xxx@zar', 'foo.bar'),
        (u'--foo___АБВbar....+xxx@zar', 'foo.bar'),
        ('foo.-.-.-.-bar@zar', 'foo.bar'),
        ('foo-.-.-.-.bar@zar', 'foo.bar'),
        ('foo', 'foo'),
    ],
)
def test_login_from_email(actual, expected):
    eq_(extract_clean_login_from_email(actual), expected)


@pytest.mark.parametrize(
    ('actual', 'expected'),
    [
        ('', ''),
        ('a', 'a'),
        ('ab', 'a***'),
        ('abc', 'a***'),
        ('longlogin', 'lon***'),
        ('a@domain.com', 'a@domain.com'),
        ('ab@domain.com', 'a***@domain.com'),
        ('abc@domain.com', 'a***@domain.com'),
        ('login@domain.com', 'lo***@domain.com'),
        ('longlogin@domain.com', 'lon***@domain.com'),
    ],
)
def test_masked_login(actual, expected):
    eq_(masked_login(actual), expected)


def test_strongly_masked_login():
    eq_(strongly_masked_login(''), '')
    eq_(strongly_masked_login('a'), 'a***a')
    eq_(strongly_masked_login('ab'), 'a***b')
    eq_(strongly_masked_login('login'), 'l***n')
    eq_(strongly_masked_login('longlogin'), 'l***n')
    eq_(strongly_masked_login('login@domain'), 'l***n@d***n')


@with_settings(
    NATIVE_EMAIL_DOMAINS=('yandex.ru', u'яндекс.рф'),
    ALT_DOMAINS=('galatasaray.net', 'auto.ru'),
)
def test_extract_phonenumber_alias_candidate_from_login():
    test_values = [
        ('Login', None),
        ('L12345', None),
        ('777@site.com', None),
        ('Login@yandex.ru', None),
        ('8-999-100(10)(10)', '89991001010'),
        ('+79991001010', '79991001010'),
        ('777@yandex.ru', '777'),
        ('8-923-777@galatasaray.net', '8923777'),
        # Домен может быть как закодирован, так и нет
        (u'11111@яндекс.рф', '11111'),
        (u'11111@' + u'яндекс.рф'.encode('idna').decode('utf-8'), '11111'),
        # UnicodeError
        (u'loggin@xn--grohandel-shop-2fb', None),
    ]
    for index, (login, expected_alias_candidate) in enumerate(test_values):
        alias_candidate = extract_phonenumber_alias_candidate_from_login(login)
        eq_(expected_alias_candidate, alias_candidate, (index, expected_alias_candidate, alias_candidate))
