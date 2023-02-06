# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.collections import CollectionsApi
from passport.backend.core.builders.collections.exceptions import (
    CollectionsApiInvalidResponseError,
    CollectionsApiPermanentError,
    CollectionsApiTemporaryError,
)
from passport.backend.core.builders.collections.faker.fake_collections_api import (
    collections_api_error_response,
    collections_successful_response,
    FakeCollectionsApi,
    pictures_successful_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_PUBLIC_ID = 'test-public-id'
TEST_PASSED_HOST = 'passport.yandex.ru'
TEST_EXPECTED_HOST = 'yandex.ru'
TEST_SESSION_ID = '3:test'
TEST_COOKIE_HEADER = 'Session_id=%s' % TEST_SESSION_ID


@with_settings(
    COLLECTIONS_API_URL='http://localhost/',
    COLLECTIONS_API_TIMEOUT=0.5,
    COLLECTIONS_API_RETRIES=2,
)
class TestCollectionsApiCommon(unittest.TestCase):
    def setUp(self):
        self.collections_api = CollectionsApi()
        self.collections_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.collections_api.useragent.request.return_value = self.response
        self.collections_api.useragent.request_error_class = self.collections_api.temporary_error_class
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.collections_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = 'not a json'
        with assert_raises(CollectionsApiPermanentError):
            self.collections_api.collections(public_id=TEST_PUBLIC_ID)

    def test_server_error(self):
        self.response.status_code = 503
        self.response.content = collections_api_error_response('ServerError')
        with assert_raises(CollectionsApiPermanentError):
            self.collections_api.collections(public_id=TEST_PUBLIC_ID)

    def test_temporary_error(self):
        self.response.status_code = 504
        self.response.content = collections_api_error_response('Gateway Timeout')
        with assert_raises(CollectionsApiTemporaryError):
            self.collections_api.collections(public_id=TEST_PUBLIC_ID)

    def test_bad_status_code(self):
        self.response.status_code = 418
        self.response.content = collections_api_error_response('IAmATeapot')
        with assert_raises(CollectionsApiPermanentError):
            self.collections_api.collections(public_id=TEST_PUBLIC_ID)

    def test_bad_response(self):
        self.response.status_code = 200
        self.response.content = json.dumps({'previous': None, 'next': None}).encode('utf8')
        with assert_raises(CollectionsApiInvalidResponseError):
            self.collections_api.collections(public_id=TEST_PUBLIC_ID)

    def test_invalid_response(self):
        self.response.status_code = 400
        self.response.content = collections_api_error_response('Invalid Request')
        with assert_raises(CollectionsApiInvalidResponseError):
            self.collections_api.collections(public_id=TEST_PUBLIC_ID)


@with_settings(
    COLLECTIONS_API_URL='http://localhost/',
    COLLECTIONS_API_TIMEOUT=0.5,
    COLLECTIONS_API_RETRIES=2,
    DOMAIN_KEYSPACES=(
        ('yandex.ru', 'yandex.ru'),
        ('yandex.ua', 'yandex.ua'),
    ),
)
class TestCollectionsApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_collections_api = FakeCollectionsApi()
        self.fake_collections_api.start()

        self.collections_api = CollectionsApi()

    def tearDown(self):
        self.fake_collections_api.stop()
        del self.fake_collections_api

    def test_collections_ok(self):
        self.fake_collections_api.set_response_value(
            'collections',
            collections_successful_response(),
        )
        response = self.collections_api.collections(
            public_id=TEST_PUBLIC_ID,
            sessionid=TEST_SESSION_ID,
            host=TEST_PASSED_HOST,
        )
        eq_(
            response,
            json.loads(collections_successful_response())['results'],
        )
        eq_(len(self.fake_collections_api.requests), 1)
        self.fake_collections_api.requests[0].assert_url_starts_with('http://localhost/api/boards/')
        self.fake_collections_api.requests[0].assert_query_equals({
            'sort': '-service.updated_at',
            'page': '1',
            'page_size': '10',
            'previews_count': '6',
            'owner.public_id': TEST_PUBLIC_ID,
        })
        self.fake_collections_api.requests[0].assert_headers_contain({
            'X-Forwarded-Host': TEST_EXPECTED_HOST,
            'Cookie': TEST_COOKIE_HEADER,
            'Accept': 'application/json',
        })

    def test_collections_with_pagination(self):
        results = [
            {
                'title': u'Избранное из Яндекс Картинок',
                'url': 'https://some.url/1',
                'cards_count': 2,
                'slug': 'izbrannoe-iz-yandex-kartinok',
                'is_private': True,
            },
            {
                'title': u'Винтажные звездные новости',
                'url': 'https://some.url/2',
                'cards_count': 6,
                'slug': 'vintage-star-news',
                'is_private': False,
            },
        ]
        self.fake_collections_api.set_response_value(
            'collections',
            collections_successful_response(results),
        )
        response = self.collections_api.collections(
            public_id=TEST_PUBLIC_ID,
            sessionid=TEST_SESSION_ID,
            host=TEST_PASSED_HOST,
            page=2,
            page_size=2,
            previews_count=3,
        )
        eq_(
            response,
            json.loads(collections_successful_response(results))['results'],
        )
        eq_(len(self.fake_collections_api.requests), 1)
        self.fake_collections_api.requests[0].assert_url_starts_with('http://localhost/api/boards/')
        self.fake_collections_api.requests[0].assert_query_equals({
            'sort': '-service.updated_at',
            'page': '2',
            'page_size': '2',
            'previews_count': '3',
            'owner.public_id': TEST_PUBLIC_ID,
        })
        self.fake_collections_api.requests[0].assert_headers_contain({
            'X-Forwarded-Host': TEST_EXPECTED_HOST,
            'Cookie': TEST_COOKIE_HEADER,
            'Accept': 'application/json',
        })

    def test_pictures_ok(self):
        self.fake_collections_api.set_response_value(
            'pictures',
            pictures_successful_response(),
        )
        response = self.collections_api.pictures(public_id=TEST_PUBLIC_ID, sessionid=TEST_SESSION_ID, host=TEST_PASSED_HOST)
        eq_(
            response,
            json.loads(pictures_successful_response())['results'],
        )
        eq_(len(self.fake_collections_api.requests), 1)
        self.fake_collections_api.requests[0].assert_url_starts_with('http://localhost/api/cards/')
        self.fake_collections_api.requests[0].assert_query_equals({
            'sort': '-id',
            'page': '1',
            'page_size': '10',
            'board.owner.public_id': TEST_PUBLIC_ID,
            'board.slug': 'izbrannoe-iz-yandex-kartinok',
        })
        self.fake_collections_api.requests[0].assert_headers_contain({
            'X-Forwarded-Host': TEST_EXPECTED_HOST,
            'Cookie': TEST_COOKIE_HEADER,
            'Accept': 'application/json',
        })

    def test_pictures_with_pagination(self):
        self.fake_collections_api.set_response_value(
            'pictures',
            pictures_successful_response(count=0),
        )
        response = self.collections_api.pictures(
            public_id=TEST_PUBLIC_ID,
            page_size=4,
            page=3,
        )
        eq_(
            response,
            json.loads(pictures_successful_response(count=0))['results'],
        )
        eq_(len(self.fake_collections_api.requests), 1)
        self.fake_collections_api.requests[0].assert_url_starts_with('http://localhost/api/cards/')
        self.fake_collections_api.requests[0].assert_query_equals({
            'sort': '-id',
            'page': '3',
            'page_size': '4',
            'board.owner.public_id': TEST_PUBLIC_ID,
            'board.slug': 'izbrannoe-iz-yandex-kartinok',
        })
        self.fake_collections_api.requests[0].assert_headers_contain({
            'Accept': 'application/json',
        })

    def test_no_host(self):
        with assert_raises(ValueError):
            self.collections_api.pictures(
                public_id=TEST_PUBLIC_ID,
                host=None,
                sessionid=TEST_SESSION_ID,
            )
        with assert_raises(ValueError):
            self.collections_api.collections(
                public_id=TEST_PUBLIC_ID,
                host=None,
                sessionid=TEST_SESSION_ID,
            )

    def test_collections_not_found_by_code__ok(self):
        self.fake_collections_api.set_response_value(
            'collections',
            collections_api_error_response('Not Found'),
            status=404,
        )
        response = self.collections_api.collections(
            public_id=TEST_PUBLIC_ID,
            sessionid=TEST_SESSION_ID,
            host=TEST_PASSED_HOST,
        )
        eq_(response, [])
        eq_(len(self.fake_collections_api.requests), 1)

    def test_collections_not_found_by_description__ok(self):
        self.fake_collections_api.set_response_value(
            'collections',
            collections_api_error_response('Invalid request', message='login is not valid'),
            status=400,
        )
        response = self.collections_api.collections(
            public_id=TEST_PUBLIC_ID,
            sessionid=TEST_SESSION_ID,
            host=TEST_PASSED_HOST,
        )
        eq_(response, [])
        eq_(len(self.fake_collections_api.requests), 1)

    def test_pictures_not_found_by_code__ok(self):
        self.fake_collections_api.set_response_value(
            'pictures',
            json.dumps({}),
            status=404,
        )
        response = self.collections_api.pictures(public_id=TEST_PUBLIC_ID, sessionid=TEST_SESSION_ID, host=TEST_PASSED_HOST)
        eq_(response, [])
        eq_(len(self.fake_collections_api.requests), 1)

    def test_pictures_not_found_by_description__ok(self):
        self.fake_collections_api.set_response_value(
            'pictures',
            collections_api_error_response('Invalid request', message='login is not valid'),
            status=400,
        )
        response = self.collections_api.pictures(public_id=TEST_PUBLIC_ID, sessionid=TEST_SESSION_ID, host=TEST_EXPECTED_HOST)
        eq_(response, [])
        eq_(len(self.fake_collections_api.requests), 1)
