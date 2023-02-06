# -*- coding: utf-8 -*-
import base64
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_login_response,
    blackbox_lrandoms_response,
    blackbox_pwdhistory_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_test_pwd_hashes_response,
    blackbox_userinfo_response,
)
from passport.backend.core.models.password import (
    PASSWORD_ENCODING_VERSION_MD5_CRYPT,
    PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON,
)
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import (
    merge_dicts,
    remove_none_values,
)

from .base_test_data import *


TEST_HOST = 'kinopoisk.ru'


class BaseChangeKinopoiskPasswordTestCase(object):

    def get_expected_response(self, state=None,
                              validation_method=u'captcha', uid=TEST_KINOPOISK_UID,
                              retpath=TEST_RETPATH, login=u'', display_login=''):
        response = {
            'track_id': self.track_id,
            'retpath': retpath,
            'account': {
                'uid': uid,
                'login': login,
                # Этот хардкод отсылает нас к `passport.test.blackbox.py:_blackbox_userinfo`
                'display_name': {'name': '', 'default_avatar': ''},
                'person': {
                    'firstname': u'\\u0414',
                    'lastname': u'\\u0424',
                    'birthday': '1963-05-15',
                    'gender': 1,
                    'language': 'ru',
                    'country': 'ru',
                },
                'display_login': login if display_login is None else display_login,
            },
        }
        if validation_method:
            response['validation_method'] = validation_method

        if state:
            response.update(state=state)
        return response


class BaseChangeKinopoiskPasswordSubmitTestCase(BaseBundleTestViews, BaseChangeKinopoiskPasswordTestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['account.change_kinopoisk_password'])

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs()
            ),
        )

        self.default_url = '/1/bundle/change_password/kinopoisk/submit/?consumer=dev'

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def build_headers(self, cookie=TEST_NONSECURE_COOKIE, host=TEST_HOST, user_ip=TEST_USER_IP):
        return mock_headers(
            user_ip=user_ip,
            user_agent=TEST_USER_AGENT,
            cookie=cookie,
            host=host,
        )

    def account_kwargs(self, uid=TEST_KINOPOISK_UID, login='', alias_type='kinopoisk',
                       cryptpasswd='1:secret', **kwargs):
        base_kwargs = dict(
            uid=uid,
            login=login,
            attributes={'password.encrypted': cryptpasswd},
            aliases={alias_type: login or TEST_KINOPOISK_ALIAS},
            emails=[],
        )
        return merge_dicts(base_kwargs, kwargs)

    def get_expected_response(self, success=True, is_strong_password_policy_required=False,
                              **kwargs):
        response = super(BaseChangeKinopoiskPasswordSubmitTestCase, self).get_expected_response(**kwargs)

        if success:
            response.update(
                revokers={
                    'default': {
                        'tokens': True,
                        'web_sessions': True,
                        'app_passwords': True,
                    },
                    'allow_select': not is_strong_password_policy_required,
                },
            )
        return response

    def query_params(self, retpath=TEST_RETPATH):
        return dict(retpath=retpath)

    def make_request(self, headers, data=None):
        return self.env.client.post(
            self.default_url,
            data=data or {},
            headers=headers,
        )

    def check_track(self, uid=TEST_KINOPOISK_UID, login=None,
                    is_password_change=True, retpath=TEST_RETPATH,
                    is_captcha_required=True):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(uid))
        eq_(track.login, login)
        eq_(track.country, 'ru')
        eq_(track.is_password_change, is_password_change)
        eq_(track.retpath, retpath)
        eq_(track.is_captcha_required, is_captcha_required)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='change_kinopoisk_password',
            track_id=self.track_id,
            uid=TEST_KINOPOISK_UID,
        )

    def check_statbox_records(self, uid=TEST_KINOPOISK_UID, with_check_cookies=False):
        expected_entries = []
        if with_check_cookies:
            expected_entries.append(self.env.statbox.entry('check_cookies', host='kinopoisk.ru'))
        self.env.statbox.assert_has_written(expected_entries)


