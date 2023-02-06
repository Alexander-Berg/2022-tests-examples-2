# -*- coding: utf-8 -*-

from contextlib import contextmanager
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.utils.common import (
    chop,
    ClassMapping,
    context_manager_to_decorator,
    flatten,
    flatten_values,
    format_code_by_3,
    from_base64_standard,
    from_base64_url,
    generate_random_code,
    get_default_if_none,
    merge_dicts,
    noneless_dict,
    normalize_code,
    remove_none_values,
    smart_merge_dicts,
    to_base64_standard,
    to_base64_url,
    unflatten,
    unique_preserve_order,
    url_to_ascii,
)
from six import StringIO


class TestClassMapping(TestCase):
    # Тестовые классы
    class _Foo(object):
        pass

    class _Bar(object):
        pass

    class _Subbar(_Bar):
        pass

    class _Spam(object):
        pass

    def setUp(self):
        self.mapping = ClassMapping([
            (self._Foo, u'Foo'),
            (self._Bar, u'Bar'),
        ])

    def test_map_same_class(self):
        eq_(self.mapping[self._Foo], u'Foo')

    def test_map_sub_class(self):
        eq_(self.mapping[self._Subbar], u'Bar')

    @raises(KeyError)
    def test_map_object(self):
        self.mapping[self._Foo()]

    @raises(KeyError)
    def test_key_error(self):
        self.mapping[self._Spam]

    def test_iter(self):
        eq_(list(self.mapping.keys()), [self._Foo, self._Bar])

    def test_length(self):
        eq_(len(self.mapping), 2)


class TestGenerateRandomCode(TestCase):
    def test_invalid(self):
        assert_raises(ValueError, generate_random_code, 0)
        assert_raises(ValueError, generate_random_code, -4)

    def test_format(self):
        code = generate_random_code(4)
        ok_(isinstance(code, str))
        ok_(code.isdigit())
        ok_(len(code) == 4)

    def test_system_random_using(self):
        with mock.patch('random.SystemRandom.randrange') as random_mock:
            generate_random_code(1)
            eq_(random_mock.call_count, 1)

    def test_length(self):
        for x in range(1000):
            code = generate_random_code(1)
            ok_(1 <= int(code) <= 9)

        with mock.patch('random.SystemRandom.randrange') as random_mock:
            generate_random_code(1)
            random_mock.assert_called_with(1, 10)
            generate_random_code(2)
            random_mock.assert_called_with(10, 100)


class TestFormatCodeBy3(TestCase):
    @parameterized.expand([
        ('1', '1'),
        ('12', '12'),
        ('123', '123'),
        ('1234', '123 4'),
        ('12345678', '123 456 78'),
    ])
    def test_ok(self, input_code, expected_code):
        assert format_code_by_3(input_code) == expected_code

    def test_delimiter(self):
        assert format_code_by_3('123456', delimiter='?') == '123?456'


class TestNormalizeCode(TestCase):
    @parameterized.expand([
        ('123 456', ' ', '123456'),
        ('123?456', '?', '123456'),
        ('12 34?56', ' ', '1234?56'),
        ('123?-_456', '_-?', '123456'),
        (123456, ' ', '123456'),
    ])
    def test_ok(self, input_code, delimiters, expected_code):
        assert normalize_code(input_code, delimiters) == expected_code


class TestUniquePreserveOrder(TestCase):
    def test_empty(self):
        eq_(unique_preserve_order([]), [])

    def test_unique(self):
        eq_(unique_preserve_order((1, 2, 3)), [1, 2, 3])

    def test_order_preserved(self):
        eq_(unique_preserve_order([3, 1, 2, 2, 1, 3]), [3, 1, 2])

    def test_with_dict(self):
        eq_(unique_preserve_order(dict(a=1, b=2)), ['a', 'b'])

    def test_with_str(self):
        eq_(unique_preserve_order('abbab'), ['a', 'b'])


class TestContextManagerToDecorator(TestCase):
    def setUp(self):
        self._mock = mock.Mock()

    def tearDown(self):
        del self._mock

    def test(self):
        decorator = context_manager_to_decorator(self._context_manager)
        decorated_func = decorator(self._mock)

        decorated_func(u'func')

        eq_(
            self._mock.mock_calls,
            [
                mock.call(u'before'),
                mock.call(u'func'),
                mock.call(u'after'),
            ],
        )

    @contextmanager
    def _context_manager(self):
        self._mock(u'before')
        yield
        self._mock(u'after')


