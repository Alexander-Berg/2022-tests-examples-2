# -*- coding: utf-8 -*-

import json

import mock
from nose.tools import eq_
from passport.backend.api.views.bundle.auth.social.base import OUTPUT_MODE_SESSIONID
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_url_params_equal
from passport.backend.core.builders.social_api.faker.social_api import task_data_response
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base_test_data import (
    TEST_AVATAR_URL,
    TEST_DISPLAY_NAME,
    TEST_LOGIN,
    TEST_PROFILE_ID,
    TEST_PROVIDER,
    TEST_TASK_ID,
    TEST_USER_IP,
    TEST_USERID,
)
from .integrational_base import TestSocialIntegrationalBase


TEST_AUTH_ID = '123:1422501443:126'
TEST_SESSIONID = 'old-sessionid'
TEST_UID = 100000000

TEST_ACCOUNT_RESPONSE = {
    'login': TEST_LOGIN,
    'is_pdd': False,
    'uid': TEST_UID,
    'display_name': TEST_DISPLAY_NAME,
}
TEST_PROFILE = {
    'username': 'some.user',
    'firstname': 'Firstname',
    'gender': 'm',
    'provider': TEST_PROVIDER,
    'userid': TEST_USERID,
    'birthday': '1963-12-28',
    'avatar': {'0x0': TEST_AVATAR_URL},
    'links': ['https://plus.google.com/118320684662584130204'],
    'lastname': 'Lastname',
    'email': 'some-mail@example.com',
}


@with_settings_hosts(
    OAUTH_URL='http://localhost/',
    OAUTH_RETRIES=1,
    BLACKBOX_URL='localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    YABS_URL='localhost',
    YAPICS_URL='localhost',
    ALLOWED_SOCIAL_RETPATH_SCHEMES=['yandexmail'],
)
class TestSocialSecureCallback(TestSocialIntegrationalBase):

    def mock_broker(self):
        # Тут должен быть поход в брокер. Возвращаемся:
        self.mock_callback_externals(2)

    def get_task_data_response(self):
        return task_data_response(birthday='1963-12-28')

    def test_no_uid_in_track_error(self):
        """
        Вызываем /secure_callback без uid в треке.
        """
        self.mock_broker()
        response = self.make_api_request(
            'secure_callback',
            data={'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id},
        )
        self.assert_error_response(response, ['track.invalid_state'])

    def test_bad_uid_error(self):
        """
        Вызываем /secure_callback, в треке уид который не нашли среди уидов от профайла
        """
        with self.track_transaction() as track:
            track.uid = '12340'

        self.mock_broker()
        response = self.make_api_request(
            'secure_callback',
            data={'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id},
        )
        self.assert_error_response(response, ['uid.rejected'])

    def test_ok(self):
        """
        Вызываем /secure_callback
        Все хорошо, выписываем куки
        """
        with self.track_transaction() as track:
            track.uid = str(TEST_UID)
            track.social_output_mode = OUTPUT_MODE_SESSIONID

        self.mock_broker()
        response = self.make_api_request(
            'secure_callback',
            data={'task_id': TEST_TASK_ID, 'status': 'ok', 'track_id': self.track_id},
        )
        eq_(response.status_code, 200)
        response = json.loads(response.data)

        cookies = sorted(response.pop('cookies'))
        (l_cookie, sessionid_cookie, lah_cookie, mda2_beacon_cookie,
         sessionid2_cookie, yandexlogin_cookie, yp_cookie, ys_cookie) = cookies
        self.assert_cookie_ok(yandexlogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(lah_cookie, 'lah', domain='.passport-test.yandex.ru')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2_cookie, 'sessionid2', expires=None, http_only=True)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(mda2_beacon_cookie, 'mda2_beacon', domain='.passport-test.yandex.ru', expires=None, secure=True)

        eq_(
            response,
            dict(
                status='ok',
                account=TEST_ACCOUNT_RESPONSE,
                default_uid=TEST_UID,
                profile=TEST_PROFILE,
                state='auth',
                track_id=self.track_id,
                has_enabled_accounts=True,
                profile_id=TEST_PROFILE_ID,
                is_native=False,
                provider=TEST_PROVIDER,
            ),
        )

        phone_attributes = [
            'admitted',
            'bound',
            'confirmed',
            'created',
            'number',
            'secured',
            'is_bank',
        ]
        phone_attributes = [EXTENDED_ATTRIBUTES_PHONE_NAME_TO_TYPE_MAPPING[a] for a in phone_attributes]
        phone_attributes = map(str, sorted(phone_attributes))

        self.env.blackbox.requests[0].assert_post_data_equals(
            dict(
                aliases='all_with_hidden',
                attributes=mock.ANY,
                dbfields=mock.ANY,
                emails='getall',
                format='json',
                getphonebindings='all',
                getphones='all',
                get_public_name='yes',
                getphoneoperations='1',
                is_display_name_empty='yes',
                method='userinfo',
                phone_attributes=','.join(phone_attributes),
                regname='yes',
                uid=str(TEST_UID),
                userip='127.0.0.1',
            ),
        )
        self.env.blackbox.requests[0].assert_contains_attributes(
            [
                'account.is_disabled',
                'password.forced_changing_reason',
                'phones.default',
                'phones.secure',
            ],
        )
        assert_builder_url_params_equal(
            self.env.blackbox,
            {
                'method': 'createsession',
                'lang': '1',
                'have_password': '0',
                'ver': '3',
                'uid': str(TEST_UID),
                'format': 'json',
                'social_id': str(TEST_PROFILE_ID),
                'keyspace': 'yandex.ru',
                'is_lite': '0',
                'ttl': '5',
                'userip': TEST_USER_IP,
                'host_id': '7f',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
            callnum=1,
        )
