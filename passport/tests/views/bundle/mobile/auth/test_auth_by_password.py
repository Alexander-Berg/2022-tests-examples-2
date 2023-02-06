# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json
from time import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import (
    EmailTestMixin,
    ProfileTestMixin,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_ANOTHER_IP,
    TEST_IP,
)
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_AVATAR_SIZE,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_CLOUD_TOKEN,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_ESCAPED_DEVICE_NAME,
    TEST_LOCATION,
    TEST_OAUTH_TOKEN_TTL,
    TEST_OAUTH_X_TOKEN,
    TEST_OAUTH_X_TOKEN_TTL,
    TEST_USER_IP,
    TEST_X_TOKEN_CLIENT_ID,
    TEST_X_TOKEN_CLIENT_SECRET,
    TEST_YANDEX_IP,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AVATAR_KEY,
    TEST_AVATAR_SECRET,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_LOGIN,
    TEST_OAUTH_TOKEN,
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_PHONE_NUMBER,
    TEST_PUBLIC_ID,
    TEST_UID,
    TEST_YANDEX_TEST_LOGIN,
)
from passport.backend.api.views.bundle.mixins.challenge import (
    DecisionSource,
    MobilePasswordSource,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.core.builders.antifraud import ScoreAction
from passport.backend.core.builders.antifraud.faker.fake_antifraud import (
    antifraud_score_response,
    AntifraudScoreParams,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
    BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
    BLACKBOX_CHECK_SIGN_STATUS_EXPIRED,
    BLACKBOX_PASSWORD_BAD_STATUS,
    BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
    BLACKBOX_SECOND_STEP_EMAIL_CODE,
    BLACKBOX_SECOND_STEP_RFC_TOTP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_sign_response,
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_sign_response,
)
from passport.backend.core.builders.captcha import (
    CaptchaLocateError,
    CaptchaServerError,
)
from passport.backend.core.builders.captcha.faker import (
    captcha_response_check,
    captcha_response_generate,
)
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import messenger_api_response
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.builders.oauth.faker import oauth_bundle_successful_response
from passport.backend.core.builders.ufo_api import UfoApiTemporaryError
from passport.backend.core.builders.ufo_api.faker import (
    ufo_api_profile_item,
    ufo_api_profile_response,
)
from passport.backend.core.builders.ysa_mirror.faker.ysa_mirror import (
    TEST_YSA_MIRROR_RESOLUTION1,
    ysa_mirror_no_resolution_response,
    ysa_mirror_ok_resolution_response,
)
from passport.backend.core.builders.ysa_mirror.ysa_mirror import (
    YsaMirrorPermanentError,
    YsaMirrorTemporaryError,
)
from passport.backend.core.conf import settings
from passport.backend.core.counters.profile_fails import is_profile_broken
from passport.backend.core.env_profile.metric import EnvDistance
from passport.backend.core.env_profile.profiles import UfoProfile
from passport.backend.core.mailer.utils import masked_login
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)
from passport.backend.core.utils.version import parse_am_version
from passport.backend.utils.common import deep_merge


TEST_ENV_PROFILE = dict(
    cloud_token=TEST_CLOUD_TOKEN,
    device_id=TEST_DEVICE_ID,
    ip=TEST_IP,
    is_mobile=True,
    yandexuid=None,
    user_agent_info={},
)

TEST_ENV_PROFILE_DISTANT = dict(
    cloud_token=TEST_CLOUD_TOKEN,
    device_id=TEST_DEVICE_ID,
    ip=TEST_ANOTHER_IP,
    is_mobile=True,
    yandexuid=None,
    user_agent_info={},
)


def region_mock_side_effect(ip):
    if ip == TEST_IP:
        as_ = 'AS1'
    else:
        as_ = 'AS2'
    return mock.Mock(AS_list=[as_], country={'id': 1}, city={'id': 2})


class BaseChallengeTestCase(BaseBundleTestViews):
    def setup_profile_response(self, distant_fresh=False, full_profile=None, add_fresh_profile=False,
                               with_device_id=False):
        items = []

        if full_profile:
            ufo_full_item = ufo_api_profile_item(
                # фреш-профили от полного профиля отличаются особым timeuuid
                timeuuid=UfoProfile.PROFILE_FAKE_UUID,
                data=full_profile,
            )
            items.append(ufo_full_item)

        self.fake_region_profile_mock.side_effect = region_mock_side_effect

        if distant_fresh or add_fresh_profile:
            data = TEST_ENV_PROFILE_DISTANT if distant_fresh else TEST_ENV_PROFILE
            if with_device_id:
                data.update(device_id=TEST_DEVICE_ID)
            ufo_fresh_item = ufo_api_profile_item(
                timeuuid=str(self.new_uuid1),
                data=data,
            )
            items.append(ufo_fresh_item)

        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=items,
                ),
            ),
        )


