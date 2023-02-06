# -*- coding: utf-8 -*-
import json
from time import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    COOKIE_YP_VALUE,
    COOKIE_YS_VALUE,
    TEST_CLEANED_PDD_RETPATH,
    TEST_COOKIE_L,
    TEST_COOKIE_MY,
    TEST_CSRF_TOKEN,
    TEST_CYRILLIC_DOMAIN_IDNA,
    TEST_CYRILLIC_LOGIN,
    TEST_DOMAIN,
    TEST_ENCODED_ENV_FOR_PROFILE,
    TEST_FAKE_PHONE_NUMBER,
    TEST_FAKE_PHONE_NUMBER_DUMPED,
    TEST_FEDERAL_ALIAS,
    TEST_FEDERAL_DOMAIN,
    TEST_FEDERAL_DOMAIN_ID,
    TEST_FEDERAL_LOGIN,
    TEST_FRETPATH,
    TEST_LITE_LOGIN,
    TEST_LOCAL_PHONE_NUMBER,
    TEST_LOCAL_PHONE_NUMBER_DUMPED,
    TEST_LOGIN,
    TEST_NEOPHONISH_LOGIN1,
    TEST_ORIGIN,
    TEST_PDD_CYRILLIC_LOGIN,
    TEST_PDD_LOGIN,
    TEST_PDD_RETPATH,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED_MASKED,
    TEST_RETPATH,
    TEST_SERVICE,
    TEST_TRACK_ID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
)
from passport.backend.core.builders.blackbox.exceptions import BlackboxInvalidParamsError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.federal_configs_api.faker import federal_config_ok
from passport.backend.core.builders.social_api import SocialApiTemporaryError
from passport.backend.core.builders.social_api.faker.social_api import (
    get_profiles_response,
    profile_item,
    task_data_response,
)
from passport.backend.core.cookies.cookie_lah import AuthHistoryContainer
from passport.backend.core.counters import (
    magic_link_per_ip_counter,
    magic_link_per_uid_counter,
)
from passport.backend.core.models.account import (
    ACCOUNT_DISABLED,
    ACCOUNT_DISABLED_ON_DELETION,
)
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.core.serializers.eav.base import EavSerializer
from passport.backend.core.test.consts import (
    TEST_CONFIRMATION_CODE1,
    TEST_CONSUMER1,
    TEST_PASSWORD_HASH1,
    TEST_SCHOLAR_LOGIN1,
    TEST_SOCIAL_TASK_ID1,
    TEST_TRACK_ID2,
    TEST_UNIXTIME1,
    TEST_UNIXTIME2,
)
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import (
    AnyMatcher,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import deep_merge
from passport.backend.utils.string import smart_text

from .base import BaseMultiStepTestcase
from .base_test_data import (
    TEST_DEVICE_ID,
    TEST_INVALID_LOGIN,
    TEST_RUSSIAN_IP,
    TEST_RUSSIAN_REGION_ID,
    TEST_UUID,
)


TEST_2FA_PICTURES_TTL = 60
TEST_MAGIC_LINK_PER_UID_LIMIT = 10
PHONISH_LOGIN = 'phne-123'

TEST_CLIENT_ID = 'clid'
TEST_DEVICE_NAME = 'device-name'
TEST_ORIGIN_WITHOUT_LITE_REG = 'origin_wo_lite_reg'

YAKEY_2FA_PICTURES_SHOWN_COUNTER = '2fa_pictures:shown:uid:%s'
YAKEY_2FA_PICTURES_DENY_FLAG_COUNTER = '2fa_pictures:deny:uid:%s'


@with_settings_hosts(
    ALLOW_REGISTRATION=True,
    ALLOW_LITE_REGISTRATION=True,
    ALLOW_NEOPHONISH_REGISTRATION=True,
    NATIVE_EMAIL_DOMAINS=['yandex.ru'],
    IS_INTRANET=False,
    ALLOW_MAGIC_LINK_FOR_LITE=True,
    AUTH_BY_SMS__ALLOW_SKIP_SIB_CHECKS=False,
    FORBID_AUTH_BY_SMS_FOR_SMS_2FA=True,
    DONT_PROMOTE_LITE_REGISTRATION_IN_WEB_FOR_ORIGINS=[TEST_ORIGIN_WITHOUT_LITE_REG],
    SOCIAL_API_RETRIES=2,
    USE_NEW_SUGGEST_BY_PHONE=False,
    YAKEY_2FA_PICTURES_TTL=TEST_2FA_PICTURES_TTL,
    **mock_counters(
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UID_COUNTER=(1, 600, TEST_MAGIC_LINK_PER_UID_LIMIT),
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_IP_COUNTER=(1, 600, 10),
        AUTH_MAGIC_LINK_EMAIL_SENT_PER_UNTRUSTED_IP_COUNTER=(1, 600, 3),
        YAKEY_2FA_PICTURES_SHOWN_COUNTER=5,
    )
)
class StartTestcase(BaseMultiStepTestcase):
    default_url = '/1/bundle/auth/password/multi_step/start/'
    http_query_args = {
        'retpath': TEST_RETPATH,
        'service': TEST_SERVICE,
        'origin': TEST_ORIGIN,
        'fretpath': TEST_FRETPATH,
        'clean': 'yes',
        'login': TEST_LOGIN,
        'process_uuid': TEST_UUID,
    }
    statbox_type = 'multi_step_start'

    def setUp(self):
        super(StartTestcase, self).setUp()

        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([]),
        )
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok())

        self.setup_kolmogor()

    def setup_kolmogor(self, denied=0, shown=0):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                '%s,%s' % (denied, shown),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def setup_blackbox_responses(self, login_available=False, pdd_domain_exists=True, **kwargs):
        super(StartTestcase, self).setup_blackbox_responses(**kwargs)
        login_status = 'free' if login_available else 'occupied'
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({
                TEST_LOGIN: login_status,
                TEST_LITE_LOGIN: login_status,
                TEST_FEDERAL_LOGIN: login_status,
            }),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1 if pdd_domain_exists else 0,
                domain=TEST_DOMAIN,
            ),
        )

    def assert_track_ok(
        self,
        track_type='authorize',
        retpath=TEST_RETPATH,
        auth_methods=None,
        with_magic=True,
        with_2fa_pictures=False,
        with_social_suggest_data=False,
        with_confirmed_phone=False,
        with_mobile_params=False,
        user_entered_login=TEST_LOGIN,
        allow_scholar=False,
    ):
        if auth_methods is None:
            auth_methods = ['password', 'magic_x_token']

        track = self.track_manager.read(TEST_TRACK_ID)

        eq_(track.origin, TEST_ORIGIN)
        eq_(track.retpath, retpath)
        eq_(track.service, TEST_SERVICE)
        eq_(track.track_type, track_type)
        if track_type == 'authorize':
            eq_(track.allow_scholar, allow_scholar)
            eq_(track.allowed_auth_methods, auth_methods)
            eq_(track.clean, 'yes')
            eq_(track.fretpath, TEST_FRETPATH)
            eq_(track.surface, 'web_password')
            eq_(track.user_entered_login, user_entered_login)
            if with_magic:
                eq_(track.uid, str(TEST_UID))
                ok_(track.is_allow_otp_magic)
                eq_(track.csrf_token, TEST_CSRF_TOKEN)
                eq_(track.browser_id, TEST_ENCODED_ENV_FOR_PROFILE['user_agent_info']['BrowserName'])
                eq_(track.os_family_id, TEST_ENCODED_ENV_FOR_PROFILE['user_agent_info']['OSFamily'])
                eq_(track.region_id, TEST_RUSSIAN_REGION_ID)
                if with_2fa_pictures:
                    ok_(track.correct_2fa_picture is not None)
                    eq_(track.correct_2fa_picture_expires_at, TimeNow(offset=TEST_2FA_PICTURES_TTL))
            if with_social_suggest_data:
                eq_(track.social_task_data, task_data_response())
                eq_(track.social_task_id, TEST_SOCIAL_TASK_ID1)
                eq_(track.social_track_id, TEST_TRACK_ID2)
            if with_confirmed_phone:
                eq_(track.phone_confirmation_code, TEST_CONFIRMATION_CODE1)
                eq_(track.phone_confirmation_first_checked, str(TEST_UNIXTIME1))
                eq_(track.phone_confirmation_first_send_at, str(TEST_UNIXTIME1))
                eq_(track.phone_confirmation_is_confirmed, True)
                eq_(track.phone_confirmation_last_checked, str(TEST_UNIXTIME2))
                eq_(track.phone_confirmation_last_send_at, str(TEST_UNIXTIME2))
                eq_(track.phone_confirmation_method, 'by_sms')
                eq_(track.phone_confirmation_phone_number, TEST_PHONE_NUMBER.e164)
                eq_(track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.e164)

        if with_mobile_params:
            eq_(track.client_id, TEST_CLIENT_ID)
            eq_(track.device_id, TEST_DEVICE_ID)
            eq_(track.device_name, TEST_DEVICE_NAME)

    def assert_statbox_ok(self, register=False, retpath=TEST_RETPATH, cleaned_retpath=TEST_RETPATH, **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted', process_uuid=TEST_UUID, retpath=retpath, **kwargs),
            self.env.statbox.entry(
                'decision_reached',
                process_uuid=TEST_UUID,
                track_type='register' if register else 'authorize',
                retpath=cleaned_retpath or retpath,
            ),
        ])

    def check_blackbox_calls(self, login=TEST_LOGIN, call_count=1, second_method='loginoccupation'):
        eq_(len(self.env.blackbox.requests), call_count)
        if call_count >= 1:
            self.env.blackbox.requests[0].assert_post_data_contains({
                'method': 'userinfo',
                'login': login,
                'find_by_phone_alias': 'force_on',
                'country': 'RU',
            })
        if call_count >= 2:
            self.env.blackbox.requests[1].assert_query_contains({
                'method': second_method,
            })

    def default_response_values(self, **kwargs):
        rv = dict(
            super(StartTestcase, self).default_response_values(),
            primary_alias_type=1,
            can_authorize=True,
            auth_methods=['password', 'magic_x_token'],
            csrf_token=TEST_CSRF_TOKEN,
            preferred_auth_method='password',
            use_new_suggest_by_phone=False,
        )
        rv.update(kwargs)
        return rv

    def setup_social_suggest_track(self):
        track = self.track_manager.create(
            track_type='authorize',
            consumer=TEST_CONSUMER1,
            track_id=TEST_TRACK_ID2,
        )
        with self.track_manager.transaction(track=track).rollback_on_error():
            track.social_task_data = task_data_response()
            track.social_task_id = TEST_SOCIAL_TASK_ID1

    def setup_old_track_with_confirmed_phone(self):
        track = self.track_manager.create(
            track_type='authorize',
            consumer=TEST_CONSUMER1,
            track_id=TEST_TRACK_ID2,
        )
        with self.track_manager.transaction(track=track).rollback_on_error():
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE1
            track.phone_confirmation_first_checked = TEST_UNIXTIME1
            track.phone_confirmation_first_send_at = TEST_UNIXTIME1
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_last_checked = TEST_UNIXTIME2
            track.phone_confirmation_last_send_at = TEST_UNIXTIME2
            track.phone_confirmation_method = 'by_sms'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.e164

    def test_invalid_host_error(self):
        resp = self.make_request(
            headers=dict(host='google.com'),
        )
        self.assert_error_response(resp, ['host.invalid'])
        self.check_blackbox_calls(call_count=0)

    def test_pdd_unknown_domain(self):
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        resp = self.make_request(query_args={'login': TEST_PDD_LOGIN, 'is_pdd': 'yes'})
        self.assert_error_response(resp, ['domain.not_hosted'])

    def test_can_authorize_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_can_authorize_by_magic_ok(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
            )
        )
        self.assert_track_ok(
            auth_methods=['magic', 'otp'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_can_authorize_with_social_profiles_ok(self):
        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([
                profile_item(uid=TEST_UID),
            ]),
        )

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_x_token', 'social_fb'],
                preferred_auth_method='password',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_x_token', 'social_fb'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_social_api_failed_ok(self):
        self.env.social_api.set_response_side_effect('get_profiles', SocialApiTemporaryError)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_x_token'],
                preferred_auth_method='password',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()
        eq_(len(self.env.social_api.requests), 2)

    def test_no_auth_methods(self):
        kwargs = deep_merge(
            dict(
                login=PHONISH_LOGIN,
                aliases={u'phonish': PHONISH_LOGIN},
            ),
            build_phone_bound(1, TEST_PHONE_NUMBER.e164),
        )
        self.setup_blackbox_responses(
            has_password=False,
            has_2fa=False,
            attributes={
                'account.qr_code_login_forbidden': 1,
            },
            **kwargs
        )
        resp = self.make_request(query_args={'login': PHONISH_LOGIN})
        self.assert_error_response(resp, ['action.impossible'], primary_alias_type=10, track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)
        self.check_blackbox_calls(login=PHONISH_LOGIN)

    def test_account_disabled(self):
        self.setup_blackbox_responses(user_disabled_status=ACCOUNT_DISABLED)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)
        self.check_blackbox_calls()

    def test_account_disabled_on_deletion(self):
        self.setup_blackbox_responses(user_disabled_status=ACCOUNT_DISABLED_ON_DELETION)
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'], can_be_restored=False, track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)
        self.check_blackbox_calls()

    def test_account_disabled_on_deletion_but_can_be_restored(self):
        self.setup_blackbox_responses(
            user_disabled_status=ACCOUNT_DISABLED_ON_DELETION,
            account_deletion_operation_started_at=time() - 60,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'], can_be_restored=True, track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)
        self.check_blackbox_calls()

    def test_can_register_portal_by_login_ok(self):
        self.setup_blackbox_responses(user_exists=False, login_available=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal'],
            login=TEST_LOGIN,
            phone_number=None,
            country='us',
            use_new_suggest_by_phone=False,
        )
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(register=True)
        self.check_blackbox_calls(call_count=2)

    def test_can_register_portal_by_login_with_native_domain_ok(self):
        login_with_native_domain = '%s@yandex.ru' % TEST_LOGIN
        self.setup_blackbox_responses(user_exists=False, login_available=True)
        resp = self.make_request(query_args={'login': login_with_native_domain})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal'],
            login=TEST_LOGIN,
            phone_number=None,
            country='us',
            looks_like_yandex_email=True,
            use_new_suggest_by_phone=False,
        )
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(register=True, input_login=login_with_native_domain)
        self.check_blackbox_calls(login=login_with_native_domain, call_count=4, second_method='hosted_domains')

    def test_can_register_portal_by_login_with_native_domain_and_spaces_ok(self):
        login_with_native_domain_and_spaces = ' %s @ yandex.ru ' % TEST_LOGIN
        self.setup_blackbox_responses(user_exists=False, login_available=True)
        resp = self.make_request(query_args={'login': login_with_native_domain_and_spaces})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal'],
            login=TEST_LOGIN,
            phone_number=None,
            country='us',
            looks_like_yandex_email=True,
            use_new_suggest_by_phone=False,
        )
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(register=True, input_login=login_with_native_domain_and_spaces.strip())
        self.check_blackbox_calls(login=login_with_native_domain_and_spaces.strip(), call_count=4, second_method='hosted_domains')

    def test_can_register_lite_by_login_ok(self):
        self.setup_blackbox_responses(user_exists=False, login_available=True, pdd_domain_exists=False)
        resp = self.make_request(query_args={'login': TEST_LITE_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_register=True,
            account_type='lite',
            allowed_account_types=['lite'],
            login=TEST_LITE_LOGIN,
            phone_number=None,
            country='us',
            use_new_suggest_by_phone=False,
        )
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(register=True, input_login=TEST_LITE_LOGIN)
        self.check_blackbox_calls(login=TEST_LITE_LOGIN, call_count=5, second_method='hosted_domains')

    def test_can_register_by_phone_number_ok(self):
        self.setup_blackbox_responses(user_exists=False, login_available=False)
        resp = self.make_request(query_args={'login': TEST_LOCAL_PHONE_NUMBER.original})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal', 'neophonish'],
            login=None,
            phone_number=TEST_LOCAL_PHONE_NUMBER_DUMPED,
            country='ru',
            use_new_suggest_by_phone=False,
        )
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(register=True, input_login=TEST_LOCAL_PHONE_NUMBER.original)
        self.check_blackbox_calls(login=TEST_LOCAL_PHONE_NUMBER.original)

    def test_login_invalid_for_registration(self):
        self.setup_blackbox_responses(user_exists=False, login_available=True)
        resp = self.make_request(query_args={'login': TEST_INVALID_LOGIN})
        self.assert_error_response(resp, ['login.prohibitedsymbols'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False,)
        self.check_blackbox_calls(login=TEST_INVALID_LOGIN, call_count=3, second_method='hosted_domains')

    def test_login_not_available_for_registration(self):
        self.setup_blackbox_responses(user_exists=False, login_available=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['login.notavailable'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False,)
        self.check_blackbox_calls(call_count=2)

    def test_blackbox_invalid_params_error(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )
        resp = self.make_request(query_args={'login': 'a\nb'})
        self.assert_error_response(resp, ['login.prohibitedsymbols'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)
        self.check_blackbox_calls(call_count=1, login='a\nb')

    def test_lite_login_with_pdd_domain(self):
        self.setup_blackbox_responses(user_exists=False, login_available=True, pdd_domain_exists=True)
        resp = self.make_request(query_args={'login': TEST_LITE_LOGIN})
        self.assert_error_response(resp, ['account.not_found'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)
        self.check_blackbox_calls(login=TEST_LITE_LOGIN, call_count=5, second_method='hosted_domains')

    def test_unable_to_register(self):
        self.setup_blackbox_responses(user_exists=False, login_available=True)
        with settings_context(ALLOW_REGISTRATION=False):
            resp = self.make_request()
        self.assert_error_response(resp, ['account.not_found'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)
        self.check_blackbox_calls(call_count=2)

    def test_unable_to_register_lite(self):
        self.setup_blackbox_responses(user_exists=False, login_available=True)
        with settings_context(ALLOW_LITE_REGISTRATION=False):
            resp = self.make_request(query_args={'login': TEST_LITE_LOGIN})
        self.assert_error_response(resp, ['login.prohibitedsymbols'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)
        self.check_blackbox_calls(call_count=3, login=TEST_LITE_LOGIN, second_method='hosted_domains')

    def test_lite_registration_prohibited_by_origin(self):
        self.setup_blackbox_responses(user_exists=False, login_available=True, pdd_domain_exists=False)
        resp = self.make_request(query_args={'login': TEST_LITE_LOGIN, 'origin': TEST_ORIGIN_WITHOUT_LITE_REG})
        self.assert_error_response(resp, ['login.prohibitedsymbols'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)

    def test_unable_to_register_neophonish(self):
        self.setup_blackbox_responses(user_exists=False, login_available=False)
        with settings_context(ALLOW_NEOPHONISH_REGISTRATION=False, USE_NEW_SUGGEST_BY_PHONE=False):
            resp = self.make_request(query_args={'login': TEST_LOCAL_PHONE_NUMBER.original})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal'],
            login=None,
            phone_number=TEST_LOCAL_PHONE_NUMBER_DUMPED,
            country='ru',
            use_new_suggest_by_phone=False,
        )
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(register=True, input_login=TEST_LOCAL_PHONE_NUMBER.original)
        self.check_blackbox_calls(login=TEST_LOCAL_PHONE_NUMBER.original)

    def test_cookies_logged(self):
        resp = self.make_request(
            headers=dict(
                cookie='yp=%s; ys=%s; %s' % (
                    COOKIE_YP_VALUE,
                    COOKIE_YS_VALUE,
                    TEST_USER_COOKIES,
                ),
            ),
        )
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_statbox_ok(
            cookie_my=TEST_COOKIE_MY,
            cookie_yp=COOKIE_YP_VALUE,
            cookie_ys=COOKIE_YS_VALUE,
            l_login=TEST_LOGIN,
            l_uid=str(TEST_UID),
        )

    def test_cookie_l_invalid(self):
        resp = self.make_request(
            headers=dict(
                cookie=('yp=%s; ys=%s; %s' % (
                    COOKIE_YP_VALUE,
                    COOKIE_YS_VALUE,
                    TEST_USER_COOKIES,
                )).replace(TEST_COOKIE_L, 'foo'),
            ),
        )
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_statbox_ok(
            cookie_my=TEST_COOKIE_MY,
            cookie_yp=COOKIE_YP_VALUE,
            cookie_ys=COOKIE_YS_VALUE,
        )

    def test_pdd_retpath(self):
        self.setup_blackbox_responses(
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            emails=[self.env.email_toolkit.create_native_email('test-user', TEST_DOMAIN)],
            subscribed_to=[102],
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )
        resp = self.make_request(query_args={'login': TEST_PDD_LOGIN, 'retpath': TEST_PDD_RETPATH})
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                primary_alias_type=7,
                auth_methods=['password', 'magic_link', 'magic_x_token'],
                preferred_auth_method='password',
                magic_link_email='%s@%s' % (TEST_LOGIN, TEST_DOMAIN),
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_link', 'magic_x_token'],
            retpath=TEST_CLEANED_PDD_RETPATH,
            user_entered_login=TEST_PDD_LOGIN,
        )
        self.assert_statbox_ok(
            retpath=TEST_PDD_RETPATH,
            cleaned_retpath=TEST_CLEANED_PDD_RETPATH,
            input_login=TEST_PDD_LOGIN,
        )
        self.check_blackbox_calls(login=TEST_PDD_LOGIN)

    def test_magic_link__ok(self):
        self.setup_blackbox_responses(
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
            ],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_link', 'magic_x_token'],
                preferred_auth_method='password',
                magic_link_email='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_link', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link_and_qr_for_lite_not_allowed__ok(self):
        self.setup_blackbox_responses(
            aliases={
                'lite': TEST_LITE_LOGIN,
            },
            has_password=False,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', default=True),
            ],
        )
        with settings_context(ALLOW_MAGIC_LINK_FOR_LITE=False):
            resp = self.make_request()
        self.assert_error_response(resp, ['action.impossible'], primary_alias_type=5, track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)

    def test_magic_link_for_superlite__ok(self):
        self.setup_blackbox_responses(
            aliases={
                'lite': TEST_LITE_LOGIN,
            },
            has_password=False,
            has_sms_2fa=True,  # не мешает входить по magic link
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', default=True),
            ],
        )
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            primary_alias_type=5,
            can_authorize=True,
            auth_methods=['magic_link'],
            preferred_auth_method='magic_link',
            magic_link_email='%s@%s' % (TEST_LOGIN, 'mail.ru'),
            use_new_suggest_by_phone=False,
        )
        self.assert_track_ok(
            auth_methods=['magic_link'],
            with_magic=False,
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_by_phone__ok(self):
        self.setup_blackbox_responses(
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
            ],
        )
        resp = self.make_request(query_args={'login': TEST_LOCAL_PHONE_NUMBER.original})
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_link', 'magic_x_token'],
                preferred_auth_method='password',
                magic_link_email='t***r@%s' % 'yandex.ru',
                phone_number=TEST_LOCAL_PHONE_NUMBER_DUMPED,
                country='ru',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_link', 'magic_x_token'],
            user_entered_login=TEST_LOCAL_PHONE_NUMBER.original,
        )
        self.assert_statbox_ok(input_login=TEST_LOCAL_PHONE_NUMBER.original)
        self.check_blackbox_calls(login=TEST_LOCAL_PHONE_NUMBER.original)

    def test_magic_link__counter_per_uid__no_link(self):
        for _ in range(TEST_MAGIC_LINK_PER_UID_LIMIT):
            magic_link_per_uid_counter.incr(TEST_UID)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link__counter_per_ip__no_link(self):
        counter = magic_link_per_ip_counter.get_counter(TEST_RUSSIAN_IP)
        for _ in range(counter.limit):
            counter.incr(TEST_RUSSIAN_IP)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link__no_email__no_link(self):
        self.setup_blackbox_responses(
            emails=[self.create_validated_external_email(TEST_LOGIN, 'mail.ru')],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link__wrong_account__no_link(self):
        self.setup_blackbox_responses(
            login=TEST_LITE_LOGIN,
            aliases={
                'lite': TEST_LITE_LOGIN,
            },
            emails=[self.env.email_toolkit.create_validated_external_email('test-user', 'okna.ru')],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(primary_alias_type=5)
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link__strong_password__no_link(self):
        self.setup_blackbox_responses(
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
            ],
            subscribed_to=[67],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link__incomplete_pdd__no_link(self):
        self.setup_blackbox_responses(
            login=TEST_PDD_LOGIN,
            aliases={
                'pdd': TEST_PDD_LOGIN,
            },
            emails=[self.env.email_toolkit.create_native_email('test-user', TEST_DOMAIN)],
        )
        resp = self.make_request(query_args={'retpath': TEST_PDD_RETPATH})
        self.assert_ok_response(
            resp,
            **self.default_response_values(primary_alias_type=7)
        )
        self.assert_track_ok(retpath=TEST_CLEANED_PDD_RETPATH)
        self.assert_statbox_ok(
            retpath=TEST_PDD_RETPATH,
            cleaned_retpath=TEST_CLEANED_PDD_RETPATH,
        )
        self.check_blackbox_calls()

    def test_magic_link__autoregistered__no_link(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.100': 1,
                'subscription.suid.100': 1,
            },
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link__change_password__no_link(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 5,
                'subscription.suid.100': 1,
            },
            subscribed_to=[8],
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            password_change_required=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link__sms_2fa__no_link(self):
        self.setup_blackbox_responses(
            uid=TEST_UID,
            login=TEST_LOGIN,
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            has_sms_2fa=True,
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_magic_link_pdd_unicode_email__ok(self):
        self.setup_blackbox_responses(
            login=TEST_PDD_CYRILLIC_LOGIN,
            aliases={
                'pdd': TEST_PDD_CYRILLIC_LOGIN,
            },
            subscribed_to=[102],
            emails=[self.env.email_toolkit.create_native_email(TEST_CYRILLIC_LOGIN, TEST_CYRILLIC_DOMAIN_IDNA)],
            dbfields={
                'userinfo_safe.hintq.uid': u'99:вопрос',
                'userinfo_safe.hinta.uid': u'ответ',
            },
        )
        resp = self.make_request(query_args={'login': TEST_PDD_CYRILLIC_LOGIN})
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                primary_alias_type=7,
                auth_methods=['password', 'magic_link', 'magic_x_token'],
                preferred_auth_method='password',
                magic_link_email=TEST_PDD_CYRILLIC_LOGIN,
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_link', 'magic_x_token'],
            user_entered_login=TEST_PDD_CYRILLIC_LOGIN,
        )
        self.assert_statbox_ok(input_login=smart_text(TEST_PDD_CYRILLIC_LOGIN))

    def test_no_magic_x_token_and_social_profiles_intranet(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True)
        with settings_context(IS_INTRANET=True):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
            )
        )
        self.assert_track_ok(
            auth_methods=['magic', 'otp'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()
        eq_(len(self.env.social_api.requests), 0)

    def test_sms_code__ok(self):
        self.setup_blackbox_responses(with_phonenumber_alias=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'sms_code', 'magic_x_token'],
                preferred_auth_method='password',
                secure_phone_number=TEST_PHONE_NUMBER_DUMPED_MASKED,
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'sms_code', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_sms_code__not_allowed_for_strong_password(self):
        self.setup_blackbox_responses(with_phonenumber_alias=True, subscribed_to=[67])
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_x_token'],
                preferred_auth_method='password',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_sms_code__not_allowed_for_sms_2fa(self):
        self.setup_blackbox_responses(with_phonenumber_alias=True, has_sms_2fa=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_x_token'],
                preferred_auth_method='password',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_sms_code__disabled(self):
        self.setup_blackbox_responses(with_phonenumber_alias=True, attributes={'account.sms_code_login_forbidden': '1'})
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_x_token'],
                preferred_auth_method='password',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_sms_code__not_allowed_for_user_not_in_lah(self):
        self.cookie_lah_unpack_mock.return_value = AuthHistoryContainer()  # без нужного пользователя
        self.setup_blackbox_responses(with_phonenumber_alias=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_x_token'],
                preferred_auth_method='password',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_sms_code__not_allowed_for_too_old_lah(self):
        container = AuthHistoryContainer()
        container.add(TEST_UID, 123, 1, TEST_LOGIN)
        self.cookie_lah_unpack_mock.return_value = container
        self.setup_blackbox_responses(with_phonenumber_alias=True)
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_x_token'],
                preferred_auth_method='password',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_social_auth__strong_password__disabled(self):
        self.setup_blackbox_responses(subscribed_to=[67])

        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([profile_item(uid=TEST_UID)]),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_statbox_ok()
        self.check_blackbox_calls()
        self.assertEqual(self.env.social_api.requests, [])

    def test_social_auth__2fa__disabled(self):
        self.setup_blackbox_responses(has_2fa=True)

        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([profile_item(uid=TEST_UID)]),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
            )
        )
        self.assert_track_ok(auth_methods=['magic', 'otp'])
        self.assert_statbox_ok()
        self.check_blackbox_calls()
        self.assertEqual(self.env.social_api.requests, [])

    def test_password__social_suggest_mode(self):
        self.setup_blackbox_responses(
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
            ],
            with_phonenumber_alias=True,
        )
        self.setup_social_suggest_track()

        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([profile_item(uid=TEST_UID)]),
        )

        resp = self.make_request(query_args=dict(social_track_id=TEST_TRACK_ID2))

        expected_resp = self.default_response_values(auth_methods=['password'])
        expected_resp.pop('csrf_token', None)
        self.assert_ok_response(resp, **expected_resp)

        self.assert_track_ok(
            auth_methods=['password'],
            with_magic=False,
            with_social_suggest_data=True,
        )
        self.assert_statbox_ok()

    def test_2fa__social_suggest_mode(self):
        self.setup_blackbox_responses(
            has_2fa=True,
            has_password=False,
        )
        self.setup_social_suggest_track()

        resp = self.make_request(query_args=dict(social_track_id=TEST_TRACK_ID2))

        expected_resp = self.default_response_values(
            auth_methods=['magic', 'otp'],
            preferred_auth_method='magic',
        )
        self.assert_ok_response(resp, **expected_resp)

        self.assert_track_ok(auth_methods=['magic', 'otp'])
        self.assert_statbox_ok()

    def test_superlite__social_suggest_mode(self):
        email_login, email_domain = TEST_LITE_LOGIN.split('@')
        self.setup_blackbox_responses(
            aliases=dict(lite=TEST_LITE_LOGIN),
            emails=[self.create_validated_external_email(email_login, email_domain, default=True)],
            has_password=False,
        )
        self.setup_social_suggest_track()

        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([profile_item(uid=TEST_UID)]),
        )

        resp = self.make_request(query_args=dict(social_track_id=TEST_TRACK_ID2))

        expected_resp = self.default_response_values(
            auth_methods=['magic_link'],
            magic_link_email=TEST_LITE_LOGIN,
            preferred_auth_method='magic_link',
            primary_alias_type=5,
        )
        expected_resp.pop('csrf_token', None)
        self.assert_ok_response(resp, **expected_resp)

    def test_lite__social_suggest_mode(self):
        email_login, email_domain = TEST_LITE_LOGIN.split('@')
        self.setup_blackbox_responses(
            aliases=dict(lite=TEST_LITE_LOGIN),
            emails=[self.create_validated_external_email(email_login, email_domain, default=True)],
            has_password=True,
        )
        self.setup_social_suggest_track()

        resp = self.make_request(query_args=dict(social_track_id=TEST_TRACK_ID2))

        expected_resp = self.default_response_values(
            auth_methods=['password'],
            primary_alias_type=5,
        )
        expected_resp.pop('csrf_token', None)
        self.assert_ok_response(resp, **expected_resp)

    def test_old_track_id(self):
        self.setup_old_track_with_confirmed_phone()

        resp = self.make_request(query_args=dict(old_track_id=TEST_TRACK_ID2))
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok(with_confirmed_phone=True)

    def test_mobile_params_saved(self):
        resp = self.make_request(
            query_args=dict(client_id=TEST_CLIENT_ID, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME)
        )
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok(with_mobile_params=True)
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_scholar_login(self):
        self.setup_blackbox_responses(
            aliases=dict(scholar=TEST_SCHOLAR_LOGIN1),
            attributes={'account.scholar_password': TEST_PASSWORD_HASH1},
            has_password=False,
        )

        resp = self.make_request(
            query_args=dict(
                allow_scholar='1',
                login=TEST_SCHOLAR_LOGIN1,
            ),
        )

        assert len(self.env.blackbox.requests) == 1
        assert self.env.blackbox.requests[0].post_args.get('allow_scholar') == 'yes'

        auth_methods = ['password']

        expected_resp = self.default_response_values(
            auth_methods=auth_methods,
            primary_alias_type=EavSerializer.alias_name_to_type('scholar'),
        )
        expected_resp.pop('csrf_token', None)
        self.assert_ok_response(resp, **expected_resp)

        self.assert_track_ok(
            allow_scholar=True,
            auth_methods=auth_methods,
            user_entered_login=TEST_SCHOLAR_LOGIN1,
            with_magic=False,
        )

        self.env.statbox.bind_entry(
            'submitted',
            _exclude=['track_id'],
            _inherit_from=['submitted'],
            input_login=TEST_SCHOLAR_LOGIN1,
        )
        self.assert_statbox_ok()

    def test_scholar_login_when_scholar_not_found(self):
        self.env.blackbox.set_response_side_effect('userinfo', [blackbox_userinfo_response(uid=None)])

        resp = self.make_request(
            query_args=dict(
                allow_scholar='1',
                login=TEST_SCHOLAR_LOGIN1,
            ),
        )

        self.assert_error_response(resp, ['account.not_found'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)

    def test_scholar_login_when_scholar_not_found_and_disallowed(self):
        self.env.blackbox.set_response_side_effect('userinfo', [blackbox_userinfo_response(uid=None)])

        resp = self.make_request(query_args=dict(login=TEST_SCHOLAR_LOGIN1))

        assert len(self.env.blackbox.requests) == 1
        assert 'allow_scholar' not in self.env.blackbox.requests[0].post_args

        self.assert_error_response(resp, ['login.prohibitedsymbols'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)

    def test_login_to_completed_scholar_with_scholar_login(self):
        self.setup_blackbox_responses(
            aliases=dict(
                neophonish=TEST_NEOPHONISH_LOGIN1,
                scholar=TEST_SCHOLAR_LOGIN1,
            ),
            attributes={'account.scholar_password': TEST_PASSWORD_HASH1},
            has_password=False,
            with_phonenumber_alias=True,
        )

        resp = self.make_request(
            query_args=dict(
                allow_scholar='1',
                login=TEST_SCHOLAR_LOGIN1,
            ),
        )

        auth_methods = ['password']

        expected_resp = self.default_response_values(
            auth_methods=auth_methods,
            primary_alias_type=EavSerializer.alias_name_to_type('neophonish'),
        )
        expected_resp.pop('csrf_token', None)
        self.assert_ok_response(resp, **expected_resp)

        self.assert_track_ok(
            allow_scholar=True,
            auth_methods=auth_methods,
            user_entered_login=TEST_SCHOLAR_LOGIN1,
            with_magic=False,
        )

    def test_login_to_completed_scholar_with_not_scholar_login(self):
        self.setup_blackbox_responses(
            aliases=dict(
                neophonish=TEST_NEOPHONISH_LOGIN1,
                scholar=TEST_SCHOLAR_LOGIN1,
            ),
            attributes={'account.scholar_password': TEST_PASSWORD_HASH1},
            has_password=False,
            with_phonenumber_alias=True,
        )

        resp = self.make_request(
            query_args=dict(
                allow_scholar='1',
                login=TEST_PHONE_NUMBER.e164,
            ),
        )

        auth_methods = ['sms_code']

        expected_resp = self.default_response_values(
            auth_methods=auth_methods,
            country='us',
            phone_number=TEST_PHONE_NUMBER.as_dict(),
            preferred_auth_method=auth_methods[0],
            primary_alias_type=EavSerializer.alias_name_to_type('neophonish'),
            secure_phone_number=TEST_PHONE_NUMBER.as_dict(only_masked=True),
        )
        expected_resp.pop('csrf_token', None)
        self.assert_ok_response(resp, **expected_resp)

        self.assert_track_ok(
            allow_scholar=True,
            auth_methods=auth_methods,
            user_entered_login=TEST_PHONE_NUMBER.e164,
            with_magic=False,
        )

    def test_federal_ok(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=None),
                blackbox_userinfo_response(
                    aliases={
                        'federal': TEST_FEDERAL_ALIAS,
                        'pdd': TEST_FEDERAL_LOGIN,
                    },
                ),
            ]
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_FEDERAL_DOMAIN,
                domid=TEST_FEDERAL_DOMAIN_ID,
                is_enabled=True,
            ),
        )
        resp = self.make_request(query_args={'login': TEST_FEDERAL_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['saml_sso'],
            primary_alias_type=EavSerializer.alias_name_to_type('federal'),
            preferred_auth_method='saml_sso',
            use_new_suggest_by_phone=False,
        )

        eq_(len(self.env.blackbox.requests), 3)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'login': TEST_FEDERAL_LOGIN,
            'find_by_phone_alias': 'force_on',
            'country': 'RU',
        })
        self.env.blackbox.requests[1].assert_query_contains({'method': 'hosted_domains'})
        federal_userinfo_request = {
            'method': 'userinfo',
            'login': TEST_FEDERAL_ALIAS,
            'sid': 'federal',
        }
        self.env.blackbox.requests[2].assert_post_data_contains(federal_userinfo_request)
        self.assert_statbox_ok(input_login=TEST_FEDERAL_LOGIN)

    def test_federal_not_exist_yet_ok(self):
        # федерал еще не зарегистрирован, но видим что домен поддержан, значит можно авторизовать
        self.setup_blackbox_responses(user_exists=False, login_available=True)
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_FEDERAL_DOMAIN,
                domid=TEST_FEDERAL_DOMAIN_ID,
                is_enabled=True,
            ),
        )
        resp = self.make_request(query_args={'login': TEST_FEDERAL_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['saml_sso'],
            primary_alias_type=EavSerializer.alias_name_to_type('federal'),
            use_new_suggest_by_phone=False,
        )

        eq_(len(self.env.blackbox.requests), 4)
        self.env.blackbox.requests[0].assert_post_data_contains({
            'method': 'userinfo',
            'login': TEST_FEDERAL_LOGIN,
            'find_by_phone_alias': 'force_on',
            'country': 'RU',
        })
        self.env.blackbox.requests[1].assert_query_contains({'method': 'hosted_domains'})
        federal_userinfo_request = {
            'method': 'userinfo',
            'login': TEST_FEDERAL_ALIAS,
            'sid': 'federal',
        }
        self.env.blackbox.requests[2].assert_post_data_contains(federal_userinfo_request)
        self.env.blackbox.requests[3].assert_query_contains({'method': 'hosted_domains'})

        self.assert_statbox_ok(input_login=TEST_FEDERAL_LOGIN)

    def test_federal_domain_disabled_ok(self):
        # федерал зарегистрирован, но видим что домен выключен, авторизовать не можем
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response(uid=None),
                blackbox_userinfo_response(
                    aliases={
                        'federal': TEST_FEDERAL_ALIAS,
                        'pdd': TEST_FEDERAL_LOGIN,
                    },
                ),
            ]
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_FEDERAL_DOMAIN,
                domid=TEST_FEDERAL_DOMAIN_ID,
                is_enabled=False,
            ),
        )
        resp = self.make_request(query_args={'login': TEST_FEDERAL_LOGIN})
        self.assert_error_response(resp, ['login.prohibitedsymbols'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)

    @parameterized.expand([
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_federal_login_on_pdd_alias_ok(self, domain_enabled, sso_enabled):
        # при заходе по пдд логину не входим в некоторые ветки проверки вкл/выкл домена/ссо, важно чтоб нас не пустили, сказали что нет доступных способов входа
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                aliases={
                    'federal': TEST_FEDERAL_ALIAS,
                    'pdd': 'mail_' + TEST_FEDERAL_LOGIN,
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_FEDERAL_DOMAIN,
                domid=TEST_FEDERAL_DOMAIN_ID,
                is_enabled=domain_enabled,
            ),
        )
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok(enabled=sso_enabled))

        resp = self.make_request(query_args={'login': 'mail_' + TEST_FEDERAL_LOGIN})
        self.assert_error_response(resp, ['action.impossible'], primary_alias_type=24, track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)

    def test_federal_not_exist_disable_jit_provisioning_disabled_ok(self):
        # федерал еще не зарегистрирован, но авторегистрация при входе запрещена - должно говорить что нет такого аккаунта
        self.setup_blackbox_responses(user_exists=False, login_available=True)
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_FEDERAL_DOMAIN,
                domid=TEST_FEDERAL_DOMAIN_ID,
                is_enabled=True,
            ),
        )
        self.env.federal_configs_api.set_response_value('config_by_domain_id', federal_config_ok(disable_jit_provisioning=True))

        resp = self.make_request(query_args={'login': TEST_FEDERAL_LOGIN})
        self.assert_error_response(resp, ['account.not_found'], track_id=TEST_TRACK_ID, use_new_suggest_by_phone=False)

    def test_new_suggest_by_phone_ok(self):
        self.setup_blackbox_responses(user_exists=False, login_available=False)
        with settings_context(
            USE_NEW_SUGGEST_BY_PHONE=True,
            NEW_SUGGEST_BY_PHONE_DENOMINATOR=9,
        ):
            resp = self.make_request(query_args={'login': TEST_FAKE_PHONE_NUMBER.original})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal', 'neophonish'],
            login=None,
            phone_number=TEST_FAKE_PHONE_NUMBER_DUMPED,
            country='us',
            use_new_suggest_by_phone=True,
        )
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(register=True, input_login=TEST_FAKE_PHONE_NUMBER.original)
        self.check_blackbox_calls(login=TEST_FAKE_PHONE_NUMBER.original)

    def test_new_suggest_by_phone_experiment_disabled_for_number(self):
        self.setup_blackbox_responses(user_exists=False, login_available=False)
        with settings_context(
            USE_NEW_SUGGEST_BY_PHONE=True,
            NEW_SUGGEST_BY_PHONE_DENOMINATOR=9,
        ):
            resp = self.make_request(query_args={'login': TEST_LOCAL_PHONE_NUMBER.original})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_register=True,
            account_type='portal',
            allowed_account_types=['portal', 'neophonish'],
            login=None,
            phone_number=TEST_LOCAL_PHONE_NUMBER_DUMPED,
            country='ru',
            use_new_suggest_by_phone=False,
        )
        self.assert_track_ok(track_type='register')
        self.assert_statbox_ok(register=True, input_login=TEST_LOCAL_PHONE_NUMBER.original)
        self.check_blackbox_calls(login=TEST_LOCAL_PHONE_NUMBER.original)

    def test_2fa_pictures__ok(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True, yakey_device_ids=[TEST_DEVICE_ID])
        self.setup_push_api_list_response(with_trusted_subscription=True)

        with mock.patch('random.sample', mock.Mock(return_value=[1, 2, 3, 4])):
            resp = self.make_request(query_args={'with_2fa_pictures': 'yes'})

        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
                **{
                    '2fa_pictures': {
                        'correct': mock.ANY,
                        'expires_at': TimeNow(offset=TEST_2FA_PICTURES_TTL),
                        'count_left': 4,
                    },
                }
            )
        )
        self.assert_track_ok(
            auth_methods=['magic', 'otp'],
            with_2fa_pictures=True,
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_2fa_pictures__last_picture(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True, yakey_device_ids=[TEST_DEVICE_ID])
        self.setup_push_api_list_response(with_trusted_subscription=True)
        self.setup_kolmogor(shown=4)

        with mock.patch('random.sample', mock.Mock(return_value=[1, 2, 3, 4])):
            resp = self.make_request(query_args={'with_2fa_pictures': 'yes'})

        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
                **{
                    '2fa_pictures': {
                        'correct': mock.ANY,
                        'expires_at': TimeNow(offset=TEST_2FA_PICTURES_TTL),
                        'count_left': 0,
                    },
                }
            )
        )
        self.assert_track_ok(
            auth_methods=['magic', 'otp'],
            with_2fa_pictures=True,
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

        extra_data_part = {
            'user_ip': TEST_RUSSIAN_IP,
            '2fa_pictures': [1, 2, 3, 4],
            'user_agent': TEST_USER_AGENT,
            '2fa_pictures_expire_at': TimeNow(offset=60),
            'track_id': TEST_TRACK_ID,
            'uid': TEST_UID,
        }
        message = dict(
            push_id=AnyMatcher(),
            push_service='2fa',
            event_name='2fa_pictures',
            recipients=[
                dict(
                    uid=str(TEST_UID),
                    app_targeting_type='CLIENT_DECIDES',
                    subscription_source='YAKEY',
                    device_ids=[TEST_DEVICE_ID],
                ),
            ],
            text_body={'title': 'None'},
        )
        send_message = self.env.lbw_challenge_pushes.dict_requests[0]
        extra_data_send = send_message['push_message_request'].pop('extra_json')
        self.assertEqual(json.loads(extra_data_send), extra_data_part)
        self.assertEqual(send_message, {'push_message_request': message})

    def test_2fa_pictures__2fa_disabled(self):
        self.setup_blackbox_responses(has_password=True, has_2fa=False)
        resp = self.make_request(query_args={'with_2fa_pictures': 'yes'})
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['password', 'magic_x_token'],
                preferred_auth_method='password',
            )
        )
        self.assert_track_ok(
            auth_methods=['password', 'magic_x_token'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_2fa_pictures__no_yakey_device_ids(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True, yakey_device_ids=[])
        resp = self.make_request(query_args={'with_2fa_pictures': 'yes'})
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
            )
        )
        self.assert_track_ok(
            auth_methods=['magic', 'otp'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_2fa_pictures__wrong_device_id(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True, yakey_device_ids=[TEST_DEVICE_ID])
        self.setup_push_api_list_response(with_trusted_subscription=False)
        resp = self.make_request(query_args={'with_2fa_pictures': 'yes'})
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
            )
        )
        self.assert_track_ok(
            auth_methods=['magic', 'otp'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_2fa_pictures__limit_reached(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True, yakey_device_ids=[TEST_DEVICE_ID])
        self.setup_push_api_list_response(with_trusted_subscription=True)
        self.setup_kolmogor(shown=5)
        resp = self.make_request(query_args={'with_2fa_pictures': 'yes'})
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
                **{
                    '2fa_pictures': {
                        'count_left': 0,
                    },
                }
            )
        )
        self.assert_track_ok(
            auth_methods=['magic', 'otp'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()

    def test_2fa_pictures__user_denied(self):
        self.setup_blackbox_responses(has_password=False, has_2fa=True, yakey_device_ids=[TEST_DEVICE_ID])
        self.setup_push_api_list_response(with_trusted_subscription=True)
        self.setup_kolmogor(denied=1)
        resp = self.make_request(query_args={'with_2fa_pictures': 'yes'})
        self.assert_ok_response(
            resp,
            **self.default_response_values(
                auth_methods=['magic', 'otp'],
                preferred_auth_method='magic',
                **{
                    '2fa_pictures': {
                        'count_left': 0,
                    },
                }
            )
        )
        self.assert_track_ok(
            auth_methods=['magic', 'otp'],
        )
        self.assert_statbox_ok()
        self.check_blackbox_calls()
