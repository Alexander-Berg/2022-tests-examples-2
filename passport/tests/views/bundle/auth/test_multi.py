# -*- coding: utf-8 -*-
import mock
from nose.tools import eq_
from passport.backend.api.common.authorization import encode_udn
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    EXPECTED_ILAHU_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    TEST_AUTH_ID,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_OLD_AUTH_ID,
    TEST_ORIGIN,
    TEST_OTHER_LOGIN,
    TEST_PDD_UID,
    TEST_REFERER,
    TEST_RETPATH,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.core import Undefined
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders.blackbox import (
    BLACKBOX_EDITSESSION_OP_DELETE,
    BLACKBOX_EDITSESSION_OP_SELECT,
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BlackboxInvalidParamsError,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_WRONG_GUARD_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_editsession_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_append_invalid_session,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.historydb.statuses import (
    SESSION_KILL,
    SESSION_UPDATE,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_all_url_params_match,
    check_url_contains_params,
    with_settings_hosts,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.display_name import DisplayName
from passport.backend.utils.string import smart_str
from six.moves.urllib.parse import (
    quote,
    quote_plus,
)


EXPECTED_L_COOKIE = 'L_COOKIE'
EXPECTED_SESSIONID_COOKIE = 'Session_id=2:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_SESSIONID2_COOKIE = 'sessionid2=2:sslsession; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'

EXPECTED_EMPTY_SESSIONID_COOKIE = 'Session_id=; Domain=.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_EMPTY_SESSIONID2_COOKIE = 'sessionid2=; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'

EXPECTED_YP_COOKIE = 'yp=200.udn.test; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/'
TEST_TUTBY_DOMAIN = 'tut.by'
TEST_TUTBY_RETPATH = 'https://profile.tut.by/logout/?retpath=%s'

MDA2_BEACON_VALUE = '1551270703270'
EXPECTED_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Secure; Path=/' % MDA2_BEACON_VALUE
EXPECTED_LONG_MDA2_BEACON_COOKIE = u'mda2_beacon=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % MDA2_BEACON_VALUE


def build_yandex_login_cookie(login):
    return 'yandex_login=%s; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/' % login


def pack_display_name(display_name):
    return quote(encode_udn(display_name))


def build_ys_cookie(display_name):
    udn = pack_display_name(display_name) if display_name else ''
    if udn:
        udn = 'udn.' + udn
    return 'ys=%s; Domain=.yandex.ru; Secure; Path=/' % udn


def build_headers(**kwargs):
    base = dict(
        host=TEST_HOST,
        user_ip=TEST_IP,
        cookie='Session_id=0:old-session; yandexuid=%s;' % TEST_YANDEXUID_COOKIE,
        user_agent=TEST_USER_AGENT,
    )
    base.update(kwargs)
    return mock_headers(**base)


EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE = build_yandex_login_cookie('')
EXPECTED_YANDEX_LOGIN_COOKIE = build_yandex_login_cookie(TEST_LOGIN)

user_display_name = DisplayName(name='user_display_name')
user_display_name_data = {
    'name': 'user_display_name',
    'default_avatar': '',
}


class MultiAuthTestCaseBase(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'auth_multi': ['base']}))

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ttl=3,
                display_name=user_display_name_data,
            ),
        )
        lrandoms_response = blackbox_lrandoms_response()
        self.env.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)

        self._build_cookie_yp = mock.Mock(return_value=EXPECTED_YP_COOKIE)
        self._build_cookie_lah = mock.Mock(return_value=EXPECTED_LAH_COOKIE)
        self._build_cookie_ilahu = mock.Mock(return_value=EXPECTED_ILAHU_COOKIE)
        self.setup_statbox_templates()
        self.patches = []

        self.patches.extend([
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                mock.Mock(return_value=EXPECTED_L_COOKIE),
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_yp',
                self._build_cookie_yp,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_lah',
                self._build_cookie_lah,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_ilahu',
                self._build_cookie_ilahu,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ])

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)
        self.patches.append(self.track_id_generator)

        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches
        del self._build_cookie_yp
        del self._build_cookie_lah
        del self._build_cookie_ilahu

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'cookie_edit',
            authid=TEST_OLD_AUTH_ID,
            uid=str(TEST_UID),
            action='cookie_edit',
            yandexuid=TEST_YANDEXUID_COOKIE,
        )

    def get_account_info(self, login=TEST_LOGIN, uid=TEST_UID, display_name_data=None, display_login=None):
        return {
            'uid': uid,
            'login': login,
            'display_name': display_name_data or {'name': '', 'default_avatar': ''},
            'display_login': login if display_login is None else display_login,
        }

    def get_method_name(self):
        raise NotImplementedError  # pragma: no cover

    def make_request(self, headers=None, **kwargs):
        data = dict(uid=TEST_UID)
        data.update(kwargs)
        headers = build_headers() if headers is None else headers

        return self.env.client.post(
            '/1/bundle/auth/%s/?consumer=dev' % self.get_method_name(),
            data=data,
            headers=headers,
        )

    def assert_build_cookie_yp_called_with(self, display_name, is_2fa_enabled_yp=None, is_child=Undefined):
        udn = encode_udn(display_name)
        self._build_cookie_yp.assert_called_with(mock.ANY, '', udn, '.yandex.ru', '/', False, is_2fa_enabled_yp, is_child)

    def get_expected_cookies(self, sessionid_cookie=None, sessionid2_cookie=None, ys_cookie=None,
                             yandex_login_cookie=None, skip_l_cookie=False, skip_lah_cookie=False,
                             mda2_beacon_cookie=None):
        cookies = [
            sessionid_cookie or EXPECTED_SESSIONID_COOKIE,
            EXPECTED_YP_COOKIE,
        ]
        if not skip_l_cookie:
            cookies.append(EXPECTED_L_COOKIE)
        if not skip_lah_cookie:
            cookies.append(EXPECTED_LAH_COOKIE)

        cookies.append(sessionid2_cookie or EXPECTED_SESSIONID_SECURE_COOKIE)
        cookies.append(mda2_beacon_cookie or EXPECTED_MDA2_BEACON_COOKIE)

        if ys_cookie:
            cookies.append(ys_cookie)
        if yandex_login_cookie:
            cookies.append(yandex_login_cookie)

        return sorted(cookies)

    def assert_ok_response(self, response, accounts=None, cookies=None, logged_out_uids=None, default_uid=None):
        kwargs = dict(
            cookies=cookies,
            accounts=accounts,
            track_id=self.track_id,
            ignore_order_for=['cookies'],
        )
        if logged_out_uids:
            kwargs.update(logged_out_uids=logged_out_uids)
        if default_uid:
            kwargs.update(default_uid=default_uid)
        super(MultiAuthTestCaseBase, self).assert_ok_response(response, **kwargs)

    def assert_track_ok(self, session=None, retpath=None):
        track = self.track_manager.read(self.track_id)
        eq_(track.session, session)
        eq_(track.retpath, retpath)

    def assert_statbox_log(self, template='cookie_edit', **kwargs):
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('check_cookies'),
                self.env.statbox.entry(template, **kwargs),
            ],
        )

    def build_auth_log_entries(self, status, **kwargs):
        entries = {
            'type': authtypes.AUTH_TYPE_WEB,
            'status': status,
            'uid': str(TEST_UID),
            'useragent': TEST_USER_AGENT,
            'yandexuid': TEST_YANDEXUID_COOKIE,
            'comment': 'aid=%s;ttl=3' % TEST_AUTH_ID,
            'ip_from': TEST_IP,
            'client_name': 'passport',
        }
        entries.update(kwargs)
        return entries.items()

    def assert_auth_log(self, expected_records):
        eq_(self.env.auth_handle_mock.call_count, len(expected_records))
        self.check_all_auth_log_records(
            self.env.auth_handle_mock,
            expected_records,
        )

    def check_no_uid_error(self):
        rv = self.make_request(uid='')
        self.assert_error_response(rv, error_codes=['uid.empty'])

    def check_blackbox_invalid_params_error(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'editsession',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['sessionid.no_uid'])

    def check_invalid_sessionid_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['sessionid.invalid'])

    def check_wrong_guard_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_WRONG_GUARD_STATUS),
        )
        rv = self.make_request()
        self.assert_error_response(rv, error_codes=['sessguard.invalid'])


