# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.tests.views.bundle.auth.base_test_data import TEST_YANDEXUID_COOKIE
from passport.backend.api.views.bundle.auth.social.base import OUTPUT_MODE_SESSIONID
from passport.backend.api.views.bundle.mixins.challenge import DecisionSource
from passport.backend.core.builders.antifraud.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_oauth_tokens_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.captcha.faker import captcha_response_generate
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import messenger_api_response
from passport.backend.core.builders.oauth.faker.oauth import oauth_bundle_successful_response
from passport.backend.core.builders.social_api import (
    SocialApiRequestError,
    SocialApiTemporaryError,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    FACEBOOK_BUSINESS_ID,
    FACEBOOK_BUSINESS_TOKEN,
    get_bind_response,
    get_profiles_response,
    PROFILE_EMAIL,
    task_data_response,
)
from passport.backend.core.builders.ufo_api.faker.ufo_api import ufo_api_profile_item
from passport.backend.core.env_profile.profiles import UfoProfile
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_DEVICE_ID1,
    TEST_DEVICE_IFV1,
    TEST_DEVICE_NAME1,
    TEST_LOGIN1,
    TEST_PHONE_NUMBER1,
    TEST_PROFILE_BAD_ESTIMATE1,
    TEST_PROFILE_GOOD_ESTIMATE1,
    TEST_RETPATH1,
    TEST_SOCIAL_TASK_ID1,
    TEST_SOCIAL_TASK_ID2,
    TEST_TRACK_ID1,
    TEST_YANDEX_EMAIL1,
)
from passport.backend.core.test.test_utils.utils import (
    check_url_equals,
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.types.social_business_info import BusinessInfo
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .base import BaseTestCase
from .base_test_data import (
    EXISTING_TASK_ID,
    TEST_DISPLAY_NAME,
    TEST_HOST,
    TEST_LOGIN,
    TEST_PROVIDER,
    TEST_RETPATH,
    TEST_SOCIAL_OTHER_UID,
    TEST_SOCIAL_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_USER_IP,
    TEST_USER_LOGIN,
    TEST_USERID,
)


eq_ = iterdiff(eq_)


class BaseAuthSocialCallbackTestCase(
    EmailTestMixin,
    BaseTestCase,
):
    consumer = 'dev'
    default_url = '/1/bundle/auth/social/callback/'
    http_method = 'POST'
    http_query_args = {
        'status': 'ok',
        'task_id': EXISTING_TASK_ID,
        'track_id': TEST_TRACK_ID1,
    }
    http_headers = {
        'accept_language': 'ru',
        'cookie': TEST_USER_COOKIES,
        'host': TEST_HOST,
        'user_agent': TEST_USER_AGENT,
        'user_ip': TEST_USER_IP,
        'x_forwarded_for': True,
    }

    def setUp(self):
        super(BaseAuthSocialCallbackTestCase, self).setUp()

        self.builder = self.get_primary_builder()
        self.track_id = self.env.track_manager.create_test_track()

        with self.track_transaction() as track:
            track.retpath = TEST_RETPATH
            track.social_broker_consumer = TEST_CONSUMER1
            track.social_place = 'fragment'

        self.patch_fill_response_with_auth_data()
        self.setup_statbox_templates()

    def tearDown(self):
        self.unpatch_fill_response_with_auth_data()
        del self.track_id
        del self.builder
        super(BaseAuthSocialCallbackTestCase, self).tearDown()

    def patch_fill_response_with_auth_data(self):
        self.fill_response_with_auth_data_response = mock.Mock()
        self.patch_for_fill_response_with_auth_data = mock.patch(
            'passport.backend.api.views.bundle.auth.social.controllers.CallbackView.fill_response_with_auth_data',
            mock.Mock(side_effect=self.fill_response_with_auth_data_response),
        )
        self.patch_for_fill_response_with_auth_data.start()

    def unpatch_fill_response_with_auth_data(self):
        self.patch_for_fill_response_with_auth_data.stop()
        del self.patch_for_fill_response_with_auth_data
        del self.fill_response_with_auth_data_response

    def build_blackbox_response_with_social_accounts(
        self,
        profiles_data,
        **bb_kwargs
    ):
        blackbox_parameter_sets = []
        for profile in profiles_data['profiles']:
            if profile['allow_auth']:
                blackbox_parameter_sets.append(self.build_blackbox_kwargs_for_profile(profile, bb_kwargs))
        if blackbox_parameter_sets:
            return blackbox_userinfo_response_multiple(blackbox_parameter_sets)

    def build_blackbox_kwargs_for_profile(self, profile, bb_kwargs):
        bb_kwargs = bb_kwargs or dict()
        return deep_merge(
            dict(
                display_name=TEST_DISPLAY_NAME,
                emails=[
                    self.create_validated_external_email(TEST_USER_LOGIN, 'gmail.com'),
                ],
                login=TEST_LOGIN,
                uid=profile['uid'],
            ),
            build_phone_secured(1, TEST_PHONE_NUMBER1.e164),
            bb_kwargs,
        )

    def setup_track(self, **kwargs):
        defaults = dict(
            social_broker_consumer=TEST_CONSUMER1,
            social_task_id=None
        )
        for key in defaults:
            kwargs.setdefault(key, defaults[key])
        self.builder.setup_track(**kwargs)

    def assert_social_api_profiles_called(
        self,
        request,
        business_id=None,
        business_token=None,
    ):
        request.assert_url_starts_with('http://socialdev-2.yandex.ru/api/profiles?')
        query = dict(
            userid=TEST_USERID,
            provider=TEST_PROVIDER['code'],
            consumer='passport',
        )
        if business_id is not None:
            query.update(business_id=str(business_id))
        if business_token is not None:
            query.update(business_token=business_token)
        request.assert_query_equals(query)

    def build_callback_ok_response(self, expected=None):
        defaults = dict(
            broker_consumer=TEST_CONSUMER1,
            is_native=False,
            place='fragment',
        )
        expected = merge_dicts(defaults, expected) if expected else defaults
        return expected

    def build_auth_not_allowed_response(self, expected=None):
        profile_response = self.builder.get_profile_response()
        profile_response.update(
            business=dict(id=FACEBOOK_BUSINESS_ID, token=FACEBOOK_BUSINESS_TOKEN),
            email=PROFILE_EMAIL,
        )
        return self.builder.build_auth_not_allowed_response(
            **self.build_callback_ok_response(
                dict(
                    profile=profile_response,
                ),
            )
        )

    def build_register_callback_ok_response(self, expected=None):
        return self.builder.build_register_response(**self.build_callback_ok_response(expected))

    def build_suggest_callback_ok_response(self, expected=None):
        return self.builder.build_suggest_response(**self.build_callback_ok_response(expected))

    def assert_suggest_callback_ok_response(self, rv, expected=None):
        expected = self.build_suggest_callback_ok_response(expected)
        skip = ['auth_retpath'] if 'auth_retpath' in expected else None
        self.assert_ok_response(rv, skip=skip, **expected)

        if 'auth_retpath' in expected:
            rv = json.loads(rv.data)
            check_url_equals(rv['auth_retpath'], expected['auth_retpath'])

    def assert_ok_antifraud_score_request(self, request, expected_antifraud_score_params=None):
        if expected_antifraud_score_params is None:
            expected_antifraud_score_params = self.build_antifraud_score_params()

        ok_(request.post_args)
        request_data = json.loads(request.post_args)

        eq_(request_data, expected_antifraud_score_params.as_dict())

        request.assert_query_contains(dict(consumer='passport'))

    def build_antifraud_score_params(self):
        params = AntifraudScoreParams.build_social_auth()
        params.as_list_freq = {'AS2': 1}
        params.available_challenges = ['phone_hint', 'phone_confirmation', 'email_hint']
        params.device_id = TEST_DEVICE_ID1
        params.device_ifv = TEST_DEVICE_IFV1
        params.device_name = TEST_DEVICE_NAME1
        params.external_id = 'track-' + self.track_id
        params.ip = TEST_USER_IP
        params.is_mobile = True
        params.known_device = 'new'
        params.lah_uids = []
        params.profile_loaded = True
        params.social_provider_code = TEST_PROVIDER['code']
        params.social_userid = BusinessInfo(id=FACEBOOK_BUSINESS_ID, token=FACEBOOK_BUSINESS_TOKEN).to_userid()
        params.surface = 'social_callback'
        params.uid = TEST_SOCIAL_UID
        params.user_agent = TEST_USER_AGENT
        params.populate_from_headers(mock_headers(**self.http_headers))
        return params

    def assert_callback_error_response(self, response, error_codes, expected=None):
        defaults = dict(
            broker_consumer=TEST_CONSUMER1,
            is_native=False,
            place='fragment',
            retpath=TEST_RETPATH + '#status=error&request_id=request_id',
            track_id=TEST_TRACK_ID1,
        )
        expected = merge_dicts(defaults, expected) if expected else defaults
        self.assert_error_response(response, error_codes, **expected)

    def setup_blackbox_get_oauth_tokens(self):
        self.env.blackbox.set_response_value('get_oauth_tokens', blackbox_get_oauth_tokens_response([]))

    def setup_blackbox_userinfo(self):
        blackbox_response = self.build_blackbox_response_with_social_accounts(self.get_social_profiles())
        self.env.blackbox.set_response_side_effect('userinfo', [blackbox_response])

    def setup_blackbox(self):
        self.setup_blackbox_userinfo()
        self.setup_blackbox_get_oauth_tokens()

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

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


@with_settings_hosts(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    AUTH_ALLOWED_PROVIDERS=[TEST_PROVIDER['code']],
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=True,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
    YDB_PERCENTAGE=0,
)
class TestAuthSocialCallback(BaseAuthSocialCallbackTestCase):
    def setUp(self):
        super(TestAuthSocialCallback, self).setUp()

        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])
        self.setup_oauth_device_status_response()
        self.setup_kolmogor_responses()

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

    def test_callback__wrong_host_header__error(self):
        with self.track_transaction() as track:
            track.social_output_mode = OUTPUT_MODE_SESSIONID

        rv = self.make_request(headers=dict(host='google.com'))

        eq_(rv.status_code, 200)
        data = json.loads(rv.data)
        eq_(data['status'], 'error')
        eq_(data['errors'], ['host.invalid'])
        self.env.statbox.assert_has_written([])

    def check_single_case(self, profiles_count, state, with_business=False, post_params={}, **bb_kwargs):
        self.setup_track()
        self.setup_blackbox_get_oauth_tokens()

        self.builder.setup_task_for_task_id(
            dict(
                email=TEST_YANDEX_EMAIL1,
                with_business=with_business,
            ),
        )
        self.builder.setup_profile_creation()

        profiles_data = get_profiles_response()
        profiles_data = {'profiles': profiles_data['profiles'][:profiles_count]}
        self.env.social_api.set_response_value('get_profiles', profiles_data)

        blackbox_responses = list()

        response_with_social_accounts = self.build_blackbox_response_with_social_accounts(profiles_data, **bb_kwargs)
        if response_with_social_accounts is not None:
            blackbox_responses.append(response_with_social_accounts)

        suggested_account_by_email = blackbox_userinfo_response(uid=None)
        blackbox_responses.append(suggested_account_by_email)

        self.env.blackbox.set_response_side_effect('userinfo', blackbox_responses)

        rv = self.make_request(query_args=post_params)

        eq_(rv.status_code, 200)
        data = json.loads(rv.data)
        eq_(data['status'], 'ok')
        ok_('retpath' in data)
        if state == 'auth':
            ok_(self.fill_response_with_auth_data_response.called)
            expected_account = {
                'login': TEST_LOGIN,
                'is_pdd': False,
                'display_name': TEST_DISPLAY_NAME,
                'uid': TEST_SOCIAL_UID,
            }
            eq_(data['account'], expected_account, data['account'])
        else:
            eq_(data['state'], state, data)

        track = self.track_manager.read(TEST_TRACK_ID1)
        eq_(track.social_task_id, EXISTING_TASK_ID)
        ok_(track.social_task_data)

        if state == 'auth':
            ok_(track.is_successful_completed)
        else:
            ok_(not track.is_successful_completed)
            ok_(not track.uid)

        extra_kwargs = dict()
        if with_business:
            extra_kwargs.update(
                business_token=FACEBOOK_BUSINESS_TOKEN,
                business_id=str(FACEBOOK_BUSINESS_ID),
            )
        self.assert_social_api_profiles_called(request=self.env.social_api.requests[1], **extra_kwargs)

    def test_choose_ok(self):
        self.check_single_case(3, 'choose')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry(
                'callback_end',
                state='choose',
                enabled_accounts_count='2',
                disabled_accounts_count='0',
                accounts='%s,%s' % (TEST_SOCIAL_UID, TEST_SOCIAL_OTHER_UID),
            ),
        ])

    def test_auth_ok(self):
        self.check_single_case(2, 'auth')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry(
                'callback_end',
                state='auth',
                enabled_accounts_count='1',
                disabled_accounts_count='0',
                accounts=str(TEST_SOCIAL_UID),
            ),
            self.env.statbox.entry(
                'ufo_profile_checked',
                _exclude=[
                    'is_fresh_profile_passed',
                    'is_model_passed',
                    'tensornet_estimate',
                    'tensornet_model',
                    'tensornet_status',
                ],
                ufo_distance='0',
            ),
        ])

    def test_auth_with_suggest_ok(self):
        self.check_single_case(3, 'auth', post_params={'uid': '100000000'})
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry(
                'callback_end',
                state='auth',
                enabled_accounts_count='2',
                disabled_accounts_count='0',
                accounts='%s,%s' % (TEST_SOCIAL_UID, TEST_SOCIAL_OTHER_UID),
            ),
            self.env.statbox.entry(
                'ufo_profile_checked',
                _exclude=[
                    'is_fresh_profile_passed',
                    'is_model_passed',
                    'tensornet_estimate',
                    'tensornet_model',
                    'tensornet_status',
                ],
                ufo_distance='0',
            ),
        ])

    def test_auth_ok_with_business_info(self):
        self.check_single_case(1, 'auth', with_business=True)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry(
                'callback_end',
                state='auth',
                enabled_accounts_count='1',
                disabled_accounts_count='0',
                accounts=str(TEST_SOCIAL_UID),
            ),
            self.env.statbox.entry(
                'ufo_profile_checked',
                _exclude=[
                    'is_fresh_profile_passed',
                    'is_model_passed',
                    'tensornet_estimate',
                    'tensornet_model',
                    'tensornet_status',
                ],
                ufo_distance='0',
            ),
        ])

    def test_account_has_2fa_enabled__error(self):
        """Пользователь со включенной 2FA должен ввести одноразовый пароль"""
        task_data = task_data_response()
        profiles_data = get_profiles_response()

        with self.track_transaction() as track:
            track.is_successful_completed = False
            track.social_task_data = None
        new_profiles_data = {'profiles': profiles_data['profiles'][:1]}
        bind_api_response = get_bind_response()
        self.env.social_api.set_social_api_response_side_effect([task_data, new_profiles_data, bind_api_response])
        blackbox_response = self.build_blackbox_response_with_social_accounts(new_profiles_data, attributes={'account.2fa_on': '1'})
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.make_request()
        eq_(rv.status_code, 200)
        data = json.loads(rv.data)
        eq_(data['status'], 'error')
        eq_(data['errors'], ['account.2fa_enabled'])
        expected_account = {
            'person': {
                'firstname': u'\\u0414',
                'language': u'ru',
                'gender': 1,
                'birthday': u'1963-05-15',
                'lastname': u'\\u0424',
                'country': u'ru'
            },
            'login': TEST_LOGIN,
            'display_name': {
                'default_avatar': u'',
                'name': u'Firstname Lastname',
                'social': {
                    'profile_id': 123456,
                    'provider': u'gg',
                },
            },
            'uid': TEST_SOCIAL_UID,
            'display_login': TEST_LOGIN,
            'is_2fa_enabled': True,
            'is_rfc_2fa_enabled': False,
            'is_yandexoid': False,
            'is_workspace_user': False,
        }
        eq_(data['account'], expected_account)

        track = self.track_manager.read(TEST_TRACK_ID1)
        eq_(track.social_task_id, EXISTING_TASK_ID)
        ok_(track.social_task_data)
        # флажки успешного прохода не установлены
        ok_(not track.is_successful_completed)

    def test_account_strong_password_policy_enabled__error(self):
        """При включенной политике сложного пароля (67 сид), пользователю нужно отказать в авторизации"""
        task_data = task_data_response()
        profiles_data = get_profiles_response()

        with self.track_transaction() as track:
            track.is_successful_completed = False
            track.social_task_data = None
        new_profiles_data = {'profiles': profiles_data['profiles'][:1]}
        bind_api_response = get_bind_response()
        self.env.social_api.set_social_api_response_side_effect([task_data, new_profiles_data, bind_api_response])
        blackbox_response = self.build_blackbox_response_with_social_accounts(new_profiles_data, subscribed_to=[67])
        self.env.blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        rv = self.make_request()
        self.assert_error_response(rv, ['account.strong_password_policy_enabled'], check_content=False)

        track = self.track_manager.read(TEST_TRACK_ID1)
        eq_(track.social_task_id, EXISTING_TASK_ID)
        ok_(track.social_task_data)
        # флажки успешного прохода не установлены
        ok_(not track.is_successful_completed)

    def test_register_ok(self):
        self.check_single_case(0, 'register')
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
            self.env.statbox.entry(
                'callback_end',
                state='register',
                enabled_accounts_count='0',
                disabled_accounts_count='0',
            ),
        ])

    def test_recall(self):
        self.setup_track(social_task_id=EXISTING_TASK_ID)
        task = self.builder.build_task(email=None)
        self.builder.setup_task_for_track(task)

        self.builder.setup_social_profiles(list())

        rv = self.make_request()

        rv = json.loads(rv.data)
        eq_(rv.get('status'), 'ok')
        eq_(rv.get('state'), 'register')

        track = self.track_manager.read(TEST_TRACK_ID1)
        eq_(track.social_task_id, EXISTING_TASK_ID)
        eq_(track.social_task_data, task_data_response(**task))
        ok_(not track.is_successful_completed)

    def test_recall__different_task_id(self):
        self.setup_track(social_task_id=TEST_SOCIAL_TASK_ID1)
        self.builder.setup_task_for_track(self.builder.build_task(email=None))

        rv = self.make_request(query_args=dict(task_id=TEST_SOCIAL_TASK_ID2))

        self.assert_error_response(rv, ['track.invalid_state'], check_content=False)

    def test_recall__broker_failed(self):
        self.setup_track(social_task_id=EXISTING_TASK_ID)
        self.builder.setup_task_for_track(self.builder.build_task(email=None))

        rv = self.make_request(
            query_args=dict(code='error1', status='error'),
            exclude_args=['task_id'],
        )

        self.assert_error_response(rv, ['track.invalid_state'], check_content=False)

    def test_broker_error(self):
        rv = self.make_request(query_args=dict(status='error'))

        self.assert_callback_error_response(rv, ['broker.failed'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'callback_begin',
                broker_status='error',
            ),
        ])

    def test_broker_error__non_ascii_retpath(self):
        with self.track_transaction() as track:
            track.retpath = 'https://www.yandex.ru/%D0%BF/?h=%D0%BF'
            track.social_place = 'query'

        rv = self.make_request(query_args=dict(status='error'))

        self.assert_callback_error_response(
            rv,
            ['broker.failed'],
            dict(
                place='query',
                retpath='https://www.yandex.ru/%D0%BF/?h=%D0%BF&status=error&request_id=request_id',
            ),
        )

    def test_error_code__broker_error(self):
        rv = self.make_request(query_args=dict(code='error1', status='error'))
        self.assert_callback_error_response(
            rv,
            ['broker.failed'],
            dict(retpath=TEST_RETPATH + '#status=error&code=error1&request_id=request_id'),
        )

    def test_broker_error__place_query(self):
        with self.track_transaction() as track:
            track.social_place = 'query'
        rv = self.make_request(query_args=dict(status='error', code='error1'))
        self.assert_callback_error_response(
            rv,
            ['broker.failed'],
            dict(
                place='query',
                retpath=TEST_RETPATH + '?status=error&code=error1&request_id=request_id',
            ),
        )

    def test_social_api_failed_temporarily(self):
        with self.track_transaction() as track:
            track.social_task_data = None
        self.env.social_api.set_social_api_response_side_effect(SocialApiTemporaryError)
        rv = self.make_request()
        self.assert_error_response(rv, ['backend.social_api_failed'], check_content=False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
        ])

    def test_social_api_failed(self):
        with self.track_transaction() as track:
            track.social_task_data = None
        self.env.social_api.set_social_api_response_side_effect(SocialApiRequestError)
        rv = self.make_request()
        self.assert_error_response(rv, ['backend.social_api_permanent_error'], check_content=False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
        ])

    def test_invalid_provider(self):
        task_data = task_data_response()
        task_data['profile']['provider'] = {'code': 'ig', 'name': 'instagram', 'id': 9}
        self.env.social_api.set_social_api_response_value(task_data)
        rv = self.make_request()
        self.assert_error_response(rv, ['provider.invalid'], check_content=False)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('callback_begin'),
        ])

    def test_suggest_login_to_portal_account(self):
        self.setup_track()

        self.builder.setup_task_for_task_id(self.builder.build_task(email=TEST_YANDEX_EMAIL1))
        self.builder.setup_social_profiles(list())

        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple(
                    [
                        self.builder.build_yandex_full_account(),
                    ],
                ),
            ],
        )

        rv = self.make_request()

        profile_response = self.builder.get_profile_response()
        profile_response.update(email=TEST_YANDEX_EMAIL1)

        suggested_accounts_response = [
            self.builder.get_suggested_account_response(
                default_avatar='',
                default_email=None,
                display_login=TEST_LOGIN1,
            ),
        ]

        self.assert_suggest_callback_ok_response(
            rv,
            dict(
                auth_retpath=TEST_RETPATH1,
                auth_track_id=TEST_TRACK_ID1,
                can_register_social=True,
                profile=profile_response,
                register_social_track_id=TEST_TRACK_ID1,
                suggested_accounts=suggested_accounts_response,
            ),
        )

        track = self.track_manager.read(TEST_TRACK_ID1)
        eq_(track.social_task_id, EXISTING_TASK_ID)
        ok_(track.social_task_data)
        ok_(not track.is_successful_completed)