class BaseTestAuthByPasswordView(EmailTestMixin, ProfileTestMixin):
    default_url = '/1/bundle/mobile/auth/password/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }
    http_query_args = {
        'password': TEST_PASSWORD,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.device_id = TEST_DEVICE_ID
            track.device_name = TEST_DEVICE_NAME
            track.avatar_size = TEST_AVATAR_SIZE
            track.cloud_token = TEST_CLOUD_TOKEN
        self.http_query_args.update(track_id=self.track_id)

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'mobile': ['auth']},
            ),
        )
        self.env.oauth.set_response_side_effect(
            '_token',
            (
                {
                    'access_token': TEST_OAUTH_X_TOKEN,
                    'token_type': 'bearer',
                    'expires_in': TEST_OAUTH_X_TOKEN_TTL,
                },
                {
                    'access_token': TEST_OAUTH_TOKEN,
                    'token_type': 'bearer',
                    'expires_in': TEST_OAUTH_TOKEN_TTL,
                },
            ),
        )
        self.setup_blackbox_response()
        self.setup_kolmogor_responses()
        self.setup_shakur_responses()
        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_statbox_templates()
        self.setup_antifraud_logger_templates()

        self.fake_region_challenge_mock = mock.Mock(return_value=mock.Mock(
            AS_list=['AS1'],
            country={'id': 84},
            city={'id': 102630},
        ))
        self.fake_region_profile_mock = mock.Mock(return_value=mock.Mock(
            AS_list=['AS1'],
            country={'id': 84},
            city={'id': 102630},
        ))
        self.region_challenge_patch = mock.patch(
            'passport.backend.api.common.ip.Region',
            self.fake_region_challenge_mock,
        )
        self.region_profile_patch = mock.patch(
            'passport.backend.core.env_profile.helpers.Region',
            self.fake_region_profile_mock,
        )
        self.region_challenge_patch.start()
        self.region_profile_patch.start()

        self.setup_messenger_api_responses()

    def tearDown(self):
        self.region_profile_patch.stop()
        del self.region_profile_patch
        self.region_challenge_patch.stop()
        del self.region_challenge_patch
        self.teardown_profile_patches()
        del self.track_manager
        self.env.stop()
        del self.env

    def setup_untrusted_network(self):
        self.fake_region_challenge_mock.side_effect = None
        self.fake_region_challenge_mock.return_value = mock.Mock(
            AS_list=['AS1234'],
            country={'id': 84},
            city={'id': 102630},
        )
        self.fake_region_profile_mock.side_effect = None
        self.fake_region_profile_mock.return_value = mock.Mock(
            AS_list=[],
            country={'id': 84},
            city={'id': 102630},
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            _inherit_from='base',
            ip=TEST_IP,
            input_login=TEST_LOGIN,
            track_id=self.track_id,
            mode='any_auth',
            type='mobile_password',
            consumer='dev',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'ysa_mirror',
            _inherit_from='local_base',
            _exclude=['input_login'],
            action='ysa_mirror',
        )
        self.env.statbox.bind_entry(
            'ufo_profile_checked',
            _inherit_from='local_base',
            action='ufo_profile_checked',
            current=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
            ufo_status='1',
            ufo_distance='100',
            is_fresh_profile_passed='0',
            is_fresh_account='0',
            is_challenge_required='0',
            is_mobile='1',
            decision_source=DecisionSource.UFO,
            uid=str(TEST_UID),
            kind='ufo',
            device_id=TEST_DEVICE_ID,
        )
        self.env.statbox.bind_entry(
            'sms_2fa_challenge',
            _inherit_from='local_base',
            action='sms_2fa_challenge',
            current=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
            ufo_status='1',
            is_challenge_required='0',
            is_mobile='1',
            decision_source=DecisionSource.UFO,
            uid=str(TEST_UID),
            kind='ufo',
            device_id=TEST_DEVICE_ID,
        )
        self.env.statbox.bind_entry(
            'skip_challenge',
            _inherit_from='local_base',
            _exclude=['input_login'],
            action='skip_challenge',
            uid=str(TEST_UID),
            device_id=TEST_DEVICE_ID,
        )
        self.env.statbox.bind_entry(
            'profile_threshold_exceeded',
            _inherit_from='local_base',
            action='profile_threshold_exceeded',
            is_password_change_required='0',
            is_mobile='1',
            email_sent='1',
            kind='ufo',
            was_online_sec_ago=TimeSpan(0),
        )
        self.env.statbox.bind_entry(
            'ufo_profile_compared',
            _inherit_from='local_base',
            _exclude=['type'],
            action='ufo_profile_compared',
            uid=str(TEST_UID),
            is_mobile='1',
            ydb_profile_items='[]',
            ufo_profile_items='[]',
        )
        self.env.statbox.bind_entry(
            'auth_notification',
            _inherit_from='local_base',
            _exclude=['input_login'],
            action='auth_notification',
            counter_exceeded='0',
            email_sent='1',
            device_name=TEST_DEVICE_NAME,
            is_challenged='1',
        )
        self.env.statbox.bind_entry(
            'tokens_issued',
            _inherit_from='local_base',
            _exclude=['user_agent', 'input_login'],
            action='tokens_issued',
            uid=str(TEST_UID),
            login=TEST_LOGIN,
            password_passed='1',
            x_token_client_id=TEST_X_TOKEN_CLIENT_ID,
            x_token_issued='1',
            client_id=TEST_CLIENT_ID,
            client_token_issued='1',
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            cloud_token=TEST_CLOUD_TOKEN,
        )

    def setup_antifraud_logger_templates(self):
        self.env.antifraud_logger.bind_entry(
            'auth_fail',
            _exclude=['user_agent'],
            request='auth',
            channel='auth',
            sub_channel='login',
            status='FAILED',
            AS='AS1',
            uid=str(TEST_UID),
            ip=TEST_IP,
            external_id='track-{}'.format(self.track_id),
            service_id='login',
        )

    def setup_messenger_api_responses(self):
        self.env.messenger_api.set_response_value('check_user_lastseen', messenger_api_response(TEST_UID))

    def setup_blackbox_response(self, uid=TEST_UID, has_password=True, aliases=None, login=TEST_LOGIN, **kwargs):
        blackbox_login_response_arguments = dict(
            uid=uid,
            login=login,
            display_name=TEST_DISPLAY_NAME_DATA,
            default_avatar_key=TEST_AVATAR_KEY,
            is_avatar_empty=True,
            crypt_password=TEST_PASSWORD_HASH if has_password else None,
            emails=[
                self.create_validated_external_email(TEST_LOGIN, 'gmail.com'),
                self.create_validated_external_email(TEST_LOGIN, 'mail.ru', rpop=True),
                self.create_validated_external_email(TEST_LOGIN, 'silent.ru', silent=True),
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            aliases=aliases,
            public_id=TEST_PUBLIC_ID,
        )
        if aliases and 'lite' in aliases:
            blackbox_login_response_arguments['emails'].pop()
            blackbox_login_response_arguments['emails'] = [self.create_validated_external_email(*(aliases['lite'].split('@')))]
        blackbox_login_response_arguments.update(kwargs)

        self.env.blackbox.set_response_value(
            'login',
            blackbox_login_response(**blackbox_login_response_arguments),
        )
        self.env.blackbox.set_response_value(
            'sign',
            blackbox_sign_response(TEST_AVATAR_SECRET),
        )

    def setup_kolmogor_responses(self):
        self.env.kolmogor.set_response_value('inc', 'OK')
        self.env.kolmogor.set_response_value('get', '1')

    def setup_shakur_responses(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def default_account_info(self, display_login=TEST_LOGIN, normalized_display_login=TEST_LOGIN, **kwargs):
        info = dict(
            uid=TEST_UID,
            native_default_email='%s@yandex.ru' % TEST_LOGIN,
            primary_alias_type=1,
            has_password=True,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
            is_avatar_empty=True,
            firstname='\\u0414',
            lastname='\\u0424',
            birthday='1963-05-15',
            gender='m',
            public_id=TEST_PUBLIC_ID,
        )
        if display_login is not None:
            info.update(display_login=display_login)
        if normalized_display_login is not None:
            info.update(normalized_display_login=normalized_display_login)
        info.update(**kwargs)
        return info

    def default_response(self, with_access_token=True, with_payment_auth=False, **kwargs):
        result = dict(
            self.default_account_info(**kwargs),
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
        )
        if with_access_token:
            result.update(
                access_token=TEST_OAUTH_TOKEN,
                access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            )
        if with_payment_auth:
            result.update(
                payment_auth_context_id='context_id',
                payment_auth_url='url',
                payment_auth_app_ids=['app_id1', 'app_id2'],
            )
        return result

    def assert_notifications_sent(
        self, location=TEST_LOCATION, device_name=TEST_ESCAPED_DEVICE_NAME, is_challenged=False, login=TEST_LOGIN, is_lite=False,
    ):
        if is_challenged:
            emails = [
                self._build_challenge_email(
                    address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
                    is_native=False,
                    location=location,
                    device_name=device_name,
                    login=login,
                ),
                self._build_challenge_email(
                    address='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
                    is_native=True,
                    location=location,
                    device_name=device_name,
                ),
            ]
        else:
            emails = [
                self._build_auth_email(
                    address='%s@%s' % (TEST_LOGIN, 'gmail.com'),
                    is_native=False,
                    location=location,
                    device_name=device_name,
                    login=login,
                ),
                self._build_auth_email(
                    address='%s@%s' % (TEST_LOGIN, 'yandex.ru'),
                    is_native=True,
                    location=location,
                    device_name=device_name,
                ),
            ]
        if is_lite:
            emails.pop()
            if is_challenged:
                emails = [
                    self._build_challenge_email(
                        address=login,
                        is_native=False,
                        location=location,
                        device_name=device_name,
                        login=login,
                    ),
                ]
            else:
                emails = [
                    self._build_auth_email(
                        address=login,
                        is_native=False,
                        location=location,
                        device_name=device_name,
                        login=login,
                    ),
                ]
        self.assert_emails_sent(emails)

    def assert_notifications_not_sent(self):
        self.assert_emails_sent([])

    def assert_ufo_profile_check_recorded_to_statbox(self, **kwargs):
        self.check_statbox_log_entry(
            self.env.statbox_handle_mock,
            self.env.statbox.entry(
                'ufo_profile_checked',
                **kwargs
            ),
            entry_index=0,
        )

    def assert_antifraud_auth_fail_not_written(self):
        self.env.antifraud_logger.assert_has_written([])

    def assert_antifraud_auth_fail_written(
        self, comment_appendix='', offset=0, _exclude=None, **kwargs
    ):
        kwargs['comment'] = 'mobile_password'
        if comment_appendix:
            kwargs['comment'] += '/' + comment_appendix
        self.env.antifraud_logger.assert_contains(
            self.env.antifraud_logger.entry('auth_fail', _exclude=_exclude, **kwargs),
            offset=offset,
        )

    def check_blackbox_call(self):
        assert len(self.env.blackbox.requests) == 1
        calls = self.env.blackbox.get_requests_by_method('login')
        assert len(calls) == 1
        calls[0].assert_post_data_contains({
            'method': 'login',
            'login': TEST_LOGIN,
            'emails': 'getall',
            'find_by_phone_alias': 'force_on',
            'country': 'US',
        })

    def _build_auth_email(self, address, location, device_name, login=TEST_LOGIN, is_native=False):
        data = {
            'language': 'ru',
            'addresses': [address],
            'subject': 'auth_challenge.lite.subject',
            'tanker_keys': {
                'greeting': {'FIRST_NAME': u'\\u0414'},
                'auth_challenge.lite.notice': {
                    'MASKED_LOGIN': login if is_native else masked_login(login),
                },
                'auth_challenge.if_hacked.with_url': {
                    'SUPPORT_URL': '<a href=\'https://yandex.ru/support/passport/troubleshooting/hacked.html\'>https://yandex.ru/support/passport/troubleshooting/hacked.html</a>',
                },
                'signature.secure': {},
            },
        }
        if location:
            data['tanker_keys']['auth_challenge.we_know'] = {}
            data['tanker_keys']['user_meta_data.location'] = {
                'LOCATION': location,
            }
        if device_name:
            data['tanker_keys']['auth_challenge.we_know'] = {}
            data['tanker_keys']['auth_challenge.device_name'] = {
                'DEVICE_NAME': device_name,
            }
        return data

    def _build_challenge_email(self, address, location, device_name, login=TEST_LOGIN, is_native=False):
        data = {
            'language': 'ru',
            'addresses': [address],
            'subject': 'auth_challenge.subject',
            'tanker_keys': {
                'greeting': {'FIRST_NAME': u'\\u0414'},
                'auth_challenge.notice': {
                    'MASKED_LOGIN': login if is_native else masked_login(login),
                },
                'auth_challenge.if_hacked.with_url': {
                    'SUPPORT_URL': '<a href=\'https://yandex.ru/support/passport/troubleshooting/hacked.html\'>https://yandex.ru/support/passport/troubleshooting/hacked.html</a>',
                },
                'auth_challenge.journal.with_url': {
                    'JOURNAL_URL': '<a href=\'https://passport.yandex.ru/profile/journal\'>https://passport.yandex.ru/profile/journal</a>',
                },
                'signature.secure': {},
            },
        }
        if location:
            data['tanker_keys']['auth_challenge.we_know'] = {}
            data['tanker_keys']['user_meta_data.location'] = {
                'LOCATION': location,
            }
        if device_name:
            data['tanker_keys']['auth_challenge.we_know'] = {}
            data['tanker_keys']['auth_challenge.device_name'] = {
                'DEVICE_NAME': device_name,
            }
        return data


class CommonAuthByPasswordTests(BaseTestAuthByPasswordView):
    def test_ok(self):
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        with self.track_transaction(self.track_id) as track:
            # известный девайс и версия которая поддерживает челенджи
            track.account_manager_version = '8.0.0'
            track.device_os_id = 'iPhone'
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response()
        )

        self.check_blackbox_call()
        eq_(len(self.env.oauth.requests), 3)
        self.env.oauth.requests[0].assert_properties_equal(
            method='GET',
            url='http://localhost/api/1/device/status?consumer=passport&uid=%s&device_id=%s&device_name=%s&am_version=%s&am_version_name=%s&app_platform=%s' % (
                TEST_UID,
                TEST_DEVICE_ID,
                TEST_DEVICE_NAME,
                '8.0.0',
                '8.0.0',
                'iPhone',
            ),
        )
        self.env.oauth.requests[1].assert_properties_equal(
            method='POST',
            url='http://localhost/token?user_ip=%s&device_id=%s&device_name=%s&am_version=%s&am_version_name=%s&app_platform=%s' % (
                TEST_USER_IP,
                TEST_DEVICE_ID,
                TEST_DEVICE_NAME,
                '8.0.0',
                '8.0.0',
                'iPhone',
            ),
            post_args={
                'grant_type': 'passport_assertion',
                'client_id': TEST_X_TOKEN_CLIENT_ID,
                'client_secret': TEST_X_TOKEN_CLIENT_SECRET,
                'assertion': TEST_UID,
                'password_passed': True,
                'cloud_token': TEST_CLOUD_TOKEN,
                'passport_track_id': self.track_id,
            },
        )
        self.env.oauth.requests[2].assert_properties_equal(
            method='POST',
            url='http://localhost/token?user_ip=%s&device_id=%s&device_name=%s&am_version=%s&am_version_name=%s&app_platform=%s' % (
                TEST_USER_IP,
                TEST_DEVICE_ID,
                TEST_DEVICE_NAME,
                '8.0.0',
                '8.0.0',
                'iPhone',
            ),
            post_args={
                'grant_type': 'x-token',
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'access_token': TEST_OAUTH_X_TOKEN,
                'passport_track_id': self.track_id,
            },
        )
        self.assert_notifications_sent()
        self.env.social_binding_logger.assert_has_written([])

        profile = self.make_user_profile(
            raw_env={
                'ip': TEST_USER_IP,
                'yandexuid': None,
                'user_agent_info': {},
                'device_id': TEST_DEVICE_ID,
                'cloud_token': TEST_CLOUD_TOKEN,
                'is_mobile': True,
                'am_version': '8.0.0',
            },
        )
        self.assert_profile_written_to_auth_challenge_log(profile)

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())

        self.assert_antifraud_auth_fail_not_written()

    def test_no_fresh_profile_written_if_enter_without_challenge(self):
        """ Не передаем версию и тип устройства, в fresh профиль не будет записи"""
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response()
        )
        eq_(self.env.auth_challenge_handle_mock.call_count, 0)

    def test_password_change_required_ok(self):
        self.setup_blackbox_response(
            attributes={
                'password.forced_changing_reason': '1',
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        self.make_request()

        self.assert_notifications_not_sent()
        self.assert_antifraud_auth_fail_not_written()

    def test_custom_account_ok(self):
        self.setup_blackbox_response(
            attributes={
                'account.have_plus': '1',
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response(has_plus=True)
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_failed_to_get_second_token__network_error(self):
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        self.env.oauth.set_response_side_effect(
            '_token',
            [
                {
                    'access_token': TEST_OAUTH_X_TOKEN,
                    'token_type': 'bearer',
                    'expires_in': TEST_OAUTH_X_TOKEN_TTL,
                },
                OAuthTemporaryError(),
            ],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response(with_access_token=False)
        )

        eq_(len(self.env.oauth.requests), 3)

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())
        self.assert_antifraud_auth_fail_not_written()

    def test_failed_to_get_second_token__server_error(self):
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        self.env.oauth.set_response_side_effect(
            '_token',
            [
                {
                    'access_token': TEST_OAUTH_X_TOKEN,
                    'token_type': 'bearer',
                    'expires_in': TEST_OAUTH_X_TOKEN_TTL,
                },
                {
                    'error': 'Internal server error',
                },
            ],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response(with_access_token=False)
        )

        eq_(len(self.env.oauth.requests), 3)

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())
        self.assert_antifraud_auth_fail_not_written()

    def test_device_status_ok_failed_to_get_x_token__network_error(self):
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        self.env.oauth.set_response_side_effect(
            '_token',
            OAuthTemporaryError(),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['backend.oauth_failed'],
            **self.default_account_info()
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_failed_to_get_second_token__payment_auth_required(self):
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        self.env.oauth.set_response_side_effect(
            '_token',
            [
                {
                    'access_token': TEST_OAUTH_X_TOKEN,
                    'token_type': 'bearer',
                    'expires_in': TEST_OAUTH_X_TOKEN_TTL,
                },
                {
                    'error': 'payment_auth_pending',
                    'error_description': 'Payment auth required',
                    'payment_auth_context_id': 'context_id',
                    'payment_auth_url': 'url',
                    'payment_auth_app_ids': ['app_id1', 'app_id2'],
                },
            ],
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response(with_access_token=False, with_payment_auth=True)
        )

        eq_(len(self.env.oauth.requests), 3)

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())
        self.assert_antifraud_auth_fail_not_written()

    def test_device_status_failed_error(self):
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_side_effect(
            'device_status',
            OAuthTemporaryError(),
        )
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['captcha.required'],
            captcha_image_url='http://u.captcha.yandex.net/image?key=1p',
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_failed_to_get_x_token__server_error(self):
        self.env.oauth.set_response_value(
            '_token',
            {
                'error': 'Internal server error',
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['backend.oauth_failed'],
            **self.default_account_info()
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_password_invalid(self):
        self.setup_blackbox_response(password_status=BLACKBOX_PASSWORD_BAD_STATUS)
        resp = self.make_request()
        self.assert_error_response(resp, ['password.not_matched'])
        self.assert_antifraud_auth_fail_written('VALID/BAD/-/password.not_matched')

    def test_invalid_track_state(self):
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = None
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_already_passed(self):
        with self.track_transaction(self.track_id) as track:
            track.oauth_token_created_at = 100
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'])
        self.assert_antifraud_auth_fail_not_written()

    def test_captcha_required__from_previous_action(self):
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            captcha_image_url='http://u.captcha.yandex.net/image?key=1p',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)
        eq_(track.captcha_key, 'key')
        self.assert_antifraud_auth_fail_written('captcha_wrong_answer', _exclude=['uid'])

    def test_captcha_required__from_blackbox(self):
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.setup_blackbox_response(bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS)
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            captcha_image_url='http://u.captcha.yandex.net/image?key=1p',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        self.assert_antifraud_auth_fail_written('VALID/VALID/captcha/captcha.required')

    def test_captcha_check_ok(self):
        self.env.captcha_mock.set_response_value('check', captcha_response_check(successful=True))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True
            track.captcha_key = 'key'
        resp = self.make_request(query_args={'captcha_answer': 'answer'})
        self.assert_ok_response(
            resp,
            **self.default_response(
                avatar_url=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SECRET),
            )
        )

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_required)
        ok_(track.is_captcha_checked)
        ok_(track.is_captcha_recognized)
        self.assert_antifraud_auth_fail_not_written()

    def test_any_captcha_accepted_for_test_login_and_yandex_ip(self):
        self.env.captcha_mock.set_response_value('check', captcha_response_check(successful=False))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True
            track.captcha_key = 'key'
            track.user_entered_login = 'yndx-test'
        resp = self.make_request(query_args={'captcha_answer': 'wrong_answer'}, headers={'user_ip': TEST_YANDEX_IP})
        self.assert_ok_response(
            resp,
            **self.default_response(
                avatar_url=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SECRET),
            )
        )

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_required)
        ok_(track.is_captcha_checked)
        ok_(track.is_captcha_recognized)
        self.assert_antifraud_auth_fail_not_written()

    def test_captcha_check_failed(self):
        self.env.captcha_mock.set_response_value('check', captcha_response_check(successful=False))
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key2'))
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True
            track.captcha_key = 'key'
        resp = self.make_request(query_args={'captcha_answer': 'wrong_answer'})
        self.assert_error_response(
            resp,
            ['captcha.required'],
            captcha_image_url='http://u.captcha.yandex.net/image?key=1p',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)
        eq_(track.captcha_key, 'key2')
        self.assert_antifraud_auth_fail_written('captcha_wrong_answer', _exclude=['uid'])

    def test_captcha_failed(self):
        self.env.captcha_mock.set_response_side_effect('check', CaptchaServerError)
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True
            track.captcha_key = 'key'
        resp = self.make_request(query_args={'captcha_answer': 'answer'})
        self.assert_error_response(resp, ['backend.captcha_failed'])
        self.assert_antifraud_auth_fail_not_written()

    def test_captcha_not_shown(self):
        self.env.captcha_mock.set_response_side_effect('check', CaptchaLocateError)
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True
            track.captcha_key = 'key'
        resp = self.make_request(query_args={'captcha_answer': 'answer'})
        self.assert_error_response(resp, ['captcha.not_shown'])
        self.assert_antifraud_auth_fail_not_written()

    def test_external_or_native_action_required(self):
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = {
            'attributes': {
                'password.forced_changing_reason': '1',
            },
        }
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.setup_blackbox_response(**account_kwargs)
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='change_password',
            change_password_reason='account_hacked',
            validation_method='captcha_and_phone',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.password_hash)
        ok_(track.is_password_change)
        ok_(track.is_force_change_password)
        ok_(track.is_change_password_sms_validation_required)
        eq_(
            track.submit_response_cache,
            {
                'status': 'ok',
                'state': 'change_password',
                'change_password_reason': 'account_hacked',
                'validation_method': 'captcha_and_phone',
                'account': {
                    'uid': TEST_UID,
                    'login': TEST_LOGIN,
                    'display_login': TEST_LOGIN,
                    'display_name': {
                        'name': 'Mr_November',
                        'default_avatar': '0/key0-0',
                    },
                    'person': {
                        'firstname': u'\\u0414',
                        'lastname': u'\\u0424',
                        'language': 'ru',
                        'country': 'ru',
                        'gender': 1,
                        'birthday': '1963-05-15',
                    },
                    'is_workspace_user': False,
                    'is_yandexoid': False,
                    'is_rfc_2fa_enabled': False,
                    'is_2fa_enabled': False,
                    'public_id': TEST_PUBLIC_ID,
                },
                'number': dump_number(TEST_PHONE_NUMBER),
                'track_id': self.track_id,
                'source': 'am',
            },
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_native_action_required(self):
        self.setup_untrusted_network()

        self.setup_blackbox_response(
            password_status=BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
            allowed_second_steps=[BLACKBOX_SECOND_STEP_RFC_TOTP],
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_native'],
            state='rfc_totp',
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_email_code_required(self):
        self.setup_blackbox_response(
            password_status=BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
            allowed_second_steps=[BLACKBOX_SECOND_STEP_EMAIL_CODE],
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='email_code',
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_device_id_is_blacklisted(self):
        with self.track_transaction(self.track_id) as track:
            track.device_id = 'blacklisted'
        resp = self.make_request()
        self.assert_error_response(resp, ['password.not_matched'])
        self.assert_antifraud_auth_fail_written('device_is_blacklisted')

    def test_untrusted_network__existing_device(self):
        self.setup_untrusted_network()

        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response()
        )
        self.check_blackbox_call()
        self.assert_notifications_not_sent()
        self.assert_antifraud_auth_fail_not_written()

    def test_pdd_user_with_hint(self):
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(domain_admin='42'),
        )
        self.setup_blackbox_response(
            login='user@doma.in',
            domid='1',
            aliases={
                'pdd': 'user@doma.in',
            },
            dbfields={
                'userinfo_safe.hintq.uid': 'вопрос',
                'userinfo_safe.hinta.uid': 'ответ',
            },
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='complete_pdd',
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_strong_password_expired(self):
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            bruteforce_policy=BLACKBOX_BRUTEFORCE_PASSWORD_EXPIRED_STATUS,
            subscribed_to=[67],
            dbfields={
                'password_quality.quality.uid': 90,
            },
            crypt_password='1:pass',
            public_id=TEST_PUBLIC_ID,
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_kwargs),
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='change_password',
            change_password_reason='password_expired',
            validation_method=None,
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.password_hash)
        ok_(track.is_password_change)
        ok_(track.is_force_change_password)
        ok_(track.is_strong_password_policy_required)
        ok_(not track.is_change_password_sms_validation_required)
        self.assert_antifraud_auth_fail_not_written()

    @parameterized.expand([
        ('social', 6, 'uid-XXX', None),
        ('phonish', 10, 'phne-XXX', None),
        ('neophonish', 5, 'nphne-XXX', 'nphne-xxx'),  # маскируемся под лайтов
    ])
    def test_accounts_without_normalized_display_login(self, alias_name, alias_type, alias, display_login):
        self.setup_blackbox_response(
            aliases={
                alias_name: alias,
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response(
                primary_alias_type=alias_type,
                display_login=display_login,
                normalized_display_login=None,
            )
        )
        self.assert_antifraud_auth_fail_not_written()


default_settings_with_af_challenges = dict(
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    BLACKLISTED_AS_LIST={'AS1234'},
    DEVICE_ID_BLACKLIST={'blacklisted'},
    EMAIL_NOTIFICATIONS_DENOMINATOR=1,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    YDB_PERCENTAGE=0,
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION='7.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION_FOR_LITE='7.6.0',
    CHALLENGE_ON_HAS_CARDS_FOR_ALL_APPS=False,
    CHALLENGE_ON_HAS_CARDS_APP_IDS=set(),
    YSA_MIRROR_API_ENABLED=False,
    ALLOW_PROFILE_CHECK_FOR_MOBILE=True,
    EMAIL_CODE_CHALLENGE_ENABLED=False,
    # Ниже - вся соль этого теста
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
)


@with_settings_hosts(**default_settings_with_af_challenges)
class TestAuthByPasswordViewAntifraud(CommonAuthByPasswordTests, BaseChallengeTestCase):
    def setUp(self):
        super(TestAuthByPasswordViewAntifraud, self).setUp()
        # надо, чтобы по умолчанию все тесты, которые не просят челленджа, могли пройти проверку на сравнение
        # полного и текущего профилей
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
                'as_list_freq_6m': [('AS1', 1)],
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID,
                                             device_name=TEST_DEVICE_NAME),
        )

        # other это kwarg для api/test/views.py::mock_headers
        self.http_headers['other'] = {
            'X-Request-Id': 'request-id',
        }

        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response())

    def assert_antifraud_api_called(self, sms_2fa_on=False, with_fresh_profile=True, with_trusted_device_ids=True, **kwargs):
        assert self.env.antifraud_api.requests
        request = self.env.antifraud_api.requests[0]

        assert request.post_args
        request_data = json.loads(request.post_args)

        params = AntifraudScoreParams.default()
        params.populate_from_headers(mock_headers(**self.http_headers))
        expected_features = params.as_dict()
        expected_features.update({
            'available_challenges': ['email_hint'],
            'as_list_freq': {'AS1': 1},
            'surface': 'mobile_password',
            'device_id': TEST_DEVICE_ID,
            'device_name': TEST_DEVICE_NAME,
            'external_id': 'track-' + self.track_id,
            'has_cloud_token': True,
            'input_login': TEST_LOGIN,
            'is_mobile': True,
            'known_device': 'new',
            'lah_uids': [],
            'profile_loaded': True,
            'sms_2fa': sms_2fa_on,
            'uid': TEST_UID,
        })
        if with_fresh_profile:
            fresh_profile = self.make_user_profile(raw_env=TEST_ENV_PROFILE)
            expected_features['fresh_profiles'].append({
                'AS': fresh_profile.AS_list,
                'am_version': fresh_profile.am_version,
                'browser_id': fresh_profile.browser_id,
                'city_id': fresh_profile.city_id,
                'country_id': fresh_profile.country_id,
                'device_id': fresh_profile.device_id,
                'has_cloud_token': bool(fresh_profile.cloud_token),
                'is_mobile': fresh_profile.is_mobile,
                'os_id': fresh_profile.os_id,
                'yandexuid_timestamp': fresh_profile.yandexuid_timestamp,
                'ip': TEST_ENV_PROFILE['ip'],
                'timestamp': fresh_profile.timestamp,
            })
        if with_trusted_device_ids:
            expected_features['trusted_device_ids'].append(TEST_DEVICE_ID)

        expected_features.update(**kwargs)

        assert request_data == expected_features

    def test_antifraud_allow(self):
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '6.0.0'
            track.device_os_id = 'iPhone'
            track.device_application = 'ru.yandex.something'

        resp = self.make_request()
        self.assert_ok_response(resp, check_all=False)
        self.assert_antifraud_api_called(
            account_manager_version='6.0.0',
            am_version='6.0.0',
            device_application='ru.yandex.something',
            device_os_id='iPhone',
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_challenge_required='0',
                af_is_auth_forbidden='0',
                af_reason='some-reason',
                af_tags='',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='6.0.0',
                ).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                ).as_json,
                ufo_distance='0',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_antifraud_challenge(self):
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '6.0.0'
            track.device_os_id = 'iPhone'
            track.device_application = 'ru.yandex.something'

        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            tags=['call', 'email_hint'],
        ))
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )
        self.assert_antifraud_api_called(
            account_manager_version='6.0.0',
            am_version='6.0.0',
            device_application='ru.yandex.something',
            device_os_id='iPhone',
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_challenge_required='1',
                af_is_auth_forbidden='0',
                af_reason='some-reason',
                af_tags='call email_hint',
                decision_source='antifraud_api',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='6.0.0',
                ).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                ).as_json,
                ufo_distance='0',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_antifraud_test_login_forced_challenge(self):
        # Если приходит тестовый пользователь, то не ходим в антифрод, а тэги берем из трека,
        # предварительно в треке выставляются тэги антифрода в ручке internal/track.
        # В даннном случае пользователю заказали КВКО челлендж, который доступен только через тэги антифрода, если тэгов нету будет каптча.
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '6.0.0'
            track.device_os_id = 'iPhone'
            track.antifraud_tags = ['question']

        self.setup_blackbox_response(
            login=TEST_YANDEX_TEST_LOGIN,
            emails=None,
            phones=None,
            attributes={'account.force_challenge': '1'},
            dbfields={
                'userinfo_safe.hintq.uid': 'вопрос',
                'userinfo_safe.hinta.uid': 'ответ',
            },
        )

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        # нет записи о походе в антифрод
        eq_(len(self.env.antifraud_api.requests), 0)
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                decision_source='forced_challenge',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='6.0.0',
                ).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                ).as_json,
                ufo_distance='0',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_antifraud_test_only_question_challenge(self):
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '6.0.0'
            track.device_os_id = 'iPhone'

        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            tags=['question'],
        ))

        self.setup_blackbox_response(
            emails=None,
            phones=None,
            dbfields={
                'userinfo_safe.hintq.uid': 'вопрос',
                'userinfo_safe.hinta.uid': 'ответ',
            },
        )

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.assert_antifraud_api_called(
            account_manager_version='6.0.0',
            am_version='6.0.0',
            device_os_id='iPhone',
            available_challenges=['question'],
        )
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_challenge_required='1',
                af_is_auth_forbidden='0',
                af_reason='some-reason',
                af_tags='question',
                decision_source='antifraud_api',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='6.0.0',
                ).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                ).as_json,
                ufo_distance='0',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_antifraud_test_only_email_code_challenge_to_lite_account(self):
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '6.0.0'
            track.device_os_id = 'iPhone'

        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            tags=['email_code'],
        ))
        login = TEST_LOGIN + '@domain.tld'
        self.setup_blackbox_response(
            aliases={
                'lite': login,
            },
            login=login,
        )

        _settings = dict(default_settings_with_af_challenges)
        _settings['EMAIL_CODE_CHALLENGE_ENABLED'] = True
        _settings['EMAIL_CODE_CHALLENGE_ENABLED_DENOMINATOR'] = 1
        with settings_context(
            **_settings
        ):
            resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.assert_antifraud_api_called(
            account_manager_version='6.0.0',
            am_version='6.0.0',
            device_os_id='iPhone',
            available_challenges=['email_code'],
        )
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_challenge_required='1',
                af_is_auth_forbidden='0',
                af_reason='some-reason',
                af_tags='email_code',
                decision_source='antifraud_api',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='6.0.0',
                ).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                ).as_json,
                ufo_distance='0',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_antifraud_challenge_fresh_account_untrusted_network(self):
        self.setup_untrusted_network()
        reg_time = datetime.now() - timedelta(seconds=settings.PROFILE_TRIAL_PERIOD - 500)
        self.setup_blackbox_response(
            dbfields={
                'userinfo.reg_date.uid': reg_time.strftime('%Y-%m-%d %H:%M:%S'),
            },
        )
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '6.0.0'
            track.device_os_id = 'iPhone'
            track.device_application = 'ru.yandex.something'

        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            tags=['sms', 'email_hint'],
        ))
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )
        self.assert_antifraud_api_called(
            account_manager_version='6.0.0',
            am_version='6.0.0',
            device_application='ru.yandex.something',
            device_os_id='iPhone',
            reg_date=reg_time.strftime('%Y-%m-%d %H:%M:%S'),
            AS=[],
            city_id=102630,
            country_id=84,
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_challenge_required='1',
                af_is_auth_forbidden='0',
                af_reason='some-reason',
                af_tags='sms email_hint',
                decision_source='antifraud_api',
                is_challenge_required='1',
                is_fresh_account='1',
                is_fresh_profile_passed='0',
                is_full_profile_passed='0',
                ufo_distance='100',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='6.0.0',
                ).as_json,
                full_profile_AS_list='AS1',
                ufo_closest=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                ).as_json,
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_antifraud_need_unavailable_challenge(self):
        # Пользователю недоступен звонок, а это единственное требование АФ.
        # Поэтому пропускаем пользователя без челленжа, а в лог пишем о некорректном ответе АФ
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            tags=['call'],
        ))
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '6.0.0'
            track.device_os_id = 'iPhone'
            track.device_application = 'ru.yandex.something'

        resp = self.make_request()
        self.assert_ok_response(resp, check_all=False)
        self.assert_antifraud_api_called(
            account_manager_version='6.0.0',
            am_version='6.0.0',
            device_application='ru.yandex.something',
            device_os_id='iPhone',
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_challenge_required='1',
                af_is_auth_forbidden='0',
                af_reason='some-reason',
                af_tags='call',
                decision_source='antifraud_api',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='6.0.0',
                ).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                ufo_distance='0',
            ),
            self.env.statbox.entry(
                'skip_challenge',
                decision_source=DecisionSource.ANTIFRAUD_INVALID_TAGS,
                challenge_reason=DecisionSource.ANTIFRAUD_API,
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ['challenges_skipped'],
            {'challenge.skipped.decision_source.antifraud_invalid_tags.rps_dmmm': 1},
        )

    def test_antifraud_challenge_sms2fa_user(self):
        # пользователь с sms2fa идет с известного девайса. АФ требует челлендж, значит покажем его.
        # без требования АФ нет челленджа
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            tags=['sms'],
        ))

        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = dict(
            attributes={
                'account.sms_2fa_on': '1',
            },
            emails=None,
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)

        self.setup_blackbox_response(**account_kwargs)
        self.setup_profile_response(
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
            },
            add_fresh_profile=True,
            with_device_id=True,
        )
        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '6.0.0'
            track.device_os_id = 'iPhone'
            track.device_application = 'ru.yandex.something'

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.assert_antifraud_api_called(
            sms_2fa_on=True,
            account_manager_version='6.0.0',
            am_version='6.0.0',
            available_challenges=['phone_hint', 'phone_confirmation'],
            device_application='ru.yandex.something',
            device_os_id='iPhone',
            as_list_freq={},
            known_device='old'
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='ALLOW',
                af_is_challenge_required='1',
                af_is_auth_forbidden='0',
                af_reason='some-reason',
                af_tags='sms',
                decision_source='antifraud_api',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='6.0.0',
                ).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                ufo_distance='0',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ['challenges_skipped'],
            {'challenge.skipped.decision_source.antifraud_invalid_tags.rps_dmmm': 0},
        )

    def test_antifraud_deny(self):
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            action=ScoreAction.DENY,
        ))
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['password.not_matched'],
        )
        self.assert_antifraud_api_called(
            available_challenges=[],
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='DENY',
                af_is_challenge_required='0',
                af_is_auth_forbidden='1',
                af_reason='some-reason',
                af_tags='',
                decision_source='antifraud_api',
                # boilerplate
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                ufo_distance='0',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.ANTIFRAUD_API,
                email_sent='0',
                was_online_sec_ago=TimeSpan(1),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_antifraud_deny_fresh_account(self):
        reg_time = datetime.now() - timedelta(seconds=settings.PROFILE_TRIAL_PERIOD - 500)
        self.setup_blackbox_response(
            dbfields={
                'userinfo.reg_date.uid': reg_time.strftime('%Y-%m-%d %H:%M:%S'),
            },
        )
        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            action=ScoreAction.DENY,
        ))
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['password.not_matched'],
        )
        self.assert_antifraud_api_called(
            available_challenges=[],
            reg_date=reg_time.strftime('%Y-%m-%d %H:%M:%S'),
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                af_action='DENY',
                af_is_challenge_required='0',
                af_is_auth_forbidden='1',
                af_reason='some-reason',
                af_tags='',
                decision_source='antifraud_api',
                is_fresh_account='1',
                # boilerplate
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                full_profile_AS_list='AS1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                ufo_distance='0',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.ANTIFRAUD_API,
                email_sent='0',
                was_online_sec_ago=TimeSpan(1),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_antifraud_test_login(self):
        self.setup_blackbox_response(
            login='yndx-gladnik',
        )
        resp = self.make_request()
        self.assert_ok_response(resp, check_all=False)
        assert not self.env.antifraud_api.requests

    def test_antifraud_for_sms_2fa__deny(self):
        self.setup_blackbox_response(
            attributes={
                'account.sms_2fa_on': '1',
            },
        )
        self.setup_profile_response(
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
                'as_list_freq_6m': [('AS1', 1)],
            },
            add_fresh_profile=False,
        )

        self.env.antifraud_api.set_response_value_without_method(antifraud_score_response(
            action=ScoreAction.DENY,
        ))
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['password.not_matched'],
        )
        self.assert_antifraud_api_called(sms_2fa_on=True, with_fresh_profile=False, with_trusted_device_ids=False, available_challenges=['email_hint'])

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'sms_2fa_challenge',
                af_action='DENY',
                af_is_challenge_required='0',
                af_is_auth_forbidden='1',
                af_reason='some-reason',
                af_tags='',
                decision_source='antifraud_api',
                is_challenge_required='1',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                ).as_json,
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()


