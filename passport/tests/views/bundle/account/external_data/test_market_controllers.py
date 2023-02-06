# -*- coding: utf-8 -*-
from time import time

from nose.tools import (
    eq_,
    istest,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_OAUTH_TOKEN
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import passport_external_data_response
from passport.backend.core.builders.market import MarketContentApiTemporaryError
from passport.backend.core.builders.market.faker.fake_market import (
    build_wishlist_item,
    market_content_api_user_wishlist_response,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseExternalDataTestCase,
    TEST_COOKIE_HEADERS,
    TEST_DATASYNC_API_URL,
    TEST_SESSION_ID,
    TEST_TOKEN_HEADERS,
    TEST_USER_IP,
)


TEST_API_URL = 'https://market.net'
TEST_API_KEY = 'api_key'
TEST_EXPECTED_HOST = 'yandex.ru'


@istest
@with_settings_hosts()
class MarketOrdersTestCase(BaseExternalDataTestCase):
    oauth_scope = 'market:content-api'
    default_url = '/1/bundle/account/external_data/market/orders/'
    http_query_args = dict(
        consumer='dev',
    )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(rv, orders=[])
        assert self.env.market_content_api.requests == []
        assert self.env.personality_api.requests == []

    def test_ok_with_session_and_pagination(self):
        rv = self.make_request(query_args={'page': 3, 'page_size': 20}, headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(rv, orders=[])
        assert self.env.market_content_api.requests == []
        assert self.env.personality_api.requests == []


@istest
@with_settings_hosts(
    MARKET_CONTENT_API_URL=TEST_API_URL,
    MARKET_CONTENT_API_KEY=TEST_API_KEY,
    DATASYNC_API_URL=TEST_DATASYNC_API_URL,
    DATASYNC_CACHE_RETRIES=1,
)
class MarketFavouritesTestCase(BaseExternalDataTestCase):
    oauth_scope = 'market:content-api'
    default_url = '/1/bundle/account/external_data/market/favourites/'
    http_query_args = dict(
        consumer='dev',
    )

    def setUp(self):
        super(MarketFavouritesTestCase, self).setUp()
        self.env.market_content_api.set_response_value(
            'user_wishlist',
            market_content_api_user_wishlist_response(items_data=[{}]),
        )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            items=[build_wishlist_item()],
        )
        self.env.market_content_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2.1.0/user/wishlist/items?sort=create_date&how=desc&fields=CATEGORY,PHOTO,PRICE&count=10&page=1&remote_ip=%s' % (
                TEST_API_URL,
                TEST_USER_IP,
            ),
            headers={
                'Authorization': TEST_API_KEY,
                'X-User-Authorization': 'OAuth {}'.format(TEST_OAUTH_TOKEN),
            },
        )

    def test_ok_with_session_and_pagination(self):
        rv = self.make_request(query_args={'page': 3, 'page_size': 20}, headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            items=[build_wishlist_item()],
        )
        self.env.market_content_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v2.1.0/user/wishlist/items?sort=create_date&how=desc&fields=CATEGORY,PHOTO,PRICE&count=20&page=3&remote_ip=%s' % (
                TEST_API_URL,
                TEST_USER_IP,
            ),
            headers={
                'Authorization': TEST_API_KEY,
                'X-User-Authorization': 'SessionId Id=%s; Host=%s' % (TEST_SESSION_ID, TEST_EXPECTED_HOST),
            },
        )

    def test_market_unavailable(self):
        self.env.market_content_api.set_response_side_effect(
            'user_wishlist',
            MarketContentApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.market_api_failed'])

    def test_result_taken_from_cache(self):
        self.env.personality_api.set_response_value(
            'passport_external_data_get',
            passport_external_data_response(
                item_id='market_favourites',
                modified_at=int(time()),
                data=dict(items=[build_wishlist_item()]),
                meta={'params': {'page': 1, 'page_size': 10}},
            ),
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            items=[build_wishlist_item()],
        )
        eq_(len(self.env.personality_api.requests), 1)  # чтение из кэша
        eq_(len(self.env.market_content_api.requests), 0)
