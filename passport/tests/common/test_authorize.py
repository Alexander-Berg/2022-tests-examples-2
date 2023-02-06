# -*- coding: utf-8 -*-
import base64
import datetime
from time import time
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.api.common.authorization import (
    authorize,
    build_cookie_i,
    build_cookie_ilahu,
    build_cookie_l,
    build_cookie_lah,
    build_cookie_mda2_beacon,
    build_cookie_mda2_domains,
    build_cookie_yandex_login,
    build_cookie_yandexuid,
    build_cookie_yp,
    build_cookie_ys,
    build_cookies_noauth,
    build_cookies_yx,
    build_non_auth_cookies,
    build_non_auth_cookies_from_track,
    is_oauth_token_created,
    is_session_created,
    update_cookie_mda2_domains,
)
from passport.backend.api.env import APIEnvironment
from passport.backend.api.exceptions import (
    InvalidIpError,
    SessionExpiredError,
)
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core import (
    authtypes,
    Undefined,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_createsession_response,
    blackbox_editsession_response,
    blackbox_lrandoms_response,
    FakeBlackbox,
)
from passport.backend.core.conf import settings
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
)
from passport.backend.core.cookies.cookie_lah import CookieLAHUnpackError
from passport.backend.core.cookies.cookie_lah.container import AuthHistoryContainer
from passport.backend.core.exceptions import WrongHostError
from passport.backend.core.logging_utils.faker.fake_tskv_logger import (
    CredentialsLoggerFaker,
    StatboxLoggerFaker,
)
from passport.backend.core.logging_utils.loggers.tskv import tskv_bool
from passport.backend.core.test.consts import TEST_SCHOLAR_LOGIN1
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.test_utils.utils import (
    check_url_contains_params,
    settings_context,
    with_settings,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.types.display_name import DisplayName
from passport.backend.utils.string import smart_text
import six
from six.moves.urllib.parse import quote


TEST_USER_AGENT_WITH_SAMESITE_SUPPORT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
TEST_RETPATH = 'https://test.yandex.ru/path'


class TestAuthorizeBase(BaseTestViews):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))

        self.blackbox = FakeBlackbox()
        self.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())

        self.auth_handle_mock = mock.Mock()
        self._auth_logger = mock.Mock()
        self._auth_logger.debug = self.auth_handle_mock

        self.statbox_faker = StatboxLoggerFaker()

        self.credentials_logger_faker = CredentialsLoggerFaker()

        self.patches = [
            self.fake_tvm_credentials_manager,
            mock.patch('passport.backend.api.common.authorization.auth_log', self._auth_logger),
            self.statbox_faker,
            self.credentials_logger_faker,
            self.blackbox,
        ]

        self.env = APIEnvironment(
            cookies={'yandexuid': 'yandexuid_value'},
            consumer_ip='87.250.235.4',
            user_ip='37.140.175.73',
            user_agent='UserAgent',
            host='passport.yandex.ru',
            referer='http://yandex.ru',
        )

        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        del self.patches
        del self.blackbox
        del self.auth_handle_mock
        del self._auth_logger
        del self.statbox_faker
        del self.credentials_logger_faker
        del self.fake_tvm_credentials_manager

    def check_statbox_log(self, session_method, captcha_passed=True, uids_count='1', old_session_uids=None,
                          **kwargs):
        expected_values = self.statbox_faker.entry(
            'cookie_set',
            **{
                'yandexuid': 'yandexuid_value',
                'ip': '37.140.175.73',
                'ip_country': 'ru',
                'user_agent': 'UserAgent',
                'captcha_passed': tskv_bool(captcha_passed),
                'session_method': session_method,
                'uids_count': uids_count,
                'authid': 'ID',
                'input_login': 'login',
            }
        )
        expected_values.update(**kwargs)
        if old_session_uids is not None:
            expected_values.update(old_session_uids=old_session_uids)

        self.statbox_faker.assert_has_written([expected_values])


