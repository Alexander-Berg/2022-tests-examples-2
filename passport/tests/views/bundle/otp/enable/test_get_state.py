# -*- coding: utf-8 -*-

import json

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .test_base import (
    get_expected_account_response,
    get_headers,
    TEST_APP_SECRET,
    TEST_APP_SECRET_CONTAINER,
    TEST_LOGIN,
    TEST_OTHER_UID,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_PIN,
    TEST_PIN_LENGTH,
    TEST_UID,
)


class GetStateTestCaseBase(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')

        self.default_headers = get_headers()
        self.default_params = self.query_params()
        self.setup_track()

    def get_account_kwargs(self, uid=TEST_UID, login=TEST_LOGIN, phone_id=1, phone=TEST_PHONE_NUMBER, secure_phone=False, **kwargs):
        account_kwargs = dict(
            uid=uid,
            login=login,
            **kwargs
        )
        if phone:
            phone_builder = build_phone_secured if secure_phone else build_phone_bound
            phone_kwargs = phone_builder(phone_id, phone.e164)
            account_kwargs = deep_merge(account_kwargs, phone_kwargs)
        return account_kwargs

    def setup_account(self, account_kwargs=None, sessionid_kwargs=None):
        if account_kwargs is None:
            account_kwargs = self.get_account_kwargs(
                secure_phone=False,
                crypt_password='1:crypt',
            )
        if sessionid_kwargs is None:
            sessionid_kwargs = {}
        params = merge_dicts(account_kwargs, sessionid_kwargs)

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**params),
        )
        self.env.db.serialize(
            blackbox_userinfo_response(**account_kwargs),
        )

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_track(self, uid=TEST_UID, is_it_otp_enable=True,
                    totp_app_secret=None, totp_pin=None,
                    session=None, retpath=None):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.is_it_otp_enable = is_it_otp_enable
            if totp_app_secret:
                track.totp_app_secret = totp_app_secret
            if totp_pin:
                track.totp_pin = totp_pin
            if session:
                track.session = session
            if retpath:
                track.retpath = retpath

    def query_params(self, **kwargs):
        params = {
            'track_id': self.track_id,
        }
        params.update(kwargs)
        return params

    def make_request(self, params=None, headers=None):
        return self.env.client.post(
            '/1/bundle/otp/enable/get_state/?consumer=dev',
            data=params or self.default_params,
            headers=headers or self.default_headers,
        )

    def assert_blackbox_sessionid_called(self):
        self.env.blackbox.requests[0].assert_query_contains(
            {
                'method': 'sessionid',
                'multisession': 'yes',
                'getphones': 'all',
                'getphoneoperations': '1',
                'getphonebindings': 'all',
                'aliases': 'all_with_hidden',
                'full_info': 'yes',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
            },
        )
        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })

    def assert_ok_response(self, resp, **kwargs):
        base_response = {
            'status': 'ok',
            'track_id': self.track_id,
            'secure_number': None,
            'is_password_required': False,
            'is_otp_checked': False,
            'skip_phone_check': False,
            'retpath': None,
            'account': get_expected_account_response(),
        }
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            merge_dicts(base_response, kwargs),
        )


@with_settings_hosts
class GetStateTestCase(GetStateTestCaseBase):

    def test_empty_track_error(self):
        self.setup_account()
        resp = self.make_request(params=self.query_params(track_id=''))
        self.assert_error_response(resp, ['track_id.empty'])

    def test_empty_cookies_error(self):
        self.setup_account()
        resp = self.make_request(headers=get_headers(cookie=''))
        self.assert_error_response_with_track_id(resp, ['sessionid.invalid'], retpath=None)

    def test_bad_cookies_error(self):
        sessionid_kwargs = dict(
            status=BLACKBOX_SESSIONID_INVALID_STATUS,
        )
        self.setup_account(sessionid_kwargs=sessionid_kwargs)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['sessionid.invalid'], retpath=None)

    def test_account_disabled_error(self):
        account_kwargs = self.get_account_kwargs(enabled=False)
        sessionid_kwargs = dict(
            enabled=False,
        )
        self.setup_account(
            account_kwargs=account_kwargs,
            sessionid_kwargs=sessionid_kwargs,
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.disabled'], retpath=None)

    def test_account_disabled_on_deletion_error(self):
        account_kwargs = deep_merge(
            self.get_account_kwargs(),
            dict(
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        self.setup_account(
            account_kwargs=account_kwargs,
            sessionid_kwargs=dict(enabled=False),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.disabled_on_deletion'], retpath=None)

    def test_account_uid_not_match_track(self):
        """
        Пришли с кукой, в которой другой аккаунт дефолтный
        """
        self.setup_account(
            account_kwargs=self.get_account_kwargs(uid=TEST_OTHER_UID, login='lala1'),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'], retpath=None)

    def test_track_not_for_otp_enable_error(self):
        self.setup_track(is_it_otp_enable=False)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'], retpath=None)

    def test_no_uid_in_track_error(self):
        self.setup_track(uid='')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'], retpath=None)

    def test_process_finished_on_this_track_error(self):
        """
        Проверим, что при завершившемся процессе на переданном треке вернем
        ошибку и retpath
        """
        self.setup_track(session='1:session', retpath='http://yandex.ru')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['action.not_required'], retpath='http://yandex.ru')

    def test_no_secure_phone_no_secret(self):
        self.setup_account()
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(resp)

    def test_with_secure_phone_no_secret(self):
        self.setup_account(
            account_kwargs=self.get_account_kwargs(secure_phone=True),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(
            resp,
            secure_number=TEST_PHONE_NUMBER_DUMPED,
        )

    def test_with_secret(self):
        self.setup_account()
        self.setup_track(
            totp_app_secret=TEST_APP_SECRET,
            totp_pin=TEST_PIN,
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(
            resp,
            pin=TEST_PIN,
            app_secret=TEST_APP_SECRET,
            app_secret_container=TEST_APP_SECRET_CONTAINER,
            pin_length=TEST_PIN_LENGTH,
        )

    def test_process_completed(self):
        account_kwargs = self.get_account_kwargs()
        account_kwargs = deep_merge(
            account_kwargs,
            dict(
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.setup_account(
            account_kwargs=account_kwargs,
        )
        self.setup_track(
            totp_app_secret=TEST_APP_SECRET,
            totp_pin=TEST_PIN,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'], track_id=self.track_id, retpath=None)