@with_settings_hosts(
    AM_ANDROID_CHALLENGE_MIN_VERSION='7.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION_FOR_LITE='7.6.0',
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    ANTIFRAUD_ON_CHALLENGE_ENABLED=True,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    BLACKLISTED_AS_LIST={'AS1234'},
    CHALLENGE_ON_HAS_CARDS_APP_IDS=set(),
    CHALLENGE_ON_HAS_CARDS_FOR_ALL_APPS=False,
    DEVICE_ID_BLACKLIST={'blacklisted'},
    EMAIL_NOTIFICATIONS_DENOMINATOR=1,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    MOBILEPROXY_CONSUMER='dev',
    OAUTH_RETRIES=1,
    OAUTH_URL='http://localhost/',
    UFO_API_RETRIES=1,
    UFO_API_URL='http://localhost/',
    YDB_PERCENTAGE=0,
    ALLOW_PROFILE_CHECK_FOR_MOBILE=True,
    YSA_MIRROR_API_ENABLED=True,  # вся суть этого тесткейса в этом параметре!
)
class TestAuthByPasswordViewYsaMirror(CommonAuthByPasswordTests, BaseChallengeTestCase):
    def setUp(self):
        super(TestAuthByPasswordViewYsaMirror, self).setUp()
        # надо, чтобы по умолчанию все тесты, которые не просят челленджа, могли пройти проверку на сравнение
        # полного и текущего профилей
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID,
                                             device_name=TEST_DEVICE_NAME),
        )

        # other это kwarg для api/test/views.py::mock_headers
        self.http_headers['other'] = {
            'X-Request-Id': 'request-id',
        }

        self.env.antifraud_api.set_response_side_effect('score', [antifraud_score_response()])

        self.env.ysa_mirror.set_response_side_effect(
            'check_client_by_requestid_v2',
            [
                ysa_mirror_ok_resolution_response(),
            ],
        )

    def assert_antifraud_api_called(self, traffic_fp=None):
        assert self.env.antifraud_api.requests
        request = self.env.antifraud_api.requests[0]
        assert request.post_args
        request_data = json.loads(request.post_args)
        assert request_data.get('traffic_fp') == traffic_fp

    def test_ysa_mirror_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp, check_all=False)
        assert self.env.ysa_mirror.requests

        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'ysa_mirror',
                    status='ok',
                    request_id='request-id',
                ),
            ],
        )

        track = self.track_manager.read(self.track_id)
        self.assertEqual(track.ysa_mirror_resolution, TEST_YSA_MIRROR_RESOLUTION1.to_base64())

        self.assert_antifraud_api_called(traffic_fp=TEST_YSA_MIRROR_RESOLUTION1.to_base64())

    def test_ysa_mirror_no_resolution(self):
        self.env.ysa_mirror.set_response_side_effect(
            'check_client_by_requestid_v2',
            [
                ysa_mirror_no_resolution_response(),
            ],
        )

        resp = self.make_request()

        self.assert_ok_response(resp, check_all=False)
        assert self.env.ysa_mirror.requests

        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'ysa_mirror',
                    status='ok',
                    request_id='request-id',
                ),
            ],
        )

        track = self.track_manager.read(self.track_id)
        self.assertIsNone(track.ysa_mirror_resolution)

        self.assert_antifraud_api_called()

    def test_ysa_mirror_temporary_error(self):
        self.env.ysa_mirror.set_response_side_effect('check_client_by_requestid_v2', YsaMirrorTemporaryError())
        resp = self.make_request()
        self.assert_ok_response(resp, check_all=False)
        assert self.env.ysa_mirror.requests

        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'ysa_mirror',
                    status='error',
                    error='YsaMirrorTemporaryError',
                    request_id='request-id',
                ),
            ],
        )

        self.assert_antifraud_api_called()

    def test_ysa_mirror_permanent_error(self):
        self.env.ysa_mirror.set_response_side_effect('check_client_by_requestid_v2', YsaMirrorPermanentError())
        resp = self.make_request()
        self.assert_ok_response(resp, check_all=False)
        assert self.env.ysa_mirror.requests

        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry(
                    'ysa_mirror',
                    status='error',
                    error='YsaMirrorPermanentError',
                    request_id='request-id',
                ),
            ],
        )

        self.assert_antifraud_api_called()