@with_settings_hosts(IS_INTRANET=False)
class TestAuthorize(TestAuthorizeBase):

    def test_ses_create(self):
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid='ID'),
        )
        session, service_guard_container = authorize(
            self.env,
            1,
            'login',
            'ru',
            captcha_passed=True,
            have_password=True,
            host='passport.yandex.ru',
            auth_challenge='phone',
        )
        self.assertIsNone(service_guard_container)
        eq_(
            session,
            {
                'session':
                {
                    'domain': '.yandex.ru',
                    'expires': 0,
                    'value': '2:session',
                },
                'sslsession':
                {
                    'domain': '.yandex.ru',
                    'expires': 1370874827,
                    'secure': True,
                    'value': '2:sslsession',
                },
            },
        )

        self.check_auth_log_entries(
            self.auth_handle_mock,
            [
                ('login', 'login'),
                ('type', authtypes.AUTH_TYPE_WEB),
                ('status', 'ses_create'),
                ('uid', '1'),
                ('useragent', 'UserAgent'),
                ('yandexuid', 'yandexuid_value'),
                ('comment', 'aid=ID;chlng=phone;cpt=1;ttl=5'),
            ],
        )
        self.check_statbox_log('create')

        createsession_url = self.blackbox._mock.request.call_args_list[0][0][1]
        ok_('is_yastaff' not in createsession_url)
        ok_('is_betatester' not in createsession_url)
        ok_('social_id' not in createsession_url)
        ok_('yateam_auth' not in createsession_url)

    def test_bad_unicode_value(self):
        env = APIEnvironment(
            cookies={'yandexuid': '\xe9\x98\x00'},
            consumer_ip='87.250.235.4',
            user_ip='37.140.175.73',
            user_agent='555\xe9\x98\x00666',
            host='passport.yandex.ru',
            referer='http://yandex.ru',
        )
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid='ID'),
        )
        session, service_guard_container = authorize(
            env,
            1,
            'login',
            'ru',
            captcha_passed=True,
            have_password=True,
            host='passport.yandex.ru',
        )
        self.assertIsNone(service_guard_container)
        ok_(session)

        self.check_auth_log_entries(
            self.auth_handle_mock,
            [
                ('login', 'login'),
                ('type', authtypes.AUTH_TYPE_WEB),
                ('status', 'ses_create'),
                ('uid', '1'),
                ('useragent', '555\xe9\x98\x00666'),
                ('yandexuid', '\xe9\x98\x00'),
                ('comment', 'aid=ID;cpt=1;ttl=5'),
            ],
        )

    def test_ses_specific_flags(self):
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid='ID'),
        )
        authorize(
            self.env,
            1,
            'login',
            'ru',
            captcha_passed=True,
            have_password=True,
            host='passport.yandex.ru',
            is_yandexoid=True,
            is_betatester=True,
            social_id=11,
        )
        createsession_url = self.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            createsession_url,
            {
                'is_yastaff': '1',
                'is_betatester': '1',
                'social_id': '11',
            },
        )

    def test_ses_create_with_retpath(self):
        """
        Проверяем, что при наличие retpath в параметрах authorize, он пишется
        в statbox.
        """
        test_retpath = 'http://ya.ru'
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid='ID'),
        )

        authorize(
            self.env,
            1,
            'login',
            'ru',
            captcha_passed=True,
            have_password=True,
            host='passport.yandex.ru',
            retpath=test_retpath,
        )

        self.check_statbox_log(
            'create',
            retpath=test_retpath,
        )

    def test_ses_create_yateam_internal(self):
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid='ID'),
        )
        with settings_context(IS_INTRANET=True):
            authorize(
                self.env,
                1,
                'login',
                'ru',
                captcha_passed=True,
                have_password=True,
                host='passport.yandex.ru',
            )
        createsession_url = self.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            createsession_url,
            {
                'ttl': '5',
                'yateam_auth': '1',
            },
        )

    def test_ses_create_yateam_external(self):
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid='ID'),
        )
        with settings_context(IS_INTRANET=True):
            authorize(
                self.env,
                1,
                'login',
                'ru',
                captcha_passed=True,
                have_password=True,
                host='passport.yandex.ru',
                is_session_restricted=True,
            )
        createsession_url = self.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            createsession_url,
            {
                'ttl': '5',
                'yateam_auth': '0',
            },
        )

    def test_extra_service_sessguard(self):
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(
                authid='ID',
                sessguard_hosts=['passportdev.yandex.ru', 'test.yandex.ru'],
            ),
        )
        session, service_guard_container = authorize(
            self.env,
            1,
            'login',
            'ru',
            captcha_passed=True,
            have_password=True,
            host='passport.yandex.ru',
            auth_challenge='phone',
            need_extra_sessguard=True,
            retpath=TEST_RETPATH,
        )
        self.assertEqual(
            session,
            {
                'session': {
                    'domain': '.yandex.ru',
                    'expires': 0,
                    'value': '2:session',
                },
                'sslsession': {
                    'domain': '.yandex.ru',
                    'expires': 1370874827,
                    'secure': True,
                    'value': '2:sslsession',
                },
                'sessguard': {
                    'domain': '.passportdev.yandex.ru',
                    'expires': 0,
                    'value': '1.sessguard',
                },
            },
        )
        self.assertEqual(service_guard_container.data, {
            'cookies': ['sessguard=1.sessguard; Domain=.test.yandex.ru; Secure; HttpOnly; Path=/'],
            'retpath': TEST_RETPATH,
        })
        self.assertEqual(service_guard_container.container_type, 'sessguard_container')

    def test_extra_service_sessguard_but_retpath_without_host(self):
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(
                authid='ID',
                sessguard_hosts=['passportdev.yandex.ru', 'test.yandex.ru'],
            ),
        )
        session, service_guard_container = authorize(
            self.env,
            1,
            'login',
            'ru',
            captcha_passed=True,
            have_password=True,
            host='passport.yandex.ru',
            auth_challenge='phone',
            need_extra_sessguard=True,
            retpath='yandextaxi://',  # нет hostname, поэтому sessguard некуда установить
        )
        self.assertEqual(
            session,
            {
                'session': {
                    'domain': '.yandex.ru',
                    'expires': 0,
                    'value': '2:session',
                },
                'sslsession': {
                    'domain': '.yandex.ru',
                    'expires': 1370874827,
                    'secure': True,
                    'value': '2:sslsession',
                },
                'sessguard': {
                    'domain': '.passportdev.yandex.ru',
                    'expires': 0,
                    'value': '1.sessguard',
                },
            },
        )
        # дополнительный сесгард на retpath _не_ выписывается в этом тесте
        assert service_guard_container is None

    def test_scholar_session(self):
        self.blackbox.set_blackbox_response_value('createsession', blackbox_createsession_response(authid='ID'))

        authorize(
            self.env,
            1,
            'login',
            'ru',
            session_scope='scholar',
        )

        self.blackbox.requests[0].assert_query_contains({'is_scholar': '1'})


@with_settings_hosts(IS_INTRANET=False)
class TestAuthorizeWithMultiAuth(TestAuthorizeBase):

    def setUp(self):
        super(TestAuthorizeWithMultiAuth, self).setUp()
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid='ID'),
        )
        self.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(authid='ID'),
        )

    def call_authorize(self, multi_session_users=None, extend_session=False,
                       retpath=None, **kwargs):
        return authorize(
            self.env,
            1,
            'login',
            'ru',
            captcha_passed=True,
            have_password=True,
            host='passport.yandex.ru',
            old_session='old_session',
            extend_session=extend_session,
            multi_session_users=multi_session_users,
            retpath=retpath,
            **kwargs
        )

    def check_ses_updates_only(self, users, **kwargs):
        self.call_authorize(
            extend_session=True,
            multi_session_users=users,
            **kwargs
        )
        self.check_all_auth_log_records(
            self.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    'ses_update',
                    comment='aid=ID;cpt=1;ttl=5',
                ),
                self.build_auth_log_entries(
                    'ses_update',
                    uid='10',
                    login='login-10',
                    comment='aid=ID;ttl=5',
                ),
            ],
        )

    def build_auth_log_entries(self, status, comment=None, login='login', uid='1'):
        return {
            'login': login,
            'type': authtypes.AUTH_TYPE_WEB,
            'status': status,
            'uid': uid,
            'useragent': 'UserAgent',
            'yandexuid': 'yandexuid_value',
            'comment': comment,
        }.items()

    def test_ses_create(self):
        self.call_authorize()

        self.check_auth_log_entries(
            self.auth_handle_mock,
            self.build_auth_log_entries('ses_create', comment='aid=ID;cpt=1;ttl=5'),
        )
        self.check_statbox_log('create')

    def test_ses_create_with_retpath(self):
        """
        Проверяем, что при наличие retpath в параметрах authorize, он пишется
        в statbox.
        """
        test_retpath = 'http://ya.ru'

        self.call_authorize(retpath=test_retpath)

        self.check_statbox_log(
            'create',
            retpath=test_retpath,
        )

    def test_ses_create_and_updates(self):
        users = {
            10: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 10,
                'login': 'login-10',
                'auth': {
                    'secure': True,
                },
            },
        }
        self.call_authorize(
            extend_session=True,
            multi_session_users=users,
        )
        self.check_all_auth_log_records(
            self.auth_handle_mock,
            [
                self.build_auth_log_entries(
                    'ses_update',
                    uid='10',
                    login='login-10',
                    comment='aid=ID;ttl=5',
                ),
                self.build_auth_log_entries(
                    'ses_create',
                    comment='aid=ID;cpt=1;ttl=5',
                ),
            ],
        )
        self.check_statbox_log('edit', uids_count='2', old_session_uids='10')

    def test_ses_updates_only(self):
        users = {
            1: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 1,
                'login': 'login',
                'auth': {
                    'secure': True,
                },
            },
            10: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 10,
                'login': 'login-10',
                'auth': {
                    'secure': True,
                },
            },
        }
        self.check_ses_updates_only(users)

    def test_ses_updates_only_with_invalid_users(self):
        users = {
            1: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 1,
                'login': 'login',
                'auth': {
                    'secure': True,
                },
            },
            5: {
                'status': blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                'uid': 5,
                'login': 'login-5',
            },
            10: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 10,
                'login': 'login-10',
                'auth': {
                    'secure': True,
                },
            },
        }
        self.check_ses_updates_only(users)

    def test_editsession_fails_with_invalid_ip__error(self):
        blackbox_error_message = ' '.join([
            blackbox.BLACKBOX_ERROR_IP_NOT_YANDEX,
            'request_id=99720a91a7cd4ede.',
            'method=editsession.',
            'host=blackbox.yandex.net.',
            'hostname=pass-s10.sezam.yandex.net.',
            'current_time=2019-07-18T16:23:59.932581+0300',
        ])
        self.blackbox.set_blackbox_response_side_effect(
            'editsession',
            blackbox.BlackboxInvalidParamsError(blackbox_error_message),
        )

        users = {
            1: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 1,
                'login': 'login',
                'auth': {
                    'secure': True,
                },
            },
            10: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 10,
                'login': 'login-10',
                'auth': {
                    'secure': True,
                },
            },
        }
        with self.assertRaises(InvalidIpError):
            self.check_ses_updates_only(users)

    def test_createsession_fails_with_invalid_ip__error(self):
        blackbox_error_message = ' '.join([
            blackbox.BLACKBOX_ERROR_IP_NOT_YANDEX,
            'request_id=99720a91a7cd4ede.',
            'method=editsession.',
            'host=blackbox.yandex.net.',
            'hostname=pass-s10.sezam.yandex.net.',
            'current_time=2019-07-18T16:23:59.932581+0300',
        ])
        self.blackbox.set_blackbox_response_side_effect(
            'createsession',
            blackbox.BlackboxInvalidParamsError(blackbox_error_message),
        )

        with self.assertRaises(InvalidIpError):
            self.call_authorize()

    def test_editsession_fails_with_invalid_params__error(self):
        blackbox_error_message = ' '.join([
            blackbox.BLACKBOX_ERROR_SESSION_LOGGED_OUT,
            'request_id=99720a91a7cd4ede.',
            'method=editsession.',
            'host=blackbox.yandex.net.',
            'hostname=pass-s10.sezam.yandex.net.',
            'current_time=2019-07-18T16:23:59.932581+0300',
        ])
        self.blackbox.set_blackbox_response_side_effect(
            'editsession',
            blackbox.BlackboxInvalidParamsError(blackbox_error_message),
        )

        users = {
            1: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 1,
                'login': 'login',
                'auth': {
                    'secure': True,
                },
            },
            10: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 10,
                'login': 'login-10',
                'auth': {
                    'secure': True,
                },
            },
        }
        with self.assertRaises(SessionExpiredError):
            self.check_ses_updates_only(users)

    def test_ses_update_yateam_internal(self):
        users = {
            1: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 1,
                'login': 'login',
                'auth': {
                    'secure': True,
                },
            },
        }
        with settings_context(IS_INTRANET=True):
            self.call_authorize(
                extend_session=True,
                multi_session_users=users,
            )
        editsession_url = self.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            editsession_url,
            {
                'yateam_auth': '1',
            },
        )

    def test_ses_update_yateam_external(self):
        users = {
            1: {
                'status': blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                'uid': 1,
                'login': 'login',
                'auth': {
                    'secure': True,
                },
            },
        }
        with settings_context(IS_INTRANET=True):
            self.call_authorize(
                extend_session=True,
                multi_session_users=users,
                is_session_restricted=True,
            )
        editsession_url = self.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            editsession_url,
            {
                'yateam_auth': '0',
            },
        )