@with_settings_hosts()
class ChangeKinopoiskPasswordSubmitTestCase(BaseChangeKinopoiskPasswordSubmitTestCase):

    def test_missing_client_ip(self):
        rv = self.make_request(
            headers=self.build_headers(
                user_ip=None,
            ),
        )

        self.assert_error_response(rv, ['ip.empty'])

    def test_missing_host(self):
        rv = self.make_request(
            headers=self.build_headers(
                host=None,
            ),
        )

        self.assert_error_response(rv, ['host.empty'])

    def test_missing_cookie(self):
        rv = self.make_request(headers=self.build_headers(cookie=None))

        self.assert_error_response(rv, ['cookie.empty'])

    def test_invalid_sessionid(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_KINOPOISK_UID,
            ),
        )
        rv = self.make_request(
            headers=self.build_headers(cookie='Session_id='),
        )

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_invalid_sessionid_with_account_info(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                uid=TEST_KINOPOISK_UID,
            ),
        )
        rv = self.make_request(
            headers=self.build_headers(cookie='Session_id='),
        )

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_disabled_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_KINOPOISK_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )
        rv = self.make_request(headers=self.build_headers())
        self.assert_error_response(rv, ['account.disabled'])

    def test_not_kinopoisk_account_blocked(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    alias_type='portal',
                    login=TEST_LOGIN,
                )
            ),
        )
        rv = self.make_request(headers=self.build_headers())
        self.assert_error_response(rv, ['account.invalid_type'])

    def test_disabled_account_with_userinfo(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_KINOPOISK_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
            ),
        )
        rv = self.make_request(headers=self.build_headers())
        self.assert_error_response(rv, ['account.disabled'])

    def test_disabled_on_deletion_account(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_KINOPOISK_UID,
                status=blackbox.BLACKBOX_SESSIONID_DISABLED_STATUS,
                attributes={
                    'account.is_disabled': '2',
                },
            ),
        )
        rv = self.make_request(headers=self.build_headers())
        self.assert_error_response(rv, ['account.disabled_on_deletion'])

    def test_kinopoisk_account_ok(self):
        rv = self.make_request(headers=self.build_headers(), data=self.query_params())
        self.assert_ok_response(rv, **self.get_expected_response())
        self.check_track()
        self.check_statbox_records(with_check_cookies=True)

    def test_kinopoisk_account_with_strong_password_policy_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    subscribed_to=[67],
                    dbfields={
                        'subscription.login_rule.67': 1,
                    },
                    attributes={'password.encrypted': '1:secret'},
                )
            ),
        )
        rv = self.make_request(headers=self.build_headers(), data=self.query_params())
        self.assert_ok_response(rv, **self.get_expected_response(is_strong_password_policy_required=True))
        self.check_track()
        self.check_statbox_records(with_check_cookies=True)

    def test_kinopoisk_account_ok_empty_retpath(self):
        rv = self.make_request(headers=self.build_headers(), data=self.query_params(retpath=''))

        self.assert_ok_response(rv, **self.get_expected_response(retpath=None))
        self.check_track(retpath=None)
        self.check_statbox_records(with_check_cookies=True)

    def test_account_without_password(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(cryptpasswd='')
            ),
        )
        rv = self.make_request(headers=self.build_headers())

        self.assert_error_response(
            rv,
            [u'account.without_password'],
            **self.get_expected_response(
                retpath=None,
                validation_method=None,
                success=False,
            )
        )
        self.check_track(
            is_password_change=None,
            retpath=None,
            is_captcha_required=None,
        )
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [self.env.statbox.entry('check_cookies', host='kinopoisk.ru')],
        )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
)
class BaseChangeKinopoiskPasswordCommitTestCase(BaseBundleTestViews):

    uid = TEST_KINOPOISK_UID
    dbshardname = 'passportdbshard2'

    is_password_hash_from_blackbox = True
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON

    accounts_table = 'accounts'
    subscriptions_table = 'subscription'
    userinfo_safe_table = 'userinfo_safe'
    attributes_table = 'attributes'

    SERIALIZE_ACCOUNT = True

    def setup_track(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = self.uid
            track.is_password_change = True
            track.is_captcha_required = True
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(['account.change_kinopoisk_password'])

        self.default_headers = self.build_headers()

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **self.account_kwargs()
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(**self.account_kwargs()),
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
        encoded_hash = base64.b64encode(TEST_OLD_SERIALIZED_PASSWORD)
        self.env.blackbox.set_response_value(
            'test_pwd_hashes',
            blackbox_test_pwd_hashes_response({encoded_hash: False}),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        blackbox_response = blackbox_userinfo_response(**self.account_kwargs())
        if self.SERIALIZE_ACCOUNT:
            self.env.db.serialize(blackbox_response)

        self.default_url = '/1/bundle/change_password/kinopoisk/commit/?consumer=dev'

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.setup_track()
        self.setup_statbox_templates()

    def get_expected_response(self, success=True, is_strong_password_policy_required=False,
                              **kwargs):
        response = super(BaseChangeKinopoiskPasswordCommitTestCase, self).get_expected_response(**kwargs)
        response.pop('retpath')
        response.pop('track_id')
        return response

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def build_headers(self, cookie=TEST_COOKIE, host=TEST_HOST, user_ip=TEST_USER_IP):
        return mock_headers(
            user_ip=user_ip,
            cookie=cookie,
            host=host,
            user_agent=TEST_USER_AGENT,
            accept_language=TEST_ACCEPT_LANGUAGE,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'local_base',
            mode='change_kinopoisk_password',
            track_id=self.track_id,
            ip=TEST_USER_IP,
            consumer='dev',
            user_agent=TEST_USER_AGENT,
            uid=str(self.uid),
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from='local_base',
            _exclude=['uid'],
            action='submitted',
        )
        self.env.statbox.bind_entry(
            'changed_password',
            _inherit_from='local_base',
            action='changed_password',
            password_quality=str(TEST_NEW_PASSWORD_QUALITY),
        )

        self.env.statbox.bind_entry(
            'account_modification',
            _inherit_from='local_base',
            _exclude=['mode', 'track_id'],
            operation='updated',
            event='account_modification',
        )
        self.env.statbox.bind_entry(
            'logout',
            _inherit_from='account_modification',
            new=DatetimeNow(convert_to_datetime=True),
            old=TEST_GLOBAL_LOGOUT_DATETIME,
            operation='updated',
        )
        self.env.statbox.bind_entry(
            'clear_is_creating_required',
            _inherit_from='account_modification',
            sid='100',
            operation='removed',
            entity='subscriptions',
        )
        self.env.statbox.bind_entry(
            'account_revoker_app_passwords',
            _inherit_from='logout',
            entity='account.revoker.app_passwords',
        )
        self.env.statbox.bind_entry(
            'account_revoker_app_tokens',
            _inherit_from='logout',
            entity='account.revoker.tokens',
        )
        self.env.statbox.bind_entry(
            'account_revoker_web_sessions',
            _inherit_from='logout',
            entity='account.revoker.web_sessions',
        )
        self.env.statbox.bind_entry(
            'account_global_logout_datetime',
            _inherit_from='logout',
            entity='account.global_logout_datetime',
        )

        self.env.statbox.bind_entry(
            'password_encrypted',
            _inherit_from='account_modification',
            entity='password.encrypted',
        )
        self.env.statbox.bind_entry(
            'password_encoding',
            _inherit_from='account_modification',
            entity='password.encoding_version',
            old=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT),
            new=str(PASSWORD_ENCODING_VERSION_MD5_CRYPT_ARGON),
        )
        self.env.statbox.bind_entry(
            'password_quality',
            _inherit_from='account_modification',
            entity='password.quality',
            old=str(TEST_PASSWORD_QUALITY),
            new=str(TEST_NEW_PASSWORD_QUALITY),
        )

    def account_kwargs(self, **kwargs):
        params = dict(
            uid=self.uid,
            login='',
            attributes={
                'person.country': TEST_USER_COUNTRY,
                'person.timezone': TEST_USER_TIMEZONE,
                'person.language': TEST_USER_LANGUAGE,
                'password.encrypted': TEST_OLD_SERIALIZED_PASSWORD,
            },
            dbfields={
                'password_quality.quality.uid': TEST_PASSWORD_QUALITY,
                'password_quality.version.uid': TEST_PASSWORD_QUALITY_VERSION,
            },
            emails=[],
            aliases={
                'kinopoisk': TEST_KINOPOISK_ALIAS,
            },
        )
        return merge_dicts(params, kwargs)

    def query_params(self, **kwargs):
        params = dict(
            uid=self.uid,
            track_id=self.track_id,
            current_password=TEST_PASSWORD,
            password=TEST_NEW_PASSWORD,
        )
        params.update(kwargs)
        return params

    def make_request(self, headers, data):
        return self.env.client.post(
            self.default_url,
            data=data,
            headers=headers,
        )

    def assert_cookies_ok(self, cookies):
        eq_(len(cookies), 6)
        l_cookie, sessionid_cookie, sessionid2_cookie, yalogin_cookie, yp_cookie, ys_cookie = sorted(cookies)
        self.assert_cookie_ok(l_cookie, 'L')
        self.assert_cookie_ok(sessionid_cookie, 'Session_id', expires=None, http_only=True)
        self.assert_cookie_ok(sessionid2_cookie, 'sessionid2', expires=None)
        self.assert_cookie_ok(yalogin_cookie, 'yandex_login', expires=None)
        self.assert_cookie_ok(yp_cookie, 'yp')
        self.assert_cookie_ok(ys_cookie, 'ys', expires=None)

    def check_db(self, centraldb_query_count=0, sharddb_query_count=2,
                 global_logout=True, web_sessions_revoked=False, tokens_revoked=False, app_passwords_revoked=False):
        timenow = TimeNow()

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count(self.dbshardname), sharddb_query_count)

        if global_logout:
            self.env.db.check(self.attributes_table, 'account.global_logout_datetime', timenow, uid=self.uid, db=self.dbshardname)
        else:
            self.env.db.check_missing(self.attributes_table, 'account.global_logout_datetime', uid=self.uid, db=self.dbshardname)

        if web_sessions_revoked:
            self.env.db.check(self.attributes_table, 'revoker.web_sessions', timenow, uid=self.uid, db=self.dbshardname)
        else:
            self.env.db.check_missing(self.attributes_table, 'revoker.web_sessions', uid=self.uid, db=self.dbshardname)

        if tokens_revoked:
            self.env.db.check(self.attributes_table, 'revoker.tokens', timenow, uid=self.uid, db=self.dbshardname)
        else:
            self.env.db.check_missing(self.attributes_table, 'revoker.tokens', uid=self.uid, db=self.dbshardname)

        if app_passwords_revoked:
            self.env.db.check(self.attributes_table, 'revoker.app_passwords', timenow, uid=self.uid, db=self.dbshardname)
        else:
            self.env.db.check_missing(self.attributes_table, 'revoker.app_passwords', uid=self.uid, db=self.dbshardname)

        self.env.db.check(self.attributes_table, 'password.update_datetime', timenow, uid=self.uid, db=self.dbshardname)
        self.env.db.check(self.attributes_table, 'password.quality', '3:100', uid=self.uid, db=self.dbshardname)

        self.env.db.check_missing(self.attributes_table, 'password.forced_changing_reason', uid=self.uid, db=self.dbshardname)
        self.env.db.check_missing(self.attributes_table, 'password.is_creating_required', uid=self.uid, db=self.dbshardname)

        eav_pass_hash = self.env.db.get(self.attributes_table, 'password.encrypted', uid=self.uid, db=self.dbshardname)
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('1:'))
            ok_(eav_pass_hash != TEST_OLD_SERIALIZED_PASSWORD)

    def check_track_ok(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.is_password_change, False)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_checked, True)
        eq_(track.is_captcha_recognized, True)
        eq_(track.have_password, True)
        eq_(track.old_session_ttl, '0')

    def check_captcha_statuses_on_error(self):
        track = self.track_manager.read(self.track_id)
        eq_(track.is_captcha_required, True)
        eq_(track.is_captcha_recognized, False)
        eq_(track.is_captcha_checked, False)

    def historydb_entry(self, uid=1, name=None, value=None):
        entry = {
            'uid': str(uid),
            'name': name,
            'value': value,
        }
        return remove_none_values(entry)

    def check_log_entries(self, password_hash=None,
                          old_session_uids=None, global_logout=True,
                          web_sessions_revoked=False, tokens_revoked=False, app_passwords_revoked=False,
                          uids_count=None, clear_is_creating_required=False, with_check_cookies=False):

        if password_hash is None:
            password_encrypted = self.env.db.get(
                self.attributes_table,
                'password.encrypted',
                uid=self.uid,
                db=self.dbshardname,
            )
            password_hash = password_encrypted

        expected_log_entries = []

        if global_logout:
            expected_log_entries.append(
                self.historydb_entry(self.uid, 'info.glogout', TimeNow()),
            )
        if tokens_revoked:
            expected_log_entries.append(
                self.historydb_entry(self.uid, 'info.tokens_revoked', TimeNow()),
            )
        if web_sessions_revoked:
            expected_log_entries.append(
                self.historydb_entry(self.uid, 'info.web_sessions_revoked', TimeNow()),
            )
        if app_passwords_revoked:
            expected_log_entries.append(
                self.historydb_entry(self.uid, 'info.app_passwords_revoked', TimeNow()),
            )

        # Одна запись в historydb о смене пароля
        expected_log_entries.extend([
            self.historydb_entry(self.uid, 'info.password', password_hash),
            self.historydb_entry(self.uid, 'info.password_quality', '100'),
            self.historydb_entry(self.uid, 'info.password_update_time', TimeNow()),
        ])

        if clear_is_creating_required:
            expected_log_entries.append(self.historydb_entry(self.uid, 'sid.rm', '100|%s' % TEST_LOGIN))

        expected_log_entries.extend([
            self.historydb_entry(self.uid, 'action', 'change_password'),
            self.historydb_entry(self.uid, 'consumer', 'dev'),
            self.historydb_entry(self.uid, 'user_agent', 'curl'),
        ])

        self.assert_events_are_logged_with_order(
            self.env.handle_mock,
            expected_log_entries,
        )

        expected_log_entries = [
            self.env.statbox.entry('submitted'),
        ]
        if with_check_cookies:
            expected_log_entries.append(self.env.statbox.entry('check_cookies', host='kinopoisk.ru'))

        if global_logout:
            expected_log_entries += [
                self.env.statbox.entry('account_global_logout_datetime'),
            ]

        if web_sessions_revoked:
            expected_log_entries += [
                self.env.statbox.entry('account_revoker_web_sessions'),
            ]

        if tokens_revoked:
            expected_log_entries += [
                self.env.statbox.entry('account_revoker_app_tokens'),
            ]

        if app_passwords_revoked:
            expected_log_entries += [
                self.env.statbox.entry('account_revoker_app_passwords'),
            ]

        expected_log_entries += [
            self.env.statbox.entry('password_encrypted'),
        ]
        if self.is_password_hash_from_blackbox:
            expected_log_entries += [
                self.env.statbox.entry('password_encoding'),
            ]
        expected_log_entries += [
            self.env.statbox.entry('password_quality'),
        ]

        if clear_is_creating_required:
            expected_log_entries.append(self.env.statbox.entry('clear_is_creating_required'))

        changed_password_entry = self.env.statbox.entry('changed_password')

        expected_log_entries.append(changed_password_entry)
        self.env.statbox.assert_has_written(expected_log_entries)

    def assert_sessionid_called(self, call_index=0):
        self.env.blackbox.requests[call_index].assert_query_contains({
            'aliases': 'all_with_hidden',
        })