@with_settings_hosts(
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    BLACKLISTED_AS_LIST={'AS1234'},
    DEVICE_ID_BLACKLIST={'blacklisted'},
    EMAIL_NOTIFICATIONS_DENOMINATOR=1,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    YDB_PERCENTAGE=0,
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION='7.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION_FOR_LITE='7.6.0',
    CHALLENGE_ON_HAS_CARDS_FOR_ALL_APPS=False,
    CHALLENGE_ON_HAS_CARDS_APP_IDS=set(),
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
    YSA_MIRROR_API_ENABLED=True,  # вся суть этого тесткейса в этом параметре!
    MOBILEPROXY_CONSUMER='some-other-consumer',  # вся суть этого тесткейса в этом параметре!
    ALLOW_PROFILE_CHECK_FOR_MOBILE=True,
)
class TestAuthByPasswordViewYsaMirrorNotFromMobileproxy(CommonAuthByPasswordTests, BaseChallengeTestCase):
    def setUp(self):
        super(TestAuthByPasswordViewYsaMirrorNotFromMobileproxy, self).setUp()
        # надо, чтобы по умолчанию все тесты, которые не просят челленджа, могли пройти проверку на сравнение
        # полного и текущего профилей
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID,
                                             device_name=TEST_DEVICE_NAME),
        )

        # other это kwarg для api/test/views.py::mock_headers
        self.http_headers['other'] = {
            'X-Request-Id': 'request-id',
        }

        # для всех тестов ysa api доступно и работает
        self.env.ysa_mirror.set_response_side_effect(
            'check_client_by_requestid_v2',
            [
                ysa_mirror_ok_resolution_response(),
            ],
        )

    def test_ysa_mirror_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp, check_all=False)
        assert not self.env.ysa_mirror.requests