@with_settings_hosts(
    FORCE_ISSUE_PORTAL_COOKIE_TO_LITE_USERS=True,
)
class TestLiteUsersPortalCookie(TestAuthorizeBase):

    def setUp(self):
        super(TestLiteUsersPortalCookie, self).setUp()
        self.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(authid='ID'),
        )
        self.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(authid='ID'),
        )

    def test_authorize_lite_users_portal_cookie(self):
        authorize(
            self.env,
            1,
            'login',
            'ru',
            captcha_passed=True,
            have_password=True,
            host='passport.yandex.ru',
            is_lite=True,
            old_session='old_session',
        )
        createsession_url = self.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            createsession_url,
            {
                'is_lite': '0',
            },
        )


@with_settings
class TestBuildCookieL(TestAuthorizeBase):
    def setUp(self):
        super(TestBuildCookieL, self).setUp()
        self.env = mock_env(host='passport.yandex.ru')
        self._cookie_l_pack = mock.Mock(return_value='123')
        self._cookie_l_pack_patch = mock.patch.object(
            cookie_l.CookieL,
            'pack',
            self._cookie_l_pack,
        )
        self._cookie_l_pack_patch.start()

    def tearDown(self):
        self._cookie_l_pack_patch.stop()
        del self.env
        del self._cookie_l_pack
        del self._cookie_l_pack_patch
        super(TestBuildCookieL, self).tearDown()

    def test_ok(self):
        eq_(
            build_cookie_l(self.env, 3000062912, 'test'),
            'L=123; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/',
        )
        self._cookie_l_pack.assert_called_once_with(3000062912, 'test')

    @raises(WrongHostError)
    def test_wrong_host_error(self):
        self.env.host = 'passport.yandex.net'
        build_cookie_l(self.env, 123, 'test')


@with_settings(
    PASSPORT_SUBDOMAIN='passport-test',
)
class TestBuildCookieLAH(TestAuthorizeBase):
    def setUp(self):
        super(TestBuildCookieLAH, self).setUp()
        self.env = mock_env(host='passport-test.yandex.ru')
        self._cookie_lah_pack = mock.Mock(return_value='123')
        self._cookie_lah_pack_patch = mock.patch.object(
            cookie_lah.CookieLAH,
            'pack',
            self._cookie_lah_pack,
        )
        self._cookie_lah_pack_patch.start()

        self.container = AuthHistoryContainer()
        self.container.add(1, 2, 3)

    def tearDown(self):
        self._cookie_lah_pack_patch.stop()
        del self._cookie_lah_pack_patch
        del self._cookie_lah_pack
        del self.env
        super(TestBuildCookieLAH, self).tearDown()

    def test_ok(self):
        eq_(
            build_cookie_lah(self.env, self.container),
            'lah=123; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/',
        )
        self._cookie_lah_pack.assert_called_once_with(container=self.container)

    def test_empty_ok(self):
        self._cookie_lah_pack.return_value = ''
        eq_(
            build_cookie_lah(self.env, AuthHistoryContainer()),
            'lah=; Domain=.passport-test.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; HttpOnly; Path=/',
        )

    def test_samesite_ok(self):
        self.env.user_agent = TEST_USER_AGENT_WITH_SAMESITE_SUPPORT
        eq_(
            build_cookie_lah(self.env, self.container),
            'lah=123; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/; SameSite=None',
        )

    @raises(WrongHostError)
    def test_wrong_host_error(self):
        self.env.host = 'passport-test.yandex.net'
        build_cookie_lah(self.env, self.container)


@with_settings(
    PASSPORT_SUBDOMAIN='passport-test',
    COOKIE_ILAHU_MAX_AGE=30 * 24 * 3600,
)
class TestBuildCookieILAHU(unittest.TestCase):
    def setUp(self):
        self.env = mock_env(host='passport-test.yandex.ru')
        self.time_patch = mock.patch('time.time', return_value=1600000000)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        del self.time_patch
        del self.env

    def test_ok(self):
        eq_(
            build_cookie_ilahu(self.env, 123),
            'ilahu=123; Domain=.passport-test.yandex.ru; Expires=Tue, 13 Oct 2020 12:26:40 GMT; Secure; HttpOnly; Path=/',
        )

    def test_samesite_ok(self):
        self.env.user_agent = TEST_USER_AGENT_WITH_SAMESITE_SUPPORT
        eq_(
            build_cookie_ilahu(self.env, 123),
            'ilahu=123; Domain=.passport-test.yandex.ru; Expires=Tue, 13 Oct 2020 12:26:40 GMT; Secure; HttpOnly; Path=/; SameSite=None',
        )

    @raises(WrongHostError)
    def test_wrong_host_error(self):
        self.env.host = 'passport-test.yandex.net'
        build_cookie_ilahu(self.env, 123)


