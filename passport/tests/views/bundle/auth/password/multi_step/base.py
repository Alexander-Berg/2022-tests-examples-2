# -*- coding: utf-8 -*-
from datetime import datetime
import json
from time import time

import mock
from nose.tools import ok_
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    ProfileTestMixin,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_OAUTH_SCOPE
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_oauth_tokens_response,
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_oauth_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import messenger_api_response
from passport.backend.core.builders.push_api.faker import (
    push_api_app_subscription_info,
    push_api_list_response,
)
from passport.backend.core.builders.push_api.push_api import make_extra_data
from passport.backend.core.cookies import cookie_lah
from passport.backend.core.cookies.cookie_lah import AuthHistoryContainer
from passport.backend.core.models.account import ACCOUNT_ENABLED
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import deep_merge

from .base_test_data import (
    DEFAULT_PROFILE_SETTINGS,
    TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    TEST_CSRF_TOKEN,
    TEST_DEVICE_ID,
    TEST_DOMAIN,
    TEST_FOREIGN_HOST,
    TEST_LITE_LOGIN,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_ORIGIN,
    TEST_OTHER_DEVICE_ID,
    TEST_PDD_DOMAIN_INFO,
    TEST_PDD_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_RAW_ENV_FOR_PROFILE,
    TEST_REFERER,
    TEST_RETPATH,
    TEST_RUSSIAN_IP,
    TEST_TRACK_ID,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_YANDEXUID_COOKIE,
)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    YABS_URL='localhost',
)
class BaseMultiStepTestcase(BaseBundleTestViews, ProfileTestMixin, EmailTestMixin):
    default_url = None
    http_method = 'POST'
    consumer = 'dev'
    http_headers = {
        'host': TEST_FOREIGN_HOST,
        'user_agent': TEST_USER_AGENT,
        'cookie': 'Session_id=0:old-session; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
        'user_ip': TEST_RUSSIAN_IP,
        'referer': TEST_REFERER,
    }
    statbox_type = 'multi_step'

    def setUp(self):
        self.patches = []

        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.setup_trackid_generator()
        self.setup_csrf_token_mock()
        self.setup_cookie_lah_mock()
        self.start_patches()

        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_push_api_responses()
        self.setup_shakur_responses()
        self.setup_kolmogor_responses()

        self.setup_blackbox_responses()
        self.setup_statbox_templates()
        self.setup_antifraud_logger_templates()

        self.setup_messenger_api_responses()

    def tearDown(self):
        self.teardown_profile_patches()
        self.stop_patches()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches

    def setup_trackid_generator(self):
        self.track_manager = self.env.track_manager.get_manager()
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(TEST_TRACK_ID)
        self.patches.append(self.track_id_generator)

    def setup_csrf_token_mock(self):
        create_csrf_token_mock = mock.Mock(return_value=TEST_CSRF_TOKEN)
        patch = mock.patch(
            'passport.backend.api.views.bundle.auth.password.multi_step.start.create_csrf_token',
            create_csrf_token_mock,
        )
        self.patches.append(patch)

    def setup_cookie_lah_mock(self):
        container = AuthHistoryContainer()
        container.add(TEST_UID, time(), 1, TEST_LOGIN)
        self.cookie_lah_unpack_mock = mock.Mock(return_value=container)

        cookie_lah_unpack_patch = mock.patch.object(
            cookie_lah.CookieLAH,
            'unpack',
            self.cookie_lah_unpack_mock,
        )
        self.patches.append(cookie_lah_unpack_patch)

    def setup_push_api_list_response(self, with_trusted_subscription=False):
        _s = push_api_app_subscription_info
        device_id = TEST_DEVICE_ID if with_trusted_subscription else TEST_OTHER_DEVICE_ID
        am_extra = make_extra_data(
            login_id=(TEST_LOGIN_ID if with_trusted_subscription else 'other-id'),
            am_version='6.5.0',
        )
        subscriptions = [
            _s(1, '12345', 'ru.yandex.test', 'apns', device_id, extra=am_extra),
            _s(2, '123456', 'ru.yandex.test', 'fcm', TEST_OTHER_DEVICE_ID),
            _s(3, '1234567', 'ru.yandex.key', 'fcm', device_id),
        ]
        self.env.push_api.set_response_value('list', push_api_list_response(subscriptions))

    def setup_push_api_responses(self):
        self.env.push_api.set_response_value('send', 'OK')

    def setup_shakur_responses(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def setup_messenger_api_responses(self):
        self.env.messenger_api.set_response_value('check_user_lastseen', messenger_api_response(TEST_UID))

    def setup_bb_get_tokens_response(self):
        trusted_token = dict(
            login_id=TEST_LOGIN_ID,
            is_xtoken_trusted=True,
            device_id=TEST_DEVICE_ID,
        )
        self.env.blackbox.set_response_value(
            'get_oauth_tokens',
            blackbox_get_oauth_tokens_response(
                [trusted_token],
            ),
        )

    def setup_blackbox_responses(
        self, user_exists=True, user_disabled_status=ACCOUNT_ENABLED, uid=TEST_UID,
        has_password=True, has_2fa=False, has_sms_2fa=False, emails=None,
        login=TEST_LOGIN, aliases=None, subscribed_to=None, display_name=None,
        avatar_key='', dbfields=None, password_change_required=False, language='ru',
        account_deletion_operation_started_at=None, with_phonenumber_alias=False,
        attributes=None, password_status=None, is_fresh=False, yakey_device_ids=None, **kwargs
    ):
        emails = emails or [
            self.create_validated_external_email(TEST_LOGIN, 'mail.ru'),
        ]
        aliases = aliases or {'portal': login}
        if with_phonenumber_alias:
            aliases['phonenumber'] = TEST_PHONE_NUMBER.digital
        attributes = attributes or {}
        attributes.update({
            'account.2fa_on': str(int(has_2fa)),
            'account.sms_2fa_on': str(int(has_sms_2fa)),
            'account.is_disabled': str(user_disabled_status),
            'account.totp.yakey_device_ids': ','.join(yakey_device_ids or []),
        })
        if account_deletion_operation_started_at is not None:
            attributes.update({'account.deletion_operation_started_at': account_deletion_operation_started_at})
        if password_change_required:
            attributes.update({'password.forced_changing_reason': '1'})
        dbfields = dbfields or {}
        if is_fresh:
            dbfields.update({
                'userinfo.reg_date.uid': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(
                count=1,
                domain=TEST_DOMAIN,
            ),
        )
        common_account_kwargs = dict(
            uid=uid if user_exists else None,
            login=login,
            aliases=aliases,
            attributes=attributes,
            dbfields=dbfields,
            emails=emails,
            crypt_password='1:pwd' if has_password else None,
            subscribed_to=subscribed_to or [],
            display_name=display_name or {},
            default_avatar_key=avatar_key,
            language=language,
            **kwargs
        )
        if with_phonenumber_alias:
            phone_secured = build_phone_secured(
                1,
                TEST_PHONE_NUMBER.e164,
            )
            common_account_kwargs = deep_merge(common_account_kwargs, phone_secured)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                **common_account_kwargs
            ),
        )
        login_kwargs = dict(common_account_kwargs)
        if password_status:
            login_kwargs.update(dict(password_status=password_status))
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                **login_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **common_account_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=TEST_OAUTH_SCOPE,
                **common_account_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='any_auth',
            type=self.statbox_type,
            track_id=TEST_TRACK_ID,
            ip=TEST_RUSSIAN_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
            origin=TEST_ORIGIN,
        )
        self.env.statbox.bind_entry(
            'submitted',
            action='submitted',
            input_login=TEST_LOGIN,
            referer=TEST_REFERER,
            retpath=TEST_RETPATH,
            _exclude=['track_id'],
        )
        self.env.statbox.bind_entry(
            'decision_reached',
            action='decision_reached',
            referer=TEST_REFERER,
            retpath=TEST_RETPATH,
        )
        self.env.statbox.bind_entry(
            'updated',
            action='updated',
            referer=TEST_REFERER,
            uid=str(TEST_UID),
            _exclude=['track_id', 'origin'],
        )
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            uid=str(TEST_UID),
            action='profile_threshold_exceeded',
            is_password_change_required='0',
            email_sent='1',
        )
        self.env.statbox.bind_entry(
            'redirect_to_password_change',
            action='redirect_to_password_change',
            mode='change_flushed_password',
            track_id=TEST_TRACK_ID,
            uid=str(TEST_UID),
            _exclude=['consumer', 'ip', 'origin', 'user_agent', 'yandexuid'],
        )
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            _exclude=['origin'],
            _inherit_from='local_base',
            action='ufo_profile_checked',
            current=self.make_user_profile(raw_env=TEST_RAW_ENV_FOR_PROFILE).as_json,
            decision_source='ufo',
            is_fresh_account='0',
            is_challenge_required='0',
            ufo_status='1',
            ufo_distance='100',
            uid=str(TEST_UID),
        )

    def setup_antifraud_logger_templates(self):
        self.env.antifraud_logger.bind_entry(
            'auth_fail',
            request='auth',
            channel='auth',
            sub_channel='login',
            status='FAILED',
            AS='AS13238',
            uid=str(TEST_UID),
            ip=TEST_RUSSIAN_IP,
            user_agent=TEST_USER_AGENT,
            external_id='track-{}'.format(TEST_TRACK_ID),
            service_id='login',
        )

    def start_patches(self):
        for patch in self.patches:
            patch.start()

    def stop_patches(self):
        for patch in reversed(self.patches):
            patch.stop()

    def default_response_values(self):
        return {
            'track_id': TEST_TRACK_ID,
        }

    def account_response_values(self, login=TEST_LOGIN, is_workspace_user=False, **kwargs):
        response = {
            'display_login': login,
            'display_name': {
                'default_avatar': '',
                'name': '',
            },
            'is_2fa_enabled': False,
            'is_rfc_2fa_enabled': False,
            'is_yandexoid': False,
            'is_workspace_user': is_workspace_user,
            'login': login,
            'person': {
                'birthday': u'1963-05-15',
                'country': u'ru',
                'firstname': u'\\u0414',
                'gender': 1,
                'language': u'ru',
                'lastname': u'\\u0424',
            },
            'uid': TEST_UID,
        }
        response.update(kwargs)
        return response

    def assert_track_ok(self):
        raise NotImplementedError()  # pragma: no cover

    def assert_antifraud_auth_fail_not_written(self):
        self.env.antifraud_logger.assert_has_written([])

    def assert_antifraud_auth_fail_written(
        self, offset=0, _exclude=None, **kwargs
    ):
        self.env.antifraud_logger.assert_contains(
            self.env.antifraud_logger.entry('auth_fail', _exclude=_exclude, **kwargs),
            offset=offset,
        )


