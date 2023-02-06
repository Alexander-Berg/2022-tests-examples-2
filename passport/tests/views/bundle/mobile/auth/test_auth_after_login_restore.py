# -*- coding: utf-8 -*-
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
    TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
    TEST_AVATAR_KEY,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_FIRSTNAME,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_OAUTH_TOKEN,
    TEST_PASSWORD_HASH,
    TEST_PHONE_NUMBER,
    TEST_PUBLIC_ID,
    TEST_UID,
)
from passport.backend.api.views.bundle.mixins.phone import KOLMOGOR_COUNTER_CALLS_SHUT_DOWN_FLAG
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.bot_api.faker.fake_bot_api import bot_api_response
from passport.backend.core.counters import login_restore_counter
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import deep_merge


@with_settings_hosts(
    AM_IOS_CHALLENGE_MIN_VERSION='5.0.0',
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_DEVICE_APP},
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    OAUTH_RETRIES=1,
    OAUTH_URL='http://localhost/',
    ALLOW_AUTH_AFTER_LOGIN_RESTORE_FOR_ALL=False,
    **mock_counters(
        LOGIN_RESTORE_PER_IP_LIMIT_COUNTER=(24, 3600, 3),
        LOGIN_RESTORE_PER_PHONE_LIMIT_COUNTER=(24, 3600, 3),
    )
)
class TestAuthAfterLoginRestoreView(BaseBundleTestViews, ProfileTestMixin):
    default_url = '/1/bundle/mobile/auth/after_login_restore/'
    consumer = 'dev'
    http_method = 'POST'
    http_query_args = {
        'uid': TEST_UID,
        'firstname': TEST_FIRSTNAME,
        'lastname': TEST_LASTNAME,
    }
    http_headers = {
        'user_ip': TEST_USER_IP,
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.create_and_fill_track()

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
        self.env.bot_api.set_response_value('send_message', bot_api_response())
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

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            _inherit_from='base',
            ip=TEST_USER_IP,
            track_id=self.track_id,
            mode='any_auth',
            type='mobile_after_login_restore',
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

    def create_and_fill_track(self, track_type='authorize'):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(track_type)
        with self.track_transaction(self.track_id) as track:
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.device_application = TEST_DEVICE_APP
            track.device_id = TEST_DEVICE_ID
            track.device_name = TEST_DEVICE_NAME
            track.cloud_token = TEST_CLOUD_TOKEN
            track.avatar_size = TEST_AVATAR_SIZE
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_sms'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

            # известный девайс и версия которая поддерживает челенджи
            track.account_manager_version = TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.version
            track.device_os_id = TEST_AM_COMPATIBLE_WITH_NEW_CHALLENGE.platform
        self.http_query_args.update(track_id=self.track_id)

    def build_account(
        self,
        primary_alias_type='neophonish',
        phone_number=None,
        **kwargs
    ):
        if phone_number is None:
            phone_number = TEST_PHONE_NUMBER

        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            aliases={
                primary_alias_type: TEST_LOGIN,
            },
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
            display_name=TEST_DISPLAY_NAME_DATA,
            default_avatar_key=TEST_AVATAR_KEY,
            is_avatar_empty=True,
            crypt_password=TEST_PASSWORD_HASH,
            public_id=TEST_PUBLIC_ID,
            **kwargs
        )
        account_kwargs = deep_merge(account_kwargs, build_phone_secured(1, phone_number.e164))

        return account_kwargs

    def setup_blackbox_userinfo_response(self, **kwargs):
        account_kwargs = self.build_account(**kwargs)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_kwargs),
        )

    def default_account_info(self, **kwargs):
        info = dict(
            uid=TEST_UID,
            display_login=TEST_LOGIN,
            primary_alias_type=5,
            has_password=True,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
            is_avatar_empty=True,
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
            birthday='1963-05-15',
            gender='m',
            public_id=TEST_PUBLIC_ID,
        )
        info.update(**kwargs)
        return info

    @parameterized.expand([
        ('authorize', ),
        ('register', ),
        ('restore', ),
    ])
    def test_ok_with_different_track_types(self, track_type):
        self.create_and_fill_track(track_type)

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
        eq_(len(self.env.bot_api.requests), 1)

        self.env.statbox.assert_contains(
            [
                self.env.statbox.entry('tokens_issued', track_id=self.track_id),
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
        self.env.social_binding_logger.assert_has_written([
            self.env.social_binding_logger.entry(
                'bind_phonish_account_by_track',
                uid=str(TEST_UID),
                track_id=self.track_id,
                ip=TEST_USER_IP,
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

    def test_ok_for_portal(self):
        self.setup_blackbox_userinfo_response(primary_alias_type='portal')
        with settings_context(
            GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
            ALLOW_AUTH_AFTER_LOGIN_RESTORE_FOR_ALL=True,
        ):
            resp = self.make_request()
        self.assert_ok_response(
            resp,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
            access_token=TEST_OAUTH_TOKEN,
            access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            **self.default_account_info(
                primary_alias_type=1,
                normalized_display_login=TEST_LOGIN,
            )
        )

    def test_account_invalid_type(self):
        self.setup_blackbox_userinfo_response(primary_alias_type='portal')
        resp = self.make_request()
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_phone_not_confirmed(self):
        with self.track_transaction(self.track_id) as track:
            track.phone_confirmation_is_confirmed = False
        resp = self.make_request()
        self.assert_error_response(resp, ['phone.not_confirmed'])

    def test_compare_not_matched(self):
        resp = self.make_request(query_args={'firstname': 'foo', 'lastname': 'bar'})
        self.assert_error_response(resp, ['compare.not_matched'])

    def test_auth_already_passed(self):
        with self.track_transaction(self.track_id) as track:
            track.oauth_token_created_at = 100
        resp = self.make_request()
        self.assert_error_response(resp, ['account.auth_passed'])

    def test_rate_limit_exceeded(self):
        for _ in range(3):
            login_restore_counter.get_per_phone_buckets().incr(TEST_PHONE_NUMBER.digital)
        resp = self.make_request()
        self.assert_error_response(resp, ['rate.limit_exceeded'])

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

    def test_new_ivory_coast_phone(self):
        self.check_ivory_coast_phone(
            account_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def test_old_ivory_coast_phone(self):
        self.check_ivory_coast_phone(
            account_phone_number=TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1,
            user_entered_phone_number=TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1,
        )

    def check_ivory_coast_phone(self, account_phone_number, user_entered_phone_number):
        self.setup_blackbox_userinfo_response(phone_number=account_phone_number)

        with self.track_transaction() as track:
            track.phone_confirmation_phone_number = user_entered_phone_number.e164

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
