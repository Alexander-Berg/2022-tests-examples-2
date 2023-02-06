# -*- coding: utf-8 -*-
from time import time

from nose.tools import (
    eq_,
    istest,
    ok_,
)
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import passport_external_data_response
from passport.backend.core.builders.music_api import MusicApiTemporaryError
from passport.backend.core.builders.music_api.faker import music_account_status_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import fake_tvm_credentials_data

from .base import (
    BaseExternalDataTestCase,
    TEST_COOKIE_HEADERS,
    TEST_TOKEN_HEADERS,
    TEST_TVM_TICKET_BLACKBOX,
    TEST_TVM_TICKET_OTHER,
    TEST_UID,
    TEST_USER_TICKET,
)


TEST_API_URL = 'https://music.net'
TEST_SUBSCRIPTION_INFO = {'canStartTrial': False}
TEST_PLUS_INFO = {
    'migrated': True,
    'isTutorialCompleted': True,
    'hasPlus': True,
}
TEST_MOSCOW_IP = '95.108.173.106'
TEST_COUNTRY_ID = 225


TEST_EXPECTED_RESPONSE_DATA = {
    'account': {
        'displayName': 'foo',
        'firstName': 'test1',
        'secondName': 'test2',
        'fullName': 'test1 test2',
        'hostedUser': False,
        'now': '2017-09-11T12:09:37+00:00',
        'region': 225,
        'serviceAvailable': True,
        'uid': 123,
    },
    'adDisableable': False,
    'hasOrdersHistory': True,
    'isMobileUser': False,
}


@istest
@with_settings_hosts(
    MUSIC_API_URL=TEST_API_URL,
)
class MusicAccountStatusTestCase(BaseExternalDataTestCase):
    default_url = '/1/bundle/account/external_data/music/account_status/'
    http_query_args = dict(
        consumer='dev',
    )
    oauth_scope = 'music:read'

    def setUp(self):
        super(MusicAccountStatusTestCase, self).setUp()
        self.env.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    '1': {'alias': 'blackbox', 'ticket': TEST_TVM_TICKET_BLACKBOX},
                    '2': {'alias': 'datasync_api', 'ticket': TEST_TVM_TICKET_OTHER},
                    '3': {'alias': 'music_api', 'ticket': TEST_TVM_TICKET_OTHER},
                },
            ),
        )
        self.env.music_api.set_response_value(
            'account_status',
            music_account_status_response(
                subscription_info=TEST_SUBSCRIPTION_INFO,
                plus_info=TEST_PLUS_INFO,
            ),
        )

    def test_ok_with_token(self):
        rv = self.make_request(
            headers=dict(
                user_ip=TEST_MOSCOW_IP,
                **TEST_TOKEN_HEADERS
            ),
        )
        self.assert_ok_response(
            rv,
            subscription=TEST_SUBSCRIPTION_INFO,
            plus=TEST_PLUS_INFO,
            **TEST_EXPECTED_RESPONSE_DATA
        )
        self.env.music_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/account/status?__uid=%s&region=%s&ip=%s' % (
                TEST_API_URL,
                TEST_UID,
                TEST_COUNTRY_ID,
                TEST_MOSCOW_IP,
            ),
            headers={
                'Accept': 'application/json',
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Ya-User-Ticket': TEST_USER_TICKET,
            },
        )

    def test_ok_with_session(self):
        rv = self.make_request(
            headers=dict(
                user_ip=TEST_MOSCOW_IP,
                **TEST_COOKIE_HEADERS
            ),
        )
        self.assert_ok_response(
            rv,
            subscription=TEST_SUBSCRIPTION_INFO,
            plus=TEST_PLUS_INFO,
            **TEST_EXPECTED_RESPONSE_DATA
        )
        self.env.music_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/account/status?__uid=%s&region=%s&ip=%s' % (
                TEST_API_URL,
                TEST_UID,
                TEST_COUNTRY_ID,
                TEST_MOSCOW_IP,
            ),
            headers={
                'Accept': 'application/json',
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Ya-User-Ticket': TEST_USER_TICKET,
            },
        )

    def test_music_unavailable(self):
        self.env.music_api.set_response_side_effect(
            'account_status',
            MusicApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.music_api_failed'])

    def test_no_region_id(self):
        resp = self.make_request(
            headers=dict(
                user_ip='127.0.0.1',
                **TEST_COOKIE_HEADERS
            ),
        )
        self.assert_ok_response(resp, subscription={})
        ok_(not self.env.music_api.requests)

    def test_result_taken_from_cache(self):
        self.env.personality_api.set_response_value(
            'passport_external_data_get',
            passport_external_data_response(
                item_id='music_account_status',
                modified_at=int(time()),
                data={
                    'subscription': TEST_SUBSCRIPTION_INFO,
                    'plus': TEST_PLUS_INFO,
                },
            ),
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            subscription=TEST_SUBSCRIPTION_INFO,
            plus=TEST_PLUS_INFO,
        )

        eq_(len(self.env.personality_api.requests), 1)  # чтение из кэша
        eq_(len(self.env.music_api.requests), 0)
