# -*- coding: utf-8 -*-

import json
import random

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
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
from passport.backend.core.types.totp_secret import APP_SECRET_LENGTH
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .test_base import (
    get_headers,
    TEST_APP_SECRET,
    TEST_APP_SECRET_CONTAINER,
    TEST_LOGIN,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_PHONE_NUMBER,
    TEST_PIN,
    TEST_PIN_LENGTH,
    TEST_PUSH_SETUP_SECRET,
    TEST_TOTP_SECRET,
    TEST_UID,
)


@with_settings_hosts
class GetSecretTestCase(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')

        self.default_headers = get_headers()
        self.default_params = self.query_params()

        self.setup_blackbox()
        self.setup_track()

        expected_secret = TEST_TOTP_SECRET
        expected_pin = TEST_PIN
        self.urandom_mock = mock.Mock(return_value=expected_secret)
        self.system_random_mock = mock.Mock(return_value=expected_pin)
        self.csrf_token_mock = mock.Mock(return_value=TEST_PUSH_SETUP_SECRET)
        self.patches = [
            mock.patch(
                'os.urandom',
                self.urandom_mock,
            ),
            mock.patch.object(
                random.SystemRandom,
                'uniform',
                self.system_random_mock,
            ),
            mock.patch(
                'passport.backend.api.views.bundle.otp.enable.get_secret.create_csrf_token',
                self.csrf_token_mock,
            ),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        self.env.stop()
        for patch in self.patches:
            patch.stop()
        del self.env
        del self.track_manager
        del self.patches
        del self.urandom_mock
        del self.system_random_mock
        del self.csrf_token_mock

    def setup_track(self, uid=TEST_UID, is_it_otp_enable=True,
                    totp_app_secret=None, totp_pin=None,
                    phone_confirmation_is_confirmed=True):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.is_it_otp_enable = is_it_otp_enable
            if totp_app_secret:
                track.totp_app_secret = totp_app_secret
            if totp_pin:
                track.totp_pin = totp_pin
            track.phone_confirmation_is_confirmed = phone_confirmation_is_confirmed
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

    def setup_blackbox(self, account_kwargs=None):
        if account_kwargs is None:
            account_kwargs = self.get_account_kwargs(TEST_UID, TEST_LOGIN)

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **account_kwargs
            ),
        )

    def query_params(self, **kwargs):
        params = {
            'track_id': self.track_id,
        }
        params.update(kwargs)
        return params

    def make_request(self, params=None, headers=None):
        if not headers:
            headers = self.default_headers
        if not params:
            params = self.default_params
        return self.env.client.post(
            '/1/bundle/otp/enable/get_secret/?consumer=dev',
            data=params,
            headers=headers,
        )

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(track.is_it_otp_enable)
        eq_(track.totp_app_secret, TEST_APP_SECRET)
        eq_(track.push_setup_secret, TEST_PUSH_SETUP_SECRET)
        eq_(track.totp_pin, TEST_PIN)

    def assert_ok_response(self, resp, **kwargs):
        base_response = {
            'status': 'ok',
            'pin': TEST_PIN,
            'track_id': self.track_id,
            'app_secret': TEST_APP_SECRET,
            'app_secret_container': TEST_APP_SECRET_CONTAINER,
            'pin_length': TEST_PIN_LENGTH,
            'push_setup_secret': TEST_PUSH_SETUP_SECRET,
        }
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            merge_dicts(base_response, kwargs),
        )

    def get_account_kwargs(self, uid, login, with_secure_phone=True):
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

    def test_empty_track_error(self):
        resp = self.make_request(params=self.query_params(track_id=''))
        self.assert_error_response(resp, ['track_id.empty'])

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
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
            ),
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
        account_kwargs = self.get_account_kwargs(
            uid=TEST_OTHER_UID,
            login=TEST_OTHER_LOGIN,
        )
        self.setup_blackbox(account_kwargs)
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

    def test_phone_was_not_confirmed(self):
        self.setup_track(phone_confirmation_is_confirmed=False)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_generate_validation_error(self):
        """
        Проверим, что производим генерацию секрета, удовлетворяющего валидному пину,
        нужное количество раз и потом возвращаем ошибку
        """
        self.system_random_mock.return_value = 1111
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['pin.weak'])
        eq_(self.urandom_mock.call_count, 5)
        eq_(self.system_random_mock.call_count, 5)

    def test_no_secure_phone_error(self):
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login=TEST_LOGIN,
            with_secure_phone=False,
        )
        self.setup_blackbox(account_kwargs)
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response_with_track_id(resp, ['phone_secure.not_found'])

    def test_ok_generate_new_secret(self):
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()
        self.urandom_mock.assert_called_once_with(APP_SECRET_LENGTH)

    def test_ok_retrive_saved_secret(self):
        self.setup_track(
            totp_pin=TEST_PIN,
            totp_app_secret=TEST_APP_SECRET,
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(resp)
        eq_(self.urandom_mock.call_count, 0)

    def test_other_account_in_session_error(self):
        """
        Пришли в ручку с мультикукой, в которой нет аккаунта, начавшего процесс.
        """
        account_kwargs = self.get_account_kwargs(
            uid=TEST_OTHER_UID,
            login=TEST_OTHER_LOGIN,
        )
        self.setup_blackbox(account_kwargs)
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_error_response(resp, ['track.invalid_state'], track_id=self.track_id)

    def test_account_in_session_not_default_and_invalid_error(self):
        """
        Пришли в ручку с мультикукой, в которой аккаунт, начавший процесс не дефолтный и невалидный.
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
        self.assert_error_response(resp, ['sessionid.invalid'], track_id=self.track_id)

    def test_account_in_session_not_default_and_valid_ok(self):
        """
        Пришли в ручку с мультикукой, в которой аккаунт,
        начавший процесс не дефолтный но валидный. Все ок, продолжаем.
        """
        account_kwargs = self.get_account_kwargs(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_OTHER_UID,
                    login='other_login',
                ),
                **account_kwargs
            ),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()
        self.urandom_mock.assert_called_once_with(APP_SECRET_LENGTH)
