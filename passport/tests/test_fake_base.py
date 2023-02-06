# -*- coding: utf-8 -*-

import json
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.base.base import (
    BaseBuilder,
    RequestInfo,
)
from passport.backend.core.builders.base.faker.fake_builder import (
    assert_builder_cookies_equal,
    assert_builder_data_equals,
    assert_builder_headers_equal,
    assert_builder_requested,
    assert_builder_url_contains_params,
    BaseFakeBuilder,
    FakedRequest,
)
from passport.backend.utils.common import identity
import six
from six import StringIO


class BuilderForTest(BaseBuilder):
    def __init__(self):
        logger = mock.Mock(u'logger')
        logger.debug = mock.Mock()

        super(BuilderForTest, self).__init__(
            url=u'http://builder/test/',
            timeout=10,
            retries=2,
            logger=logger,
            useragent=mock.Mock(u'useragent'),
        )

    def method(self):
        return self._request_with_retries(
            u'GET',
            RequestInfo(u'http://builder/test/method', None, None),
            identity,
        )


class FakeBuilderForTest(BaseFakeBuilder):
    def __init__(self):
        super(FakeBuilderForTest, self).__init__(BuilderForTest)

    @staticmethod
    def parse_method_from_request(http_method, url, data, headers=None):
        if (http_method == u'GET' and
                url == u'http://builder/test/method'):
            return u'method'


class BaseAssertBuilderTestCase(TestCase):
    def setUp(self):
        self.builder = BuilderForTest()
        self.faker = FakeBuilderForTest()
        self.faker.start()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.builder


class AssertBuilderRequestedTestCase(BaseAssertBuilderTestCase):
    def test_when_builder_requested(self):
        self.builder._request('GET', 'http://localhost/', None)
        assert_builder_requested(self.faker)

    def test_when_builder_non_requested(self):
        with assert_raises(AssertionError):
            assert_builder_requested(self.faker)

    def test_when_builder_requested_exactly_two_times(self):
        for _ in range(2):
            self.builder._request('GET', 'http://localhost/', None)
        assert_builder_requested(self.faker, times=2)

    def test_when_builder_non_requested_exactly_two_times(self):
        with assert_raises(AssertionError):
            self.builder._request('GET', 'http://localhost/', None)
            assert_builder_requested(self.faker, times=2)


class AssertBuilderUrlContainsParamsTestCase(BaseAssertBuilderTestCase):
    def setUp(self):
        super(AssertBuilderUrlContainsParamsTestCase, self).setUp()
        self.builder._request('GET', 'http://localhost/?bar=foo', None)
        self.builder._request('GET', 'http://localhost/?foo=bar', None)

    def test_last_call(self):
        assert_builder_url_contains_params(self.faker, {'foo': 'bar'})

    def test_first_call(self):
        assert_builder_url_contains_params(self.faker, {'bar': 'foo'}, 0)

    def test_wrong_params(self):
        with assert_raises(AssertionError):
            assert_builder_url_contains_params(self.faker, {'bar': 'foo'})

    def test_no_calls(self):
        with assert_raises(AssertionError):
            self.builder._request.reset_mock()
            assert_builder_url_contains_params(self.faker, {'bar': 'foo'})


class AssertBuilderHeadersEqualTestCase(BaseAssertBuilderTestCase):
    def setUp(self):
        super(AssertBuilderHeadersEqualTestCase, self).setUp()
        self.builder._request(
            'GET',
            'http://localhost/',
            None,
            headers={'foo': 'bar'},
        )
        self.builder._request(
            'GET',
            'http://localhost/',
            None,
            headers={'bar': 'foo'},
        )

    def test_last_call(self):
        assert_builder_headers_equal(self.faker, {'bar': 'foo'})

    def test_first_call(self):
        assert_builder_headers_equal(self.faker, {'foo': 'bar'}, 0)

    def test_wrong_params(self):
        with assert_raises(AssertionError):
            assert_builder_headers_equal(self.faker, {'foo': 'bar'})

    def test_no_calls(self):
        with assert_raises(AssertionError):
            self.builder._request.reset_mock()
            assert_builder_headers_equal(self.faker, {'bar': 'foo'})


