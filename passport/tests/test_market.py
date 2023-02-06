# -*- coding: utf-8 -*-
from datetime import datetime
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.core.builders.market import (
    MarketContentApi,
    MarketContentApiInvalidResponseError,
    MarketContentApiPermanentError,
    MarketContentApiTemporaryError,
)
from passport.backend.core.builders.market.faker.fake_market import (
    FakeMarketContentApi,
    market_content_api_user_orders_response,
    market_content_api_user_wishlist_response,
)
from passport.backend.core.builders.market.market import (
    MARKET_CONTENT_API_VERSION,
    MARKET_REQUEST_ID_HEADER,
    USER_ORDERS_FAKE_UUID,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.useragent.sync import RequestError


TEST_UID = 1
TEST_API_KEY = '123'
TEST_TOKEN = 'token'
TEST_SESSIONID = 'sessionid'
TEST_USER_IP = '127.0.0.1'
TEST_PASSED_HOST = 'host.yandex.ru'
TEST_EXPECTED_HOST = 'yandex.ru'


@with_settings(
    MARKET_CONTENT_API_URL='http://content_api/',
    MARKET_CONTENT_API_RETRIES=2,
    MARKET_CONTENT_API_TIMEOUT=1,
    MARKET_CONTENT_API_KEY=TEST_API_KEY,
)
class TestContentApiCommon(unittest.TestCase):
    def setUp(self):
        self.content_api = MarketContentApi()

        self.response = mock.Mock()
        self.content_api.useragent.request = mock.Mock(return_value=self.response)
        self.response.content = b'OK'
        self.response.status_code = 200

    def tearDown(self):
        del self.content_api.useragent.request
        del self.content_api
        del self.response

    def test_network_error(self):
        self.content_api.useragent.request.side_effect = RequestError
        with assert_raises(MarketContentApiTemporaryError):
            self.content_api.user_orders(oauth_token=TEST_TOKEN)

    def test_bad_json(self):
        self.response.content = b'bad json'
        with assert_raises(MarketContentApiInvalidResponseError):
            self.content_api.user_orders(oauth_token=TEST_TOKEN)

    def test_error_in_json_response(self):
        self.response.status_code = 400
        self.response.content = b'{"errors":"bad request"}'
        with assert_raises(MarketContentApiInvalidResponseError):
            self.content_api.user_orders(oauth_token=TEST_TOKEN)

    def test_server_error_500(self):
        self.response.status_code = 500
        self.response.content = b'{"errors":"server is down"}'
        with assert_raises(MarketContentApiPermanentError):
            self.content_api.user_orders(oauth_token=TEST_TOKEN)

    def test_bad_gateway_502(self):
        self.response.status_code = 502
        self.response.content = '\n'.join([
            '<html>',
            '<head><title>502 Bad Gateway</title></head>',
            '<body bgcolor="white">',
            '<center><h1>502 Bad Gateway</h1></center>',
            '<hr>',
            '<center>nginx</center>',
            '</body>',
            '</html>',
        ]).encode('utf-8')
        with assert_raises(MarketContentApiTemporaryError):
            self.content_api.user_orders(oauth_token=TEST_TOKEN)

    def test_service_unavailable_503(self):
        self.response.status_code = 503
        self.response.content = '\n'.join([
            '<html>',
            '<head><title>503 Service Unavailable</title></head>',
            '<body bgcolor="white">',
            '<center><h1>503 Service Unavailable</h1></center>',
            '<hr>',
            '<center>nginx</center>',
            '</body>',
            '</html>',
        ]).encode('utf-8')
        with assert_raises(MarketContentApiTemporaryError):
            self.content_api.user_orders(oauth_token=TEST_TOKEN)

    def test_error_with_req_id(self):
        self.response.headers = {MARKET_REQUEST_ID_HEADER: 'req-id'}
        self.response.status_code = 503
        with assert_raises(MarketContentApiTemporaryError):
            self.content_api.user_orders(oauth_token=TEST_TOKEN)


@with_settings(
    MARKET_CONTENT_API_URL='http://content_api/',
    MARKET_CONTENT_API_RETRIES=2,
    MARKET_CONTENT_API_TIMEOUT=1,
    MARKET_CONTENT_API_KEY=TEST_API_KEY,
    DOMAIN_KEYSPACES=(
        ('yandex.ru', 'yandex.ru'),
        ('yandex.ua', 'yandex.ua'),
    ),
)
class TestContentApi(unittest.TestCase):
    def setUp(self):
        self.fake_content_api = FakeMarketContentApi()
        self.fake_content_api.start()
        self.content_api = MarketContentApi()

    def tearDown(self):
        self.fake_content_api.stop()
        del self.fake_content_api

    def test_user_orders_by_token(self):
        self.fake_content_api.set_response_value(
            'user_orders',
            market_content_api_user_orders_response(),
        )

        response = self.content_api.user_orders(
            oauth_token=TEST_TOKEN,
        )
        eq_(response, json.loads(market_content_api_user_orders_response()))

        self.fake_content_api.get_requests_by_method('user_orders')[0].assert_properties_equal(
            method='GET',
            url='http://content_api/user/orders?format=json&uuid=%s' % (
                USER_ORDERS_FAKE_UUID,
            ),
            headers={
                'Authorization': TEST_API_KEY,
                'X-User-Authorization': 'OAuth {}'.format(TEST_TOKEN),
            },
        )

    def test_user_orders_by_session(self):
        self.fake_content_api.set_response_value(
            'user_orders',
            market_content_api_user_orders_response(),
        )

        response = self.content_api.user_orders(
            sessionid=TEST_SESSIONID,
            host=TEST_PASSED_HOST,
        )
        eq_(response, json.loads(market_content_api_user_orders_response()))

        self.fake_content_api.get_requests_by_method('user_orders')[0].assert_properties_equal(
            method='GET',
            url='http://content_api/user/orders?format=json&uuid=%s' % USER_ORDERS_FAKE_UUID,
            headers={
                'Authorization': TEST_API_KEY,
                'X-User-Authorization': 'SessionId Id=%s; Host=%s' % (TEST_SESSIONID, TEST_EXPECTED_HOST),
            },
        )

    @raises(ValueError)
    def test_user_orders_host_required(self):
        self.content_api.user_orders(sessionid=TEST_SESSIONID)

    def test_user_orders_with_params(self):
        self.fake_content_api.set_response_value(
            'user_orders',
            market_content_api_user_orders_response(),
        )

        response = self.content_api.user_orders(
            oauth_token=TEST_TOKEN,
            from_date=datetime(year=2010, month=10, day=2),
            to_date=datetime(year=2017, month=11, day=3),
            fields=['EVENT', 'SHOP'],
            page=3,
            count=10,
        )
        eq_(response, json.loads(market_content_api_user_orders_response()))

        self.fake_content_api.get_requests_by_method('user_orders')[0].assert_properties_equal(
            method='GET',
            url=(
                'http://content_api/user/orders?format=json&uuid=%s&from_date=2010-10-02'
                '&to_date=2017-11-03&fields=EVENT,SHOP&page=3&count=10'
            ) % (USER_ORDERS_FAKE_UUID,),
            headers={
                'Authorization': TEST_API_KEY,
                'X-User-Authorization': 'OAuth {}'.format(TEST_TOKEN),
            },
        )

    def test_user_orders_with_no_credentials(self):
        with assert_raises(ValueError):
            self.content_api.user_orders()

    @parameterized.expand([
        (dict(count=0),),
        (dict(count=51),),
        (dict(page=0),),
    ])
    def test_user_orders_with_bad_paging_params(self, params):
        with assert_raises(ValueError):
            self.content_api.user_orders(oauth_token=TEST_TOKEN, **params)

    @parameterized.expand([
        (True,),
        (False,),
    ])
    def test_user_wishlist_error_if_unknown_remote_ip(self, with_req_id):
        if with_req_id:
            headers = {MARKET_REQUEST_ID_HEADER: 'req-id'}
        else:
            headers = None
        self.fake_content_api.set_response_value(
            'user_wishlist',
            '{"message": "Required parameter \'geo_id\' is missing"}',
            status=422,
            headers=headers,
        )
        with assert_raises(MarketContentApiPermanentError):
            self.content_api.user_wishlist(
                TEST_USER_IP,
                oauth_token=TEST_TOKEN,
            )

    def test_user_withlist_internal_error_is_temporary(self):
        self.fake_content_api.set_response_value(
            'user_wishlist',
            '{"message": "Internal Error"}',
            status=500,
        )
        with assert_raises(MarketContentApiTemporaryError):
            self.content_api.user_wishlist(
                TEST_USER_IP,
                oauth_token=TEST_TOKEN,
            )

    def test_user_wishlist_by_token(self):
        self.fake_content_api.set_response_value(
            'user_wishlist',
            market_content_api_user_wishlist_response(),
        )

        response = self.content_api.user_wishlist(
            TEST_USER_IP,
            oauth_token=TEST_TOKEN,
        )
        eq_(response, json.loads(market_content_api_user_wishlist_response()))

        eq_(len(self.fake_content_api.requests), 1)
        self.fake_content_api.requests[0].assert_url_starts_with(
            'http://content_api/%s/user/wishlist/items' % MARKET_CONTENT_API_VERSION,
        )
        self.fake_content_api.requests[0].assert_query_equals({
            'remote_ip': TEST_USER_IP,
            'sort': 'create_date',
            'how': 'desc',
        })
        self.fake_content_api.requests[0].assert_headers_contain({
            'Authorization': TEST_API_KEY,
            'X-User-Authorization': 'OAuth {}'.format(TEST_TOKEN),
        })

    def test_user_wishlist_by_session(self):
        self.fake_content_api.set_response_value(
            'user_wishlist',
            market_content_api_user_wishlist_response(),
        )

        response = self.content_api.user_wishlist(
            TEST_USER_IP,
            sessionid=TEST_SESSIONID,
            host=TEST_PASSED_HOST,
        )
        eq_(response, json.loads(market_content_api_user_wishlist_response()))

        eq_(len(self.fake_content_api.requests), 1)
        self.fake_content_api.requests[0].assert_url_starts_with(
            'http://content_api/%s/user/wishlist/items' % MARKET_CONTENT_API_VERSION,
        )
        self.fake_content_api.requests[0].assert_query_equals({
            'remote_ip': TEST_USER_IP,
            'sort': 'create_date',
            'how': 'desc',
        })
        self.fake_content_api.requests[0].assert_headers_contain({
            'Authorization': TEST_API_KEY,
            'X-User-Authorization': 'SessionId Id=%s; Host=%s' % (TEST_SESSIONID, TEST_EXPECTED_HOST),
        })

    def test_user_wishlist_with_params(self):
        items = [
            {
                'kind': 'Item1',
                'description': 'Desc1',
                'name': 'Super Cool Item',
                'price': '1.0',
                'photo': 'url1',
            },
            {
                'kind': 'Item2',
                'description': 'Desc2',
                'name': 'Item of average coolness',
                'price': '10.6',
                'photo': 'url2',
            },
        ]
        self.fake_content_api.set_response_value(
            'user_wishlist',
            market_content_api_user_wishlist_response(items, count=15, page=3),
        )

        response = self.content_api.user_wishlist(
            TEST_USER_IP,
            fields=['price', 'photo'],
            sort_by='model',
            how='asc',
            oauth_token=TEST_TOKEN,
            page=3,
            count=15,
        )
        eq_(response, json.loads(market_content_api_user_wishlist_response(items, count=15, page=3)))

        eq_(len(self.fake_content_api.requests), 1)
        self.fake_content_api.requests[0].assert_url_starts_with(
            'http://content_api/%s/user/wishlist/items' % MARKET_CONTENT_API_VERSION,
        )
        self.fake_content_api.requests[0].assert_query_equals({
            'remote_ip': TEST_USER_IP,
            'fields': 'price,photo',
            'sort': 'model',
            'how': 'asc',
            'count': '15',
            'page': '3',
        })
        self.fake_content_api.requests[0].assert_headers_contain({
            'Authorization': TEST_API_KEY,
            'X-User-Authorization': 'OAuth {}'.format(TEST_TOKEN),
        })

    def test_user_wishlist_no_credentials(self):
        with assert_raises(ValueError):
            self.content_api.user_wishlist(TEST_USER_IP)