@with_settings_hosts(
    COOKIE_YP_DISPLAY_NAME_AGE=100,
    PDD_DOMAIN_RETPATH_WRAPPER_MAP={TEST_TUTBY_DOMAIN: TEST_TUTBY_RETPATH},
    PASSPORT_SUBDOMAIN='passport-test',
)
class LogoutViewTestCase(MultiAuthTestCaseBase):

    def setUp(self):
        super(LogoutViewTestCase, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='',
                session_value='',
                ssl_session_value='',
            ),
        )

    def setup_statbox_templates(self):
        super(LogoutViewTestCase, self).setup_statbox_templates()
        self.env.statbox.bind_entry(
            'cookie_edit',
            user_agent=TEST_USER_AGENT,
            **{
                'mode': 'logout',
                'global': '0',
            }
        )
        self.env.statbox.bind_entry(
            'cookie_remove',
            _inherit_from='cookie_edit',
            action='cookie_remove',
            authid=TEST_OLD_AUTH_ID,
            uid=str(TEST_UID),
            yandexuid=TEST_YANDEXUID_COOKIE,
        )

    def get_method_name(self):
        return 'logout'

    def get_expected_cookies(self, **kwargs):
        return super(LogoutViewTestCase, self).get_expected_cookies(**kwargs) + [EXPECTED_ILAHU_COOKIE]

    def assert_no_recods_in_auth_log(self, **kwargs):
        eq_(self.env.auth_handle_mock.call_count, 0)

    def test_no_uid_error(self):
        self.check_no_uid_error()

    def test_blackbox_invalid_params_error(self):
        self.check_blackbox_invalid_params_error()
        self.assert_no_recods_in_auth_log()

    def test_invalid_sessionid_error(self):
        self.check_invalid_sessionid_error()
        self.assert_no_recods_in_auth_log()

    def test_wrong_guard_error(self):
        self.check_wrong_guard_error()
        self.assert_no_recods_in_auth_log()

    def test_new_default_not_in_sessionid_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
            ),
        )
        rv = self.make_request(default_uid=12345)
        self.assert_error_response(rv, error_codes=['sessionid.no_uid'])
        self.assert_no_recods_in_auth_log()

    def test_ok(self):
        """
        В куке один пользователь, выходим им.
        """
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            accounts=[],
            logged_out_uids=[TEST_UID],
            cookies=self.get_expected_cookies(
                sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                mda2_beacon_cookie=EXPECTED_LONG_MDA2_BEACON_COOKIE,
                ys_cookie=build_ys_cookie(''),
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
        )
        self.assert_build_cookie_yp_called_with(None, is_child=False)
        self.assert_track_ok(session='')
        sessionid_url = self.env.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            sessionid_url,
            {
                'allow_scholar': 'yes',
                'multisession': 'yes',
                'sessionid': '0:old-session',
            },
        )

        edit_session_url = self.env.blackbox._mock.request.call_args_list[1][0][1]
        check_all_url_params_match(
            edit_session_url,
            {
                'uid': '1',
                'format': 'json',
                'sessionid': '0:old-session',
                'host': 'passport-test.yandex.ru',
                'userip': '3.3.3.3',
                'method': 'editsession',
                'op': BLACKBOX_EDITSESSION_OP_DELETE,
                'create_time': TimeNow(),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )
        self.assert_statbox_log('cookie_remove')
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
            ],
        )

    def test_ok_write_ua_referer_origin_retpath_to_statbox(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.retpath = TEST_RETPATH
            track.origin = TEST_ORIGIN

        rv = self.make_request(
            track_id=self.track_id,
            headers=build_headers(
                referer=TEST_REFERER,
            ),
        )

        self.assert_ok_response(
            rv,
            accounts=[],
            logged_out_uids=[TEST_UID],
            cookies=self.get_expected_cookies(
                sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                mda2_beacon_cookie=EXPECTED_LONG_MDA2_BEACON_COOKIE,
                ys_cookie=build_ys_cookie(''),
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
        )
        self.assert_statbox_log(
            template='cookie_remove',
            **{
                'retpath': TEST_RETPATH,
                'origin': TEST_ORIGIN,
                'referer': TEST_REFERER,
            }
        )

    def test_ok_with_https(self):
        """
        Производим выход по хттпс.
        """
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='',
                session_value='',
                ssl_session_value='',
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ttl=3,
                display_name=user_display_name_data,
            ),
        )
        rv = self.make_request(
            headers=build_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )
        self.assert_ok_response(
            rv,
            accounts=[],
            logged_out_uids=[TEST_UID],
            cookies=self.get_expected_cookies(
                sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                ys_cookie=build_ys_cookie(''),
                yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                mda2_beacon_cookie=EXPECTED_LONG_MDA2_BEACON_COOKIE,
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
        )
        self.assert_build_cookie_yp_called_with(None, is_child=False)
        sessionid_url = self.env.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            sessionid_url,
            {
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
                'multisession': 'yes',
            },
        )

        edit_session_url = self.env.blackbox._mock.request.call_args_list[1][0][1]
        check_all_url_params_match(
            edit_session_url,
            {
                'uid': '1',
                'format': 'json',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
                'host': 'passport-test.yandex.ru',
                'userip': '3.3.3.3',
                'method': 'editsession',
                'op': BLACKBOX_EDITSESSION_OP_DELETE,
                'create_time': TimeNow(),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )
        self.assert_statbox_log('cookie_remove')
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
            ],
        )

    def test_ok_with_multiple_accounts(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    ttl=3,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=123,
                login='login123',
                display_name=user_display_name_data,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(authid=TEST_AUTH_ID, default_uid='123'),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            accounts=[self.get_account_info(uid=123, login='login123', display_name_data=user_display_name_data)],
            logged_out_uids=[TEST_UID],
            default_uid=123,
            cookies=self.get_expected_cookies(
                ys_cookie=build_ys_cookie(user_display_name),
                yandex_login_cookie=build_yandex_login_cookie('login123'),
            ),
        )
        self.assert_build_cookie_yp_called_with(user_display_name)
        self.assert_statbox_log()
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    SESSION_UPDATE,
                    uid='123',
                    login='login123',
                    comment='aid=%s;ttl=3' % TEST_AUTH_ID,
                ),
            ],
        )

    def test_ok_for_non_existing_in_session_account_error(self):
        """Пытаемся разлогинить несуществующий в сессии аккаунт"""
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    ttl=3,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=123,
                login='login123',
                display_name=user_display_name_data,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(authid=TEST_AUTH_ID, default_uid=TEST_UID),
        )
        rv = self.make_request(uid=111)
        self.assert_error_response(rv, error_codes=['sessionid.no_uid'])

    def test_ok_for_deleted_account_error(self):
        """Пытаемся разлогинить удалённый аккаунт"""
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.retpath = TEST_RETPATH

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ttl=3,
                authid=TEST_OLD_AUTH_ID,
                default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS,
                item_id=TEST_UID,
                uid=None,
                aliases=None,
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='',
                session_value='',
                ssl_session_value='',
            ),
        )
        rv = self.make_request(track_id=self.track_id)
        self.assert_ok_response(
            rv,
            accounts=[],
            logged_out_uids=[TEST_UID],
            cookies=self.get_expected_cookies(
                sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                ys_cookie=build_ys_cookie(''),
                yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                mda2_beacon_cookie=EXPECTED_LONG_MDA2_BEACON_COOKIE,
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
        )

    def test_ok_with_switch_to_2fa_account(self):
        """
        В сессии 2 пользователя, разлогиниваем первого, у второго включен 2fa.
        Удостоверимся, что передаем флаг о включенности 2фа в куку yp.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    ttl=3,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=123,
                login='login123',
                display_name=user_display_name_data,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(authid=TEST_AUTH_ID, default_uid='123'),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            accounts=[self.get_account_info(uid=123, login='login123', display_name_data=user_display_name_data)],
            logged_out_uids=[TEST_UID],
            default_uid=123,
            cookies=self.get_expected_cookies(
                ys_cookie=build_ys_cookie(user_display_name),
                yandex_login_cookie=build_yandex_login_cookie('login123'),
            ),
        )
        self.assert_build_cookie_yp_called_with(user_display_name, is_2fa_enabled_yp=True)

    def test_ok_with_sessional_cookie(self):
        """
        Выходим из одного из аккаунтов короткоживущей сессии
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    ttl=0,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=123,
                login='login123',
                display_name=user_display_name_data,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(authid=TEST_AUTH_ID, default_uid='123'),
        )

        rv = self.make_request()

        self.assert_ok_response(
            rv,
            accounts=[self.get_account_info(uid=123, login='login123', display_name_data=user_display_name_data)],
            logged_out_uids=[TEST_UID],
            default_uid=123,
            cookies=self.get_expected_cookies(
                ys_cookie=build_ys_cookie(user_display_name),
                yandex_login_cookie=build_yandex_login_cookie('login123'),
                skip_lah_cookie=True,
            ),
        )

    def test_tutby_retpath_ok(self):
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.retpath = TEST_RETPATH

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    authid=TEST_OLD_AUTH_ID,
                    ttl=3,
                    domain=TEST_TUTBY_DOMAIN,
                    uid=TEST_PDD_UID,
                    login='test@%s' % TEST_TUTBY_DOMAIN,
                    aliases={
                        'pdd': 'test@%s' % TEST_TUTBY_DOMAIN,
                    },
                ),
                uid=123,
                login=TEST_OTHER_LOGIN,
                display_name=user_display_name_data,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(authid=TEST_AUTH_ID, default_uid='123'),
        )

        rv = self.make_request(uid=TEST_PDD_UID, track_id=self.track_id)

        self.assert_ok_response(
            rv,
            accounts=[
                self.get_account_info(
                    uid=123,
                    login=TEST_OTHER_LOGIN,
                    display_name_data=user_display_name_data,
                ),
            ],
            logged_out_uids=[TEST_PDD_UID],
            default_uid=123,
            cookies=self.get_expected_cookies(
                ys_cookie=build_ys_cookie(user_display_name),
                yandex_login_cookie=build_yandex_login_cookie(TEST_OTHER_LOGIN),
            ),
        )
        self.assert_build_cookie_yp_called_with(user_display_name)
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    uid=str(TEST_PDD_UID),
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    SESSION_UPDATE,
                    uid='123',
                    login=TEST_OTHER_LOGIN,
                    comment='aid=%s;ttl=3' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_track_ok(
            session='2:session',
            retpath=TEST_TUTBY_RETPATH % quote_plus(TEST_RETPATH),
        )

    def test_tutby_retpath_non_ascii_ok(self):
        test_retpath = u'http://test.yandex.ru?text=кириллица'
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.retpath = test_retpath

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    authid=TEST_OLD_AUTH_ID,
                    ttl=3,
                    domain=TEST_TUTBY_DOMAIN,
                    uid=TEST_PDD_UID,
                    login='test@%s' % TEST_TUTBY_DOMAIN,
                    aliases={
                        'pdd': 'test@%s' % TEST_TUTBY_DOMAIN,
                    },
                ),
                uid=123,
                login=TEST_OTHER_LOGIN,
                display_name=user_display_name_data,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(authid=TEST_AUTH_ID, default_uid='123'),
        )

        rv = self.make_request(uid=TEST_PDD_UID, track_id=self.track_id)

        self.assert_ok_response(
            rv,
            accounts=[
                self.get_account_info(
                    uid=123,
                    login=TEST_OTHER_LOGIN,
                    display_name_data=user_display_name_data,
                ),
            ],
            logged_out_uids=[TEST_PDD_UID],
            default_uid=123,
            cookies=self.get_expected_cookies(
                ys_cookie=build_ys_cookie(user_display_name),
                yandex_login_cookie=build_yandex_login_cookie(TEST_OTHER_LOGIN),
            ),
        )
        self.assert_build_cookie_yp_called_with(user_display_name)
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    uid=str(TEST_PDD_UID),
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    SESSION_UPDATE,
                    uid='123',
                    login=TEST_OTHER_LOGIN,
                    comment='aid=%s;ttl=3' % TEST_AUTH_ID,
                ),
            ],
        )
        self.assert_track_ok(
            session='2:session',
            retpath=TEST_TUTBY_RETPATH % quote_plus(smart_str(test_retpath)),
        )


