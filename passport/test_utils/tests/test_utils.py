# -*- coding: utf-8 -*-

from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.test.test_utils.form_utils import check_error_codes
from passport.backend.core.test.test_utils.utils import (
    _Call,
    check_all_url_params_match,
    check_url_contains_params,
    check_url_equals,
    last_call,
    nth_call,
    PassportTestCase,
    traverse_dict_from_leaves_to_root,
    with_settings,
    with_settings_hosts,
)
from passport.backend.core.validators.base import Invalid


def test_check_error_codes_fails_when_no_error():
    with assert_raises(AssertionError):
        form = mock.Mock()
        check_error_codes(form, (), {'a': 'b'})


def test_check_error_code_with_error_list():
    form = mock.Mock()
    form.to_python.side_effect = Invalid('message',
                                         {},
                                         None,
                                         error_dict={'field': Invalid('message',
                                                                      {},
                                                                      None,
                                                                      error_list=[Invalid(('code1', 'message'), {}, None),
                                                                                  Invalid(('code2', 'message'), {}, None)])})
    check_error_codes(form, (), {'field': ['code1', 'code2']})


def test_check_error_code_with_error_dict():
    form = mock.Mock()
    form.to_python.side_effect = Invalid('message',
                                             {},
                                             None,
                                             error_dict={'field1': Invalid(('code1', 'message'), {}, None),
                                                         'field2': Invalid(('code2', 'message'), {}, None)})
    check_error_codes(form, (), {'field1': 'code1', 'field2': 'code2'})


def test_check_error_code_err_condition():
    with assert_raises(AssertionError):
        form = mock.Mock()
        form.to_python.side_effect = Invalid('message',
                                             {},
                                             None,
                                             error_dict={'field1': Invalid(('code1', 'message'), {}, None),
                                                         'field2': Invalid(('code2', 'message'), {}, None)})
        check_error_codes(form, (), {'field1': ['code1', 'code2'], 'field2': 'code2'})


def test_check_url_contains_params():
    check_url_contains_params('http://ya.ru/?k1=v1&k2=v2&k3=v3', {
        'k1': 'v1',
        'k2': 'v2',
    })


def test_check_url_contains_params_err_missing_key():
    with assert_raises(AssertionError):
        check_url_contains_params(
            'http://ya.ru/?k1=v1&k2=v2&k3=v3',
            {
                'k4': 'v4',
            },
        )


def test_check_url_contains_params_err_not_equal_value():
    with assert_raises(AssertionError):
        check_url_contains_params(
            'http://ya.ru/?k1=v1&k2=v2&k3=v3',
            {
                'k1': 'v2',
            },
        )


def test_check_all_url_params_match():
    check_all_url_params_match('http://ya.ru/?k1=v1&k2=v2&k3=v3', {
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
    })


def test_check_all_url_params_match_with_unicode():
    check_all_url_params_match('http://ya.ru/?k1=v1&k2=v2&ping=%D0%BF%D0%BE%D0%BD%D0%B3', {
        'k1': 'v1',
        'k2': 'v2',
        'ping': u'понг',
    })


def test_check_all_url_params_match_with_unicode_url():
    check_all_url_params_match(u'http://ya.ru/?k1=v1&k2=v2&ping=%D0%BF%D0%BE%D0%BD%D0%B3', {
        'k1': 'v1',
        'k2': 'v2',
        'ping': u'понг',
    })


def test_check_all_url_params_match_err1():
    """Нехватает параметров в строке запроса"""
    with assert_raises(AssertionError):
        check_all_url_params_match('http://ya.ru/?k1=v1&k2=v2', {
            'k1': 'v1',
            'k2': 'v2',
            'k3': 'v3',
        })


def test_check_all_url_params_match_err2():
    """Нехватает параметров в ожидаемом словаре"""
    with assert_raises(AssertionError):
        check_all_url_params_match('http://ya.ru/?k1=v1&k2=v2&k3=v3', {
            'k1': 'v1',
            'k2': 'v2',
        })


class CallTestMixin(object):
    def test_arg(self):
        eq_(self.call.arg(0), 1)

    def test_nonexistent_arg(self):
        with assert_raises(AssertionError):
            self.call.arg(100)

    def test_kwarg(self):
        eq_(self.call.kwarg('foo'), 3)

    def test_nonexistennt_kwarg(self):
        with assert_raises(AssertionError):
            self.call.kwarg('bar')


class TestCallWithoutName(TestCase, CallTestMixin):
    def setUp(self):
        self.call = _Call(
            (
                (1, 2),
                {'foo': 3},
            ),
        )

    def tearDown(self):
        del self.call


class TestCallWithName(TestCase, CallTestMixin):
    def setUp(self):
        self.call = _Call(
            (
                'call_name',
                (1, 2),
                {'foo': 3},
            ),
        )

    def tearDown(self):
        del self.call


