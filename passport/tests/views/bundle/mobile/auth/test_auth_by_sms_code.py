# -*- coding: utf-8 -*-
import abc
from datetime import (
    datetime,
    timedelta,
)

import mock
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.mixins import ProfileTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE,
    TEST_AVATAR_SIZE,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_CLOUD_TOKEN,
    TEST_DEVICE_APP,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_OAUTH_TOKEN_TTL,
    TEST_OAUTH_X_TOKEN,
    TEST_OAUTH_X_TOKEN_TTL,
    TEST_USER_IP,
    TEST_X_TOKEN_CLIENT_ID,
    TEST_X_TOKEN_CLIENT_SECRET,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AVATAR_KEY,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_LOGIN,
    TEST_OAUTH_TOKEN,
    TEST_PASSWORD_HASH,
    TEST_PHONE_NUMBER,
    TEST_PUBLIC_ID,
    TEST_UID,
)
from passport.backend.api.views.bundle.mixins.phone import KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.oauth.faker import oauth_bundle_successful_response
from passport.backend.core.conf import settings
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import deep_merge


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


class UserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self, env):
        self._env = env
        self._kwargs = dict()

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_userinfo_response(**self.kwargs)
        self._env.blackbox.extend_response_side_effect('userinfo', [response])
        self._env.db.serialize(response)


class PortalUserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self, env):
        self._userinfo_response = UserinfoBlackboxResponse(env)

        kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            aliases={
                'portal': TEST_LOGIN,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            display_name=TEST_DISPLAY_NAME_DATA,
            default_avatar_key=TEST_AVATAR_KEY,
            is_avatar_empty=True,
            crypt_password=TEST_PASSWORD_HASH,
            public_id=TEST_PUBLIC_ID,
        )
        phone_secured = build_phone_secured(1, TEST_PHONE_NUMBER.e164)
        kwargs = deep_merge(kwargs, phone_secured)
        self._userinfo_response.kwargs.update(kwargs)

    @property
    def kwargs(self):
        return self._userinfo_response.kwargs

    def setup(self):
        self._userinfo_response.setup()


class BaseAuthBySmsCodeTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/mobile/auth/sms_code/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            _inherit_from='base',
            ip=TEST_USER_IP,
            track_id=self.track_id,
            mode='any_auth',
            type='mobile_sms_code',
            consumer='dev',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'tokens_issued',
            _inherit_from='local_base',
            _exclude=['user_agent'],
            action='tokens_issued',
            uid=str(TEST_UID),
            login=TEST_LOGIN,
            password_passed='0',
            x_token_client_id=TEST_X_TOKEN_CLIENT_ID,
            x_token_issued='1',
            client_id=TEST_CLIENT_ID,
            client_token_issued='1',
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            cloud_token=TEST_CLOUD_TOKEN,
            am_version=TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
            am_version_name=TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
            app_id=TEST_DEVICE_APP,
            app_platform=TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.platform,
        )

    def default_account_info(self, **kwargs):
        info = dict(
            uid=TEST_UID,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN,
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
        info.update(**kwargs)
        return info

    def setup_track(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_transaction(self.track_id) as track:
            track.user_entered_login = TEST_LOGIN
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.device_application = TEST_DEVICE_APP
            track.device_id = TEST_DEVICE_ID
            track.device_name = TEST_DEVICE_NAME
            track.cloud_token = TEST_CLOUD_TOKEN
            track.avatar_size = TEST_AVATAR_SIZE
            track.allowed_auth_methods = ['password', 'sms_code']
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_sms'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.uid = TEST_UID

            # известный девайс и версия которая поддерживает челенджи
            track.account_manager_version = TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version
            track.device_os_id = TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.platform

    def setup_blackbox_userinfo_response(self, **kwargs):
        userinfo_response = PortalUserinfoBlackboxResponse(self.env)
        userinfo_response.kwargs.update(deep_merge(userinfo_response.kwargs, kwargs))
        userinfo_response.setup()

    def setup_oauth_response(self):
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=True, device_id=TEST_DEVICE_ID, device_name=TEST_DEVICE_NAME),
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

    def setup_grants_config(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'mobile': ['auth']},
            ),
        )


