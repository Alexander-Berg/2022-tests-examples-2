# -*- coding: utf-8 -*-

import abc
from collections import defaultdict
from datetime import datetime
import json
from time import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import ProfileTestMixin
from passport.backend.api.views.bundle.account.check_exists import ACCOUNT_CHECK_EXISTS_BY_EMAIL_SCOPE
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
from passport.backend.core.builders.antifraud.faker.fake_antifraud import antifraud_score_response
from passport.backend.core.builders.avatars_mds_api.faker import avatars_mds_api_upload_ok_response
from passport.backend.core.builders.blackbox import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
    BlackboxInvalidResponseError,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_GET_DEVICE_PUBLIC_KEY_STATUS,
    BLACKBOX_SECOND_STEP_RFC_TOTP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_device_signature_response,
    blackbox_check_rfc_totp_response,
    blackbox_create_pwd_hash_response,
    blackbox_createsession_response,
    blackbox_generate_public_id_response,
    blackbox_get_device_public_key_response,
    blackbox_hosted_domains_response,
    blackbox_login_response,
    blackbox_loginoccupation_response,
    blackbox_oauth_response,
    blackbox_phone_bindings_response,
    blackbox_sign_response,
    blackbox_userinfo_response,
    blackbox_userinfo_response_multiple,
    blackbox_yakey_backup_response,
)
from passport.backend.core.builders.bot_api.faker.fake_bot_api import bot_api_response
from passport.backend.core.builders.captcha.faker import (
    captcha_response_check,
    captcha_response_generate,
)
from passport.backend.core.builders.drive_api.faker import (
    drive_api_find_drive_session_id_found_response,
    FakeDriveApi,
)
from passport.backend.core.builders.oauth import OAuthDeviceCodeNotAccepted
from passport.backend.core.builders.oauth.faker import (
    check_device_code_response,
    issue_device_code_response,
    oauth_bundle_successful_response,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    get_bind_response,
    get_profiles_response,
    profile_item,
    social_api_person_item,
)
from passport.backend.core.builders.ufo_api.faker import (
    TEST_FRESH_ITEM,
    ufo_api_profile_item,
)
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.builders.ysa_mirror.faker.ysa_mirror import ysa_mirror_ok_resolution_response
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.crypto.signing import (
    get_signing_registry,
    SigningRegistry,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.models.drive import DriveSession
from passport.backend.core.models.phones.faker import (
    build_phone_bound,
    build_phone_secured,
)
from passport.backend.core.services import Service
from passport.backend.core.test.consts import (
    TEST_APPLICATION_ID1,
    TEST_OAUTH_CLIENT_ID1,
    TEST_PHONE_NUMBER1,
    TEST_SOCIAL_LOGIN1,
    TEST_UID1,
)
from passport.backend.core.test.cookiemy_for_language import cookiemy_for_language
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.ydb.faker.ydb_keyvalue import FakeYdbKeyValue
from passport.backend.core.ydb.processors.drive import save_drive_session
from passport.backend.utils.common import (
    bytes_to_hex,
    deep_merge,
    merge_dicts,
)
from passport.backend.utils.time import (
    datetime_to_string,
    unixtime_to_datetime,
)
from six import BytesIO

from .base import BaseMobileProxyTestCase
from .test_base_data import (
    TEST_AUTH_HEADER,
    TEST_AVATAR_KEY,
    TEST_AVATAR_URL_TEMPLATE,
    TEST_BACKUP,
    TEST_COUNTRY_CODE,
    TEST_DEVICE_INFO,
    TEST_DISPLAY_LANGUAGE,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_EMAIL,
    TEST_FIRSTNAME,
    TEST_HINT_ANSWER,
    TEST_HINT_QUESTION,
    TEST_HOST,
    TEST_LANGUAGE,
    TEST_LASTNAME,
    TEST_LOGIN,
    TEST_OAUTH_TOKEN,
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_PHONE_ID1,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_PHONE_NUMBER_DUMPED_MASKED,
    TEST_PHONISH_LOGIN1,
    TEST_PUBLIC_ID,
    TEST_SMS_TEXT,
    TEST_SOCIAL_DISPLAY_NAME,
    TEST_SOCIAL_LOGIN,
    TEST_TIMESTAMP_UPDATED,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
)


TEST_PHONISH_LOGIN = 'phne-test'
TEST_NEOPHONISH_LOGIN = 'nphne-test'
TEST_LITE_LOGIN = 'login@gmail.com'
TEST_RETPATH = 'https://yandex.ru'
TEST_RETPATH_WITHOUT_HOST = 'yandextaxi://'
TEST_CONFIRMATION_CODE = '1234'
TEST_CONFIRMATION_CODE_LONG = '123456'

FRODO_RESPONSE_OK = '<spamlist></spamlist>'

EXPECTED_SESSIONID_COOKIE = u'Session_id=2:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_SESSIONID_SECURE_COOKIE = u'sessionid2=2:sslsession; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
EXPECTED_AUTH_ID = '123:1422501443:126'
COOKIE_L_VALUE = 'VFV5DX94f0RRfXFTXVl5YH8GB2F6VlJ7XzNUTyYaIB1HBlpZBSd6QFkfOAJ7OgEACi5QFlIEGUM+KjlhRgRXZw==.1376993918.1002323.298859.ee75287c1d\
fd8b073375aee93158eb5b'
EXPECTED_L_COOKIE = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % COOKIE_L_VALUE

COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YP_WITH_2FA_ENABLED_VALUE = '1751012630.udn.p%3Atest#1751012630.2fa.1'

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = u'ys=%s; Domain=.yandex.ru; Secure; Path=/' % COOKIE_YS_VALUE

EXPECTED_YANDEX_LOGIN_COOKIE = u'yandex_login=%s; Domain=.yandex.ru; Secure; Path=/' % TEST_LOGIN

COOKIE_LAH_VALUE = 'OG5EOF8wU_bOAGhjXFp7YXkHAGB9UVFyB2IACGZedV4DWl8FWXF5BgJXYFVzYQVKV3kFVlpaU0p2f31iRkZRYQ.1473090908.1002323.1.2fe2104fff29aa69e867d7d1ea601470'
COOKIE_LAH_TEMPLATE = u'lah=%s; Domain=.passport.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/'
EXPECTED_LAH_COOKIE = COOKIE_LAH_TEMPLATE % COOKIE_LAH_VALUE

TEST_OAUTH_CODE = 'qwerty123456'
TEST_OAUTH_CODE_TTL = 600
TEST_OAUTH_SCOPE = 'oauth:grant_xtoken'
TEST_OAUTH_X_TOKEN = 'x-token'
TEST_OAUTH_X_TOKEN_TTL = 3600 * 24
TEST_OAUTH_TOKEN_TTL = 3600
TEST_AVATAR_SIZE = 'normal'
TEST_DEFAULT_AVATAR_KEY = '0/0-0'
TEST_AVATAR_URL = TEST_AVATAR_URL_TEMPLATE % (TEST_DEFAULT_AVATAR_KEY, TEST_AVATAR_SIZE)
TEST_X_TOKEN_CLIENT_ID = 'x-token-client-id'
TEST_X_TOKEN_CLIENT_SECRET = 'x-token-client-secret'
TEST_CLIENT_ID = 'client-id'
TEST_CLIENT_SECRET = 'client-secret'

TEST_PASSWORD_HASH_MD5_CRYPT_ARGON = '1:1:2048:md5salt:argonsalt:hash'
TEST_SERIALIZED_PASSWORD = '6:%s' % TEST_PASSWORD_HASH_MD5_CRYPT_ARGON

TEST_UNIXTIME = 946674001
TEST_DATETIME_STR = datetime_to_string(unixtime_to_datetime(TEST_UNIXTIME))

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE

TEST_MAGIC_LINK_RANDOM_BYTES = b'1' * 10
TEST_MAGIC_LINK_SECRET = bytes_to_hex(TEST_MAGIC_LINK_RANDOM_BYTES)
TEST_MAGIC_LINK_SECRET_WITH_UID = '%s%x' % (TEST_MAGIC_LINK_SECRET, TEST_UID)
TEST_MAGIC_LINK_TTL = 1200
TEST_POLL_INTERVAL = 5

TEST_CSRF_TOKEN = 'csrf'

TEST_DRIVE_DEVICE_ID = '0' * 32
TEST_DRIVE_SESSION_ID = 'drive_session_id'
TEST_NONCE = 'nonce'
TEST_SIGNATURE = 'signature'
TEST_OWNER = 'device_owner1'
TEST_PUBLIC_KEY = 'key1'

TEST_ACCESS_TOKEN = '12345678'
TEST_EXPIRES_IN = '100'
TEST_PROVIDER_TOKEN = 'token1'
TEST_USERID = '57575757575'
TEST_TASK_ID = 'task_id1'

TEST_CLOUD_TOKEN = 'cl-xxx'


class _TranslationSettings(object):
    QUESTIONS = {
        'ru': {
            '1': u'Первый вопрос',
        },
    }
    SMS = {
        'ru': {
            'APPROVE_CODE': TEST_SMS_TEXT,
        },
    }
    NOTIFICATIONS = {
        'ru': defaultdict(str),
        'en': defaultdict(str),
    }
    TANKER_DEFAULT_KEYSET = 'NOTIFICATIONS'


@with_settings_hosts(
    YASMS_URL='http://localhost/',
    FRODO_URL='http://localhost/',
    BLACKBOX_URL='http://localhost',
    OAUTH_URL='http://localhost/',
    DEFAULT_AVATAR_KEY=TEST_DEFAULT_AVATAR_KEY,
    GET_AVATAR_URL='https://localhost/get-yapic/%s/%s',
    HINT_QUESTION_IDS_FOR_LANGUAGES={
        'ru': ['1'],
    },
    PASSPORT_BASE_URL_TEMPLATE='https://passport.yandex.%(tld)s',
    COMPLETION_URL_AM_TEMPLATE='https:/passport.yandex.%(tld)s/am?mode=upgrade',
    PASSPORT_SUBDOMAIN='passport',
    translations=_TranslationSettings,
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
    SMS_VALIDATION_CODE_LENGTH=6,
    SMS_LEGACY_VALIDATION_CODE_LENGTH=4,
    SOCIAL_DEFAULT_SUBSCRIPTION=[],
    IS_INTRANET=False,
    ALLOW_REGISTRATION=True,
    ALLOW_LITE_REGISTRATION=True,
    ALLOW_NEOPHONISH_REGISTRATION=True,
    ALLOW_MAGIC_LINK=True,
    ALLOW_MAGIC_LINK_FOR_LITE=True,
    AUTH_MAGIC_LINK_POLL_INTERVAL=TEST_POLL_INTERVAL,
    AUTH_MAGIC_LINK_TTL=TEST_MAGIC_LINK_TTL,
    MOBILE_LITE_DATA_STATUS_DEFAULT={
        'name': 'not_used',
        'phone_number': 'not_used',
        'password': 'not_used',
    },
    MOBILE_LITE_DATA_STATUS_BY_APP_ID_PREFIX={},
    CLEAN_WEB_API_ENABLED=False,
    DEVICE_PUBLIC_KEY_OWNER_TO_OWNER_ID={TEST_OWNER: 1},
    DRIVE_DEVICE_PUBLIC_KEY_API_ENABLED=True,
    DRIVE_NONCE_SIGN_SPACE='auto_head_unit',
    YDB_PERCENTAGE=0,
    ALLOW_AUTH_BY_SMS_FOR_MOBILE=True,
    ALLOW_AUTH_BY_SMS_FOR_MOBILE_ONLY_FOR_TEST_LOGINS=False,
)
class SimpleViewsTestCase(BaseMobileProxyTestCase, ProfileTestMixin):
    """
    Смоук-тесты на все ручки + тесты на специальную логику мобпрокси
    """
    def setUp(self):
        super(SimpleViewsTestCase, self).setUp()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        self.env.grants.set_grants_return_value(
            merge_dicts(
                mock_grants(
                    consumer='mobileproxy',
                    grants={
                        'account': [
                            'delete_by_credentials',
                            'register_alternative',
                            'register_phonish',
                            'register_require_confirmed_phone',
                            'register_uncompleted',
                            'uncompleted_set_password',
                            'check_exists',
                            'short_info_read',
                            'full_info_read',
                            'complete',
                            'completion_status',
                        ],
                        'account_person': ['write'],
                        'allow_yakey_backup': ['*'],
                        'auth_forward_drive': [
                            'build_nonce',
                            'issue_authorization_code',
                        ],
                        'auth_forwarding_by_track': ['exchange'],
                        'auth_oauth': ['issue_code'],
                        'auth_password': ['base'],
                        'auth_by_token': ['base'],
                        'captcha': ['*'],
                        'change_avatar': ['base'],
                        'control_questions': ['*'],
                        'country': ['suggest'],
                        'device_public_key_create': [TEST_OWNER],
                        'experiments': ['device_id'],
                        'gender': ['suggest'],
                        'hint': ['validate'],
                        'language': ['suggest'],
                        'login': ['suggest', 'validate'],
                        'mobile': [
                            'base',
                            'auth',
                            'magic_link',
                            'register',
                            'register_lite',
                            'register_neophonish',
                            'register_phonish',
                        ],
                        'oauth': ['token_create'],
                        'otp': ['app'],
                        'password': ['validate'],
                        'phone_bundle': ['base'],
                        'phone_number': ['validate', 'confirm'],
                        'phonish': ['disable_auth_by_xtoken'],
                        'push_api': ['subscribe'],
                        'login_restore': ['simple'],
                        'retpath': ['validate'],
                        'session': ['create'],
                        'statbox': ['*'],
                        'subscription': ['*'],
                        'track': ['*'],
                        'auth_social': ['register_by_token'],
                    },
                ),
                mock_grants(
                    consumer='passport',
                    grants={
                        'auth_password': ['base'],
                    },
                ),
                mock_grants(
                    consumer='drive_device',
                    networks=[TEST_USER_IP],
                    grants={
                        'auth_forward_drive': ['public_access'],
                    },
                ),
            ),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.fake_ydb_key_value = FakeYdbKeyValue()
        self.fake_drive_api = FakeDriveApi()

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)
        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)

        self.patches = [
            self.track_id_generator,
            mock.patch.object(
                cookie_l.CookieL,
                'pack',
                self._cookie_l_pack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
            mock.patch.object(
                cookie_y.SessionCookieY,
                'pack',
                self._cookie_ys_pack,
            ),
            mock.patch.object(
                cookie_y.PermanentCookieY,
                'pack',
                self._cookie_yp_pack,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
            self.fake_ydb_key_value,
            self.fake_drive_api,
        ]
        login_mock = mock.Mock()
        login_mock.return_value = TEST_PHONISH_LOGIN1
        self.patches.append(mock.patch('passport.backend.core.types.login.login.generate_phonish_login', login_mock))

        urandom_mock = mock.Mock(return_value=TEST_MAGIC_LINK_RANDOM_BYTES)
        self.patches.append(mock.patch('os.urandom', urandom_mock))

        for patch in self.patches:
            patch.start()
        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([]),
        )
        self.env.bot_api.set_response_value('send_message', bot_api_response())
        LazyLoader.register('SigningRegistry', SigningRegistry)

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.patches
        del self._cookie_yp_pack
        del self._cookie_ys_pack
        del self._cookie_l_pack
        del self._cookie_lah_pack
        del self.fake_ydb_key_value
        del self.fake_drive_api
        del self.track_manager
        del self.track_id_generator
        super(SimpleViewsTestCase, self).tearDown()

    def make_request(self, url, method='POST', args=None, data=None, headers=None, with_track=True):
        params = dict(
            url=url,
            method=method,
            args=args or {},
            data=data or {},
            headers=headers,
        )
        if with_track:
            if method.upper() == 'GET':
                params['args'].update(track_id=self.track_id)
            else:
                params['data'].update(track_id=self.track_id)
        return super(SimpleViewsTestCase, self).make_request(**params)

    def test_login_validation(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        rv = self.make_request(
            'mobileproxy/1/validation/login/',
            data={
                'login': TEST_LOGIN,
            },
        )
        self.check_json_ok(rv)

    def test_password_validation(self):
        rv = self.make_request(
            'mobileproxy/1/validation/password/',
            data={
                'login': TEST_LOGIN,
                'password': 'aaa1bbbccc',
            },
        )
        self.check_json_ok(rv)

    def test_hint_validation(self):
        rv = self.make_request(
            'mobileproxy/1/validation/hint/',
            data={
                'hint_question': TEST_HINT_QUESTION,
                'hint_answer': TEST_HINT_ANSWER,
            },
        )
        self.check_json_ok(rv, hint_question=TEST_HINT_QUESTION, hint_answer=TEST_HINT_ANSWER)

    def test_phone_number_validation(self):
        rv = self.make_request(
            'mobileproxy/1/validation/phone_number/',
            data={
                'phone_number': TEST_PHONE_NUMBER.e164,
                'ignore_phone_compare': '1',
            },
        )
        self.check_json_ok(rv, phone_number=TEST_PHONE_NUMBER.e164)

    def test_retpath_validation(self):
        rv = self.make_request(
            'mobileproxy/1/validation/retpath/',
            data={
                'retpath': TEST_RETPATH,
            },
        )
        self.check_json_ok(rv, retpath=TEST_RETPATH)

    def test_suggest_login(self):
        expected_logins = [
            'bl.al',
            'al.bl',
            'bl.a2012',
            'bl2012',
            'bl2013',
            'al.bl2012',
            'bl.al2013',
            'bl.al2012',
            'cool.a2012',
            'a.bl2013',
        ]
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response(dict.fromkeys(expected_logins, 'free')),
        )
        self.env.login_suggester.setup_next_pack_side_effect([expected_logins, []])
        rv = self.make_request(
            'mobileproxy/1/suggest/login/',
            data={
                'firstname': 'al',
                'lastname': 'bl',
                'language': 'ru',
                'login': 'aaa',
            },
        )
        self.check_json_ok(rv, logins=expected_logins)

    def test_suggest_gender(self):
        self.env.fio_suggest.set_response_value('get', '{}')
        rv = self.make_request(
            'mobileproxy/1/suggest/gender/',
            data={
                'name': 'Adam Smith',
            },
        )
        self.check_json_ok(rv, gender='male')

    def test_suggest_country(self):
        rv = self.make_request(
            'mobileproxy/1/suggest/country/',
            headers=self.default_headers(**{
                'Ya-Client-Host': 'yandex.com.tr',
                'Ya-Consumer-Client-Ip': '144.122.145.170',
            }),
        )
        self.check_json_ok(rv, country=['tr'])

    def test_suggest_language(self):
        rv = self.make_request(
            'mobileproxy/1/suggest/language/',
            headers=self.default_headers(**{'Cookie': 'my=%s' % cookiemy_for_language('uk')}),
        )
        self.check_json_ok(rv, language='uk')

    def test_suggest_mobile_language(self):
        rv = self.make_request(
            'mobileproxy/1/bundle/suggest/mobile_language/',
            method='GET',
            headers=self.default_headers(**{'Accept-Language': 'ru'}),
        )
        self.check_json_ok(rv, language='ru')

    def test_register_phonish(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_PHONISH_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)

        with mock.patch('passport.backend.core.types.login.login.generate_phonish_login', mock.Mock(return_value=TEST_PHONISH_LOGIN)):
            rv = self.make_request(
                'mobileproxy/1/account/register/phonish/',
                headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            )
        self.check_json_ok(rv, uid=TEST_UID, is_new_account=True)

    def test_register_phonish_internal_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.env.blackbox.set_blackbox_response_side_effect(
            'loginoccupation',
            BlackboxInvalidResponseError,
        )

        rv = self.make_request(
            'mobileproxy/1/account/register/phonish/',
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
        )
        self.check_json_error(
            rv,
            errors=[
                {'field': None, 'message': 'Internal error', 'code': 'internal'},
            ],
            status_code=500,
        )

    def test_register_require_confirmed_phone(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)

        rv = self.make_request(
            'mobileproxy/1/account/register/phone/',
            data={
                'login': TEST_LOGIN,
                'firstname': 'firstname',
                'lastname': 'lastname',
                'language': 'en',
                'country': 'tr',
                'eula_accepted': 'True',
                'display_language': 'en',
                'password': 'aaa1bbbccc',
                'mode': 'phonereg',
            },
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
        )
        self.check_json_ok(rv, uid=TEST_UID)

    def test_register_uncompleted(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )

        with mock.patch(
            'passport.backend.core.counters.uncompleted_registration_captcha.is_required',
            mock.Mock(return_value=False),
        ):
            rv = self.make_request(
                'mobileproxy/1/account/register/uncompleted/',
                data={
                    'login': TEST_LOGIN,
                    'firstname': 'firstname',
                    'lastname': 'lastname',
                    'language': 'en',
                    'country': 'tr',
                    'gender': '1',
                    'birthday': '1950-12-30',
                    'timezone': 'Europe/Paris',
                },
                headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            )
        self.check_json_ok(rv, access_token=TEST_OAUTH_TOKEN)

    def test_uncompleted_set_password(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('complete')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                dbfields={
                    'userinfo.reg_date.uid': '2013-08-01 18:00:00',
                },
                attributes={
                    'person.firstname': 'firstname',
                    'person.lastname': 'lastname',
                    'person.country': 'TR',
                    'person.language': 'en',
                },
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/account/register/uncompleted/setpassword/',
            data={
                'eula_accepted': 'True',
                'password': 'aaa1bbbccc',
            },
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
        )
        self.check_json_ok(rv)

    def test_statbox(self):
        rv = self.make_request(
            'mobileproxy/1/statbox/',
            data={
                'action': 'open',
                'data': 'smth',
            },
        )
        self.check_json_ok(rv)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'base',
                _is_external_event='1',
                track_id=self.track_id,
                data='smth',
                action='open',
                consumer='mobileproxy',
            ),
        ])

    def test_track_create(self):
        rv = self.make_request(
            'mobileproxy/1/track/',
        )
        self.check_json_ok(rv, id=self.track_id)

    def test_track_update(self):
        rv = self.make_request(
            'mobileproxy/1/track/%s/' % self.track_id,
            data={
                'language': 'ru',
            },
        )
        self.check_json_ok(rv)

    def test_control_questions(self):
        rv = self.make_request(
            'mobileproxy/1/questions/',
            data={
                'display_language': 'ru',
            },
        )
        self.check_json_ok(
            rv,
            questions=[
                {'id': '1', 'value': u'Первый вопрос'},
            ],
        )

    def test_oauth(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.login = TEST_LOGIN
            track.allow_oauth_authorization = True

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(),
        )
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )

        rv = self.make_request(
            'mobileproxy/1/oauth/token/',
            data={
                'client_id': 'foo',
                'client_secret': 'bar',
            },
        )
        self.check_json_ok(
            rv,
            oauth={
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )

    def test_check_exists(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=ACCOUNT_CHECK_EXISTS_BY_EMAIL_SCOPE, has_user_in_token=False),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/account/check_exists/',
            data={
                'email': TEST_EMAIL,
            },
            headers=self.default_headers(**{'Ya-Consumer-Authorization': TEST_AUTH_HEADER}),
        )
        self.check_json_ok(
            rv,
            exists=True,
        )

    def test_captcha_generate(self):
        self.env.captcha_mock.set_response_value('generate', captcha_response_generate())

        rv = self.make_request(
            'mobileproxy/1/captcha/generate/',
            data={
                'display_language': 'ru',
            },
        )
        self.check_json_ok(
            rv,
            image_url='http://u.captcha.yandex.net/image?key=1p',
            key='1p',
        )

    def test_captcha_check(self):
        self.env.captcha_mock.set_response_value('check', captcha_response_check())

        rv = self.make_request(
            'mobileproxy/1/captcha/check/',
            data={
                'answer': 'a',
                'key': 'b',
            },
        )
        self.check_json_ok(rv, correct=True)

    def test_phonenumber_send_code(self):
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())

        rv = self.make_request(
            'mobileproxy/1/phonenumber/send_confirmation_code/',
            data={
                'country': 'RU',
                'display_language': 'ru',
                'phone_number': TEST_PHONE_NUMBER.e164,
                'ignore_phone_compare': '1',
            },
            headers=dict(user_agent=TEST_USER_AGENT),
        )
        self.check_json_ok(rv, code_length=4)

    def test_phonenumber_confirm(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_last_send_at = time() - 20

        rv = self.make_request(
            'mobileproxy/1/phonenumber/confirm/',
            data={
                'code': TEST_CONFIRMATION_CODE,
            },
        )
        self.check_json_ok(rv, result=True)

    def test_subscription_add_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_UID),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )
        rv = self.make_request(
            'mobileproxy/1/account/subscription/mail/',
            headers=self.default_headers(**{'Ya-OAuth-Header': 'token'}),
        )
        self.check_json_ok(rv)

    def test_subscription_add_no_token_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_UID),
        )
        rv = self.make_request(
            'mobileproxy/1/account/subscription/mail/',
        )
        self.check_xml_error(rv, 'Oauth token not set')

    def test_subscription_token_invalid_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        rv = self.make_request(
            'mobileproxy/1/account/subscription/mail/',
            headers=self.default_headers(**{'Ya-OAuth-Header': 'invalid token'}),
        )
        self.check_xml_error(rv, 'Oauth token invalid', status_code=401)

    def test_bundle_phone_confirm_submit(self):
        self.env.code_generator.set_return_value(TEST_CONFIRMATION_CODE_LONG)
        self.env.antifraud_api.set_response_value('score', antifraud_score_response())
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())

        rv = self.make_request(
            'mobileproxy/1/bundle/phone/confirm/submit/',
            data={
                'number': TEST_PHONE_NUMBER.e164,
                'display_language': 'ru',
            },
            headers=dict(user_agent=TEST_USER_AGENT),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            code_length=6,
            deny_resend_until=TimeNow(),
            number=TEST_PHONE_NUMBER_DUMPED,
        )

    def test_bundle_phone_confirm_commit(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE_LONG
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_last_send_at = time() - 20
            track.phone_confirmation_method = 'by_sms'
            track.country = TEST_COUNTRY_CODE
            track.state = 'confirm'

        rv = self.make_request(
            'mobileproxy/1/bundle/phone/confirm/commit/',
            data={
                'code': TEST_CONFIRMATION_CODE_LONG,
            },
        )
        self.check_json_ok(
            rv,
            number=TEST_PHONE_NUMBER_DUMPED,
        )

    def test_bundle_phone_confirm_and_bind_submit(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope=TEST_OAUTH_SCOPE,
            ),
        )
        self.env.code_generator.set_return_value(TEST_CONFIRMATION_CODE_LONG)
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())

        rv = self.make_request(
            'mobileproxy/1/bundle/phone/confirm_and_bind/submit/',
            data={
                'number': TEST_PHONE_NUMBER.e164,
                'display_language': 'ru',
            },
            headers=self.default_headers(**{
                'User-Agent': TEST_USER_AGENT,
                'Authorization': TEST_AUTH_HEADER,
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            code_length=6,
            deny_resend_until=TimeNow(),
            number=TEST_PHONE_NUMBER_DUMPED,
        )

    def test_bundle_phone_confirm_and_bind_commit(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope=TEST_OAUTH_SCOPE,
            ),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE_LONG
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_last_send_at = time() - 20
            track.country = TEST_COUNTRY_CODE
            track.uid = TEST_UID
            track.state = 'confirm_and_bind'

        rv = self.make_request(
            'mobileproxy/1/bundle/phone/confirm_and_bind/commit/',
            data={
                'code': TEST_CONFIRMATION_CODE_LONG,
            },
            headers=self.default_headers(**{
                'User-Agent': TEST_USER_AGENT,
                'Authorization': TEST_AUTH_HEADER,
            }),
        )
        self.check_json_ok(
            rv,
            number=TEST_PHONE_NUMBER_DUMPED,
            phone_id=TEST_PHONE_ID1,
        )

    def test_bundle_phone_bind_simple_or_confirm_bound_submit(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope=TEST_OAUTH_SCOPE,
            ),
        )
        self.env.code_generator.set_return_value(TEST_CONFIRMATION_CODE_LONG)
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())

        rv = self.make_request(
            'mobileproxy/2/bundle/phone/bind_simple_or_confirm_bound/submit/',
            data={
                'number': TEST_PHONE_NUMBER.e164,
                'display_language': 'ru',
            },
            headers=self.default_headers(**{
                'User-Agent': TEST_USER_AGENT,
                'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            code_length=6,
            deny_resend_until=TimeNow(),
            number=TEST_PHONE_NUMBER_DUMPED,
        )

    def test_bundle_phone_bind_simple_or_confirm_bound_commit(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope=TEST_OAUTH_SCOPE,
            ),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE_LONG
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_last_send_at = time() - 20
            track.country = TEST_COUNTRY_CODE
            track.uid = TEST_UID
            track.state = 'bind_or_confirm_bound_state'

        rv = self.make_request(
            'mobileproxy/2/bundle/phone/bind_simple_or_confirm_bound/commit/',
            data={
                'code': TEST_CONFIRMATION_CODE_LONG,
            },
            headers=self.default_headers(**{
                'User-Agent': TEST_USER_AGENT,
                'Authorization': 'OAuth %s' % TEST_OAUTH_TOKEN,
            }),
        )
        self.check_json_ok(
            rv,
            number=TEST_PHONE_NUMBER_DUMPED,
        )

    def test_bundle_validate_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/validate/login/',
            data={
                'login': TEST_LOGIN,
            },
        )
        self.check_json_ok(rv)

    def test_bundle_validate_password(self):
        rv = self.make_request(
            'mobileproxy/1/bundle/validate/password/',
            data={
                'password': 'simple123456',
            },
        )
        self.check_json_ok(rv)

    def test_bundle_validate_phone_number(self):
        rv = self.make_request(
            'mobileproxy/1/bundle/validate/phone_number/',
            data={
                'phone_number': TEST_PHONE_NUMBER.e164,
            },
        )
        self.check_json_ok(
            rv,
            phone_number=TEST_PHONE_NUMBER_DUMPED,
        )

    def test_bundle_auth_xtoken(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/auth/x_token/',
            data={
                'type': 'x-token',
                'retpath': TEST_RETPATH,
            },
            headers=self.default_headers(**{'Authorization': TEST_AUTH_HEADER}),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            passport_host='https://passport.yandex.ru',
        )

    def test_bundle_auth_xtoken_retpath_without_host(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/auth/x_token/',
            data={
                'type': 'x-token',
                'retpath': TEST_RETPATH_WITHOUT_HOST,
            },
            headers=self.default_headers(**{'Authorization': TEST_AUTH_HEADER}),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            passport_host=None,
        )

    def test_issue_code_for_am(self):
        self.env.oauth.set_response_value(
            'issue_authorization_code',
            oauth_bundle_successful_response(
                code=TEST_OAUTH_CODE,
                expires_in=TEST_OAUTH_CODE_TTL,
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/auth/oauth/code_for_am/',
            headers=self.default_headers(**{
                'Ya-Client-Host': TEST_HOST,
                'Ya-Client-Cookie': 'foo=bar',
            }),
        )
        self.check_json_ok(
            rv,
            code=TEST_OAUTH_CODE,
            expires_in=TEST_OAUTH_CODE_TTL,
        )

    def test_yakey_backup_send_code(self):
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())

        rv = self.make_request(
            'mobileproxy/1/bundle/yakey_backup/send_code/',
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            data={
                'number': TEST_PHONE_NUMBER.original,
                'display_language': TEST_DISPLAY_LANGUAGE,
            },
            with_track=False,
        )
        self.check_json_ok(rv, number=TEST_PHONE_NUMBER_DUMPED, track_id=self.track_id)

    def test_yakey_backup_check_code(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_sms_count.incr()
            track.phone_confirmation_code = TEST_CONFIRMATION_CODE
            track.process_name = 'yakey_backup'

        rv = self.make_request(
            'mobileproxy/1/bundle/yakey_backup/check_code/',
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            data={
                'code': TEST_CONFIRMATION_CODE,
                'track_id': self.track_id,
            },
        )
        self.check_json_ok(rv, track_id=self.track_id)

    def test_yakey_backup_upload(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = 'yakey_backup'
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_is_confirmed = True

        self.env.blackbox.set_blackbox_response_value(
            'yakey_backup',
            blackbox_yakey_backup_response(is_found=False),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/yakey_backup/upload/',
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            data={
                'track_id': self.track_id,
                'number': TEST_PHONE_NUMBER.original,
                'country': TEST_COUNTRY_CODE,
                'backup': TEST_BACKUP,
            },
        )
        self.check_json_ok(rv)

    def test_yakey_backup_download(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = 'yakey_backup'
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_is_confirmed = True

        self.env.blackbox.set_blackbox_response_value(
            'yakey_backup',
            blackbox_yakey_backup_response(
                updated=TEST_TIMESTAMP_UPDATED,
                device_name=TEST_DEVICE_INFO['device_name'],
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/yakey_backup/download/',
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            data={
                'track_id': self.track_id,
                'number': TEST_PHONE_NUMBER.digital,
            },
        )
        self.check_json_ok(
            rv,
            backup=TEST_BACKUP,
            backup_info=dict(
                updated=TEST_TIMESTAMP_UPDATED,
                device_name=TEST_DEVICE_INFO['device_name'],
            ),
        )

    def test_yakey_backup_get_info(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.process_name = 'yakey_backup'
            track.phone_confirmation_phone_number_original = TEST_PHONE_NUMBER.original
            track.phone_confirmation_is_confirmed = True

        self.env.blackbox.set_blackbox_response_value(
            'yakey_backup',
            blackbox_yakey_backup_response(
                info_only=True,
                device_name=TEST_DEVICE_INFO['device_name'],
                updated=TEST_TIMESTAMP_UPDATED,
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/yakey_backup/info/',
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            data={
                'track_id': self.track_id,
                'number': TEST_PHONE_NUMBER.digital,
            },
        )
        self.check_json_ok(
            rv,
            backup_info=dict(
                updated=TEST_TIMESTAMP_UPDATED,
                device_name=TEST_DEVICE_INFO['device_name'],
            ),
        )

    def test_short_info(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_login=TEST_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                scope=TEST_OAUTH_SCOPE,
                default_avatar_key=TEST_AVATAR_KEY,
                is_avatar_empty=False,
                oauth_token_info={'issue_time': TEST_DATETIME_STR},
                public_id=TEST_PUBLIC_ID,
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/account/short_info/',
            method='GET',
            args={
                'avatar_size': 'islands-1500',
            },
            headers={
                'Authorization': TEST_AUTH_HEADER,
                'If-None-Match': 'foo',
            },
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            primary_alias_type=1,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'islands-1500'),
            firstname='\\u0414',
            lastname='\\u0424',
            birthday='1963-05-15',
            gender='m',
            x_token_issued_at=TEST_UNIXTIME,
            public_id=TEST_PUBLIC_ID,
        )

        # Проверим, что при повторном запросе мы сэкономим траффик
        rv2 = self.make_request(
            'mobileproxy/1/bundle/account/short_info/',
            method='GET',
            args={
                'avatar_size': 'islands-1500',
            },
            headers={
                'Authorization': TEST_AUTH_HEADER,
                'If-None-Match': rv.headers['etag'],
            },
        )
        eq_(rv2.status_code, 304)
        ok_(not rv2.data)

    def test_full_info(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_login=TEST_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                scope=TEST_OAUTH_SCOPE,
                default_avatar_key=TEST_AVATAR_KEY,
                is_avatar_empty=False,
                public_id=TEST_PUBLIC_ID,
            ),
        )
        profiles = [
            profile_item(
                person=social_api_person_item(firstname='first', lastname='last'),
                subscriptions=[],
                expand_provider=True,
            ),
        ]
        self.env.social_api.set_response_value(
            'get_profiles_by_uid',
            get_profiles_response(profiles),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/account/',
            method='GET',
            args={
                'need_display_name_variants': 'true',
                'need_social_profiles': 'true',
                # последующие параметры должны быть проигнорированы
                'need_phones': 'true',
                'need_emails': 'true',
                'need_question': 'true',
                'need_additional_account_data': 'true',
            },
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
            }),
        )
        self.check_json_ok(
            rv,
            account={
                'uid': TEST_UID,
                'login': TEST_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': {
                    'name': 'Mr_November',
                    'default_avatar': '0/key0-0',
                },
                'display_names': {
                    TEST_LOGIN: 'p:%s' % TEST_LOGIN,
                    'some.user': 'p:some.user',
                    u'\\u0414': u'p:\\u0414',
                    u'\\u0424': u'p:\\u0424',
                    u'\\u0414 \\u0424': u'p:\\u0414 \\u0424',
                    'first': 'p:first',
                    'last': 'p:last',
                    'first last': 'p:first last',
                },
                'is_workspace_user': False,
                'is_yandexoid': False,
                'is_2fa_enabled': False,
                'is_rfc_2fa_enabled': False,
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'language': 'ru',
                    'city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                    'country': 'ru',
                    'timezone': 'Europe/Moscow',
                    'birthday': '1963-05-15',
                    'gender': 1,
                },
                'profiles': profiles,
                'public_id': TEST_PUBLIC_ID,
            },
        )

    def test_full_info_minimal(self):
        self.env.blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_login=TEST_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                scope=TEST_OAUTH_SCOPE,
                default_avatar_key=TEST_AVATAR_KEY,
                is_avatar_empty=False,
                public_id=TEST_PUBLIC_ID,
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/account/',
            method='GET',
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
            }),
        )
        self.check_json_ok(
            rv,
            account={
                'uid': TEST_UID,
                'login': TEST_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': {
                    'name': 'Mr_November',
                    'default_avatar': '0/key0-0',
                },
                'is_workspace_user': False,
                'is_yandexoid': False,
                'is_2fa_enabled': False,
                'is_rfc_2fa_enabled': False,
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'language': 'ru',
                    'city': u'\u041c\u043e\u0441\u043a\u0432\u0430',
                    'country': 'ru',
                    'timezone': 'Europe/Moscow',
                    'birthday': '1963-05-15',
                    'gender': 1,
                },
                'public_id': TEST_PUBLIC_ID,
            },
        )

    def test_track_init(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=TEST_OAUTH_SCOPE),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/track/init/',
            headers=self.default_headers(**{'Authorization': TEST_AUTH_HEADER}),
        )
        self.check_json_ok(rv, track_id=self.track_id)

    def test_personal_info(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.uid = TEST_UID
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=TEST_OAUTH_SCOPE, uid=TEST_UID, firstname='foo'),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/account/person/',
            data={
                'track_id': self.track_id,
                'firstname': 'bar',
            },
            headers=self.default_headers(**{'Authorization': TEST_AUTH_HEADER}),
        )
        self.check_json_ok(rv)

    def test_personal_info_display_name_change_not_allowed(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.uid = TEST_UID
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=TEST_OAUTH_SCOPE,
                uid=TEST_UID,
                firstname='foo',
                attributes={
                    'account.is_verified': True,
                },
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/account/person/',
            data={
                'track_id': self.track_id,
                'display_name': 'p:bar',
            },
            headers=self.default_headers(**{'Authorization': TEST_AUTH_HEADER}),
        )
        self.check_json_error(
            rv,
            status_code=200,
            errors=['display_name.invalid'],
        )

    def test_avatar_upload(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=TEST_OAUTH_SCOPE),
        )
        self.env.avatars_mds_api.set_response_value(
            'upload_from_file',
            avatars_mds_api_upload_ok_response(),
        )
        with mock.patch(
            'passport.backend.core.avatars.avatars.get_avatar_mds_key',
            mock.Mock(return_value='567890'),
        ):
            rv = self.make_request(
                'mobileproxy/2/change_avatar/',
                data={
                    'file': (BytesIO(b'my file content'), 'test.png'),
                },
                headers=self.default_headers(**{'Authorization': TEST_AUTH_HEADER}),
            )
        self.check_json_ok(rv, avatar_url='https://localhost/get-yapic/1234/567890/normal')

    def test_push_api_subscribe(self):
        http_headers = dict(
            authorization='Oauth ' + TEST_OAUTH_TOKEN,
        )
        http_method = 'POST'
        http_query_args = dict(
            app_id='ru.yandex.test_app',
            app_platform='iPhone',
            deviceid='123-456-789',
        )
        http_data = dict(
            device_token='123',
            uid='456',
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_UID, login=TEST_LOGIN, scope=TEST_OAUTH_SCOPE),
        )
        self.env.push_api.set_response_value('subscribe', 'OK')
        rv = self.make_request(
            'mobileproxy/1/bundle/push/subscribe/',
            args=http_query_args,
            data=http_data,
            headers=http_headers,
            method=http_method,
        )
        self.check_json_ok(rv)

    def test_push_api_unsubscribe(self):
        http_headers = dict(
            authorization='Oauth ' + TEST_OAUTH_TOKEN,
        )
        http_method = 'POST'
        http_query_args = dict(
            app_id='ru.yandex.test',
            deviceid='123-456-789',
        )
        http_data = dict(
            uid='123',
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(uid=TEST_UID, login=TEST_LOGIN, scope=TEST_OAUTH_SCOPE),
        )
        self.env.push_api.set_response_value('unsubscribe', 'OK')
        rv = self.make_request(
            'mobileproxy/1/bundle/push/unsubscribe/',
            args=http_query_args,
            data=http_data,
            headers=http_headers,
            method=http_method,
        )
        self.check_json_ok(rv)

    def test_mobile_start_v1(self):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_login=TEST_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                default_avatar_key=TEST_AVATAR_KEY,
                is_avatar_empty=False,
                crypt_password=TEST_PASSWORD_HASH,
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/start/',
            data={
                'login': TEST_LOGIN,
                'x_token_client_id': 'x_client_id',
                'x_token_client_secret': 'x_client_secret',
                'avatar_size': 'islands-1500',
                'display_language': TEST_LANGUAGE,
                'cloud_token': TEST_CLOUD_TOKEN,
            },
            headers=self.default_headers(),
            method='POST',
        )
        self.check_json_ok(
            rv,
            primary_alias_type=1,
            can_authorize=True,
            auth_methods=['password'],
            track_id=self.track_id,
        )

    def test_mobile_password_auth_integrational(self):
        bb_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            display_login=TEST_LOGIN,
            display_name={'name': TEST_DISPLAY_NAME},
            default_avatar_key=TEST_AVATAR_KEY,
            is_avatar_empty=False,
            crypt_password=TEST_PASSWORD_HASH,
            public_id=TEST_PUBLIC_ID,
        )
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**bb_kwargs),
        )
        self.env.blackbox.set_response_value(
            'login',
            blackbox_login_response(
                password_status=BLACKBOX_PASSWORD_SECOND_STEP_REQUIRED_STATUS,
                allowed_second_steps=[BLACKBOX_SECOND_STEP_RFC_TOTP],
                **bb_kwargs
            ),
        )
        self.env.blackbox.set_response_value(
            'check_rfc_totp',
            blackbox_check_rfc_totp_response(),
        )
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(has_auth_on_device=False, device_id='test', device_name='test-device'),
        )
        self.env.ysa_mirror.set_response_side_effect(
            'check_client_by_requestid_v2',
            [
                ysa_mirror_ok_resolution_response(),
            ],
        )

        # стартовая ручка
        rv = self.make_request(
            'mobileproxy/2/bundle/mobile/start/',
            data={
                'login': TEST_LOGIN,
                'x_token_client_id': 'x_client_id',
                'x_token_client_secret': 'x_client_secret',
                'avatar_size': 'islands-1500',
                'display_language': TEST_LANGUAGE,
                'cloud_token': TEST_CLOUD_TOKEN,
            },
            headers=self.default_headers(),
            method='POST',
        )
        self.check_json_ok(
            rv,
            primary_alias_type=1,
            can_authorize=True,
            auth_methods=['password'],
            track_id=self.track_id,
        )
        # ручка проверки пароля
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/auth/password/',
            data={
                'password': 'pass',
            },
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_error(
            rv,
            status_code=200,
            errors=['action.required_native'],
            state='rfc_totp',
        )
        # ручка проверки одноразового пароля
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/auth/rfc_otp/',
            data={
                'rfc_otp': '123',
            },
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            primary_alias_type=1,
            has_password=True,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'islands-1500'),
            firstname='\\u0414',
            lastname='\\u0424',
            birthday='1963-05-15',
            gender='m',
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_TOKEN,
            x_token_issued_at=TimeNow(),
            public_id=TEST_PUBLIC_ID,
        )

    def test_mobile_magic_link_auth_integrational(self):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_login=TEST_LOGIN,
                display_name={'name': TEST_DISPLAY_NAME},
                default_avatar_key=TEST_AVATAR_KEY,
                is_avatar_empty=False,
                crypt_password=TEST_PASSWORD_HASH,
                emails=[
                    self.env.email_toolkit.create_native_email(TEST_LOGIN, 'yandex.ru'),
                ],
                public_id=TEST_PUBLIC_ID,
            ),
        )
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )

        # стартовая ручка
        rv = self.make_request(
            'mobileproxy/2/bundle/mobile/start/',
            data={
                'login': TEST_LOGIN,
                'device_name': 'iPhone',
                'x_token_client_id': 'x_client_id',
                'x_token_client_secret': 'x_client_secret',
                'avatar_size': 'islands-1500',
                'display_language': TEST_LANGUAGE,
                'cloud_token': TEST_CLOUD_TOKEN,
            },
            headers=self.default_headers(),
            method='POST',
        )
        self.check_json_ok(
            rv,
            primary_alias_type=1,
            can_authorize=True,
            auth_methods=['password', 'magic_link'],
            magic_link_email='login@yandex.ru',
            track_id=self.track_id,
        )
        # ручка отправки письма
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/magic_link/send/',
            data={
                'retpath': TEST_RETPATH,
            },
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            poll_interval=TEST_POLL_INTERVAL,
            expires_in=TEST_MAGIC_LINK_TTL,
        )
        # ручка проверки статуса
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/magic_link/status/',
            headers=self.default_headers(),
            method='GET',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            magic_link_confirmed=False,
        )
        # фронтовая ручка информации о ссылке (НЕ мобпрокси)
        rv = self.make_request(
            '1/bundle/auth/password/multi_step/magic_link/info/',
            args={
                'consumer': 'passport',
                'avatar_size': 'islands-1500',
            },
            headers=self.default_headers(**{
                'Ya-Client-Host': 'yandex.ru',
                'Ya-Client-User-Agent': 'curl',
                'Ya-Client-Cookie': 'foo=bar',
            }),
            method='GET',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'islands-1500'),
            browser='iPhone',
            location=u'Мекильтео',
            start_time=TimeNow(),
        )
        # ручка подтверждения ссылки
        rv = self.make_request(
            'mobileproxy/1/bundle/auth/password/multi_step/magic_link/commit/',
            data={
                'secret': TEST_MAGIC_LINK_SECRET_WITH_UID,
                'redirect': True,
            },
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
            }),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        # опять ручка проверки статуса
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/magic_link/status/',
            headers=self.default_headers(),
            method='GET',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            magic_link_confirmed=True,
        )
        # ручка авторизации
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/auth/magic_link/',
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            primary_alias_type=1,
            has_password=True,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'islands-1500'),
            firstname='\\u0414',
            lastname='\\u0424',
            birthday='1963-05-15',
            gender='m',
            native_default_email='%s@yandex.ru' % TEST_LOGIN,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_TOKEN,
            x_token_issued_at=TimeNow(),
            public_id=TEST_PUBLIC_ID,
        )
        # ручка инвалидации ссылки
        rv = self.make_request(
            'mobileproxy/1/bundle/auth/password/multi_step/magic_link/invalidate/',
            args={
                'consumer': 'passport',
            },
            data={
                'secret': TEST_MAGIC_LINK_SECRET_WITH_UID,
                'redirect': True,
            },
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_error(
            rv,
            status_code=200,
            errors=['action.not_required'],
        )

    def test_mobile_restore_login(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.user_entered_login = TEST_LOGIN
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/restore_login/',
            data={
                'track_id': self.track_id,
                'firstname': 'first',
                'lastname': 'last',
            },
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            accounts=[],
            allowed_registration_flows=['neophonish', 'portal'],
        )

    def test_mobile_auth_after_login_restore(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.cloud_token = TEST_CLOUD_TOKEN
            track.avatar_size = TEST_AVATAR_SIZE
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_method = 'by_sms'

        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            aliases={
                'neophonish': TEST_LOGIN,
            },
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
            display_login=TEST_LOGIN,
            display_name={'name': TEST_DISPLAY_NAME},
            default_avatar_key=TEST_AVATAR_KEY,
            is_avatar_empty=False,
            public_id=TEST_PUBLIC_ID,
        )
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_kwargs),
        )
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/auth/after_login_restore/',
            data={
                'uid': TEST_UID,
                'firstname': TEST_FIRSTNAME,
                'lastname': TEST_LASTNAME,
            },
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            primary_alias_type=5,
            display_login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, TEST_AVATAR_SIZE),
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
            birthday='1963-05-15',
            gender='m',
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_TOKEN,
            x_token_issued_at=TimeNow(),
            public_id=TEST_PUBLIC_ID,
        )

    def test_mobile_validate_phone_number(self):
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/validate/phone_number/',
            data={
                'phone_number': TEST_PHONE_NUMBER.e164,
            },
        )
        self.check_json_ok(
            rv,
            phone_number=TEST_PHONE_NUMBER_DUMPED,
        )

    def test_mobile_register_phonish(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.country = 'ru'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.cloud_token = TEST_CLOUD_TOKEN

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_PHONISH_LOGIN1: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )
        self.env.blackbox.set_blackbox_response_value(
            'generate_public_id',
            blackbox_generate_public_id_response(public_id=TEST_PUBLIC_ID),
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

        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/register/phonish/',
            data={'track_id': self.track_id},
            headers=self.default_headers(),
            method='POST',
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            display_name=TEST_PHONE_NUMBER.e164,
            primary_alias_type=10,
            avatar_url=TEST_AVATAR_URL,
            is_avatar_empty=True,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
            access_token=TEST_OAUTH_TOKEN,
            access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            public_id=TEST_PUBLIC_ID,
        )

    def test_mobile_register_neophonish(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.country = 'ru'
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.cloud_token = TEST_CLOUD_TOKEN

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_NEOPHONISH_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'generate_public_id',
            blackbox_generate_public_id_response(public_id=TEST_PUBLIC_ID),
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

        with mock.patch(
            'passport.backend.core.types.login.login.generate_neophonish_login',
            mock.Mock(return_value=TEST_NEOPHONISH_LOGIN),
        ):
            rv = self.make_request(
                'mobileproxy/1/bundle/mobile/register/neophonish/',
                data={
                    'track_id': self.track_id,
                    'firstname': TEST_FIRSTNAME,
                    'lastname': TEST_LASTNAME,
                    'eula_accepted': 'true',
                },
                headers=self.default_headers(),
            )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            display_login=TEST_NEOPHONISH_LOGIN,
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
            display_name=' '.join([TEST_FIRSTNAME, TEST_LASTNAME]),
            primary_alias_type=5,
            avatar_url=TEST_AVATAR_URL,
            is_avatar_empty=True,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
            access_token=TEST_OAUTH_TOKEN,
            access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            public_id=TEST_PUBLIC_ID,
        )

    def test_mobile_register(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.country = 'ru'
            track.language = 'ru'
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True

            track.x_token_client_id = TEST_X_TOKEN_CLIENT_ID
            track.x_token_client_secret = TEST_X_TOKEN_CLIENT_SECRET
            track.client_id = TEST_CLIENT_ID
            track.client_secret = TEST_CLIENT_SECRET
            track.cloud_token = TEST_CLOUD_TOKEN

        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'generate_public_id',
            blackbox_generate_public_id_response(public_id=TEST_PUBLIC_ID),
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

        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/register/',
            data={
                'track_id': self.track_id,
                'login': TEST_LOGIN,
                'password': TEST_PASSWORD,
                'firstname': TEST_FIRSTNAME,
                'lastname': TEST_LASTNAME,
                'eula_accepted': '1',
            },
            headers=self.default_headers(),
            method='POST',
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            firstname=TEST_FIRSTNAME,
            lastname=TEST_LASTNAME,
            display_name=TEST_LOGIN,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN,
            has_password=True,
            primary_alias_type=1,
            avatar_url=TEST_AVATAR_URL,
            is_avatar_empty=True,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_X_TOKEN,
            x_token_expires_in=TEST_OAUTH_X_TOKEN_TTL,
            x_token_issued_at=TimeNow(),
            access_token=TEST_OAUTH_TOKEN,
            access_token_expires_in=TEST_OAUTH_TOKEN_TTL,
            public_id=TEST_PUBLIC_ID,
        )

    def test_mobile_register_lite_integrational(self):
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LITE_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=0),
        )
        self.env.blackbox.set_blackbox_response_value(
            'generate_public_id',
            blackbox_generate_public_id_response(public_id=TEST_PUBLIC_ID),
        )
        self.env.frodo.set_response_value(u'check', u'<spamlist></spamlist>')
        self.env.frodo.set_response_value(u'confirm', u'')
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )

        # стартовая ручка
        rv = self.make_request(
            'mobileproxy/2/bundle/mobile/start/',
            data={
                'login': TEST_LITE_LOGIN,
                'device_name': 'iPhone',
                'x_token_client_id': 'x_client_id',
                'x_token_client_secret': 'x_client_secret',
                'avatar_size': 'islands-1500',
                'display_language': TEST_LANGUAGE,
                'cloud_token': TEST_CLOUD_TOKEN,
            },
            headers=self.default_headers(),
            method='POST',
        )
        self.check_json_error(
            rv,
            status_code=200,
            errors=['account.not_found'],
            can_register=True,
            login=TEST_LITE_LOGIN,
            account_type='lite',
            allowed_account_types=['lite'],
            track_id=self.track_id,
            lite_data_necessity={
                'name': 'not_used',
                'password': 'not_used',
                'phone_number': 'not_used',
            },
        )
        # ручка отправки письма
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/magic_link/send/',
            data={
                'retpath': TEST_RETPATH,
            },
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            poll_interval=TEST_POLL_INTERVAL,
            expires_in=TEST_MAGIC_LINK_TTL,
        )
        # ручка проверки статуса
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/magic_link/status/',
            headers=self.default_headers(),
            method='GET',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            magic_link_confirmed=False,
        )
        # фронтовая ручка информации о ссылке (НЕ мобпрокси)
        rv = self.make_request(
            '1/bundle/auth/password/multi_step/magic_link/info/',
            args={
                'consumer': 'passport',
                'avatar_size': 'islands-1500',
            },
            headers=self.default_headers(**{
                'Ya-Client-Host': 'yandex.ru',
                'Ya-Client-User-Agent': 'curl',
                'Ya-Client-Cookie': 'foo=bar',
            }),
            method='GET',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            browser='iPhone',
            location=u'Мекильтео',
            start_time=TimeNow(),
            login=TEST_LITE_LOGIN,
        )
        # ручка подтверждения ссылки
        rv = self.make_request(
            'mobileproxy/1/bundle/auth/password/multi_step/magic_link/commit_registration/',
            data={
                'secret': TEST_MAGIC_LINK_SECRET,
                'redirect': True,
            },
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
            }),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            retpath=TEST_RETPATH,
        )
        # опять ручка проверки статуса
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/magic_link/status/',
            headers=self.default_headers(),
            method='GET',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            magic_link_confirmed=True,
            lite_data_necessity={
                'name': 'not_used',
                'password': 'not_used',
                'phone_number': 'not_used',
            },
        )
        # ручка регистрации
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/register/lite/',
            headers=self.default_headers(),
            method='POST',
            data={
                'eula_accepted': True,
            },
            with_track=True,
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            primary_alias_type=5,
            display_login=TEST_LITE_LOGIN,
            normalized_display_login=TEST_LITE_LOGIN,
            display_name=TEST_LITE_LOGIN,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_DEFAULT_AVATAR_KEY, 'islands-1500'),
            is_avatar_empty=True,
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_TOKEN,
            x_token_issued_at=TimeNow(),
            public_id=TEST_PUBLIC_ID,
        )

    def test_complete_status(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_SOCIAL_LOGIN,
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                subscribed_to=[Service.by_slug('social')],
                scope=TEST_OAUTH_SCOPE,
                public_id=TEST_PUBLIC_ID,
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/complete/status/',
            method='GET',
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
            }),
        )
        self.check_json_ok(
            rv,
            is_complete=False,
            is_completion_available=True,
            is_completion_recommended=False,
            is_completion_required=False,
            completion_url='https:/passport.yandex.ru/am?mode=upgrade',
        )

    def test_complete_submit(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_SOCIAL_LOGIN,
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                subscribed_to=[Service.by_slug('social')],
                scope=TEST_OAUTH_SCOPE,
                public_id=TEST_PUBLIC_ID,
            ),
        )
        rv = self.make_request(
            'mobileproxy/1/bundle/complete/submit/',
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
                'User-Agent': TEST_USER_AGENT,
                'Accept-Language': 'ru',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            state='complete_social_with_login',
            account={
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'language': 'ru',
                    'country': 'ru',
                    'gender': 1,
                    'birthday': '1963-05-15',
                },
                'login': TEST_SOCIAL_LOGIN,
                'display_name': TEST_SOCIAL_DISPLAY_NAME,
                'uid': TEST_UID,
                'display_login': '',
                'public_id': TEST_PUBLIC_ID,
            },
            has_recovery_method=False,
        )

    def test_complete_submit_for_unsupported_neophonish(self):
        account_kwargs = deep_merge(
            dict(
                uid=TEST_UID,
                login=TEST_NEOPHONISH_LOGIN,
                aliases={
                    'neophonish': TEST_NEOPHONISH_LOGIN,
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                display_name=TEST_DISPLAY_NAME_DATA,
                public_id=TEST_PUBLIC_ID,
            ),
            build_phone_secured(1, TEST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=TEST_OAUTH_SCOPE,
                **account_kwargs
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/complete/submit/',
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
                'User-Agent': TEST_USER_AGENT,
                'Accept-Language': 'ru',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            state='complete_lite',
            account={
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'language': 'ru',
                    'country': 'ru',
                    'gender': 1,
                    'birthday': '1963-05-15',
                },
                'login': TEST_NEOPHONISH_LOGIN,
                'display_name': TEST_DISPLAY_NAME_DATA,
                'uid': TEST_UID,
                'display_login': '',
                'public_id': TEST_PUBLIC_ID,
            },
            has_recovery_method=True,
        )

    def test_complete_submit_for_neophonish(self):
        account_kwargs = deep_merge(
            dict(
                uid=TEST_UID,
                login=TEST_NEOPHONISH_LOGIN,
                aliases={
                    'neophonish': TEST_NEOPHONISH_LOGIN,
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                display_name=TEST_DISPLAY_NAME_DATA,
                public_id=TEST_PUBLIC_ID,
            ),
            build_phone_secured(1, TEST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=TEST_OAUTH_SCOPE,
                **account_kwargs
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/complete/submit/',
            data={
                'can_handle_neophonish': True,
            },
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
                'User-Agent': TEST_USER_AGENT,
                'Accept-Language': 'ru',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            state='complete_neophonish',
            account={
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'language': 'ru',
                    'country': 'ru',
                    'gender': 1,
                    'birthday': '1963-05-15',
                },
                'login': TEST_NEOPHONISH_LOGIN,
                'display_name': TEST_DISPLAY_NAME_DATA,
                'uid': TEST_UID,
                'display_login': '',
                'public_id': TEST_PUBLIC_ID,
            },
            has_recovery_method=True,
        )

    def test_complete_commit_social_with_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_SOCIAL_LOGIN,
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
                display_name=TEST_SOCIAL_DISPLAY_NAME,
                subscribed_to=[Service.by_slug('social')],
                scope=TEST_OAUTH_SCOPE,
                public_id=TEST_PUBLIC_ID,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.login = TEST_SOCIAL_LOGIN
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            'mobileproxy/1/bundle/complete/commit_social_with_login/',
            data={
                'track_id': self.track_id,
                'display_language': 'ru',
                'firstname': 'fname',
                'lastname': 'lname',
                'login': TEST_LOGIN,
                'password': TEST_PASSWORD,
                'validation_method': 'phone',
            },
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
                'User-Agent': TEST_USER_AGENT,
                'Accept-Language': 'ru',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            account={
                'person': {
                    'firstname': 'fname',
                    'lastname': 'lname',
                    'language': 'ru',
                    'country': 'us',
                    'gender': 1,
                    'birthday': '1963-05-15',
                },
                'login': TEST_LOGIN,
                'display_name': {
                    'name': 'Some User',
                    'default_avatar': '',
                },
                'uid': TEST_UID,
                'display_login': '',
                'public_id': TEST_PUBLIC_ID,
            },
            retpath=None,
        )

    def test_complete_commit_social_already_having_login(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                aliases={
                    'portal': TEST_LOGIN,
                    'social': TEST_SOCIAL_LOGIN,
                },
                display_name=TEST_DISPLAY_NAME_DATA,
                subscribed_to=[Service.by_slug('social')],
                scope=TEST_OAUTH_SCOPE,
                public_id=TEST_PUBLIC_ID,
            ),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.login = TEST_LOGIN
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            'mobileproxy/1/bundle/complete/commit_social/',
            data={
                'track_id': self.track_id,
                'display_language': 'ru',
                'firstname': 'fname',
                'lastname': 'lname',
                'password': TEST_PASSWORD,
                'validation_method': 'phone',
            },
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
                'User-Agent': TEST_USER_AGENT,
                'Accept-Language': 'ru',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            account={
                'person': {
                    'firstname': 'fname',
                    'lastname': 'lname',
                    'language': 'ru',
                    'country': 'us',
                    'gender': 1,
                    'birthday': '1963-05-15',
                },
                'login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME_DATA,
                'uid': TEST_UID,
                'display_login': TEST_LOGIN,
                'public_id': TEST_PUBLIC_ID,
            },
            retpath=None,
        )

    def test_complete_commit_lite(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LITE_LOGIN,
                aliases={
                    'lite': TEST_LITE_LOGIN,
                },
                display_name=TEST_DISPLAY_NAME_DATA,
                scope=TEST_OAUTH_SCOPE,
                public_id=TEST_PUBLIC_ID,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.login = TEST_LITE_LOGIN
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        rv = self.make_request(
            'mobileproxy/1/bundle/complete/commit_lite/',
            data={
                'track_id': self.track_id,
                'login': TEST_LOGIN,
                'display_language': 'ru',
                'firstname': 'fname',
                'lastname': 'lname',
                'password': TEST_PASSWORD,
                'validation_method': 'phone',
                'eula_accepted': 'true',
            },
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
                'User-Agent': TEST_USER_AGENT,
                'Accept-Language': 'ru',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            account={
                'person': {
                    'firstname': 'fname',
                    'lastname': 'lname',
                    'language': 'ru',
                    'country': 'us',
                    'gender': 1,
                    'birthday': '1963-05-15',
                },
                'login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME_DATA,
                'uid': TEST_UID,
                'display_login': TEST_LITE_LOGIN,
                'public_id': TEST_PUBLIC_ID,
            },
            retpath=None,
        )

    def test_complete_commit_neophonish(self):
        account_kwargs = deep_merge(
            dict(
                uid=TEST_UID,
                login=TEST_NEOPHONISH_LOGIN,
                aliases={
                    'neophonish': TEST_NEOPHONISH_LOGIN,
                    'phonenumber': TEST_PHONE_NUMBER.digital,
                },
                display_name=TEST_DISPLAY_NAME_DATA,
                firstname='fname',
                lastname='lname',
                public_id=TEST_PUBLIC_ID,
            ),
            build_phone_secured(1, TEST_PHONE_NUMBER.e164),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=TEST_OAUTH_SCOPE,
                **account_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.login = TEST_LITE_LOGIN

        rv = self.make_request(
            'mobileproxy/1/bundle/complete/commit_neophonish/',
            data={
                'track_id': self.track_id,
                'display_language': 'ru',
                'firstname': 'fname',
                'lastname': 'lname',
                'login': TEST_LOGIN,
                'password': TEST_PASSWORD,
            },
            headers=self.default_headers(**{
                'Authorization': TEST_AUTH_HEADER,
                'User-Agent': TEST_USER_AGENT,
                'Accept-Language': 'ru',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            account={
                'person': {
                    'firstname': 'fname',
                    'lastname': 'lname',
                    'language': 'ru',
                    'country': 'us',
                    'gender': 1,
                    'birthday': '1963-05-15',
                },
                'login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME_DATA,
                'uid': TEST_UID,
                'display_login': '',
                'public_id': TEST_PUBLIC_ID,
            },
            retpath=None,
        )

    def test_bundle_auth_forward_by_track_forward(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )
        self.env.oauth.set_response_value(
            'device_status',
            oauth_bundle_successful_response(
                has_auth_on_device=True,
                device_id='device-id',
                device_name=TEST_DEVICE_INFO['device_name'],
            ),
        )
        self.track_id = self.env.track_manager.create_test_track(
            manager=self.track_manager,
            track_type='authorize',
            process_name='forward_auth_to_mobile_by_track',
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.allow_oauth_authorization = True

        rv = self.make_request(
            'mobileproxy/1/bundle/auth/forward_by_track/exchange/',
            method='POST',
            data={
                'track_id': self.track_id,
                'client_id': 'client_id',
                'client_secret': 'client_secret',
            },
        )

        self.check_json_ok(
            rv,
            token=TEST_OAUTH_TOKEN,
        )

    def test_bundle_auth_forward_drive_build_nonce(self):
        self.env.blackbox.set_response_side_effect(
            'sign',
            [blackbox_sign_response('nonce')],
        )
        self.env.blackbox.set_response_side_effect(
            'get_device_public_key',
            [blackbox_get_device_public_key_response()],
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/auth/forward_drive/build_nonce/',
            method='POST',
            data={
                'drive_device_id': TEST_DRIVE_DEVICE_ID,
            },
        )

        self.check_json_ok(
            rv,
            nonce='nonce',
        )

    def test_bundle_auth_forward_drive_issue_authorization_code(self):
        get_signing_registry().add_from_dict(
            {
                'default_version_id': b'1',
                'versions': [
                    {
                        'id':   b'1',
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': b'0' * 32,
                    },
                ],
            }
        )
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                blackbox_check_device_signature_response(),
            ],
        )
        self.env.blackbox.set_response_side_effect(
            'get_device_public_key',
            [
                blackbox_get_device_public_key_response(),
            ],
        )
        save_drive_session(
            DriveSession(
                drive_device_id=TEST_DRIVE_DEVICE_ID,
                drive_session_id=TEST_DRIVE_SESSION_ID,
                uid=TEST_UID,
            ),
        )
        self.fake_drive_api.set_response_side_effect(
            'find_drive_session_id',
            [
                drive_api_find_drive_session_id_found_response(TEST_DRIVE_SESSION_ID),
            ],
        )
        self.env.oauth.set_response_side_effect(
            'issue_authorization_code',
            [
                oauth_bundle_successful_response(code=TEST_OAUTH_CODE),
            ],
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/auth/forward_drive/issue_authorization_code/',
            method='POST',
            data={
                'drive_device_id': TEST_DRIVE_DEVICE_ID,
                'nonce': TEST_NONCE,
                'signature': TEST_SIGNATURE,
                'oauth_client_id': TEST_CLIENT_ID,
                'oauth_client_secret': TEST_CLIENT_SECRET,
            },
        )

        self.check_json_ok(
            rv,
            authorization_code=TEST_OAUTH_CODE,
        )

    def test_bundle_drive_device_public_key_create(self):
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                blackbox_check_device_signature_response(),
            ],
        )
        self.env.blackbox.set_response_side_effect(
            'get_device_public_key',
            [
                blackbox_get_device_public_key_response(status=BLACKBOX_GET_DEVICE_PUBLIC_KEY_STATUS.PUBLIC_KEY_NOT_FOUND),
            ],
        )
        self.env.kolmogor.set_response_side_effect('get', ['0', '0'])
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

        rv = self.make_request(
            'mobileproxy/1/bundle/drive_device_public_key/create/',
            method='POST',
            data={
                'device_id': TEST_DRIVE_DEVICE_ID,
                'owner': TEST_OWNER,
                'public_key': TEST_PUBLIC_KEY,
                'check_nonce': TEST_NONCE,
                'check_signature': TEST_SIGNATURE,
            },
        )

        self.check_json_ok(rv)

    def test_auth_by_magic_integrational(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
            ),
        )
        self.env.oauth.set_response_value(
            'issue_device_code',
            issue_device_code_response(),
        )
        self.env.oauth.set_response_side_effect(
            'check_device_code',
            OAuthDeviceCodeNotAccepted(),
        )
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )

        with mock.patch(
            'passport.backend.api.views.bundle.auth.password.start.create_csrf_token',
            mock.Mock(return_value=TEST_CSRF_TOKEN),
        ):
            # Выдаём данные для QR и короткого кода
            rv = self.make_request(
                'mobileproxy/2/bundle/auth/password/submit/',
                method='POST',
                data={
                    'with_code': '1',
                },
                headers=self.default_headers(**{
                    'Ya-Client-Host': TEST_HOST,
                    'Ya-Client-Cookie': '',
                    'Ya-Client-User-Agent': 'curl',
                }),
            )

            track = self.track_manager.read(self.track_id)
            eq_(track.surface, 'mobile_proxy_password')

        self.check_json_ok(
            rv,
            track_id=self.track_id,
            csrf_token=TEST_CSRF_TOKEN,
            user_code='user-code',
            verification_url='ver-url',
            expires_in=30,
        )
        # поллим трек - не готово
        rv = self.make_request(
            'mobileproxy/2/bundle/auth/password/commit_magic/',
            method='POST',
            data={
                'csrf_token': TEST_CSRF_TOKEN,
            },
            headers=self.default_headers(**{
                'Ya-Client-Host': TEST_HOST,
                'Ya-Client-Cookie': '',
                'Ya-Client-User-Agent': 'curl',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            state='otp_auth_not_ready',
        )
        # "подтверждаем" код
        self.env.oauth.set_response_value(
            'check_device_code',
            check_device_code_response(uid=TEST_UID, scopes=['passport:create_session'])
        )
        # поллим трек - успех
        rv = self.make_request(
            'mobileproxy/2/bundle/auth/password/commit_magic/',
            method='POST',
            data={
                'csrf_token': TEST_CSRF_TOKEN,
            },
            headers=self.default_headers(**{
                'Ya-Client-Host': TEST_HOST,
                'Ya-Client-Cookie': '',
                'Ya-Client-User-Agent': 'curl',
            }),
        )
        self.check_json_ok(
            rv,
            track_id=self.track_id,
            state='otp_auth_finished',
        )
        # получаем токен
        rv = self.make_request(
            'mobileproxy/1/oauth/token/',
            data={
                'client_id': 'foo',
                'client_secret': 'bar',
            },
        )
        self.check_json_ok(
            rv,
            oauth={
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )

    def test_mobile_auth_by_sms_code_integrational(self):
        account_kwargs = dict(
            uid=TEST_UID,
            login=TEST_LOGIN,
            aliases={
                'portal': TEST_LOGIN,
                'phonenumber': TEST_PHONE_NUMBER.digital,
            },
            display_login=TEST_LOGIN,
            display_name={'name': TEST_DISPLAY_NAME},
            default_avatar_key=TEST_AVATAR_KEY,
            is_avatar_empty=False,
            crypt_password=TEST_PASSWORD_HASH,
            public_id=TEST_PUBLIC_ID,
        )
        phone_secured = build_phone_secured(
            1,
            TEST_PHONE_NUMBER.e164,
        )
        account_kwargs = deep_merge(account_kwargs, phone_secured)
        self.env.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(**account_kwargs),
        )
        self.env.code_generator.set_return_value(TEST_CONFIRMATION_CODE_LONG)
        self.env.yasms.set_response_value('send_sms', yasms_send_sms_response())
        self.env.oauth.set_response_value(
            '_token',
            {
                'access_token': TEST_OAUTH_TOKEN,
                'token_type': 'bearer',
            },
        )
        self.setup_profile_responses([
            ufo_api_profile_item(data=dict(TEST_FRESH_ITEM, device_id='device_id')),
        ])

        # стартовая ручка
        rv = self.make_request(
            'mobileproxy/2/bundle/mobile/start/',
            data={
                'login': TEST_LOGIN,
                'device_id': 'device_id',
                'device_name': 'iPhone',
                'x_token_client_id': 'x_client_id',
                'x_token_client_secret': 'x_client_secret',
                'avatar_size': 'islands-1500',
                'display_language': TEST_LANGUAGE,
                'cloud_token': TEST_CLOUD_TOKEN,
            },
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            method='POST',
        )
        self.check_json_ok(
            rv,
            primary_alias_type=1,
            can_authorize=True,
            auth_methods=['password', 'sms_code'],
            secure_phone_number=TEST_PHONE_NUMBER_DUMPED_MASKED,
            track_id=self.track_id,
        )
        # ручка отправки cмс
        rv = self.make_request(
            'mobileproxy/1/bundle/phone/confirm_tracked_secure/submit/',
            data={
                'display_language': 'ru',
            },
            headers=self.default_headers(**{'User-Agent': TEST_USER_AGENT}),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            code_length=6,
            deny_resend_until=TimeNow(),
            number=TEST_PHONE_NUMBER_DUMPED_MASKED,
            track_id=self.track_id,
        )
        # ручка проверки кода
        rv = self.make_request(
            'mobileproxy/1/bundle/phone/confirm_tracked_secure/commit/',
            data={
                'code': TEST_CONFIRMATION_CODE_LONG,
            },
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            number=TEST_PHONE_NUMBER_DUMPED_MASKED,
        )
        # ручка авторизации
        rv = self.make_request(
            'mobileproxy/1/bundle/mobile/auth/sms_code/',
            headers=self.default_headers(),
            method='POST',
            with_track=True,
        )
        self.check_json_ok(
            rv,
            uid=TEST_UID,
            primary_alias_type=1,
            has_password=True,
            display_login=TEST_LOGIN,
            normalized_display_login=TEST_LOGIN,
            display_name=TEST_DISPLAY_NAME,
            public_name=TEST_DISPLAY_NAME,
            avatar_url=TEST_AVATAR_URL_TEMPLATE % (TEST_AVATAR_KEY, 'islands-1500'),
            firstname='\\u0414',
            lastname='\\u0424',
            birthday='1963-05-15',
            gender='m',
            cloud_token=TEST_CLOUD_TOKEN,
            x_token=TEST_OAUTH_TOKEN,
            x_token_issued_at=TimeNow(),
            public_id=TEST_PUBLIC_ID,
        )

    def test_bundle_auth_social_register_by_token(self):
        self.env.social_api.set_response_value(
            'get_profiles',
            get_profiles_response([profile_item(uid=TEST_UID)]),
        )
        self.env.oauth.set_response_value(
            '_token',
            json.dumps({
                'token_type': 'bearer',
                'access_token': TEST_ACCESS_TOKEN,
                'expires_in': TEST_EXPIRES_IN,
            })
        )
        self.env.social_broker.set_response_value(
            'get_task_by_token',
            self.env.social_broker.get_task_by_token_response(
                provider_code='mt',
                userid=TEST_USERID,
                task_id='task_id1',
                firstname=TEST_FIRSTNAME,
            ),
        )
        self.env.social_api.set_response_value('bind_task_profile', json.dumps(get_bind_response()))
        response = blackbox_userinfo_response_multiple([
            dict(
                uid=TEST_UID,
                login=TEST_SOCIAL_LOGIN,
                aliases={'social': TEST_SOCIAL_LOGIN},
            ),
        ])
        self.env.blackbox.set_response_value('userinfo', response)
        rv = self.make_request(
            'mobileproxy/1/bundle/auth/social/register_by_token/',
            method='POST',
            headers={
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
            },
            data={
                'provider_token': TEST_PROVIDER_TOKEN,
                'provider': 'mt',
                'application': TEST_APPLICATION_ID1,
            },
        )

        self.check_json_ok(
            rv,
            access_token=TEST_ACCESS_TOKEN,
            expires_in=TEST_EXPIRES_IN,
        )

    def test_bundle_auth_otp_prepare(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = True


        rv = self.make_request(
            'mobileproxy/1/bundle/auth/otp/prepare/',
            method='POST',
            data={
                'track_id': self.track_id,
                'login': TEST_LOGIN,
                'otp': '123456',
            },
        )

        self.check_json_ok(
            rv,
            server_time=TimeNow(),
        )

    def test_bundle_auth_otp_not_me(self):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_allow_otp_magic = True
            track.correct_2fa_picture = 42
            track.correct_2fa_picture_expires_at = int(time()) + 60

        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

        rv = self.make_request(
            'mobileproxy/1/bundle/auth/otp/not_me/',
            method='POST',
            data={
                'track_id': self.track_id,
            },
        )

        self.check_json_ok(rv)

    def test_disable_phonish_auth_by_xtoken(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                enabled=True,
                aliases={'phonish': '_'},
                phones=[
                    {
                        'id': TEST_PHONE_ID1,
                        'number': TEST_PHONE_NUMBER.e164,
                        'created': datetime.now(),
                        'confirmed': datetime.now(),
                        'bound': datetime.now(),
                    },
                ],
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        rv = self.make_request(
            'mobileproxy/1/bundle/account/phonish/disable_auth_by_xtoken/',
            headers=self.default_headers(**{'Authorization': TEST_AUTH_HEADER}),
        )

        self.check_json_ok(rv)

    def test_bundle_delete_account_by_credentials(self):
        MtsAccountDeleteByCredentialsTestEnv(self.env).setup()

        rv = self.make_request(
            'mobileproxy/1/bundle/delete_account/by_credentials/',
            method='POST',
            headers={
                'authorization': TEST_AUTH_HEADER,
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
            },
        )

        self.check_json_ok(rv)


class IBlackboxResponse(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def kwargs(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass


class UserinfoBlackboxResponse(IBlackboxResponse):
    def __init__(self, env, response_dict):
        self._env = env
        self._kwargs = dict()
        self._response_dict = response_dict

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_userinfo_response(**self.kwargs)
        self._response_dict[self.kwargs.get('uid')] = response
        self._env.db.serialize(response)


class PhoneBlackboxResponseMixin(object):
    def add_phone(self):
        kwargs = deep_merge(
            self.kwargs,
            build_phone_bound(TEST_PHONE_ID1, TEST_PHONE_NUMBER1.e164),
        )
        self.kwargs.clear()
        self.kwargs.update(kwargs)


class OauthBlackboxResponse(
    PhoneBlackboxResponseMixin,
    IBlackboxResponse,
):
    def __init__(self, env):
        self._env = env
        self._kwargs = dict()

    @classmethod
    def from_userinfo(cls, userinfo_response, env):
        self = cls(env)
        self.kwargs.update(deep_merge(
            userinfo_response.kwargs,
            dict(
                scope=X_TOKEN_OAUTH_SCOPE,
            ),
        ))
        return self

    @property
    def kwargs(self):
        return self._kwargs

    def setup(self):
        response = blackbox_oauth_response(**self.kwargs)
        self._env.blackbox.extend_response_side_effect('oauth', [response])
        self._env.db.serialize(response, 'oauth')


class SocialUserinfoBlackboxResponse(UserinfoBlackboxResponse):
    def __init__(self, env):
        super(SocialUserinfoBlackboxResponse, self).__init__(env, dict())
        kwargs = deep_merge(
            self.kwargs,
            dict(
                aliases=dict(social=TEST_SOCIAL_LOGIN1),
                subscribed_to=[Service.by_slug('social')],
                uid=TEST_UID1,
            ),
        )
        self.kwargs.clear()
        self.kwargs.update(kwargs)


class MtsSocialUserinfoBlackboxResponse(
    PhoneBlackboxResponseMixin,
    SocialUserinfoBlackboxResponse,
):
    def __init__(self, env):
        super(MtsSocialUserinfoBlackboxResponse, self).__init__(env)
        self.add_phone()


class MtsSocialOauthBlackboxResponse(OauthBlackboxResponse):
    def __init__(self, env):
        super(MtsSocialOauthBlackboxResponse, self).__init__(env)
        self._kwargs = OauthBlackboxResponse.from_userinfo(MtsSocialUserinfoBlackboxResponse(env), env).kwargs


class SocialGetProfilesResponse(object):
    def __init__(self, env):
        self._env = env
        self._profiles = list()

    @classmethod
    def with_mts(cls, env):
        self = cls(env)
        self._profiles.extend([dict(
            provider_code='mt',
            uid=TEST_UID1,
        )])
        return self

    @property
    def profiles(self):
        return self._profiles

    def setup(self):
        response = get_profiles_response(self.profiles)
        self._env.social_api.extend_response_side_effect('get_profiles', [response])


class SocialDeleteAllProfilesByUidResponse(object):
    def __init__(self, env):
        self._env = env

    def setup(self):
        self._env.social_api.extend_response_side_effect('delete_all_profiles_by_uid', [dict()])


class BaseAccountDeleteByCredentialsTestEnv(object):
    def setup(self):
        self.setup_oauth()
        self.setup_family_info()
        self.setup_husky_api()
        self.setup_get_profiles()
        self.setup_delete_all_profiles_by_uid()

    def setup_oauth(self):
        pass

    def setup_family_info(self):
        pass

    def setup_husky_api(self):
        pass

    def setup_get_profiles(self):
        pass

    def setup_delete_all_profiles_by_uid(self):
        pass


class MtsAccountDeleteByCredentialsTestEnv(BaseAccountDeleteByCredentialsTestEnv):
    def __init__(self, env):
        super(MtsAccountDeleteByCredentialsTestEnv, self).__init__()

        self.oauth_response = MtsSocialOauthBlackboxResponse(env)
        self.oauth_response.kwargs.update(client_id=TEST_OAUTH_CLIENT_ID1)

        self.get_profiles_response = SocialGetProfilesResponse.with_mts(env)
        self.delete_all_profiles_by_uid_response = SocialDeleteAllProfilesByUidResponse(env)

    def setup_oauth(self):
        self.oauth_response.setup()

    def setup_get_profiles(self):
        self.get_profiles_response.setup()

    def setup_delete_all_profiles_by_uid(self):
        self.delete_all_profiles_by_uid_response.setup()
