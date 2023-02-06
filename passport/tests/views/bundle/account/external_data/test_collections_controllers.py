# -*- coding: utf-8 -*-
from time import time

from nose.tools import (
    eq_,
    istest,
)
from passport.backend.core.builders.collections import CollectionsApiTemporaryError
from passport.backend.core.builders.collections.faker.fake_collections_api import (
    collections_api_error_response,
    collections_successful_response,
    pictures_successful_response,
)
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import passport_external_data_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseExternalDataTestCase,
    TEST_COOKIE_HEADERS,
    TEST_DATASYNC_API_URL,
    TEST_NORMALIZED_PUBLIC_ID,
    TEST_SESSION_ID,
)


TEST_API_URL = 'https://collections.net'
TEST_URL = 'https://some.url'
TEST_COLLECTIONS_RESPONSE = [
    {
        'id': 1,
        'preview': {
            'id': 1,
            'mds_group_id': 1,
            'mds_key': 'avatar-key',
        },
        'slug': 'izbrannoe-iz-yandex-kartinok',
        'title': u'Избранное из Яндекс Картинок',
        'url': TEST_URL,
    },
]
TEST_PICTURES_RESPONSE = [
    {
        'id': 'id-for-nothing',
        'mds_group_id': 'group-id',
        'mds_key': 'avatar-key',
    },
]
TEST_EXPECTED_HOST = 'yandex.ru'


@with_settings_hosts(
    COLLECTIONS_API_URL=TEST_API_URL,
    DATASYNC_API_URL=TEST_DATASYNC_API_URL,
)
class BaseCollectionsTestCase(BaseExternalDataTestCase):
    oauth_scope = 'oauth:grant_xtoken'


@istest
class PicturesCollectionsTestCase(BaseCollectionsTestCase):
    default_url = '/1/bundle/account/external_data/pictures/collections/'
    http_query_args = dict(
        consumer='dev',
    )

    def setUp(self):
        super(PicturesCollectionsTestCase, self).setUp()
        self.env.collections_api.set_response_value(
            'collections',
            collections_successful_response([
                {
                    'title': u'Избранное из Яндекс Картинок',
                    'cards_count': 2,
                    'slug': 'izbrannoe-iz-yandex-kartinok',
                    'is_private': True,
                    'url': TEST_URL,
                },
            ]),
        )

    def test_ok_with_session_and_pagination(self):
        rv = self.make_request(query_args={'page': 3, 'page_size': 20}, headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            collections=TEST_COLLECTIONS_RESPONSE,
        )
        self.env.collections_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/api/boards/?sort=-service.updated_at&previews_count=1&owner.public_id=%s&page=3&page_size=20' % (
                TEST_API_URL,
                TEST_NORMALIZED_PUBLIC_ID,
            ),
            headers={
                'Cookie': 'Session_id=%s' % TEST_SESSION_ID,
                'X-Forwarded-Host': TEST_EXPECTED_HOST,
                'Accept': 'application/json',
            },
        )

    def test_collections_api_unavailable(self):
        self.env.collections_api.set_response_side_effect(
            'collections',
            CollectionsApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_error_response(rv, ['backend.collections_api_failed'])

    def test_empty_response(self):
        self.env.collections_api.set_response_value(
            'collections',
            {
                'results': [
                    {},
                ],
            },
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            collections=[],
        )

    def test_not_found_ok(self):
        self.env.collections_api.set_response_value(
            'collections',
            collections_api_error_response('Invalid request', message='login is not valid'),
            status=404,
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            collections=[],
        )

    def test_result_taken_from_cache(self):
        self.env.personality_api.set_response_value(
            'passport_external_data_get',
            passport_external_data_response(
                item_id='pictures_collections',
                modified_at=int(time()),
                data=dict(collections=TEST_COLLECTIONS_RESPONSE),
                meta={'params': {'page': 1, 'page_size': 10}},
            ),
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            collections=TEST_COLLECTIONS_RESPONSE,
        )

        eq_(len(self.env.personality_api.requests), 1)  # чтение из кэша
        eq_(len(self.env.collections_api.requests), 0)


@istest
class PicturesFavouritesTestCase(BaseCollectionsTestCase):
    default_url = '/1/bundle/account/external_data/pictures/favourites/'
    http_query_args = dict(
        consumer='dev',
    )

    def setUp(self):
        super(PicturesFavouritesTestCase, self).setUp()
        self.env.collections_api.set_response_value(
            'pictures',
            pictures_successful_response(),
        )

    def test_ok_with_session_and_pagination(self):
        rv = self.make_request(query_args={'page': 3, 'page_size': 20}, headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            pictures=TEST_PICTURES_RESPONSE,
        )
        self.env.collections_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/api/cards/?sort=-id&board.slug=izbrannoe-iz-yandex-kartinok&board.owner.public_id=%s&page=3&page_size=20' % (
                TEST_API_URL,
                TEST_NORMALIZED_PUBLIC_ID,
            ),
            headers={
                'Cookie': 'Session_id=%s' % TEST_SESSION_ID,
                'X-Forwarded-Host': TEST_EXPECTED_HOST,
                'Accept': 'application/json',
            },
        )

    def test_collections_api_unavailable(self):
        self.env.collections_api.set_response_side_effect(
            'pictures',
            CollectionsApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_error_response(rv, ['backend.collections_api_failed'])

    def test_empty_response(self):
        self.env.collections_api.set_response_value(
            'pictures',
            {
                'results': [
                    {},
                ],
            },
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            pictures=[],
        )

    def test_not_found_ok(self):
        self.env.collections_api.set_response_value(
            'pictures',
            collections_api_error_response('Invalid request', message='login is not valid'),
            status=400,
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            pictures=[],
        )

    def test_result_taken_from_cache(self):
        self.env.personality_api.set_response_value(
            'passport_external_data_get',
            passport_external_data_response(
                item_id='pictures_favourites',
                modified_at=int(time()),
                data=dict(pictures=TEST_PICTURES_RESPONSE),
                meta={'params': {'page': 1, 'page_size': 10}},
            ),
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            pictures=TEST_PICTURES_RESPONSE,
        )

        eq_(len(self.env.personality_api.requests), 1)  # чтение из кэша
        eq_(len(self.env.collections_api.requests), 0)