class CommonAuthTests(object):
    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response_values()
        )
        self.assert_track_ok()
        self.assert_antifraud_auth_fail_not_written()

    def test_invalid_host_error(self):
        resp = self.make_request(
            headers=dict(host='google.com'),
        )
        self.assert_error_response(resp, ['host.invalid'])
        self.assert_antifraud_auth_fail_not_written()

    def test_invalid_track_type(self):
        _, track_id = self.env.track_manager.get_manager_and_trackid('register')
        resp = self.make_request(query_args={'track_id': track_id})
        self.assert_error_response(resp, ['track.invalid_state'], track_id=track_id)
        self.assert_antifraud_auth_fail_not_written()

    def test_invalid_track_state(self):
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = None
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=TEST_TRACK_ID)
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_already_passed_error(self):
        with self.track_transaction(self.track_id) as track:
            track.session = '0:session'
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'], track_id=TEST_TRACK_ID)
        self.assert_antifraud_auth_fail_not_written()

    def test_password_change_required(self):
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            dbfields={
                'subscription.login_rule.8': 4,
            },
            attributes={
                'password.forced_changing_reason': '1',
            },
            crypt_password='1:pass',
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_kwargs),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
            state='change_password',
            validation_method='captcha_and_phone',
            change_password_reason='account_hacked',
            number=dump_number(TEST_PHONE_NUMBER),
            account=self.account_response_values(),
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_pdd_completion_required(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_PDD_LOGIN,
                crypt_password='1:pwd',
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
            ),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='complete_pdd',
                account=self.account_response_values(login=TEST_PDD_LOGIN, domain=TEST_PDD_DOMAIN_INFO),
            )
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(track.is_complete_pdd)
        ok_(not track.is_complete_pdd_with_password)
        self.assert_antifraud_auth_fail_not_written()

    def test_lite_completion_required(self):
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LITE_LOGIN,
                crypt_password='1:pwd',
                aliases={
                    'lite': TEST_LITE_LOGIN,
                },
            ),
        )
        with settings_context(
                GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
                BLACKBOX_URL='localhost',
                YABS_URL='localhost',
                LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=1,
                **dict(
                    DEFAULT_PROFILE_SETTINGS,
                    AUTH_PROFILE_ENABLED=False,
                )
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='force_complete_lite',
                account=self.account_response_values(login=TEST_LITE_LOGIN),
                has_recovery_method=False,
            )
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_show_antifraud_challenge(self):
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            tags=['call', 'email_hint'],
        ))

        with settings_context(
            GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
            BLACKBOX_URL='localhost',
            YABS_URL='localhost',
            **DEFAULT_PROFILE_SETTINGS
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_sms_2fa_challenge(self):
        self.cookie_lah_unpack_mock.return_value = AuthHistoryContainer()  # без нужного пользователя
        self.setup_blackbox_responses(has_sms_2fa=True)

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_sms_2fa_old_device_challenge(self):
        self.setup_blackbox_responses(has_sms_2fa=True)

        with settings_context(
            GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
            DISABLE_SMS_2FA_CHALLENGE_ONLY_ON_KNOWN_DEVICES_DENOMINATOR=1,  # 100%
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_account_force_challenge(self):
        self.setup_blackbox_responses(attributes={'account.force_challenge': '1'})

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_account_force_challenge_no_settings_auth_profile(self):
        self.setup_blackbox_responses(attributes={'account.force_challenge': '1'})

        with settings_context(
            AUTH_PROFILE_ENABLED=False,
            GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
            ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )

    def test_account_force_challenge_account_is_shared(self):
        self.setup_blackbox_responses(attributes={
            'account.force_challenge': '1',
            'account.is_shared': '1',
        })

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )

    def test_account_force_challenge_account_totp_secret_is_set(self):
        self.setup_blackbox_responses(
            attributes={'account.force_challenge': '1'},
            has_2fa=True,
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(is_2fa_enabled=True),
            )
        )

    def test_account_force_challenge_fresh_account(self):
        self.setup_blackbox_responses(
            attributes={'account.force_challenge': '1'},
            is_fresh=True,
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )

    def test_account_force_challenge_zero_denominator(self):
        self.setup_blackbox_responses(
            attributes={'account.force_challenge': '1'},
            is_fresh=True,
        )

        with settings_context(
            AUTH_CHALLENGE_DENOMINATOR=0,
            GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
            ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
        ):
            resp = self.make_request()

        self.assert_ok_response(
            resp,
            **dict(
                self.default_response_values(),
                state='auth_challenge',
                account=self.account_response_values(),
            )
        )
