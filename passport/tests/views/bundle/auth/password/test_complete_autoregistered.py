# -*- coding: utf-8 -*-
import base64
from datetime import timedelta
import json
import time

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.authorization import (
    AUTHORIZATION_SESSION_POLICY_PERMANENT,
    AUTHORIZATION_SESSION_POLICY_SESSIONAL,
)
from passport.backend.api.test.mixins import (
    AccountModificationNotifyTestMixin,
    ProfileTestMixin,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    COOKIE_L_VALUE,
    COOKIE_LAH_VALUE,
    COOKIE_YP_VALUE,
    COOKIE_YS_VALUE,
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YANDEX_LOGIN_COOKIE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    FRODO_RESPONSE_BAD_USER,
    FRODO_RESPONSE_OK,
    FRODO_RESPONSE_SPAM_USER,
    MDA2_BEACON_VALUE,
    SESSION,
    TEST_ACCEPT_LANGUAGE,
    TEST_AUTH_ID,
    TEST_COOKIE_TIMESTAMP,
    TEST_FUID01_COOKIE,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_NOT_STRONG_PASSWORD,
    TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER,
    TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE,
    TEST_NOT_STRONG_PASSWORD_IS_WORD,
    TEST_NOT_STRONG_PASSWORD_LENGTH,
    TEST_NOT_STRONG_PASSWORD_QUALITY,
    TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER,
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_PHONE_ID,
    TEST_PHONE_NUMBER,
    TEST_RAW_ENV_FOR_PROFILE,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIES,
    TEST_WEAK_PASSWORD,
    TEST_WEAK_PASSWORD_HASH,
    TEST_WEAK_PASSWORD_IS_SEQUENCE,
    TEST_WEAK_PASSWORD_IS_WORD,
    TEST_WEAK_PASSWORD_LENGTH,
    TEST_WEAK_PASSWORD_QUALITY,
    TEST_WEAK_PASSWORD_SEQUENCES_NUMBER,
    TEST_YANDEX_GID_COOKIE,
    TEST_YANDEXUID_COOKIE,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_lrandoms_response,
    blackbox_phone_bindings_response,
    blackbox_pwdhistory_response,
    blackbox_sessionid_multi_response,
    blackbox_test_pwd_hashes_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.builders.frodo.utils import get_phone_number_hash
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.counters import (
    registration_karma,
    sms_per_ip,
)
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.models.phones.faker import (
    assert_secure_phone_bound,
    build_phone_secured,
    event_lines_phone_created,
    event_lines_secure_bind_operation_created,
    event_lines_secure_bind_operation_deleted,
    event_lines_secure_phone_bound,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    check_all_url_params_match,
    check_url_contains_params,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import deep_merge


TEST_APP_ID = 'app-id'

TEST_SESSIONID = '0:old-session'
TEST_SSL_SESSIONID = '0:old-sslsession'


def build_headers(cookie=TEST_USER_COOKIES):
    return mock_headers(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie=cookie,
        user_agent=TEST_USER_AGENT,
        accept_language=TEST_ACCEPT_LANGUAGE,
    )


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    BIND_RELATED_PHONISH_ACCOUNT_APP_IDS={TEST_APP_ID},
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class CompleteAutoregisteredTestCase(
    AccountModificationNotifyTestMixin,
    BaseBundleTestViews,
    ProfileTestMixin,
):
    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_password': ['base']}))

        self.env.blackbox.set_response_value(
            'phone_bindings',
            blackbox_phone_bindings_response([]),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_complete_autoregistered = True
            track.is_password_passed = True
            track.uid = TEST_UID
            track.login = TEST_LOGIN
            track.country = 'ru'
            track.language = 'ru'
            track.human_readable_login = TEST_LOGIN
            track.authorization_session_policy = AUTHORIZATION_SESSION_POLICY_PERMANENT
            track.is_captcha_checked = True
            track.is_captcha_recognized = True
            track.have_password = True
            track.auth_method = 'password'
            track.device_application = TEST_APP_ID

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(TEST_PASSWORD_HASH): False,
                    base64.b64encode(TEST_WEAK_PASSWORD_HASH): False,
                },
            ),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[100],
            dbfields={
                'subscription.login_rule.100': 1,
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            attributes={'password.encrypted': TEST_WEAK_PASSWORD_HASH},
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                ip=TEST_IP,
                time=TEST_COOKIE_TIMESTAMP,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )
        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )
        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_OK)
        self.expected_password = TEST_PASSWORD
        self.phone_number = TEST_PHONE_NUMBER
        self.env.db.serialize(blackbox_response)

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)
        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)

        self.cookies_patches = [
            mock.patch.object(
                cookie_l.CookieL,
                'pack',
                self._cookie_l_pack,
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
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ]
        for patch in self.cookies_patches:
            patch.start()

        self.uid = TEST_UID
        self.expected_accounts = [
            {
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            },
        ]
        self.setup_profile_patches()
        self.setup_statbox_templates()
        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(ip=TEST_IP)

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            track_id=self.track_id,
            user_agent=TEST_USER_AGENT,
            ip=TEST_IP,
            consumer='dev',
            mode='any_auth',
        )
        self.env.statbox.bind_entry(
            'local_cookie_set',
            _inherit_from='cookie_set',
            _exclude=('consumer',),
            cookie_version='3',
            person_country='ru',
            ip_country='ru',
            captcha_passed='1',
            uid=str(self.uid),
            ip=TEST_IP,
            authid=TEST_AUTH_ID,
            yandexuid=TEST_YANDEXUID_COOKIE,
            input_login=TEST_LOGIN,
        )
        base_phone_params = dict(
            number=self.phone_number.masked_format_for_statbox,
            ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )
        self.env.statbox.bind_entry(
            'local_secure_bind_operation_created',
            _inherit_from='secure_bind_operation_created',
            _exclude=['mode', 'track_id'],
            **base_phone_params
        )
        self.env.statbox.bind_entry(
            'local_phone_confirmed',
            _inherit_from='phone_confirmed',
            code_checks_count='0',
            **base_phone_params
        )
        self.env.statbox.bind_entry(
            'local_secure_phone_bound',
            _inherit_from='secure_phone_bound',
            **base_phone_params
        )
        self.env.statbox.bind_entry(
            'password_validation_error',
            _exclude=['consumer', 'mode', 'ip', 'user_agent'],
            action='password_validation_error',
            weak=tskv_bool(True),
            policy='strong',
            password_quality=str(TEST_NOT_STRONG_PASSWORD_QUALITY),
            length=str(TEST_NOT_STRONG_PASSWORD_LENGTH),
            classes_number=str(TEST_NOT_STRONG_PASSWORD_CLASSES_NUMBER),
            sequences_number=str(TEST_NOT_STRONG_PASSWORD_SEQUENCES_NUMBER),
            is_sequence=tskv_bool(TEST_NOT_STRONG_PASSWORD_IS_SEQUENCE),
            is_word=tskv_bool(TEST_NOT_STRONG_PASSWORD_IS_WORD),
            is_additional_word=tskv_bool(False),
            additional_subwords_number='0',
        )
        self.env.statbox.bind_entry(
            'registration_with_sms_error',
            _exclude=['consumer', 'user_agent'],
            mode='complete_autoregistered',
            action='registration_with_sms',
            track_id=self.track_id,
            ip=TEST_IP,
            error='registration_sms_per_ip_limit_has_exceeded',
            counter_prefix='registration:sms:ip',
            is_special_testing_ip='0',
        )

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.teardown_profile_patches()
        for patch in reversed(self.cookies_patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.cookies_patches
        del self._cookie_yp_pack
        del self._cookie_ys_pack
        del self._cookie_l_pack
        del self._cookie_lah_pack

    def make_request(self, headers=None, exclude=None, validated_via_phone=False, **kwargs):
        data = {
            'track_id': self.track_id,
            'password': self.expected_password,
            'eula_accepted': '1',
            'timezone': 'Europe/Paris',
            'country': 'tr',
            'language': 'tr',
            'birthday': '1950-01-30',
            'validation_method': 'phone' if validated_via_phone else 'captcha',
        }
        data.update(kwargs)
        if exclude:
            for key in exclude:
                data.pop(key)
        headers = build_headers() if headers is None else headers
        return self.env.client.post(
            '/2/bundle/auth/password/complete_autoregistered/?consumer=dev',
            data=data,
            headers=headers,
        )

    def check_response_ok(self, response, accounts=None, with_lah=True):
        expected_response = {
            'cookies': [
                EXPECTED_SESSIONID_COOKIE,
                EXPECTED_SESSIONID_SECURE_COOKIE,
                EXPECTED_YP_COOKIE,
                EXPECTED_YS_COOKIE,
                EXPECTED_L_COOKIE,
                EXPECTED_YANDEX_LOGIN_COOKIE,
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
            'default_uid': TEST_UID,
            'account': {
                'uid': int(TEST_UID),
                'login': TEST_LOGIN,
                'display_login': TEST_LOGIN,
            },
        }
        if with_lah:
            expected_response['cookies'].append(EXPECTED_LAH_COOKIE)
        if accounts:
            expected_response['accounts'] = accounts

        self.assert_ok_response(response, ignore_order_for=['cookies'], **expected_response)

    def create_frodo_params(self, **kwargs):
        params = {
            'uid': str(TEST_UID),
            'login': TEST_LOGIN,
            'from': '',
            'consumer': 'dev',
            'passwd': '10.0.9.1',
            'passwdex': '3.6.0.0',
            'v2_password_quality': '80',
            'hintqid': '',
            'hintq': '0.0.0.0.0.0',
            'hintqex': '0.0.0.0.0.0',
            'hinta': '0.0.0.0.0.0',
            'hintaex': '0.0.0.0.0.0',
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'v2_yandex_gid': TEST_YANDEX_GID_COOKIE,
            'fuid': TEST_FUID01_COOKIE,
            'useragent': TEST_USER_AGENT,
            'host': TEST_HOST,
            'ip_from': TEST_IP,
            'v2_ip': TEST_IP,
            'valkey': '0000000000',
            'action': 'change_password',
            'v2_track_created': TimeNow(),
            'xcountry': 'tr',
            'lang': 'tr',
            'v2_old_password_quality': kwargs.pop('old_password_quality', '10'),
            'v2_account_country': 'tr',
            'v2_account_language': 'tr',
            'v2_account_timezone': 'Europe/Paris',
            'v2_accept_language': 'ru',
            'v2_account_karma': '',
            'v2_is_ssl': '1',
            'v2_has_cookie_l': '1',
            'v2_has_cookie_yandex_login': '0',
            'v2_has_cookie_my': '1',
            'v2_has_cookie_ys': '0',
            'v2_has_cookie_yp': '0',
            'v2_cookie_my_block_count': '1',
            'v2_cookie_my_language': 'tt',
            'v2_cookie_l_login': TEST_LOGIN,
            'v2_cookie_l_uid': str(TEST_UID),
            'v2_cookie_l_timestamp': str(TEST_COOKIE_TIMESTAMP),
            'v2_application': TEST_APP_ID,
        }
        params.update(**kwargs)
        return EmptyFrodoParams(**params)

    def check_frodo_call(self, **kwargs):
        requests = self.env.frodo.requests
        eq_(len(requests), 1)
        requests[0].assert_query_equals(self.create_frodo_params(**kwargs))

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def get_account_info(self):
        return {
            'uid': TEST_UID,
            'login': TEST_LOGIN,
            'display_name': {'name': '', 'default_avatar': ''},
            'display_login': TEST_LOGIN,
        }

    def assert_sessionid_called(self, ssl_session=None):
        sessionid_url = self.env.blackbox._mock.request.call_args_list[3][0][1]
        expected_args = {
            'method': 'sessionid',
            'multisession': 'yes',
            'sessionid': TEST_SESSIONID,
        }
        if ssl_session:
            expected_args['sslsessionid'] = ssl_session
        check_url_contains_params(
            sessionid_url,
            expected_args,
        )

    def assert_createsession_called(self, call_index=None):
        default_call_index = 5 if self.is_password_hash_from_blackbox else 4
        call_index = call_index if call_index is not None else default_call_index
        url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        check_all_url_params_match(
            url,
            {
                'is_lite': '0',
                'method': 'createsession',
                'lang': '1',
                'password_check_time': TimeNow(),
                'have_password': u'1',
                'ver': u'3',
                'uid': str(self.uid),
                'format': 'json',
                'keyspace': 'yandex.ru',
                'ttl': '5',
                'userip': TEST_IP,
                'host_id': '7f',
                'create_time': TimeNow(),
                'auth_time': TimeNow(as_milliseconds=True),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )

    def assert_editsession_called(self, editsession_index, ssl_session=None):
        edit_session_url = self.env.blackbox._mock.request.call_args_list[editsession_index][0][1]
        expected_args = {
            'uid': str(self.uid),
            'format': 'json',
            'sessionid': TEST_SESSIONID,
            'host': 'passport-test.yandex.ru',
            'userip': TEST_IP,
            'method': 'editsession',
            'op': 'add',
            'password_check_time': TimeNow(),
            'have_password': '1',
            'new_default': str(self.uid),
            'keyspace': 'yandex.ru',
            'lang': '1',
            'create_time': TimeNow(),
            'guard_hosts': 'passport-test.yandex.ru',
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }
        if ssl_session:
            expected_args['sslsessionid'] = ssl_session
        check_all_url_params_match(
            edit_session_url,
            expected_args,
        )

    def _assert_user_phones_requested(self):
        request = self.env.blackbox.requests[0]
        request.assert_post_data_contains({
            'method': 'userinfo',
            'aliases': 'all_with_hidden',
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
        })
        request.assert_contains_attributes({
            'phones.secure',
            'phones.default',
        })

    def build_auth_log_entry(self, status, uid):
        return [
            ('uid', str(uid)),
            ('status', status),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('client_name', 'passport'),
            ('useragent', TEST_USER_AGENT),
            ('ip_from', TEST_IP),
        ]

    def assert_auth_and_event_log_ok(self, password_hash, expected_auth_log_records, additional_entries=None,
                                     is_phone_bound=True, user_agent=TEST_USER_AGENT):
        log_entries = {
            'action': 'complete_autoregistered',
            'consumer': 'dev',
            # Пароль
            'info.password_quality': '80',
            'info.password': password_hash,
            'info.password_update_time': TimeNow(),
            'info.glogout': TimeNow(),
            'info.tz': 'Europe/Paris',
            'info.country': 'tr',
            'info.lang': 'tr',
            'sid.rm': '100|%s' % TEST_LOGIN,
            'user_agent': user_agent,
        }
        if additional_entries:
            log_entries.update(additional_entries)
        self.env.event_logger.assert_contains(log_entries)

        if is_phone_bound:
            self.env.event_logger.assert_contains(
                event_lines_phone_created(
                    uid=self.uid,
                    phone_id=TEST_PHONE_ID,
                    phone_number=self.phone_number,
                    user_agent=user_agent,
                ) +
                event_lines_secure_bind_operation_created(
                    uid=self.uid,
                    phone_id=TEST_PHONE_ID,
                    phone_number=self.phone_number,
                    operation_id=1,
                    operation_ttl=timedelta(seconds=60),
                ) +
                (
                    {'uid': str(self.uid), 'name': 'action', 'value': 'acquire_phone'},
                    {'uid': str(self.uid), 'name': 'consumer', 'value': 'dev'},
                    {'uid': str(self.uid), 'name': 'user_agent', 'value': user_agent},
                ) +
                event_lines_secure_bind_operation_deleted(
                    uid=self.uid,
                    phone_id=TEST_PHONE_ID,
                    phone_number=self.phone_number,
                    operation_id=1,
                    action='complete_autoregistered',
                    user_agent=user_agent,
                ) +
                event_lines_secure_phone_bound(
                    uid=self.uid,
                    phone_id=TEST_PHONE_ID,
                    phone_number=self.phone_number,
                    operation_id=1,
                    action='complete_autoregistered',
                    user_agent=user_agent,
                ),
            )

        eq_(self.env.auth_handle_mock.call_count, len(expected_auth_log_records))
        # Остальные записи об апдейте сессий для каждого валидного пользователя в куке
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_auth_log_records,
        )

    def assert_statbox_ok(self, session_method, uids_count, **kwargs):
        self.env.statbox.assert_equals(
            self.env.statbox.entry(
                'local_cookie_set',
                session_method=session_method,
                uids_count=str(uids_count),
                **kwargs
            ),
            offset=-1,
        )

    def check_ok(self, response, entries=None, check_frodo=True, strong_password=False,
                 frodo_kwargs=None, is_phone_bound=True, with_lah=True):
        if entries is None:
            entries = {}
        self.check_response_ok(
            response,
            accounts=[self.get_account_info()],
            with_lah=with_lah,
        )
        self.check_db()

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db='passportdbshard1')
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('1:'))

        if strong_password:
            self.env.db.check('password_history', 'encrypted_password', TEST_WEAK_PASSWORD_HASH, uid=TEST_UID, db='passportdbshard1')
            self.env.db.check('password_history', 'ts', DatetimeNow(), uid=TEST_UID, db='passportdbshard1')

        self.assert_auth_and_event_log_ok(
            password_hash=eav_pass_hash,
            expected_auth_log_records=[
                self.build_auth_log_entry('ses_create', self.uid),
            ],
            additional_entries=entries,
            is_phone_bound=is_phone_bound,
        )

        expected_social_binding_entries = []
        if is_phone_bound:
            expected_social_binding_entries.append(
                self.env.social_binding_logger.entry(
                    'bind_phonish_account_by_track',
                    uid=str(TEST_UID),
                    track_id=self.track_id,
                    ip=TEST_IP,
                ),
            )
        self.env.social_binding_logger.assert_has_written(expected_social_binding_entries)

        track = self.track_manager.read(self.track_id)
        ok_(track.session)
        if check_frodo:
            self.check_frodo_call(
                action='change_password_to_strong' if strong_password else 'change_password',
                **(frodo_kwargs or {})
            )

    def check_db(self, with_optional_params=True):
        timenow = TimeNow()
        if with_optional_params:
            self.env.db.check('attributes', 'person.country', 'tr', uid=TEST_UID, db='passportdbshard1')
            self.env.db.check('attributes', 'person.timezone', 'Europe/Paris', uid=TEST_UID, db='passportdbshard1')
            self.env.db.check('attributes', 'person.language', 'tr', uid=TEST_UID, db='passportdbshard1')
        else:
            self.env.db.check_missing('attributes', 'person.country', uid=TEST_UID, db='passportdbshard1')
            self.env.db.check_missing('attributes', 'person.timezone', uid=TEST_UID, db='passportdbshard1')
            self.env.db.check_missing('attributes', 'person.language', uid=TEST_UID, db='passportdbshard1')

        self.env.db.check('attributes', 'person.gender', 'm', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'person.birthday', '1963-05-15', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'password.update_datetime', timenow, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'password.quality', '3:80', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.is_creating_required', uid=TEST_UID, db='passportdbshard1')
        self.env.db.check_missing('attributes', 'password.forced_changing_reason', uid=TEST_UID, db='passportdbshard1')

    def test_user_not_verified_by_captcha_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False

        rv = self.make_request(display_language='ru', question='question', answer='lala')

        self.assert_error_response(rv, ['user.not_verified'])

    def test_user_not_verified_by_phone_error(self):
        rv = self.make_request(validated_via_phone=True, display_language='ru')

        self.assert_error_response(rv, ['user.not_verified'])

    def test_user_verified_by_phone_but_captcha_required_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = False
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164

        rv = self.make_request(display_language='ru', question='question', answer='lala')

        self.assert_error_response(rv, ['user.not_verified'])

    def test_eula_not_accepted_error(self):
        rv = self.make_request(eula_accepted='0')

        self.assert_error_response(rv, ['eula_accepted.not_accepted'])

    def test_ok_without_optional_params(self):
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)
        resp = self.make_request(
            display_language='ru',
            question='question',
            answer='lala',
            exclude=['country', 'timezone', 'language', 'birthday'],
        )
        self.check_response_ok(resp, accounts=[self.get_account_info()])
        self.check_frodo_call(
            xcountry='ru',
            v2_account_country='ru',
            lang='ru',
            v2_account_language='ru',
            v2_account_timezone='Europe/Moscow',
        )
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 1)
        self.check_db(with_optional_params=False)

    def test_ok_with_env_profile_modification(self):
        resp = self.make_request(
            display_language='ru',
            question='question',
            answer='lala',
        )
        self.check_response_ok(resp, accounts=[self.get_account_info()])
        profile = self.make_user_profile(raw_env=TEST_RAW_ENV_FOR_PROFILE)
        self.assert_profile_written_to_auth_challenge_log(profile)

    def test_ok_with_empty_headers(self):
        resp = self.make_request(
            headers=mock_headers(
                host=TEST_HOST,
                user_ip=TEST_IP,
                user_agent='',
                cookie='',
                referer='',
            ),
            display_language='ru',
            question='question',
            answer='lala',
        )
        self.check_response_ok(resp, accounts=[self.get_account_info()])
        self.check_frodo_call(
            useragent='',
            v2_accept_language='',
            valkey='0000000100',
            fuid='',
            yandexuid='',
            v2_yandex_gid='',
            v2_has_cookie_my='0',
            v2_has_cookie_l='0',
            v2_cookie_my_block_count='',
            v2_cookie_my_language='',
            v2_cookie_l_uid='',
            v2_cookie_l_login='',
            v2_cookie_l_timestamp='',
        )

    def test_phone_logged(self):
        blackbox_response = blackbox_userinfo_response(
            **deep_merge(
                dict(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    subscribed_to=[100],
                    dbfields={
                        'subscription.login_rule.100': 1,
                        'password_quality.quality.uid': 10,
                        'password_quality.version.uid': 3,
                    },
                    attributes={'password.encrypted': TEST_WEAK_PASSWORD_HASH},
                ),
                build_phone_secured(phone_id=TEST_PHONE_ID, phone_number=self.phone_number.e164),
            )
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        resp = self.make_request(
            headers=mock_headers(
                host=TEST_HOST,
                user_ip=TEST_IP,
                user_agent='',
                cookie=TEST_USER_COOKIES,
                referer='',
            ),
            display_language='ru',
            question='question',
            answer='lala',
        )
        self.check_response_ok(resp, accounts=[self.get_account_info()])
        self.env.phone_logger.assert_has_written([
            self.env.phone_logger.get_log_entry(
                TEST_UID,
                self.phone_number.e164,
                TEST_YANDEXUID_COOKIE,
            ),
        ])

    def test_complete__wrong_host__error(self):
        resp = self.make_request(headers=mock_headers(
            host='google.com',
            user_ip=TEST_IP,
            user_agent='',
            cookie='',
        ))
        self.assert_error_response(resp, ['host.invalid'])

    def test_blackbox_userinfo_no_uid_error(self):
        """ЧЯ вернул пустой ответ по методу userinfo - ошибка обрабатывается"""
        userinfo_response = blackbox_userinfo_response(uid=None)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            userinfo_response,
        )

        resp = self.make_request()

        self.assert_error_response(resp, ['account.not_found'])

    def test_blackbox_user_is_disabled_error(self):
        """Пользователь с этим uid "выкл" (disabled) - ошибка обрабатывается"""
        blackbox_response = blackbox_userinfo_response(enabled=False)
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'])

    def test_blackbox_user_is_disabled_on_deletion_error(self):
        """
        Пользователь с этим uid был заблокирован при удалении,,
        т.к. подписан на блокирующий SID. Это не мешает нам обработать
        ошибку.
        """
        blackbox_response = blackbox_userinfo_response(
            enabled=False,
            attributes={
                'account.is_disabled': ACCOUNT_DISABLED_ON_DELETION,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'])

    def test_empty_display_language_and_answer_args(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['answer.empty', 'display_language.empty'])

    def test_no_control_question_args(self):
        rv = self.make_request(display_language='ru', answer='answer')

        self.assert_error_response(rv, ['question.empty'])

    def test_too_many_control_question_args(self):
        rv = self.make_request(
            display_language='ru',
            question='question',
            question_id=1,
            answer='answer',
        )

        self.assert_error_response(rv, ['question.inconsistent'])

    def test_is_complete_autoregistered_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.is_complete_autoregistered = False

        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        rv = self.make_request()

        self.assert_error_response(rv, ['track.invalid_state'])

    def test_error_authorization_already_passed(self):
        """В треке указано, что авторизация уже пройдена"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = SESSION['session']['value']

        resp = self.make_request()

        self.assert_error_response(resp, ['account.auth_passed'])
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_no_sid100_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164

        blackbox_response = blackbox_userinfo_response(
            uid=str(TEST_UID),
            login=TEST_LOGIN,
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        rv = self.make_request()

        self.assert_error_response(rv, ['action.not_required'])

    def test_strong_password_found_in_history(self):
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=True),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164

        rv = self.make_request()
        self.assert_error_response(rv, ['password.found_in_history'])

    def test_password_equals_previous_from_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(TEST_WEAK_PASSWORD_HASH): True,
                },
            ),
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['password.equals_previous'])

    def test_password_equals_previous_from_account(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164
            track.password_hash = None

        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response(
                {
                    base64.b64encode(TEST_PASSWORD_HASH): True,
                },
            ),
        )

        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[100],
            dbfields={
                'subscription.login_rule.100': 1,
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            attributes={'password.encrypted': TEST_PASSWORD_HASH},
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        rv = self.make_request()
        self.assert_error_response(rv, ['password.equals_previous'])

    def test_strong_password_is_too_weak(self):
        """При подписке на сильный пароль, пришел очень слабый пароль"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_strong_password_policy_required = True
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164

        # Пароль с качеством 50
        rv = self.make_request(password=TEST_NOT_STRONG_PASSWORD)

        self.assert_error_response(rv, ['password.weak'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('password_validation_error'),
        ])

    def test_password_is_too_weak(self):
        """Пароль слишком слабый"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164

        # Пароль с качеством 0
        rv = self.make_request(password=TEST_WEAK_PASSWORD)
        self.assert_error_response(rv, ['password.weak'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'password_validation_error',
                policy='basic',
                is_sequence=tskv_bool(TEST_WEAK_PASSWORD_IS_SEQUENCE),
                sequences_number=str(TEST_WEAK_PASSWORD_SEQUENCES_NUMBER),
                is_word=tskv_bool(TEST_WEAK_PASSWORD_IS_WORD),
                length=str(TEST_WEAK_PASSWORD_LENGTH),
                password_quality=str(TEST_WEAK_PASSWORD_QUALITY),
            ),
        ])

    def test_registration_sms_limit_reached_error(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_phone_number = TEST_PHONE_NUMBER.e164
            track.phone_confirmation_is_confirmed = True
            track.is_captcha_checked = False
            track.is_captcha_recognized = False

        counter = sms_per_ip.get_registration_completed_with_phone_counter(TEST_IP)
        for i in range(counter.limit + 1):
            counter.incr(TEST_IP)

        rv = self.make_request(validated_via_phone=True)
        self.assert_error_response(rv, ['account.registration_limited'])
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'registration_with_sms_error',
                counter_current_value=str(counter.limit + 1),
                counter_limit_value=str(counter.limit),
            ),
        ])

    def test_account_global_logout_after_track_created_error(self):
        """
        Хотим закомплитить пользователя, но аккаунт был глобально разлогинен
        уже после того, как завели трек для комплита.
        """
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[100],
            dbfields={
                'subscription.login_rule.100': 1,
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            attributes={
                'account.global_logout_datetime': str(int(time.time()) + 1),
                'password.encrypted': TEST_WEAK_PASSWORD_HASH,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        rv = self.make_request()
        self.assert_error_response(rv, ['account.global_logout'])

    def call_with_phone(self, strong_password=False, action=None, old_password_quality='10', with_lah=True):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164
            track.is_captcha_recognized = False

        rv = self.make_request(validated_via_phone=True)
        self.check_ok(
            rv,
            strong_password=strong_password,
            frodo_kwargs={
                'phonenumber': TEST_PHONE_NUMBER.masked_format_for_frodo,
                'v2_phonenumber_hash': get_phone_number_hash(TEST_PHONE_NUMBER.e164),
                'old_password_quality': old_password_quality,
            },
            with_lah=with_lah,
        )

        self._assert_user_phones_requested()

        self.env.statbox.assert_contains([
            self.env.statbox.entry('local_secure_bind_operation_created'),
            self.env.statbox.entry('local_phone_confirmed'),
            self.env.statbox.entry('local_secure_phone_bound'),
        ])

        assert_secure_phone_bound.check_db(
            db_faker=self.env.db,
            uid=TEST_UID,
            phone_attributes={
                'id': TEST_PHONE_ID,
                'bound': DatetimeNow(),
                'secure': DatetimeNow(),
            },
        )

    def test_ok_with_phone(self):
        self.call_with_phone()

        createsession_requests = self.env.blackbox.get_requests_by_method('createsession')
        eq_(len(createsession_requests), 1)
        createsession_requests[0].assert_query_contains({'is_lite': '0'})

    def test_ok_with_phone_and_strong_policy(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[67, 100],
            dbfields={
                'subscription.login_rule.100': 1,
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            attributes={'password.encrypted': TEST_WEAK_PASSWORD_HASH},
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.call_with_phone(
            strong_password=True,
        )

    def test_ok_with_phone_without_password(self):
        """Пароля на аккаунте может не быть, все равно привязываем телефон"""
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[100],
            dbfields={
                'subscription.login_rule.100': 1,
            },
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.call_with_phone(old_password_quality='')

    def test_ok_with_short_session(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.authorization_session_policy = AUTHORIZATION_SESSION_POLICY_SESSIONAL

        self.call_with_phone(with_lah=False)

    def test_ok(self):
        rv = self.make_request(display_language='ru', question='question', answer='lala')
        self.check_ok(
            rv,
            entries={'info.hintq': '99:question', 'info.hinta': 'lala'},
            is_phone_bound=False,
        )

        call_index = 5 if self.is_password_hash_from_blackbox else 4
        url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        check_url_contains_params(url, {'is_lite': '0', 'method': 'createsession'})

    def test_send_push_when_password_changed(self):
        rv = self.make_request(
            answer='lala',
            country='ru',
            display_language='ru',
            language='ru',
            question='question',
        )

        self.assert_ok_response(rv, check_all=False)

        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='changed_password',
            uid=TEST_UID,
            title='Пароль в аккаунте {} успешно изменён'.format(TEST_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )

    def test_ok_with_question_id(self):
        rv = self.make_request(display_language='en', question_id='1', answer='lala')
        self.check_ok(
            rv,
            entries={'info.hintq': '1:Your mother\'s maiden name', 'info.hinta': 'lala'},
            is_phone_bound=False,
        )

    def test_ok_subscribe_user(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.service = 'lenta'
        rv = self.make_request(display_language='ru', question='question', answer='lala')
        self.check_ok(
            rv,
            entries={
                'info.hintq': '99:question',
                'info.hinta': 'lala',
                'sid.add': '23',
            },
            check_frodo=False,
            is_phone_bound=False,
        )
        self.check_frodo_call(**{'from': 'lenta'})

        self.env.db.check('attributes', 'subscription.23', '1', uid=TEST_UID, db='passportdbshard1')

    def test_ok_with_frodo_spam_user(self):
        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_SPAM_USER)
        self.env.frodo.set_response_value(u'confirm', u'')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164

        response = self.make_request(validated_via_phone=True)

        self.check_response_ok(response, accounts=[self.get_account_info()])

        self.env.db.check('attributes', 'karma.value', '85', uid=TEST_UID, db='passportdbshard1')

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(
            self.create_frodo_params(
                phonenumber=TEST_PHONE_NUMBER.masked_format_for_frodo,
                v2_phonenumber_hash=get_phone_number_hash(TEST_PHONE_NUMBER.e164),
            ),
        )

    def test_ok_with_frodo_bad_user(self):
        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_BAD_USER)
        self.env.frodo.set_response_value(u'confirm', u'')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164

        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 0)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)
        response = self.make_request(validated_via_phone=True)

        self.check_response_ok(response, accounts=[self.get_account_info()])

        self.env.db.check('attributes', 'karma.value', '100', uid=TEST_UID, db='passportdbshard1')

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(
            self.create_frodo_params(
                phonenumber=TEST_PHONE_NUMBER.masked_format_for_frodo,
                v2_phonenumber_hash=get_phone_number_hash(TEST_PHONE_NUMBER.e164),
            ),
        )
        eq_(registration_karma.get_bad_buckets().get(TEST_IP), 1)
        eq_(registration_karma.get_good_buckets().get(TEST_IP), 0)

    def test_ok_with_strong_password(self):
        blackbox_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[100, 67],
            dbfields={
                'subscription.login_rule.100': 1,
                'password_quality.quality.uid': 10,
                'password_quality.version.uid': 3,
            },
            attributes={'password.encrypted': TEST_WEAK_PASSWORD_HASH},
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )

        self.env.frodo.set_response_value(u'check', FRODO_RESPONSE_SPAM_USER)
        self.env.frodo.set_response_value(u'confirm', u'')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.phone_confirmation_is_confirmed = True
            track.phone_confirmation_phone_number = self.phone_number.e164
            track.is_strong_password_policy_required = True

        response = self.make_request(validated_via_phone=True)

        self.check_response_ok(response, accounts=[self.get_account_info()])

        self.env.db.check('password_history', 'encrypted_password', TEST_WEAK_PASSWORD_HASH, uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('password_history', 'ts', DatetimeNow(), uid=TEST_UID, db='passportdbshard1')
        self.env.db.check('attributes', 'karma.value', '85', uid=TEST_UID, db='passportdbshard1')

        # Проверяем параметры для frodo
        requests = self.env.frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_query_equals(
            self.create_frodo_params(
                action='change_password_to_strong',
                phonenumber=TEST_PHONE_NUMBER.masked_format_for_frodo,
                v2_phonenumber_hash=get_phone_number_hash(TEST_PHONE_NUMBER.e164),
            ),
        )

    def test_with_cookies__overflow_error(self):
        """
        Пришли с мультикукой, на которую
        ЧЯ говорит, что в куку больше нельзя дописать пользователей
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                time=TEST_COOKIE_TIMESTAMP,
                ip=TEST_IP,
                age='123',
                allow_more_users=False,
            ),
        )
        resp = self.make_request(
            display_language='ru',
            question='question',
            answer='lala',
            headers=build_headers(
                cookie='Session_id=0:old-session;sessionid2=%s;%s' % (TEST_SSL_SESSIONID, TEST_USER_COOKIES),
            ),
        )
        eq_(resp.status_code, 200, [resp.status_code, resp.data])
        actual_response = json.loads(resp.data)
        eq_(
            actual_response,
            {
                'status': 'error',
                'errors': [u'sessionid.overflow'],
            },
        )

    def test_ok_without_cookie(self):
        """
        Дорегистрируем пользователя вообще без куки
        Вызов должен проходить так же как для моноавторизации
        """

        rv = self.make_request(display_language='ru', question='question', answer='lala')

        self.check_response_ok(
            rv,
            accounts=[{
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            }],
        )
        self.assert_createsession_called()
        self.assert_statbox_ok('create', '1')
        self.check_frodo_call()

    def test_ok_with_invalid_cookie(self):
        """
        Дорегистрируем пользователя вообще c невалидной полностью кукой
        Вызов должен проходить так же как для моноавторизации
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        rv = self.make_request(
            display_language='ru',
            question='question',
            answer='lala',
            headers=build_headers(cookie='Session_id=0:old-session;%s' % TEST_USER_COOKIES),
        )

        self.check_response_ok(
            rv,
            accounts=[{
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            }],
        )

        self.assert_sessionid_called()
        self.assert_createsession_called(call_index=6 if self.is_password_hash_from_blackbox else 5)
        self.assert_statbox_ok('create', '1')
        self.check_frodo_call()

    def test_ok_with_invalid_sesguard_cookie(self):
        """
        Поведение с неверным sessguard аналогично поведению с невалидной кукой
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_WRONG_GUARD_STATUS,
            ),
        )

        rv = self.make_request(
            display_language='ru',
            question='question',
            answer='lala',
            headers=build_headers(
                cookie='Session_id=0:old-session;%s' % TEST_USER_COOKIES),
        )

        self.check_response_ok(
            rv,
            accounts=[{
                'uid': self.uid,
                'login': TEST_LOGIN,
                'display_name': {'name': '', 'default_avatar': ''},
                'display_login': TEST_LOGIN,
            }],
        )

        self.assert_sessionid_called()
        self.assert_createsession_called(
            call_index=6 if self.is_password_hash_from_blackbox else 5)
        self.assert_statbox_ok('create', '1')
        self.check_frodo_call()

    def test_ok_with_cookie_with_other_account_by_https(self):
        """
        Дорегистрируем пользователя с мультикукой
        Проверим что записали в auth логи и статбокc все верно
        Сделаем это по хттпс
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
                time=TEST_COOKIE_TIMESTAMP,
                ip=TEST_IP,
                age='123',
                ttl=5,
            ),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.old_session = TEST_SESSIONID

        rv = self.make_request(
            display_language='ru',
            question='question',
            answer='lala',
            headers=build_headers(
                cookie='Session_id=0:old-session;sessionid2=%s;%s' % (TEST_SSL_SESSIONID, TEST_USER_COOKIES),
            ),
        )

        self.check_response_ok(
            rv,
            accounts=[
                {
                    'uid': 1234,
                    'login': 'other_login',
                    'display_name': {'name': '', 'default_avatar': ''},
                    'display_login': 'other_login',
                },
                {
                    'uid': self.uid,
                    'login': TEST_LOGIN,
                    'display_name': {'name': '', 'default_avatar': ''},
                    'display_login': TEST_LOGIN,
                },
            ],
        )

        self.assert_sessionid_called(ssl_session=TEST_SSL_SESSIONID)
        self.assert_editsession_called(
            ssl_session=TEST_SSL_SESSIONID,
            editsession_index=6 if self.is_password_hash_from_blackbox else 5,
        )

        eav_pass_hash = self.env.db.get('attributes', 'password.encrypted', uid=TEST_UID, db='passportdbshard1')
        self.assert_auth_and_event_log_ok(
            eav_pass_hash,
            [
                self.build_auth_log_entry('ses_update', '1234'),
                self.build_auth_log_entry('ses_create', self.uid),
            ],
            additional_entries={
                'info.hinta': 'lala',
                'info.hintq': '99:question',
            },
            is_phone_bound=False,
        )
        self.assert_statbox_ok('edit', '2', old_session_uids='1234')
        self.check_frodo_call(
            v2_session_age='123',
            v2_session_ip=TEST_IP,
            v2_session_create_timestamp=str(TEST_COOKIE_TIMESTAMP),
        )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class CompleteAutoregisteredNoBlackboxHashTestCase(CompleteAutoregisteredTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
