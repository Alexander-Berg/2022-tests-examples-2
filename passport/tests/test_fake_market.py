# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.market import (
    BaseMarketContentApiError,
    MarketContentApi,
)
from passport.backend.core.builders.market.faker.fake_market import (
    FakeMarketContentApi,
    market_content_api_user_orders_response,
    market_content_api_user_wishlist_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 1
TEST_API_KEY = '123'
TEST_TOKEN = 'token'
TEST_REMOTE_IP = '127.0.0.1'


@with_settings(
    MARKET_CONTENT_API_URL='http://content_api/',
    MARKET_CONTENT_API_RETRIES=2,
    MARKET_CONTENT_API_TIMEOUT=1,
    MARKET_CONTENT_API_KEY=TEST_API_KEY,
)
class FakeContentApiTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_content_api = FakeMarketContentApi()
        self.fake_content_api.start()

    def tearDown(self):
        self.fake_content_api.stop()
        del self.fake_content_api

    def test_set_response_side_effect(self):
        ok_(not self.fake_content_api._mock.request.called)

        builder = MarketContentApi()
        self.fake_content_api.set_response_side_effect('user_orders', BaseMarketContentApiError)
        with assert_raises(BaseMarketContentApiError):
            builder.user_orders(oauth_token=TEST_TOKEN)
        assert_builder_requested(self.fake_content_api, times=1)

    def test_set_user_orders_response_value(self):
        ok_(not self.fake_content_api._mock.request.called)

        builder = MarketContentApi()
        self.fake_content_api.set_response_value('user_orders', market_content_api_user_orders_response())
        result = builder.user_orders(oauth_token=TEST_TOKEN)
        eq_(result, json.loads(market_content_api_user_orders_response()))
        assert_builder_requested(self.fake_content_api, times=1)

    def test_set_user_wishlist_response(self):
        ok_(not self.fake_content_api._mock.request.called)

        items = [
            {
                'kind': 'toaster',
                'description': 'a good one',
                'name': 'Good Toaster',
            },
        ]

        builder = MarketContentApi()
        self.fake_content_api.set_response_value(
            'user_wishlist',
            market_content_api_user_wishlist_response(items),
        )
        result = builder.user_wishlist(TEST_REMOTE_IP, oauth_token=TEST_TOKEN)
        eq_(result, json.loads(market_content_api_user_wishlist_response(items)))
        assert_builder_requested(self.fake_content_api, times=1)

    def test_set_user_wishlist_extended_response(self):
        ok_(not self.fake_content_api._mock.request.called)

        items = [
            {
                'kind': 'toaster',
                'description': 'a good one',
                'name': 'Good Toaster',
                'price': 1,
                'photo': 'https://mds-url',
            },
        ]

        builder = MarketContentApi()
        self.fake_content_api.set_response_value(
            'user_wishlist',
            market_content_api_user_wishlist_response(items),
        )
        result = builder.user_wishlist(TEST_REMOTE_IP, oauth_token=TEST_TOKEN)
        eq_(result, json.loads(market_content_api_user_wishlist_response(items)))
        assert_builder_requested(self.fake_content_api, times=1)

    def test_set_user_wishlist_empty_response(self):
        ok_(not self.fake_content_api._mock.request.called)

        builder = MarketContentApi()
        self.fake_content_api.set_response_value(
            'user_wishlist',
            market_content_api_user_wishlist_response(),
        )
        result = builder.user_wishlist(TEST_REMOTE_IP, oauth_token=TEST_TOKEN)
        eq_(result, json.loads(market_content_api_user_wishlist_response()))
        assert_builder_requested(self.fake_content_api, times=1)
