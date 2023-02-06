# -*- coding: utf-8 -*-
from collections import namedtuple

from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_error_codes,
    check_raise_error,
)
from passport.backend.core.validators.login.login import (
    LiteLogin,
    Login,
    PddLogin,
    ScholarLogin,
    SocialLogin,
    YandexTeamLogin,
)
import pytest


_domain_keyspace = namedtuple('domain_keyspace', ['domain', 'keyspace'])


@pytest.mark.parametrize('valid_login', [
    'yndx.volozh',
    'double--hyphen',
    'abc.123',
    'hello-world',
    '12345678',
    '0___o',
    '_' * 40,
    ])
def test_pdd_login(valid_login):
    check_equality(PddLogin(), (valid_login, valid_login))


@pytest.mark.parametrize('invalid_login', [
    'привет.мир',
    u'привет.мир',
    '     ',
    'y' * 41,
    '!@#$!',
    'bilbo@sumkin!org',
    ])
def test_pdd_login_invalid(invalid_login):
    check_raise_error(PddLogin(), invalid_login)


@pytest.mark.parametrize(('login', 'expected_codes'), [
    (
        '1foo..bar£qwe.-rty' + 'a' * 300 + '-',
        {
            'login': [
                'prohibitedSymbols',
                'tooLong'
            ],
        }
    ),
    ])
def test_pdd_login_expected_codes(login, expected_codes):
    check_error_codes(PddLogin(), login, expected_codes)


@pytest.mark.parametrize(('valid_login', 'result'), [
    ('asdfgh', 'asdfgh'),
    ('abc123', 'abc123'),
    ('abc.123', 'abc.123'),
    ('foo.bar123', 'foo.bar123'),
    ('foo-bar.123', 'foo-bar.123'),
    ('l' * 30, 'l' * 30),
    (' login ', 'login'),
    ])
def test_login(valid_login, result):
    check_equality(Login(), (valid_login, result))


@pytest.mark.parametrize('invalid_login', [
    '',
    '.abc',
    'abc.',
    '-abc',
    'abc-',
    'foo--bar',
    'foo..bar',
    'foo.-bar',
    'foo-.bar',
    'русский',
    '123abc',
    'long' * 40,
    'vasya@yandex',
    '    ',
    'ostap@yandex.ru',
    ])
def test_login_invalid(invalid_login):
    check_raise_error(Login(), invalid_login)


@pytest.mark.parametrize(('login', 'expected_codes'), [
    ('.foo..bar--qwe.-rty-.', {'login': ['startsWithDot', 'endsWithDot', 'doubledDot', 'doubledHyphen', 'dotHyphen', 'hyphenDot']}),
    ('1foo..bar£qwe.-rty' + 'a' * 300 + '-', {'login': ['startsWithDigit', 'endsWithHyphen', 'doubledDot', 'dotHyphen', 'prohibitedSymbols', 'tooLong']}),
    ('-foo..bar£qwe-.rty' + 'a' * 300 + '-', {'login': ['startsWithHyphen', 'endsWithHyphen', 'doubledDot', 'hyphenDot', 'prohibitedSymbols', 'tooLong']}),
    ('asd fgh', {'login': ['prohibitedSymbols']}),
    ('asdfgh#аа', {'login': ['prohibitedSymbols']}),
    ])
def test_login_params(login, expected_codes):
    check_error_codes(Login(), login, expected_codes)


@pytest.mark.parametrize('valid_login', [
    'uid-asdfgh',
    'uid-xx123sdf',
    'uid.123sdf',
    ])
def test_sociallogin(valid_login):
    check_equality(SocialLogin(), (valid_login, valid_login))


@pytest.mark.parametrize('invalid_login', [
    'asdfgh',
    'abc123',
    'abc.123',
    'foo.bar123',
    'foo-bar.123',
    'l' * 30,
    '',
    '.abc',
    'abc.',
    '-abc',
    'abc-',
    'foo--bar',
    'foo..bar',
    'foo.-bar',
    'foo-.bar',
    'русский',
    '123abc',
    'long' * 40,
    'vasya@yandex',
    '    ',
    'ostap@yandex.ru',
    'uid.123sdf ',
    ])
def test_sociallogin_invalid(invalid_login):
    check_raise_error(SocialLogin(), invalid_login)


@pytest.mark.parametrize(('login', 'expected_codes'), [
    ('uid-.foo..bar--qwe.-rty-.',
     {'login': [
         'endsWithDot',
         'doubledDot',
         'doubledHyphen',
         'dotHyphen',
         'hyphenDot'
     ]}),
    ('1foo..bar£qwe.-rty' + 'a' * 300 + '-', {'login': ['notSocial']}),
    ])
def test_sociallogin_params(login, expected_codes):
    check_error_codes(SocialLogin(), login, expected_codes)


@with_settings(
    DOMAIN_KEYSPACES=[
        _domain_keyspace('yandex.ru', ''),
        _domain_keyspace('yandex.com', ''),
    ],
    LITE_LOGIN_MAX_DOMAIN_LEVEL=3,
    LITE_LOGIN_BLACKLISTED_DOMAINS=['evil.com'],
)
@pytest.mark.parametrize('valid_login', [
    'a@b.ru',
    'a.b@mail.ru',
    'a.b-c_2@e.domain.com',
    'Lite@mk.ru',
    ])
