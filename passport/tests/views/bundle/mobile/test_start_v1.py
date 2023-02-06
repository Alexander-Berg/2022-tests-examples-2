# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.mobile.base_test_data.base_test_data import (
    TEST_AVATAR_SIZE,
    TEST_CAPTCHA_SCALE_FACTOR,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
    TEST_MASKED_LOGIN,
    TEST_TRACK_ID,
    TEST_USER_IP,
    TEST_X_TOKEN_CLIENT_ID,
    TEST_X_TOKEN_CLIENT_SECRET,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_LANGUAGE,
    TEST_LOGIN,
    TEST_PASSWORD_HASH,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_SOCIAL_LOGIN,
    TEST_UID,
)
from passport.backend.core.builders.blackbox.exceptions import BlackboxInvalidParamsError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_loginoccupation_response,
    blackbox_userinfo_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator


@with_settings_hosts(ALLOW_REGISTRATION=True)
class TestStartView(BaseBundleTestViews):
    default_url = '/1/bundle/mobile/start/'
    consumer = 'dev'
    http_method = 'POST'
    http_headers = {
        'user_ip': TEST_USER_IP,
        'user_agent': 'curl',
    }
    http_query_args = {
        'x_token_client_id': TEST_X_TOKEN_CLIENT_ID,
        'x_token_client_secret': TEST_X_TOKEN_CLIENT_SECRET,
        'display_language': 'ru',
    }

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.track_manager = self.env.track_manager.get_manager()
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(TEST_TRACK_ID)

        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer='dev',
                grants={'mobile': ['base']},
            ),
        )
        self.setup_statbox_templates()
        self.setup_blackbox_userinfo_response()
        self.setup_blackbox_loginoccupation_response()

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.track_manager
        del self.track_id_generator
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='any_auth',
            type='mobile_start',
            ip=TEST_USER_IP,
            user_agent='curl',
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'opened',
            action='opened',
            track_id=TEST_TRACK_ID,
            user_entered_login=TEST_LOGIN,
        )

    def setup_blackbox_userinfo_response(self, uid=TEST_UID, primary_alias_type='portal',
                                         enabled=True, has_password=True, with_social_alias=False):
        aliases = {
            primary_alias_type: TEST_LOGIN,
        }
        if with_social_alias:
            aliases.update({
                'social': TEST_SOCIAL_LOGIN,
            })
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=uid,
                login=TEST_LOGIN,
                crypt_password=TEST_PASSWORD_HASH if has_password else None,
                aliases=aliases,
                enabled=enabled,
            ),
        )

    def setup_blackbox_loginoccupation_response(self, status='occupied'):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: status}),
        )

    def check_blackbox_calls(self, login=TEST_LOGIN, call_count=1):
        eq_(len(self.env.blackbox.requests), call_count)
        if call_count >= 1:
            self.env.blackbox.requests[0].assert_post_data_contains({
                'method': 'userinfo',
                'login': login,
                'find_by_phone_alias': 'force_on',
                'country': 'US',
            })
        if call_count >= 2:
            self.env.blackbox.requests[1].assert_query_contains({
                'method': 'loginoccupation',
            })

    def assert_statbox_ok(self, **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('opened', **kwargs),
        ])

    def test_ok_by_login(self):
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
        )

        self.check_blackbox_calls(login=TEST_LOGIN)
        self.assert_statbox_ok()

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'authorize')
        eq_(track.x_token_client_id, TEST_X_TOKEN_CLIENT_ID)
        eq_(track.x_token_client_secret, TEST_X_TOKEN_CLIENT_SECRET)
        eq_(track.display_language, TEST_LANGUAGE)
        eq_(track.language, TEST_LANGUAGE)
        ok_(track.client_id is None)
        ok_(track.client_secret is None)
        ok_(track.avatar_size is None)
        ok_(track.captcha_scale_factor is None)
        ok_(track.device_name is None)
        ok_(track.country is None)
        eq_(track.user_entered_login, TEST_LOGIN)

    def test_ok_by_phonenumber_alias(self):
        resp = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.original})
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
            masked_login=TEST_MASKED_LOGIN,
        )

        self.check_blackbox_calls(login=TEST_PHONE_NUMBER.original)
        self.assert_statbox_ok(user_entered_login=TEST_PHONE_NUMBER.original)

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'authorize')
        eq_(track.x_token_client_id, TEST_X_TOKEN_CLIENT_ID)
        eq_(track.x_token_client_secret, TEST_X_TOKEN_CLIENT_SECRET)
        eq_(track.display_language, TEST_LANGUAGE)
        eq_(track.language, TEST_LANGUAGE)
        ok_(track.client_id is None)
        ok_(track.client_secret is None)
        ok_(track.avatar_size is None)
        ok_(track.captcha_scale_factor is None)
        ok_(track.device_name is None)
        ok_(track.country is None)
        eq_(track.user_entered_login, TEST_PHONE_NUMBER.original)

    def test_ok_with_extra_params_and_second_client(self):
        resp = self.make_request(query_args={
            'login': TEST_LOGIN,
            'am_version_name': 'test-am-version',
            'device_id': TEST_DEVICE_ID,
            'device_name': TEST_DEVICE_NAME,
            'avatar_size': TEST_AVATAR_SIZE,
            'captcha_scale_factor': TEST_CAPTCHA_SCALE_FACTOR,
            'display_language': 'en',
            'client_id': TEST_CLIENT_ID,
            'client_secret': TEST_CLIENT_SECRET,
        })
        self.assert_ok_response(
            resp,
            track_id=TEST_TRACK_ID,
            can_authorize=True,
            auth_methods=['password'],
            primary_alias_type=1,
        )

        self.check_blackbox_calls()
        self.assert_statbox_ok(
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            am_version_name='test-am-version',
        )

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'authorize')
        eq_(track.avatar_size, TEST_AVATAR_SIZE)
        eq_(track.captcha_scale_factor, str(TEST_CAPTCHA_SCALE_FACTOR))
        eq_(track.account_manager_version, 'test-am-version')
        eq_(track.device_id, TEST_DEVICE_ID)
        eq_(track.device_name, TEST_DEVICE_NAME)
        eq_(track.display_language, 'en')
        ok_(track.country is None)
        eq_(track.x_token_client_id, TEST_X_TOKEN_CLIENT_ID)
        eq_(track.x_token_client_secret, TEST_X_TOKEN_CLIENT_SECRET)
        eq_(track.client_id, TEST_CLIENT_ID)
        eq_(track.client_secret, TEST_CLIENT_SECRET)

    def test_account_without_auth_methods(self):
        self.setup_blackbox_userinfo_response(primary_alias_type='social', has_password=False)
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            auth_methods=[],
            primary_alias_type=6,
        )

        eq_(len(self.env.blackbox.requests), 1)

    def test_account_not_found_by_login(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')

        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            track_id=TEST_TRACK_ID,
        )

        self.check_blackbox_calls(call_count=2)  # userinfo + loginoccupation

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'register')
        eq_(track.country, 'us')
        eq_(track.user_entered_login, TEST_LOGIN)

    def test_account_not_found_by_phonenumber_alias(self):
        self.setup_blackbox_userinfo_response(uid=None)

        resp = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.original})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            track_id=TEST_TRACK_ID,
            phone_number=TEST_PHONE_NUMBER_DUMPED,
        )

        self.check_blackbox_calls(login=TEST_PHONE_NUMBER.original, call_count=1)

        track = self.track_manager.read(TEST_TRACK_ID)
        eq_(track.track_type, 'register')
        eq_(track.country, 'us')
        ok_(track.user_entered_login is None)

    def test_force_register(self):
        resp = self.make_request(query_args={'phone_number': TEST_PHONE_NUMBER.original, 'force_register': 'yes'})
        self.assert_error_response(
            resp,
            ['account.not_found'],
            can_register=True,
            track_id=TEST_TRACK_ID,
            phone_number=TEST_PHONE_NUMBER_DUMPED,
        )

        eq_(len(self.env.blackbox.requests), 0)

    def test_account_blocked(self):
        self.setup_blackbox_userinfo_response(enabled=False)

        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['account.disabled'],
        )

        self.check_blackbox_calls(call_count=1)  # userinfo

    def test_login_not_available_for_registration(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('stoplist')

        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['login.notavailable'],
        )

        eq_(len(self.env.blackbox.requests), 2)  # userinfo + loginoccupation

    def test_login_invalid_for_registration(self):
        self.setup_blackbox_userinfo_response(uid=None)

        resp = self.make_request(query_args={'login': '^_^'})
        self.assert_error_response(
            resp,
            ['login.prohibitedsymbols'],
        )

        self.check_blackbox_calls(login='^_^', call_count=1)  # в loginoccupation не идём, ибо логин заведомо невалиден

    def test_phone_number_invalid(self):
        self.setup_blackbox_userinfo_response(uid=None)

        resp = self.make_request(query_args={'phone_number': '^_^'})
        self.assert_error_response(
            resp,
            ['phone_number.invalid'],
        )

        self.check_blackbox_calls(login='^_^', call_count=1)

    def test_blackbox_invalid_params_error(self):
        self.env.blackbox.set_response_side_effect(
            'userinfo',
            BlackboxInvalidParamsError,
        )

        resp = self.make_request(query_args={'login': 'a\nb'})
        self.assert_error_response(
            resp,
            ['login.prohibitedsymbols'],
        )

        self.check_blackbox_calls(login='a\nb', call_count=1)  # в loginoccupation не идём, ибо логин заведомо невалиден

    def test_unable_to_register(self):
        self.setup_blackbox_userinfo_response(uid=None)
        self.setup_blackbox_loginoccupation_response('free')

        with settings_context(ALLOW_REGISTRATION=False):
            resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_error_response(
            resp,
            ['account.not_found'],
        )

        self.check_blackbox_calls(call_count=2)  # userinfo + loginoccupation

    def test_social_with_login_without_password(self):
        self.setup_blackbox_userinfo_response(
            has_password=False,
            with_social_alias=True,
        )
        resp = self.make_request(query_args={'login': TEST_LOGIN})
        self.assert_ok_response(
            resp,
            auth_methods=[],
            primary_alias_type=6,
        )

        self.check_blackbox_calls(login=TEST_LOGIN)
