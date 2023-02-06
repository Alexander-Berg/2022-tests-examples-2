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
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import TEST_MODEL_CONFIGS
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_AVATAR_SIZE,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_CLOUD_TOKEN,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_OAUTH_TOKEN_TTL,
    TEST_OAUTH_X_TOKEN,
    TEST_OAUTH_X_TOKEN_TTL,
    TEST_OTP,
    TEST_OTP_CHECK_TIME,
    TEST_USER_IP,
    TEST_X_TOKEN_CLIENT_ID,
    TEST_X_TOKEN_CLIENT_SECRET,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AVATAR_KEY,
    TEST_AVATAR_SECRET,
    TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_LOGIN,
    TEST_OAUTH_TOKEN,
    TEST_PASSWORD_HASH,
    TEST_PUBLIC_ID,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_CHECK_RFC_TOTP_INVALID_STATUS,
    BLACKBOX_CHECK_RFC_TOTP_VALID_STATUS,
    BLACKBOX_SECOND_STEP_RFC_TOTP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_rfc_totp_response,
    blackbox_sign_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.captcha.faker import (
    captcha_response_check,
    captcha_response_generate,
)
from passport.backend.core.counters import bad_rfc_otp_counter
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings_hosts(
    AUTH_PROFILE_CHALLENGE_ENABLED=True,
    AUTH_PROFILE_ENABLED=True,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    GET_AVATAR_WITH_SECRET_URL=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE,
    OAUTH_RETRIES=1,
    OAUTH_URL='http://localhost/',
    TENSORNET_API_URL='http://tensornet:80/',
    TENSORNET_MODEL_CONFIGS=TEST_MODEL_CONFIGS,
    **mock_counters(
        BAD_RFC_OTP_COUNTER=(6, 600, 2),
    )
)
class TestAuthByRfcOtpView(BaseBundleTestViews, ProfileTestMixin):
    default_url = '/1/bundle/mobile/auth/rfc_otp/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
    }
    http_query_args = {
        'rfc_otp': TEST_OTP,
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
            track.is_second_step_required = True
            track.allowed_second_steps = [BLACKBOX_SECOND_STEP_RFC_TOTP]
            track.uid = TEST_UID
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
        self.setup_blackbox_check_rfc_totp_response()
        self.setup_blackbox_sign_response()
        self.setup_profile_patches()
        self.setup_profile_responses()

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

    def setup_blackbox_check_rfc_totp_response(self, is_otp_correct=True):
        self.env.blackbox.set_response_value(
            'check_rfc_totp',
            blackbox_check_rfc_totp_response(
                status=BLACKBOX_CHECK_RFC_TOTP_VALID_STATUS if is_otp_correct else BLACKBOX_CHECK_RFC_TOTP_INVALID_STATUS,
                time=TEST_OTP_CHECK_TIME,
            ),
        )

    def setup_blackbox_sign_response(self):
        self.env.blackbox.set_response_value(
            'sign',
            blackbox_sign_response(TEST_AVATAR_SECRET),
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
            avatar_url=TEST_AVATAR_URL_WITH_SECRET_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SECRET),
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
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

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
            url='http://localhost/token?user_ip=%s&device_id=%s&device_name=%s' % (
            TEST_USER_IP, TEST_DEVICE_ID, TEST_DEVICE_NAME),
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
        self.env.oauth.requests[1].assert_properties_equal(
            method='POST',
            url='http://localhost/token?user_ip=%s&device_id=%s&device_name=%s' % (
            TEST_USER_IP, TEST_DEVICE_ID, TEST_DEVICE_NAME),
            post_args={
                'grant_type': 'x-token',
                'client_id': TEST_CLIENT_ID,
                'client_secret': TEST_CLIENT_SECRET,
                'access_token': TEST_OAUTH_X_TOKEN,
                'passport_track_id': self.track_id,
            },
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.allow_oauth_authorization)
        eq_(track.oauth_token_created_at, TimeNow())

        self.env.db.check(
            'attributes',
            'account.rfc_totp.check_time',
            str(TEST_OTP_CHECK_TIME),
            uid=TEST_UID,
            db='passportdbshard1',
        )

    def test_otp_invalid(self):
        self.setup_blackbox_check_rfc_totp_response(is_otp_correct=False)
        resp = self.make_request()
        self.assert_error_response(resp, ['rfc_otp.invalid'])

    def test_invalid_track_state(self):
        with self.track_transaction(self.track_id) as track:
            track.uid = None
        resp = self.make_request()
        self.assert_error_response(resp, ['track.invalid_state'])

    def test_auth_already_passed(self):
        with self.track_transaction(self.track_id) as track:
            track.oauth_token_created_at = 100
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'])

    def test_captcha_required__from_previous_action(self):
        """Пришли с треком с непройденной капчей - потребуем капчу"""
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

    def test_captcha_required__counter_limit(self):
        """Счётчик уже перегрет - потребуем капчу"""
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        counter = bad_rfc_otp_counter.get_counter()
        for _ in range(2):
            counter.incr(TEST_UID)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            captcha_image_url='http://u.captcha.yandex.net/image?key=1p',
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)

    def test_counter_limit_captcha_passed_and_otp_good__ok(self):
        """Счётчик уже перегрет, но мы пришли с разгаданной капчей и верным отп - пропустим"""
        self.env.captcha_mock.set_response_value('check', captcha_response_check(successful=True))
        counter = bad_rfc_otp_counter.get_counter()
        for _ in range(2):
            counter.incr(TEST_UID)
        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True
            track.captcha_key = 'key'
        resp = self.make_request(query_args={'captcha_answer': 'answer'})
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

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(track.is_captcha_checked)
        ok_(track.is_captcha_recognized)

    def test_counter_limit_captcha_passed_and_otp_bad__ok(self):
        """Счётчик уже перегрет, но мы пришли с разгаданной капчей и неверным отп - отдадим ошибку"""
        self.env.captcha_mock.set_response_value('check', captcha_response_check(successful=True))
        counter = bad_rfc_otp_counter.get_counter()
        for _ in range(2):
            counter.incr(TEST_UID)

        self.setup_blackbox_check_rfc_totp_response(is_otp_correct=False)

        with self.track_transaction(self.track_id) as track:
            track.is_captcha_required = True
            track.captcha_key = 'key'
        resp = self.make_request(query_args={'captcha_answer': 'answer'})
        self.assert_error_response(
            resp,
            ['rfc_otp.invalid'],
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)

    def test_captcha_required__bad_otp_and_counter_limit(self):
        """Счётчик перегрелся на текущей неудачной проверке otp - отдадим ошибку"""
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate(key='key'))
        counter = bad_rfc_otp_counter.get_counter()
        counter.incr(TEST_UID)

        self.setup_blackbox_check_rfc_totp_response(is_otp_correct=False)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['rfc_otp.invalid'],
        )

        track = self.track_manager.read(self.track_id)
        ok_(not track.is_captcha_required)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)

    def test_external_or_native_action_required(self):
        self.setup_blackbox_userinfo_response(
            attributes={
                'password.forced_changing_reason': '1',
            },
        )
        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.required_external_or_native'],
            state='change_password',
            change_password_reason='account_hacked',
            validation_method='captcha_and_phone',
        )

    def test_track_invalidated_by_glogout(self):
        track = self.track_manager.read(self.track_id)
        self.setup_blackbox_userinfo_response(
            attributes={
                'account.global_logout_datetime': str(int(track.logout_checkpoint_timestamp) + 1),
            },
        )

        resp = self.make_request()
        self.assert_error_response(resp, ['account.global_logout'])