@with_settings_hosts(
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    BLACKLISTED_AS_LIST={'AS1234'},
    DEVICE_ID_BLACKLIST={'blacklisted'},
    EMAIL_NOTIFICATIONS_DENOMINATOR=1,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    YDB_PERCENTAGE=0,
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION='7.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION_FOR_LITE='7.6.0',
    CHALLENGE_ON_HAS_CARDS_FOR_ALL_APPS=False,
    CHALLENGE_ON_HAS_CARDS_APP_IDS={'ru.yandex.test'},
    YSA_MIRROR_API_ENABLED=False,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
    ALLOW_PROFILE_CHECK_FOR_MOBILE=True,
)
class TestAuthByPasswordViewWithChallengesOnPerAppHasCard(CommonAuthByPasswordTests, BaseChallengeTestCase):
    def setUp(self):
        super(TestAuthByPasswordViewWithChallengesOnPerAppHasCard, self).setUp()
        # надо, чтобы по умолчанию все тесты, которые не просят челленджа, могли пройти проверку на сравнение
        # полного и текущего профилей
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
            },
        )

    def test_ok_per_app_has_cards_app_no_match(self):
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'has_cards': True,
                'as_list_freq_3m': [('AS1', 1)],
            },
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'
            track.device_application = 'ru.yandex.test2'

        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID,
                                             device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()
        self.assert_ok_response(resp, check_all=False)

    def test_ok_per_app_has_cards_app_matches(self):
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'has_cards': True,
                'as_list_freq_3m': [('AS1', 1)],
            },
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'
            track.device_application = 'ru.yandex.test'

        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID,
                                             device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.assert_notifications_sent(is_challenged=True)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance='0',
                is_fresh_profile_passed='1',
                is_challenge_required='1',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                decision_source=DecisionSource.HAS_CARDS,
                full_profile_AS_list='AS1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.HAS_CARDS,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()


