# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.music_api import MusicApi
from passport.backend.core.builders.music_api.exceptions import (
    MusicApiInvalidResponseError,
    MusicApiPermanentError,
)
from passport.backend.core.builders.music_api.faker import (
    FakeMusicApi,
    music_account_status_response,
    music_error_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
)


TEST_UID = 123
TEST_SERVICE_TICKET = 'service-ticket'
TEST_USER_TICKET = 'user-ticket'
TEST_USER_IP = '1.2.3.4'

TEST_PROMO_CODE = '12345'
TEST_INVALID_PROMO_CODE = 'invalid-promo'
TEST_ORDER_ID = 4567890

TEST_COUNTRY_ID = 225


@with_settings(
    MUSIC_API_URL='http://localhost/api/',
    MUSIC_API_TIMEOUT=0.5,
    MUSIC_API_RETRIES=2,
)
class TestMusicApiCommon(unittest.TestCase):
    def setUp(self):
        self.music_api = MusicApi(tvm_credentials_manager=mock.Mock())
        self.music_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.music_api.useragent.request.return_value = self.response
        self.music_api.useragent.request_error_class = self.music_api.temporary_error_class
        self.response.content = b'{}'
        self.response.status_code = 200

    def tearDown(self):
        del self.music_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = 'not a json'
        with assert_raises(MusicApiInvalidResponseError):
            self.music_api.account_status(
                TEST_UID,
                TEST_USER_TICKET,
                country_id=TEST_COUNTRY_ID,
                user_ip=TEST_USER_IP,
            )

    def test_server_error(self):
        self.response.status_code = 503
        self.response.content = music_error_response('ServerError')
        with assert_raises(MusicApiPermanentError):
            self.music_api.account_status(
                TEST_UID,
                TEST_USER_TICKET,
                country_id=TEST_COUNTRY_ID,
                user_ip=TEST_USER_IP,
            )

    def test_bad_status_code(self):
        self.response.status_code = 418
        self.response.content = music_error_response('IAmATeapot')
        with assert_raises(MusicApiPermanentError):
            self.music_api.account_status(
                TEST_UID,
                TEST_USER_TICKET,
                country_id=TEST_COUNTRY_ID,
                user_ip=TEST_USER_IP,
            )


@with_settings(
    MUSIC_API_URL='http://localhost/api/',
    MUSIC_API_TIMEOUT=0.5,
    MUSIC_API_RETRIES=2,
)
class TestMusicApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_music_api = FakeMusicApi()
        self.fake_music_api.start()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'music_api',
                    'ticket': TEST_SERVICE_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()
        self.music_api = MusicApi()

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        self.fake_music_api.stop()
        del self.fake_tvm_credentials_manager
        del self.fake_music_api

    def assert_headers_are_ok(self):
        self.fake_music_api.requests[0].assert_headers_contain({
            'Accept': 'application/json',
            'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
            'X-Ya-User-Ticket': TEST_USER_TICKET,
        })

    def test_account_status_ok(self):
        self.fake_music_api.set_response_value(
            'account_status',
            music_account_status_response(),
        )
        response = self.music_api.account_status(
            uid=TEST_UID,
            user_ticket=TEST_USER_TICKET,
            country_id=TEST_COUNTRY_ID,
            user_ip=TEST_USER_IP,
        )
        eq_(
            response,
            json.loads(music_account_status_response())['result'],
        )
        eq_(len(self.fake_music_api.requests), 1)
        self.fake_music_api.requests[0].assert_url_starts_with('http://localhost/api/account/status')
        self.fake_music_api.requests[0].assert_query_equals({
            '__uid': str(TEST_UID),
            'region': str(TEST_COUNTRY_ID),
            'ip': TEST_USER_IP,
        })
        self.assert_headers_are_ok()