@with_settings(
    PASSPORT_SUBDOMAIN='passport-test',
    DOMAIN_KEYSPACES=[
        ('yandex.ru', 'yandex.ru'),
        ('ya.ru', 'ya.ru'),
        ('ya.com', 'ya.com'),
    ],
)
class TestBuildCookieMda2Domains(unittest.TestCase):
    def setUp(self):
        self.env = mock_env(host='passport-test.yandex.ru')

    def tearDown(self):
        del self.env

    def test_ok(self):
        eq_(
            build_cookie_mda2_domains(self.env, ['1', '2']),
            'mda2_domains=1,2; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    @raises(WrongHostError)
    def test_wrong_host_error(self):
        self.env.host = 'passport-test.yandex.net'
        build_cookie_mda2_domains(self.env, ['1', '2'])

    def test_update_existing_cookie(self):
        self.env.cookies = {'mda2_domains': 'ya.ru'}
        eq_(
            update_cookie_mda2_domains(self.env, 'my.ya.com'),
            'mda2_domains=ya.com,ya.ru; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_update_existing_empty_cookie(self):
        self.env.cookies = {'mda2_domains': ''}
        eq_(
            update_cookie_mda2_domains(self.env, 'ya.com'),
            'mda2_domains=ya.com; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )


@with_settings(
    PASSPORT_SUBDOMAIN='passport-test',
    DOMAIN_KEYSPACES=[
        ('yandex.ru', 'yandex.ru'),
        ('ya.ru', 'ya.ru'),
        ('ya.com', 'ya.com'),
    ],
)
class TestBuildCookieMda2Beacon(unittest.TestCase):
    def setUp(self):
        self.env = mock_env(host='passport-test.yandex.ru')
        self.time_patch = mock.patch('time.time', return_value=1551267793.21081)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        del self.time_patch
        del self.env

    def test_ok(self):
        eq_(
            build_cookie_mda2_beacon(self.env),
            'mda2_beacon=1551267793210; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )
        eq_(
            build_cookie_mda2_beacon(self.env, domain='.kinopoisk.ru'),
            'mda2_beacon=1551267793210; Domain=.kinopoisk.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )
        eq_(
            build_cookie_mda2_beacon(self.env, expires=0),
            'mda2_beacon=1551267793210; Domain=.passport-test.yandex.ru; Secure; Path=/',
        )
        eq_(
            build_cookie_mda2_beacon(self.env, expires=1551268000),
            'mda2_beacon=1551267793210; Domain=.passport-test.yandex.ru; Expires=Wed, 27 Feb 2019 11:46:40 GMT; Secure; Path=/',
        )
        eq_(
            build_cookie_mda2_beacon(self.env, expires=datetime.datetime(2020, 2, 27, 15, 47, 15)),
            'mda2_beacon=1551267793210; Domain=.passport-test.yandex.ru; Expires=Thu, 27 Feb 2020 15:47:15 GMT; Secure; Path=/',
        )

    def test_samesite_ok(self):
        self.env.user_agent = TEST_USER_AGENT_WITH_SAMESITE_SUPPORT
        eq_(
            build_cookie_mda2_beacon(self.env),
            'mda2_beacon=1551267793210; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/; SameSite=None',
        )

    @raises(WrongHostError)
    def test_wrong_host_error(self):
        self.env.host = 'passport-test.yandex.net'
        build_cookie_mda2_beacon(self.env)


@with_settings(
    COOKIE_I_MAX_AGE=10 * 365 * 24 * 3600,
)
class TestBuildCookieI(unittest.TestCase):
    def setUp(self):
        self.env = mock_env(host='passport-test.yandex.ru')
        self.time_patch = mock.patch('time.time', return_value=1600000000)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        del self.time_patch
        del self.env

    def test_ok(self):
        eq_(
            build_cookie_i(self.env, 123),
            'i=123; Domain=.yandex.ru; Expires=Wed, 11 Sep 2030 12:26:40 GMT; Secure; HttpOnly; Path=/',
        )

    def test_samesite_ok(self):
        self.env.user_agent = TEST_USER_AGENT_WITH_SAMESITE_SUPPORT
        eq_(
            build_cookie_i(self.env, 123),
            'i=123; Domain=.yandex.ru; Expires=Wed, 11 Sep 2030 12:26:40 GMT; Secure; HttpOnly; Path=/; SameSite=None',
        )

    @raises(WrongHostError)
    def test_wrong_host_error(self):
        self.env.host = 'passport-test.yandex.net'
        build_cookie_i(self.env, 123)


@with_settings(
    COOKIE_YANDEXUID_MAX_AGE=10 * 365 * 24 * 3600,
)
class TestBuildCookieYandexuid(unittest.TestCase):
    def setUp(self):
        self.env = mock_env(host='passport-test.yandex.ru')
        self.time_patch = mock.patch('time.time', return_value=1600000000)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        del self.time_patch
        del self.env

    def test_ok(self):
        eq_(
            build_cookie_yandexuid(self.env, 123),
            'yandexuid=123; Domain=.yandex.ru; Expires=Wed, 11 Sep 2030 12:26:40 GMT; Secure; Path=/',
        )

    def test_samesite_ok(self):
        self.env.user_agent = TEST_USER_AGENT_WITH_SAMESITE_SUPPORT
        eq_(
            build_cookie_yandexuid(self.env, 123),
            'yandexuid=123; Domain=.yandex.ru; Expires=Wed, 11 Sep 2030 12:26:40 GMT; Secure; Path=/; SameSite=None',
        )

    @raises(WrongHostError)
    def test_wrong_host_error(self):
        self.env.host = 'passport-test.yandex.net'
        build_cookie_yandexuid(self.env, 123)


@with_settings(
    COOKIE_YANDEX_LOGIN_MAX_AGE=2 * 3600,
)
class TestBuildCookieYandexLogin(unittest.TestCase):
    def setUp(self):
        self.env = mock_env(host='passport.yandex.ru')
        self.time_patch = mock.patch('time.time', return_value=1600000000)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        del self.time_patch
        del self.env

    def test_ok(self):
        eq_(
            build_cookie_yandex_login(self.env, 'test.test'),
            'yandex_login=test.test; Domain=.yandex.ru; Max-Age={}; Secure; Path=/'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
        )

    def test_pdd_ok(self):
        eq_(
            build_cookie_yandex_login(self.env, u'test@okna.ru'),
            'yandex_login=test@okna.ru; Domain=.yandex.ru; Max-Age={}; Secure; Path=/'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
        )

    def test_pdd_cyrillic_login_ok(self):
        eq_(
            build_cookie_yandex_login(self.env, u'test@окна.рф'),
            'yandex_login=test@%D0%BE%D0%BA%D0%BD%D0%B0.%D1%80%D1%84; Domain=.yandex.ru; Max-Age={}; Secure; Path=/'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
        )

    def test_pdd_long_login_ok(self):
        eq_(
            build_cookie_yandex_login(self.env, u'test-cyrillic@закодированный.домен'),
            (
                'yandex_login=test-cyrillic@%D0%B7%D0%B0%D0%BA%D0%BE%D0%B4%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%BD%D1%8B%D0%B9.%D0%B4%D0%BE%D0%BC%D0%B5%D0%BD; '
                'Domain=.yandex.ru; Max-Age={}; Secure; Path=/'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE)
            ),
        )

    def test_empty_value_ok(self):
        eq_(
            build_cookie_yandex_login(self.env, ''),
            'yandex_login=; Domain=.yandex.ru; Max-Age={}; Secure; Path=/'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
        )

    def test_none_value_ok(self):
        eq_(
            build_cookie_yandex_login(self.env, None),
            'yandex_login=; Domain=.yandex.ru; Max-Age={}; Secure; Path=/'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
        )

    def test_samesite_ok(self):
        self.env.user_agent = TEST_USER_AGENT_WITH_SAMESITE_SUPPORT
        eq_(
            build_cookie_yandex_login(self.env, 'test.test'),
            'yandex_login=test.test; Domain=.yandex.ru; Max-Age={}; Secure; Path=/; SameSite=None'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
        )

    def test_scholar(self):
        eq_(
            build_cookie_yandex_login(self.env, u'вовочка13'),
            'yandex_login=%D0%B2%D0%BE%D0%B2%D0%BE%D1%87%D0%BA%D0%B013; Domain=.yandex.ru; Max-Age={}; Secure; Path=/'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
        )


@with_settings(
    COOKIE_SESSIONID_NOAUTH_MAX_AGE=2 * 3600,
    COOKIE_YANDEX_LOGIN_MAX_AGE=3 * 3600,
)
class TestBuildCookiesNoauth(unittest.TestCase):
    def setUp(self):
        self.env = mock_env(host='passport-test.yandex.ru')
        self.time_patch = mock.patch('time.time', return_value=1600000000)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        del self.time_patch
        del self.env

    def test_ok(self):
        eq_(
            build_cookies_noauth(self.env),
            [
                'Session_id=noauth:1600000000; Domain=.yandex.ru; Max-Age={}; Secure; HttpOnly; Path=/'.format(settings.COOKIE_SESSIONID_NOAUTH_MAX_AGE),
                'yandex_login=; Domain=.yandex.ru; Max-Age={}; Secure; Path=/'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
            ],
        )

    def test_samesite_ok(self):
        self.env.user_agent = TEST_USER_AGENT_WITH_SAMESITE_SUPPORT
        eq_(
            build_cookies_noauth(self.env),
            [
                'Session_id=noauth:1600000000; Domain=.yandex.ru; Max-Age={}; Secure; HttpOnly; Path=/; SameSite=None'.format(settings.COOKIE_SESSIONID_NOAUTH_MAX_AGE),
                'yandex_login=; Domain=.yandex.ru; Max-Age={}; Secure; Path=/; SameSite=None'.format(settings.COOKIE_YANDEX_LOGIN_MAX_AGE),
            ],
        )

    @raises(WrongHostError)
    def test_wrong_host_error(self):
        self.env.host = 'passport-test.yandex.net'
        build_cookies_noauth(self.env)


@with_settings(
    COOKIE_YX_DISPLAY_NAME_FIELD='display_name',
    COOKIE_YP_DISPLAY_NAME_AGE=100,
    COOKIE_YX_DISPLAY_NAME_LENGTH=10,
)
class TestBuildCookieYx(unittest.TestCase):
    def setUp(self):
        self.env = mock_env(host='passport.yandex.com.tr')
        self.time_patch = mock.patch('time.time', return_value=100)
        self.time_patch.start()
        self.display_name = DisplayName(name='test')

    def tearDown(self):
        self.time_patch.stop()
        del self.time_patch
        del self.env

    @property
    def packed_display_name(self):
        return self.pack_display_name(self.display_name)

    def pack_display_name(self, display_name, max_length=10):
        value = smart_text(display_name)[:max_length]
        if six.PY2:
            encoder = base64.encodestring
        else:
            encoder = base64.encodebytes
        return quote(encoder(value.encode('utf-8')).replace(b'\n', b''))

    def test_ok(self):
        eq_(
            build_cookies_yx(self.env, self.display_name),
            [
                'yp=200.display_name.%s; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % self.packed_display_name,
                'ys=display_name.%s; Domain=.yandex.com.tr; Secure; Path=/' % self.packed_display_name,
            ],
        )

    def test_ys_only_ok(self):
        eq_(
            build_cookies_yx(self.env, self.display_name, need_yp=False),
            [
                'ys=display_name.%s; Domain=.yandex.com.tr; Secure; Path=/' % self.packed_display_name,
            ],
        )

    def test_yp_only_ok(self):
        eq_(
            build_cookies_yx(self.env, self.display_name, need_ys=False),
            [
                'yp=200.display_name.%s; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % self.packed_display_name,
            ],
        )

    def test_with_cookie_check_value_ok(self):

        eq_(
            build_cookies_yx(self.env, self.display_name, cookie_check_value=123),
            [
                'yp=200.display_name.%s; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % self.packed_display_name,
                'ys=display_name.%s#c_chck.123; Domain=.yandex.com.tr; Secure; Path=/' % self.packed_display_name,
            ],
        )

    def test_unicode_ok(self):
        self.display_name.name = u'Страшные символы @#$!'
        eq_(
            build_cookies_yx(self.env, self.display_name),
            [
                'yp=200.display_name.%s; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % self.packed_display_name,
                'ys=display_name.%s; Domain=.yandex.com.tr; Secure; Path=/' % self.packed_display_name,
            ],
        )

    def test_pdd_long_display_name_ok(self):
        expected_cookie_yx_display_name_length = 50
        with settings_context(
            COOKIE_YX_DISPLAY_NAME_FIELD='display_name',
            COOKIE_YP_DISPLAY_NAME_AGE=100,
            COOKIE_YX_DISPLAY_NAME_LENGTH=expected_cookie_yx_display_name_length,
        ):
            self.display_name.name = 20 * u'б' + u'test-cyrillic@закодированный.домен'
            packed_display_name = self.pack_display_name(
                self.display_name,
                max_length=expected_cookie_yx_display_name_length,
            )
            eq_(
                build_cookies_yx(self.env, self.display_name),
                [
                    'yp=200.display_name.%s; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % packed_display_name,
                    'ys=display_name.%s; Domain=.yandex.com.tr; Secure; Path=/' % packed_display_name,
                ],
            )

    def test_delete_display_name(self):
        eq_(
            build_cookies_yx(self.env, None),
            [
                'yp=; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
                'ys=; Domain=.yandex.com.tr; Secure; Path=/',
            ],
        )

    def test_with_old_cookies_values(self):
        env = mock_env(
            host='passport.yandex.com.tr',
            cookies={
                'yp': '500.foo.bar',
                'ys': 'foo.bar',
            },
        )
        eq_(
            build_cookies_yx(env, self.display_name),
            [
                'yp=500.foo.bar#200.display_name.%s; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % self.packed_display_name,
                'ys=foo.bar#display_name.%s; Domain=.yandex.com.tr; Secure; Path=/' % self.packed_display_name,
            ],
        )

    def test_with_old_cookies_values_delete_display_name(self):
        env = mock_env(
            host='passport.yandex.com.tr',
            cookies={
                'yp': '500.foo.bar#200.display_name.bmtjaGVybg%3D%3D',
                'ys': 'foo.bar#display_name.bmtjaGVybg%3D%3D',
            },
        )
        eq_(
            build_cookies_yx(env, display_name=None),
            [
                'yp=500.foo.bar; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
                'ys=foo.bar; Domain=.yandex.com.tr; Secure; Path=/',
            ],
        )

    def test_with_old_cookies_values_display_name_not_changed(self):
        env = mock_env(
            host='passport.yandex.com.tr',
            cookies={
                'yp': '500.foo.bar#200.display_name.bmtjaGVybg%3D%3D',
                'ys': 'foo.bar#display_name.bmtjaGVybg%3D%3D',
            },
        )
        eq_(
            build_cookies_yx(env, display_name=Undefined),
            [
                'yp=500.foo.bar#200.display_name.bmtjaGVybg%3D%3D; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
                'ys=foo.bar#display_name.bmtjaGVybg%3D%3D; Domain=.yandex.com.tr; Secure; Path=/',
            ],
        )


@with_settings(
    COOKIE_YX_DISPLAY_NAME_FIELD='display_name',
    COOKIE_YP_DISPLAY_NAME_AGE=100,
    COOKIE_YP_MULTIBROWSER_FIELD='multi',
    COOKIE_YP_MULTIBROWSER_AGE=101,
    COOKIE_YP_2FA_FIELD='2fa',
    COOKIE_YP_2FA_AGE=102,
    COOKIE_YP_SP_FIELD='sp',
    COOKIE_YP_SP_AGE=103,
)
class TestBuildCookieYp(unittest.TestCase):
    def make_env(self, cookies=None):
        base_cookies = {'yandexuid': 'yandexuid_value'}
        if cookies:
            base_cookies.update(cookies)
        return APIEnvironment(
            cookies=base_cookies,
            consumer_ip='87.250.235.4',
            user_ip='37.140.175.73',
            user_agent='UserAgent',
            host='passport.yandex.ru',
            referer='http://yandex.ru',
        )

    def setUp(self):
        self.time_patch = mock.patch('time.time', return_value=100)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()
        del self.time_patch

    def test_ok(self):
        eq_(
            build_cookie_yp(
                self.make_env(),
                '',
                u'привет',
                '.yandex.com.tr',
            ),
            'yp=200.display_name.%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_with_old(self):
        eq_(
            build_cookie_yp(
                self.make_env(),
                '400.key.value#600.display_name.Bob#100.foo.bar',
                u'Joe',
                '.yandex.com.tr',
            ),
            'yp=400.key.value#200.display_name.Joe#100.foo.bar; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_with_old_delete_display_name(self):
        eq_(
            build_cookie_yp(
                self.make_env(),
                '400.key.value#600.display_name.Bob#100.foo.bar',
                None,
                '.yandex.com.tr',
            ),
            'yp=400.key.value#100.foo.bar; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_set_multibrowser_field(self):
        eq_(
            build_cookie_yp(
                self.make_env(),
                '1.foo.bar',
                'Petr',
                '.yandex.com.tr',
                is_multibrowser=True,
            ),
            'yp=1.foo.bar#200.display_name.Petr#201.multi.1; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_set_multibrowser_field_already_set(self):
        eq_(
            build_cookie_yp(
                self.make_env(),
                '1.foo.bar#600.multi.1',
                'Petr',
                '.yandex.com.tr',
                is_multibrowser=True,
            ),
            'yp=1.foo.bar#600.multi.1#200.display_name.Petr; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_2fa_on_true_no_2fa_in_cookie(self):
        """
        В куке yp не было знания о 2fa, пришел аккаунт со включенным 2fa.
        Взведем флажек в куке.
        """
        eq_(
            build_cookie_yp(
                self.make_env(),
                '1.foo.bar',
                'Petr',
                '.yandex.com.tr',
                is_2fa_enabled_yp=True,
            ),
            'yp=1.foo.bar#200.display_name.Petr#202.2fa.1; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_2fa_on_false_2fa_on_in_cookie(self):
        """
        В куке yp было знание о 2fa, пришел аккаунт с выключенным 2fa.
        Уберем флажок из куки.
        """
        eq_(
            build_cookie_yp(
                self.make_env(),
                '1.foo.bar#202.2fa.1',
                'Petr',
                '.yandex.com.tr',
                is_2fa_enabled_yp=False,
            ),
            'yp=1.foo.bar#200.display_name.Petr; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_2fa_on_true_2fa_on_in_cookie(self):
        """
        В куке yp было знание о 2fa, пришел аккаунт с включенным 2fa.
        Удостоверимся, что флажек остался.
        """
        eq_(
            build_cookie_yp(
                self.make_env(),
                '1.foo.bar#202.2fa.1',
                'Petr',
                '.yandex.com.tr',
                is_2fa_enabled_yp=True,
            ),
            'yp=1.foo.bar#202.2fa.1#200.display_name.Petr; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_2fa_on_true_2fa_on_in_cookie_current_unknown(self):
        """
        В куке yp было знание о 2fa, пришел аккаунт с неизвестным знанием про 2fa.
        Удостоверимся, что флажек остался.
        """
        eq_(
            build_cookie_yp(
                self.make_env(),
                '1.foo.bar#202.2fa.1',
                'Petr',
                '.yandex.com.tr',
                is_2fa_enabled_yp=None,
            ),
            'yp=1.foo.bar#202.2fa.1#200.display_name.Petr; Domain=.yandex.com.tr; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_with_child_ok(self):
        eq_(
            build_cookie_yp(
                self.make_env(),
                '400.key.value',
                None,
                '.yandex.com',
                is_child=True,
            ),
            'yp=400.key.value#203.sp.family:2; Domain=.yandex.com; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_change_family_in_sp_with_child_ok(self):
        eq_(
            build_cookie_yp(
                self.make_env(),
                '400.key.value#203.sp.family:0',
                None,
                '.yandex.com',
                is_child=True,
            ),
            'yp=400.key.value#203.sp.family:2; Domain=.yandex.com; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )

    def test_change_family_in_sp_save_order_with_child_ok(self):
        eq_(
            build_cookie_yp(
                self.make_env(),
                '400.key.value#203.sp.bhtt:0:family:0:brl:0',
                None,
                '.yandex.com',
                is_child=True,
            ),
            'yp=400.key.value#203.sp.bhtt:0:family:2:brl:0; Domain=.yandex.com; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/',
        )


@with_settings(
    COOKIE_YX_DISPLAY_NAME_FIELD='display_name',
)
class TestBuildCookieYs(unittest.TestCase):
    def make_env(self, cookies=None):
        base_cookies = {'yandexuid': 'yandexuid_value'}
        if cookies:
            base_cookies.update(cookies)
        return APIEnvironment(
            cookies=base_cookies,
            consumer_ip='87.250.235.4',
            user_ip='37.140.175.73',
            user_agent='UserAgent',
            host='passport.yandex.ru',
            referer='http://yandex.ru',
        )

    def test_ok(self):
        eq_(
            build_cookie_ys(
                self.make_env(),
                '',
                u'привет',
                '.yandex.com.tr',
            ),
            'ys=display_name.%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82; Domain=.yandex.com.tr; Secure; Path=/',
        )

    def test_with_old_ok(self):
        eq_(
            build_cookie_ys(
                self.make_env(),
                'key.value#display_name.Bob#foo.bar',
                u'Joe',
                '.yandex.com.tr',
            ),
            'ys=key.value#display_name.Joe#foo.bar; Domain=.yandex.com.tr; Secure; Path=/',
        )

    def test_with_old_delete_display_name(self):
        eq_(
            build_cookie_ys(
                self.make_env(),
                'key.value#display_name.Bob#foo.bar',
                None,
                '.yandex.com.tr',
            ),
            'ys=key.value#foo.bar; Domain=.yandex.com.tr; Secure; Path=/',
        )


@with_settings()
class TestBuildNonAuthCookies(TestAuthorizeBase):

    def make_env(self, cookies=None):
        base_cookies = {'yandexuid': 'yandexuid_value'}
        if cookies:
            base_cookies.update(cookies)
        return APIEnvironment(
            cookies=base_cookies,
            consumer_ip='87.250.235.4',
            user_ip='37.140.175.73',
            user_agent='UserAgent',
            host='passport.yandex.ru',
            referer='http://yandex.ru',
        )

    def setUp(self):
        super(TestBuildNonAuthCookies, self).setUp()
        self.env = self.make_env()

        self.expected_uid = 1
        self.another_uid = 2
        self.expected_path = '/'

        self.cookie_l_unpack = mock.Mock()
        self.cookie_lah_unpack = mock.Mock()
        self.build_cookie_l_mock = mock.Mock(return_value='cookie_l')
        self.build_cookie_lah_mock = mock.Mock(return_value='cookie_lah')
        self.build_cookie_ilahu_mock = mock.Mock(return_value='cookie_ilahu')
        self.build_cookies_yx_mock = mock.Mock(return_value=['ys', 'yp'])

        self.extra_patches = [
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                self.build_cookie_l_mock,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_lah',
                self.build_cookie_lah_mock,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_ilahu',
                self.build_cookie_ilahu_mock,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookies_yx',
                self.build_cookies_yx_mock,
            ),
            mock.patch.object(
                cookie_l.CookieL,
                'unpack',
                self.cookie_l_unpack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'unpack',
                self.cookie_lah_unpack,
            ),
        ]
        for patch in self.extra_patches:
            patch.start()

        self.setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.extra_patches):
            patch.stop()
        del self.extra_patches
        del self.expected_path
        del self.env
        del self.cookie_l_unpack
        del self.cookie_lah_unpack
        del self.build_cookie_l_mock
        del self.build_cookie_lah_mock
        del self.build_cookie_ilahu_mock
        del self.build_cookies_yx_mock
        super(TestBuildNonAuthCookies, self).tearDown()

    def setup_statbox_templates(self):
        self.statbox_faker.bind_entry(
            'multibrowser_update',
            uid='1',
            user_agent='UserAgent',
            mode='any_auth',
            action='multibrowser_update',
            yandexuid='yandexuid_value',
            ip='37.140.175.73',
            old_multibrowser='0',
            new_multibrowser='1',
        )

    def test_human_readable_login_passed_to_cookie_l(self):
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
        )
        self.build_cookie_l_mock.assert_called_once_with(
            self.env,
            self.expected_uid,
            'human_readable_login',
            path=self.expected_path,
        )

    def test_is_multibrowser_field_not_set_empty_cookie_l(self):
        """
        Кука Л пуста - не выставляем мультиброузерность.
        """
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
        )
        self.build_cookies_yx_mock.assert_called_once_with(
            self.env,
            'dispname',
            path=self.expected_path,
            is_multibrowser=False,
            is_2fa_enabled_yp=None,
            is_child=False,
        )

    def test_is_multibrowser_field_not_set_old_login_matched_human_readable_login(self):
        """
        Логин в куке Л совпадает с human_readable_login.
        Не выставляем мультиброузерность.
        """
        self.cookie_l_unpack.return_value = {
            'uid': self.expected_uid,
            'login': 'human_readable_login',
        }
        self.env = self.make_env(cookies={'L': 'l_cookie'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
        )
        self.build_cookies_yx_mock.assert_called_once_with(
            self.env,
            'dispname',
            path=self.expected_path,
            is_multibrowser=False,
            is_2fa_enabled_yp=None,
            is_child=False,
        )
        self.cookie_l_unpack.assert_called_once_with('l_cookie')

    def test_is_multibrowser_field_not_set_old_login_matched_machine_readable_login(self):
        """
        Логин в куке Л совпадает с machine_readable_login.
        Не выставляем мультиброузерность.
        """
        self.cookie_l_unpack.return_value = {
            'uid': self.expected_uid,
            'login': 'machine_readable_login',
        }
        self.env = self.make_env(cookies={'L': 'l_cookie'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
        )
        self.build_cookies_yx_mock.assert_called_once_with(
            self.env,
            'dispname',
            path=self.expected_path,
            is_multibrowser=False,
            is_2fa_enabled_yp=None,
            is_child=False,
        )
        self.cookie_l_unpack.assert_called_once_with('l_cookie')

    def test_is_multibrowser_field_not_set_error_occured(self):
        """
        В куке Л пришла какая-то ерунда. Проглотили ошибку.
        Не выставляем мультиброузерность.
        """
        self.cookie_l_unpack.side_effect = cookie_l.CookieLUnpackError
        self.env = self.make_env(cookies={'L': 'l_cookie'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
        )
        self.build_cookies_yx_mock.assert_called_once_with(
            self.env,
            'dispname',
            path=self.expected_path,
            is_multibrowser=False,
            is_2fa_enabled_yp=None,
            is_child=False,
        )
        self.cookie_l_unpack.assert_called_once_with('l_cookie')

    def test_is_multibrowser_field_set(self):
        """
        Логин в куке Л не совпал ни с human_readable_login, ни с machine_readable_login
        Выставляем мультиброузерность.
        """
        self.cookie_l_unpack.return_value = {
            'uid': self.expected_uid,
            'login': 'old_login',
        }
        self.env = self.make_env(cookies={'L': 'l_cookie'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
        )
        self.build_cookies_yx_mock.assert_called_once_with(
            self.env,
            'dispname',
            path=self.expected_path,
            is_multibrowser=True,
            is_2fa_enabled_yp=None,
            is_child=False,
        )
        self.cookie_l_unpack.assert_called_once_with('l_cookie')
        self.statbox_faker.assert_has_written([
            self.statbox_faker.entry('multibrowser_update'),
        ])

    def test_old_multibrowser_bad_field_in_yp(self):
        """
        Логин в куке Л не совпадает с human_readable_login.
        В куке yp уже было выставленна мультибраузерность причем в виде произвольной строчки.
        Проверим что запишем все правильно, не упадем, странную строчку не запишем в лог.
        """
        self.cookie_l_unpack.return_value = {
            'uid': self.expected_uid,
            'login': 'old_login',
        }
        self.env = self.make_env(
            cookies={
                'L': 'l_cookie',
                'yp': '1.multib.lala',
            },
        )
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
        )
        self.build_cookies_yx_mock.assert_called_once_with(
            self.env,
            'dispname',
            path=self.expected_path,
            is_multibrowser=True,
            is_2fa_enabled_yp=None,
            is_child=False,
        )
        self.cookie_l_unpack.assert_called_once_with('l_cookie')
        self.statbox_faker.assert_has_written([
            self.statbox_faker.entry('multibrowser_update'),
        ])

    def test_update_cookie_lah__add_user(self):
        container = AuthHistoryContainer()
        container.add(self.another_uid, 100500, 2)
        self.cookie_lah_unpack.return_value = container

        self.env = self.make_env(cookies={'lah': 'lah_cookie'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
            auth_method='password',
            input_login=u'input_login@окна.рф',
        )
        self.cookie_lah_unpack.assert_called_once_with('lah_cookie')
        new_container = self.build_cookie_lah_mock.call_args[0][1]
        eq_(len(new_container), 2)
        eq_(new_container[0].uid, self.another_uid)
        eq_(new_container[1].uid, self.expected_uid)
        eq_(new_container[1].timestamp, TimeNow())
        eq_(new_container[1].method, 1)
        eq_(new_container[1].input_login, u'input_login@окна.рф')

    def test_update_cookie_lah__add_user_without_method(self):
        container = AuthHistoryContainer()
        container.add(self.another_uid, 100500, 2)
        self.cookie_lah_unpack.return_value = container

        self.env = self.make_env(cookies={'lah': 'lah_cookie'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
            auth_method=None,
        )
        self.cookie_lah_unpack.assert_called_once_with('lah_cookie')
        new_container = self.build_cookie_lah_mock.call_args[0][1]
        eq_(len(new_container), 2)
        eq_(new_container[0].uid, self.another_uid)
        eq_(new_container[1].uid, self.expected_uid)
        eq_(new_container[1].timestamp, TimeNow())
        eq_(new_container[1].method, 0)
        ok_(not new_container[1].input_login)

    def test_update_cookie_lah__update_user_without_method(self):
        container = AuthHistoryContainer()
        container.add(self.expected_uid, 100500, 2, 'input_login')
        self.cookie_lah_unpack.return_value = container

        self.env = self.make_env(cookies={'lah': 'lah_cookie'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
            auth_method=None,
        )
        self.cookie_lah_unpack.assert_called_once_with('lah_cookie')
        new_container = self.build_cookie_lah_mock.call_args[0][1]
        eq_(len(new_container), 1)
        eq_(new_container[0].uid, self.expected_uid)
        eq_(new_container[0].timestamp, TimeNow())
        eq_(new_container[0].method, 2)
        eq_(new_container[0].input_login, 'input_login')

    def test_cookie_lah_parse_error(self):
        self.cookie_lah_unpack.side_effect = CookieLAHUnpackError

        self.env = self.make_env(cookies={'lah': 'lah_cookie'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
            auth_method='password',
        )
        self.cookie_lah_unpack.assert_called_once_with('lah_cookie')
        new_container = self.build_cookie_lah_mock.call_args[0][1]
        eq_(len(new_container), 1)
        eq_(new_container[0].uid, self.expected_uid)
        eq_(new_container[0].timestamp, TimeNow())
        eq_(new_container[0].method, 1)

    def test_update_cookie_lah__add_scholar(self):
        container = AuthHistoryContainer()
        container.add(self.another_uid, 100500, 2)
        self.cookie_lah_unpack.return_value = container

        self.env = self.make_env(cookies={'lah': 'lah_cookie'})

        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            display_name='dispname',
            auth_method='password',
            input_login=TEST_SCHOLAR_LOGIN1,
        )

        self.cookie_lah_unpack.assert_called_once_with('lah_cookie')
        new_container = self.build_cookie_lah_mock.call_args[0][1]
        assert len(new_container) == 1
        assert new_container[0].uid == self.another_uid

    def test_update_cookie_ilahu__ok(self):
        self.env = self.make_env(cookies={'ilahu': '100'})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            ignore_lah_for=100,
        )
        self.build_cookie_ilahu_mock.assert_called_once_with(self.env, TimeNow(offset=100), path='/')

    def test_update_cookie_ilahu__no_need_to_update(self):
        future_timestamp = int(time() + 3600)
        self.env = self.make_env(cookies={'ilahu': str(future_timestamp)})
        build_non_auth_cookies(
            self.env,
            self.expected_uid,
            'human_readable_login',
            'machine_readable_login',
            self.expected_path,
            ignore_lah_for=100,
        )
        self.build_cookie_ilahu_mock.assert_called_once_with(self.env, future_timestamp, path='/')


@with_settings_hosts()
class TestBuildNonAuthCookiesFromTrack(unittest.TestCase):

    def setUp(self):
        super(TestBuildNonAuthCookiesFromTrack, self).setUp()

        self.request_env = APIEnvironment(host='passport.yandex.ru')

        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.use_non_auth_cookies_from_track = True

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager
        super(TestBuildNonAuthCookiesFromTrack, self).tearDown()

    def test_ok(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.cookie_l_value = 'l'
            track.cookie_my_value = 'my'
            track.cookie_yp_value = 'yp'
            track.cookie_ys_value = 'ys'
            track.cookie_yandex_login_value = 'yandex_login'
            track.cookie_yandex_gid_value = 'yandex_gid'

        cookies = build_non_auth_cookies_from_track(
            self.request_env,
            track,
        )
        eq_(len(cookies), 6)

    def test_ok_for_empty_cookies(self):
        track = self.track_manager.read(self.track_id)
        cookies = build_non_auth_cookies_from_track(
            self.request_env,
            track,
        )
        eq_(cookies, [])


@with_settings_hosts(
    TOKEN_REISSUE_INTERVAL=10,
)
class TestIsOauthTokenCreated(unittest.TestCase):

    def setUp(self):
        super(TestIsOauthTokenCreated, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track = self.track_manager.read(self.track_id)

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track
        del self.track_manager
        super(TestIsOauthTokenCreated, self).tearDown()

    def test_not_created(self):
        ok_(not is_oauth_token_created(self.track))

    def test_created_recently(self):
        self.track.oauth_token_created_at = time() - 1
        ok_(not is_oauth_token_created(self.track))

    def test_created_long_ago(self):
        self.track.oauth_token_created_at = time() - 60
        ok_(is_oauth_token_created(self.track))

    def test_fallback(self):
        self.track.is_oauth_token_created = True
        ok_(is_oauth_token_created(self.track))


@with_settings_hosts(
    TOKEN_REISSUE_INTERVAL=10,
)
class TestIsSessionCreated(unittest.TestCase):
    def setUp(self):
        super(TestIsSessionCreated, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track = self.track_manager.read(self.track_id)

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track
        del self.track_manager
        super(TestIsSessionCreated, self).tearDown()

    def test_not_created(self):
        ok_(not is_session_created(self.track))

    def test_created_recently(self):
        self.track.session_created_at = time() - 1
        ok_(not is_session_created(self.track))

    def test_created_long_ago(self):
        self.track.session_created_at = time() - 60
        ok_(is_session_created(self.track))

    def test_fallback(self):
        self.track.session = 'session'
        ok_(is_session_created(self.track))

    def test_custom_created_recently(self):
        self.track.session_created_at = time() - 60
        ok_(not is_session_created(self.track, 300))

    def test_custom_created_long_ago(self):
        self.track.session_created_at = time() - 500
        ok_(is_session_created(self.track, 300))