class TestRemoveNoneValues(TestCase):
    def test_dict(self):
        eq_(
            remove_none_values({'a': 1, 'b': None}),
            {'a': 1},
        )
        eq_(
            remove_none_values({'a': None}),
            {},
        )

    def test_pair_list(self):
        eq_(
            remove_none_values([('a', 1), ('b', 2), ('b', None)]),
            [('a', 1), ('b', 2)],
        )
        eq_(
            remove_none_values([('a', None)]),
            [],
        )


class TestGetDefaultIfNone(TestCase):
    def test_no_key(self):
        eq_(
            get_default_if_none({}, 'foo', 'DEFAULT'),
            'DEFAULT',
        )

    def test_value_is_none(self):
        eq_(
            get_default_if_none({'foo': None}, 'foo', 'DEFAULT'),
            'DEFAULT',
        )

    def test_value_is_false(self):
        eq_(
            get_default_if_none({'foo': False}, 'foo', 'DEFAULT'),
            False,
        )

    def test_value_is_zero(self):
        eq_(
            get_default_if_none({'foo': 0}, 'foo', 'DEFAULT'),
            0,
        )

    def test_value_is_not_none(self):
        eq_(
            get_default_if_none({'foo': 123}, 'foo', 'DEFAULT'),
            123,
        )


class TestNonelessDictValues(TestCase):
    def test_noneless_dict(self):
        eq_(
            noneless_dict(dict([('a', 1), ('b', 2), ('c', None)])),
            dict(a=1, b=2),
        )
        eq_(
            noneless_dict(a=1, b=2, c=None),
            dict(a=1, b=2),
        )
        eq_(
            noneless_dict(a=None),
            {},
        )


class TestFlattenValues(TestCase):
    def test_dict(self):
        eq_(
            flatten_values({'a': 1, 'b': [1, 2, 3]}),
            [('a', 1), ('b', 1), ('b', 2), ('b', 3)],
        )
        eq_(
            flatten_values({'a': None}),
            [('a', None)],
        )

    def test_pair_list(self):
        eq_(
            flatten_values([('a', 1), ('b', [1, 2, 3])]),
            [('a', 1), ('b', 1), ('b', 2), ('b', 3)],
        )
        eq_(
            flatten_values([('a', None)]),
            [('a', None)],
        )


class TestMergeDicts(TestCase):
    def test_ok(self):
        eq_(merge_dicts({'a': 1}, {'b': 1}), {'a': 1, 'b': 1})
        eq_(merge_dicts({'a': 1}, {'a': 1}), {'a': 1})
        eq_(merge_dicts({}, {}), {})
        eq_(merge_dicts({}, {'a': 1}), {'a': 1})
        eq_(merge_dicts({'a': 1}, {}), {'a': 1})


class TestBase64(TestCase):
    TEST_CASES = [
        (b'', b'', b''),
        (b'A', b'QQ', b'QQ'),
        (b'AA', b'QUE', b'QUE'),
        (b'AAA', b'QUFB', b'QUFB'),
        (b'AAAA', b'QUFBQQ', b'QUFBQQ'),
        (b'AAAAA', b'QUFBQUE', b'QUFBQUE'),
        (b'Hello, World!', b'SGVsbG8sIFdvcmxkIQ', b'SGVsbG8sIFdvcmxkIQ'),
        (b'c\xf7>', b'Y_c-', b'Y/c+'),
    ]

    @parameterized.expand(TEST_CASES)
    def test_encode_decode(self, decoded, urlsafe, standard):
        eq_(to_base64_url(decoded), urlsafe)
        eq_(to_base64_standard(decoded), standard)
        eq_(from_base64_url(urlsafe), decoded)
        eq_(from_base64_standard(standard), decoded)


class TestUrlToAscii(TestCase):
    def test_ok(self):
        for from_, to_ in (
            (
                'https://yandex.ru',
                'https://yandex.ru',
            ),
            (
                'https://login:password@yandex.ru:443/path1/path2?param=value#fragment',
                'https://login:password@yandex.ru:443/path1/path2?param=value#fragment',
            ),
            (
                u'https://яндекс.рф',
                'https://xn--d1acpjx3f.xn--p1ai',
            ),
            (
                u'https://логин:пароль@яндекс.рф:443/путь1/путь2/%2F/?параметр=значение#фрагмент',
                (
                    'https://%D0%BB%D0%BE%D0%B3%D0%B8%D0%BD:%D0%BF%D0%B0%D1%80%D0%BE%D0%BB%D1%8C@'
                    'xn--d1acpjx3f.xn--p1ai:443'
                    '/%D0%BF%D1%83%D1%82%D1%8C1/%D0%BF%D1%83%D1%82%D1%8C2/%2F/'
                    '?%D0%BF%D0%B0%D1%80%D0%B0%D0%BC%D0%B5%D1%82%D1%80=%D0%B7%D0%BD%D0%B0%D1%87%D0%B5%D0%BD%D0%B8%D0%B5'
                    '#%D1%84%D1%80%D0%B0%D0%B3%D0%BC%D0%B5%D0%BD%D1%82'
                ),
            ),
        ):
            eq_(
                url_to_ascii(from_),
                to_,
            )