@with_settings_hosts(
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    BLACKLISTED_AS_LIST={'AS1234'},
    DEVICE_ID_BLACKLIST={'blacklisted'},
    EMAIL_NOTIFICATIONS_DENOMINATOR=1,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    YDB_PERCENTAGE=0,
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION='7.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION_FOR_LITE='7.6.0',
    CHALLENGE_ON_HAS_CARDS_FOR_ALL_APPS=True,
    YSA_MIRROR_API_ENABLED=False,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
    ALLOW_PROFILE_CHECK_FOR_MOBILE=True,
)
class TestAuthByPasswordViewWithChallengesOnHasCard(CommonAuthByPasswordTests, BaseChallengeTestCase):
    def setUp(self):
        super(TestAuthByPasswordViewWithChallengesOnHasCard, self).setUp()
        # надо, чтобы по умолчанию все тесты, которые не просят челленджа, могли пройти проверку на сравнение
        # полного и текущего профилей
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
            },
        )

    def test_ok_fresh_profile_is_ok_is_new_device_has_cards(self):
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'has_cards': True,
                'as_list_freq_3m': [('AS1', 1)],
            },
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.assert_notifications_sent(is_challenged=True)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance='0',
                is_fresh_profile_passed='1',
                is_challenge_required='1',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                decision_source=DecisionSource.HAS_CARDS,
                full_profile_AS_list='AS1',
                is_full_profile_passed='1',
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.HAS_CARDS,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_fresh_profile_is_ok_is_new_device_no_cards(self):
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                # !! тут нету has_cards !!
                'as_list_freq_3m': [('AS1', 1)],
            },
        )
        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_ok_response(resp, check_all=False)


default_settings_with_challenges = dict(
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    BLACKLISTED_AS_LIST={'AS1234'},
    DEVICE_ID_BLACKLIST={'blacklisted'},
    EMAIL_NOTIFICATIONS_DENOMINATOR=1,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    YDB_PERCENTAGE=0,
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION='7.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION_FOR_LITE='7.6.0',
    YSA_MIRROR_API_ENABLED=False,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
    MAGNITOLA_MODELS=['magnitola_model'],
    MAGNITOLA_APP_IDS=['magnitola_app_id'],
    ALLOW_PROFILE_CHECK_FOR_MOBILE=True,
)