class TestNthCallWithCalls(TestCase):
    def setUp(self):
        self.call = mock.Mock()
        self.call(1)
        self.call(2)

    def tearDown(self):
        del self.call

    def test_first_call(self):
        eq_(nth_call(self.call, 0), mock.call(1))

    def test_nonexistent_call(self):
        with assert_raises(AssertionError):
            nth_call(self.call, 100)


class TestNthCallWithoutCalls(TestCase):
    def setUp(self):
        self.call = mock.Mock()

    def tearDown(self):
        del self.call

    def test_raises_assertion_error_on_any_call(self):
        with assert_raises(AssertionError):
            nth_call(self.call, 0)


class TestLastCall(TestCase):
    def setUp(self):
        self.nth_call_patcher = mock.patch('passport.backend.core.test.test_utils.utils.nth_call')
        self.nth_call = self.nth_call_patcher.start()
        self.call = mock.Mock()

    def tearDown(self):
        self.nth_call_patcher.stop()
        del self.nth_call
        del self.nth_call_patcher
        del self.call

    def test_uses_nth_call(self):
        last_call(self.call)
        ok_(self.nth_call.called_with_args(self.call, -1))


class TestCheckUrlEquals(TestCase):
    def test_equal(self):
        check_url_equals(
            'http://check.url.equals/hello/world?foo=1&bar=3&foo=2',
            'http://check.url.equals/hello/world?foo=1&foo=2&bar=3',
        )
        check_url_equals(
            u'http://check.url.equals/hello/world?foo=%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82',
            'http://check.url.equals/hello/world?foo=%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82',
        )
        check_url_equals(
            'http://check.url.equals/hello/world?foo=%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82',
            u'http://check.url.equals/hello/world?foo=%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82',
        )

    def test_different_schemes(self):
        with assert_raises(AssertionError):
            check_url_equals(
                'http://check.url.equals/',
                'https://check.url.equals/',
            )

    def test_different_netloc(self):
        with assert_raises(AssertionError):
            check_url_equals(
                'http://check.url.equals/',
                'http://karma.police/',
            )

    def test_different_path(self):
        with assert_raises(AssertionError):
            check_url_equals(
                'http://check.url.equals/foo/',
                'http://check.url.equals/bar/',
            )

    def test_different_params(self):
        with assert_raises(AssertionError):
            check_url_equals(
                'http://check.url.equals/;foo=1;bar=2',
                'http://check.url.equals/;foo=2;bar=1',
            )

    def test_different_query(self):
        with assert_raises(AssertionError):
            check_url_equals(
                'http://check.url.equals/?foo=1',
                'http://check.url.equals/?bar=2',
            )


@with_settings_hosts(C=1024)
@with_settings_hosts(C=512)
@with_settings(B=12345)
@with_settings(A=42, B=43)
class TestStackedSettings(PassportTestCase):
    '''
    Проверяем, что переопределяемые моки настроек работают со специальным
    тест-кейсом Паспорта
    '''
    def test_ok(self):
        from passport.backend.core.conf import settings
        eq_(settings.A, 42)
        eq_(settings.B, 12345)
        eq_(settings.C, 1024)


@with_settings(B=12345)
@with_settings(A=42, B=43)
class TestStackedSettingsWontWorkForUsualTestCase(TestCase):
    '''
    Проверяем, что переопределяемые моки настроек не затрагивают стандартное
    поведение
    '''
    def test_ok(self):
        from passport.backend.core.conf import settings
        eq_(settings.A, 42)
        eq_(settings.B, 43)


class TestTraverseDictFromLeavesToRoot(TestCase):
    def _assert_dict_traversed_in_order(self, main_dict, leaf_paths):
        actual = list(traverse_dict_from_leaves_to_root(main_dict))

        expected = []
        for leaf_path in leaf_paths:
            expected.append(self._main_dict_and_leaf_path_to_sub_dict_and_key(main_dict, leaf_path))

        eq_(actual, expected)

    def _main_dict_and_leaf_path_to_sub_dict_and_key(self, main_dict, leaf_path):
        leaf_key = leaf_path[-1]
        container = main_dict
        for key in leaf_path[:-1]:
            container = container[key]
        return container, leaf_key

    def test_three_level_nesting(self):
        self._assert_dict_traversed_in_order(
            {
                'a': 1,
                'b': {
                    'c': {
                        'e': 5,
                        'f': 6,
                    },
                    'd': 4,
                },
            },
            ['bce', 'bcf', 'bc', 'bd', 'a', 'b'],
        )

    def test_no_nesting(self):
        self._assert_dict_traversed_in_order({'a': 1, 'b': 2}, ['a', 'b'])

    def test_empty(self):
        self._assert_dict_traversed_in_order(dict(), [])
