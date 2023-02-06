# -*- coding: utf-8 -*-

from datetime import datetime
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.views.bundle.auth.social.base import OUTPUT_MODE_SESSIONID
from passport.backend.core import Undefined
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_oauth_tokens_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    get_bind_response,
    get_profiles_response,
    PROFILE_EMAIL,
)
from passport.backend.core.builders.ufo_api.faker.ufo_api import ufo_api_profile_item
from passport.backend.core.env_profile.profiles import UfoProfile
from passport.backend.core.test.consts import TEST_TRACK_ID1
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.types.account.account import (
    ACCOUNT_TYPE_NORMAL,
    ACCOUNT_TYPE_SOCIAL,
)
from passport.backend.utils.common import merge_dicts

from .base import BaseTestCase
from .base_test_data import (
    EXISTING_TASK_ID,
    TEST_CONSUMER1,
    TEST_DISPLAY_NAME,
    TEST_HOST,
    TEST_PROFILE_ID,
    TEST_PROVIDER,
    TEST_RETPATH,
    TEST_SOCIAL_UID,
    TEST_SOCIAL_USERID,
    TEST_UID1,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_USER_IP,
)


eq_ = iterdiff(eq_)


TEST_DEFAULT_GLOGOUT = datetime.fromtimestamp(1)


