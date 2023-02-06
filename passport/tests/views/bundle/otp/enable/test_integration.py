# -*- coding: utf-8 -*-
from base64 import urlsafe_b64encode
import json
import random

import mock
from nose.tools import eq_
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_edit_totp_response,
    blackbox_editsession_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import (
    deep_merge,
    merge_dicts,
)

from .test_base import (
    get_expected_account_response,
    get_headers,
    TEST_APP_SECRET,
    TEST_APP_SECRET_CONTAINER,
    TEST_CONFIRMATION_CODE,
    TEST_IP,
    TEST_LOGIN,
    TEST_OTHER_PHONE_NUMBER,
    TEST_OTHER_PHONE_NUMBER_DUMPED,
    TEST_OTP,
    TEST_PASSWORD,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_PIN,
    TEST_PIN_LENGTH,
    TEST_PUSH_SETUP_SECRET,
    TEST_TOTP_SECRET,
    TEST_UID,
    TOTP_SECRET_ENCRYPTED,
)


@with_settings_hosts(
    SMS_VALIDATION_RESEND_TIMEOUT=0,
    OAUTH_CONSUMER='passport',
    SESSION_REISSUE_INTERVAL=0,
    PASSPORT_SUBDOMAIN='passport-test',
)
class OtpEnableIntegrationTestCase(BaseBundleTestViews, AccountModificationNotifyTestMixin):

    def setUp(self):

        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.code_generator.set_return_value(TEST_CONFIRMATION_CODE)
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'otp': ['edit'],
            'phone_bundle': ['base', 'bind_secure'],
        }))

        self.default_headers = get_headers()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('register')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        expected_secret = TEST_TOTP_SECRET
        expected_pin = TEST_PIN
        self.urandom_mock = mock.Mock(return_value=expected_secret)
        self.system_random_mock = mock.Mock(return_value=expected_pin)
        self.csrf_token_mock = mock.Mock(return_value=TEST_PUSH_SETUP_SECRET)
        self.patches = [
            self.track_id_generator,
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

        self.env.oauth.set_response_value(
            'revalidate', {},
        )
        self.setup_yasms()
        self.setup_social_api()
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(
            ip=TEST_IP,
        )

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator,
        del self.patches
        del self.urandom_mock
        del self.system_random_mock
        del self.csrf_token_mock

    def setup_yasms(self):
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())

    def setup_blackbox(self, uid=TEST_UID, login=TEST_LOGIN, phone=TEST_PHONE_NUMBER, secure_phone=False,
                       sessionid_kwargs=None, serialize=True):
        account_kwargs = dict(
            uid=uid,
            login=login,
            crypt_password='1:crypt',
        )
        if phone:
            phone_builder = build_phone_secured if secure_phone else build_phone_bound
            phone_kwargs = phone_builder(1, phone.e164)
            account_kwargs = deep_merge(account_kwargs, phone_kwargs)

        if sessionid_kwargs is None:
            sessionid_kwargs = {}
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **deep_merge(account_kwargs, sessionid_kwargs)
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                **account_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'edit_totp',
            blackbox_edit_totp_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                ip=TEST_IP,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                **account_kwargs
            ),
        )
        if serialize:
            self.env.db.serialize(blackbox_userinfo_response(**account_kwargs))

        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

    def setup_social_api(self, response=None):
        response = response or {'profiles': []}
        self.env.social_api.set_social_api_response_value(response)

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

    def assert_error_response(self, resp, errors, **kwargs):
        expected = {
            'status': 'error',
            'errors': errors,
        }
        expected.update(kwargs)
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            expected,
        )

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

    def generate_secret(self):
        resp = self.make_request('/1/bundle/otp/enable/get_secret/?consumer=dev', track_id=self.track_id)
        self.assert_ok_response(
            resp,
            pin=TEST_PIN,
            app_secret=TEST_APP_SECRET,
            app_secret_container=TEST_APP_SECRET_CONTAINER,
            pin_length=TEST_PIN_LENGTH,
            push_setup_secret=TEST_PUSH_SETUP_SECRET,
        )

    def do_submit(self, secure_number=None, skip_phone_check=False):
        resp = self.make_request('/2/bundle/otp/enable/submit/?consumer=dev')
        if secure_number:
            secure_number = dict(secure_number)
            secure_number['is_deleting'] = False
        self.assert_ok_response(
            resp,
            account=get_expected_account_response(),
            secure_number=secure_number,
            profiles=[],
            skip_phone_check=skip_phone_check,
        )

    def check_otp(self, is_password_required=False):
        resp = self.make_request(
            '/1/bundle/otp/enable/check_otp/?consumer=dev',
            track_id=self.track_id,
            otp=TEST_OTP,
        )
        self.assert_ok_response(
            resp,
            is_password_required=is_password_required,
        )

    def do_commit(self, current_password=None):
        query_args = dict(
            track_id=self.track_id,
        )
        if current_password:
            query_args['current_password'] = current_password
        resp = self.make_request(
            '/1/bundle/otp/enable/commit/?consumer=dev',
            **query_args
        )
        self.assert_ok_response(
            resp,
            check_cookies=True,
            account=get_expected_account_response(),
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

    def get_state(self, expected_pin=TEST_PIN, is_password_required=False):
        resp = self.make_request('/1/bundle/otp/enable/get_state/?consumer=dev', track_id=self.track_id)
        self.assert_ok_response(
            resp,
            pin=expected_pin,
            app_secret=TEST_APP_SECRET,
            app_secret_container=TEST_APP_SECRET_CONTAINER,
            pin_length=TEST_PIN_LENGTH,
            secure_number=TEST_PHONE_NUMBER_DUMPED,
            is_password_required=is_password_required,
            is_otp_checked=True,
            skip_phone_check=False,
            retpath=None,
            account=get_expected_account_response(),
        )

    def assert_db_ok(self, secret=TOTP_SECRET_ENCRYPTED, dbshard_query_count=2):
        dbshardname = 'passportdbshard1'

        eq_(self.env.db.query_count('passportdbcentral'), 1)
        eq_(self.env.db.query_count(dbshardname), dbshard_query_count)

        self.env.db.check(
            'attributes',
            'account.totp.secret',
            secret,
            uid=TEST_UID,
            db=dbshardname,
        )
        self.env.db.check(
            'attributes',
            'account.global_logout_datetime',
            TimeNow(),
            uid=TEST_UID,
            db=dbshardname,
        )

    def test_ok_with_secure_phone(self):
        """
        У пользователя есть защищенный телефон,
        подтвердим его
        """
        self.setup_blackbox(secure_phone=True)
        self.do_submit(
            secure_number=TEST_PHONE_NUMBER_DUMPED,
        )

        # Подтвердим защищенный телефон
        resp = self.make_request(
            '/1/bundle/phone/confirm_tracked_secure/submit/?consumer=dev',
            track_id=self.track_id,
            display_language='ru',
        )
        self.assert_ok_response(
            resp,
            code_length=6,
            deny_resend_until=TimeNow(),
            number=TEST_PHONE_NUMBER_DUMPED,
            global_sms_id='1',
        )

        resp = self.make_request(
            '/1/bundle/phone/confirm_tracked_secure/commit/?consumer=dev',
            track_id=self.track_id,
            code=TEST_CONFIRMATION_CODE,
        )
        self.assert_ok_response(
            resp,
            with_track_id=False,
            number=TEST_PHONE_NUMBER_DUMPED,
        )

        # Сгенерируем секрет
        self.generate_secret()

        # Проверяем отп
        self.check_otp()

        # Посмотрим состояние
        self.get_state()

        # Подтверждаем включение
        self.do_commit()

        self.assert_db_ok()

        # Убедимся, что второй раз вызвать commit не можем
        resp = self.make_request(
            '/1/bundle/otp/enable/commit/?consumer=dev',
            track_id=self.track_id,
            otp=TEST_OTP,
        )
        self.assert_error_response(
            resp,
            ['action.not_required'],
            track_id=self.track_id,
        )

    def test_ok_with_secure_phone_binding(self):
        """
        У пользователя нет защищенного телефона, привяжем его.
        Пароль просим один раз в момент привязки
        """
        self.setup_blackbox(
            secure_phone=False,
            sessionid_kwargs=dict(
                age=100600,
            ),
        )

        self.do_submit()

        # Привяжем защищенный телефон
        resp = self.make_request(
            '/2/bundle/phone/confirm_and_bind_secure/submit/?consumer=dev',
            track_id=self.track_id,
            display_language='ru',
            number=TEST_PHONE_NUMBER.e164,
        )
        self.assert_ok_response(
            resp,
            code_length=6,
            deny_resend_until=TimeNow(),
            number=TEST_PHONE_NUMBER_DUMPED,
            is_password_required=False,
            global_sms_id='1',
        )
        resp = self.make_request(
            '/2/bundle/phone/confirm_and_bind_secure/commit/?consumer=dev',
            track_id=self.track_id,
            code=TEST_CONFIRMATION_CODE,
            password='321',
        )
        self.assert_ok_response(
            resp,
            with_track_id=False,
            number=TEST_PHONE_NUMBER_DUMPED,
        )
        self.setup_blackbox(secure_phone=True, serialize=False)

        # Сгенерируем секрет
        self.generate_secret()

        # Проверяем отп
        self.check_otp()
        # Посмотрим состояние, пароль не требуется, т.к. был введен
        self.get_state()

        # Подтверждаем включение
        self.do_commit()

        self.assert_db_ok(
            dbshard_query_count=6,
        )

    def test_error_secure_phone_not_equals_to_confirmed_phone_in_track(self):
        """
        У пользователя есть защищенный телефон,
        каким-то образом в треке подтвержден другой телефон.
        """
        self.setup_blackbox(secure_phone=True)

        self.do_submit(
            secure_number=TEST_PHONE_NUMBER_DUMPED,
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_OTHER_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        # Попробуем сгенерировать секрет, получим ошибку
        resp = self.make_request('/1/bundle/otp/enable/get_secret/?consumer=dev', track_id=self.track_id)
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['track.invalid_state'],
            },
        )

    def test_error_secure_phone_not_equals_to_confirmed_phone(self):
        """
        У пользователя есть защищенный телефон,
        но ХАКЕР пытается подтвердить другой телефон.
        """
        self.setup_blackbox(secure_phone=True)

        self.do_submit(
            secure_number=TEST_PHONE_NUMBER_DUMPED,
        )

        # Подтвердим другой телефон
        resp = self.make_request(
            '/1/bundle/phone/confirm/submit/?consumer=dev',
            track_id=self.track_id,
            number=TEST_OTHER_PHONE_NUMBER.e164,
            display_language='ru',
        )
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            {
                'status': 'error',
                'track_id': self.track_id,
                'errors': ['number.invalid'],
                'number': TEST_OTHER_PHONE_NUMBER_DUMPED,
                'global_sms_id': self.env.yasms_fake_global_sms_id_mock.return_value,
            },
        )

    def test_ok_with_edit_pin(self):
        """
        Проверим возможность редактирования пина пользователем
        """
        self.setup_blackbox(secure_phone=True)

        self.do_submit(
            secure_number=TEST_PHONE_NUMBER_DUMPED,
        )

        # Подтвердим защищенный телефон
        resp = self.make_request(
            '/1/bundle/phone/confirm_tracked_secure/submit/?consumer=dev',
            track_id=self.track_id,
            display_language='ru',
        )
        self.assert_ok_response(
            resp,
            code_length=6,
            deny_resend_until=TimeNow(),
            number=TEST_PHONE_NUMBER_DUMPED,
            global_sms_id='1',
        )

        resp = self.make_request(
            '/1/bundle/phone/confirm_tracked_secure/commit/?consumer=dev',
            track_id=self.track_id,
            code=TEST_CONFIRMATION_CODE,
        )
        self.assert_ok_response(
            resp,
            with_track_id=False,
            number=TEST_PHONE_NUMBER_DUMPED,
        )

        # Сгенерируем секрет
        self.generate_secret()

        new_pin = '0011'
        resp = self.make_request(
            '/1/bundle/otp/enable/set_pin/?consumer=dev',
            track_id=self.track_id,
            pin=new_pin,
        )
        self.assert_ok_response(
            resp,
        )

        # Проверяем отп
        self.check_otp()
        # Убедимся, что передали в ЧЯ секрет для шифрования, а также новый пин
        self.env.blackbox.requests[6].assert_post_data_contains(
            {
                'method': 'edit_totp',
                'secret': urlsafe_b64encode(TEST_TOTP_SECRET).decode().rstrip('='),
                'pin': new_pin,
            },
        )

        # Посмотрим состояние
        self.get_state(expected_pin=new_pin)

        # Подтверждаем включение
        self.do_commit()

        self.assert_db_ok()