@with_settings_hosts(
    ALLOW_AUTH_BY_SMS_FOR_MOBILE_ONLY_FOR_TEST_LOGINS=False,
    ALLOW_AUTH_BY_SMS_FOR_MOBILE=True,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    OAUTH_RETRIES=1,
    OAUTH_URL='http://localhost/',
    BLACKLISTED_AS_LIST={'AS1234'},
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
)
class TestAuthBySmsCodeView(
    ProfileTestMixin,
    BaseAuthBySmsCodeTestCase,
):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.setup_track()
        self.http_query_args.update(track_id=self.track_id)
        self.env.push_api.set_response_value('send', 'OK')

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

        self.setup_grants_config()
        self.setup_oauth_response()
        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_statbox_templates()
        flag = {KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0}
        self.env.kolmogor.set_response_value('get', flag)

    def tearDown(self):
        self.region_challenge_patch.stop()
        del self.region_challenge_patch
        self.region_profile_patch.stop()
        del self.region_profile_patch
        self.teardown_profile_patches()
        del self.track_manager
        self.env.stop()
        del self.env

    def test_ok(self):
        self.setup_blackbox_userinfo_response()

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
            access_token=TEST_OAUTH_TOKEN,
            access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            **self.default_account_info()
        )

        eq_(len(self.env.oauth.requests), 2)
        self.env.oauth.requests[0].assert_properties_equal(
            method='POST',
            url='http://localhost/token?user_ip=%s&device_id=%s&device_name=%s&am_version=%s&am_version_name=%s&'
            'app_platform=%s&app_id=%s' %
            (
                TEST_USER_IP,
                TEST_DEVICE_ID,
                TEST_DEVICE_NAME,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.platform,
                TEST_DEVICE_APP,
            ),
            post_args={
                'grant_type': 'passport_assertion',
                'client_id': TEST_X_TOKEN_CLIENT_ID,
                'client_secret': TEST_X_TOKEN_CLIENT_SECRET,
                'assertion': TEST_UID,
                'password_passed': False,
                'cloud_token': TEST_CLOUD_TOKEN,
                'passport_track_id': self.track_id,
            },
        )
        self.env.oauth.requests[1].assert_properties_equal(
            method='POST',
            url='http://localhost/token?user_ip=%s&device_id=%s&device_name=%s&am_version=%s&am_version_name=%s&'
            'app_platform=%s&app_id=%s' %
            (
                TEST_USER_IP,
                TEST_DEVICE_ID,
                TEST_DEVICE_NAME,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.platform,
                TEST_DEVICE_APP,
            ),
            post_args={
                'grant_type': 'x-token',
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'access_token': TEST_OAUTH_X_TOKEN,
                'passport_track_id': self.track_id,
            },
        )

        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry('tokens_issued'),
            ],
            offset=-1,
        )
        self.env.phone_logger.assert_has_written([
            self.env.phone_logger.get_log_entry(
                TEST_UID,
                TEST_PHONE_NUMBER.e164,
                yandexuid='',
            ),
        ])

        profile = self.make_user_profile(
            raw_env={
                'am_version': TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                'cloud_token': TEST_CLOUD_TOKEN,
                'device_id': TEST_DEVICE_ID,
                'ip': TEST_USER_IP,
                'is_mobile': True,
                'user_agent_info': {},
                'yandexuid': None,
            },
        )
        self.assert_profile_written_to_auth_challenge_log(profile)

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())
        eq_(track.human_readable_login, TEST_LOGIN)

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

    def test_ok_blacklisted_as_fresh_account(self):
        self.setup_untrusted_network()
        reg_time = datetime.now() - timedelta(seconds=settings.PROFILE_TRIAL_PERIOD - 500)
        self.setup_blackbox_userinfo_response(
            dbfields={
                'userinfo.reg_date.uid': reg_time.strftime('%Y-%m-%d %H:%M:%S'),
            },
        )

        with self.track_transaction(self.track_id) as track:
            track.account_manager_version = '4.9.9'

        resp = self.make_request()

        self.assert_ok_response(
            resp,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
            access_token=TEST_OAUTH_TOKEN,
            access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            **self.default_account_info()
        )

    def test_not_allowed_auth_method(self):
        self.setup_blackbox_userinfo_response()
        with self.track_transaction(self.track_id) as track:
            track.allowed_auth_methods = ['password']
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_allowed_auth_methods_undefined(self):
        self.setup_blackbox_userinfo_response()
        with self.track_transaction(self.track_id) as track:
            track.allowed_auth_methods = None
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_phone_not_confirmed(self):
        self.setup_blackbox_userinfo_response()
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = False
        resp = self.make_request()
        self.assert_error_response(resp, ['phone.not_confirmed'])

    @parameterized.expand([
        ('by_call', ),
        ('by_flash_call',),
    ])
    def test_phone_confirmed_insecurely(self, phone_confirmation_method):
        self.setup_blackbox_userinfo_response()
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_method = phone_confirmation_method
        resp = self.make_request()
        self.assert_error_response(resp, ['phone.not_confirmed'])

    def test_auth_already_passed(self):
        self.setup_blackbox_userinfo_response()
        with self.track_transaction(self.track_id) as track:
            track.oauth_token_created_at = 100
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'])

    def test_captcha_from_previous_action_is_ignored(self):
        self.setup_blackbox_userinfo_response()
        # на этом шаге капча возникать не может, а капча от другого метода нас не интересует
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
            access_token=TEST_OAUTH_TOKEN,
            access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            **self.default_account_info()
        )

    def test_external_or_native_action_required(self):
        self.setup_blackbox_userinfo_response(attributes={'password.forced_changing_reason': '1'})
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='change_password',
            change_password_reason='account_hacked',
            validation_method='captcha_and_phone',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_password_change)
        ok_(track.is_force_change_password)
        ok_(track.is_change_password_sms_validation_required)
        ok_(not track.retpath)

    def test_sms_2fa_on__no_challenge(self):
        self.setup_blackbox_userinfo_response(
            attributes={
                'account.sms_2fa_on': '1',
            },
        )

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
            access_token=TEST_OAUTH_TOKEN,
            access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            **self.default_account_info()
        )


