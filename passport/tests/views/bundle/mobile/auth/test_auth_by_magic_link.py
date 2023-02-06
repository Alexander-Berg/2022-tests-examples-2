# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
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
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import deep_merge


TEST_RETPATH = 'https://yxclid.oauth-test.yandex.ru/magic-link/app-id/finish'


@with_settings_hosts(
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    OAUTH_RETRIES=1,
    OAUTH_URL='http://localhost/',
)
class TestAuthByMagicLinkView(BaseBundleTestViews, ProfileTestMixin):
    default_url = '/1/bundle/mobile/auth/magic_link/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
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
            track.cloud_token = TEST_CLOUD_TOKEN
            track.avatar_size = TEST_AVATAR_SIZE
            track.magic_link_confirm_time = 123456
            track.uid = TEST_UID
            track.retpath = TEST_RETPATH

            # известный девайс и версия которая поддерживает челенджи
            track.account_manager_version = TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version
            track.device_os_id = TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.platform
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
        self.setup_blackbox_userinfo_response()
        self.setup_profile_patches()
        self.setup_profile_responses()
        self.setup_antifraud_log_templates()

    def setup_antifraud_log_templates(self):
        self.env.antifraud_logger.bind_entry(
            'auth_fail',
            _exclude=['user_agent'],
            request='auth',
            channel='auth',
            sub_channel='login',
            status='FAILED',
            ip=TEST_USER_IP,
            external_id='track-{}'.format(self.track_id),
            service_id='login',
        )

    def assert_antifraud_auth_fail_not_written(self):
        self.env.antifraud_logger.assert_has_written([])

    def assert_antifraud_auth_fail_written(
        self, comment_appendix='', offset=0, _exclude=None, **kwargs
    ):
        kwargs['comment'] = 'mobile_magic_link'
        if comment_appendix:
            kwargs['comment'] += '/' + comment_appendix
        self.env.antifraud_logger.assert_contains(
            self.env.antifraud_logger.entry('auth_fail', _exclude=_exclude, **kwargs),
            offset=offset,
        )

    def tearDown(self):
        self.teardown_profile_patches()
        del self.track_manager
        self.env.stop()
        del self.env

    def setup_blackbox_userinfo_response(self, **kwargs):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=TEST_DISPLAY_NAME_DATA,
                default_avatar_key=TEST_AVATAR_KEY,
                is_avatar_empty=True,
                crypt_password=TEST_PASSWORD_HASH,
                public_id=TEST_PUBLIC_ID,
                **kwargs
            ),
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

    def test_ok(self):
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
            'app_platform=%s' %
            (
                TEST_USER_IP,
                TEST_DEVICE_ID,
                TEST_DEVICE_NAME,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.platform,
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
            'app_platform=%s' %
            (
                TEST_USER_IP,
                TEST_DEVICE_ID,
                TEST_DEVICE_NAME,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version,
                TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.platform,
            ),
            post_args={
                'grant_type': 'x-token',
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'access_token': TEST_OAUTH_X_TOKEN,
                'passport_track_id': self.track_id,
            },
        )

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
        eq_(track.retpath, TEST_RETPATH)  # убеждаемся, что не меняли ранее записанное значение
        self.assert_antifraud_auth_fail_not_written()

    def test_magic_link_not_confirmed(self):
        with self.track_transaction(self.track_id) as track:
            track.magic_link_confirm_time = None
        resp = self.make_request()
        self.assert_error_response(resp, ['magic_link.not_confirmed'])
        self.assert_antifraud_auth_fail_written('magic_link_not_confirmed')

    def test_invalid_track_state(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])
        self.assert_antifraud_auth_fail_not_written()

    def test_auth_already_passed(self):
        with self.track_transaction(self.track_id) as track:
            track.oauth_token_created_at = 100
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'])
        self.assert_antifraud_auth_fail_not_written()

    def test_captcha_from_previous_action_is_ignored(self):
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
        self.assert_antifraud_auth_fail_not_written()

    def test_track_invalidated_by_glogout(self):
        track = self.track_manager.read(self.track_id)
        self.setup_blackbox_userinfo_response(
            attributes={
                'account.global_logout_datetime': str(int(track.logout_checkpoint_timestamp) + 1),
            },
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['account.global_logout'])
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
        self.setup_blackbox_userinfo_response(**account_kwargs)
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
        self.assert_antifraud_auth_fail_not_written()
