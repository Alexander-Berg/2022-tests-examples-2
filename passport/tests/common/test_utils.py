# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.oauth.core.common.utils import (
    bytes_to_int,
    escape,
    first_or_none,
    from_base64_url,
    hex_to_bytes,
    int_or_default,
    int_to_bytes,
    make_hash,
    mask_string,
    normalize_url,
    smart_any,
    sorted_uniqs,
    split_by_predicate,
    to_base64_url,
    update_url_params,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


class TestMiscUtils(BaseTestCase):
    def test_first_or_none(self):
        eq_(first_or_none(None), None)
        eq_(first_or_none([]), None)
        eq_(first_or_none(tuple()), None)
        eq_(first_or_none([1]), 1)
        eq_(first_or_none([1, 2, 3]), 1)

    def test_int_or_default(self):
        eq_(int_or_default('1'), 1)
        eq_(int_or_default('1', 42), 1)
        eq_(int_or_default('foo'), None)
        eq_(int_or_default('foo', 42), 42)
        eq_(int_or_default(None, 42), 42)

    def test_smart_any(self):
        ok_(not smart_any(int, []))
        ok_(not smart_any(lambda x: True, []))
        ok_(not smart_any(lambda x: False, [1, 2, 3]))
        ok_(smart_any(lambda x: x > 2, [1, 2, 3]))

    def test_split_by_predicate(self):
        eq_(
            split_by_predicate([0, -1, 100500, -100501, 42], lambda x: x > 1),
            ([100500, 42], [0, -1, -100501]),
        )
        eq_(
            split_by_predicate([1, 2, 3, 4, 5], lambda x: x % 2, lambda x: str(x)),
            (['1', '3', '5'], ['2', '4']),
        )


class TestEscape(BaseTestCase):
    def test_ok(self):
        eq_(escape(None), 'None')
        eq_(escape(123), '123')
        eq_(escape('\\1\t2\r3\n4\0'), '\\\\1\\t2\\r3\\n4\\0')


class TestMaskString(BaseTestCase):
    def test_ok(self):
        eq_(mask_string(None, 0), None)
        eq_(mask_string('', 0), '')
        eq_(mask_string('hello', 0), '*****')
        eq_(mask_string('hello', 1), 'h****')
        eq_(mask_string('hello', 5), 'hello')
        eq_(mask_string('hello', 10), 'hello')


class TestMakeHash(BaseTestCase):
    def test_ok(self):
        for from_, to_ in (
            ('', b'1:47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU'),
            ('abc', b'1:ungWv48Bz+pBQUDeXa4iI7ADYaOWF3qctBD/YfIAFa0'),
        ):
            eq_(make_hash(from_, version=1), to_)


class TestSortedUniqs(BaseTestCase):
    def test_ok(self):
        eq_(
            sorted_uniqs([]),
            [],
        )
        eq_(
            sorted_uniqs([1, 3, 2]),
            [1, 3, 2],
        )
        eq_(
            sorted_uniqs([1, 3, 2, 2, 3, 3]),
            [3, 2, 1],
        )


class TestBase64(BaseTestCase):
    cases = {
        '': b'',
        'A': b'QQ',
        'AA': b'QUE',
        'AAA': b'QUFB',
        'AAAA': b'QUFBQQ',
        'AAAAA': b'QUFBQUE',
        'Hello, World!': b'SGVsbG8sIFdvcmxkIQ',
    }

    def test_encode(self):
        for from_, to_ in self.cases.items():
            eq_(to_base64_url(from_), to_)

    def test_decode(self):
        for from_, to_ in self.cases.items():
            eq_(from_base64_url(to_), from_.encode())


class TestIntToBytes(BaseTestCase):
    def test_ok(self):
        eq_(int_to_bytes(65534, 0), b'')
        # в первую очередь берём младшие байты
        eq_(int_to_bytes(65534, 1), b'\xfe')
        # размер совпал
        eq_(int_to_bytes(65534, 2), b'\xff\xfe')
        # добавляем нулевые старшие байты
        eq_(int_to_bytes(65534, 3), b'\x00\xff\xfe')

    def test_zero(self):
        eq_(int_to_bytes(0, 0), b'')
        eq_(int_to_bytes(0, 1), b'\x00')
        eq_(int_to_bytes(0, 2), b'\x00\x00')


