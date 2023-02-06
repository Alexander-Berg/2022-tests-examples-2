# -*- coding: utf-8 -*-
import json
from time import time

from nose.tools import (
    eq_,
    istest,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_OAUTH_TOKEN
from passport.backend.core.builders.bilet_api import BiletApiTemporaryError
from passport.backend.core.builders.bilet_api.faker.fake_bilet_api import (
    order_successful_response,
    TEST_ORDER_ID,
    TEST_ORDERS_RESPONSE,
    TEST_USER_POINTS_RESPONSE,
)
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import passport_external_data_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseExternalDataTestCase,
    TEST_COOKIE_HEADERS,
    TEST_REQUEST_ID,
    TEST_SESSION_ID,
    TEST_TOKEN_HEADERS,
    TEST_USER_IP,
)


TEST_API_KEY = 'api_key'
TEST_CLIENT_KEY = 'client_key'
TEST_API_URL = 'https://afisha.net'
TEST_EXPECTED_HOST = 'yandex.ru'


@with_settings_hosts(
    BILET_API_URL=TEST_API_URL,
    BILET_API_KEY=TEST_API_KEY,
    BILET_API_CLIENT_KEY=TEST_CLIENT_KEY,
)
class BaseAfishaTestCase(BaseExternalDataTestCase):
    oauth_scope = 'afisha:all'

    def make_builder_headers(self, custom_headers):
        headers = {
            'Accept-Language': 'RU',
            'X-Forwarded-For': TEST_USER_IP,
            'X-Request-Id': TEST_REQUEST_ID,
            'X-Tickets-Client': 'ClientKey %s' % TEST_CLIENT_KEY,
            'WWW-Authenticate': 'ApiKey %s' % TEST_API_KEY,
            'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
        }
        headers.update(custom_headers)
        return headers


@istest
class AfishaOrdersTestCase(BaseAfishaTestCase):
    default_url = '/1/bundle/account/external_data/afisha/orders/'
    http_query_args = dict(
        consumer='dev',
    )

    def setUp(self):
        super(AfishaOrdersTestCase, self).setUp()
        self.env.bilet_api.set_response_value(
            'orders',
            TEST_ORDERS_RESPONSE,
        )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(TEST_ORDERS_RESPONSE)['result']
        )
        self.env.bilet_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2/orders/?sort=session-date&approved_only=true&limit=10&offset=0' % TEST_API_URL,
            headers=self.make_builder_headers({
                'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
            }),
        )

    def test_ok_with_session_and_pagination(self):
        rv = self.make_request(query_args={'page': 3, 'page_size': 20}, headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(TEST_ORDERS_RESPONSE)['result']
        )
        self.env.bilet_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2/orders/?sort=session-date&approved_only=true&limit=20&offset=40' % TEST_API_URL,
            headers=self.make_builder_headers({
                'Authorization': 'SessionId %s' % TEST_SESSION_ID,
                'X-Frontend-Host': TEST_EXPECTED_HOST,
            }),
        )

    def test_bilet_api_unavailable(self):
        self.env.bilet_api.set_response_side_effect(
            'orders',
            BiletApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.bilet_api_failed'])


@istest
class AfishaOrderInfoTestCase(BaseAfishaTestCase):
    default_url = '/1/bundle/account/external_data/afisha/order_info/'
    http_query_args = dict(
        consumer='dev',
        order_id=TEST_ORDER_ID,
    )

    def setUp(self):
        super(AfishaOrderInfoTestCase, self).setUp()
        self.env.bilet_api.set_response_value(
            'order',
            order_successful_response(),
        )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(order_successful_response())['result']
        )
        self.env.bilet_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2/orders/%s/' % (TEST_API_URL, TEST_ORDER_ID),
            headers=self.make_builder_headers({
                'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
            }),
        )

    def test_ok_with_session(self):
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(order_successful_response())['result']
        )
        self.env.bilet_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2/orders/%s/' % (TEST_API_URL, TEST_ORDER_ID),
            headers=self.make_builder_headers({
                'Authorization': 'SessionId %s' % TEST_SESSION_ID,
                'X-Frontend-Host': TEST_EXPECTED_HOST,
            }),
        )

    def test_bilet_api_unavailable(self):
        self.env.bilet_api.set_response_side_effect(
            'order',
            BiletApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.bilet_api_failed'])

    def test_with_http_images_ok(self):
        images = [
            {
                'width': 1280,
                'crop': False,
                'url': 'http://avatars.mdst.yandex.net:443/get-tickets/24260/2c32cccf/orig',
                'height': 851,
            },
            {
                'width': 50,
                'crop': False,
                'url': 'https://avatars.mdt.yandex.net:443/get-tickets/24260/2c32cccf/NOCROP_SIZE_50x75',
                'height': 33,
            },
        ]
        self.env.bilet_api.set_response_value(
            'order',
            order_successful_response(images),
        )
        images_exp = images[:]
        images_exp[0]['url'] = 'https://avatars.mdst.yandex.net:443/get-tickets/24260/2c32cccf/orig'
        expected_response = order_successful_response(images_exp)

        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(expected_response)['result']
        )
        self.env.bilet_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2/orders/%s/' % (TEST_API_URL, TEST_ORDER_ID),
            headers=self.make_builder_headers({
                'Authorization': 'SessionId %s' % TEST_SESSION_ID,
                'X-Frontend-Host': TEST_EXPECTED_HOST,
            }),
        )


@istest
class AfishaUserPointsTestCase(BaseAfishaTestCase):
    default_url = '/1/bundle/account/external_data/afisha/user_points/'
    http_query_args = dict(
        consumer='dev',
    )

    def setUp(self):
        super(AfishaUserPointsTestCase, self).setUp()
        self.env.bilet_api.set_response_value(
            'user_points',
            TEST_USER_POINTS_RESPONSE,
        )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(TEST_USER_POINTS_RESPONSE)['result']
        )
        self.env.bilet_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2/user/points/' % TEST_API_URL,
            headers=self.make_builder_headers({
                'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
            }),
        )

    def test_ok_with_session(self):
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(TEST_USER_POINTS_RESPONSE)['result']
        )
        self.env.bilet_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2/user/points/' % TEST_API_URL,
            headers=self.make_builder_headers({
                'Authorization': 'SessionId %s' % TEST_SESSION_ID,
                'X-Frontend-Host': TEST_EXPECTED_HOST,
            }),
        )

    def test_bilet_api_unavailable(self):
        self.env.bilet_api.set_response_side_effect(
            'user_points',
            BiletApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.bilet_api_failed'])

    def test_result_taken_from_cache(self):
        self.env.personality_api.set_response_value(
            'passport_external_data_get',
            passport_external_data_response(
                item_id='afisha_user_points',
                modified_at=int(time()),
                data=json.loads(TEST_USER_POINTS_RESPONSE)['result'],
            ),
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(TEST_USER_POINTS_RESPONSE)['result']
        )

        eq_(len(self.env.personality_api.requests), 1)  # чтение из кэша
        eq_(len(self.env.bilet_api.requests), 0)