def test_lite_login(valid_login):
    check_equality(LiteLogin(), (valid_login, valid_login.lower()))


@with_settings(
    DOMAIN_KEYSPACES=[
        _domain_keyspace('yandex.ru', ''),
        _domain_keyspace('yandex.com', ''),
    ],
    LITE_LOGIN_MAX_DOMAIN_LEVEL=3,
    LITE_LOGIN_BLACKLISTED_DOMAINS=['evil.com'],
)
@pytest.mark.parametrize('invalid_login', [
    'uid-123',
    'abc123',
    'abc.123',
    'foo.bar123',
    'foo-bar.123',
    'a@yandex.ru',
    'a.b@yandex.com',
    u'русский',
    'a@b.c.d.ru',
    'a@evil.com',
    'a@EvIl.CoM',
    ])
def test_lite_login_invalid(invalid_login):
    check_raise_error(LiteLogin(), invalid_login)


@with_settings(
    DOMAIN_KEYSPACES=[
        _domain_keyspace('yandex.ru', ''),
        _domain_keyspace('yandex.com', ''),
    ],
    LITE_LOGIN_MAX_DOMAIN_LEVEL=3,
    LITE_LOGIN_BLACKLISTED_DOMAINS=['evil.com'],
)
@pytest.mark.parametrize(('login', 'expected_codes'), [
    ('a' * 41, {'login': ['tooLong']}),
    ('!$%^&*_-`/?.+=@mail.ru', {'login': ['prohibitedSymbols']}),
    (u'админ@mail.ru', {'login': ['prohibitedSymbols']}),
    (u'admin@окна.рф', {'login': ['prohibitedSymbols']}),
    ('admin@xn--80atjc.xn--p1ai', {'login': ['idna']}),
    ])
def test_lite_login_params(login, expected_codes):
    check_error_codes(LiteLogin(), login, expected_codes)


@pytest.mark.parametrize(('valid_login', 'result'), [
    ('asdfgh', 'asdfgh'),
    ('abc123', 'abc123'),
    ('1abc', '1abc'),
    ('aa--aa', 'aa--aa'),
    ('abc-123', 'abc-123'),
    ('foo-bar123', 'foo-bar123'),
    ('foo-bar-123', 'foo-bar-123'),
    ('l' * 100, 'l' * 100),
    (' login ', 'login'),
    ('login_login', 'login_login'),
    ])
def test_yandex_team_login(valid_login, result):
    check_equality(YandexTeamLogin(), (valid_login, result))


@pytest.mark.parametrize('invalid_login', [
    '',
    '-abc',
    'abc-',
    'foo..bar',
    'foo.-bar',
    'foo-.bar',
    'русский',
    'long' * 200,
    'a' * 101,
    'vasya@yandex',
    '    ',
    'ostap@yandex.ru',
    ])
def test_yandex_team_login_invalid(invalid_login):
    check_raise_error(YandexTeamLogin(), invalid_login)


@pytest.mark.parametrize(('login', 'expected_codes'), [
    (
        '-foo..bar£qwe-.rty' + 'a' * 300 + '-',
        {
            'login':
            [
                'startsWithHyphen',
                'endsWithHyphen',
                'prohibitedSymbols',
                'tooLong',
            ],
        },
    ),
    ('asd fgh', {'login': ['prohibitedSymbols']}),
    ('asdfgh#аа', {'login': ['prohibitedSymbols']}),
    ('.abcd', {'login': ['prohibitedSymbols']}),
    ('.abcd.', {'login': ['prohibitedSymbols']}),
    ])
def test_yandex_team_login_params(login, expected_codes):
    check_error_codes(YandexTeamLogin(), login, expected_codes)


@pytest.mark.parametrize(('valid_login', 'result'), [
    ('ю', 'ю'),
    ('ё', 'ё'),
    ('ё123', 'ё123'),
    ('ё' * 30, 'ё' * 30),
    (' вовочка ', 'вовочка'),
    ])
def test_scholar_login(valid_login, result):
    check_equality(ScholarLogin(), (valid_login, result))


@pytest.mark.parametrize('invalid_login', [
    '',
    '1',
    '1ё',
    '.ё',
    'ё.',
    'ё.ё',
    '-ё',
    'ё-',
    'ё-ё',
    'w',
    'в' * 31,
    'вовочка@яндекс',
    '    ',
    'вовочка@яндекс.рф',
    ])
def test_scholar_login_invalid(invalid_login):
    check_raise_error(ScholarLogin(), invalid_login)


@pytest.mark.parametrize(('login', 'expected_codes'), [
    (
        '1' + 'w' * 31,
        {
            'login': [
                'tooLong',
                'startsWithDigit',
                'prohibitedSymbols',
            ],
        },
    ),
    ])
def test_scholar_login_params(login, expected_codes):
    check_error_codes(ScholarLogin(), login, expected_codes)