class AssertBuilderCookiesEqualTestCase(BaseAssertBuilderTestCase):
    def setUp(self):
        super(AssertBuilderCookiesEqualTestCase, self).setUp()
        self.builder._request(
            'GET',
            'http://localhost/',
            None,
            cookies={'foo': 'bar'},
        )
        self.builder._request(
            'GET',
            'http://localhost/',
            None,
            cookies={'bar': 'foo'},
        )

    def test_last_call(self):
        assert_builder_cookies_equal(self.faker, {'bar': 'foo'})

    def test_first_call(self):
        assert_builder_cookies_equal(self.faker, {'foo': 'bar'}, 0)

    def test_wrong_params(self):
        with assert_raises(AssertionError):
            assert_builder_cookies_equal(self.faker, {'foo': 'bar'})

    def test_no_calls(self):
        with assert_raises(AssertionError):
            self.builder._request.reset_mock()
            assert_builder_cookies_equal(self.faker, {'bar': 'foo'})


class AssertBuilderDataEqualsTestCase(BaseAssertBuilderTestCase):
    def setUp(self):
        super(AssertBuilderDataEqualsTestCase, self).setUp()
        self.builder._request(
            'GET',
            'http://localhost/',
            {'foo': 'bar'},
        )
        self.builder._request(
            'GET',
            'http://localhost/',
            {'bar': 'foo'},
        )

    def test_last_call(self):
        assert_builder_data_equals(self.faker, {'bar': 'foo'})

    def test_first_call(self):
        assert_builder_data_equals(self.faker, {'foo': 'bar'}, 0)

    def test_wrong_params(self):
        with assert_raises(AssertionError):
            assert_builder_data_equals(self.faker, {'foo': 'bar'})

    def test_no_calls(self):
        with assert_raises(AssertionError):
            self.builder._request.reset_mock()
            assert_builder_data_equals(self.faker, {'bar': 'foo'})

    def test_with_exclude(self):
        self.builder._request(
            'GET',
            'http://localhost/',
            {'bar': 'foo', 'a': 'b', 'c': 'd'},
        )
        assert_builder_data_equals(self.faker, {'bar': 'foo'}, exclude_fields=['a', 'c'])


class SetResponseSideEffectTestCase(BaseAssertBuilderTestCase):
    def test_with_exception(self):
        with assert_raises(ValueError):
            self.faker.set_response_side_effect('', ValueError)
            self.builder._request('GET', 'http://localhost/', None)

    def test_with_simple_response(self):
        self.faker.set_response_side_effect('', ['response'])
        response = self.builder._request('GET', 'http://localhost/', None)
        eq_(response.content.decode('utf8'), 'response')

    def test_with_callable_response(self):
        self.faker.set_response_side_effect('', lambda *args, **kwargs: 'response')
        response = self.builder._request('GET', 'http://localhost/', None)
        eq_(response, 'response')

    def test_with_multiple_side_effects(self):
        self.faker.set_response_side_effect('', [
            'response_1',
            ValueError,
            TypeError(),
            'response_2',
        ])
        response = self.builder._request('GET', 'http://localhost/', None)
        eq_(response.content.decode('utf8'), 'response_1')
        with assert_raises(ValueError):
            self.builder._request('GET', 'http://localhost/', None)
        with assert_raises(TypeError):
            self.builder._request('GET', 'http://localhost/', None)
        response = self.builder._request('GET', 'http://localhost/', None)
        eq_(response.content.decode('utf8'), 'response_2')


