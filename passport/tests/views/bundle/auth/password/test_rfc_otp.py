# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    TEST_HOST,
    TEST_LOGIN,
    TEST_PHONE_NUMBER,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_USER_IP,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.views.bundle.constants import (
    CHANGE_PASSWORD_REASON_EXPIRED,
    CHANGE_PASSWORD_REASON_HACKED,
)
from passport.backend.api.views.bundle.phone.helpers import dump_number
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_CHECK_RFC_TOTP_INVALID_STATUS,
    BLACKBOX_CHECK_RFC_TOTP_VALID_STATUS,
    BLACKBOX_SECOND_STEP_RFC_TOTP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_rfc_totp_response,
    blackbox_userinfo_response,
)
from passport.backend.core.counters import bad_rfc_otp_counter
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import deep_merge


TEST_TOTP_CHECK_TIME = 100


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    YABS_URL='localhost',
    **mock_counters(
        BAD_RFC_OTP_COUNTER=(6, 600, 2),
    )
)
class RfcOtpTestCase(BaseBundleTestViews):
    default_url = '/1/bundle/auth/password/rfc_otp/check/?consumer=dev'
    http_method = 'POST'
    http_query_args = dict(
        uid=TEST_UID,
        otp='test',
    )
    http_headers = dict(
        host=TEST_HOST,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(RfcOtpTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.http_query_args.update(track_id=self.track_id)
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.is_second_step_required = True
            track.allowed_second_steps = [BLACKBOX_SECOND_STEP_RFC_TOTP]

        self.setup_blackbox_responses()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id
        super(RfcOtpTestCase, self).tearDown()

    def setup_blackbox_responses(self, rfc_2fa_on=True, password_change_required=False, is_otp_correct=True):
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            crypt_password='1:pass',
            attributes={},
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        if rfc_2fa_on:
            account_kwargs['attributes']['account.rfc_2fa_on'] = '1'
        if password_change_required:
            account_kwargs['attributes']['password.forced_changing_reason'] = '1'

        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_kwargs),
        )
        self.env.blackbox.set_response_value(
            'check_rfc_totp',
            blackbox_check_rfc_totp_response(
                status=BLACKBOX_CHECK_RFC_TOTP_VALID_STATUS if is_otp_correct else BLACKBOX_CHECK_RFC_TOTP_INVALID_STATUS,
                time=TEST_TOTP_CHECK_TIME,
            ),
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='any_auth',
            track_id=self.track_id,
            ip=TEST_USER_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            yandexuid=TEST_YANDEXUID_COOKIE,
        )
        self.env.statbox.bind_entry(
            'submitted',
            action='rfc_otp_submitted',
        )
        self.env.statbox.bind_entry(
            'redirect_to_password_change',
            mode='change_password_force',
            action='defined_validation_method',
            validation_method='captcha_and_phone',
            track_id=self.track_id,
            uid=str(TEST_UID),
            _exclude=['consumer', 'ip', 'origin', 'user_agent', 'yandexuid'],
        )

    def check_statbox_entries_xunistater_parsed(self):
        self.env.xunistater_checker.check_xunistater_signals(
            [entry[0][0] for entry in self.env.statbox_handle_mock.call_args_list],
            ["auth_2fa.rps"],
            {"auth_2fa.rps.total_dmmm": 1}
        )

    def account_response_values(self, login=TEST_LOGIN, rfc_2fa=False):
        response = {
            'display_login': login,
            'display_name': {
                'default_avatar': '',
                'name': '',
            },
            'is_2fa_enabled': False,
            'is_rfc_2fa_enabled': rfc_2fa,
            'is_yandexoid': False,
            'is_workspace_user': False,
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
        return response

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
        self.env.db.check(
            'attributes',
            'account.rfc_totp.check_time',
            str(TEST_TOTP_CHECK_TIME),
            uid=TEST_UID,
            db='passportdbshard1',
        )
        track = self.track_manager.read(self.track_id)
        ok_(track.allow_authorization)
        ok_(track.is_session_restricted)
        eq_(track.password_verification_passed_at, TimeNow())
        self.check_statbox_entries_xunistater_parsed()

    def test_invalid_otp(self):
        self.setup_blackbox_responses(is_otp_correct=False)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['rfc_otp.invalid'],
            track_id=self.track_id,
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
        ])
        self.env.db.check_missing(
            'attributes',
            'account.rfc_totp.check_time',
            uid=TEST_UID,
            db='passportdbshard1',
        )
        track = self.track_manager.read(self.track_id)
        ok_(not track.allow_authorization)
        ok_(not track.password_verification_passed_at)
        ok_(not track.is_captcha_required)
        self.check_statbox_entries_xunistater_parsed()

    def test_password_change_required(self):
        self.setup_blackbox_responses(password_change_required=True)

        resp = self.make_request()
        expected_response_values = dict(
            track_id=self.track_id,
            state='change_password',
            validation_method='captcha_and_phone',
            change_password_reason='account_hacked',
            number=dump_number(TEST_PHONE_NUMBER),
            account=self.account_response_values(rfc_2fa=True),
        )
        self.assert_ok_response(resp, **expected_response_values)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('submitted'),
            self.env.statbox.entry('redirect_to_password_change'),
        ])
        track = self.track_manager.read(self.track_id)
        ok_(track.is_password_change)
        ok_(track.is_force_change_password)
        eq_(track.change_password_reason, CHANGE_PASSWORD_REASON_HACKED)
        eq_(
            track.submit_response_cache,
            dict(
                expected_response_values,
                status='ok',
            ),
        )
        self.check_statbox_entries_xunistater_parsed()

    def test_password_expired(self):
        with self.track_transaction(self.track_id) as track:
            track.change_password_reason = CHANGE_PASSWORD_REASON_EXPIRED

        resp = self.make_request()
        expected_response_values = dict(
            track_id=self.track_id,
            state='change_password',
            change_password_reason='password_expired',
            validation_method=None,
            account=self.account_response_values(rfc_2fa=True),
        )
        self.assert_ok_response(resp, **expected_response_values)

        track = self.track_manager.read(self.track_id)
        ok_(track.is_password_change)
        ok_(track.is_force_change_password)
        eq_(track.change_password_reason, CHANGE_PASSWORD_REASON_EXPIRED)
        eq_(
            track.submit_response_cache,
            dict(
                expected_response_values,
                status='ok',
            ),
        )
        self.check_statbox_entries_xunistater_parsed()

    def test_invalid_track_state_second_step_not_required(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.is_second_step_required = False
            track.allowed_second_steps = None

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['track.invalid_state'],
            track_id=self.track_id,
        )
        self.check_statbox_entries_xunistater_parsed()

    def test_invalid_track_state_no_field(self):
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.allowed_second_steps = None

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['track.invalid_state'],
            track_id=self.track_id,
        )
        self.check_statbox_entries_xunistater_parsed()

    def test_action_impossible(self):
        self.setup_blackbox_responses(rfc_2fa_on=False)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['action.impossible'],
            track_id=self.track_id,
        )
        self.check_statbox_entries_xunistater_parsed()

    def test_captcha_required__from_previous_step(self):
        """Откуда-то пришли с треком с непройденной капчей - потребуем капчу"""
        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            track_id=self.track_id,
        )
        self.check_statbox_entries_xunistater_parsed()

    def test_captcha_required__counter_limit(self):
        """Счётчик уже перегрет - потребуем капчу"""
        counter = bad_rfc_otp_counter.get_counter()
        for _ in range(2):
            counter.incr(TEST_UID)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        self.check_statbox_entries_xunistater_parsed()

    def test_captcha_required__bad_otp_and_counter_limit(self):
        """Счётчик перегрелся на текущей неудачной проверке otp - потребуем капчу"""
        counter = bad_rfc_otp_counter.get_counter()
        counter.incr(TEST_UID)

        self.setup_blackbox_responses(is_otp_correct=False)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        self.check_statbox_entries_xunistater_parsed()

    def test_counter_limit_reached_captcha_passed_and_good_otp(self):
        """Счётчик уже перегрет, но капча в треке пройдена - пустим с верным otp"""
        counter = bad_rfc_otp_counter.get_counter()
        for _ in range(2):
            counter.incr(TEST_UID)

        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.setup_blackbox_responses(is_otp_correct=True)

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            track_id=self.track_id,
        )
        self.check_statbox_entries_xunistater_parsed()

    def test_counter_limit_reached_captcha_passed_and_bad_otp(self):
        """Счётчик уже перегрет, капча в треке пройдена - с неверным otp потребуем ещё капчу"""
        counter = bad_rfc_otp_counter.get_counter()
        for _ in range(2):
            counter.incr(TEST_UID)

        with self.track_manager.transaction(track_id=self.track_id).rollback_on_error() as track:
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        self.setup_blackbox_responses(is_otp_correct=False)

        resp = self.make_request()
        self.assert_error_response(
            resp,
            ['captcha.required'],
            track_id=self.track_id,
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.is_captcha_required)
        ok_(not track.is_captcha_checked)
        ok_(not track.is_captcha_recognized)
        self.check_statbox_entries_xunistater_parsed()
