# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
    BLACKBOX_PASSWORD_BAD_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_editsession_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_pwdhistory_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.builders.captcha.faker import captcha_response_check
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .test_base import (
    get_headers,
    TEST_IP,
    TEST_LOGIN,
    TEST_OTP,
    TEST_PASSWORD,
    TEST_PHONE_NUMBER,
    TEST_UID,
)


@with_settings_hosts(
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    OAUTH_CONSUMER='passport',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    SESSION_REISSUE_INTERVAL=0,
    PASSPORT_SUBDOMAIN='passport-test',
    ACCOUNT_MODIFICATION_PUSH_ENABLE={'app_password_add'},
    ACCOUNT_MODIFICATION_NOTIFY_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={
            'push:login_method_change': 5,
            'email:login_method_change': 5,
        },
    )
)
class OtpDisableIntegrationTestCase(BaseBundleTestViews, AccountModificationNotifyTestMixin):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'otp': ['edit'],
            'captcha': ['*'],
        }))

        self.default_headers = get_headers()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.setup_blackbox()
        self.setup_shakur()
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def setup_blackbox(self):
        account_args = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            attributes={'account.2fa_on': '1'},
        )
        phone_args = build_phone_secured(
            phone_id=1,
            phone_number=TEST_PHONE_NUMBER.e164,
        )
        args = deep_merge(account_args, phone_args)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **args
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**args),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                ip=TEST_IP,
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

    def setup_shakur(self):
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def make_request(self, url, headers=None, **kwargs):
        if not headers:
            headers = self.default_headers
        return self.env.client.post(url, data=kwargs, headers=headers)

    def get_expected_account_response(self):
        return {
            'person': {
                'firstname': u'\\u0414',
                'language': u'ru',
                'gender': 1,
                'birthday': u'1963-05-15',
                'lastname': u'\\u0424',
                'country': u'ru',
            },
            'display_name': {u'default_avatar': u'', u'name': u''},
            'login': TEST_LOGIN,
            'uid': int(TEST_UID),
            'display_login': TEST_LOGIN,
        }

    def assert_cookies_ok(self, cookies):
        eq_(len(cookies), 7)
        l_cookie, sessionid_cookie, mda2_beacon, sessionid2_cookie, yalogin_cookie, yp_cookie, ys_cookie = sorted(cookies)
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2_cookie, 'sessionid2', expires=None, http_only=True, secure=True)
        self.assert_cookie_ok(yalogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(mda2_beacon, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

    def assert_ok_response(self, resp, with_track_id=True, check_cookies=False, **kwargs):
        base_response = {
            'status': 'ok',
        }
        if with_track_id:
            base_response['track_id'] = self.track_id

        body = json.loads(resp.data)
        if check_cookies:
            eq_(body.pop('default_uid', None), TEST_UID)
            cookies = body.pop('cookies', [])
            self.assert_cookies_ok(cookies)

        eq_(resp.status_code, 200)
        eq_(
            body,
            merge_dicts(base_response, kwargs),
        )

    def check_otp(self):
        resp = self.make_request(
            '/1/bundle/otp/disable/check_otp/?consumer=dev',
            track_id=self.track_id,
            otp=TEST_OTP,
        )
        self.assert_ok_response(resp, state='otp_auth_finished')

    def do_submit(self):
        resp = self.make_request('/1/bundle/otp/disable/submit/?consumer=dev')
        self.assert_ok_response(
            resp,
            account=self.get_expected_account_response(),
            revokers={
                'default': {
                    'tokens': True,
                    'web_sessions': True,
                    'app_passwords': True,
                },
                'allow_select': True,
            },
        )

    def do_commit(self):
        resp = self.make_request(
            '/1/bundle/otp/disable/commit/?consumer=dev',
            track_id=self.track_id,
            password=TEST_PASSWORD,
        )
        self.assert_ok_response(
            resp,
            check_cookies=True,
            account=self.get_expected_account_response(),
            accounts=[
                {
                    'login': TEST_LOGIN,
                    'display_name': {'default_avatar': '', 'name': ''},
                    'uid': int(TEST_UID),
                    'display_login': TEST_LOGIN,
                },
            ],
            retpath=None,
        )

    def check_captcha(self):
        captcha_response = captcha_response_check()
        self.env.captcha_mock.set_response_value('check', captcha_response)
        resp = self.make_request(
            '/1/captcha/check/?consumer=dev',
            answer='a',
            key='b',
            track_id=self.track_id,
        )
        self.assert_ok_response(resp, correct=True, with_track_id=False)

    def test_ok(self):
        """
        Проходим сценарий - выключаем 2fa,
        капчи нет, все хорошо.
        """
        self.do_submit()

        # Проверим одноразовый пароль
        self.check_otp()

        # Подтверждаем выключение
        self.do_commit()

        # Убедимся, что второй раз вызвать commit не можем
        resp = self.make_request(
            '/1/bundle/otp/disable/commit/?consumer=dev',
            track_id=self.track_id,
            password=TEST_PASSWORD,
        )
        self.assert_error_response(
            resp,
            ['action.not_required'],
            track_id=self.track_id,
        )

    def test_magic_ok_with_saving_blackbox_ok_response_state(self):
        """
        Проходим сценарий - при выключении 2fa убедимся,
        что не перезапрашиваем проверку логина-пароля в ЧЯ,
        если пароль ввели правильно с первого раза в результате магии,
        а капчу ввели со второй попытки.
        """
        self.do_submit()

        # Проверим одноразовый пароль, пароль ок,
        # капча не ок.
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                attributes={'account.2fa_on': '1'},
                bruteforce_policy=BLACKBOX_BRUTEFORCE_CAPTCHA_STATUS,
            ),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.otp = 'magic'
        resp = self.make_request(
            '/1/bundle/otp/disable/check_otp/?consumer=dev',
            track_id=self.track_id,
        )
        self.assert_error_response_with_track_id(resp, ['captcha.required'])

        # проверим капчу
        self.check_captcha()

        # ЧЯ теперь ответит, что отп протух, если в него сходить,
        # но ходить мы туда не должны
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                password_status=BLACKBOX_PASSWORD_BAD_STATUS,
                attributes={'account.2fa_on': '1'},
            ),
        )
        # Еще раз проверяем пароль и убеждаемся,
        # что в ЧЯ не ходим
        resp = self.make_request(
            '/1/bundle/otp/disable/check_otp/?consumer=dev',
            track_id=self.track_id,
        )
        self.assert_ok_response(resp, state='otp_auth_finished')

        # Подтверждаем выключение
        self.do_commit()


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class OtpDisableIntegrationTestCaseNoBlackboxHash(OtpDisableIntegrationTestCase):
    pass
