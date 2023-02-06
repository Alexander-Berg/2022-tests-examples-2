# -*- coding: utf-8 -*-

import mock
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.views.bundle.auth.social.base import (
    OUTPUT_MODE_AUTHORIZATION_CODE,
    OUTPUT_MODE_SESSIONID,
    OUTPUT_MODE_XTOKEN,
)
from passport.backend.core.builders.antifraud.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_lrandoms_response,
    blackbox_sign_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import messenger_api_response
from passport.backend.core.builders.oauth.faker.oauth import oauth_bundle_successful_response
from passport.backend.core.builders.social_api.faker.social_api import (
    get_bind_response,
    get_profiles_response,
    task_data_response,
)
from passport.backend.core.builders.ufo_api.faker.ufo_api import ufo_api_profile_item
from passport.backend.core.env_profile.profiles import UfoProfile
from passport.backend.core.services import Service
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_DEVICE_ID1,
    TEST_DEVICE_NAME1,
    TEST_EMAIL1,
    TEST_PROFILE_GOOD_ESTIMATE1,
    TEST_RETPATH1,
    TEST_SOCIAL_LOGIN1,
    TEST_SOCIAL_PROFILE_ID1,
    TEST_SOCIAL_TASK_ID1,
    TEST_TRACK_ID1,
    TEST_UID1,
    TEST_UID2,
    TEST_USER_AGENT1,
    TEST_YANDEX_AUTHORIZATION_CODE1,
    TEST_YANDEX_TOKEN1,
    TEST_YANDEX_TOKEN_EXPIRES_IN1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.undefined import Undefined
from passport.backend.utils.common import deep_merge

from .base import BaseTestCase
from .base_test_data import (
    TEST_USER_IP,
    TEST_USER_LOGIN,
)


