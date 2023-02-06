# -*- coding: utf-8 -*-

import sys

from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import RetPath
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
allowed_retpath_scheme_prefixes = {u'scheme.prefix'}

allowed_social_retpath_schemes = {u'weirdscheme'}
allowed_social_retpath_scheme_prefixes = {u'weirdprefix'}


def get_social_retpath_validator():
    return RetPath(
        additional_allowed_schemes=allowed_social_retpath_schemes,
        additional_allowed_scheme_prefixes=allowed_social_retpath_scheme_prefixes,
    )


@with_settings(
    ALLOWED_HOSTS=allowed_hosts,
    ALLOWED_RETPATH_SCHEME_PREFIXES=allowed_retpath_scheme_prefixes,
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
    ADDITIONAL_ALLOWED_RETPATH_SCHEMES={'customscheme'},
)
@pytest.mark.parametrize('valid_url', [
    u'https://derpina.ya.ru/duckface',
    u'http://music.yandex.kz/foo/bar',
    u'//slovari.yandex.kz/?foo=bar&a=b',
    u'//yet.another.long.url.ya.ru',
    u'//яндекс.рф',
    u'//yandex.ru:8080/lorem/impsum',
    u'//yandex.com.tr/subaddr',
    u'//Yandex.Ru',
    u'//YaNdEx.rU',
    u'http://maps.yandex.ru/-/CVRlAX2V',
    u'//yandex.com.tr/subaddr         ',
    u'customscheme:',
    u'customscheme://foo',
    u'scheme.prefix:',
    ])
def test_retpath(valid_url):
    check_equality(RetPath(), (valid_url, valid_url.strip()))


@with_settings(
    ALLOWED_HOSTS=allowed_hosts,
    ALLOWED_RETPATH_SCHEME_PREFIXES=allowed_retpath_scheme_prefixes,
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
    ADDITIONAL_ALLOWED_RETPATH_SCHEMES={'customscheme'},
)
@pytest.mark.skipif(sys.version_info < (3, 9, 5), reason='Python version less then 3.9.5')
@pytest.mark.parametrize('valid_url', [
    u'http://mus\ric.yandex.kz/foo/bar',
    u'http://mus\nic.yandex.kz/foo/bar',
    u'http://mus\tic.yandex.kz/foo/bar',
    u'http://yandex.ru/hello\nLocation',
    u'http://yandex.ru/hello\rLocation',
    u'http://yandex.ru/hello\tLocation',
    ])
def test_retpath_py_3_9_5(valid_url):
    # Начиная с Python 3.9.5 символы \n, \r и \t заменяются на пустую строку
    # https://bugs.python.org/issue43882
    check_equality(RetPath(), (valid_url, "".join(char for char in valid_url if char not in ('\t', '\n', '\r'))))


@with_settings(
    ALLOWED_HOSTS=allowed_hosts,
    ALLOWED_RETPATH_SCHEME_PREFIXES=allowed_retpath_scheme_prefixes,
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
    ADDITIONAL_ALLOWED_RETPATH_SCHEMES={'customscheme'},
)
@pytest.mark.parametrize('invalid_url', [
    u'//kyprizel.net!passport.yandex.ru',
    u'//somesite.com',
    u'http://blogs.mail.ru/derpina/?blobpost=duckface3',
    u'//b91647b&^(B$B%7',
    u'//.ru',
    u'//com.tr',  # недостаточная часть яндексового трехуровнегого урла
    u'//yandex.ru.zloyvasya.ru',
    u'//nyandex.ru',
    u'//уаndex.ru',  # cyrillic 'у, a, е'
    u'//yandex.kewlhaxxor.ru',
    u'//yandex.ru.ru',
    u'//dobryvasya.ru\\@fotki.yandex.ru',  # в логине, пароле или домене недопустим "\"
    u'http://yandex.ru\\@kewl.haxxor.se',  # валидатор не должен менять "\" на"/"
    u'javascript:getroot()',
    u'foobar://yandex.ru/foobar',
    u'//:kewlhaxxor.eq\\@fotki.yandex.ru',
    u'//kewl:haxx0r.eq\\@fotki.yandex.ru',
    u'//kewlhaxx0r.eq\\fotki.yandex.ru',
    u'         ',
    u'http://mytp]\ufffd',  # неправильный url
    u'http://h%0D.school-wiki.yandex.net',
    u'http://h%0A.school-wiki.yandex.net',
    u'http://vasya%0D:password@yandex.net',
    u'http://yandex.ru/redirect?url=hello%00+world',
    u'http://yandex.ru/redirect?url=hello%0A+world',
    u'http://yandex.ru/redirect?url=hello%0D+world',
    u'http://yandex.ru/hello\\Location',
    u'http://yandex.ru/hello\0Location',
    u'customschemeprefix://foo',
    u'scheme.another_prefix:',
    ])
