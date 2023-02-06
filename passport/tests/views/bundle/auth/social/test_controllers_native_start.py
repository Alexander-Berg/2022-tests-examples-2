# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
)
from passport.backend.core.builders.ufo_api.faker.ufo_api import ufo_api_profile_item
from passport.backend.core.env_profile.profiles import UfoProfile
from passport.backend.core.test.consts import TEST_TRACK_ID1
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts

from .base import BaseTestCase
from .base_test_data import (
    TEST_ACCEPT_LANGUAGE,
    TEST_BROKER_CONSUMER,
    TEST_CONSUMER_IP1,
    TEST_HOST,
    TEST_PROVIDER,
    TEST_PROVIDER_TOKEN,
    TEST_RETPATH,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
    TEST_USERID,
)


@with_settings_hosts(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    AUTH_ALLOWED_PROVIDERS=[TEST_PROVIDER['code']],
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=True,
    YDB_PERCENTAGE=0,
)
class TestAuthSocialNativeStart(BaseTestCase):
    default_url = '/1/bundle/auth/social/native_start/?consumer=dev'
    http_method = 'POST'
    http_query_args = {
        'broker_consumer': TEST_BROKER_CONSUMER,
        'provider': 'vk',
        'provider_token': TEST_PROVIDER_TOKEN,
        'retpath': TEST_RETPATH,
    }
    http_headers = {
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
        'cookie': TEST_USER_COOKIE,
        'accept_language': TEST_ACCEPT_LANGUAGE,
        'consumer_ip': TEST_CONSUMER_IP1,
    }

    def setUp(self):
        super(TestAuthSocialNativeStart, self).setUp()
        self._builder = self.get_primary_builder()
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])
        self.setup_push_send_response()

        full_profile = dict(
            as_list_freq_3m=[('AS1', 1)],
            as_list_freq_6m=[('AS1', 1)],
        )
        self.setup_profile_responses(
            [
                ufo_api_profile_item(
                    # фреш-профили от полного профиля отличаются особым timeuuid
                    timeuuid=UfoProfile.PROFILE_FAKE_UUID,
                    data=full_profile,
                ),
            ],
        )

        self.setup_kolmogor_responses()

    def tearDown(self):
        del self._builder
        super(TestAuthSocialNativeStart, self).tearDown()

    def _setup_task_for_token(self):
        args = dict()
        task = self._builder.build_task(**args)
        self._builder.setup_task_for_token(task)

    def _setup_account(self, **kwargs):
        self._builder.setup_social_profiles([self._builder.build_social_profile()])
        self._builder.setup_yandex_accounts([self._builder.build_yandex_social_account()])

    def build_auth_not_allowed_response(self, expected=None):
        profile_response = self._builder.get_profile_response()
        defaults = dict(
            broker_consumer=TEST_BROKER_CONSUMER,
            profile=profile_response,
            return_brief_profile=False,
        )
        expected = merge_dicts(defaults, expected) if expected else defaults
        return self._builder.build_auth_not_allowed_response(**expected)

    def assert_ok_antifraud_score_request(self, request):
        ok_(request.post_args)
        request_data = json.loads(request.post_args)

        params = AntifraudScoreParams.build_social_auth()
        params.external_id = 'track-' + TEST_TRACK_ID1
        params.ip = TEST_USER_IP
        params.social_provider_code = TEST_PROVIDER['code']
        params.social_userid = TEST_USERID
        params.uid = 123
        params.user_agent = TEST_USER_AGENT
        params.device_id = 'device_id'
        params.device_ifv = 'ifv'
        params.device_name = 'device_name'
        params.is_mobile = True
        params.lah_uids = []
        params.surface = 'social_native_start'
        eq_(request_data, params.as_dict())

        request.assert_query_contains(dict(consumer='passport'))

    def setup_push_send_response(self):
        self.env.push_api.set_response_side_effect('send', ['OK'])

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def test_invalid_token(self):
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            json.dumps({
                'error': {
                    'code': 'OAuthTokenInvalidError',
                    'message': 'Invalid code',
                },
            }),
        )

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['provider_token.invalid'],
            is_native=True,
            return_brief_profile=False,
            track_id=TEST_TRACK_ID1,
            retpath=TEST_RETPATH,
            broker_consumer=TEST_BROKER_CONSUMER,
        )

    def test_no_provider(self):
        rv = self.make_request(exclude_args=['provider'])
        self.assert_error_response(rv, ['application.empty'], retpath=TEST_RETPATH)

    def test_no_provider_token(self):
        rv = self.make_request(exclude_args=['provider_token'])
        self.assert_error_response(rv, ['provider_token.empty'], retpath=TEST_RETPATH)

    def test_no_retpath(self):
        rv = self.make_request(exclude_args=['retpath'])
        self.assert_error_response(rv, ['retpath.empty'])

    def test_morda_ru_retpath(self):
        self._setup_task_for_token()
        self._setup_account()
        self._builder.setup_profile_creation()
        self._builder.setup_yandex_token_generation()

        rv = self.make_request(query_args=dict(retpath='https://www.yandex.ru/'))

        self.assert_ok_response(
            rv,
            check_all=False,
            retpath='https://www.yandex.ru/',
        )

    def test_morda_com_retpath(self):
        self._setup_task_for_token()
        self._setup_account()
        self._builder.setup_profile_creation()
        self._builder.setup_yandex_token_generation()

        rv = self.make_request(query_args=dict(retpath='https://www.yandex.com/'))

        self.assert_ok_response(
            rv,
            check_all=False,
            retpath='https://www.yandex.com/?redirect=0',
        )

    def test_morda_com_retpath_with_query(self):
        self._setup_task_for_token()
        self._setup_account()
        self._builder.setup_profile_creation()
        self._builder.setup_yandex_token_generation()

        rv = self.make_request(query_args=dict(retpath='https://www.yandex.com/?foo=%D1%8F'))

        self.assert_ok_response(
            rv,
            check_all=False,
            retpath='https://www.yandex.com/?foo=%D1%8F&redirect=0',
        )

    def test_morda_com_retpath_error_response(self):
        rv = self.make_request(
            query_args=dict(retpath='https://www.yandex.com/'),
            exclude_args=['provider'],
        )

        self.assert_error_response(
            rv,
            ['application.empty'],
            retpath='https://www.yandex.com/?redirect=0',
        )

    def test_broker_consumer(self):
        self._setup_task_for_token()
        self._setup_account()
        self._builder.setup_profile_creation()
        self._builder.setup_yandex_token_generation()

        rv = self.make_request(query_args=dict(broker_consumer=TEST_BROKER_CONSUMER))

        self.assert_ok_response(rv, check_all=False)

        track = self.track_manager.read(TEST_TRACK_ID1)
        eq_(track.social_broker_consumer, TEST_BROKER_CONSUMER)