@with_settings_hosts(**default_settings_with_challenges)
class TestAuthByPasswordViewWithChallenges(CommonAuthByPasswordTests, BaseChallengeTestCase):
    def setUp(self):
        super(TestAuthByPasswordViewWithChallenges, self).setUp()
        # надо, чтобы по умолчанию все тесты, которые не просят челленджа, могли пройти проверку на сравнение
        # полного и текущего профилей
        self.setup_profile_response(full_profile={
            'as_list_freq_3m': [('AS1', 1)],
        })

    def test_sms_2fa_on__new_device(self):
        self.setup_blackbox_response(
            attributes={
                'account.sms_2fa_on': '1',
            },
        )
        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_sms_2fa_on__known_device(self):
        self.setup_blackbox_response(
            attributes={
                'account.sms_2fa_on': '1',
            },
        )
        self.setup_profile_response(
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
            },
            add_fresh_profile=True,
            with_device_id=True,
        )
        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response()
        )

    def test_untrusted_network__oauth_failed(self):
        self.setup_untrusted_network()

        self.env.oauth.set_response_side_effect(
            'device_status',
            OAuthTemporaryError,
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iphone'

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )
        self.check_blackbox_call()
        self.assert_antifraud_auth_fail_not_written()

    def test_ok_fresh_profile_is_ok_is_new_device(self):
        self.setup_profile_response(add_fresh_profile=True)
        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response()
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance='0',
                is_challenge_required='0',
                is_fresh_profile_passed='1',  # fresh профиль сказал, что ОК. Мнение full профиля уже не интересно
                is_full_profile_passed='0',
                full_profile_AS_list='-',
                captcha_reason='new_challenge_not_available_for_account',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                decision_source=DecisionSource.UFO,
                ufo_status='1',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='0',
            ),
            self.env.statbox.entry(
                'tokens_issued',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_all_is_ok__is_new_device_failed(self):
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
            },
        )
        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_side_effect(
            'device_status',
            OAuthTemporaryError,
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iphone'
            track.device_name = TEST_DEVICE_NAME

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.assert_notifications_sent(is_challenged=True)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                decision_source=DecisionSource.DEVICE_STATUS_FAILED,
                is_challenge_required='1',
                is_fresh_profile_passed='1',
                is_full_profile_passed='1',
                full_profile_AS_list='AS1',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                ufo_distance='0',
                ufo_status='1',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.DEVICE_STATUS_FAILED,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_ufo_api_failed(self):
        """
        UfoApi вернуло ошибку => просим челлендж
        """

        self.env.ufo_api.set_response_side_effect(
            'profile',
            UfoApiTemporaryError,
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.assert_notifications_sent(is_challenged=True)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance='0',
                is_challenge_required='1',
                is_fresh_profile_passed='0',
                is_full_profile_passed='0',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                decision_source=DecisionSource.UFO_FAILED,
                ufo_status='0',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.UFO_FAILED,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_ufo_api_failed_and_profile_is_broken(self):
        """
        UfoApi вернуло ошибку и счётчик поломок перегрет => не просим челлендж
        """

        self.env.ufo_api.set_response_side_effect(
            'profile',
            UfoApiTemporaryError,
        )

        # греем счётчик
        while not is_profile_broken():
            is_profile_broken()

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response()
        )

        self.assert_notifications_sent()
        self.assert_ufo_api_called(call_count=2)  # не смогли получить в первый раз, пришлось перезапросить
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance='0',  # не смогли измерить
                is_challenge_required='0',
                is_fresh_profile_passed='0',
                is_full_profile_passed='0',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                decision_source=DecisionSource.UFO_FAILED,
                ufo_status='0',  # не смогли сходить за профилем
                challenge_reason=DecisionSource.UFO_FAILED,
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='0',
            ),
            self.env.statbox.entry(
                'tokens_issued',
                am_version='5.0.0',
                am_version_name='5.0.0',
                app_platform='iPhone',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    @parameterized.expand([
        ('5.0.0', 'iPhone'),
        ('2019.09.2+#3263', u'iPhone+Hãĉĸ_ŧēşt+1.03+root+(REL)'),  # PASSP-25536
    ])
    def test_profile_model_full_profile_AS_match(self, app_version, app_platform):
        # Челлендж не запросили, потому что AS совпадают в полном профиле
        self.setup_profile_response(
            distant_fresh=True,
            full_profile={
                'as_list_freq_3m': [('AS1', 1)],
            },
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = app_version
            track.device_os_id = app_platform

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_ok_response(resp, check_all=False)

        expected_am_ver = '.'.join([str(x) for x in parse_am_version(track.account_manager_version)])
        ufo_profile_checked_log = dict(
            ufo_distance=str(EnvDistance.Max),
            is_challenge_required='0',
            is_fresh_profile_passed='0',
            current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version=expected_am_ver).as_json,
            ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE_DISTANT).as_json,
            decision_source=DecisionSource.UFO,
            full_profile_AS_list='AS1',
            is_full_profile_passed='1',
        )
        if app_version != '5.0.0':
            ufo_profile_checked_log['captcha_reason'] = 'new_challenge_not_available_for_account'
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                **ufo_profile_checked_log
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='0',
            ),
            self.env.statbox.entry(
                'tokens_issued',
                am_version=app_version,
                am_version_name=app_version,
                app_platform=app_platform,
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    @parameterized.expand([
        (
            {  # id текущей AS будет сравниваться с AS10, AS20, AS30, AS40
                'as_list_freq_3m': [('AS10', 1), ('AS20', 1)],
                'su_as_list_freq_3m': [('AS30', 1), ('AS40', 1)],
            },
            'AS10,AS20,AS30,AS40',
        ),
        (
            {  # ... будет сравниваться с AS10, AS20
                'as_list_freq_3m': [('AS10', 1), ('AS20', 1)],
            },
            'AS10,AS20',
        ),
        (
            {  # ... будет  сравниваться с AS30, AS40
                'su_as_list_freq_3m': [('AS30', 1), ('AS40', 1)],
            },
            'AS30,AS40',
        ),
        ({}, ''),  # пустой профиль - тоже челлендж
    ])
    def test_profile_model_full_profile_AS_mismatch(self, full_profile, statbox_AS_list):
        # Челлендж запросили, потому что AS разошлись в полном и текущем профилях

        self.setup_profile_response(distant_fresh=True, full_profile=full_profile)

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.assert_notifications_sent(is_challenged=True)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance='100',  # в полный профиль ходим, если расхождение в fresh профиле, и вот оно расхождение
                is_fresh_profile_passed='0',  # проверка fresh профиля не прошла
                is_challenge_required='1',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                decision_source=DecisionSource.MOBILE_FULL_PROFILE,
                full_profile_AS_list=statbox_AS_list or '-',
                is_full_profile_passed='0',
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE_DISTANT).as_json,
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.MOBILE_FULL_PROFILE,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_model_old_device_always_passes(self):
        """
        Челлендж не запросили, потому что устройство старое и известное
        """
        self.setup_profile_response(distant_fresh=True)

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='test', device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response()
        )

        self.assert_notifications_not_sent()
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance=str(EnvDistance.High),
                is_challenge_required='0',  # не требуется челлендж, потому что старое устройство
                is_fresh_profile_passed='0',  # нет, не прошли из-за разных стран
                is_full_profile_passed='0',  # нет, не прошли, потому что полного профиля нету
                full_profile_AS_list='-',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE_DISTANT).as_json,
                decision_source=DecisionSource.MOBILE_KNOWN_DEVICE,
                challenge_reason=DecisionSource.MOBILE_FULL_PROFILE,
            ),
            self.env.statbox.entry(
                'tokens_issued',
                am_version='5.0.0',
                am_version_name='5.0.0',
                app_platform='iPhone',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_full_profile_check_not_passed_but_am_smartlock_passed(self):
        """
        Челлендж должен быть показан, но не показан из-за того, что пришли из смартлока АМ
        """
        self.setup_profile_response(distant_fresh=True)

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        _settings = dict(default_settings_with_challenges)
        _settings['CHECK_AVATARS_SECRETS_DENOMINATOR'] = 0
        with settings_context(
            **_settings
        ):
            resp = self.make_request(query_args={'password_source': 'autologin'})

        self.assert_ok_response(
            resp,
            **self.default_response()
        )

        self.assert_notifications_sent(is_challenged=False)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance=str(EnvDistance.High),
                is_challenge_required='0',  # не требуется челлендж, потому что старое устройство
                is_fresh_profile_passed='0',  # нет, не прошли из-за разных стран
                is_full_profile_passed='0',  # нет, не прошли, потому что полного профиля нету
                full_profile_AS_list='-',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE_DISTANT).as_json,
                decision_source=DecisionSource.AM_SMARTLOCK,
                mobile_password_source=MobilePasswordSource.AUTO_LOGIN,
                challenge_reason=DecisionSource.MOBILE_FULL_PROFILE,
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='0',
            ),
            self.env.statbox.entry(
                'tokens_issued',
                am_version='5.0.0',
                am_version_name='5.0.0',
                app_platform='iPhone',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_full_profile_check_not_passed_but_smartlock_and_unknown_AM(self):
        """
        Челлендж должен быть показан, даже если пришли из смартлока, потому что неизвестная версия АМ
        """
        self.setup_profile_response(distant_fresh=True)

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        _settings = dict(default_settings_with_challenges)
        _settings['CHECK_AVATARS_SECRETS_DENOMINATOR'] = 0
        with settings_context(
            **_settings
        ):
            resp = self.make_request(query_args={'password_source': 'autologin'})

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                # порог: High это расхождение страны, а Moderate это расхождение в браузерах (константа для мобилок)
                ufo_distance=str(EnvDistance.High),
                is_challenge_required='1',
                is_fresh_profile_passed='0',  # нет, не прошли из-за разных стран
                is_full_profile_passed='0',  # нет, не прошли из-за отсутствия полного профиля
                decision_source=DecisionSource.AM_SMARTLOCK_FRAUD,
                full_profile_AS_list='-',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE).as_json,
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE_DISTANT).as_json,
                mobile_password_source='autologin',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.AM_SMARTLOCK_FRAUD,
                was_online_sec_ago=TimeSpan(0),
                mobile_password_source='autologin',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_profile_full_profile_check_not_passed__diff_AS(self):
        """
        Челлендж показан из-за того, что АС не совпала с fresh и полным профилем
        """
        self.setup_profile_response(distant_fresh=True)

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.password_hash)
        ok_(not track.is_password_change)
        ok_(not track.is_force_change_password)
        ok_(not track.is_change_password_sms_validation_required)

        self.assert_notifications_sent(is_challenged=True)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                # порог: High это расхождение страны, а Moderate это расхождение в браузерах (константа для мобилок)
                ufo_distance=str(EnvDistance.High),
                is_challenge_required='1',
                is_fresh_profile_passed='0',  # нет, не прошли из-за разных стран
                is_full_profile_passed='0',  # нет, не прошли из-за отсутствия полного профиля
                decision_source=DecisionSource.MOBILE_FULL_PROFILE,
                full_profile_AS_list='-',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                ufo_closest=self.make_user_profile(raw_env=TEST_ENV_PROFILE_DISTANT).as_json,
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.MOBILE_FULL_PROFILE,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_untrusted_network__test_login(self):
        """Челлендж показан даже для тестового аккаунта, потому что вход из AS из чёного списка"""
        self.setup_untrusted_network()
        self.setup_blackbox_response(
            login='yndx-gladnik',
        )
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test',
                                             device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_untrusted_network__fresh_account(self):
        """Челлендж показан даже для свежего аккаунта, потому что вход из AS из чёрного списка"""
        self.setup_untrusted_network()
        reg_time = datetime.now() - timedelta(seconds=settings.PROFILE_TRIAL_PERIOD - 500)
        self.setup_blackbox_response(
            dbfields={
                'userinfo.reg_date.uid': reg_time.strftime('%Y-%m-%d %H:%M:%S'),
            },
        )
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test',
                                             device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance=str(EnvDistance.Max),
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version='5.0.0').as_json,
                is_challenge_required='1',
                is_fresh_account='1',
                is_fresh_profile_passed='0',
                decision_source=DecisionSource.BLACKLISTED_AS,
                is_full_profile_passed='0',
                full_profile_AS_list='AS1',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.BLACKLISTED_AS,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    @parameterized.expand([
        # платформа, версия, лайт / не лайт пользователь
        ('iPhone', '5.0.0', False),
        ('iPhone', '5.0', False),
        ('iPhone', '7.0.0', False),
        ('Android 9 (REL)', '7.0.0', False),
        ('iPhone', '5.0.0', True),
        ('iPhone', '5.0', True),
        ('Android 9 (REL)', '7.6.0', True),
    ])
    def test_untrusted_network__new_device__can_use_new_challenge(self, platform, version, is_lite):
        # Челлендж показан из-за того, что новое устройство и недоверенная сеть
        self.setup_untrusted_network()

        login = TEST_LOGIN + '@domain.tld' if is_lite else TEST_LOGIN
        if is_lite:
            self.setup_blackbox_response(
                aliases={
                    'lite': login,
                },
                login=login,
                **build_phone_secured(
                    1,
                    TEST_PHONE_NUMBER.e164,
                    is_default=False,
                )
            )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = version
            track.device_os_id = platform

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test',
                                             device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.password_hash)
        ok_(not track.is_password_change)
        ok_(not track.is_force_change_password)
        ok_(not track.is_change_password_sms_validation_required)
        eq_(
            track.submit_response_cache,
            {
                'status': 'ok',
                'state': 'auth_challenge',
                'account': {
                    'uid': TEST_UID,
                    'login': login,
                    'display_login': login,
                    'display_name': {
                        'name': 'Mr_November',
                        'default_avatar': '0/key0-0',
                    },
                    'person': {
                        'firstname': u'\\u0414',
                        'lastname': u'\\u0424',
                        'language': 'ru',
                        'country': 'ru',
                        'gender': 1,
                        'birthday': '1963-05-15',
                    },
                    'is_workspace_user': False,
                    'is_yandexoid': False,
                    'is_rfc_2fa_enabled': False,
                    'is_2fa_enabled': False,
                    'public_id': TEST_PUBLIC_ID,
                },
                'track_id': self.track_id,
                'source': 'am',
            },
        )

        expected_am_ver = '.'.join([str(x) for x in parse_am_version(track.account_manager_version)])

        self.assert_notifications_sent(is_challenged=True, login=login, is_lite=is_lite)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                ufo_distance=str(EnvDistance.Max),
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version=expected_am_ver).as_json,
                is_challenge_required='1',
                is_fresh_profile_passed='0',
                decision_source=DecisionSource.BLACKLISTED_AS,
                is_full_profile_passed='0',
                full_profile_AS_list='AS1',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.BLACKLISTED_AS,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test__cannot_use_new_challenge__captcha_passed(self):
        self.setup_untrusted_network()
        version = '4.9.9'
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = version
            track.device_os_id = 'iPhone'
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test',
                                             device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            skip=['avatar_url'],
            **self.default_response()
        )

        self.assert_notifications_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'skip_challenge',
                decision_source=DecisionSource.CAPTCHA_ALREADY_PASSED,
                captcha_reason='new_challenge_not_available_for_account'
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='0',
            ),
            self.env.statbox.entry(
                'tokens_issued',
                am_version=version,
                am_version_name=version,
                app_platform='iPhone',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test__new_challenge_not_available_for_account__captcha_passed(self):
        self.setup_untrusted_network()
        self.setup_blackbox_response(
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test',
                                             device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            skip=['avatar_url'],
            **self.default_response()
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'skip_challenge',
                decision_source=DecisionSource.CAPTCHA_ALREADY_PASSED,
                captcha_reason='new_challenge_not_available_for_account'
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='0',
            ),
            self.env.statbox.entry(
                'tokens_issued',
                am_version='5.0.0',
                am_version_name='5.0.0',
                app_platform='iPhone',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test__shared_account(self):
        account_kwargs = {
            'attributes': {
                'account.is_shared': True,
            },
        }
        self.setup_blackbox_response(**account_kwargs)

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID,
                                             device_name=TEST_DEVICE_NAME),
        )
        with self.track_transaction(self.track_id) as track:
            # известный девайс и версия которая поддерживает челенджи
            track.account_manager_version = '8.0.0'
            track.device_os_id = 'iPhone'

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            skip=['avatar_url'],
            **self.default_response()
        )

        self.assert_notifications_sent()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'skip_challenge',
                decision_source=DecisionSource.ACCOUNT_IS_SHARED,
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='0',
            ),
            self.env.statbox.entry(
                'tokens_issued',
                am_version='8.0.0',
                am_version_name='8.0.0',
                app_platform='iPhone',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_fresh_account_skip_challenge(self):
        self.env.ufo_api.set_response_side_effect(
            'profile',
            UfoApiTemporaryError,
        )
        reg_time = datetime.now() - timedelta(seconds=settings.PROFILE_TRIAL_PERIOD - 500)
        self.setup_blackbox_response(
            dbfields={
                'userinfo.reg_date.uid': reg_time.strftime('%Y-%m-%d %H:%M:%S'),
            },
        )
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '4.9.9'
            track.device_os_id = 'iPhone'

        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test',
                                             device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response()
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'skip_challenge',
                decision_source=DecisionSource.FRESH_ACCOUNT,
                challenge_reason=DecisionSource.UFO_FAILED,
                captcha_reason='new_challenge_not_available_for_account',
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_all_challenges_passed_skip_challenge(self):
        self.env.ufo_api.set_response_side_effect(
            'profile',
            UfoApiTemporaryError,
        )
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = dict(
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.setup_blackbox_response(**account_kwargs)

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.email_check_ownership_passed = True

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test',
                                             device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.default_response()
        )

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'skip_challenge',
                decision_source=DecisionSource.ALL_CHALLENGES_PASSED,
                challenge_reason=DecisionSource.UFO_FAILED,
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    @parameterized.expand([
        # платформа, версия, лайт / не лайт пользователь
        ('iPhone', '4.9.9', False),
        (None, None, False),
        (None, '7.0.0', False),
        ('Android 9 (REL)', None, False),
        ('Android 9 (REL)', '7.0.0', True),
    ])
    def test_untrusted_network__new_device__cannot_use_new_challenge(self, platform, version, is_lite):
        self.setup_untrusted_network()

        login = TEST_LOGIN + '@domain.tld' if is_lite else TEST_LOGIN
        if is_lite:
            self.setup_blackbox_response(
                aliases={
                    'lite': login,
                },
                login=login,
            )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = version
            track.device_os_id = platform

        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test',
                                             device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['captcha.required'],
            captcha_image_url='http://u.captcha.yandex.net/image?key=1p',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_password_change)
        ok_(not track.is_force_change_password)
        ok_(not track.is_change_password_sms_validation_required)

        self.assert_notifications_sent(is_challenged=True, is_lite=is_lite, login=login)
        self.assert_ufo_api_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'ufo_profile_checked',
                current=self.make_user_profile(raw_env=TEST_ENV_PROFILE, am_version=version).as_json,
                ufo_distance=str(EnvDistance.Max),
                is_challenge_required='1',
                is_fresh_profile_passed='0',
                decision_source=DecisionSource.BLACKLISTED_AS,
                is_full_profile_passed='0',
                full_profile_AS_list='AS1',
                captcha_reason='new_challenge_not_available_for_account',
            ),
            self.env.statbox.entry(
                'auth_notification',
                email_sent='1',
                is_challenged='1',
            ),
            self.env.statbox.entry(
                'profile_threshold_exceeded',
                is_password_change_required='0',
                decision_source=DecisionSource.BLACKLISTED_AS,
                was_online_sec_ago=TimeSpan(0),
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()

    def test_force_challenge(self):
        # PASSP-28789
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'has_cards': True,
                'as_list_freq_3m': [('AS1', 1)],
            },
        )

        account_kwargs = {
            'attributes': {
                'account.force_challenge': '1',
            },
        }
        self.setup_blackbox_response(**account_kwargs)
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request(query_args={'password_source': 'login'})
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )
        self.assert_antifraud_auth_fail_not_written()

    def test_magnitola__cannot_use_new_challenge(self):
        self.setup_untrusted_network()

        self.setup_blackbox_response(
            login=TEST_LOGIN,
            attributes={
                'account.enable_app_password': '1',
            },
        )

        with self.track_transaction(self.track_id) as track:
            track.device_hardware_model = 'magnitola_model'
            track.device_application = 'magnitola_app_id'

        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['captcha.required'],
            captcha_image_url='http://u.captcha.yandex.net/image?key=1p',
        )

        self.assert_antifraud_auth_fail_not_written()

    def test_magnitola__no_app_passwords(self):
        with self.track_transaction(self.track_id) as track:
            track.device_hardware_model = 'magnitola_model'
            track.device_application = 'magnitola_app_id'

        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['password.not_matched'],
        )

        self.assert_antifraud_auth_fail_written(
            'VALID/BAD/-/password.not_matched',
            model='magnitola_model',
            app_id='magnitola_app_id',
        )

    def test_magnitola__sms_2fa_not_used(self):
        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})
        self.setup_blackbox_response(
            login=TEST_LOGIN,
            attributes={
                'account.enable_app_password': '1',
                'account.sms_2fa_on': '1',
            },
        )

        with self.track_transaction(self.track_id) as track:
            track.device_hardware_model = 'magnitola_model'
            track.device_application = 'magnitola_app_id'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response()
        )

    def test_magnitola__account_not_found(self):
        with self.track_transaction(self.track_id) as track:
            track.device_hardware_model = 'magnitola_model'
            track.device_application = 'magnitola_app_id'

        self.setup_blackbox_response(uid=None)
        resp = self.make_request()

        self.assert_error_response(
            resp,
            ['account.not_found'],
        )