@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
)
class ChangeKinopoiskPasswordCommitTestCase(BaseChangeKinopoiskPasswordCommitTestCase,
                                            BaseChangeKinopoiskPasswordTestCase):

    SERIALIZE_ACCOUNT = False

    def setUp(self):
        super(ChangeKinopoiskPasswordCommitTestCase, self).setUp()
        account_kwargs = self.account_kwargs()
        blackbox_response = blackbox_userinfo_response(**account_kwargs)
        self.env.db.serialize(blackbox_response)
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                **account_kwargs
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )

    def test_change_password__good_way__ok(self):
        rv = self.make_request(
            self.default_headers,
            self.query_params(),
        )

        self.assert_ok_response(rv, **self.get_expected_response())
        self.check_db()
        self.check_log_entries(old_session_uids=str(self.uid), with_check_cookies=True)
        self.check_track_ok()
        self.assert_sessionid_called()

    def test_not_kinopoisk_account_blocked(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                **self.account_kwargs(
                    aliases={
                        'portal': TEST_LOGIN,
                    },
                )
            ),
        )
        rv = self.make_request(
            self.default_headers,
            self.query_params(),
        )
        self.assert_error_response(rv, ['account.invalid_type'])


@with_settings_hosts(
    BLACKBOX_URL='http://localhost/',
)
class MultiAuthChangeKinopoiskPasswordCommitTestCase(BaseChangeKinopoiskPasswordCommitTestCase,
                                                     BaseChangeKinopoiskPasswordTestCase):

    def assert_change_password_ok(self):
        self.check_db()

        eav_pass_hash = self.env.db.get(self.attributes_table, 'password.encrypted', uid=self.uid, db=self.dbshardname)
        if self.is_password_hash_from_blackbox:
            eq_(eav_pass_hash, TEST_SERIALIZED_PASSWORD)
        else:
            eq_(len(eav_pass_hash), 36)
            ok_(eav_pass_hash.startswith('1:'))
            ok_(eav_pass_hash != TEST_OLD_SERIALIZED_PASSWORD)

        self.check_track_ok()
        return eav_pass_hash

    def assert_blackbox_calls(self):
        self.env.blackbox.requests[0].assert_query_contains({
            'method': 'sessionid',
            'multisession': 'yes',
            'sessionid': TEST_SESSIONID,
            'sslsessionid': TEST_SSL_SESSIONID,
            'aliases': 'all_with_hidden',
        })

    def build_auth_log_entry(self, status, uid):
        return [
            ('uid', str(uid)),
            ('status', status),
            ('type', authtypes.AUTH_TYPE_WEB),
            ('client_name', 'passport'),
            ('useragent', TEST_USER_AGENT),
            ('ip_from', TEST_USER_IP),
        ]

    def assert_auth_and_event_log_ok(self, password_hash,
                                     global_logout=True):
        expected_log_entries = {
            'info.password_quality': '100',
            'info.password': password_hash,
            'info.password_update_time': TimeNow(),
            'action': 'change_password',
            'consumer': 'dev',
            'user_agent': 'curl',
        }
        if global_logout:
            expected_log_entries['info.glogout'] = TimeNow()

        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def test_change_password_for_single_user_session(self):

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                authid=TEST_OLD_AUTH_ID,
                **self.account_kwargs()
            ),
        )

        rv = self.make_request(
            self.default_headers,
            self.query_params(),
        )

        self.assert_ok_response(rv, **self.get_expected_response())
        pass_hash = self.assert_change_password_ok()
        self.assert_blackbox_calls()
        self.check_log_entries(old_session_uids=str(self.uid), global_logout=True, with_check_cookies=True)
        self.assert_auth_and_event_log_ok(pass_hash)

    def test_change_password_for_multiple_users_session(self):

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ip=TEST_USER_IP,
                    age=TEST_COOKIE_AGE,
                    time=TEST_COOKIE_TIMESTAMP,
                    authid=TEST_OLD_AUTH_ID,
                    **self.account_kwargs()
                ),
                uid=12345,
                login='other_login',
            ),
        )

        rv = self.make_request(
            self.default_headers,
            self.query_params(),
        )

        self.assert_ok_response(rv, **self.get_expected_response())
        pass_hash = self.assert_change_password_ok()
        self.assert_blackbox_calls()
        self.check_log_entries(
            old_session_uids='%d,12345' % self.uid,
            global_logout=True,
            uids_count='2',
            with_check_cookies=True,
        )
        self.assert_auth_and_event_log_ok(pass_hash)

    def test_change_password_for_multiple_users_session_one_invalid(self):

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(
                    ip=TEST_USER_IP,
                    age=TEST_COOKIE_AGE,
                    time=TEST_COOKIE_TIMESTAMP,
                    authid=TEST_OLD_AUTH_ID,
                    **self.account_kwargs()
                ),
                uid=12345,
                login='other_login',
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

        rv = self.make_request(
            self.default_headers,
            self.query_params(),
        )

        self.assert_ok_response(rv, **self.get_expected_response())
        pass_hash = self.assert_change_password_ok()
        self.assert_blackbox_calls()
        self.check_log_entries(
            old_session_uids='%d,12345' % self.uid,
            uids_count='2',
            global_logout=True,
            with_check_cookies=True,
        )
        self.assert_auth_and_event_log_ok(
            pass_hash,
            [
                self.build_auth_log_entry('ses_update', self.uid),
            ],
        )

    def test_change_password_for_multiple_users_session_default_invalid_error(self):

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                ip=TEST_USER_IP,
                age=TEST_COOKIE_AGE,
                time=TEST_COOKIE_TIMESTAMP,
                authid=TEST_OLD_AUTH_ID,
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
                **self.account_kwargs()
            ),
        )

        rv = self.make_request(
            self.default_headers,
            self.query_params(),
        )

        self.assert_error_response(rv, ['sessionid.invalid'])

    def test_foreign_session_cookie__error(self):
        """В треке и в куке разные uid'ы - ошибка состояния"""
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 42

        rv = self.make_request(
            self.default_headers,
            self.query_params(),
        )

        self.assert_error_response(
            rv,
            ['track.invalid_state'],
            **self.get_expected_response(validation_method=None)
        )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class ChangeKinopoiskPasswordCommitTestCaseNoBlackboxHash(ChangeKinopoiskPasswordCommitTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class MultiAuthChangeKinopoiskPasswordCommitTestCaseNoBlackboxHash(MultiAuthChangeKinopoiskPasswordCommitTestCase):
    is_password_hash_from_blackbox = False
    password_hash_version = PASSWORD_ENCODING_VERSION_MD5_CRYPT