class TestChop(TestCase):
    cases = {
        ('', 1): [],
        ('ab', 1): ['a', 'b'],
        ('abc', 2): ['ab', 'c'],
        ('a', 2): ['a'],
    }
    cases = [(a, e) for a, e in cases.items()]

    @parameterized.expand(cases)
    def test_chop_lists(self, args, expected):
        tail, length = args
        tail = list(tail)
        expected = [list(e) for e in expected]
        eq_(list(chop(tail, length)), expected)

    @parameterized.expand(cases)
    def test_chop_files(self, args, expected):
        tail, length = args
        tail = StringIO('\n'.join(tail))
        expected = [list(e) for e in expected]
        eq_(list(chop(tail, length)), expected)


class TestFlatten(TestCase):
    def test_merge_dict_with_merge_list_policy(self):
        dict_1 = {
            'key-1': 1,
            'key-2': '2',
            'key-3': {
                'key-3-1': 1,
                'key-3-2': '2',
                'key-3-3': {},
                'key-3-4': {},
            },
            'key-4': ['v-1', 'v-2'],
        }
        dict_2 = {
            'key-1': 3,
            'key-3': {
                'key-3-1': 3,
                'key-3-3': 2,
                'key-3-4': {
                    'key-3-4-1': 0,
                }
            },
            'key-4': ['v-3', 'v-4']
        }
        assert smart_merge_dicts(dict_1, dict_2) == {
            'key-1': 3,
            'key-2': '2',
            'key-3': {
                'key-3-1': 3,
                'key-3-2': '2',
                'key-3-3': 2,
                'key-3-4': {
                    'key-3-4-1': 0,
                },
            },
            'key-4': ['v-1', 'v-2', 'v-3', 'v-4'],
        }
        assert dict_1 == {
            'key-1': 1,
            'key-2': '2',
            'key-3': {
                'key-3-1': 1,
                'key-3-2': '2',
                'key-3-3': {},
                'key-3-4': {},
            },
            'key-4': ['v-1', 'v-2'],
        }
        assert dict_2 == {
            'key-1': 3,
            'key-3': {
                'key-3-1': 3,
                'key-3-3': 2,
                'key-3-4': {
                    'key-3-4-1': 0,
                }
            },
            'key-4': ['v-3', 'v-4']
        }

    def test_merge_dict_with_override_list_policy(self):
        dict_1 = {
            'key-1': 1,
            'key-2': '2',
            'key-3': {
                'key-3-1': 1,
                'key-3-2': '2',
                'key-3-3': {},
                'key-3-4': {},
            },
            'key-4': ['v-1', 'v-2'],
        }
        dict_2 = {
            'key-1': 3,
            'key-3': {
                'key-3-1': 3,
                'key-3-3': 2,
                'key-3-4': {
                    'key-3-4-1': 0,
                }
            },
            'key-4': ['v-3', 'v-4']
        }
        assert smart_merge_dicts(dict_1, dict_2, list_policy='override') == {
            'key-1': 3,
            'key-2': '2',
            'key-3': {
                'key-3-1': 3,
                'key-3-2': '2',
                'key-3-3': 2,
                'key-3-4': {
                    'key-3-4-1': 0,
                },
            },
            'key-4': ['v-3', 'v-4'],
        }
        assert dict_1 == {
            'key-1': 1,
            'key-2': '2',
            'key-3': {
                'key-3-1': 1,
                'key-3-2': '2',
                'key-3-3': {},
                'key-3-4': {},
            },
            'key-4': ['v-1', 'v-2'],
        }
        assert dict_2 == {
            'key-1': 3,
            'key-3': {
                'key-3-1': 3,
                'key-3-3': 2,
                'key-3-4': {
                    'key-3-4-1': 0,
                }
            },
            'key-4': ['v-3', 'v-4']
        }

    def test_flatten_unflatten(self):
        d = {
            'a': 'b',
            'c': {
                'd': 'e',
                'd-1': 'e-1',
                'd-2': {
                    'd-3': 'e-3',
                }
            },
            'f': ['e', 'g']
        }
        flattened_d = flatten(d)
        assert flattened_d == {
            'a': 'b',
            'c.d': 'e',
            'c.d-1': 'e-1',
            'c.d-2.d-3': 'e-3',
            'f': ['e', 'g'],
        }
        assert unflatten(flattened_d) == d