@with_settings_hosts(
    ALLOW_AUTH_BY_SMS_FOR_MOBILE_ONLY_FOR_TEST_LOGINS=False,
    ALLOW_AUTH_BY_SMS_FOR_MOBILE=True,
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_DEVICE_APP},
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    OAUTH_RETRIES=1,
    OAUTH_URL='http://localhost/',
)
class TestNeophonishAuthBySmsCodeView(
    ProfileTestMixin,
    BaseAuthBySmsCodeTestCase,
):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.setup_track()
        self.http_query_args.update(track_id=self.track_id)

        self.setup_grants_config()
        self.setup_oauth_response()
        self.setup_blackbox_userinfo_response()
        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_statbox_templates()
        flag = {KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG: 0}
        self.env.kolmogor.set_response_value('get', flag)

    def tearDown(self):
        self.teardown_profile_patches()
        del self.track_manager
        self.env.stop()
        del self.env

    def test_bind_phonish_to_neophonish(self):
        resp = self.make_request()

        self.assert_ok_response(resp, check_all=False)

        self.env.social_binding_logger.assert_equals(
            [
                self.env.social_binding_logger.entry(
                    'bind_phonish_account_by_track',
                    ip=TEST_USER_IP,
                    track_id=self.track_id,
                    uid=str(TEST_UID),
                ),
            ],
        )

    def test_binding_disabled_for_app(self):
        with self.track_transaction(self.track_id) as track:
            track.device_application = 'ru.yandex.no_binding'

        resp = self.make_request()

        self.assert_ok_response(resp, check_all=False)

        self.env.social_binding_logger.assert_equals([])
