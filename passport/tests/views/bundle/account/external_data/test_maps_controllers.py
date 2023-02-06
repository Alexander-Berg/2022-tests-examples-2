# -*- coding: utf-8 -*-
import json

from nose.tools import istest
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.datasync_api import (
    DatasyncApiObjectNotFoundError,
    DatasyncApiTemporaryError,
)
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import maps_bookmarks_response
from passport.backend.core.builders.geosearch import GeoSearchApiTemporaryError
from passport.backend.core.builders.geosearch.faker import (
    empty_response,
    geosearch_response_geo,
    geosearch_response_geo_parsed,
    geosearch_response_org,
    geosearch_response_org_parsed,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    TEST_CLIENT_ID_2,
)

from .base import (
    BaseExternalDataTestCase,
    TEST_COOKIE_HEADERS,
    TEST_TOKEN_HEADERS,
    TEST_TVM_TICKET_OTHER,
    TEST_UID,
)


TEST_API_URL = 'https://maps.net'
TEST_URI_GEO = 'ymapsbm1://geo?text=leningradka&ll=37.536733,55.682336&spn=0.432587,0.095074'
TEST_URI_ORG = 'ymapsbm1://org?oid=1'
TEST_URI_PIN = 'ymapsbm1://pin?ll=37.586926,55.734042'


@with_settings_hosts(
    DATASYNC_API_URL=TEST_API_URL,
)
class BaseMapsTestCase(BaseExternalDataTestCase):
    oauth_scope = 'oauth:grant_xtoken'

    http_query_args = dict(
        consumer='dev',
    )


@istest
class MapsBookmarksTestCase(BaseMapsTestCase):
    default_url = '/1/bundle/account/external_data/maps/bookmarks/'

    def setUp(self):
        super(MapsBookmarksTestCase, self).setUp()
        self.env.personality_api.set_response_value(
            'maps_bookmarks',
            maps_bookmarks_response(),
        )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            bookmarks=json.loads(maps_bookmarks_response())['items'],
        )
        self.env.personality_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/personality/profile/maps_common/bookmarks?offset=0&limit=10' % TEST_API_URL,
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
            },
        )

    def test_ok_with_session_and_pagination(self):
        rv = self.make_request(query_args={'page': 3, 'page_size': 20}, headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            bookmarks=json.loads(maps_bookmarks_response())['items'],
        )
        self.env.personality_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/personality/profile/maps_common/bookmarks?offset=40&limit=20' % TEST_API_URL,
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
            },
        )

    def test_personality_api_unavailable(self):
        self.env.personality_api.set_response_side_effect(
            'maps_bookmarks',
            DatasyncApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.datasync_api_failed'])

    def test_history_empty(self):
        self.env.personality_api.set_response_side_effect(
            'maps_bookmarks',
            DatasyncApiObjectNotFoundError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(rv, bookmarks=[])


@with_settings_hosts(
    GEOSEARCH_API_URL='http://localhost',
    GEOSEARCH_API_TIMEOUT=1,
    GEOSEARCH_API_RETRIES=2,
    PORTAL_LANGUAGES=('ru', 'en'),
)
class TestMapsGeoSearchInfoTestCase(BaseBundleTestViews):
    consumer = 'dev'
    default_url = '/1/bundle/account/external_data/maps/bookmark_info/'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['external_info'],
        }))
        self.env.tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'geosearch_api',
                    'ticket': TEST_TVM_TICKET_OTHER,
                },
            },
        ))

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_org__ok(self):
        self.env.geosearch_api.set_response_value(
            'get_info',
            geosearch_response_org(),
        )
        rv = self.make_request(query_args={'uri': TEST_URI_ORG, 'language': 'ru'})
        self.assert_ok_response(rv, bookmark_info=geosearch_response_org_parsed())

    def test_geo__ok(self):
        self.env.geosearch_api.set_response_value(
            'get_info',
            geosearch_response_geo(),
        )
        rv = self.make_request(query_args={'uri': TEST_URI_GEO, 'language': 'en'})
        self.assert_ok_response(rv, bookmark_info=geosearch_response_geo_parsed())

    def test_pin__ok(self):
        self.env.geosearch_api.set_response_value(
            'get_info',
            empty_response(),
        )
        rv = self.make_request(query_args={'uri': TEST_URI_PIN, 'language': 'ru'})
        self.assert_ok_response(rv, bookmark_info={})

    def test_error__ok(self):
        self.env.geosearch_api.set_response_side_effect(
            'get_info',
            GeoSearchApiTemporaryError,
        )
        rv = self.make_request(query_args={'uri': TEST_URI_PIN, 'language': 'en'})
        self.assert_error_response(rv, ['backend.geosearch_api_failed'])
