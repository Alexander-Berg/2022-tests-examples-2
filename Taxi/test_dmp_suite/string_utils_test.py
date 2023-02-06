# coding: utf-8
import re
import pytest
import unittest

from dmp_suite import string_utils as su
import dmp_suite.yql as yql_utils
from dmp_suite.string_utils import underscore_to_camelcase


class TestStringUtils(unittest.TestCase):
    def assertEqualValueAndType(self, actual, expected, message=None):
        self.assertIs(type(actual), type(expected), message)
        self.assertEqual(actual, expected, message)

    def test_transliterate_by_view(self):
        ru_str = u'ХАЙУ-Хай!'.encode('utf-8')
        ru_str_u = u'ХАЙУ-Хай!'
        en_str = u'XAЙY-Xай!'.encode('utf-8')
        en_str_u = u'XAЙY-Xай!'
        self.assertEqualValueAndType(
            su.transliterate_uppercase_by_view(ru_str, 'ru', 'en'), en_str_u
        )
        self.assertEqualValueAndType(
            su.transliterate_uppercase_by_view(ru_str, 'en', 'ru'), ru_str_u
        )
        self.assertEqualValueAndType(
            su.transliterate_uppercase_by_view(en_str, 'en', 'ru'), ru_str_u
        )
        self.assertEqualValueAndType(
            su.transliterate_uppercase_by_view(en_str, 'ru', 'en'), en_str_u
        )
        self.assertEqualValueAndType(
            su.transliterate_uppercase_by_view(ru_str_u, 'ru', 'en'), en_str_u
        )
        self.assertEqualValueAndType(
            su.transliterate_uppercase_by_view(en_str_u, 'en', 'ru'), ru_str_u
        )

    def test_remove_non_alphanumeric(self):
        self.assertEqualValueAndType(
            su.remove_non_alphanumeric(u'АБВ ГДЕ 1!'.encode('utf-8')), u'АБВГДЕ1'
        )
        self.assertEqualValueAndType(
            su.remove_non_alphanumeric(u'АБВ XYZ 2!?'), u'АБВXYZ2'
        )

    def test_apply_other_replacement_rules(self):
        self.assertEqualValueAndType(
            su.apply_other_replacement_rules(u'З'.encode('utf-8'), 'ru'), u'3'
        )
        self.assertEqualValueAndType(
            su.apply_other_replacement_rules(u'З'.encode('utf-8'), 'en'), u'З'
        )
        self.assertEqualValueAndType(
            su.apply_other_replacement_rules(u'З', 'ru'), u'3'
        )
        self.assertEqualValueAndType(
            su.apply_other_replacement_rules(u'З', 'en'), u'З'
        )
        self.assertEqualValueAndType(
            su.apply_other_replacement_rules(u'А'.encode('utf-8'), 'en'), u'А'
        )
        self.assertEqualValueAndType(
            su.apply_other_replacement_rules(u'А'.encode('utf-8'), 'ru'), u'А'
        )
        self.assertEqualValueAndType(
            su.apply_other_replacement_rules(u'А', 'en'), u'А'
        )
        self.assertEqualValueAndType(
            su.apply_other_replacement_rules(u'А', 'ru'), u'А'
        )

    def test_normalize(self):
        self.assertEqualValueAndType(su.normalize(b''), u'')
        self.assertEqualValueAndType(su.normalize(u''), u'')
        self.assertEqualValueAndType(su.normalize(None), None)
        self.assertEqualValueAndType(su.normalize(u'авс'), u'ABC')
        self.assertEqualValueAndType(su.normalize(u'авс'.encode('utf-8')), u'ABC')
        self.assertEqualValueAndType(su.normalize(u'abc', 'en', 'ru'), u'АВС')
        self.assertEqualValueAndType(su.normalize(u'abc'.encode('utf-8'), 'en', 'ru'), u'АВС')
        self.assertRaises(AttributeError, su.normalize, 0)

    @pytest.mark.slow
    def test_use_as_YQL_UDF_script(self):
        from textwrap import dedent
        transliteration_script_alias = 'transliteration.py'
        test_query = (
            yql_utils.YqlSelect
                .from_string(
                    dedent(
                        """
                        $test_driver_license = '{driver_license}';
    
                        $transliteration_script =
                            FileContent('{transliteration_script_alias}');
                        $normalize_driver_license =
                            Python3::normalize(
                                Callable<(String?)->String?>, 
                                $transliteration_script
                            );
    
                        select 
                            $normalize_driver_license($test_driver_license)
                                as result_driver_license;
                        """
                    )
                )
                .add_params(
                    driver_license=u'УКЕНТРАЯК1234 : YKEHTPAЯK1234',
                    transliteration_script_alias=transliteration_script_alias
                )
                .attach_file(
                    yql_utils.PythonScriptAttachment.from_module(
                        su,
                        alias=transliteration_script_alias
                    )
                )
        )
        result = test_query.get_one_data_dict()['result_driver_license']
        self.assertEqualValueAndType(result, 'YKEHTPAЯK1234YKEHTPAЯK1234')

    def test_to_unicode(self):
        str_ = u'åß∂ƒ1234'.encode('utf-8')
        converted = su.to_unicode(str_)
        decoded = str_.decode('utf-8')
        unicode_ = u'åß∂ƒ1234'
        self.assertEqual(decoded, converted)
        self.assertEqual(unicode_, converted)
        self.assertRaises(TypeError, su.to_unicode, None)

    def test_to_unicode_with_ignore(self):
        self.assertEqual(su.to_unicode(b'\xd1\x82\xd0\xd1\x81\xd1\x82', errors='ignore'), u'тст')
        self.assertEqual(su.to_unicode(b'\xd1\x82\xd0\xd1\x81\xd1\x82', errors='replace'), u'т�ст')

    def test_truncate(self):
        str_value = u'åß∂ƒ1234'.encode('utf-8')
        truncated_str = su.truncate(str_value, 3)
        expected_result = u'åß∂'
        self.assertEqual(truncated_str, expected_result)

        unicode_value = u'åß∂ƒ1234'
        truncated_unicode = su.truncate(unicode_value, 3)
        self.assertEqual(truncated_unicode, expected_result)

        self.assertRaises(TypeError, su.truncate, None, 3)

    def test_ensure_utf8(self):
        def assert_the_same(value, decoded=True):
            if decoded:
                _ = lambda v: v.decode('utf8')
            else:
                _ = lambda v: v

            self.assertEqual(su.ensure_utf8(value), _(value))

            data = {'key': value}
            self.assertEqual(su.ensure_utf8(data), {'key': _(value)})

            data = [value]
            self.assertEqual(su.ensure_utf8(data), [_(value)])

        def assert_is_none(value):
            self.assertIs(su.ensure_utf8(value), None)

            data = {'key': value}
            self.assertEqual(su.ensure_utf8(data), {'key': None})

            data = [value]
            self.assertEqual(su.ensure_utf8(data), [None])

        assert_is_none(None)
        assert_is_none(b'\xed\xa6\x80')
        assert_is_none(b'\xed\xa0\x80')
        assert_is_none(b'\xed\xbf\xbf')
        assert_is_none(b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82\xed\xa6\x80')
        assert_is_none(b'Mozilla/5.0 \\u0016e-\xcc\xb6\xc4; WEXLER-TAB')

        assert_the_same(b'')
        assert_the_same(10, False)
        assert_the_same(b'Hello')
        assert_the_same(b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82!')
        assert_the_same(b'\xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82!Hello!')


@pytest.mark.parametrize('text, expected', [
    ('hello', 'Hello'),
    ('hello_world', 'HelloWorld'),
    ('helloWorld', 'HelloWorld'),
    ('_', '_'),
    ('__name__', 'Name'),
])
def test_underscore_to_camelcase(text, expected):
    assert expected == underscore_to_camelcase(text)


@pytest.mark.parametrize(
    'text, expected, uppercase_first_letter', [
        ('hello', 'Hello', True),
        ('hello', 'hello', False),
        ('hello__world', 'HelloWorld', True),
        ('hello__world', 'helloWorld', False),
        ('hello___world', 'HelloWorld', True),
        ('hello___world', 'helloWorld', False),
        ('__hello___world__', 'HelloWorld', True),
        ('__hello___world__', 'helloWorld', False),
    ]
)
def test_underscore_to_camelcase_modifiers(
        text,
        expected,
        uppercase_first_letter,
):
    actual = underscore_to_camelcase(
        text,
        upper_first_letter=uppercase_first_letter,
    )
    assert actual == expected


def test_repr_html_calls_magic():
    # Функция repr_html должна либо вызывать на объекте
    # magic метод _repr_html_, если он есть.
    # а если нет, то вызывать обычный repr и эскейпить спецсимволы так,
    # чтобы они не ломали HTML разметку.

    class WithHtmlRepr():
        def _repr_html_(self):
            return '<b>Hello World!</b>'

    assert su.repr_html(WithHtmlRepr()) == '<b>Hello World!</b>'

    class WithPlainRepr():
        def __repr__(self):
            return '<Hello World!>'

    assert su.repr_html(WithPlainRepr()) == '&lt;Hello World!&gt;'

    class WithoutRepr():
        pass

    assert re.match(
        r'&lt;test_dmp_suite.string_utils_test.test_repr_html_calls_magic.&lt;locals&gt;.WithoutRepr object at 0x.*&gt;',
        su.repr_html(WithoutRepr())
    )


def test_repr_html_for_functions():
    # Функция repr_html должна отдавать имя функции
    # если ей передана функция. Для lambda имени нет,
    # поэтому для неё должно отдаваться заэскейпленное
    # значение <lambda>.

    def some_func(blah, **kargs):
        pass

    assert su.repr_html(some_func) == 'some_func'

    some_lambda = lambda blah, **kargs: None

    assert su.repr_html(some_lambda) == '&lt;lambda&gt;'


def test_truncate_text():

    assert su.truncate_text('123456789', 6) == '123...'
    assert su.truncate_text('123456789', 8, '>>>') == '12345>>>'
    with pytest.raises(AssertionError):
        su.truncate_text('123456789', 1, '>>>')


def test_undo_escape():
    assert su.undo_escape(r'\n\t\v\\') == '\n\t\v\\'
    assert su.undo_escape(r'\x55nicode') == 'Unicode'


def test_format_string_has_key_wrong_key():
    with pytest.raises(ValueError):
        su.format_string_has_key('', '')


@pytest.mark.parametrize('string, key, result', [
    ('', 'a', False),
    ('adf {}', 'a', False),
    ('adf {b}', 'a', False),
    ('adf {a}', 'a', True),
    ('adf {a} {b}', 'a', True),
    ('adf {a} {b}', 'b', True),
])
def test_format_string_has_key(string, key, result):
    assert su.format_string_has_key(string, key) is result
