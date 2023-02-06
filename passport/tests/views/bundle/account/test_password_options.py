# -*- coding: utf-8 -*-
import base64
from datetime import date
import time

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.password_options import (
    ACCOUNT_GLOBAL_LOGOUT_GRANT,
    ACCOUNT_REVOKE_APP_PASSWORDS_GRANT,
    ACCOUNT_REVOKE_TOKENS_GRANT,
    ACCOUNT_REVOKE_WEB_SESSIONS_GRANT,
    ACCOUNT_SHOW_2FA_PROMO_GRANT,
    LOG_ADMIN_ACTION_GRANT,
    PASSWORD_CHANGING_REQUIREMENT_REASON_GRANT,
    PASSWORD_IS_CHANGING_REQUIRED_GRANT,
    PASSWORD_OPTIONS_BASE_GRANT,
    PASSWORD_UPDATE_DATETIME_GRANT,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms.faker import (
    DEFAULT_PHONE_NUMBER,
    yasms_send_sms_response,
)
from passport.backend.core.models.password import (
    PASSWORD_CHANGING_REASON_HACKED,
    PASSWORD_CHANGING_REASON_PWNED,
)
from passport.backend.core.models.phones.faker import build_phone_secured
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import deep_merge
from passport.backend.utils.time import DEFAULT_FORMAT


ALL_GRANTS = (
    ACCOUNT_GLOBAL_LOGOUT_GRANT,
    ACCOUNT_REVOKE_WEB_SESSIONS_GRANT,
    ACCOUNT_REVOKE_TOKENS_GRANT,
    ACCOUNT_REVOKE_APP_PASSWORDS_GRANT,
    ACCOUNT_SHOW_2FA_PROMO_GRANT,
    LOG_ADMIN_ACTION_GRANT,
    PASSWORD_CHANGING_REQUIREMENT_REASON_GRANT,
    PASSWORD_IS_CHANGING_REQUIRED_GRANT,
    PASSWORD_OPTIONS_BASE_GRANT,
    PASSWORD_UPDATE_DATETIME_GRANT,
)

TEST_LOGIN = 'login'
TEST_UID = 1
TEST_IP = '127.0.0.1'
TEST_ADMIN_LOGIN = 'test-admin'
TEST_COMMENT = 'comment'
TEST_TIMESTAMP = 12345678
TEST_PASSWORD_UPDATE_TIMESTAMP = 1234567
TEST_PASSWORD_HASH = '1:pwd'
TEST_USER_AGENT = 'curl'

# Эта история плохих сессий содержит одно синтетическое значение
# SessionKarma(timestamp=0, authid='test-authid')
TEST_BAD_SESSIONS = base64.b64encode('\x08\x01\x12\x13\x08\x01\x10\x00\x1a\x0btest-authid d')

DEFAULT_GLOGOUT_VALUE = 1


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestPasswordOptionsView(BaseBundleTestViews):

    default_url = '/2/account/%d/password_options/?consumer=dev' % TEST_UID
    http_method = 'post'

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.set_grants()

        self.accounts_table = 'accounts'
        self.subscriptions_table = 'subscription'
        self.attributes_table = 'attributes'

        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            uid=str(TEST_UID),
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'is_changing_required',
            entity='password.is_changing_required',
            operation='created',
            event='account_modification',
            ip=TEST_IP,
            user_agent='-',
            new='1',
            old='-',
        )
        self.env.statbox.bind_entry(
            'is_not_changing_required',
            entity='password.is_changing_required',
            operation='deleted',
            event='account_modification',
            ip=TEST_IP,
            user_agent='-',
            new='-',
            old='1',
        )
        self.env.statbox.bind_entry(
            'notification_sent',
            unixtime=TimeNow(),
            mode='password_options',
            action='password_options.notification_sent',
            number='+79031******',
            sms_id='1',
        )
        self.env.statbox.bind_entry(
            'loaded_secure_number',
            unixtime=TimeNow(),
            mode='password_options',
            action='loaded_secure_number',
            error='invalid_phone_number',
        )
        self.env.statbox.bind_entry(
            'pwn_forced_changing_suspended_at',
            entity='password.pwn_forced_changing_suspended_at',
            operation='created',
            event='account_modification',
            ip=TEST_IP,
            user_agent='-',
            new=DatetimeNow(convert_to_datetime=True),
            old='-',
        )

    def default_userinfo_response(
        self,
        uid=TEST_UID,
        is_changing_required=False,
        dbfields=None,
        has_password=True,
        password_update_datetime=TEST_PASSWORD_UPDATE_TIMESTAMP,
        enabled_2fa=False,
        forced_changing_reason=PASSWORD_CHANGING_REASON_HACKED,
        **kwargs
    ):
        attributes = {
            'password.update_datetime': password_update_datetime,
            'account.2fa_on': '1' if enabled_2fa else None,
        }
        dbfields = dbfields or {}
        subscribed_to = None
        if is_changing_required:
            subscribed_to = [8]
            dbfields.update({'subscription.login_rule.8': 5})
            attributes['password.forced_changing_reason'] = str(forced_changing_reason)

        account_kwargs = deep_merge(
            dict(
                uid=uid,
                login=TEST_LOGIN,
                subscribed_to=subscribed_to,
                dbfields=dbfields,
                attributes=attributes,
                crypt_password=TEST_PASSWORD_HASH if has_password else None,
            ),
            kwargs,
        )

        return blackbox_userinfo_response(**account_kwargs)

    def set_grants(self, *args):
        prefix, suffix = PASSWORD_OPTIONS_BASE_GRANT.split('.')
        grants = {prefix: [suffix]}
        for grant in args:
            prefix, suffix = grant.split('.')
            grants.setdefault(prefix, []).append(suffix)
        self.env.grants.set_grants_return_value(mock_grants(grants=grants))

    def set_and_serialize_userinfo(self, blackbox_response):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_response,
        )
        self.env.db.serialize(blackbox_response)

    def check_db_ok(
        self, centraldb_query_count=0, sharddb_query_count=0, update_timestamp=None,
        glogout=None, tokens_revoked_at=None, app_passwords_revoked_at=None,
        web_sessions_revoked_at=None, show_2fa_promo=None, is_changing_required=False,
        changing_requirement_reason='1', pwn_forced_changing_suspended_at=None,
    ):
        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_query_count)

        if update_timestamp is not None:
            self.env.db.check(
                self.attributes_table,
                'password.update_datetime',
                str(update_timestamp),
                uid=TEST_UID,
                db='passportdbshard1',
            )
        # проверим модификацию global_logout_datetime и времён отзыва отдельных сущностей
        if glogout:
            self.env.db.check_db_attr(TEST_UID, 'account.global_logout_datetime', glogout)
        else:
            self.env.db.check_db_attr_missing(TEST_UID, 'account.global_logout_datetime')

        if tokens_revoked_at:
            self.env.db.check_db_attr(TEST_UID, 'revoker.tokens', tokens_revoked_at)
        else:
            self.env.db.check_db_attr_missing(TEST_UID, 'revoker.tokens')

        if app_passwords_revoked_at:
            self.env.db.check_db_attr(TEST_UID, 'revoker.app_passwords', app_passwords_revoked_at)
        else:
            self.env.db.check_db_attr_missing(TEST_UID, 'revoker.app_passwords')

        if web_sessions_revoked_at:
            self.env.db.check_db_attr(TEST_UID, 'revoker.web_sessions', web_sessions_revoked_at)
        else:
            self.env.db.check_db_attr_missing(TEST_UID, 'revoker.web_sessions')

        # проверим модификацию is_changing_required
        if is_changing_required:
            self.env.db.check(
                self.attributes_table,
                'password.forced_changing_reason',
                changing_requirement_reason,
                uid=TEST_UID,
                db='passportdbshard1',
            )
        else:
            self.env.db.check_missing(
                self.attributes_table,
                'password.forced_changing_reason',
                uid=TEST_UID,
                db='passportdbshard1',
            )

        if show_2fa_promo:
            self.env.db.check(
                self.attributes_table,
                'account.show_2fa_promo',
                '1',
                uid=TEST_UID,
                db='passportdbshard1',
            )
        else:
            self.env.db.check_missing(
                self.attributes_table,
                'account.show_2fa_promo',
                uid=TEST_UID,
                db='passportdbshard1',
            )

        if pwn_forced_changing_suspended_at:
            self.env.db.check(
                self.attributes_table,
                'password.pwn_forced_changing_suspended_at',
                TimeNow(),
                uid=TEST_UID,
                db='passportdbshard1',
            )
        else:
            self.env.db.check_missing(
                self.attributes_table,
                'password.pwn_forced_changing_suspended_at',
                uid=TEST_UID,
                db='passportdbshard1',
            )

    def check_events_ok(
        self, update_timestamp=None, glogout=None, tokens_revoked_at=None,
        app_passwords_revoked_at=None, web_sessions_revoked_at=None,
        is_changing_required=None, comment=None, admin_name=None, user_agent=None,
        pwn_forced_changing_suspended_at=None,
    ):
        expected_log_entries = {
            'action': 'password',
            'consumer': 'dev',
        }
        if user_agent is not None:
            expected_log_entries['user_agent'] = user_agent
        if update_timestamp is not None:
            expected_log_entries['info.password_update_time'] = str(update_timestamp)
        if glogout is not None:
            expected_log_entries['info.glogout'] = glogout
        if tokens_revoked_at is not None:
            expected_log_entries['info.tokens_revoked'] = tokens_revoked_at
        if app_passwords_revoked_at is not None:
            expected_log_entries['info.app_passwords_revoked'] = app_passwords_revoked_at
        if web_sessions_revoked_at is not None:
            expected_log_entries['info.web_sessions_revoked'] = web_sessions_revoked_at
        if is_changing_required is not None:
            sid8_login_rule = 5 if is_changing_required else 1
            expected_log_entries['sid.login_rule'] = '8|%d' % sid8_login_rule
        if admin_name and comment:
            expected_log_entries['admin'] = admin_name
            expected_log_entries['comment'] = comment
        if pwn_forced_changing_suspended_at is not None:
            expected_log_entries['info.password_pwn_forced_changing_suspension_time'] = pwn_forced_changing_suspended_at
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

        parsed_events = [e._asdict() for e in self.env.event_logger.parse_events()]
        if any([
            glogout is not None,
            tokens_revoked_at is not None,
            app_passwords_revoked_at is not None,
            web_sessions_revoked_at is not None,
        ]):
            eq_(len(parsed_events), 1)
            eq_(parsed_events[0].get('event_type'), 'global_logout')
            actions = parsed_events[0].get('actions', [])
            if glogout is not None:
                ok_({'type': 'global_logout'} in actions)
            if tokens_revoked_at:
                ok_({'type': 'tokens_revoked'} in actions)
            if app_passwords_revoked_at:
                ok_({'type': 'app_passwords_revoked'} in actions)
            if web_sessions_revoked_at:
                ok_({'type': 'web_sessions_revoked'} in actions)

    def test_unknown_uid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(uid=None),
        )

        resp = self.make_request(query_args=dict(global_logout='yes'))
        self.assert_error_response(resp, ['account.not_found'])

    def _assert_wrong_grants_fail(self, missing_grant, **query_kwargs):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)

        grants = list(ALL_GRANTS)
        grants.remove(missing_grant)
        self.set_grants(*grants)

        resp = self.make_request(query_args=query_kwargs)
        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_wrong_grants_global_logout_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_GLOBAL_LOGOUT_GRANT,
            global_logout='yes',
        )

    def test_wrong_grants_revoke_tokens_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_REVOKE_TOKENS_GRANT,
            revoke_tokens='yes',
        )

    def test_wrong_grants_revoke_app_passwords_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_REVOKE_APP_PASSWORDS_GRANT,
            revoke_app_passwords='yes',
        )

    def test_wrong_grants_revoke_web_sessions_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_REVOKE_WEB_SESSIONS_GRANT,
            revoke_web_sessions='yes',
        )

    def test_wrong_grants_is_changing_required_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=PASSWORD_IS_CHANGING_REQUIRED_GRANT,
            is_changing_required='yes',
        )

    def test_wrong_grants_changing_requirement_reason_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=PASSWORD_CHANGING_REQUIREMENT_REASON_GRANT,
            is_changing_required='yes',
            changing_requirement_reason='PASSWORD_CHANGING_REASON_HACKED',
        )

    def test_wrong_grants_update_datetime_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=PASSWORD_UPDATE_DATETIME_GRANT,
            update_timestamp=TEST_TIMESTAMP,
        )

    def test_wrong_grants_show_2fa_promo_fails(self):
        self._assert_wrong_grants_fail(
            missing_grant=ACCOUNT_SHOW_2FA_PROMO_GRANT,
            is_changing_required='yes',
            show_2fa_promo='1',
        )

    def test_global_logout_false_works(self):
        """Указано отрицательное значение global_logout, ничего не происходит"""
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(ACCOUNT_GLOBAL_LOGOUT_GRANT)

        resp = self.make_request(query_args=dict(global_logout='no'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_global_logout_true_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(ACCOUNT_GLOBAL_LOGOUT_GRANT)

        resp = self.make_request(query_args=dict(global_logout='1'))
        self.assert_ok_response(resp)
        now = TimeNow()
        self.check_db_ok(
            sharddb_query_count=1,
            glogout=now,
        )
        self.check_events_ok(glogout=now)

    def test_revoke_tokens_false_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)

        resp = self.make_request(query_args=dict(revoke_tokens='no'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_revoke_tokens_true_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(ACCOUNT_REVOKE_TOKENS_GRANT)

        resp = self.make_request(query_args=dict(revoke_tokens='1'))
        self.assert_ok_response(resp)
        now = TimeNow()
        self.check_db_ok(
            sharddb_query_count=1,
            tokens_revoked_at=now,
        )
        self.check_events_ok(tokens_revoked_at=now)

    def test_revoke_app_passwords_false_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)

        resp = self.make_request(query_args=dict(revoke_app_passwords='no'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_revoke_app_passwords_true_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(ACCOUNT_REVOKE_APP_PASSWORDS_GRANT)

        resp = self.make_request(query_args=dict(revoke_app_passwords='1'))
        self.assert_ok_response(resp)
        now = TimeNow()
        self.check_db_ok(
            sharddb_query_count=1,
            app_passwords_revoked_at=now,
        )
        self.check_events_ok(app_passwords_revoked_at=now)

    def test_revoke_web_sessions_false_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)

        resp = self.make_request(query_args=dict(revoke_web_sessions='no'))
        self.assert_ok_response(resp)
        self.check_db_ok()

    def test_revoke_web_sessions_true_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(ACCOUNT_REVOKE_WEB_SESSIONS_GRANT)

        resp = self.make_request(query_args=dict(revoke_web_sessions='1'))
        self.assert_ok_response(resp)
        now = TimeNow()
        self.check_db_ok(
            sharddb_query_count=1,
            web_sessions_revoked_at=now,
        )
        self.check_events_ok(web_sessions_revoked_at=now)

    def test_update_timestamp_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_UPDATE_DATETIME_GRANT)

        resp = self.make_request(query_args=dict(update_timestamp=TEST_TIMESTAMP))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            update_timestamp=TEST_TIMESTAMP,
        )
        self.check_events_ok(update_timestamp=TEST_TIMESTAMP)

    def test_is_changing_required_false_works(self):
        """Снятие 3-го бита работает"""
        userinfo_response = self.default_userinfo_response(is_changing_required=True)
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_changing_required='no'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_changing_required=False,
        )
        self.check_events_ok(is_changing_required=False)

    def test_is_changing_required_true_works(self):
        """Установка 3-го бита работает"""
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_changing_required='1'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_changing_required=True,
        )
        self.check_events_ok(is_changing_required=True)

    def test_changing_requirement_reason_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT, PASSWORD_CHANGING_REQUIREMENT_REASON_GRANT)

        resp = self.make_request(query_args=dict(
            is_changing_required='1',
            changing_requirement_reason='PASSWORD_CHANGING_REASON_PWNED',
        ))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_changing_required=True,
            changing_requirement_reason=str(PASSWORD_CHANGING_REASON_PWNED),
        )
        self.check_events_ok(is_changing_required=True)

    def test_all_options_at_once_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(
            PASSWORD_IS_CHANGING_REQUIRED_GRANT,
            ACCOUNT_GLOBAL_LOGOUT_GRANT,
            PASSWORD_UPDATE_DATETIME_GRANT,
        )

        resp = self.make_request(query_args=dict(
            is_changing_required='1',
            update_timestamp=TEST_TIMESTAMP,
            global_logout='yes',
        ))
        self.assert_ok_response(resp)
        updated_fields = {
            'is_changing_required': True,
            'glogout': TimeNow(),
            'update_timestamp': TEST_TIMESTAMP,
        }
        self.check_db_ok(
            sharddb_query_count=1,
            **updated_fields
        )
        self.check_events_ok(**updated_fields)

    def test_update_timestamp_without_comment_works(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_UPDATE_DATETIME_GRANT)

        resp = self.make_request(query_args=dict(update_timestamp=TEST_TIMESTAMP))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            update_timestamp=TEST_TIMESTAMP,
        )
        self.check_events_ok(update_timestamp=TEST_TIMESTAMP, comment='-')

    def test_event_with_admin_name_and_comment__logged(self):
        userinfo_response = self.default_userinfo_response()
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_UPDATE_DATETIME_GRANT, LOG_ADMIN_ACTION_GRANT)

        resp = self.make_request(query_args=dict(
            update_timestamp=TEST_TIMESTAMP,
            admin_name=TEST_ADMIN_LOGIN,
            comment=TEST_COMMENT,
        ))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            update_timestamp=TEST_TIMESTAMP,
        )
        self.check_events_ok(
            update_timestamp=TEST_TIMESTAMP,
            admin_name=TEST_ADMIN_LOGIN,
            comment=TEST_COMMENT,
        )

    def test_too_frequent_password_change__error(self):
        today_ts = int(time.mktime(date.today().timetuple()))
        userinfo_response = self.default_userinfo_response(
            password_update_datetime=str(today_ts),  # Пароль уже меняли сегодня
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(
            is_changing_required='1',
            max_change_frequency_in_days=7,  # Менять пароль не чаще раза в неделю
        ))
        self.assert_error_response(resp, ['password.too_frequent_change'])
        self.check_db_ok(
            sharddb_query_count=0,
            is_changing_required=False,
            update_timestamp=today_ts,
        )

    def test_is_changing_required_true_works_when_reg_date_eq_update_psswd_date(self):
        today = date.today()
        today_ts = int(time.mktime(today.timetuple()))
        userinfo_response = self.default_userinfo_response(
            dbfields={
                'userinfo.reg_date.uid': today.strftime(DEFAULT_FORMAT),
            },
            password_update_datetime=str(today_ts),
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(
            query_args=dict(
                is_changing_required='1',
                max_change_frequency_in_days=7,  # Менять пароль не чаще раза в неделю
            ),
        )
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_changing_required=True,
        )
        self.check_events_ok(is_changing_required=True)

    def test_already_has_is_changing_required_flag__error(self):
        userinfo_response = self.default_userinfo_response(is_changing_required=True)
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_changing_required='1'))
        self.assert_error_response(resp, ['action.not_required'])
        self.check_db_ok(
            sharddb_query_count=0,
            is_changing_required=True,
        )

    def test_param_max_frequent_password_change__ok(self):
        N_days = 7
        week_ago = int(time.time()) - 60 * 60 * 24 * N_days - 1  # -1 чтоб наверняка
        userinfo_response = self.default_userinfo_response(
            password_update_datetime=str(week_ago),
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(
            is_changing_required='1',
            max_change_frequency_in_days=7,
        ))
        self.assert_ok_response(resp)
        self.check_db_ok(sharddb_query_count=1, is_changing_required=True)
        self.check_events_ok(is_changing_required=True)

    def test_param_max_frequent_password_change_account_without_password_update_datetime__ok(self):
        userinfo_response = self.default_userinfo_response(
            password_update_datetime=None,
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(
            is_changing_required='1',
            max_change_frequency_in_days=7,
        ))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            update_timestamp=None,
            is_changing_required=True,
        )
        self.check_events_ok(is_changing_required=True)

    def test_max_frequent_password_change_no_changing_required__max_freq_ignored(self):
        now = int(time.time())
        userinfo_response = self.default_userinfo_response(
            password_update_datetime=now,
            is_changing_required=True,
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(
            is_changing_required='no',
            max_change_frequency_in_days=7,
        ))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            update_timestamp=now,
            is_changing_required=False,
        )
        self.check_events_ok(is_changing_required=False)

    def test_2fa_password_change_nonsense(self):
        """
        При включенной 2FA направление на принудительную смену пароля не имеет смысла.
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(enabled_2fa=True),
        )

        resp = self.make_request(query_args=dict(is_changing_required='yes'))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_no_password_password_change_nonsense(self):
        """
        При отсутствии пароля направление на принудительную смену пароля не имеет смысла.
        """
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            self.default_userinfo_response(has_password=False),
        )

        resp = self.make_request(query_args=dict(is_changing_required='yes'))
        self.assert_error_response(resp, ['account.invalid_type'])

    def test_no_password_but_can_cancel_password_change(self):
        """
        Даже если пароля нет, принудительную смену пароля можно отменить.
        """
        userinfo_response = self.default_userinfo_response(is_changing_required=True, has_password=False)
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_changing_required='no'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=1,
            is_changing_required=False,
        )
        self.check_events_ok(is_changing_required=False)

    def test_show_2fa_promo__ok(self):
        self.set_and_serialize_userinfo(self.default_userinfo_response())
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT, ACCOUNT_SHOW_2FA_PROMO_GRANT)

        resp = self.make_request(query_args=dict(
            is_changing_required='1',
            show_2fa_promo='1',
        ))
        self.assert_ok_response(resp)
        self.check_db_ok(
            is_changing_required=True,
            show_2fa_promo=True,
            sharddb_query_count=1,
        )

    def test_show_2fa_promo_unset__ok(self):
        bb_response = blackbox_userinfo_response(
            uid=TEST_UID,
            login=TEST_LOGIN,
            subscribed_to=[8],
            dbfields={},
            attributes={
                'password.update_datetime': TEST_PASSWORD_UPDATE_TIMESTAMP,
                'account.show_2fa_promo': '1',
            },
            crypt_password=TEST_PASSWORD_HASH,
        )
        self.set_and_serialize_userinfo(bb_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT, ACCOUNT_SHOW_2FA_PROMO_GRANT)

        resp = self.make_request(query_args=dict(
            is_changing_required='1',
            show_2fa_promo='0',
        ))
        self.assert_ok_response(resp)
        self.check_db_ok(
            is_changing_required=True,
            show_2fa_promo=False,
            sharddb_query_count=2,
        )

    def test_sms_sent_to_secure_number(self):
        phone_secured = build_phone_secured(
            1,
            DEFAULT_PHONE_NUMBER,
            is_default=False,
        )
        userinfo_response = self.default_userinfo_response(**phone_secured)
        self.set_and_serialize_userinfo(userinfo_response)
        self.env.yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_changing_required='1', notify_by_sms='1'), headers=dict(user_agent=TEST_USER_AGENT))

        self.assert_ok_response(resp, notifications={'is_sms_sent': True})
        self.check_db_ok(sharddb_query_count=1, is_changing_required=True)
        self.check_events_ok(is_changing_required=True, user_agent=TEST_USER_AGENT)

        requests = self.env.yasms.requests
        eq_(len(requests), 1)  # Один раз отправили sms

        requests[0].assert_query_contains({
            'phone': DEFAULT_PHONE_NUMBER,
            'caller': 'dev',
            'identity': 'password_options.notify',
        })

        self.env.blackbox.requests[0].assert_post_data_contains({
            'getphones': 'all',
            'getphoneoperations': '1',
            'getphonebindings': 'all',
            'aliases': 'all_with_hidden',
        })

        self.env.blackbox.requests[0].assert_contains_attributes({
            'phones.default',
            'phones.secure',
        })
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('is_changing_required', user_agent=TEST_USER_AGENT),
            self.env.statbox.entry('notification_sent'),
        ])

    def test_unset_pwned_changing_requirement_suspend(self):
        """
        При снятии pwned требования на смену пароля даём индульгенцию.
        """
        userinfo_response = self.default_userinfo_response(
            is_changing_required=True,
            forced_changing_reason=PASSWORD_CHANGING_REASON_PWNED,
        )
        self.set_and_serialize_userinfo(userinfo_response)
        self.set_grants(PASSWORD_IS_CHANGING_REQUIRED_GRANT)

        resp = self.make_request(query_args=dict(is_changing_required='no'))
        self.assert_ok_response(resp)
        self.check_db_ok(
            sharddb_query_count=2,
            is_changing_required=False,
            pwn_forced_changing_suspended_at=True,
        )
        self.check_events_ok(
            is_changing_required=False,
            pwn_forced_changing_suspended_at=TimeNow(),
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('is_not_changing_required', old=PASSWORD_CHANGING_REASON_PWNED),
            self.env.statbox.entry('pwn_forced_changing_suspended_at'),
        ])
