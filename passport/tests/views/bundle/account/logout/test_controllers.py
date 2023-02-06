# -*- coding: utf-8 -*-
from datetime import datetime

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.authorization import encode_udn
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.password.base_test_data import (
    EXPECTED_YP_COOKIE,
    TEST_AUTH_ID,
    TEST_OLD_AUTH_ID,
    TEST_ORIGIN,
    TEST_REFERER,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONNECTION_ID_VALUE,
    TEST_COOKIE_ILAHU,
    TEST_COOKIE_L,
    TEST_COOKIE_LAH,
    TEST_DISPLAY_NAME,
    TEST_DISPLAY_NAME_DATA,
    TEST_FUID01_VALUE,
    TEST_HOST,
    TEST_L_VALUE,
    TEST_LOGIN,
    TEST_MY_VALUE,
    TEST_OLD_SESSIONID_VALUE,
    TEST_OLD_SSL_SESSIONID_VALUE,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_PDD_UID,
    TEST_RETPATH,
    TEST_SESSGUARD_VALUE,
    TEST_SESSIONID_VALUE,
    TEST_SSL_SESSIONID_VALUE,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_IP,
    TEST_YANDEX_GID_VALUE,
    TEST_YANDEXUID_VALUE,
    TEST_YP_VALUE,
    TEST_YS_VALUE,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_SESSIONID_DISABLED_STATUS,
    BLACKBOX_SESSIONID_EXPIRED_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
)
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
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.types.display_name import DisplayName
from passport.backend.utils.string import smart_str
from six.moves.urllib.parse import (
    quote,
    quote_plus,
)


ACCOUNT_LOGOUT_GRANT = 'account.logout'
TEST_DEFAULT_RETPATH = 'https://www.yandex.ru'

EXPECTED_SESSIONID_COOKIE = 'Session_id=2:session; Domain=.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_SESSIONID2_COOKIE = 'sessionid2=2:sslsession; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
EXPECTED_SESSGUARD_COOKIE = 'sessguard=%s; Domain=.passport-test.yandex.ru; Secure; HttpOnly; Path=/' % TEST_SESSGUARD_VALUE

EXPECTED_EMPTY_SESSIONID_COOKIE = 'Session_id=; Domain=.yandex.ru; Secure; HttpOnly; Path=/'
EXPECTED_EMPTY_SESSIONID2_COOKIE = 'sessionid2=; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
EXPECTED_EMPTY_SESSGUARD_COOKIE = 'sessguard=; Domain=.passport-test.yandex.ru; Secure; HttpOnly; Path=/'

TEST_USER_COOKIES = 'Session_id=%s; sessionid2=%s; yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s; ys=%s; yp=%s; sessguard=%s' % (
    TEST_SESSIONID_VALUE,
    TEST_SSL_SESSIONID_VALUE,
    TEST_YANDEXUID_VALUE,
    TEST_YANDEX_GID_VALUE,
    TEST_FUID01_VALUE,
    TEST_MY_VALUE,
    TEST_L_VALUE,
    TEST_YS_VALUE,
    TEST_YP_VALUE,
    TEST_SESSGUARD_VALUE,
)
TEST_COOKIE_MY = 'my=%s; Domain=.yandex.ru; Path=/' % TEST_MY_VALUE
TEST_TUTBY_DOMAIN = 'tut.by'

EXPECTED_SESSION_ID_AFTER_REMOVE = 'Session_id=; Domain=.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; HttpOnly; Path=/'
EXPECTED_SESSIONID2_AFTER_REMOVE = 'sessionid2=; Domain=.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; HttpOnly; Path=/'
EXPECTED_YANDEX_LOGIN_AFTER_REMOVE = 'yandex_login=; Domain=.yandex.ru; Max-Age=31536000; Secure; Path=/'
EXPECTED_SESSGUARD_AFTER_REMOVE = 'sessguard=; Domain=.passport-test.yandex.ru; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; HttpOnly; Path=/'

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

EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE = build_yandex_login_cookie('')
EXPECTED_YANDEX_LOGIN_COOKIE = build_yandex_login_cookie(TEST_LOGIN)

