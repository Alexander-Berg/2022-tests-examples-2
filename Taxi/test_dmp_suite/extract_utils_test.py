from datetime import datetime
from unittest import TestCase

import pytest
from mock import patch

from dmp_suite import extract_utils as eu


def test_strip_extractor():
    assert eu.strip_extractor(dict(field='1a'), 'field') == '1a'
    assert eu.strip_extractor(dict(field=' 1a '), 'field') == '1a'
    assert eu.strip_extractor(dict(field=' 1a 1a '), 'field') == '1a 1a'
    assert eu.strip_extractor(dict(field='1a'), 'wrong_field') is None
    assert eu.strip_extractor(dict(field=None), 'field') is None
    assert eu.strip_extractor(dict(field=''), 'field') == ''
    assert eu.strip_extractor(dict(field='  '), 'field') == ''
    with pytest.raises(AttributeError):
        eu.strip_extractor(dict(field=1), 'field')
    with pytest.raises(AttributeError):
        eu.strip_extractor(dict(field=['1', '2', '3']), 'field')


def test_lower_case_extractor():
    assert eu.lower_case_extractor(dict(field='1a'), 'field') == '1a'
    assert eu.lower_case_extractor(dict(field=''), 'field') == ''
    assert eu.lower_case_extractor(dict(field='aaBBBaa'), 'field') == 'aabbbaa'
    assert eu.lower_case_extractor(dict(field='aaBBBaa'), 'wrong_field') is None
    assert eu.lower_case_extractor(dict(field=None), 'field') is None
    with pytest.raises(AttributeError):
        eu.lower_case_extractor(dict(field=1), 'field')
    with pytest.raises(AttributeError):
        eu.lower_case_extractor(dict(field=['1', '2', '3']), 'field')


def test_parse_path():
    assert ('a',) == eu.parse_path('a')
    assert ('a', 'b') == eu.parse_path('a.b')
    assert ('a', 'b', 1) == eu.parse_path('a.b.1')
    assert ('a', 'b', -2) == eu.parse_path('a.b.-2')
    assert ('a', 1, -2, 'b') == eu.parse_path('a.1.-2.b')
    assert (1, ) == eu.parse_path('1')

    with pytest.raises(ValueError):
        eu.parse_path(None)

    with pytest.raises(ValueError):
        eu.parse_path('')


def test_path_extractor():
    extract = eu.path_extractor(path='a')
    assert extract(dict()) is None
    assert 1 == extract(dict(a=1))
    assert '1' == extract(dict(a='1'))
    assert 0 == extract(dict(a=0))

    extract = eu.path_extractor(path='1')
    assert extract(dict()) is None
    assert extract({'1': 1}) is None
    assert 2 == extract([1, 2, 3])
    assert 0 == extract([1, 0, 3])

    extract = eu.path_extractor(path='-2')
    assert 2 == extract([1, 2, 3])

    extract = eu.path_extractor(path='a', converter=int)
    assert extract(dict()) is None
    assert 1 == extract(dict(a='1'))
    assert extract(dict(a=None)) is None
    assert extract(dict(a='abc')) is None

    extract = eu.path_extractor(path='a', converter=str)
    assert extract(dict()) is None
    assert '' == extract(dict(a=''))
    assert 'a' == extract(dict(a='a'))

    extract = eu.path_extractor(path='a', default_value=1)
    assert 1 == extract(dict())
    assert '1' == extract(dict(a='1'))
    assert 2 == extract(dict(a=2))
    assert 1 == extract(dict(a=None))
    assert 0 == extract(dict(a=0))

    extract = eu.path_extractor(path='a', default_value=1, converter=int)
    assert 1 == extract(dict())
    assert 1 == extract(dict(a=None))
    assert 1 == extract(dict(a='1'))
    assert 2 == extract(dict(a='2'))
    assert 1 == extract(dict(a='avc'))
    assert 2 == extract(dict(a=2.2))

    extract = eu.path_extractor(path='a.a')
    assert 1 == extract(dict(a=dict(a=1)))
    assert 0 == extract(dict(a=dict(a=0)))

    extract = eu.path_extractor(path='a.a.a')
    assert extract(dict(a=dict())) is None

    extract = eu.path_extractor(path='a.1')
    assert 1 == extract(dict(a=[2, 1]))

    extract = eu.path_extractor(path='a.-1')
    assert 1 == extract(dict(a=[3, 2, 1]))
    assert extract(dict(a=[])) is None

    extract = eu.path_extractor(path='a.-1.1')
    assert 2 == extract(dict(a=[[1, 2]]))

    extract = eu.path_extractor(path='a.-1.1.b')
    assert 3 == extract(dict(a=[[], [1, dict(b=3)]]))

    extract = eu.path_extractor(('a', 1, 'b'))
    assert 10 == extract(dict(a=[dict(), dict(b=10)]))


