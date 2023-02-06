# -*- coding: utf-8 -*-

import base64
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_data_equals
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_edit_totp_response,
    blackbox_sessionid_multi_append_invalid_session,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import get_unixtime

from .test_base import (
    get_headers,
    TEST_APP_SECRET,
    TEST_LOGIN,
    TEST_OTHER_UID,
    TEST_OTP,
    TEST_PHONE_NUMBER,
    TEST_PIN,
    TEST_TOTP_CHECK_TIME,
    TEST_TOTP_SECRET,
    TEST_UID,
    TOTP_JUNK_SECRET_ENCRYPTED,
)


DB_SHARD_NAME = 'passportdbshard1'


@with_settings_hosts
class CheckOtpTestCase(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        self.default_headers = get_headers()
        self.default_params = self.query_params()

        self.setup_blackbox()
        self.setup_track()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_track(self, uid=TEST_UID, is_it_otp_enable=True, totp_app_secret=TEST_APP_SECRET,
                    totp_pin=TEST_PIN, phone_confirmation_is_confirmed=True,
                    password_verification_passed_at=None):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.is_it_otp_enable = is_it_otp_enable
            track.totp_app_secret = totp_app_secret
            if totp_pin:
                track.totp_pin = totp_pin
            track.phone_confirmation_is_confirmed = phone_confirmation_is_confirmed
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            if password_verification_passed_at:
                track.password_verification_passed_at = password_verification_passed_at

    def setup_blackbox(self, uid=TEST_UID, login=TEST_LOGIN):
        account_kwargs = self.default_account_kwargs(uid, login)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **account_kwargs
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'edit_totp',
            blackbox_edit_totp_response(totp_check_time=TEST_TOTP_CHECK_TIME),
        )

    def query_params(self, **kwargs):
        params = {
            'track_id': self.track_id,
            'otp': TEST_OTP,
        }
        params.update(kwargs)
        return params

    def make_request(self, params=None, headers=None):
        if not headers:
            headers = self.default_headers
        if not params:
            params = self.default_params
        return self.env.client.post(
            '/1/bundle/otp/enable/check_otp/?consumer=dev',
            data=params,
            headers=headers,
        )

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(track.is_it_otp_enable)
        ok_(track.is_otp_checked)
        eq_(track.totp_secret_ids, {'1': TimeNow()})
        eq_(track.blackbox_totp_check_time, str(TEST_TOTP_CHECK_TIME))
        eq_(track.totp_secret_encrypted, 'encrypted_secret')

    def assert_blackbox_edit_totp_called(self, password=TEST_OTP, callnum=1):
        args = {
            'uid': int(TEST_UID),
            'format': 'json',
            'method': 'edit_totp',
            'op': 'create',
            'pin': TEST_PIN,
            'secret': base64.urlsafe_b64encode(TEST_TOTP_SECRET).decode().rstrip('='),
            'secret_id': 1,
            'password': password,
        }
        assert_builder_data_equals(
            self.env.blackbox,
            args,
            callnum=callnum,
        )

    def assert_ok_response(self, resp, **kwargs):
        base_response = {
            'status': 'ok',
            'track_id': self.track_id,
            'is_password_required': False,
        }
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            merge_dicts(base_response, kwargs),
        )

    def default_account_kwargs(self, uid=TEST_UID, login=TEST_LOGIN, with_secure_phone=True):
        account_kwargs = dict(
            uid=uid,
            login=login,
            crypt_password='1:crypt',
        )
        phone_builder = build_phone_secured if with_secure_phone else build_phone_bound
        phone = phone_builder(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        return deep_merge(account_kwargs, phone)

    def assert_blackbox_sessionid_called(self):
        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

        self.env.blackbox.requests[0].assert_query_contains({
            'full_info': 'yes',
            'multisession': 'yes',
            'method': 'sessionid',
            'sessionid': '0:old-session',
            'sslsessionid': '0:old-sslsession',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

    def check_db(self, is_otp_correct=True):
        if is_otp_correct:
            self.env.db.check_missing(
                'attributes',
                'account.totp.junk_secret',
                uid=TEST_UID,
                db=DB_SHARD_NAME,
            )
        else:
            self.env.db.check(
                'attributes',
                'account.totp.junk_secret',
                TOTP_JUNK_SECRET_ENCRYPTED,
                uid=TEST_UID,
                db=DB_SHARD_NAME,
            )

    def test_empty_track_error(self):
        resp = self.make_request(params=self.query_params(track_id=''))
        self.assert_error_response(resp, ['track_id.empty'])

    def test_empty_pin_error(self):
        resp = self.make_request(params=self.query_params(otp=''))
        self.assert_error_response(resp, ['otp.empty'])

    def test_empty_cookies_error(self):
        resp = self.make_request(headers=get_headers(cookie=''))
        self.assert_error_response_with_track_id(resp, ['sessionid.invalid'])

    def test_bad_cookies_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['sessionid.invalid'])

    def test_account_disabled_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_UID, enabled=False),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.disabled'])

    def test_account_disabled_on_deletion_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.disabled_on_deletion'])

    def test_action_not_required_error(self):
        """
        Пришли в ручку, а секрет уже установлен на аккаунте
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:crypt',
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['action.not_required'])

    def test_account_uid_not_match_track(self):
        """
        Пришли с кукой, в которой другой аккаунт дефолтный
        """
        self.setup_blackbox(uid=TEST_OTHER_UID, login='lala1')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_track_not_for_otp_enable_error(self):
        self.setup_track(is_it_otp_enable=False)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_no_uid_in_track_error(self):
        self.setup_track(uid='')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_sercret_was_not_generated_error(self):
        self.setup_track(totp_app_secret='', totp_pin='')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_no_secure_phone_error(self):
        account_kwargs = self.default_account_kwargs(with_secure_phone=False)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **account_kwargs
            ),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response_with_track_id(resp, ['phone_secure.not_found'])

    def test_bad_otp_error(self):
        """
        Пользователь ввел неправильный otp
        """
        self.env.blackbox.set_blackbox_response_value(
            'edit_totp',
            blackbox_edit_totp_response(status=False, encrypted_secret=TOTP_JUNK_SECRET_ENCRYPTED),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_edit_totp_called()
        self.assert_error_response_with_track_id(resp, ['otp.not_matched'], invalid_otp_count=1)
        self.check_db(is_otp_correct=False)

    def test_ok(self):
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_edit_totp_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()
        self.check_db()

    def test_ok_with_old_cookie_but_password_not_required(self):
        """
        Пришли с несвежей кукой, но пароль уже вводили на предыдущих шагах,
        сообщаем, что пароль не нужен
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                age=100500,
                **self.default_account_kwargs()
            ),
        )
        self.setup_track(password_verification_passed_at=get_unixtime())
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_edit_totp_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_other_account_in_session_error(self):
        """
        Пришли в ручку с мультикукой, в которой нет аккаунта, начавшего процесс.
        """
        self.setup_blackbox(uid=TEST_OTHER_UID)
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_account_in_session_not_default_and_invalid_error(self):
        """
        Пришли в ручку с мультикукой, в которой аккаунт, начавший процесс недефолтный и невалидный.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_invalid_session(
                blackbox_sessionid_multi_response(
                    uid=TEST_OTHER_UID,
                    login='other_login',
                ),
                item_id=TEST_UID,
                status=BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response_with_track_id(resp, ['sessionid.invalid'])

    def test_account_in_session_not_default_and_valid_ok(self):
        """
        Пришли в ручку с мультикукой, в которой аккаунт,
        начавший процесс, недефолтный но валидный. Все ок, продолжаем.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_OTHER_UID,
                    login='other_login',
                ),
                **self.default_account_kwargs()
            ),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_edit_totp_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()