@with_settings_hosts(
    COOKIE_YP_DISPLAY_NAME_AGE=100,
    PASSPORT_SUBDOMAIN='passport-test',
)
class ChangeDefaultViewTestCase(MultiAuthTestCaseBase):
    def setUp(self):
        super(ChangeDefaultViewTestCase, self).setUp()
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ttl=3,
                    uid=123,
                    login='login123',
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=user_display_name_data,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid=TEST_UID,
            ),
        )

    def get_method_name(self):
        return 'change_default'

    def test_no_uid_error(self):
        self.check_no_uid_error()

    def test_blackbox_invalid_params_error(self):
        self.check_blackbox_invalid_params_error()

    def test_invalid_sessionid_error(self):
        self.check_invalid_sessionid_error()

    def test_wrong_guard_error(self):
        self.check_wrong_guard_error()

    def test_uid_not_in_sessionid_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                display_name=user_display_name_data,
            ),
        )
        rv = self.make_request(uid=12345)
        self.assert_error_response(rv, error_codes=['sessionid.no_uid'])

    def test_change_to_same_uid_error(self):
        """Пытаемся сменить дефолта на самого себя же"""
        rv = self.make_request(uid=123)
        self.assert_error_response(rv, error_codes=['action.not_required'])

    def test_ok(self):
        """
        Производим смену дефолта.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ttl=3,
                    uid=123,
                    login='login123',
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=user_display_name_data,
                attributes={
                    'account.is_child': '1',
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid=TEST_UID,
            ),
        )
        rv = self.make_request(
            headers=build_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )
        self.assert_ok_response(
            rv,
            accounts=[
                self.get_account_info(display_name_data=user_display_name_data),
                self.get_account_info(uid=123, login='login123'),
            ],
            cookies=self.get_expected_cookies(
                yandex_login_cookie=build_yandex_login_cookie(TEST_LOGIN),
                ys_cookie=build_ys_cookie(user_display_name),
            ),
            default_uid=TEST_UID,
        )
        self.assert_build_cookie_yp_called_with(user_display_name, is_child=True)
        self.assert_track_ok(session='2:session')
        sessionid_url = self.env.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            sessionid_url,
            {
                'allow_scholar': 'yes',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
                'multisession': 'yes',
            },
        )
        edit_session_url = self.env.blackbox._mock.request.call_args_list[1][0][1]
        check_all_url_params_match(
            edit_session_url,
            {
                'uid': str(TEST_UID),
                'format': 'json',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
                'host': 'passport-test.yandex.ru',
                'userip': '3.3.3.3',
                'method': 'editsession',
                'op': BLACKBOX_EDITSESSION_OP_SELECT,
                'create_time': TimeNow(),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )
        self.assert_statbox_log(mode='change_default')
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_UPDATE,
                    comment='aid=%s;ttl=3' % TEST_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    SESSION_UPDATE,
                    uid='123',
                    login='login123',
                    comment='aid=%s;ttl=3' % TEST_AUTH_ID,
                ),
            ],
        )

    def test_ok_change_to_invalid_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_invalid_session(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                ),
                item_id=2,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='2',
            ),
        )
        rv = self.make_request(uid='2')
        self.assert_ok_response(
            rv,
            accounts=[
                self.get_account_info(),
            ],
            cookies=self.get_expected_cookies(
                ys_cookie=build_ys_cookie(''),
                yandex_login_cookie=build_yandex_login_cookie(''),
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
            default_uid=2,
        )
        self.assert_build_cookie_yp_called_with(None, is_child=False)
        sessionid_url = self.env.blackbox._mock.request.call_args_list[0][0][1]
        check_url_contains_params(
            sessionid_url,
            {
                'sessionid': '0:old-session',
                'multisession': 'yes',
            },
        )
        edit_session_url = self.env.blackbox._mock.request.call_args_list[1][0][1]
        check_all_url_params_match(
            edit_session_url,
            {
                'uid': '2',
                'format': 'json',
                'sessionid': '0:old-session',
                'host': 'passport-test.yandex.ru',
                'userip': '3.3.3.3',
                'method': 'editsession',
                'op': BLACKBOX_EDITSESSION_OP_SELECT,
                'create_time': TimeNow(),
                'guard_hosts': 'passport-test.yandex.ru',
                'request_id': mock.ANY,
                'get_login_id': 'yes',
            },
        )
        self.assert_statbox_log(
            mode='change_default',
            uid='2',
            authid=TEST_AUTH_ID,
        )
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_UPDATE,
                    comment='aid=%s;ttl=0' % TEST_AUTH_ID,
                ),
            ],
        )

    def test_ok_with_switch_to_2fa_account(self):
        """
        В сессии 2 пользователя, у недефолтного включен 2fa. Переключаемся на него.
        Удостоверимся, что передаем флаг о включенности 2фа в куку yp.
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ttl=3,
                    uid=123,
                    login='login123',
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=user_display_name_data,
                attributes={
                    'account.2fa_on': '1',
                },
            ),
        )

        rv = self.make_request(
            headers=build_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )
        self.assert_ok_response(
            rv,
            cookies=self.get_expected_cookies(
                yandex_login_cookie=build_yandex_login_cookie(TEST_LOGIN),
                ys_cookie=build_ys_cookie(user_display_name),
            ),
            default_uid=TEST_UID,
            accounts=[
                self.get_account_info(display_name_data=user_display_name_data),
                self.get_account_info(uid=123, login='login123'),
            ],
        )
        self.assert_build_cookie_yp_called_with(user_display_name, is_2fa_enabled_yp=True)

    def test_ok_with_sessional_cookie(self):
        """
        Производим смену дефолта в короткоживущей сессии
        """
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ttl=0,
                    uid=123,
                    login='login123',
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=TEST_UID,
                login=TEST_LOGIN,
                display_name=user_display_name_data,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid=TEST_UID,
            ),
        )
        rv = self.make_request(
            headers=build_headers(
                cookie='Session_id=0:old-session; sessionid2=0:old-sslsession; yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            ),
        )
        self.assert_ok_response(
            rv,
            accounts=[
                self.get_account_info(display_name_data=user_display_name_data),
                self.get_account_info(uid=123, login='login123'),
            ],
            cookies=self.get_expected_cookies(
                yandex_login_cookie=build_yandex_login_cookie(TEST_LOGIN),
                ys_cookie=build_ys_cookie(user_display_name),
                skip_lah_cookie=True,
            ),
            default_uid=TEST_UID,
        )
