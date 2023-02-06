# -*- coding: utf-8 -*-

import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import EmailTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders.base.faker.fake_builder import (
    assert_builder_data_equals,
    assert_builder_url_contains_params,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
    BLACKBOX_LOGIN_DISABLED_STATUS,
    BLACKBOX_LOGIN_NOT_FOUND_STATUS,
    BLACKBOX_LOGIN_UNKNOWN_STATUS,
    BLACKBOX_LOGIN_VALID_STATUS,
    BLACKBOX_PASSWORD_BAD_STATUS,
    BLACKBOX_PASSWORD_UNKNOWN_STATUS,
    BLACKBOX_PASSWORD_VALID_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_login_response,
    blackbox_sessionid_multi_append_invalid_session,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .test_base import (
    get_headers,
    TEST_LOGIN,
    TEST_OTHER_UID,
    TEST_OTP,
    TEST_PHONE_NUMBER,
    TEST_UID,
)


class CheckOtpTestCaseBase(BaseBundleTestViews, EmailTestMixin):

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

    def setup_track(self, uid=TEST_UID, is_it_otp_disable=True,
                    is_captcha_required=False, is_captcha_recognized=True,
                    blackbox_login_status='', blackbox_password_status=''):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = uid
            track.is_it_otp_disable = is_it_otp_disable
            track.is_captcha_required = is_captcha_required
            track.is_captcha_checked = is_captcha_required
            track.is_captcha_recognized = is_captcha_recognized
            track.blackbox_login_status = blackbox_login_status
            track.blackbox_password_status = blackbox_password_status

    def default_account_kwargs(self, uid=TEST_UID, login=TEST_LOGIN):
        account_args = dict(
            uid=uid,
            login=login,
            attributes={'account.2fa_on': '1'},
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        phone_args = build_phone_secured(
            phone_id=1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        return deep_merge(account_args, phone_args)

    def setup_blackbox(self, uid=TEST_UID, login=TEST_LOGIN):
        account_kwargs = self.default_account_kwargs(uid, login)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**account_kwargs),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**account_kwargs),
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
            '/1/bundle/otp/disable/check_otp/?consumer=dev',
            data=params,
            headers=headers,
        )

    def assert_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        ok_(track.is_it_otp_disable)
        ok_(track.is_otp_checked)
        ok_(track.can_use_secure_number_for_password_validation)
        eq_(track.secure_phone_number, TEST_PHONE_NUMBER.e164)
        ok_(track.blackbox_login_status, BLACKBOX_LOGIN_VALID_STATUS)
        ok_(track.blackbox_password_status, BLACKBOX_PASSWORD_VALID_STATUS)
        ok_(not track.is_captcha_required)
        eq_(track.login, TEST_LOGIN)

    def assert_blackbox_sessionid_called(self):
        params = {
            'full_info': 'yes',
            'multisession': 'yes',
            'method': 'sessionid',
            'sessionid': '0:old-session',
            'sslsessionid': '0:old-sslsession',
            'emails': 'getall',
        }
        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })
        params.update({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        assert_builder_url_contains_params(
            self.env.blackbox,
            params,
            callnum=0,
        )

    def assert_blackbox_login_called(self, password=TEST_OTP, callnum=1):
        args = {
            'aliases': 'all_with_hidden',
            'authtype': authtypes.AUTH_TYPE_VERIFY,
            'format': 'json',
            'full_info': 'yes',
            'get_badauth_counts': 'yes',
            'get_public_name': 'yes',
            'is_display_name_empty': 'yes',
            'method': 'login',
            'password': password,
            'regname': 'yes',
            'uid': int(TEST_UID),
            'useragent': 'curl',
            'ver': '2',
            'yandexuid': 'testyandexuid',
        }
        assert_builder_data_equals(
            self.env.blackbox,
            args,
            callnum=callnum,
            exclude_fields=[
                'userip',  # возвращается инстансом внутреннего класса в libipreg
            ],
        )

    def assert_ok_response(self, resp, **kwargs):
        base_response = {
            'status': 'ok',
            'track_id': self.track_id,
            'state': 'otp_auth_finished',
        }
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            merge_dicts(base_response, kwargs),
        )


@with_settings_hosts()
class CheckOtpTestCase(CheckOtpTestCaseBase):

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
        Пришли в ручку, а 2fa уже отключена
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                crypt_password='1:crypt',
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['action.not_required'])

    def test_account_uid_not_match_track(self):
        """
        Пришли с кукой, в которой другой аккаунт
        """
        self.setup_blackbox(uid=TEST_OTHER_UID, login='lala1')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_track_not_for_otp_disable_error(self):
        self.setup_track(is_it_otp_disable=False)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_no_uid_in_track_error(self):
        self.setup_track(uid='')
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['track.invalid_state'])

    def test_captcha_not_recognized_error(self):
        self.setup_track(is_captcha_required=True, is_captcha_recognized=False)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['captcha.required'])
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_otp_checked)

    def test_blackbox_unknown_status_error(self):
        """
        ЧЯ почему-то вернул статус UNKNOWN для логина или пароля
        """
        for status in [
            BLACKBOX_LOGIN_UNKNOWN_STATUS,
            BLACKBOX_PASSWORD_UNKNOWN_STATUS,
        ]:
            self.env.blackbox.set_blackbox_response_value(
                'login',
                blackbox_login_response(
                    password_status=status,
                ),
            )
            resp = self.make_request()
            self.assert_error_response_with_track_id(resp, ['backend.blackbox_failed'])
            # Удостоверимся, что не кешируем такой ответ ЧЯ
            track = self.track_manager.read(self.track_id)
            eq_(track.blackbox_login_status, '')
            eq_(track.blackbox_password_status, '')

    def test_blackbox_unexpected_response_error(self):
        """
        ЧЯ вернул что-то странное при запросе в метод login,
        то, чего возвращать он никак не должен. Проверим, что корректно
        отработаем данную ситуацию.
        """

        self.env.blackbox.set_blackbox_response_value(
            'login',
            json.dumps(
                {
                    'error': 'ok',
                    'login_status': {
                        'id': 111,
                        'value': 'upyachka',
                    },
                    'password_status': {
                        'id': 111,
                        'value': 'upyachka',
                    },
                },
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['backend.blackbox_permanent_error'])

    def test_blackbox_bad_password_for_account_not_found_error(self):
        """
        Пришли с аккаунтом, про который ЧЯ говорит что не найден,
        при этом возвращая password_status='BAD'. Отловили такую ошибку в проде,
        ЧЯ действительно такое мог возвратить!
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=BLACKBOX_LOGIN_NOT_FOUND_STATUS,
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.not_found'])

    def test_blackbox_account_disabled_status_error(self):
        """
        Метод login сказал, что аккаунт заблокирован при проверке otp
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=BLACKBOX_LOGIN_DISABLED_STATUS,
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.disabled'])

    def test_blackbox_account_disabled_on_deletion_error(self):
        """
        Метод login сказал, что аккаунт заблокирован при проверке otp,
        и у аккаунта есть подписка на блокирующие сиды.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                attributes={
                    'account.2fa_on': '1',
                    'account.is_disabled': '2',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(login_status=BLACKBOX_LOGIN_DISABLED_STATUS),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.disabled_on_deletion'])

    def test_blackbox_account_not_found_status_error(self):
        """
        Метод login сказал, что аккаунт не найден при проверке otpp
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                login_status=BLACKBOX_LOGIN_NOT_FOUND_STATUS,
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['account.not_found'])

    def test_bad_otp_error(self):
        """
        Ввели неправильный одноразовый пароль
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['password.not_matched'])
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called()
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_otp_checked)

    def test_magic_no_blackbox_calls_on_errors(self):
        """
        Проверим, что при магическом сценарии для случаев, когда аккаунт не найден,
        заблокирован или не подошел пароль, мы не ходим второй раз method=login в ЧЯ,
        а пользуемся знанием из трека.
        """
        for login_status, password_status, error_code in (
                (
                    BLACKBOX_LOGIN_VALID_STATUS,
                    BLACKBOX_PASSWORD_BAD_STATUS,
                    'password.not_matched',
                ),
                (
                    BLACKBOX_LOGIN_DISABLED_STATUS,
                    '',
                    'account.disabled',
                ),
                (
                    BLACKBOX_LOGIN_NOT_FOUND_STATUS,
                    '',
                    'account.not_found',
                ),
        ):
            self.setup_track(blackbox_login_status=login_status, blackbox_password_status=password_status)
            with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
                track.otp = 'magic'
            resp = self.make_request(params=dict(track_id=self.track_id))
            self.assert_error_response_with_track_id(resp, [error_code])
            # вызывали только method=sessionid
            self.assert_blackbox_sessionid_called()
            eq_(self.env.blackbox._mock.request.call_count, 1)
            self.env.blackbox._mock.request.reset_mock()
            track = self.track_manager.read(self.track_id)
            ok_(not track.is_otp_checked)

    def test_blackbox_brute_force_captcha_required_error(self):
        """
        ЧЯ потребовал капчу первый раз при неправильном пароле
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['captcha.required'])
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called()
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_otp_checked)

    def test_blackbox_brute_force_captcha_required_and_ok_otp_error(self):
        """
        ЧЯ потребовал капчу первый раз, пароль был правильный
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_VALID_STATUS,
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['captcha.required'])
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called()
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_otp_checked)
        eq_(track.blackbox_login_status, BLACKBOX_LOGIN_VALID_STATUS)
        eq_(track.blackbox_password_status, BLACKBOX_PASSWORD_VALID_STATUS)
        eq_(track.bruteforce_status, BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS)

    def test_blackbox_brute_force_captcha_required_and_passed_error(self):
        """
        ЧЯ потребовал капчу при неправильном пароле,
        капчу ввели, но пароль все еще неправильный.
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )
        self.setup_track(is_captcha_required=True, is_captcha_recognized=True)
        resp = self.make_request()
        self.assert_error_response_with_track_id(resp, ['captcha.required', 'password.not_matched'])
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called()
        track = self.track_manager.read(self.track_id)
        ok_(not track.is_otp_checked)
        ok_(track.is_captcha_required)

    def test_magic_not_ready(self):
        """
        Магический сценарий, пароль еще не сохранен в треке,
        и нам об этом говорят.
        """
        resp = self.make_request(params=dict(track_id=self.track_id))
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(resp, state='otp_auth_not_ready')

    def test_ok(self):
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_ok_ensure_blackbox_cached_reset(self):
        """
        Проверяем немагический сценарий - отп передан, и в треке есть
        закешированные значения вызова ЧЯ. Удостоверимся, что они сбрасываются
        в этом случае и идем в ЧЯ по-новому.
        """
        self.setup_track(
            blackbox_login_status=BLACKBOX_LOGIN_VALID_STATUS,
            blackbox_password_status=BLACKBOX_PASSWORD_BAD_STATUS,
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_magic(self):
        """
        Магический сценарий, пароль сохранен в треке,
        проверим его и получим ок.
        """
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
            is_default=False,
        )
        account_kwargs = self.default_account_kwargs()
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**account_kwargs),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = 'magic'

        resp = self.make_request(params=dict(track_id=self.track_id))

        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called(password='magic')
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_ok_with_captcha_required_and_recognized(self):
        """
        Капча требовалась и ее успешно ввели,
        пароль правильный - все хорошо
        """
        self.setup_track(is_captcha_required=True, is_captcha_recognized=True)
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_ok_with_captcha_required_and_recognized_and_blackbox_bruteforce(self):
        """
        Капча требовалась и ее успешно ввели,
        пароль правильный, ЧЯ вернул брутфорс - все хорошо
        """
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_VALID_STATUS,
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )
        self.setup_track(is_captcha_required=True, is_captcha_recognized=True)
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_blackbox_login_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_magic_ok_with_captcha_required_and_saved_password_ok(self):
        """
        Магический сценарий, пароль сохранен в треке,
        капча требовалась и ее успешно ввели,
        а пароль ввели успешно до этого, удостоверимся, что не полезем в ЧЯ
        """
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = 'magic'

        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
            ),
        )
        self.setup_track(
            is_captcha_required=True,
            is_captcha_recognized=True,
            blackbox_login_status=BLACKBOX_LOGIN_VALID_STATUS,
            blackbox_password_status=BLACKBOX_PASSWORD_VALID_STATUS,
        )
        resp = self.make_request(params=dict(track_id=self.track_id))
        self.assert_blackbox_sessionid_called()
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
        начавший процесс недефолтный, но валидный. Все ок, продолжаем.
        """
        account_args = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            attributes={'account.2fa_on': '1'},
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
        )
        phone_args = build_phone_secured(
            phone_id=1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        sessionid_args = deep_merge(account_args, phone_args)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_OTHER_UID,
                    login='other_login',
                ),
                **sessionid_args
            ),
        )
        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()

    def test_67_sid_track_flag_ok(self):
        """
        Проверим, что сохраняем в трек знание о 67 сиде
        """
        account_args = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            attributes={'account.2fa_on': '1'},
            emails=[
                self.create_native_email(TEST_LOGIN, 'yandex.ru'),
            ],
            subscribed_to=[67],
        )
        phone_args = build_phone_secured(
            phone_id=1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        sessionid_args = deep_merge(account_args, phone_args)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(**sessionid_args),
        )

        resp = self.make_request()
        self.assert_blackbox_sessionid_called()
        self.assert_ok_response(resp)
        self.assert_track_ok()

        track = self.track_manager.read(self.track_id)
        eq_(track.is_strong_password_policy_required, True)
