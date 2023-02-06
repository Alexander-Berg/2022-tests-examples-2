# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import SimpleUrlValidator
import pytest


TEST_BAD_SYMBOLS = set('\\\t\r\n\0')


allowed_hosts = (
    u'yandex.ru',
    u'yandex.kz',
    u'yandex.net',
    u'yandex.by',
    u'ya.ru',
    u'yandex.com.tr',
    u'яндекс.рф',
)


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('valid_url', [
    u'https://derpina.ya.ru/duckface',
    u'http://music.yandex.kz/foo/bar',
    u'http://maps.yandex.ru/-/CVRlAX2V',
    u'http://maps.yandex.ru/-/CVRlAX2V               ',
    ])
def test_urls(valid_url):
    check_equality(SimpleUrlValidator(), (valid_url, valid_url.strip()))


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('invalid_url', [
    u'//somesite.com',
    u'//b91647b&^(B$B%7',
    u'//.ru',
    u'//dobryvasya.ru\\@fotki.yandex.ru',  # в логине, пароле или домене недопустим "\"
    u'http://yandex.ru\\@kewl.haxxor.se',  # валидатор не должен менять "\" на"/"
    u'foobar://yandex.ru/foobar',
    u'https://yandex.ru/foobar#frag',
    u'http://mytp]\ufffd',
    u'http://h%0D.school-wiki.yandex.net',
    u'http://h%0A.school-wiki.yandex.net',
    u'http://h\r.school-wiki.yandex.net',
    u'http://h\n.school-wiki.yandex.net',
    u'http://h\t.school-wiki.yandex.net',
    u'http://vasya%0D:password@yandex.net',
    u'http://yandex.ru/redirect?url=hello%00+world',
    u'http://yandex.ru/redirect?url=hello%0A+world',
    u'http://yandex.ru/redirect?url=hello%0D+world',
    u'http://yandex.ru/hello\\Location',
    u'http://yandex.ru/hello\nLocation',
    u'http://yandex.ru/hello\rLocation',
    u'http://yandex.ru/hello\tLocation',
    u'http://yandex.ru/hello\0Location',
    u'customschemeprefix://foo',
    ])
def test_urls_invalid(invalid_url):
    check_raise_error(SimpleUrlValidator(), invalid_url)


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('valid_url', [
    u'opa://derpina.ya.ru/duckface',
    u'ololo://music.yandex.kz/foo/bar',
    ])
def test_urls_with_custom_scheme(valid_url):
    check_equality(SimpleUrlValidator(additional_allowed_schemes=['opa', 'ololo']), (valid_url, valid_url.strip()))


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('invalid_url', [
    u'opapa://derpina.ya.ru/duckface',
    u'olo://music.yandex.kz/foo/bar',
    ])
def test_urls_with_custom_scheme_invalid(invalid_url):
    check_raise_error(SimpleUrlValidator(additional_allowed_schemes=['opa', 'ololo']), invalid_url)


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('valid_url', [
    u'http:///foo/bar',
    ])
def test_urls_with_allow_empty_host(valid_url):
    check_equality(SimpleUrlValidator(allow_empty_host=True), (valid_url, valid_url.strip()))


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('valid_url', [
    u'http://yandex.ru/foo/bar#fragment',
    u'http://yandex.ru/',
    ])
def test_urls_with_allow_fragments(valid_url):
    check_equality(SimpleUrlValidator(allow_fragments=True), (valid_url, valid_url.strip()))


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('invalid_url', [
    u'http:///foo/bar',
    ])
def test_urls_with_allow_fragments_invalid(invalid_url):
    check_raise_error, SimpleUrlValidator(allow_fragments=True), invalid_url


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('valid_url', [
    u'http://yandex.ru/foo/bar',
    u'http://maps.yandex.ru/foo/bar',
    ])
def test_urls_with_allowed_hosts(valid_url):
    check_equality(SimpleUrlValidator(allowed_hosts=allowed_hosts), (valid_url, valid_url.strip()))


@with_settings(
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('invalid_url', [
    u'http://naydex.ru/foo/bar',
    u'http://yandex.com/foo/bar',
    u'http://yandex.com.ru/foo/bar',
    ])
def test_urls_with_allowed_hosts_invalid(invalid_url):
    check_raise_error(SimpleUrlValidator(allowed_hosts=allowed_hosts), invalid_url)