USER_DISPLAY_NAME = DisplayName(name=TEST_DISPLAY_NAME)
TEST_TUTBY_RETPATH = 'https://profile.tut.by/logout/?retpath=%s'


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    COOKIE_YP_DISPLAY_NAME_AGE=100,
    PDD_DOMAIN_RETPATH_WRAPPER_MAP={TEST_TUTBY_DOMAIN: TEST_TUTBY_RETPATH},
    PASSPORT_SUBDOMAIN='passport-test',
)
class TestAccountLogoutView(BaseBundleTestViews):
    default_url = '/1/bundle/account/logout/?consumer=dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        cookie=TEST_USER_COOKIES,
        user_agent=TEST_USER_AGENT,
        referer=TEST_REFERER,
        user_ip=TEST_USER_IP,
    )
    mocked_grants = [ACCOUNT_LOGOUT_GRANT]

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.setup_statbox_templates()
        self.http_query_args = {
            'yu': TEST_YANDEXUID_VALUE,
            'retpath': TEST_RETPATH,
            'target': 'default',
            'is_global': 0,
            'origin': TEST_ORIGIN,
        }
        lrandoms_response = blackbox_lrandoms_response()
        self.env.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)

        self.patches = []
        self._build_cookie_yp = mock.Mock(return_value=EXPECTED_YP_COOKIE)
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)
        self.patches.extend([
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_l',
                mock.Mock(return_value=TEST_COOKIE_L),
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_yp',
                self._build_cookie_yp,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_lah',
                mock.Mock(return_value=TEST_COOKIE_LAH),
            ),
            mock.patch(
                'passport.backend.api.common.authorization.build_cookie_ilahu',
                mock.Mock(return_value=TEST_COOKIE_ILAHU),
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
            self.track_id_generator,
        ])

        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.patches
        del self.track_manager
        del self.track_id_generator
        del self.track_id
        del self._build_cookie_yp

    def get_account_info(self, login=TEST_LOGIN, uid=TEST_UID, display_name_data=None, display_login=None):
        return {
            'uid': uid,
            'login': login,
            'display_name': display_name_data or {'name': '', 'default_avatar': ''},
            'display_login': login if display_login is None else display_login,
        }

    def assert_track_ok(self, session='2:session', sslsession='2:sslsession', sessguard='1.sessguard', retpath=TEST_RETPATH):
        track = self.track_manager.read(self.track_id)
        eq_(track.session, session)
        eq_(track.sslsession, sslsession)
        eq_(track.sessguard, sessguard)
        eq_(track.retpath, retpath)

    def assert_historydb_ok(self):
        expected_log_entries = {
            'action': 'logout',
            'consumer': 'dev',
            'user_agent': TEST_USER_AGENT,
            'info.glogout': TimeNow(),
        }
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def assert_db_ok(self):
        shard_name = 'passportdbshard1'
        eq_(self.env.db.query_count(shard_name), 1)
        self.env.db.check(
            'attributes',
            'account.global_logout_datetime',
            TimeNow(),
            uid=TEST_UID,
            db=shard_name,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            uid=str(TEST_UID),
            consumer='dev',
        )
        statbox_params = {
            'mode': 'logout',
            'ip': TEST_USER_IP,
            'user_agent': TEST_USER_AGENT,
            'origin': TEST_ORIGIN,
            'retpath': TEST_RETPATH,
            'referer': TEST_REFERER,
            'yandexuid': TEST_YANDEXUID_VALUE,
            'authid': TEST_OLD_AUTH_ID,
            'global': '0',
            'target': 'default',
        }
        self.env.statbox.bind_entry(
            'local_base',
            **statbox_params
        )
        self.env.statbox.bind_entry(
            'cookie_remove',
            _inherit_from='local_base',
            action='cookie_remove',
        )
        self.env.statbox.bind_entry(
            'cookie_edit',
            _inherit_from='local_base',
            action='cookie_edit',
        )
        self.env.statbox.bind_entry(
            'everybody',
            _inherit_from='local_base',
            target='everybody',
            action='cookie_remove',
        )
        self.env.statbox.bind_entry(
            'account_modification',
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            entity='account.global_logout_datetime',
            operation='updated',
            old=datetime.fromtimestamp(1).strftime('%Y-%m-%d %H:%M:%S'),
            new=DatetimeNow(convert_to_datetime=True),
        )
        self.env.statbox.bind_entry(
            'multibrowser_update',
            _exclude=['consumer'],
            mode='any_auth',
            action='multibrowser_update',
            yandexuid=TEST_YANDEXUID_VALUE,
            ip=TEST_USER_IP,
            user_agent=TEST_USER_AGENT,
            old_multibrowser='0',
            new_multibrowser='1',
        )

    def build_auth_log_entries(self, status, **kwargs):
        entries = {
            'type': 'web',
            'status': status,
            'uid': str(TEST_UID),
            'useragent': TEST_USER_AGENT,
            'yandexuid': TEST_YANDEXUID_VALUE,
            'comment': 'aid=%s;ttl=3' % TEST_AUTH_ID,
            'ip_from': TEST_USER_IP,
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

    def get_expected_cookies(self, sessionid_cookie=None, sessionid2_cookie=None, ys_cookie=None,
                             yandex_login_cookie=None, skip_l_cookie=False, skip_lah_cookie=False,
                             mda2_beacon_cookie=None, sessguard_cookie=None):

        cookies = [
            sessionid_cookie or EXPECTED_SESSIONID_COOKIE,
            EXPECTED_YP_COOKIE,
            TEST_COOKIE_ILAHU,
        ]
        if not skip_l_cookie:
            cookies.append(TEST_COOKIE_L)
        if not skip_lah_cookie:
            cookies.append(TEST_COOKIE_LAH)

        if sessionid2_cookie:
            cookies.append(sessionid2_cookie)
        if sessguard_cookie:
            cookies.append(sessguard_cookie)
        if ys_cookie:
            cookies.append(ys_cookie)
        if yandex_login_cookie:
            cookies.append(yandex_login_cookie)

        cookies.append(mda2_beacon_cookie or EXPECTED_LONG_MDA2_BEACON_COOKIE)

        return cookies

    def get_cookies_after_remove(self):
        return [
            EXPECTED_SESSION_ID_AFTER_REMOVE,
            EXPECTED_SESSIONID2_AFTER_REMOVE,
            EXPECTED_SESSGUARD_AFTER_REMOVE,
            build_ys_cookie(''),
            EXPECTED_YP_COOKIE,
            EXPECTED_YANDEX_LOGIN_AFTER_REMOVE,
            TEST_COOKIE_ILAHU,
            EXPECTED_LONG_MDA2_BEACON_COOKIE,
        ]

    def test_empty_cookie_header__error(self):
        resp = self.make_request(exclude_headers=['cookie'])
        self.assert_error_response(resp, ['cookie.empty'])

    def test_yandexuid_not_matched__error(self):
        resp = self.make_request(query_args=dict(yu=123))
        self.assert_error_response(resp, ['csrf_token.invalid'])

    def test_connection_id_not_matched__error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                connection_id=TEST_CONNECTION_ID_VALUE,
            ),
        )
        resp = self.make_request(query_args=dict(ci=123), exclude_args=['yu'])
        self.assert_error_response(resp, ['csrf_token.invalid'])

    def test_invalid_form__error(self):
        data = dict(
            yu='    ',
            retpath='foo.bar',
            target='def ault',
        )
        resp = self.make_request(query_args=data)
        self.assert_error_response(resp, ['form.invalid'])
        self.env.statbox.assert_has_written([])

    def test_session_invalid__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        resp = self.make_request()
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_cookies_after_remove(),
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
            retpath=TEST_DEFAULT_RETPATH,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry(
                'cookie_remove',
                _exclude=['authid'],
                uid='0',
                retpath=TEST_DEFAULT_RETPATH,
            ),
        ])
        self.assert_events_are_empty(self.env.auth_handle_mock)

    def test_session_expired_with_global__ok(self):
        retpath = 'http://yandex.com.tr/test'
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_EXPIRED_STATUS),
        )
        resp = self.make_request(query_args=dict(is_global=1, target='everybody', retpath=retpath))
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_cookies_after_remove(),
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
            retpath=retpath,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry(
                'cookie_remove',
                _exclude=['authid'],
                **{
                    'uid': '0',
                    'global': '1',
                    'retpath': retpath,
                }
            ),
        ])
        self.assert_events_are_empty(self.env.auth_handle_mock)

    def test_global_logout_default__with_one_account__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                authid=TEST_OLD_AUTH_ID,
            ),
        )
        self.env.blackbox.set_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='',
                session_value='',
                ssl_session_value='',
                sessguard_value='',
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )
        resp = self.make_request(query_args=dict(is_global=1))
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_expected_cookies(
                sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                sessguard_cookie=EXPECTED_EMPTY_SESSGUARD_COOKIE,
                ys_cookie=build_ys_cookie(''),
                yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
            logged_out_uids=[TEST_UID],
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('account_modification'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry('cookie_remove', **{'global': '1'}),
        ])
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    comment='aid=%s;ttl=0' % TEST_OLD_AUTH_ID,
                ),
            ],
        )

    def test_global_logout_default__one_disabled_account__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                authid=TEST_OLD_AUTH_ID,
                default_user_status=BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )
        self.env.blackbox.set_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='',
                session_value='',
                ssl_session_value='',
                sessguard_value='',
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )
        resp = self.make_request(query_args=dict(is_global=1))
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_expected_cookies(
                sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                sessguard_cookie=EXPECTED_EMPTY_SESSGUARD_COOKIE,
                ys_cookie=build_ys_cookie(''),
                yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
            logged_out_uids=[TEST_UID],
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('account_modification'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry('cookie_remove', **{'global': '1'}),
        ])
        self.assert_db_ok()
        self.assert_historydb_ok()  # глогаут всё равно проставили
        self.assert_auth_log([])  # сессия уже была невалидна

    def test_global_logout_default__one_deleted_account__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ttl=3,
                authid=TEST_OLD_AUTH_ID,
                default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS,
                item_id=TEST_UID,
                uid=None,
            ),
        )
        self.env.blackbox.set_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='',
                session_value='',
                ssl_session_value='',
                sessguard_value='',
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )
        resp = self.make_request(query_args=dict(is_global=1))
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_expected_cookies(
                sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                sessguard_cookie=EXPECTED_EMPTY_SESSGUARD_COOKIE,
                ys_cookie=build_ys_cookie(''),
                yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
            logged_out_uids=[TEST_UID],
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry('cookie_remove', **{'global': '1'}),
        ])
        self.env.event_logger.assert_events_are_logged([])
        self.assert_auth_log([])  # сессия уже была невалидна

    def test_global_logout_everybody__with_multiple_accounts__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    ttl=3,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
                display_name=TEST_DISPLAY_NAME_DATA,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid=TEST_OTHER_UID,
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )

        resp = self.make_request(query_args=dict(is_global=1, target='everybody'))

        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            accounts=[
                self.get_account_info(
                    uid=TEST_OTHER_UID,
                    login=TEST_OTHER_LOGIN,
                    display_name_data=TEST_DISPLAY_NAME_DATA,
                ),
            ],
            cookies=self.get_expected_cookies(
                sessionid2_cookie=EXPECTED_SESSIONID2_COOKIE,
                sessguard_cookie=EXPECTED_SESSGUARD_COOKIE,
                ys_cookie=build_ys_cookie(USER_DISPLAY_NAME),
                yandex_login_cookie=build_yandex_login_cookie(TEST_OTHER_LOGIN),
                mda2_beacon_cookie=EXPECTED_MDA2_BEACON_COOKIE,
            ),
            default_uid=TEST_OTHER_UID,
            logged_out_uids=[TEST_UID],
        )
        self.assert_track_ok()
        self.assert_db_ok()
        self.assert_historydb_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('account_modification'),
            self.env.statbox.entry('multibrowser_update', uid=str(TEST_OTHER_UID)),
            self.env.statbox.entry(
                'cookie_edit',
                **{
                    'retpath': TEST_DEFAULT_RETPATH,
                    'global': '1',
                }
            ),
        ])
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    SESSION_UPDATE,
                    uid=str(TEST_OTHER_UID),
                    login=TEST_OTHER_LOGIN,
                    comment='aid=%s;ttl=3' % TEST_AUTH_ID,
                ),
            ],
        )

    def test_logout_everybody__with_one_account__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                authid=TEST_OLD_AUTH_ID,
            ),
        )
        data = self.http_query_args.update(target='everybody', retpath=None)
        resp = self.make_request(data)
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_cookies_after_remove(),
            logged_out_uids=[TEST_UID],
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
            retpath=TEST_DEFAULT_RETPATH,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry('everybody', retpath=TEST_DEFAULT_RETPATH),
        ])

    def test_logout_everybody__with_multiple_accounts__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    ttl=3,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
            ),
        )
        data = self.http_query_args.update(target='everybody', retpath=None)
        resp = self.make_request(data)
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_cookies_after_remove(),
            logged_out_uids=[TEST_UID, TEST_OTHER_UID],
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
            retpath=TEST_DEFAULT_RETPATH,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry('everybody', retpath=TEST_DEFAULT_RETPATH),
        ])
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    uid=str(TEST_UID),
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    SESSION_KILL,
                    uid=str(TEST_OTHER_UID),
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
            ],
        )

    def test_logout_everybody__with_multiple_accounts__not_logging_invalid__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_invalid_session(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    ttl=3,
                    authid=TEST_OLD_AUTH_ID,
                ),
                item_id=TEST_OTHER_UID,
            ),
        )
        data = self.http_query_args.update(target='everybody', retpath=None)
        resp = self.make_request(data)
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_cookies_after_remove(),
            logged_out_uids=[TEST_UID, TEST_OTHER_UID],
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
            retpath=TEST_DEFAULT_RETPATH,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry('everybody', retpath=TEST_DEFAULT_RETPATH),
        ])
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
            ],
        )

    def test_logout_everybody__with_multiple_accounts__default_invalid__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ttl=3,
                    authid=TEST_OLD_AUTH_ID,
                    default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS,
                    item_id=TEST_UID,
                    uid=None,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
            ),
        )
        data = self.http_query_args.update(target='everybody', retpath=None)
        resp = self.make_request(data)
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_cookies_after_remove(),
            logged_out_uids=[TEST_UID, TEST_OTHER_UID],
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
            retpath=TEST_DEFAULT_RETPATH,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('multibrowser_update', _exclude=['uid']),
            self.env.statbox.entry('everybody', retpath=TEST_DEFAULT_RETPATH),
        ])
        self.assert_auth_log([
            self.build_auth_log_entries(
                SESSION_KILL,
                uid=str(TEST_OTHER_UID),
                comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
            ),
        ])

    def test_logout_default__with_one_account__ok(self):
        self.env.blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                authid=TEST_OLD_AUTH_ID,
                ttl=3,
                display_name=TEST_DISPLAY_NAME_DATA,
            ),
        )
        self.env.blackbox.set_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='',
                session_value='',
                ssl_session_value='',
                sessguard_value='',
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )
        rv = self.make_request(
            headers=dict(
                cookie='Session_id=%s; sessionid2=%s; yandexuid=%s' % (
                    TEST_OLD_SESSIONID_VALUE,
                    TEST_OLD_SSL_SESSIONID_VALUE,
                    TEST_YANDEXUID_VALUE,
                ),
            ),
        )
        self.assert_ok_response(
            rv,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_expected_cookies(
                sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                sessguard_cookie=EXPECTED_EMPTY_SESSGUARD_COOKIE,
                ys_cookie=build_ys_cookie(''),
                yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                skip_l_cookie=True,
                skip_lah_cookie=True,
            ),
            logged_out_uids=[TEST_UID],
        )
        self.assert_track_ok(
            session='',
            sslsession='',
            sessguard='',
        )
        sessionid_request = self.env.blackbox.requests[0]
        ok_(sessionid_request.method_equals('sessionid', self.env.blackbox))
        sessionid_request.assert_query_contains(
            {
                'allow_scholar': 'yes',
                'multisession': 'yes',
                'sessionid': TEST_OLD_SESSIONID_VALUE,
                'sslsessionid': TEST_OLD_SSL_SESSIONID_VALUE,
            },
        )

        edit_session_request = self.env.blackbox.requests[1]
        ok_(edit_session_request.method_equals('editsession', self.env.blackbox))
        edit_session_request.assert_query_contains(
            {
                'uid': str(TEST_UID),
                'format': 'json',
                'sessionid': TEST_OLD_SESSIONID_VALUE,
                'sslsessionid': TEST_OLD_SSL_SESSIONID_VALUE,
                'host': TEST_HOST,
                'userip': TEST_USER_IP,
                'op': 'delete',
                'create_time': TimeNow(),
            },
        )

        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies'),
            self.env.statbox.entry('cookie_remove'),
        ])
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
            ],
        )

    def test_logout_default__with_multiple_accounts__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    uid=TEST_UID,
                    login=TEST_LOGIN,
                    ttl=3,
                    authid=TEST_OLD_AUTH_ID,
                ),
                uid=TEST_OTHER_UID,
                login=TEST_OTHER_LOGIN,
                display_name=TEST_DISPLAY_NAME_DATA,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid=TEST_OTHER_UID,
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )

        rv = self.make_request(exclude_args=['target'])

        self.assert_ok_response(
            rv,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            accounts=[
                self.get_account_info(
                    uid=TEST_OTHER_UID,
                    login=TEST_OTHER_LOGIN,
                    display_name_data=TEST_DISPLAY_NAME_DATA,
                ),
            ],
            cookies=self.get_expected_cookies(
                sessionid2_cookie=EXPECTED_SESSIONID2_COOKIE,
                sessguard_cookie=EXPECTED_SESSGUARD_COOKIE,
                ys_cookie=build_ys_cookie(USER_DISPLAY_NAME),
                yandex_login_cookie=build_yandex_login_cookie(TEST_OTHER_LOGIN),
                mda2_beacon_cookie=EXPECTED_MDA2_BEACON_COOKIE,
            ),
            default_uid=TEST_OTHER_UID,
            logged_out_uids=[TEST_UID],
        )
        self.assert_track_ok()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', have_sessguard='1'),
            self.env.statbox.entry('multibrowser_update', uid=str(TEST_OTHER_UID)),
            self.env.statbox.entry(
                'cookie_edit',
                retpath=TEST_DEFAULT_RETPATH,
                target='default',
            ),
        ])
        self.assert_auth_log(
            [
                self.build_auth_log_entries(
                    SESSION_KILL,
                    comment='aid=%s;ttl=3' % TEST_OLD_AUTH_ID,
                ),
                self.build_auth_log_entries(
                    SESSION_UPDATE,
                    uid=str(TEST_OTHER_UID),
                    login=TEST_OTHER_LOGIN,
                    comment='aid=%s;ttl=3' % TEST_AUTH_ID,
                ),
            ],
        )

    def test_logout_tutby(self):
        retpaths = [
            u'https://www.yandex.ru/test?test1=test1&test2=test2',
            u'https://www.yandex.by/search/?text=карта расстояний',
        ]
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                authid=TEST_OLD_AUTH_ID,
                domain=TEST_TUTBY_DOMAIN,
                uid=TEST_PDD_UID,
                login='test@tut.by',
                aliases={
                    'pdd': 'test@tut.by',
                },
            ),
        )
        self.env.blackbox.set_response_value(
            'editsession',
            blackbox_editsession_response(
                authid=TEST_AUTH_ID,
                default_uid='',
                session_value='',
                ssl_session_value='',
                sessguard_value='',
                sessguard_hosts=['passport-test.yandex.ru'],
            ),
        )
        for retpath in retpaths:
            resp = self.make_request(
                query_args=dict(retpath=retpath),
                headers=dict(
                    cookie='Session_id=%s; sessionid2=%s; yandexuid=%s' % (
                        TEST_OLD_SESSIONID_VALUE,
                        TEST_OLD_SSL_SESSIONID_VALUE,
                        TEST_YANDEXUID_VALUE,
                    ),
                ),
            )
            expected_retpath = TEST_TUTBY_RETPATH % quote_plus(smart_str(retpath))
            self.assert_ok_response(
                resp,
                ignore_order_for=['cookies'],
                track_id=self.track_id,
                cookies=self.get_expected_cookies(
                    sessionid_cookie=EXPECTED_EMPTY_SESSIONID_COOKIE,
                    sessionid2_cookie=EXPECTED_EMPTY_SESSIONID2_COOKIE,
                    sessguard_cookie=EXPECTED_EMPTY_SESSGUARD_COOKIE,
                    ys_cookie=build_ys_cookie(''),
                    yandex_login_cookie=EXPECTED_EMPTY_YANDEX_LOGIN_COOKIE,
                    skip_l_cookie=True,
                    skip_lah_cookie=True,
                ),
                logged_out_uids=[TEST_PDD_UID],
            )
            self.assert_track_ok(
                session='',
                sslsession='',
                sessguard='',
                retpath=expected_retpath,
            )
            self.env.statbox.assert_contains([
                self.env.statbox.entry(
                    'cookie_remove',
                    retpath=expected_retpath,
                    uid=str(TEST_PDD_UID),
                ),
            ], offset=-1)
            self.check_auth_log_entries(
                self.env.auth_handle_mock,
                self.build_auth_log_entries(
                    SESSION_KILL,
                    uid=str(TEST_PDD_UID),
                    comment='aid=%s;ttl=0' % TEST_OLD_AUTH_ID,
                ),
            )

    def test_logout_everybody__with_connection_id__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                connection_id=TEST_CONNECTION_ID_VALUE,
            ),
        )
        data = self.http_query_args.update(target='everybody', retpath=None, ci=TEST_CONNECTION_ID_VALUE)
        resp = self.make_request(data, exclude_args=['yu'])
        self.assert_ok_response(
            resp,
            ignore_order_for=['cookies'],
            track_id=self.track_id,
            cookies=self.get_cookies_after_remove(),
            logged_out_uids=[TEST_UID],
        )
