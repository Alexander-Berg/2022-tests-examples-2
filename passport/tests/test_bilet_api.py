# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.bilet_api import (
    BiletApi,
    BiletApiInvalidResponseError,
    BiletApiNoAuthError,
    BiletApiPermanentError,
    BiletApiTemporaryError,
)
from passport.backend.core.builders.bilet_api.faker.fake_bilet_api import (
    FakeBiletApi,
    order_successful_response,
    TEST_ORDER_ID,
    TEST_ORDERS_RESPONSE,
    TEST_USER_POINTS_RESPONSE,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.useragent.sync import RequestError


TEST_API_KEY = 'testapikey'
TEST_CLIENT_KEY = 'testclientkey'
TEST_IP = '1.2.3.4'
TEST_SESSIONID = 'testsessionid'
TEST_PASSED_HOST = 'yandex.ua'
TEST_EXPECTED_HOST = 'yandex.ua'
TEST_TOKEN = 'token'
TEST_YANDEXUID = '123123123123'
TEST_USER_AGENT = 'YaBrowser/17.3.1.840 Yowser/2.5 Safari/537.36'
TEST_REQUEST_ID = 'requestid1'

TEST_METHODS_ARGS = (
    ('orders', dict(sessionid=TEST_SESSIONID, host=TEST_PASSED_HOST)),
    ('order', dict(order_id=TEST_ORDER_ID, sessionid=TEST_SESSIONID, host=TEST_PASSED_HOST)),
    ('user_points', dict(sessionid=TEST_SESSIONID, host=TEST_PASSED_HOST)),
)


@with_settings(
    BILET_API_URL='http://localhost/',
    BILET_API_TIMEOUT=1,
    BILET_API_RETRIES=2,
    BILET_API_KEY=TEST_API_KEY,
    BILET_API_CLIENT_KEY=TEST_CLIENT_KEY,
    DOMAIN_KEYSPACES=(
        ('yandex.ru', 'yandex.ru'),
        ('yandex.ua', 'yandex.ua'),
    ),
)
class TestBiletApiCommon(unittest.TestCase):
    def setUp(self):
        self.bilet_api = BiletApi()
        self.response = mock.Mock()
        self.bilet_api.useragent.request = mock.Mock(return_value=self.response)
        self.response.content = 'OK'
        self.response.status_code = 200

    def tearDown(self):
        del self.bilet_api.useragent.request
        del self.bilet_api
        del self.response

    def test_server_error(self):
        self.response.status_code = 500
        self.response.content = b'xxx'
        for method_name, kwargs in TEST_METHODS_ARGS:
            with assert_raises(BiletApiPermanentError):
                method = getattr(self.bilet_api, method_name)
                method(**kwargs)

    def test_network_error(self):
        self.bilet_api.useragent.request.side_effect = RequestError
        for method_name, kwargs in TEST_METHODS_ARGS:
            with assert_raises(BiletApiTemporaryError):
                method = getattr(self.bilet_api, method_name)
                method(**kwargs)


@with_settings(
    BILET_API_URL='http://localhost/',
    BILET_API_TIMEOUT=1,
    BILET_API_RETRIES=2,
    BILET_API_KEY=TEST_API_KEY,
    BILET_API_CLIENT_KEY=TEST_CLIENT_KEY,
    DOMAIN_KEYSPACES=(
        ('yandex.ru', 'yandex.ru'),
        ('yandex.ua', 'yandex.ua'),
    ),
)
class TestBiletApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_bilet_api = FakeBiletApi()
        self.fake_bilet_api.start()
        self.bilet_api = BiletApi()

    def tearDown(self):
        self.fake_bilet_api.stop()
        del self.fake_bilet_api

    def test_orders_ok(self):
        self.fake_bilet_api.set_response_value('orders', TEST_ORDERS_RESPONSE)

        response = self.bilet_api.orders(sessionid=TEST_SESSIONID, host=TEST_PASSED_HOST)
        eq_(json.loads(TEST_ORDERS_RESPONSE)['result'], response)
        self.fake_bilet_api.get_requests_by_method('orders')[0].assert_properties_equal(
            method='GET',
            url='http://localhost/v2/orders/',
            headers={
                'X-Tickets-Client': 'ClientKey %s' % TEST_CLIENT_KEY,
                'WWW-Authenticate': 'ApiKey %s' % TEST_API_KEY,
                'Authorization': 'SessionId %s' % TEST_SESSIONID,
                'X-Frontend-Host': TEST_EXPECTED_HOST,
                'Accept-Language': 'RU',
            },
        )

    def test_orders_with_params_ok(self):
        self.fake_bilet_api.set_response_value('orders', TEST_ORDERS_RESPONSE)

        response = self.bilet_api.orders(
            limit=10,
            offset=5,
            sort='desc',
            approved_only=True,
            user_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID,
            request_id=TEST_REQUEST_ID,
            oauth_token=TEST_TOKEN,
        )
        eq_(json.loads(TEST_ORDERS_RESPONSE)['result'], response)
        self.fake_bilet_api.get_requests_by_method('orders')[0].assert_properties_equal(
            method='GET',
            url='http://localhost/v2/orders/?limit=10&offset=5&sort=desc&approved_only=true',
            headers={
                'X-Forwarded-For': TEST_IP,
                'X-Tickets-Client': 'ClientKey %s' % TEST_CLIENT_KEY,
                'WWW-Authenticate': 'ApiKey %s' % TEST_API_KEY,
                'Authorization': 'OAuth %s' % TEST_TOKEN,
                'X-Tickets-YUID': TEST_YANDEXUID,
                'Accept-Language': 'RU',
                'User-Agent': TEST_USER_AGENT,
                'X-Request-Id': TEST_REQUEST_ID,
            },
        )

    def test_order_ok(self):
        self.fake_bilet_api.set_response_value('order', order_successful_response())

        response = self.bilet_api.order(TEST_ORDER_ID, sessionid=TEST_SESSIONID, host=TEST_PASSED_HOST)
        eq_(json.loads(order_successful_response())['result'], response)
        self.fake_bilet_api.get_requests_by_method('order')[0].assert_properties_equal(
            method='GET',
            url='http://localhost/v2/orders/%s/' % TEST_ORDER_ID,
            headers={
                'X-Tickets-Client': 'ClientKey %s' % TEST_CLIENT_KEY,
                'WWW-Authenticate': 'ApiKey %s' % TEST_API_KEY,
                'Authorization': 'SessionId %s' % TEST_SESSIONID,
                'X-Frontend-Host': TEST_EXPECTED_HOST,
                'Accept-Language': 'RU',
            },
        )

    def test_user_points_ok(self):
        self.fake_bilet_api.set_response_value('user_points', TEST_USER_POINTS_RESPONSE)

        response = self.bilet_api.user_points(sessionid=TEST_SESSIONID, host=TEST_PASSED_HOST)
        eq_(json.loads(TEST_USER_POINTS_RESPONSE)['result'], response)
        self.fake_bilet_api.get_requests_by_method('user_points')[0].assert_properties_equal(
            method='GET',
            url='http://localhost/v2/user/points/',
            headers={
                'X-Tickets-Client': 'ClientKey %s' % TEST_CLIENT_KEY,
                'WWW-Authenticate': 'ApiKey %s' % TEST_API_KEY,
                'Authorization': 'SessionId %s' % TEST_SESSIONID,
                'X-Frontend-Host': TEST_EXPECTED_HOST,
                'Accept-Language': 'RU',
            },
        )

    def test_host_required(self):
        for method_name, kwargs in TEST_METHODS_ARGS:
            with assert_raises(ValueError):
                method = getattr(self.bilet_api, method_name)
                kwargs = dict(kwargs, host=None)
                method(**kwargs)

    def test_bad_json(self):
        for method_name, kwargs in TEST_METHODS_ARGS:
            with assert_raises(BiletApiInvalidResponseError):
                self.fake_bilet_api.set_response_value(method_name, 'no json')
                method = getattr(self.bilet_api, method_name)
                method(**kwargs)

    def test_bad_status(self):
        for method_name, kwargs in TEST_METHODS_ARGS:
            with assert_raises(BiletApiInvalidResponseError):
                self.fake_bilet_api.set_response_value(method_name, '{"status":"nemogu"}')
                method = getattr(self.bilet_api, method_name)
                method(**kwargs)

    def test_no_auth(self):
        for method_name, kwargs in TEST_METHODS_ARGS:
            with assert_raises(BiletApiNoAuthError):
                self.fake_bilet_api.set_response_value(method_name, '{"status":"no-auth"}')
                method = getattr(self.bilet_api, method_name)
                method(**kwargs)
