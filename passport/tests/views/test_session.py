# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.historydb.entry import AuthEntry
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_all_url_params_match,
    check_url_contains_params,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.common import merge_dicts


TEST_UID = 1
TEST_HOST = '.yandex.ru'
TEST_USER_IP = '127.0.0.1'
TEST_USER_AGENT = 'curl'
TEST_YANDEXUID_COOKIE = 'cookie_yandexuid'
TEST_USER_COOKIES = 'yandexuid=%s' % TEST_YANDEXUID_COOKIE
TEST_REFERER = 'http://passportdev-python.yandex.ru/passport?mode=passport'

EXPECTED_SESSIONID_COOKIE = u'Session_id=2:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_SESSIONID_SECURE_COOKIE = u'sessionid2=2:sslsession; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
EXPECTED_AUTH_ID = '123:1422501443:126'
COOKIE_L_VALUE = 'VFV5DX94f0RRfXFTXVl5YH8GB2F6VlJ7XzNUTyYaIB1HBlpZBSd6QFkfOAJ7OgEACi5QFlIEGUM+KjlhRgRXZw==.1376993918.1002323.298859.ee75287c1d\
fd8b073375aee93158eb5b'
EXPECTED_L_COOKIE = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % COOKIE_L_VALUE

COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = u'ys=%s; Domain=.yandex.ru; Secure; Path=/' % COOKIE_YS_VALUE

EXPECTED_YANDEX_LOGIN_COOKIE = u'yandex_login=test; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/'

COOKIE_LAH_VALUE = 'OG5EOF8wU_bOAGhjXFp7YXkHAGB9UVFyB2IACGZedV4DWl8FWXF5BgJXYFVzYQVKV3kFVlpaU0p2f31iRkZRYQ.1473090908.1002323.1.2fe2104fff29aa69e867d7d1ea601470'
COOKIE_LAH_TEMPLATE = u'lah=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/'
EXPECTED_LAH_COOKIE = COOKIE_LAH_TEMPLATE % COOKIE_LAH_VALUE

EXPECTED_SESSGUARD_COOKIE = u'sessguard=1.sessguard; Domain=.passport-test.yandex.ru; Secure; HttpOnly; Path=/'

TEST_SESSIONID = '0:old-session'
TEST_USER_COOKIES_WITH_SESSION = TEST_USER_COOKIES + ';Session_id=%s' % TEST_SESSIONID

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE


def build_headers(cookie=TEST_USER_COOKIES):
    return mock_headers(
        host=TEST_HOST,
        user_ip=TEST_USER_IP,
        user_agent=TEST_USER_AGENT,
        cookie=cookie,
        referer=TEST_REFERER,
    )


