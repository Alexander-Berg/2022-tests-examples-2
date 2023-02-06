# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.adm_api.test.mock_objects import (
    mock_grants,
    mock_headers,
)
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import (
    BaseViewTestCase,
    ViewsTestEnvironment,
)
from passport.backend.adm_api.tests.views.restore.data import *
from passport.backend.adm_api.views.restore.helpers import format_timestamp
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.historydb_api import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_failed_item,
    auths_failed_response,
    event_item,
    event_restore_item,
    events_response,
    events_restore_response,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ATT
from passport.backend.core.historydb.analyzer.event_handlers.account_state import (
    ACCOUNT_STATUS_DELETED,
    ACCOUNT_STATUS_DELETED_BY_SUPPORT,
    ACCOUNT_STATUS_DISABLED,
    ACCOUNT_STATUS_DISABLED_ON_DELETE,
    ACCOUNT_STATUS_LIVE,
    ACCOUNT_STATUS_LIVE_UNBLOCKED,
)
from passport.backend.core.historydb.events import *


@with_settings_hosts()
class RestoreAccountStateViewTestCase(BaseViewTestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='admin'))
        self.env.grants_loader.set_grants_json(mock_grants())

        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[]),
        )
        self.env.historydb_api.set_response_value(
            'auths_failed',
            auths_failed_response(uid=TEST_UID, auths=[]),
        )

    def tearDown(self):
        self.env.stop()

    def make_request(self, restore_id=TEST_RESTORE_ID, uid=None, headers=None):
        if uid is None:
            query = dict(consumer='dev', restore_id=restore_id)
        else:
            query = dict(consumer='dev', uid=uid)
        return self.env.client.get(
            '/1/restore/account_state/',
            query_string=query,
            headers=headers,
        )

    def get_headers(self, cookie=TEST_COOKIE, host=TEST_HOST, ip=TEST_IP):
        return mock_headers(cookie=cookie, host=host, user_ip=ip)

    def get_event_restore_item(self, restore_id, ts, contact_email):
        return event_restore_item(
            restore_id=restore_id,
            timestamp=ts,
            data_json=json.dumps({'request_info': {'contact_email': contact_email}}),
        )

    def check_response_ok(self, resp, uid=TEST_UID, login=TEST_LOGIN, account_type='normal', same_login_history=None,
                          non_natural_aliases=None, non_natural_removed_aliases=None, incomplete_password_changing=None,
                          account_history_status=ACCOUNT_STATUS_LIVE, account_status_consistent=True,
                          account_blackbox_status=ACCOUNT_STATUS_LIVE, yastaff_login=None,
                          have_password=False, is_2fa_enabled=False, karma_status=0, blocking_sids=None,
                          karma_events=None, history_action_user_ip=None, history_action_timestamp=None,
                          history_action_admin=None, history_action_comment=None, other_restore_events=None,
                          challenge_shown=None):
        account_options = {'status': account_blackbox_status}
        if yastaff_login is not None:
            account_options['yastaff_login'] = yastaff_login
        if account_blackbox_status != ACCOUNT_STATUS_DELETED:
            blocking_sids = blocking_sids or []
            account_options.update({
                'have_password': have_password,
                'is_2fa_enabled': is_2fa_enabled,
                'karma_status': karma_status,
                'blocking_sids': blocking_sids,
            })
        karma_events = karma_events or []
        account_history_status_values = {
            'status': account_history_status,
            'karma_events': karma_events,
        }
        if history_action_user_ip is not None:
            account_history_status_values['user_ip'] = history_action_user_ip
        if history_action_timestamp is not None:
            account_history_status_values['timestamp'] = history_action_timestamp
            account_history_status_values['datetime'] = format_timestamp(history_action_timestamp)
        if history_action_admin is not None:
            account_history_status_values['admin'] = history_action_admin
            account_history_status_values['comment'] = history_action_comment
        super(RestoreAccountStateViewTestCase, self).check_response_ok(
            resp,
            uid=uid,
            login=login,
            type=account_type,
            same_login_history=same_login_history or [],
            non_natural_aliases=non_natural_aliases or {},
            non_natural_removed_aliases=non_natural_removed_aliases or {},
            incomplete_password_changing=incomplete_password_changing,
            account_status_consistent=account_status_consistent,
            account_options=account_options,
            account_history_status=account_history_status_values,
            other_restore_events=other_restore_events or [],
            challenge_shown=challenge_shown,
        )

    def check_db_ok(self, centraldb_query_count=2, sharddb_query_count=0):
        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_query_count)

    def set_userinfo_response(self, uid=TEST_UID, login=TEST_LOGIN, aliases=None, alias_type='portal',
                              subscribed_to=None, **extra_args):
        aliases = aliases or {}
        if not aliases:
            aliases[alias_type] = login
        subscribed_to = subscribed_to or []
        params = {'login': login, 'uid': uid, 'aliases': aliases}
        if subscribed_to:
            params.update(subscribed_to=subscribed_to)
        params.update(extra_args)

        self.env.blackbox.set_response_value('userinfo', blackbox_userinfo_response(**params))

    def set_removed_aliases(self, uid=TEST_UID, aliases=None):
        aliases = aliases or {}
        for alias_name, aliases_list in aliases.items():
            for alias in aliases_list:
                self.env.db.insert(
                    'removed_aliases',
                    db='passportdbcentral',
                    uid=uid,
                    type=ATT[alias_name],
                    value=alias,
                )

    def test_no_headers(self):
        resp = self.make_request(restore_id=TEST_RESTORE_ID_2)
        self.check_response_error(resp, ['ip.empty', 'cookie.empty', 'host.empty'])
        self.check_db_ok(centraldb_query_count=0)

    def test_no_grants(self):
        self.env.blackbox.set_response_value('sessionid', blackbox_sessionid_response(login='looser'))
        resp = self.make_request(uid=TEST_UID, headers=self.get_headers())
        self.check_response_error(resp, ['access.denied'])
        self.check_db_ok(centraldb_query_count=0)

    def test_historydb_api_failed(self):
        self.set_userinfo_response()
        self.env.historydb_api.set_response_side_effect('events', HistoryDBApiTemporaryError)

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_error(resp, ['backend.historydb_api_failed'])
        self.check_db_ok()

    def test_live_account_in_blackbox(self):
        self.set_userinfo_response()
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp)
        self.check_db_ok()

    def test_live_account_natural_and_extra_aliases(self):
        natural_aliases = dict(
            portal=TEST_LOGIN,
            narodmail=TEST_LOGIN,
            social=TEST_SOCIAL_ALIAS,
            altdomain=TEST_GALATASARAY_ALIAS,
            phonenumber=TEST_PHONE_ALIAS,
        )
        self.set_userinfo_response(aliases=natural_aliases)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, non_natural_aliases={})
        self.check_db_ok()

    def test_live_account_non_natural_aliases(self):
        non_natural_aliases = dict(mail='mail_alias', narodmail='narodmail_alias')
        self.set_userinfo_response(aliases=dict(non_natural_aliases, portal=TEST_LOGIN))
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, non_natural_aliases=non_natural_aliases)
        self.check_db_ok()

    def test_live_account_not_normalized_login_with_alias(self):
        """Ненормализованный логин и алиас, содержащий нормализованный логин"""
        self.set_userinfo_response(
            display_login=TEST_LOGIN_NOT_NORMALIZED,
            aliases={'mail': TEST_LOGIN, 'portal': TEST_LOGIN},
        )
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, login=TEST_LOGIN_NOT_NORMALIZED)
        self.check_db_ok()

    def test_live_account_yandexoid_alias(self):
        aliases = dict(yandexoid=TEST_YANDEXOID_ALIAS, portal=TEST_LOGIN)
        self.set_userinfo_response(aliases=aliases)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, yastaff_login=TEST_YANDEXOID_ALIAS)
        self.check_db_ok()

    def test_live_account_lite_alias(self):
        aliases = dict(lite=TEST_LITE_ALIAS)
        self.set_userinfo_response(login=TEST_LITE_ALIAS, aliases=aliases)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, login=TEST_LITE_ALIAS, account_type='lite')
        self.check_db_ok()

    def test_live_account_phonish_alias(self):
        aliases = dict(phonish=TEST_PHONISH_ALIAS)
        self.set_userinfo_response(login=TEST_PHONISH_ALIAS, aliases=aliases)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, login=TEST_PHONISH_ALIAS, account_type='phonish')
        self.check_db_ok()

    def test_live_account_pdd_alias(self):
        aliases = dict(pdd=TEST_PDD_ALIAS, pddalias=TEST_PDD_ALIAS_2)
        self.set_userinfo_response(uid=TEST_PDD_UID, login=TEST_PDD_LOGIN, aliases=aliases)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(uid=TEST_PDD_UID, headers=self.get_headers())
        self.check_response_ok(resp, uid=TEST_PDD_UID, login=TEST_PDD_ALIAS, account_type='pdd')
        self.check_db_ok()

    def test_live_account_non_natural_removed_aliases(self):
        non_natural_removed_aliases = dict(
            mail=['mail_alias', 'mail_alias_2'],
            narodmail=['narodmail_alias'],
        )
        removed_aliases_with_phonenumber = dict(non_natural_removed_aliases, phonenumber=[TEST_PHONE_ALIAS])
        self.set_userinfo_response()
        self.set_removed_aliases(aliases=removed_aliases_with_phonenumber)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, non_natural_removed_aliases=non_natural_removed_aliases)
        self.check_db_ok()

    def test_live_account_with_blocking_sids_and_password(self):
        self.set_userinfo_response(subscribed_to=[24], crypt_password=TEST_CRYPT_PASSWORD)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, blocking_sids=['24 (partner)'], have_password=True)
        self.check_db_ok()

    def test_live_account_with_2fa(self):
        self.set_userinfo_response(attributes={'account.2fa_on': True})
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, have_password=True, is_2fa_enabled=True)
        self.check_db_ok()

    def test_live_account_with_incomplete_password_changing(self):
        self.set_userinfo_response(crypt_password=TEST_CRYPT_PASSWORD)
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_CHANGE_PASSWORD),
                event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|1'),
                event_item(timestamp=2, name=EVENT_ACTION, value=ACTION_ACCOUNT_PASSWORD, admin='alexco', comment='broken'),
                event_item(timestamp=2, name=EVENT_SID_LOGIN_RULE, value='8|5'),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            have_password=True,
            incomplete_password_changing={
                u'comment': u'broken',
                u'admin': u'alexco',
                u'timestamp': 2,
                u'datetime': DATETIME_FOR_TS_2,
                u'change_required': True,
            },
        )
        self.check_db_ok()

    def test_live_account_with_incomplete_password_changing_aborted(self):
        self.set_userinfo_response(crypt_password=TEST_CRYPT_PASSWORD)
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_PASSWORD, admin='alexco', comment='broken'),
                event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|5'),
                event_item(timestamp=2, name=EVENT_ACTION, value=ACTION_ACCOUNT_PASSWORD, admin='alexco', comment='not broken'),
                event_item(timestamp=2, name=EVENT_SID_LOGIN_RULE, value='8|1'),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, have_password=True, incomplete_password_changing=None)
        self.check_db_ok()

    def test_live_account_with_incomplete_password_changing_completed(self):
        self.set_userinfo_response(crypt_password=TEST_CRYPT_PASSWORD)
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_PASSWORD, admin='alexco', comment='broken'),
                event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|5'),
                event_item(timestamp=2, name=EVENT_ACTION, value=ACTION_ACCOUNT_CHANGE_PASSWORD),
                event_item(timestamp=2, name=EVENT_SID_LOGIN_RULE, value='8|1'),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, have_password=True, incomplete_password_changing=None)
        self.check_db_ok()

    def test_account_status_inconsistent_blocked_but_live_in_history(self):
        self.set_userinfo_response(enabled=False)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(resp, account_blackbox_status=ACCOUNT_STATUS_DISABLED, account_status_consistent=False)
        self.check_db_ok()

    def test_account_status_consisted_blocked_and_blocked_on_delete_in_history(self):
        self.set_userinfo_response(enabled=False, subscribed_to=[14])
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                # Срез событий, пишущихся при регистрации
                event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
                event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
                event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
                event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
                # Блокировка при удалении пользователем
                event_item(timestamp=5, name=EVENT_ACTION, value=ACTION_ACCOUNT_DELETE, user_ip=TEST_IP),
                event_item(timestamp=5, name=EVENT_INFO_ENA, value='0'),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            account_blackbox_status=ACCOUNT_STATUS_DISABLED,
            account_history_status=ACCOUNT_STATUS_DISABLED_ON_DELETE,
            blocking_sids=['14 (slova)'],
            karma_events=[
                {u'comment': None, u'admin': None, u'karma': 0, u'timestamp': 1, u'datetime': DATETIME_FOR_TS_1},
                {u'comment': None, u'admin': None, u'timestamp': 1, u'karma_prefix': 0, u'datetime': DATETIME_FOR_TS_1},
            ],
            history_action_user_ip=TEST_IP,
            history_action_timestamp=5,
        )
        self.check_db_ok()

    def test_account_status_inconsistent_live_and_deleted_by_support_in_history(self):
        self.set_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                # Срез событий, пишущихся при регистрации
                event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
                event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
                event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
                event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
                # Удален саппортом
                event_item(timestamp=5, name=EVENT_ACTION, value=ACTION_ACCOUNT_DELETE, admin='support', user_ip=TEST_IP),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            account_history_status=ACCOUNT_STATUS_DELETED_BY_SUPPORT,
            karma_events=[
                {u'comment': None, u'admin': None, u'karma': 0, u'timestamp': 1, u'datetime': DATETIME_FOR_TS_1},
                {u'comment': None, u'admin': None, u'timestamp': 1, u'karma_prefix': 0, u'datetime': DATETIME_FOR_TS_1},
            ],
            history_action_user_ip=TEST_IP,
            history_action_timestamp=5,
            history_action_admin='support',
            account_status_consistent=False,
        )
        self.check_db_ok()

    def test_account_status_consistent_live_and_live_unblocked(self):
        self.set_userinfo_response()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                # Срез событий, пишущихся при регистрации
                event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
                event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
                event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
                event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
                # Очернение, блокировка саппортом
                event_item(timestamp=2, name=EVENT_INFO_KARMA_PREFIX, value='1', admin='alexco', comment='spammer'),
                event_item(timestamp=3, name=EVENT_INFO_ENA, value='0', admin='alexco', comment='disable spammer'),
                # Обеление, разблокировка
                event_item(timestamp=4, name=EVENT_INFO_ENA, value='1', admin='support', comment='enable spammer', user_ip=TEST_IP),
                event_item(timestamp=4, name=EVENT_INFO_KARMA_PREFIX, value='2', admin='support', comment='enable spammer'),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            account_history_status=ACCOUNT_STATUS_LIVE_UNBLOCKED,
            karma_events=[
                {u'comment': None, u'admin': None, u'karma': 0, u'timestamp': 1, u'datetime': DATETIME_FOR_TS_1},
                {u'comment': None, u'admin': None, u'timestamp': 1, u'karma_prefix': 0, u'datetime': DATETIME_FOR_TS_1},
                {u'comment': 'spammer', u'admin': 'alexco', u'timestamp': 2, u'karma_prefix': 1, u'datetime': DATETIME_FOR_TS_2},
                {u'comment': 'enable spammer', u'admin': 'support', u'timestamp': 4, u'karma_prefix': 2, u'datetime': DATETIME_FOR_TS_4},
            ],
            history_action_user_ip=TEST_IP,
            history_action_timestamp=4,
            history_action_admin='support',
            history_action_comment='enable spammer',
        )
        self.check_db_ok()

    def test_account_not_found_anywhere(self):
        self.set_userinfo_response(uid=None)
        self.env.historydb_api.set_response_value('events', events_response(events=[]))

        resp = self.make_request(restore_id=TEST_RESTORE_ID_2, headers=self.get_headers())
        self.check_response_error(resp, ['account.not_found'])
        self.check_db_ok(centraldb_query_count=1)

    def test_deleted_account_found_in_removed_aliases(self):
        removed_aliases = dict(
            portal=[TEST_LOGIN],
            phonenumber=[TEST_PHONE_ALIAS]
        )
        self.set_userinfo_response(uid=None)
        self.set_removed_aliases(aliases=removed_aliases)
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[
                # Срез событий, пишущихся при регистрации
                event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
                event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
                event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
                event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
                # Удален саппортом
                event_item(timestamp=5, name=EVENT_ACTION, value=ACTION_ACCOUNT_DELETE, admin='support', user_ip=TEST_IP),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            account_blackbox_status=ACCOUNT_STATUS_DELETED,
            account_history_status=ACCOUNT_STATUS_DELETED_BY_SUPPORT,
            karma_events=[
                {u'comment': None, u'admin': None, u'karma': 0, u'timestamp': 1, u'datetime': DATETIME_FOR_TS_1},
                {u'comment': None, u'admin': None, u'timestamp': 1, u'karma_prefix': 0, u'datetime': DATETIME_FOR_TS_1},
            ],
            history_action_user_ip=TEST_IP,
            history_action_timestamp=5,
            history_action_admin='support',
        )
        self.check_db_ok()

    def test_same_login_history_pdd_lite(self):
        removed_aliases_1 = dict(
            pdd=[TEST_PDD_ALIAS_ENCODED],
            pddalias=[TEST_PDD_ALIAS_2_ENCODED],
            phonenumber=[TEST_PHONE_ALIAS],
        )
        self.set_removed_aliases(uid=TEST_PDD_UID, aliases=removed_aliases_1)
        removed_aliases_2 = dict(
            lite=[TEST_PDD_ALIAS_ENCODED_AS_LITE],
            social=[TEST_SOCIAL_ALIAS],
        )
        self.set_removed_aliases(aliases=removed_aliases_2)
        self.set_userinfo_response(uid=TEST_PDD_UID, login=TEST_PDD_LOGIN, alias_type='pdd')
        self.env.historydb_api.set_response_side_effect(
            'events',
            [
                events_response(events=[  # Вызов для найденного аккаунта с таким же логином
                    event_item(
                        name=EVENT_ACTION,
                        timestamp=1,
                        value=ACTION_ACCOUNT_CREATE_PREFIX,
                        user_ip=TEST_IP,
                    ),
                    event_item(
                        timestamp=2,
                        name=EVENT_ACTION,
                        value=ACTION_ACCOUNT_DELETE,
                        user_ip=TEST_IP,
                    ),
                ]),
                events_response(events=[]),  # Вызов для основного аккаунта
            ],
        )

        resp = self.make_request(uid=TEST_PDD_UID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            uid=TEST_PDD_UID,
            login=TEST_PDD_ALIAS,
            account_type='pdd',
            same_login_history=[
                {
                    u'uid': TEST_UID,
                    u'created': {u'user_ip': TEST_IP, u'timestamp': 1, u'datetime': DATETIME_FOR_TS_1},
                    u'deleted': {u'user_ip': TEST_IP, u'timestamp': 2, u'datetime': DATETIME_FOR_TS_2},
                },
            ],
        )
        self.check_db_ok()

    def test_other_restore_events_by_uid(self):
        self.set_userinfo_response()
        self.env.historydb_api.set_response_value('events', events_response(events=[]))
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                self.get_event_restore_item(restore_id=TEST_RESTORE_ID_2, ts=200, contact_email='2@test.ru'),
                self.get_event_restore_item(restore_id=TEST_RESTORE_ID, ts=100, contact_email='1@test.ru'),
            ]),
        )

        resp = self.make_request(uid=TEST_UID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            other_restore_events=[
                {
                    'restore_id': TEST_RESTORE_ID_2,
                    'contact_email': '2@test.ru',
                    'timestamp': 200,
                    'datetime': '1970-01-01 03:03:20',
                },
                {
                    'restore_id': TEST_RESTORE_ID,
                    'contact_email': '1@test.ru',
                    'timestamp': 100,
                    'datetime': '1970-01-01 03:01:40',
                },
            ],
        )
        self.check_db_ok()

    def test_other_restore_events_by_restore_id(self):
        self.set_userinfo_response()
        self.env.historydb_api.set_response_value('events', events_response(events=[]))
        self.env.historydb_api.set_response_value(
            'events_restore',
            events_restore_response(restore_events=[
                self.get_event_restore_item(restore_id=TEST_RESTORE_ID_2, ts=200, contact_email='2@test.ru'),
                self.get_event_restore_item(restore_id=TEST_RESTORE_ID, ts=100, contact_email='1@test.ru'),
            ]),
        )

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            other_restore_events=[
                {
                    'restore_id': TEST_RESTORE_ID_2,
                    'contact_email': '2@test.ru',
                    'timestamp': 200,
                    'datetime': '1970-01-01 03:03:20',
                },
            ],
        )
        self.check_db_ok()

    def test_with_challenge(self):
        self.set_userinfo_response()
        self.env.historydb_api.set_response_value('events', events_response(events=[]))
        self.env.historydb_api.set_response_value('auths_failed', auths_failed_response(
            uid=TEST_UID,
            auths=[
                auth_failed_item(timestamp=100500, status='challenge_shown'),
                auth_failed_item(timestamp=100501, status='challenge_shown'),
            ],
        ))

        resp = self.make_request(restore_id=TEST_RESTORE_ID, headers=self.get_headers())
        self.check_response_ok(
            resp,
            challenge_shown={
                'user_ip': '87.250.235.4',
                'timestamp': 100501,
                'datetime': '1970-01-02 06:55:01 MSK+0300',
            },
        )
        self.check_db_ok()