@with_settings_hosts(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=True,
    SOCIAL_API_URL='https://social/api/',
    YDB_PERCENTAGE=0,
)
class TestIssueCredentials(
    EmailTestMixin,
    BaseTestCase,
):
    default_url = '/1/bundle/auth/social/issue_credentials/?consumer=' + TEST_CONSUMER1
    http_method = 'POST'
    http_headers = dict(
        accept_language='ru',
        host='passport.yandex.ru',
        user_agent=TEST_USER_AGENT1,
        user_ip=TEST_USER_IP,
    )
    http_query_args = dict(
        track_id=TEST_TRACK_ID1,
    )

    def __init__(self, *args, **kwargs):
        super(TestIssueCredentials, self).__init__(*args, **kwargs)

        self.blackbox_login = None
        self.blackbox_uid = Undefined
        self.does_antifraud_score_deny = None
        self.does_track_allow_authorization = None
        self.is_account_disabled = None
        self.is_account_strong_password_policy_enabled = None
        self.social_profiles = None
        self.track_auth_challenge_shown = Undefined
        self.track_retpath = Undefined
        self.track_service = None
        self.track_social_task_data = Undefined
        self.track_social_output_mode = None
        self.track_uid = None
        self.ufo_estimate = None

    def setup_statbox_templates(self):
        super(TestIssueCredentials, self).setup_statbox_templates()

        self.env.statbox.bind_entry(
            'auth',
            _inherit_from=['auth'],
            accounts=str(TEST_UID1),
            consumer=TEST_CONSUMER1,
            disabled_accounts_count='0',
            enabled_accounts_count='1',
            login=self.blackbox_login,
            uid=str(TEST_UID1),
        )
        self.env.statbox.bind_entry(
            'cookie_set',
            _exclude=[
                'consumer',
                'ip_country',
                'yandexuid',
            ],
            _inherit_from=['cookie_set'],
            input_login=self.blackbox_login,
            is_auth_challenge_shown='1',
            person_country='ru',
            uid=str(TEST_UID1),
            **{'from': self.track_service}
        )
        self.env.statbox.bind_entry(
            'subscriptions',
            _exclude=['mode'],
            _inherit_from=['subscriptions'],
            consumer='-',
            sid=str(Service.by_slug(self.track_service).sid),
            uid=str(TEST_UID1),
        )
        self.env.statbox.bind_entry(
            'ufo_profile_check_imply_challenge',
            _exclude=[
                'is_fresh_profile_passed',
                'is_model_passed',
                'tensornet_estimate',
                'tensornet_model',
                'tensornet_status',
                'yandexuid',
            ],
            _inherit_from=['ufo_profile_checked'],
            accounts=str(TEST_UID1),
            af_action='ALLOW',
            af_is_auth_forbidden='0',
            af_is_challenge_required='1',
            af_tags='email_hint',
            consumer=TEST_CONSUMER1,
            current=self.make_user_profile(
                raw_env=dict(
                    ip=TEST_USER_IP,
                    user_agent_info=None,
                    yandexuid=None,
                ),
            ).as_json,
            decision_source='antifraud_api',
            disabled_accounts_count='0',
            enabled_accounts_count='1',
            is_challenge_required='1',
            is_mobile='0',
            ufo_distance='0',
            uid=str(TEST_UID1),
        )
        self.env.statbox.bind_entry(
            'user_notified_about_authentication',
            _inherit_from=['user_notified_about_authentication'],
            consumer=TEST_CONSUMER1,
            uid=str(TEST_UID1),
        )
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            _inherit_from=['profile_threshold_exceeded'],
            consumer=TEST_CONSUMER1,
            decision_source='antifraud_api',
            uid=str(TEST_UID1),
        )

    def setup_environment(self):
        self.setup_default_environment()
        self.setup_grants()
        self.setup_track()
        self.setup_social()
        self.setup_blackbox()
        self.setup_oauth()
        self.setup_antifraud()
        self.setup_oauth_device_status_response()
        self.setup_ufo()
        self.setup_statbox_templates()
        self.setup_messenger()
        self.setup_kolmogor_responses()

    def setup_default_environment(self):
        self.track_id = TEST_TRACK_ID1

        if self.track_retpath is Undefined:
            self.track_retpath = TEST_RETPATH1

        if self.track_auth_challenge_shown is Undefined:
            self.track_auth_challenge_shown = True

        if self.blackbox_login is None:
            self.blackbox_login = TEST_SOCIAL_LOGIN1

        if self.social_profiles is None:
            self.social_profiles = [self.build_social_profile()]

    def setup_grants(self, **kwargs):
        super(TestIssueCredentials, self).setup_grants()
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    grants=dict(
                        auth_social=['issue_credentials'],
                    ),
                    networks=[TEST_CONSUMER_IP1],
                ),
            },
        )

    def setup_track(self):
        if self.track_social_task_data is Undefined:
            self.track_social_task_data = task_data_response(
                email=TEST_EMAIL1,
            )

        self.track_manager.create(
            consumer=TEST_CONSUMER1,
            track_id=TEST_TRACK_ID1,
            track_type='authorize',
        )
        with self.track_transaction() as track:
            if self.track_social_task_data:
                track.social_task_data = self.track_social_task_data

            track.social_task_id = TEST_SOCIAL_TASK_ID1

            if self.track_retpath:
                track.retpath = self.track_retpath

            track.social_output_mode = OUTPUT_MODE_SESSIONID
            if self.track_social_output_mode:
                track.social_output_mode = self.track_social_output_mode

            track.uid = TEST_UID1 if self.track_uid is None else self.track_uid

            if self.does_track_allow_authorization:
                track.allow_authorization = True

            if self.track_service:
                track.service = self.track_service

            if self.track_auth_challenge_shown:
                track.is_auth_challenge_shown = True

    def setup_social(self):
        self.env.social_api.set_response_side_effect(
            'get_profiles',
            [
                get_profiles_response(self.social_profiles),
            ],
        )
        self.env.social_api.set_response_value('bind_task_profile', get_bind_response())

    def build_social_profile(self):
        return dict(uid=TEST_UID1, profile_id=TEST_SOCIAL_PROFILE_ID1, allow_auth=True)

    def setup_blackbox(self):
        b = self.get_primary_builder()

        userinfo_args = b.build_yandex_social_account()

        userinfo_args = deep_merge(
            userinfo_args,
            dict(
                emails=[
                    self.create_validated_external_email(TEST_USER_LOGIN, 'gmail.com'),
                ],
            ),
        )

        if self.is_account_strong_password_policy_enabled:
            userinfo_args = deep_merge(userinfo_args, dict(subscribed_to=[Service.by_slug('strongpwd')]))

        if self.blackbox_uid is not Undefined:
            userinfo_args = deep_merge(userinfo_args, dict(uid=self.blackbox_uid))

        if self.blackbox_login is not None:
            userinfo_args = deep_merge(userinfo_args, dict(login=self.blackbox_login))

        if self.is_account_disabled:
            userinfo_args = deep_merge(userinfo_args, dict(attributes={'account.is_disabled': '1'}))

        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple([userinfo_args]),
            ],
        )
        self.env.blackbox.set_response_side_effect(
            'createsession',
            [
                blackbox_createsession_response(),
            ],
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_response_side_effect('sign', [blackbox_sign_response()])

    def setup_antifraud(self):
        if self.does_antifraud_score_deny:
            score_response = antifraud_score_response(action=ScoreAction.DENY)
        else:
            score_response = antifraud_score_response()
        self.env.antifraud_api.set_response_side_effect('score', [score_response])

    def setup_oauth_device_status_response(self):
        self.env.oauth.set_response_side_effect(
            'device_status',
            [
                oauth_bundle_successful_response(
                    device_id=TEST_DEVICE_ID1,
                    device_name=TEST_DEVICE_NAME1,
                    has_auth_on_device=False,
                ),
            ],
        )

    def setup_ufo(self):
        estimate = TEST_PROFILE_GOOD_ESTIMATE1 if self.ufo_estimate is None else self.ufo_estimate
        full_profile = dict(
            as_list_freq_3m=[('AS2', 1)],
            as_list_freq_6m=[('AS2', 1)],
        )
        self.setup_profile_responses(
            ufo_items=[
                ufo_api_profile_item(
                    # фреш-профили от полного профиля отличаются особым timeuuid
                    timeuuid=UfoProfile.PROFILE_FAKE_UUID,
                    data=full_profile,
                ),
            ],
            estimate=estimate,
        )

    def setup_messenger(self):
        self.env.messenger_api.set_response_side_effect(
            'check_user_lastseen',
            [
                messenger_api_response(TEST_UID1),
            ],
        )

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def build_issue_credentials_response(self):
        b = self.get_primary_builder()
        profile_response = b.get_profile_response()
        profile_response['email'] = TEST_EMAIL1
        response = b.build_auth_response(
            is_native=False,
            profile=profile_response,
        )
        response.pop('broker_consumer', None)
        response.pop('return_brief_profile', None)
        response.update(
            cookies=mock.ANY,
            default_uid=TEST_UID1,
        )
        return response

    def build_auth_not_allowed_response(self):
        b = self.get_primary_builder()
        profile_response = b.get_profile_response()
        profile_response['email'] = TEST_EMAIL1
        return b.build_auth_not_allowed_response(
            broker_consumer=None,
            is_native=False,
            profile=profile_response,
        )

    def setup_oauth(self):
        b = self.get_primary_builder()
        b.setup_yandex_auth_code_generation(TEST_YANDEX_AUTHORIZATION_CODE1)
        b.setup_yandex_token_generation()

    def assert_account_subscribed_to_service(self):
        self.env.db.check(
            'attributes',
            'subscription.%s' % Service.by_slug(self.track_service).sid,
            '1',
            uid=TEST_UID1,
            db='passportdbshard1',
        )

    def assert_ok_bind_social_profile_to_account_request(self, request):
        request.assert_url_starts_with('https://social/api/task/%s/bind?' % TEST_SOCIAL_TASK_ID1)
        request.assert_query_equals(
            dict(
                allow_auth='1',
                consumer='passport',
                uid=str(TEST_UID1),
            ),
        )

    def assert_ok_issue_credentials_event_log(self):
        e = EventCompositor(uid=str(TEST_UID1))

        e('action', 'subscribe')
        e('from', self.track_service)
        e('sid.add', str(Service.by_slug(self.track_service).sid))
        e('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged(e.to_lines())

    def assert_ok_issue_credentials_statbox_log(self):
        lines = list()

        def req(name):
            lines.append(self.env.statbox.entry(name))

        req('auth')
        req('cookie_set')
        req('subscriptions')

        self.env.statbox.assert_equals(lines)

    def test_ok_to_get_sessionid(self):
        self.setup_environment()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_issue_credentials_response())

    def test_account_strong_password_policy_is_enabled(self):
        self.is_account_strong_password_policy_enabled = True
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['account.strong_password_policy_enabled'],
            **self.build_auth_not_allowed_response()
        )

    def test_track_auth_allowed_but_user_policy_auth_forbidden(self):
        self.does_track_allow_authorization = True
        self.is_account_strong_password_policy_enabled = True
        self.track_service = 'music'
        self.setup_environment()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_issue_credentials_response())

        track = self.track_manager.read(TEST_TRACK_ID1)
        assert track.is_successful_completed

        assert len(self.env.social_api.requests) == 2
        self.assert_ok_bind_social_profile_to_account_request(self.env.social_api.requests[1])

        self.assert_account_subscribed_to_service()

        self.assert_ok_issue_credentials_statbox_log()
        self.assert_ok_issue_credentials_event_log()

    def test_antifraud_score_deny(self):
        self.does_antifraud_score_deny = True
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(rv, ['auth.not_allowed'], **self.build_auth_not_allowed_response())

    def test_challenge_required(self):
        self.setup_environment()
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(tags=['email_hint'])])

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            state='auth_challenge',
            **self.build_auth_not_allowed_response()
        )

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('ufo_profile_check_imply_challenge'),
                self.env.statbox.entry('user_notified_about_authentication'),
                self.env.statbox.entry('profile_threshold_exceeded'),
            ],
        )

        self.env.event_logger.assert_events_are_logged(list())

    def test_track_auth_allowed_but_antifraud_score_deny(self):
        self.does_antifraud_score_deny = True
        self.does_track_allow_authorization = True
        self.setup_environment()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_issue_credentials_response())

    def test_social_profile_not_exist_for_track_uid(self):
        self.track_uid = TEST_UID2
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(rv, ['auth.not_allowed'], **self.build_auth_not_allowed_response())

    def test_social_auth_not_allowed_for_track_uid(self):
        self.blackbox_uid = TEST_UID2
        self.does_track_allow_authorization = True

        social_profile1 = self.build_social_profile()
        social_profile1.update(allow_auth=False)
        social_profile2 = self.build_social_profile()
        social_profile2.update(uid=TEST_UID2)
        self.social_profiles = [social_profile1, social_profile2]

        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(rv, ['auth.not_allowed'], **self.build_auth_not_allowed_response())

    def test_no_social_profiles(self):
        self.does_track_allow_authorization = True
        self.social_profiles = list()
        self.setup_environment()

        rv = self.make_request()

        expected_response = self.build_auth_not_allowed_response()
        expected_response.update(has_enabled_accounts=False)

        self.assert_error_response(rv, ['auth.not_allowed'], **expected_response)

    def test_ok_to_get_token(self):
        self.track_social_output_mode = OUTPUT_MODE_XTOKEN
        self.setup_environment()

        rv = self.make_request()

        expected_response = self.build_issue_credentials_response()
        expected_response.pop('cookies', None)
        expected_response.pop('default_uid', None)
        expected_response.update(
            is_native=True,
            token=TEST_YANDEX_TOKEN1,
            token_expires_in=TEST_YANDEX_TOKEN_EXPIRES_IN1,
            x_token=TEST_YANDEX_TOKEN1,
        )
        self.assert_ok_response(rv, **expected_response)

    def test_ok_to_get_authorization_code(self):
        self.track_social_output_mode = OUTPUT_MODE_AUTHORIZATION_CODE
        self.setup_environment()

        rv = self.make_request()

        expected_response = self.build_issue_credentials_response()
        expected_response.pop('cookies', None)
        expected_response.pop('default_uid', None)
        expected_response.update(yandex_authorization_code=TEST_YANDEX_AUTHORIZATION_CODE1)
        self.assert_ok_response(rv, **expected_response)

    def test_not_social_auth_track(self):
        self.track_social_task_data = None
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            is_native=False,
            retpath=TEST_RETPATH1,
            track_id=self.track_id,
        )

    def test_no_retpath(self):
        self.track_retpath = None
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            is_native=False,
            track_id=self.track_id,
        )

    def test_account_not_found(self):
        self.blackbox_uid = None
        self.setup_environment()

        rv = self.make_request()

        expected_response = self.build_auth_not_allowed_response()
        expected_response.update(has_enabled_accounts=False)

        self.assert_error_response(rv, ['auth.not_allowed'], **expected_response)

    def test_account_disabled(self):
        self.is_account_disabled = True
        self.setup_environment()

        rv = self.make_request()

        expected_response = self.build_issue_credentials_response()
        expected_response.update(has_enabled_accounts=False)
        exclude_list = [
            'cookies',
            'default_uid',
            'profile_id',
            'state',
        ]
        for exclude_arg in exclude_list:
            expected_response.pop(exclude_arg, None)

        self.assert_error_response(rv, ['account.disabled'], **expected_response)