class BaseTestSessionCreate(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'session': ['create']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID
            track.login = 'test'
            track.human_readable_login = 'test'
            track.machine_readable_login = 'test'
            track.language = 'ru'
            track.allow_authorization = True
            track.have_password = True
            track.is_password_passed = True
            track.auth_method = 'password'

        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        )
        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)

        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)

        self.patches = []
        cookies_patches = [
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
        self.patches += cookies_patches

        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.patches
        del self.track_manager
        del self._cookie_l_pack
        del self._cookie_yp_pack
        del self._cookie_ys_pack
        del self._cookie_lah_pack

    def build_auth_log_entry(self, status, uid, login, comment):
        return [
            ('login', login),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('status', status),
            ('uid', uid),
            ('useragent', TEST_USER_AGENT),
            ('yandexuid', TEST_YANDEXUID_COOKIE),
            ('comment', comment),
        ]

    def build_auth_log_entries(self, *args):
        entries = [
            ('login', 'test'),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('status', 'ses_create'),
            ('uid', '1'),
            ('useragent', TEST_USER_AGENT),
            ('yandexuid', TEST_YANDEXUID_COOKIE),
        ]
        entries += args
        return entries

    def session_create_request(self, data, headers):
        return self.env.client.post(
            '/1/session/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self):
        return {
            'track_id': self.track_id,
        }

    def assert_createsession_called(self, call_index=1, password_check_time_is_sent=True):
        sessionid_url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        expected_params = {
            'method': 'createsession',
            'lang': '1',
            'have_password': '1',
            'ver': '3',
            'uid': '1',
            'format': 'json',
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
        }

        if password_check_time_is_sent:
            expected_params['password_check_time'] = TimeNow()

        check_all_url_params_match(sessionid_url, expected_params)


@with_settings_hosts(
    PERMANENT_COOKIE_TTL=5,
    PASSPORT_SUBDOMAIN='passport-test',
)
class TestSessionCreate(BaseTestSessionCreate):

    def test_no_host_header(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        rv = self.session_create_request(
            self.query_params(),
            {},
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])

    def test_without_track(self):
        rv = self.session_create_request(
            {},
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                u'status': u'error',
                u'errors': [
                    {
                        u'field': u'track_id',
                        u'message': u'Missing value',
                        u'code': u'missingvalue',
                    },
                ],
            },
        )

    def test_incorrect_track_id(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        with self.track_manager.transaction(self.track_id).delete():
            pass

        rv = self.session_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])

    def test_with_authorization_not_allowed(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.allow_authorization = False

        rv = self.session_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Authorization is not allowed for this track',
                          u'code': u'authorizationnotallowed'}]})

    def test_with_already_created_session(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = 'abc123'
            track.sslsession = 'abc123'

        rv = self.session_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400)
        eq_(json.loads(rv.data),
            {u'status': u'error',
             u'errors': [{u'field': None,
                          u'message': u'Session already created for this account',
                          u'code': u'sessionalreadycreatederror'}]})

    def test_https_session_response_password_not_passed(self):
        '''
        Просим создать сессию по хттпс, но пароль не передавался.
        Секьюрная кука должна быть выписана.
        '''
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_password_passed = False

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        rv = self.session_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        expected_response = {
            'status': 'ok',
            'cookies': [
                EXPECTED_SESSIONID_COOKIE,
                EXPECTED_SESSIONID_SECURE_COOKIE,
                EXPECTED_YP_COOKIE,
                EXPECTED_YS_COOKIE,
                EXPECTED_L_COOKIE,
                EXPECTED_YANDEX_LOGIN_COOKIE,
                EXPECTED_LAH_COOKIE,
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
            'default_uid': TEST_UID,
            'session': {
                'domain': '.yandex.ru',
                'expires': 0,
                'secure': True,
                'http-only': True,
                'value': '2:session',
            },
            'sslsession': {
                'domain': '.yandex.ru',
                'expires': 1370874827,
                'secure': True,
                'http-only': True,
                'value': '2:sslsession',
            },
        }
        assert json.loads(rv.data) == expected_response
        self.assert_createsession_called(password_check_time_is_sent=False)
        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                ('comment', AuthEntry.format_comment_dict({
                    'aid': EXPECTED_AUTH_ID,
                    'ttl': 5,
                })),
            ),
        )
        track = self.track_manager.read(self.track_id)
        eq_(track.session, '2:session')
        eq_(track.sslsession, '2:sslsession')

    def test_https_session_response(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        rv = self.session_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        expected_response = {
            'status': 'ok',
            'cookies': [
                EXPECTED_SESSIONID_COOKIE,
                EXPECTED_SESSIONID_SECURE_COOKIE,
                EXPECTED_YP_COOKIE,
                EXPECTED_YS_COOKIE,
                EXPECTED_L_COOKIE,
                EXPECTED_YANDEX_LOGIN_COOKIE,
                EXPECTED_LAH_COOKIE,
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
            'default_uid': TEST_UID,
            'session': {
                'domain': '.yandex.ru',
                'expires': 0,
                'secure': True,
                'http-only': True,
                'value': '2:session',
            },
            'sslsession': {
                'domain': '.yandex.ru',
                'expires': 1370874827,
                'secure': True,
                'http-only': True,
                'value': '2:sslsession',
            },
        }
        assert json.loads(rv.data) == expected_response

        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                ('comment', AuthEntry.format_comment_dict({
                    'aid': EXPECTED_AUTH_ID,
                    'ttl': 5,
                })),
            ),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.session, '2:session')
        eq_(track.sslsession, '2:sslsession')

    def test_ok_with_sessguard(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )

        rv = self.session_create_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        expected_response = {
            'status': 'ok',
            'cookies': [
                EXPECTED_SESSIONID_COOKIE,
                EXPECTED_SESSIONID_SECURE_COOKIE,
                EXPECTED_SESSGUARD_COOKIE,
                EXPECTED_YP_COOKIE,
                EXPECTED_YS_COOKIE,
                EXPECTED_L_COOKIE,
                EXPECTED_YANDEX_LOGIN_COOKIE,
                EXPECTED_LAH_COOKIE,
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
            'default_uid': TEST_UID,
            'session': {
                'domain': '.yandex.ru',
                'expires': 0,
                'secure': True,
                'http-only': True,
                'value': '2:session',
            },
            'sslsession': {
                'domain': '.yandex.ru',
                'expires': 1370874827,
                'secure': True,
                'http-only': True,
                'value': '2:sslsession',
            },
            'sessguard': {
                'domain': '.passport-test.yandex.ru',
                'expires': 0,
                'secure': True,
                'http-only': True,
                'value': '1.sessguard',
            },
        }
        assert json.loads(rv.data) == expected_response

        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                ('comment', AuthEntry.format_comment_dict({
                    'aid': EXPECTED_AUTH_ID,
                    'ttl': 5,
                })),
            ),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.session, '2:session')
        eq_(track.sslsession, '2:sslsession')
        eq_(track.sessguard, '1.sessguard')

    def test_create_session_with_captcha_passed(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        rv = self.session_create_request(
            self.query_params(),
            build_headers(),
        )
        eq_(rv.status_code, 200)

        self.check_auth_log_entries(
            self.env.auth_handle_mock,
            self.build_auth_log_entries(
                ('comment', AuthEntry.format_comment_dict({
                    'aid': EXPECTED_AUTH_ID,
                    'cpt': 1,
                    'ttl': 5,
                })),
            ),
        )

        track = self.track_manager.read(self.track_id)
        eq_(track.session, '2:session')


@with_settings_hosts(
    PERMANENT_COOKIE_TTL=5,
    PASSPORT_SUBDOMAIN='passport-test',
)
class TestMultiSessionCreate(BaseTestSessionCreate):

    def setUp(self):
        super(TestMultiSessionCreate, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=EXPECTED_AUTH_ID,
                ip=TEST_USER_IP,
            ),
        )

    def get_expected_cookies(self, with_lah=True):
        result = [
            EXPECTED_SESSIONID_COOKIE,
            EXPECTED_SESSIONID_SECURE_COOKIE,
            EXPECTED_YP_COOKIE,
            EXPECTED_YS_COOKIE,
            EXPECTED_L_COOKIE,
            EXPECTED_YANDEX_LOGIN_COOKIE,
        ]
        if with_lah:
            result.append(EXPECTED_LAH_COOKIE)
        result.append(EXPECTED_MDA2_BEACON_COOKIE)
        return result

    def assert_response_ok(self, rv, with_lah=True):
        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        expected_response = {
            'status': 'ok',
            'cookies': self.get_expected_cookies(with_lah=with_lah),
            'default_uid': TEST_UID,
            'session': {
                'domain': '.yandex.ru',
                'expires': 0,
                'secure': True,
                'http-only': True,
                'value': '2:session',
            },
            'sslsession': {
                'domain': '.yandex.ru',
                'expires': 1370874827,
                'secure': True,
                'http-only': True,
                'value': '2:sslsession',
            },
        }
        assert json.loads(rv.data) == expected_response
        track = self.track_manager.read(self.track_id)
        eq_(track.session, '2:session')
        eq_(track.sslsession, '2:sslsession')

    def assert_auth_log_ok(self, *args):
        eq_(self.env.auth_handle_mock.call_count, len(args))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            args,
        )

    def assert_sessionid_called(self):
        sessionid_url = self.env.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            sessionid_url,
            {
                'method': 'sessionid',
                'multisession': 'yes',
                'sessionid': TEST_SESSIONID,
                'request_id': mock.ANY,
            },
        )

    def assert_editsession_called(self, call_index=1, password_check_time_is_sent=True):
        sessionid_url = self.env.blackbox._mock.request.call_args_list[call_index][0][1]
        expected_params = {
            'method': 'editsession',
            'sessionid': TEST_SESSIONID,
            'sslsessionid': '0:old-sslsession',
            'lang': '1',
            'have_password': '1',
            'uid': '1',
            'new_default': '1',
            'format': 'json',
            'host': '.yandex.ru',
            'keyspace': u'yandex.ru',
            'userip': TEST_USER_IP,
            'op': 'add',
            'create_time': TimeNow(),
            'guard_hosts': 'passport-test.yandex.ru',
            'request_id': mock.ANY,
            'get_login_id': 'yes',
        }
        if password_check_time_is_sent:
            expected_params['password_check_time'] = TimeNow()

        check_all_url_params_match(sessionid_url, expected_params)

    def assert_statbox_ok(self, uids_count='1', method='create', login='test', with_check_cookie=True, **kwargs):
        statbox_cookie_set_params = self.env.statbox.entry(
            'cookie_set',
            **{
                'track_id': self.track_id,
                'session_method': method,
                'uids_count': uids_count,
                'yandexuid': TEST_YANDEXUID_COOKIE,
                'ip': TEST_USER_IP,
                'input_login': login,
                'user_agent': TEST_USER_AGENT,
            }
        )

        statbox_cookie_set_params.update(kwargs)

        statbox_check_cookies_param = self.env.statbox.entry('check_cookies', host='.yandex.ru')
        lines = []
        if with_check_cookie:
            lines.append(statbox_check_cookies_param)
        lines.append(statbox_cookie_set_params)
        self.env.statbox.assert_has_written(lines)

    def test_ok_without_cookie(self):
        rv = self.session_create_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_response_ok(rv)
        self.assert_createsession_called()

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_create',
                uid='1',
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.assert_statbox_ok(with_check_cookie=False)

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
                ttl=5,
                allow_more_users=False,
            ),
        )
        resp = self.session_create_request(
            self.query_params(),
            build_headers(cookie=TEST_USER_COOKIES_WITH_SESSION),
        )
        eq_(resp.status_code, 400, [resp.status_code, resp.data])
        actual_response = json.loads(resp.data)
        eq_(
            actual_response,
            {
                u'status': u'error',
                u'errors': [
                    {
                        u'field': None,
                        u'message': u'No more users allowed',
                        u'code': u'sessionoverflowerror',
                    },
                ],
            },
        )

    def test_with_cookies__no_overflow_for_same_uid(self):
        """
        Пришли с мультикукой, на которую
        ЧЯ говорит, что в куку больше нельзя дописать пользователей,
        но мы пришли с пользователем, который уже есть в куке,
        значит ошибки нет.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1',
                login='test',
                ttl=5,
                allow_more_users=False,
            ),
        )
        resp = self.session_create_request(
            self.query_params(),
            build_headers(
                cookie='%s;sessionid2=%s' % (TEST_USER_COOKIES_WITH_SESSION, '0:old-sslsession'),
            ),
        )
        self.assert_response_ok(resp)
        self.assert_sessionid_called()
        self.assert_editsession_called(call_index=2)

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_update',
                uid='1',
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.assert_statbox_ok(method='edit', uids_count='1', old_session_uids='1')

    def test_ok_with_invalid_cookie(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        rv = self.session_create_request(
            self.query_params(),
            build_headers(cookie=TEST_USER_COOKIES_WITH_SESSION),
        )

        self.assert_response_ok(rv)
        self.assert_sessionid_called()
        self.assert_createsession_called(call_index=2)

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_create',
                uid='1',
                login='test',
                comment='aid=%s;ttl=5' % EXPECTED_AUTH_ID,
            ),
        )
        self.assert_statbox_ok()

    def test_ok_with_valid_short_cookie(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid='1234',
                login='other_login',
            ),
        )

        rv = self.session_create_request(
            self.query_params(),
            build_headers(
                cookie='%s;sessionid2=%s' % (TEST_USER_COOKIES_WITH_SESSION, '0:old-sslsession'),
            ),
        )

        self.assert_response_ok(rv, with_lah=False)
        self.assert_sessionid_called()
        self.assert_editsession_called(call_index=2)

        self.assert_auth_log_ok(
            self.build_auth_log_entry(
                status='ses_update',
                uid='1234',
                login='other_login',
                comment='aid=%s;ttl=0' % EXPECTED_AUTH_ID,
            ),
            self.build_auth_log_entry(
                status='ses_create',
                uid='1',
                login='test',
                comment='aid=%s;ttl=0' % EXPECTED_AUTH_ID,
            ),
        )
        self.assert_statbox_ok(method='edit', uids_count='2', old_session_uids='1234', ttl='0')


@with_settings_hosts(
    PASSPORT_SUBDOMAIN='passport-test',
)
class TestSessionCheck(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'session': ['check']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def session_check_request(self, data, headers):
        return self.env.client.post(
            '/1/session/check/?consumer=dev',
            data=data,
            headers=headers,
        )

    def query_params(self, **kwargs):
        base_params = {
            'track_id': self.track_id,
            'session': '2:session',
        }
        return merge_dicts(base_params, kwargs)

    def test_incorrect_track_id(self):
        with self.track_manager.transaction(self.track_id).delete():
            pass

        rv = self.session_check_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])

    def test_track_id_without_session(self):
        rv = self.session_check_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 400, [rv.status_code, rv.data])

    def test_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'

        rv = self.session_check_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': True,
                'session_has_users': True,
            },
        )

    def test_ok_empty_session(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = ''

        rv = self.session_check_request(
            self.query_params(session=''),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': True,
                'session_has_users': False,
            },
        )

    def test_extra_params(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'
            track.retpath = 'http://yandex.ru'
            track.fretpath = 'http://yandex.com'
            track.clean = 'yes'

        rv = self.session_check_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': True,
                'session_has_users': True,
                'retpath': 'http://yandex.ru',
                'fretpath': 'http://yandex.com',
                'clean': 'yes',
            },
        )

    def test_not_equal(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'

        rv = self.session_check_request(
            self.query_params(session='2:notsession'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': False,
            },
        )

    def test_not_equal_empty_session(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = ''

        rv = self.session_check_request(
            self.query_params(),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': False,
            },
        )

    def test_equal_session_and_sslsession_and_sessguard(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'
            track.sslsession = '2:sslsession'
            track.sessguard = '1.sessguard'

        rv = self.session_check_request(
            self.query_params(session='2:session', sslsession='2:sslsession', sessguard='1.sessguard'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': True,
                'session_has_users': True,
            },
        )

    def test_equal_session_and_sslsession_both_empty(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = ''
            track.sslsession = ''

        rv = self.session_check_request(
            self.query_params(session='', sslsession=''),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': True,
                'session_has_users': False,
            },
        )

    def test_equal_session_and_not_equal_sslsession(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'
            track.sslsession = '2:sslsession'

        rv = self.session_check_request(
            self.query_params(session='2:session', sslsession='2:ssl-not-equal'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': False,
            },
        )

    def test_equal_session_and_not_equal_empty_sslsession(self):
        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'
            track.sslsession = ''

        rv = self.session_check_request(
            self.query_params(session='2:session', sslsession='2:ssl-not-equal'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': False,
            },
        )

    def test_not_equal_session_and_equal_sslsession(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'
            track.sslsession = '2:sslsession'

        rv = self.session_check_request(
            self.query_params(session='2:session-not-equal', sslsession='2:sslsession'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': False,
            },
        )

    def test_not_equal_session_and_sslsession(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'
            track.sslsession = '2:sslsession'

        rv = self.session_check_request(
            self.query_params(session='2:session-not-equal', sslsession='2:ssl-not-equal'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': False,
            },
        )

    def test_equal_session_and_sslsession_and_not_equal_sessguard(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'
            track.sslsession = '2:sslsession'
            track.sessguard = '1.sessguard'

        rv = self.session_check_request(
            self.query_params(session='2:session', sslsession='2:sslsession', sessguard='1.sessguard-not-equal'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': False,
            },
        )

    def test_equal_session_and_sslsession_not_in_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.session = '2:session'

        rv = self.session_check_request(
            self.query_params(session='2:session', sslsession='2:sslsession'),
            build_headers(),
        )

        eq_(rv.status_code, 200, [rv.status_code, rv.data])
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'session_is_correct': True,
                'session_has_users': True,
            },
        )