@pytest.mark.parametrize(('retpath_validator', 'ignore_invalid'), [
    (RetPath(), False),
    (get_social_retpath_validator(), False),
    (RetPath(ignore_invalid=True, not_empty=False), True),
    ])
def test_retpath_invalid(invalid_url, retpath_validator, ignore_invalid):
    if ignore_invalid:
        check_equality(retpath_validator, (invalid_url, None))
    else:
        check_raise_error(retpath_validator, invalid_url)


@with_settings(
    ALLOWED_HOSTS=allowed_hosts,
    ALLOWED_RETPATH_SCHEME_PREFIXES=allowed_retpath_scheme_prefixes,
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
    ADDITIONAL_ALLOWED_RETPATH_SCHEMES={'customscheme'},
)
@pytest.mark.skipif(sys.version_info >= (3, 9, 5), reason='Python version greater then or equal 3.9.5')
@pytest.mark.parametrize('invalid_url', [
    u'http://h\r.school-wiki.yandex.net',
    u'http://h\n.school-wiki.yandex.net',
    u'http://h\t.school-wiki.yandex.net',
    u'http://yandex.ru/hello\nLocation',
    u'http://yandex.ru/hello\rLocation',
    u'http://yandex.ru/hello\tLocation',
    ])
@pytest.mark.parametrize(('retpath_validator', 'ignore_invalid'), [
    (RetPath(), False),
    (get_social_retpath_validator(), False),
    (RetPath(ignore_invalid=True, not_empty=False), True),
    ])
def test_retpath_invalid_py_3_9_5(invalid_url, retpath_validator, ignore_invalid):
    # Начиная с Python 3.9.5 символы \n, \r и \t заменяются на пустую строку
    # https://bugs.python.org/issue43882
    if ignore_invalid:
        check_equality(retpath_validator, (invalid_url, None))
    else:
        check_raise_error(retpath_validator, invalid_url)


@with_settings(
    ALLOWED_HOSTS=allowed_hosts,
    ALLOWED_RETPATH_SCHEME_PREFIXES=allowed_retpath_scheme_prefixes,
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
    ADDITIONAL_ALLOWED_RETPATH_SCHEMES={'customscheme'},
)
@pytest.mark.parametrize('valid_url', [
    u'https://derpina.ya.ru/duckface',
    u'http://music.yandex.kz/foo/bar',
    u'//slovari.yandex.kz/?foo=bar&a=b',
    u'weirdscheme://news.yandex.kz/',
    u'weirdscheme://some-host/foo',
    u'weirdprefix://some-host/foo',
    u'weirdprefixscheme://some-host/foo',
    u'weirdprefixscheme:',
    u'weirdscheme:?foo=bar',
    u'customscheme://foo',
    u'scheme.prefix:'
    ])
def test_retpath_social_schemes(valid_url):
    check_equality(get_social_retpath_validator(), (valid_url, valid_url.strip()))


@with_settings(
    ALLOWED_HOSTS=allowed_hosts,
    ALLOWED_RETPATH_SCHEME_PREFIXES=allowed_retpath_scheme_prefixes,
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
    ADDITIONAL_ALLOWED_RETPATH_SCHEMES={'customscheme'},
)
@pytest.mark.parametrize('invalid_url', [
    u'weirdscheme://dobryvasya.ru\\@fotki.yandex.ru',  # в логине, пароле или домене недопустим "\"
    u'weirdscheme://kewl:haxx0r.eq\\@fotki.yandex.ru',
    u'weirdscheme//.ru',
    u'customschemeprefix://foo',
    ])
def test_retpath_social_schemes_invalid(invalid_url):
    check_raise_error(get_social_retpath_validator(), invalid_url)


@with_settings(
    ALLOWED_HOSTS=allowed_hosts,
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('valid_url', [
    u'http://yandex.ru/qweasd',
    u'http://maps.yandex.ru/-/CVRlAX2V',
    u'http://subdomain.h.yandex.ru',
    u'http://yandex.ru/clck',
    u'http://subdomain.h.yandex.ru/clck/123456/?a=b',
    ])
def test_retpath_with_blacklist(valid_url):
    check_equality(RetPath(), (valid_url, valid_url.strip()))


@with_settings(
    ALLOWED_HOSTS=allowed_hosts,
    RETPATH_BAD_SYMBOLS=TEST_BAD_SYMBOLS,
)
@pytest.mark.parametrize('invalid_url', [
    u'http://h.yandex.ru/qwe\\asd',
    u'http://yandex.org/',
    u'https://yandex.net',
    u'https://swf.static.yandex.net',
    u'http://yandex.ru/clck/',
    u'http://yandex.ru/clck/100500/?asdads=adss',
    u'http://yandex.com.tr/clck/100500/?asdads=adss&b=c',
    u'https://yandex.ru/count/03LfXrKeXTS50FG2CJSalLq00000EDJ27K02I09W',
    ])
def test_retpath_with_blacklist_invalid(invalid_url):
    check_raise_error(RetPath(), invalid_url)