@with_settings_hosts(
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    AUTH_ALLOWED_PROVIDERS=[TEST_PROVIDER['code']],
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    CHALLENGE_ON_SOCIAL_AUTH_ENABLED=True,
    YDB_PERCENTAGE=0,
)
class TestAuthSocialChoose(BaseTestCase):
    consumer = 'dev'
    default_url = '/1/bundle/auth/social/choose/'
    http_method = 'POST'
    http_query_args = {
        'track_id': TEST_TRACK_ID1,
        'uid': TEST_UID1,
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
        super(TestAuthSocialChoose, self).setUp()

        self.builder = self.get_primary_builder()

        self.track_id = self.env.track_manager.create_test_track(track_type='authorize')
        with self.track_transaction() as track:
            track.social_broker_consumer = TEST_CONSUMER1
            track.social_task_data = {'provider': TEST_PROVIDER}
            track.social_task_id = EXISTING_TASK_ID
            track.retpath = TEST_RETPATH
            track.social_output_mode = OUTPUT_MODE_SESSIONID

        self.setup_statbox_templates()
        self.patch_build_auth_cookies_and_session()

        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])
        self.setup_push_send_response()
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

    def tearDown(self):
        self.unpatch_build_auth_cookies_and_session()
        del self.track_id
        del self.builder
        super(TestAuthSocialChoose, self).tearDown()

    def blackbox_userinfo_kwargs(
        self,
        uid,
        account_enabled=True,
        alias_type='portal',
        display_name=None,
        has_2fa=None,
        is_betatester=False,
        is_strong_password_policy=False,
        is_yandexoid=False,
        login='userlogin',
        sms_2fa_on=None,
    ):
        aliases = {
            alias_type: login,
        }
        if is_yandexoid:
            aliases['yandexoid'] = 'yastaff_login'

        display_name = display_name or TEST_DISPLAY_NAME
        subscribed_to = [67] if is_strong_password_policy else None

        dbfields = {}
        if is_betatester:
            dbfields['subscription.suid.668'] = '1'
            dbfields['subscription.login.668'] = 'betatester_login'

        attributes = {}
        if has_2fa:
            attributes['account.2fa_on'] = '1'
        if sms_2fa_on:
            attributes['account.sms_2fa_on'] = '1'

        return dict(
            aliases=aliases,
            attributes=attributes,
            dbfields=dbfields,
            display_name=display_name,
            enabled=account_enabled,
            login=login,
            subscribed_to=subscribed_to,
            uid=uid,
        )

    def setup_push_send_response(self):
        self.env.push_api.set_response_side_effect('send', ['OK'])

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def _check(
        self,
        api_response_item,
        account_enabled,
        status,
        errors=None,
        bb_response_no_uid=False,
        is_yandexoid=False,
        is_betatester=False,
        has_2fa=None,
        login='userlogin',
        alias_type='portal',
        expected_account_type=ACCOUNT_TYPE_NORMAL,
        is_strong_password_policy=False,
        headers=None,
        need_extra_sessguard=True,
        task=Undefined,
        sms_2fa_on=None,
    ):
        self.build_auth_cookies_and_session_response.return_value = (
            {'cookies': {}},
            {'session': {'value': 'sess'}},
            None,
        )

        if task is Undefined:
            task = dict(userid=TEST_SOCIAL_USERID)
        if task is not None:
            self.builder.setup_task_for_track(task)
        else:
            with self.track_transaction() as track:
                track.social_task_data = None

        if api_response_item is not None:
            api_response = {'profiles': [get_profiles_response()['profiles'][api_response_item]]}
            uid = api_response['profiles'][0]['uid']
            bb_uid = None if bb_response_no_uid else uid
            blackbox_response = blackbox_userinfo_response(
                **self.blackbox_userinfo_kwargs(
                    account_enabled=account_enabled,
                    alias_type=alias_type,
                    has_2fa=has_2fa,
                    is_betatester=is_betatester,
                    is_strong_password_policy=is_strong_password_policy,
                    is_yandexoid=is_yandexoid,
                    login=login,
                    sms_2fa_on=sms_2fa_on,
                    uid=bb_uid,
                )
            )
            self.env.blackbox.set_response_side_effect('userinfo', [blackbox_response])
        else:
            api_response = {'profiles': []}
            uid = TEST_SOCIAL_UID

        bind_api_response = get_bind_response()
        self.env.social_api.set_social_api_response_side_effect([api_response, bind_api_response])
        self.env.blackbox.set_response_value('get_oauth_tokens', blackbox_get_oauth_tokens_response([]))

        rv = self.make_request(
            query_args={
                'uid': uid,
                'track_id': self.track_id,
            },
            headers=headers,
        )

        data = json.loads(rv.data)
        eq_(rv.status_code, 200)
        if status == 'ok':
            eq_(data['status'], 'ok')
            expected_account = {
                'login': login,
                'is_pdd': False,
                'display_name': TEST_DISPLAY_NAME,
                'uid': TEST_SOCIAL_UID,
            }
            eq_(
                data['account'],
                expected_account,
            )

            eq_(self.build_auth_cookies_and_session_response.call_count, 1)

            call_args = self.build_auth_cookies_and_session_response.call_args[-1]

            display_name = call_args['display_name']
            ok_(display_name.is_social)
            eq_(display_name.as_dict(), TEST_DISPLAY_NAME)

            expected_args = {
                'account_type': expected_account_type,
                'social_id': TEST_PROFILE_ID,
                'is_yandexoid': is_yandexoid,
                'is_betatester': is_betatester,
                # TODO 'is_workspace_user': False,
                'multi_session_users': {},
                'extend_session': False,
                'display_name': display_name,
                'logout_datetime': TEST_DEFAULT_GLOGOUT,
                'need_extra_sessguard': need_extra_sessguard,
                'is_child': Undefined,
            }

            eq_(call_args, expected_args)

        else:
            data = json.loads(rv.data)
            eq_(data['status'], 'error')
            eq_(data['errors'], errors, data)

            if has_2fa:
                expected_account = {
                    'uid': uid,
                    'login': login,
                    'display_login': login,
                    'display_name': {
                        'default_avatar': '',
                        'name': 'Firstname Lastname',
                        'social': {
                            'profile_id': 123456,
                            'provider': 'gg',
                        },
                    },
                    'person': {
                        'firstname': u'\\u0414',
                        'language': u'ru',
                        'gender': 1,
                        'birthday': u'1963-05-15',
                        'lastname': u'\\u0424',
                        'country': u'ru'
                    },
                    'is_2fa_enabled': True,
                    'is_rfc_2fa_enabled': False,
                    'is_yandexoid': False,
                    'is_workspace_user': False,
                }
                eq_(data['account'], expected_account)

    def build_auth_not_allowed_response(self, expected=None):
        profile_response = self.builder.get_profile_response()
        profile_response.update(
            email=PROFILE_EMAIL,
            userid=100000000,
        )
        defaults = dict(
            broker_consumer=TEST_CONSUMER1,
            is_native=False,
            profile=profile_response,
        )
        expected = merge_dicts(defaults, expected) if expected else defaults
        return self.builder.build_auth_not_allowed_response(**expected)

    def assert_ok_antifraud_score_request(self, request):
        ok_(request.post_args)
        request_data = json.loads(request.post_args)

        params = AntifraudScoreParams.build_social_auth()
        params.external_id = 'track-' + self.track_id
        params.ip = TEST_USER_IP
        params.social_provider_code = TEST_PROVIDER['code']
        params.social_userid = str(TEST_SOCIAL_USERID)
        params.uid = TEST_SOCIAL_UID
        params.user_agent = TEST_USER_AGENT
        params.is_mobile = False
        params.lah_uids = []
        params.surface = 'social_choose'
        eq_(request_data, params.as_dict())

        request.assert_query_contains(dict(consumer='passport'))

    def test_choose__wrong_host_header__error(self):
        self._check(
            api_response_item=0,
            account_enabled=True,
            status='error',
            errors=['host.invalid'],
            headers=dict(host='google.com'),
        )

        self.env.statbox.assert_has_written([])

    def test_ok(self):
        self._check(0, True, 'ok')
        self.env.statbox.assert_has_written([
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
            self.env.statbox.entry('auth', ip=TEST_USER_IP, userid=str(TEST_SOCIAL_USERID), login='userlogin'),
        ])

    def test_ok_with_subscriptions(self):
        self._check(0, True, 'ok', is_betatester=True, is_yandexoid=True)
        self.env.statbox.assert_has_written([
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
            self.env.statbox.entry('auth', ip=TEST_USER_IP, userid=str(TEST_SOCIAL_USERID), login='userlogin'),
        ])

    def test_correct_account_type(self):
        self._check(0, True, 'ok', login='uid-abc', alias_type='social', expected_account_type=ACCOUNT_TYPE_SOCIAL)
        self.env.statbox.assert_has_written([
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
            self.env.statbox.entry(
                'auth',
                ip=TEST_USER_IP,
                userid=str(TEST_SOCIAL_USERID),
                login='uid-abc',
            ),
        ])

    def test_invalid_uid_no_profile(self):
        """Social-api вернул пустой список профилей"""
        self._check(
            api_response_item=None,
            account_enabled=True,
            status='error', errors=['uid.rejected'],
        )
        self.env.statbox.assert_has_written([])

    def test_2fa_enabled__error(self):
        """При включенной 2ФА, пользователя нужно попросить ввести otp"""
        self._check(
            api_response_item=0,
            account_enabled=True,
            status='error',
            errors=['account.2fa_enabled'],
            has_2fa=True,
        )
        self.env.statbox.assert_has_written([])

    def test_strong_password_policy__error(self):
        """При включенной политике сложного пароля (67 сид), пользователю нужно отказать в авторизации"""
        self._check(
            api_response_item=0,
            account_enabled=True,
            status='error',
            errors=['account.strong_password_policy_enabled'],
            is_strong_password_policy=True,
        )
        self.env.statbox.assert_has_written([])

    def test_already_registered(self):
        """Трек с состоянием is_successful_completed=True"""
        with self.track_transaction() as track:
            track.is_successful_completed = True

        self._check(0, True, 'ok')

        self.env.statbox.assert_has_written([
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
            self.env.statbox.entry('auth', ip=TEST_USER_IP, userid=str(TEST_SOCIAL_USERID), login='userlogin'),
        ])

    def test_track_without_social_profile(self):
        """Трек без соц. профиля"""
        self._check(
            api_response_item=None,
            account_enabled=True,
            status='error',
            errors=['track.invalid_state'],
            task=None,
        )
        self.env.statbox.assert_has_written([])