class TestBytesToInt(BaseTestCase):
    def test_ok(self):
        eq_(bytes_to_int(b''), 0)
        eq_(bytes_to_int(b'\x00'), 0)
        eq_(bytes_to_int(b'\x01'), 1)
        eq_(bytes_to_int(b'\xff\xfe'), 65534)


class TestHexToBytes(BaseTestCase):
    def test_ok(self):
        eq_(hex_to_bytes(''), b'')
        eq_(hex_to_bytes('aa'), b'\xaa')
        eq_(hex_to_bytes('deadbeef'), b'\xde\xad\xbe\xef')


class TestAddParamsToUrl(BaseTestCase):
    def test_ok(self):
        eq_(update_url_params('https://ya.ru', foo='bar'), 'https://ya.ru?foo=bar')

    def test_already_has_query(self):
        eq_(update_url_params('https://ya.ru?search=text', foo='bar'), 'https://ya.ru?search=text&foo=bar')

    def test_replace_param(self):
        eq_(update_url_params('https://ya.ru?search=text&foo=none', foo='bar'), 'https://ya.ru?search=text&foo=bar')


class TestNormalizeUrl(BaseTestCase):
    def test_ok(self):
        for from_, to_ in (
            ('', ''),
            (b'NotAnUrl', 'NotAnUrl'),
            (b'https://google.com', 'https://google.com'),
            ('HTTPS://Google.com/Test?Foo=Bar', 'https://google.com/Test?Foo=Bar'),
            ('http://окна.рф', 'http://xn--80atjc.xn--p1ai'),
            ('https://Окна.рф:443/тест/path?a=1&я=2#хэш-tag', 'https://xn--80atjc.xn--p1ai:443/тест/path?a=1&я=2#хэш-tag'),
            ('customscheme:///auth/finish?platform=ios', 'customscheme:/auth/finish?platform=ios'),
            ('yandexta://ozon.ru', 'yandexta://ozon.ru'),
            ('yandexta://ozon.ru/', 'yandexta://ozon.ru'),
            ('yandexta://ozon.ru/some/path', 'yandexta://ozon.ru/some/path'),
            ('yandexta://ozon.ru/some/path/', 'yandexta://ozon.ru/some/path'),
        ):
            eq_(normalize_url(from_), to_)
            eq_(normalize_url(to_), to_)

    def test_strict_ok(self):
        for from_, to_ in (
            ('', ''),
            (b'NotAnUrl', 'NotAnUrl'),
            (b'https://google.com', 'https://google.com'),
            ('HTTPS://Google.com/Test?Foo=Bar', 'https://google.com/Test'),
            ('http://окна.рф', 'http://xn--80atjc.xn--p1ai'),
            ('https://Окна.рф:443/тест/path?a=1&я=2#хэш-tag', 'https://xn--80atjc.xn--p1ai:443/тест/path'),
            ('customscheme:///auth/finish?platform=ios', 'customscheme:/auth/finish'),
            ('yandexta://ozon.ru', 'yandexta://ozon.ru'),
            ('yandexta://ozon.ru/', 'yandexta://ozon.ru'),
            ('yandexta://ozon.ru/some/path', 'yandexta://ozon.ru'),
            ('yandexta://ozon.ru/some/path/', 'yandexta://ozon.ru'),
        ):
            eq_(
                normalize_url(
                    from_,
                    drop_path_for_schemes={'yandexta'},
                    drop_params=True,
                    drop_query=True,
                    drop_fragment=True,
                ),
                to_,
            )
            eq_(
                normalize_url(
                    to_,
                    drop_path_for_schemes={'yandexta'},
                    drop_params=True,
                    drop_query=True,
                    drop_fragment=True,
                ),
                to_,
            )