class TestFakedRequest(TestCase):
    def test_equal_requests(self):
        actual_params = expected_params = self._get_params()
        request = FakedRequest(**actual_params)
        request.assert_properties_equal(**expected_params)

        actual_params = self._get_params(
            files={u'foo': (u'foo.txt', StringIO(u'foo_content'))},
        )
        request = FakedRequest(**actual_params)
        expected_params = self._get_params(
            files={u'foo': u'foo_content'},
        )
        request.assert_properties_equal(**expected_params)

        actual_params = self._get_params(
            files={u'foo': (u'foo.txt', StringIO(u'foo_content'))},
        )
        request = FakedRequest(**actual_params)
        expected_params = self._get_params(
            files={u'foo': StringIO(u'foo_content')},
        )
        request.assert_properties_equal(**expected_params)

        actual_params = self._get_params(
            files={u'foo': StringIO(u'foo_content')},
        )
        request = FakedRequest(**actual_params)
        expected_params = self._get_params(
            files={u'foo': u'foo_content'},
        )
        request.assert_properties_equal(**expected_params)

        actual_params = self._get_params(
            files={u'foo': (u'foo.txt', StringIO(u'foo_content'))},
        )
        request = FakedRequest(**actual_params)
        expected_params = self._get_params(
            files={u'foo': (u'foo.txt', u'foo_content')},
        )
        request.assert_properties_equal(**expected_params)

        actual_params = self._get_params(
            files={u'foo': (u'foo.txt', u'foo_content', u'image/png')},
        )
        request = FakedRequest(**actual_params)
        expected_params = self._get_params(
            files={u'foo': (u'foo.txt', u'foo_content')},
        )
        request.assert_properties_equal(**expected_params)

        actual_params = self._get_params(
            files={u'foo': (u'foo.txt', u'foo_content', u'image/png')},
        )
        request = FakedRequest(**actual_params)
        expected_params = self._get_params(
            files={u'foo': (u'foo.txt', u'foo_content', u'image/png')},
        )
        request.assert_properties_equal(**expected_params)

    def test_repr(self):
        params = self._get_params()
        request = FakedRequest(**params)
        if six.PY2:
            expected_repr = (
                u"<FakedRequest POST http://par.se.me/foo/bar?spam=1 "
                u"post_arguments={u'alpha': u'omega'} headers={u'theta': u'eta'} "
                u"cookies={u'mu': u'nu'} files={u'beta': (u'gamma', u'content')}>"
            )
        else:
            expected_repr = (
                u"<FakedRequest POST http://par.se.me/foo/bar?spam=1 "
                u"post_arguments={'alpha': 'omega'} headers={'theta': 'eta'} "
                u"cookies={'mu': 'nu'} files={'beta': ('gamma', 'content')}>"
            )
        eq_(
            repr(request),
            expected_repr,
        )

    def test_non_equal_methods(self):
        with assert_raises(AssertionError):
            actual_params = self._get_params(method=u'POST')
            request = FakedRequest(**actual_params)
            expected_params = self._get_params(method=u'GET')
            request.assert_properties_equal(**expected_params)

    def test_non_equal_url(self):
        with assert_raises(AssertionError):
            actual_params = self._get_params(url=u'http://foo/')
            request = FakedRequest(**actual_params)
            expected_params = self._get_params(url=u'http://bar/')
            request.assert_properties_equal(**expected_params)

    def test_non_equal_post_arguments(self):
        with assert_raises(AssertionError):
            actual_params = self._get_params(post_args={u'foo': u'foo'})
            request = FakedRequest(**actual_params)
            expected_params = self._get_params(post_args={u'foo': u'bar'})
            request.assert_properties_equal(**expected_params)

    def test_non_equal_files(self):
        with assert_raises(AssertionError):
            actual_params = self._get_params(
                files={u'foo': (u'foo.txt', u'foo_content')},
            )
            request = FakedRequest(**actual_params)
            expected_params = self._get_params(
                files={u'foo': u'bar_content'},
            )
            request.assert_properties_equal(**expected_params)

    def test_invalid_files(self):
        with assert_raises(ValueError):
            actual_params = self._get_params(
                files={u'foo': (u'foo.txt', u'foo_content')},
            )
            request = FakedRequest(**actual_params)
            expected_params = self._get_params(
                files={u'foo': (u'foo.txt', u'foo_content', u'image/png', u'extra')},
            )
            request.assert_properties_equal(**expected_params)

    def test_non_equal_headers(self):
        with assert_raises(AssertionError):
            actual_params = self._get_params(headers={u'foo': u'foo'})
            request = FakedRequest(**actual_params)
            expected_params = self._get_params(headers={u'foo': u'bar'})
            request.assert_properties_equal(**expected_params)

    def test_non_equal_cookies(self):
        with assert_raises(AssertionError):
            actual_params = self._get_params(cookies={u'foo': u'foo'})
            request = FakedRequest(**actual_params)
            expected_params = self._get_params(cookies={u'foo': u'bar'})
            request.assert_properties_equal(**expected_params)

    def test_contain_empty_headers(self):
        actual_params = self._get_params(headers={u'foo': u'foo'})
        request = FakedRequest(**actual_params)
        request.assert_headers_contain({})

    def test_contain_dict_of_headers(self):
        actual_params = self._get_params(headers={u'foo': u'foo'})
        request = FakedRequest(**actual_params)
        request.assert_headers_contain({u'foo': u'foo'})
        request.assert_headers_contain([(u'foo', u'foo')])

    def test_contain_list_of_headers(self):
        actual_params = self._get_params(headers=[(u'foo', u'foo')])
        request = FakedRequest(**actual_params)
        request.assert_headers_contain({u'foo': u'foo'})
        request.assert_headers_contain([(u'foo', u'foo')])

    def test_not_contain_headers(self):
        with assert_raises(AssertionError):
            actual_params = self._get_params(headers={u'foo': u'foo'})
            request = FakedRequest(**actual_params)
            request.assert_headers_contain({u'bar': u'bar'})

    def test_post_data_contains_some(self):
        request = FakedRequest(
            **self._get_params(post_args={u'foo': u'foo', u'bar': u'bar'})
        )
        request.assert_post_data_contains({u'bar': u'bar'})

    def test_post_data_contains_all(self):
        request = FakedRequest(
            **self._get_params(post_args={u'foo': u'foo', u'bar': u'bar'})
        )
        request.assert_post_data_contains({u'foo': u'foo', u'bar': u'bar'})

    def test_post_data_contains_empty(self):
        request = FakedRequest(
            **self._get_params(post_args={u'foo': u'foo'})
        )
        request.assert_post_data_contains({})

    def test_json_data_without_header(self):
        request = FakedRequest(
            **self._get_params(post_args=json.dumps({u'foo': u'foo'}))
        )
        with assert_raises(AssertionError):
            request.assert_properties_equal(json_data={u'foo': u'foo'})

    def test_json_data(self):
        request = FakedRequest(
            **self._get_params(
                post_args=json.dumps({u'foo': u'foo'}),
                headers={u'Content-Type': u'application/json'}
            )
        )
        request.assert_properties_equal(json_data={u'foo': u'foo'})

    def test_post_data_does_not_contain_some(self):
        with assert_raises(AssertionError):
            request = FakedRequest(
                **self._get_params(post_args={u'foo': u'foo'})
            )
            request.assert_post_data_contains({u'foo': u'bar'})

    def _get_params(self, **override_params):
        default_params = {
            u'method': u'POST',
            u'url': u'http://par.se.me/foo/bar?spam=1',
            u'post_args': {u'alpha': u'omega'},
            u'files': {u'beta': (u'gamma', u'content')},
            u'headers': {u'theta': u'eta'},
            u'cookies': {u'mu': u'nu'},
        }
        default_params.update(override_params)
        return default_params


class TestGetRequestsByMethod(BaseAssertBuilderTestCase):
    def test_one_found(self):
        self.builder.method()
        eq_(len(self.faker.get_requests_by_method(u'method')), 1)

    def test_many_found(self):
        self.builder.method()
        self.builder.method()
        eq_(len(self.faker.get_requests_by_method(u'method')), 2)

    def test_not_found(self):
        self.builder.method()
        eq_(len(self.faker.get_requests_by_method(u'func')), 0)