def test_caching_path_extractor_create_path_extractor_once():
    with patch('dmp_suite.extract_utils.PathExtractor') as path_extractor_mock:
        class PathExtractorMock(object):
            def __call__(self, data, default_value=None, converter=None):
                return 10

        path_extractor_mock.return_value = PathExtractorMock()
        extract = eu.CachingPathExtractor()

        assert 10 == extract({}, 'a.b.c')
        path_extractor_mock.assert_called_once_with('a.b.c')
        assert 10 == extract({}, 'a.b.c')
        path_extractor_mock.assert_called_once_with('a.b.c')


def test_caching_path_extractor_path_only():
    extract = eu.CachingPathExtractor()
    assert extract(dict(), 'a') is None
    assert extract(dict(b=10), 'a') is None
    assert 10 == extract(dict(a=10), 'a')
    assert 'a' == extract(dict(a='a'), 'a')
    assert 0 == extract(dict(a=0), 'a')


def test_caching_path_extractor_default_value():
    extract = eu.CachingPathExtractor()
    assert 5 == extract(dict(), 'a', default_value=5)
    assert 15 == extract(dict(a=15), 'a', default_value=5)
    assert 0 == extract(dict(a=0), 'a', default_value=5)


def test_caching_path_extractor_int_converter():
    extract = eu.CachingPathExtractor()
    assert extract(dict(), 'a', converter=int) is None
    assert extract(dict(a='abc'), 'a', converter=int) is None
    assert 25 == extract(dict(a='25'), 'a', converter=int)
    assert 0 == extract(dict(a=0), 'a', converter=int)


def test_caching_path_extractor_str_converter():
    extract = eu.CachingPathExtractor()
    assert extract(dict(), 'a', converter=str) is None
    assert '' == extract(dict(a=''), 'a', converter=str)
    assert 'b' == extract(dict(a='b'), 'a', converter=str)


def test_caching_path_extractor_converter_and_default_value():
    extract = eu.CachingPathExtractor()
    assert 5 == extract(dict(), 'a', default_value=5, converter=int)
    assert 5 == extract(dict(a='abc'), 'a', default_value=5, converter=int)
    assert 20 == extract(dict(a='20'), 'a', default_value=5, converter=int)
    assert 0 == extract(dict(a=0), 'a', default_value=5, converter=int)