@with_settings_hosts(
    ALLOW_PROFILE_CHECK_FOR_MOBILE=True,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    AUTH_ALLOWED_PROVIDERS=[TEST_PROVIDER['code']],
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=True,
    EMAIL_CODE_CHALLENGE_ENABLED=False,
    SOCIAL_API_URL='http://socialdev-2.yandex.ru/api/',
    YDB_PERCENTAGE=0,
)
class TestChallengeAuthSocialCallback(BaseAuthSocialCallbackTestCase):
    def setup_statbox_templates(self):
        super(TestChallengeAuthSocialCallback, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'callback_end',
            _inherit_from=['callback_end'],
            state='auth',
            enabled_accounts_count='1',
            disabled_accounts_count='0',
            accounts=str(TEST_SOCIAL_UID),
        )
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            _exclude=[
                'is_model_passed',
                'tensornet_estimate',
                'tensornet_model',
                'tensornet_status',
            ],
            _inherit_from=['ufo_profile_checked'],
            af_action='DENY',
            af_is_auth_forbidden='1',
            challenge_reason='mobile_full_profile',
            current=self.make_user_profile(
                raw_env=dict(
                    device_id=TEST_DEVICE_ID1,
                    ip=TEST_USER_IP,
                    is_mobile=True,
                    user_agent_info=None,
                    yandexuid=TEST_YANDEXUID_COOKIE,
                ),
            ).as_json,
            decision_source=DecisionSource.ANTIFRAUD_API,
            device_id=TEST_DEVICE_ID1,
            full_profile_AS_list='AS2',
            is_full_profile_passed='0',
            is_mobile='1',
        )
        self.env.statbox.bind_entry(
            'user_notified_about_authentication',
            _inherit_from=['user_notified_about_authentication'],
            device_name=TEST_DEVICE_NAME1,
        )
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            _inherit_from=['profile_threshold_exceeded'],
            decision_source='antifraud_api',
            is_mobile='1',
            yandexuid=TEST_YANDEXUID_COOKIE,
        )

    def setup_web_track(self):
        with self.track_transaction() as track:
            track.is_successful_completed = False
            track.social_task_data = None

    def setup_mobile_track(self):
        self.setup_web_track()
        with self.track_transaction() as track:
            track.device_id = TEST_DEVICE_ID1
            track.device_ifv = TEST_DEVICE_IFV1
            track.device_name = TEST_DEVICE_NAME1

    def setup_social(self):
        self.env.social_api.set_response_side_effect(
            None,
            [
                task_data_response(with_business=True),
                self.get_social_profiles(),
                get_bind_response(),
            ],
        )

    def get_social_profiles(self):
        profiles_data = get_profiles_response()
        return {'profiles': profiles_data['profiles'][:1]}

    def setup_ufo(self, estimate=TEST_PROFILE_GOOD_ESTIMATE1):
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
            estimate=TEST_PROFILE_BAD_ESTIMATE1,
        )

    def setup_antifraud(self):
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])

    def setup_messenger(self):
        self.env.messenger_api.set_response_side_effect(
            'check_user_lastseen',
            [
                messenger_api_response(TEST_SOCIAL_UID),
            ],
        )

    def setup_captcha(self):
        self.env.captcha_mock.set_response_side_effect('generate', [captcha_response_generate(key='key')])

    def build_challenge_required_response(self):
        profile_response = self.builder.get_profile_response()
        profile_response.update(
            business=dict(id=FACEBOOK_BUSINESS_ID, token=FACEBOOK_BUSINESS_TOKEN),
            email=PROFILE_EMAIL,
        )
        return self.builder.build_ok_response(
            account=None,
            is_native=False,
            place='fragment',
            profile=profile_response,
            profile_id=None,
            return_brief_profile=None,
            state='auth_challenge',
        )

    def build_captcha_required_response(self):
        profile_response = self.builder.get_profile_response()
        profile_response.update(
            business=dict(id=FACEBOOK_BUSINESS_ID, token=FACEBOOK_BUSINESS_TOKEN),
            email=PROFILE_EMAIL,
        )
        return self.builder.build_ok_response(
            account=None,
            captcha_image_url='http://u.captcha.yandex.net/image?key=1p',
            is_native=False,
            place='fragment',
            profile=profile_response,
            profile_id=None,
            return_brief_profile=None,
        )

    def test_antifraud_score_deny(self):
        self.setup_mobile_track()
        self.setup_social()
        self.setup_blackbox()
        self.setup_oauth_device_status_response()
        self.setup_ufo()
        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])
        self.setup_messenger()
        self.setup_kolmogor_responses()

        rv = self.make_request()

        self.assert_error_response(rv, ['auth.not_allowed'], **self.build_auth_not_allowed_response())

        ok_(not self.fill_response_with_auth_data_response.called)

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_auth_challenge_shown)
        ok_(not track.uid)

        eq_(len(self.env.antifraud_api.requests), 1)
        self.assert_ok_antifraud_score_request(self.env.antifraud_api.requests[0])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('callback_begin'),
                self.env.statbox.entry('callback_end'),
                self.env.statbox.entry('ufo_profile_checked'),
                self.env.statbox.entry('user_notified_about_authentication'),
                self.env.statbox.entry('profile_threshold_exceeded'),
            ],
        )

    def test_challenge_required(self):
        self.setup_mobile_track()
        self.setup_social()
        self.setup_blackbox()
        self.setup_oauth_device_status_response()
        self.setup_ufo(estimate=TEST_PROFILE_BAD_ESTIMATE1)
        self.setup_antifraud()
        self.setup_messenger()
        self.setup_kolmogor_responses()

        rv = self.make_request()

        self.assert_ok_response(rv, **self.build_challenge_required_response())

        ok_(not self.fill_response_with_auth_data_response.called)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_auth_challenge_shown)
        eq_(track.uid, str(TEST_SOCIAL_UID))

        eq_(len(self.env.antifraud_api.requests), 1)
        self.assert_ok_antifraud_score_request(self.env.antifraud_api.requests[0])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('callback_begin'),
                self.env.statbox.entry('callback_end'),
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    _exclude=['challenge_reason'],
                    af_action='ALLOW',
                    af_is_auth_forbidden='0',
                    decision_source='mobile_full_profile',
                    is_challenge_required='1',
                ),
                self.env.statbox.entry('user_notified_about_authentication'),
                self.env.statbox.entry(
                    'profile_threshold_exceeded',
                    decision_source='mobile_full_profile',
                ),
            ],
        )

    def test_nothing_to_use_as_challenge(self):
        self.setup_mobile_track()
        self.setup_social()
        self.setup_blackbox_get_oauth_tokens()

        social_profile = self.get_social_profiles()['profiles'][0]
        blackbox_kwargs = self.build_blackbox_kwargs_for_profile(social_profile, dict())
        blackbox_kwargs.update(emails=None, phones=None)
        blackbox_response = blackbox_userinfo_response_multiple([blackbox_kwargs])
        self.env.blackbox.set_response_side_effect('userinfo', [blackbox_response])

        self.setup_oauth_device_status_response()
        self.setup_ufo(estimate=TEST_PROFILE_BAD_ESTIMATE1)
        self.setup_antifraud()
        self.setup_messenger()
        self.setup_captcha()
        self.setup_kolmogor_responses()

        rv = self.make_request()

        self.assert_ok_response(rv, check_all=False, state='auth')

        ok_(self.fill_response_with_auth_data_response.called)

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_auth_challenge_shown)

    def test_web(self):
        self.setup_web_track()
        self.setup_social()
        self.setup_blackbox()
        self.setup_ufo()

        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response(action=ScoreAction.DENY)])

        self.setup_messenger()
        self.setup_kolmogor_responses()

        rv = self.make_request()

        self.assert_error_response(rv, ['auth.not_allowed'], **self.build_auth_not_allowed_response())

        ok_(not self.fill_response_with_auth_data_response.called)

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_auth_challenge_shown)
        ok_(not track.uid)

        eq_(len(self.env.antifraud_api.requests), 1)
        score_params = self.build_antifraud_score_params()
        score_params.device_id = None
        score_params.device_ifv = None
        score_params.device_name = None
        score_params.is_mobile = None
        score_params.known_device = None
        self.assert_ok_antifraud_score_request(self.env.antifraud_api.requests[0], score_params)

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('callback_begin'),
                self.env.statbox.entry('callback_end'),
                self.env.statbox.entry(
                    'ufo_profile_checked',
                    _exclude=[
                        'challenge_reason',
                        'device_id',
                        'full_profile_AS_list',
                        'is_full_profile_passed',
                        'is_fresh_profile_passed',
                        'is_model_passed',
                        'tensornet_estimate',
                        'tensornet_model',
                        'tensornet_status',
                    ],
                    current=self.make_user_profile(
                        raw_env=dict(
                            ip=TEST_USER_IP,
                            user_agent_info=None,
                            yandexuid=TEST_YANDEXUID_COOKIE,
                        ),
                    ).as_json,
                    is_mobile='0',
                    ufo_distance='0',
                ),
                self.env.statbox.entry(
                    'user_notified_about_authentication',
                    _exclude=['device_name'],
                ),
                self.env.statbox.entry(
                    'profile_threshold_exceeded',
                    is_mobile='0',
                ),
            ],
        )