@with_settings_hosts(
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    CHECK_AVATARS_SECRETS_DENOMINATOR=1,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    AM_ANDROID_CHALLENGE_MIN_VERSION='5.0.0',
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    YDB_PERCENTAGE=0,
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    CHALLENGE_ON_HAS_CARDS_FOR_ALL_APPS=False,
    YSA_MIRROR_API_ENABLED=False,
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
)
class TestAuthByPasswordViewWithAvatarSecret(BaseTestAuthByPasswordView, BaseChallengeTestCase):
    def setUp(self):
        super(TestAuthByPasswordViewWithAvatarSecret, self).setUp()
        self.setup_blackbox_sign_response()
        self.setup_profile_response(
            add_fresh_profile=True,
            full_profile={
                'has_cards': False,
                'as_list_freq_3m': [('AS1', 1)],
            },
        )

    def setup_blackbox_sign_response(self):
        self.env.blackbox.set_response_value(
            'sign',
            blackbox_sign_response(TEST_AVATAR_SECRET),
        )

        self.env.blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response('%s:%s' % (TEST_UID, int(time()))),
        )

    @parameterized.expand([
        ('iPhone', 'login'),
        ('android', 'login'),  # источник login тоже, даже на android
        ('KGB_smartfone', 'login'),  # неизвестное устройство
    ])
    def test_no_challenge_on_any_phone_without_smartlock(self, phone, password_source):

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '8.0.0'  # версия для любой ОС которая поддерживает челендж
            track.device_os_id = phone

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='test', device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request(query_args={'password_source': password_source})

        self.assert_ok_response(
            resp,
            skip=['avatar_url'],
            **self.default_response()
        )

    @parameterized.expand([
        ('android', 'autologin'),  # android c автовходом
        ('android', 'smartlock'),
        ('iPhone', 'autologin'),  # iPhone с непонятно откуда взятым смартлоком
    ])
    def test_challenge_without_avatar_secret_on_slartlock_auth(self, phone, password_source):
        # Челендж должен быть показан, если пришли скорее всего со смартлока и не показали нам секрет

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '8.0.0'  # версия для любой ОС которая поддерживает челендж
            track.device_os_id = phone

        resp = self.make_request(query_args={'password_source': password_source})

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

    def test_challenge_without_avatar_secret_on_smartlock_auth_on_unknown_device(self):
        # на неизвестном устройстве KGB_smartfone показывается капча.
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '8.0.0'  # версия для любой ОС которая поддерживает челендж
            track.device_os_id = 'KGB_smartfone'

        resp = self.make_request(query_args={'password_source': 'autologin'})

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

    @parameterized.expand([
        #  (устройство, тип входа, ожидаем ли аватарку с секретом в ответе)
        ('android', 'autologin', True),  # android c автовходом
        ('android', 'smartlock', True),
        ('KGB_smartfone', 'autologin', True),  # неизвестное устройство, но был автовход
        ('iPhone', 'autologin', False),  # iPhone с непонятно откуда взятым смартлоком
    ])
    def test_no_challenge_with_correct_avatar_secret(self, phone, password_source, expect_secret_on_response):
        # Предыдущий тест с верным секретом в аватарке, дает успешно пройти логин не вызывая челендж и возвращает новую аватарку в ответе
        test_avatar_secret_value = 'super_secret_value'

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        self.env.blackbox.set_response_value(
            'sign',
            blackbox_sign_response(test_avatar_secret_value),
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '8.0.0'  # версия для любой ОС которая поддерживает челендж
            track.device_os_id = phone

        avatar_url_with_secret = TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SECRET)

        resp = self.make_request(query_args={'password_source': password_source,
                                             'avatar_url': avatar_url_with_secret})

        expected_response = self.default_response()

        if expect_secret_on_response:
            avatar_url_with_secret_in_answer = TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_KEY, test_avatar_secret_value)
            expected_response['avatar_url'] = avatar_url_with_secret_in_answer

        self.assert_ok_response(
            resp,
            **expected_response
        )

    @parameterized.expand([
        ('ololololololololo',),
        (None,),
    ])
    def test_challenge_with_incorrect_avatar_secret_on_android(self, avatar_secret):
        # Когда секрет неверный, пустой, истекший
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        self.env.blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(status=BLACKBOX_CHECK_SIGN_STATUS_EXPIRED),
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '8.0.0'  # версия для любой ОС которая поддерживает челендж
            track.device_os_id = 'android'

        avatar_url_with_secret = TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_KEY, avatar_secret)

        resp = self.make_request(query_args={'password_source': 'smartlock',
                                             'avatar_url': avatar_url_with_secret})

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )

    def test_challenge_with_correct_avatar_secret_from_another_uid(self):
        # Когда секрет проходит проверку подписи, но в нем зашит другой uid

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id='test', device_name=TEST_DEVICE_NAME),
        )
        self.env.blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response('%s:%s' % (TEST_UID + 1, int(time()))),
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '8.0.0'  # версия для любой ОС которая поддерживает челендж
            track.device_os_id = 'android'

        avatar_url_with_secret = TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SECRET)

        resp = self.make_request(query_args={'password_source': 'smartlock',
                                             'avatar_url': avatar_url_with_secret})

        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='auth_challenge',
        )


@with_settings_hosts(
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    YDB_PERCENTAGE=0,
    UFO_API_URL='http://localhost/',
    UFO_API_RETRIES=1,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    ANTIFRAUD_ON_CHALLENGE_ENABLED=False,
    # вся суть теста в этой настройке
    ALLOW_PROFILE_CHECK_FOR_MOBILE=False,
)
class TestAuthByPasswordViewWithDisabledMobileChallenges(BaseTestAuthByPasswordView, BaseChallengeTestCase):
    def setUp(self):
        super(TestAuthByPasswordViewWithDisabledMobileChallenges, self).setUp()
        # на всякий случай сделаем фейковый профиль который точно должен дать челлендж по профилю
        self.setup_profile_response(
            full_profile={
                'has_cards': True,
                'as_list_freq_3m': [('AS1000', 1)],
            },
        )

    def test_disable_mobile_profile_check(self):
        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '5.0.0'
            track.device_os_id = 'iPhone'

        # не совпадает с профилем
        self.fake_region_profile_mock.return_value = mock.Mock(AS_list=['AS1'], country={'id': 1}, city={'id': 2})

        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
        )

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            **self.default_response()
        )

        # нет записи о походе в антифрод
        eq_(len(self.env.antifraud_api.requests), 0)
        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'ufo_profile_checked',
                challenge_reason='',
                decision_source='ufo',
                is_challenge_required='0',
                # boilerplate
                current=self.make_user_profile(
                    raw_env=TEST_ENV_PROFILE,
                    am_version='5.0.0',
                ).as_json,
                ufo_distance='0',
                _exclude=['is_fresh_profile_passed']
            ),
        ])
        self.assert_antifraud_auth_fail_not_written()