class TestExtractUtils(TestCase):
    def test_delimiter_extractor_factory(self):
        extractor = eu.delimiter_extractor_factory('-', '_')
        data = {'simple-field': 'qwerty', 'field': 'ytrewq'}
        self.assertEqual(extractor(data, 'simple_field'), 'qwerty')
        self.assertEqual(extractor(data, 'field'), 'ytrewq')

    def test_multi_format_date_extractor(self):
        extractor = eu.MultiFormatDateExtractor()

        result = datetime(2017, 3, 23)

        # test YYYYMMDD
        self.assertEqual(extractor({'dttm': '2017-03-23'}, 'dttm'),
                         result)
        self.assertEqual(extractor({'dttm': ' 2017-03-23    '}, 'dttm'),
                         result)
        self.assertEqual(extractor({'dttm': '2017.03.23'}, 'dttm'),
                         result)
        self.assertEqual(extractor({'dttm': ' 2017.03.23 '}, 'dttm'),
                         result)

        # test DDMMYYYY
        self.assertEqual(extractor({'dttm': '23-03-2017'}, 'dttm'),
                         result)
        self.assertEqual(extractor({'dttm': '   23-03-2017 '}, 'dttm'),
                         result)
        self.assertEqual(extractor({'dttm': '23.03.2017'}, 'dttm'),
                         result)
        self.assertEqual(extractor({'dttm': ' 23.03.2017 '}, 'dttm'),
                         result)

        # test invalid format
        self.assertIsNone(extractor({'dttm': '03-2017'}, 'dttm'))
        self.assertIsNone(extractor({'dttm': None}, 'dttm'))
        self.assertIsNone(extractor({'dttm': '201703'}, 'dttm'))
        self.assertIsNone(extractor({'dttm': ''}, 'dttm'))
        self.assertIsNone(extractor({'dttm': ' '}, 'dttm'))
        self.assertIsNone(extractor({'dttm': '/n'}, 'dttm'))

    def test_extract_value(self):
        data = {
            'key1': 'foo',
            'key2': ['bar'],
            'nested': [['a', 'b', 'c'], ['d', ['e', {'f': 'g'}]]]
        }

        def test_extract(path, expected):
            self.assertEqual(
                eu.extract_value(data, path),
                expected
            )

        test_extract('key1', 'foo')
        test_extract('key2', ['bar'])
        test_extract('key2.0', 'bar')
        test_extract('nested.0.0', 'a')
        test_extract('nested.0.1', 'b')
        test_extract('nested.1.1.1.f', 'g')

        test_extract('nokey', None)
        test_extract('nested.0.1000', None)
        test_extract('nested.1000.0', None)
        test_extract('nested.1.1.nokey', None)

    def test_liter_eval_extractor(self):
        field = 'a'

        def create_data(s):
            return {field: s}

        extractor = eu.literal_eval_extractor()

        actual = extractor(create_data('[1, 2, 3]'), field)
        expected = [1, 2, 3]
        self.assertListEqual(expected, actual)

        actual = extractor(create_data("['1', '2', '3']"), field)
        expected = ['1', '2', '3']
        self.assertListEqual(expected, actual)

        self.assertIsNone(extractor(create_data(None), field))

    def test_apply_extractor(self):
        extract = eu.apply_extractor(int, 'f')
        self.assertRaises(TypeError, extract, dict())
        self.assertRaises(TypeError, extract, dict(a=1))
        self.assertRaises(TypeError, extract, dict(f=None))
        self.assertRaises(ValueError, extract, dict(f='a'))
        self.assertEqual(1, extract(dict(f=1)))
        self.assertEqual(10, extract(dict(f='10')))
        self.assertEqual(20, extract(dict(f=20.2)))

    def test_safe_apply_extractor(self):
        extract = eu.safe_apply_extractor(func=int, name='f', exceptions=())
        self.assertRaises(TypeError, extract, dict())
        self.assertRaises(TypeError, extract, dict(f=None))
        self.assertRaises(TypeError, extract, dict(a=2))
        self.assertRaises(ValueError, extract, dict(f='a'))
        self.assertEqual(1, extract(dict(f='1')))
        self.assertEqual(2, extract(dict(f=2.0)))
        self.assertEqual(3, extract(dict(f=3)))

        extract = eu.safe_apply_extractor(func=int,
                                          name='f',
                                          exceptions=(TypeError,))
        self.assertIsNone(extract(dict()))
        self.assertIsNone(extract(dict(f=None)))
        self.assertRaises(ValueError, extract, dict(f='a'))

        extract = eu.safe_apply_extractor(func=int,
                                          name='f',
                                          exceptions=(ValueError,))
        self.assertRaises(TypeError, extract, dict())
        self.assertRaises(TypeError, extract, dict(f=None))
        self.assertIsNone(extract(dict(f='a')))

        extract = eu.safe_apply_extractor(int, name='f')
        self.assertIsNone(extract(dict()))
        self.assertIsNone(extract(dict(f='a')))
        self.assertIsNone(extract(dict(f=None)))
        self.assertEqual(1, extract(dict(f='1')))

        extract = eu.safe_apply_extractor(int, name='f', default_value=2)
        self.assertEqual(2, extract(dict()))
        self.assertEqual(2, extract(dict(f='a')))
        self.assertEqual(2, extract(dict(f=None)))
        self.assertEqual(1, extract(dict(f='1')))

    def test_extractor_with_fallback(self):
        extract = eu.extractor_with_fallback(eu.path_extractor("a"), eu.path_extractor("b"))
        assert extract(dict()) is None
        assert extract(dict(a=1)) is 1
        assert extract(dict(b=2)) is 2
        assert extract(dict(a=1, b=2)) is 1
        assert extract(dict(c=3)) is None

        lambda_extract = eu.extractor_with_fallback(lambda _: "success",
                                                    lambda _: "not supposed to happen")
        assert lambda_extract(dict(a=1)) is "success"

        very_large_extractor_chain = eu.extractor_with_fallback(*([lambda _: None] * 100000 + [eu.path_extractor("a")]))

        assert very_large_extractor_chain(dict(a=1)) is 1


class TestCoalesceExtractor:
    @pytest.mark.parametrize('doc, fields, expected', [
        (dict(), ('a',), None),
        (dict(a=None), ('a',), None),
        (dict(a=''), ('a',), ''),
        (dict(a=1), ('a',), 1),
        (dict(a=None, b=2, c=None), ('a', 'b', 'c'), 2),
        (dict(b=2, c=None), ('a', 'b', 'c'), 2),
        (dict(a=1, b=2, c=3), ('a', 'b', 'c'), 1),
        (dict(a=None, b=None, c=3), ('a', 'b', 'c'), 3),
        (dict(c=3), ('a', 'b', 'c'), 3),
    ])
    def test_coalesce_extractor(self, doc, fields, expected):
        actual = eu.coalesce_extractor(*fields)(doc)
        assert actual == expected

    @pytest.mark.parametrize('doc, fields, default, expected', [
        (dict(), ('a',), 1, 1),
        (dict(a=None), ('a',), 1, 1),
        (dict(a=1), ('a',), None, 1),
        (dict(a=1), ('a',), 2, 1),
        (dict(a=''), ('a',), 1, ''),
        (dict(), ('a', 'b', 'c'), 1, 1),
    ])
    def test_coalesce_extractor_default(self, doc, fields, default, expected):
        actual = eu.coalesce_extractor(*fields, default_value=default)(doc)
        assert actual == expected

    def test_coalesce_extractor_wrong_arguments(self):
        with pytest.raises(ValueError):
            eu.coalesce_extractor()
