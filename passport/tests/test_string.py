# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from nose_parameterized import parameterized
from passport.backend.utils.string import (
    always_str,
    escape_special_chars_to_unicode_entities,
    escape_unprintable_bytes,
    mask_postfix,
    mask_prefix,
    smart_bytes,
    smart_unicode,
    snake_case_to_camel_case,
)
import six


class TestString(unittest.TestCase):
    def test_escape_unprintable_bytes(self):
        eub = escape_unprintable_bytes
        assert eub('foo') == 'foo'
        assert eub(u'привет') == '\\x43f\\x440\\x438\\x432\\x435\\x442'
        assert eub('\xbb') == '\\xbb'
        assert eub('\n') == '\\x0a'

    def test_mask_prefix(self):
        mp = mask_prefix
        eq_(mp(u'12345', 0), u'*****')
        eq_(mp(u'12345', 1), u'****5')
        eq_(mp(u'12345', 4), u'*2345')
        eq_(mp(u'12345', 5), u'12345')
        eq_(mp(u'12345', 6), u'12345')

        eq_(mp(u'лягушка', 5), u'**гушка')
        if six.PY2:
            eq_(mp('лягушка', 10), '****\xd0\xb3\xd1\x83\xd1\x88\xd0\xba\xd0\xb0')  # '****гушка'

        with assert_raises(ValueError):
            mp(u'12345', -1)

    def test_mask_postfix(self):
        mp = mask_postfix
        eq_(mp(u'12345', 0), u'12345')
        eq_(mp(u'12345', 1), u'1234*')
        eq_(mp(u'12345', 4), u'1****')
        eq_(mp(u'12345', 5), u'*****')
        eq_(mp(u'12345', 6), u'*****')

        eq_(mp(u'лягушка', 5), u'ля*****')
        if six.PY2:
            eq_(mp('лягушка', 10), '\xd0\xbb\xd1\x8f**********')  # 'ля**********'

        with assert_raises(ValueError):
            mp(u'12345', -1)

    def test_escape_to_unicode_entities(self):
        eq_(
            escape_special_chars_to_unicode_entities('Chip & Dale'),
            'Chip \\u0026 Dale',
        )

    def test_escape_to_unicode_entities__idempotent(self):
        attack_vector = '<script>alert("hacked %)")</script>'
        expected_escaped = '\\u003cscript\\u003ealert(\\u0022hacked %)\\u0022)\\u003c/script\\u003e'

        # экранируем один раз
        eq_(
            escape_special_chars_to_unicode_entities(attack_vector),
            expected_escaped,
        )

        # экранируем два раза, результат не меняется
        eq_(
            escape_special_chars_to_unicode_entities(
                escape_special_chars_to_unicode_entities(attack_vector)
            ),
            expected_escaped,
        )

    def test_snake_case_to_camel_case(self):
        cases = [
            ('', False, ''),
            ('_', False, ''),
            ('_____', False, ''),
            ('first', False, 'First'),
            ('camel_case_string', False, 'CamelCaseString'),
            ('', True, ''),
            ('_', True, ''),
            ('_____', True, ''),
            ('first', True, 'first'),
            ('lower_camel_case_string', True, 'lowerCamelCaseString'),
        ]
        for original, first_lower, result in cases:
            eq_(
                snake_case_to_camel_case(original, first_lower=first_lower),
                result,
            )

    def test_smart_unicode_bytes(self):
        assert smart_unicode(b'bytes') == six.text_type('bytes')

    def test_smart_unicode_object__no_str(self):
        class SomeObject(object):
            pass

        some_object = SomeObject()
        assert smart_unicode(some_object) == six.text_type(repr(some_object))

    def test_smart_unicode_object__str(self):
        class SomeObject(object):
            def __str__(self):
                return 'hi there'

        some_object = SomeObject()
        assert smart_unicode(some_object) == six.text_type('hi there')

    def test_smart_unicode_text(self):
        if six.PY2:
            assert smart_unicode(u'Тест') == u'Тест'
        else:
            assert smart_unicode('Тест') == 'Тест'

    @parameterized.expand([
        (smart_unicode('тест'), 'тест'),
        (smart_bytes('тест'), 'тест'),
        (1, '1'),
    ])
    def test_always_str(self, value, expected_value):
        eq_(always_str(value), expected_value)
