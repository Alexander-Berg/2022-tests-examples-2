# -*- coding: utf-8 -*-

from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
)
from passport.backend.core.historydb.analyzer.event_handlers.account_state import (
    ACCOUNT_STATUS_DELETED,
    ACCOUNT_STATUS_DELETED_BY_SUPPORT,
    ACCOUNT_STATUS_DISABLED,
    ACCOUNT_STATUS_DISABLED_ON_DELETE,
    ACCOUNT_STATUS_LIVE,
    ACCOUNT_STATUS_LIVE_UNBLOCKED,
)
from passport.backend.core.historydb.events import (
    ACTION_ACCOUNT_CHANGE_PASSWORD,
    ACTION_ACCOUNT_CREATE_PREFIX,
    ACTION_ACCOUNT_DELETE,
    ACTION_ACCOUNT_REGISTER_PREFIX,
    ACTION_RESTORE_SUPPORT_LINK_CREATED,
    EVENT_ACTION,
    EVENT_INFO_ENA,
    EVENT_INFO_FIRSTNAME,
    EVENT_INFO_HINTA,
    EVENT_INFO_HINTQ,
    EVENT_INFO_KARMA,
    EVENT_INFO_KARMA_PREFIX,
    EVENT_USER_AGENT,
    EVENT_USERINFO_FT,
)
from passport.backend.core.test.test_utils import with_settings_hosts

from ..data import (
    TEST_IP,
    TEST_USER_AGENT,
    TranslationSettings,
)
from ..test_events import BaseEventsAnalyzerTestCase


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class RegistrationEnvAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_registration_env_userinfo_ft_user_ip_events(self):
        response = [
            event_item(user_ip=TEST_IP, name=EVENT_USERINFO_FT, timestamp=1),
            event_item(user_ip=None, name=EVENT_USERINFO_FT, timestamp=1),
            event_item(user_ip=TEST_IP, name=EVENT_USERINFO_FT, timestamp=1),
            event_item(user_ip='', name=EVENT_USERINFO_FT, timestamp=1),
            event_item(user_ip=TEST_IP, name=EVENT_USERINFO_FT, timestamp=1),
        ]

        info = self.load_and_analyze_events(registration_env=True, events=response)
        self.assert_events_info_ok(
            info,
            registration_env=events_info_interval_point(),
        )

    def test_registration_env_mixed_info_firstname_userinfo_ft_events(self):
        response = [
            event_item(user_ip=TEST_IP, firstname=u'вася', name=EVENT_USERINFO_FT, timestamp=1),
            event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT, timestamp=1),
            event_item(name=EVENT_INFO_FIRSTNAME, value=u'петя'),
        ]

        info = self.load_and_analyze_events(names=True, registration_env=True, events=response)
        self.assert_events_info_ok(
            info,
            firstnames=[u'вася', u'петя'],
            registration_env=events_info_interval_point(user_agent=TEST_USER_AGENT),
        )

    def test_registration_env_registration_events_repaired(self):
        response = [
            event_item(user_ip=TEST_IP, firstname=u'вася', name=EVENT_USERINFO_FT, timestamp=1),
            event_item(name=EVENT_USER_AGENT, value=TEST_USER_AGENT, timestamp=1.1),
            event_item(name=EVENT_INFO_FIRSTNAME, value=u'петя', timestamp=1.2),
            event_item(name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX, timestamp=1.2, user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(registration_env=True, events=response)
        self.assert_events_info_ok(
            info,
            registration_env=events_info_interval_point(user_agent=TEST_USER_AGENT),
        )

    def test_registration_env_from_action(self):
        response = [
            event_item(name=EVENT_ACTION, value='some action', user_ip='2.2.2.2', timestamp=1),
            event_item(name=EVENT_ACTION, value='account_create', user_ip=TEST_IP, timestamp=2),
        ]

        info = self.load_and_analyze_events(registration_env=True, events=response)
        self.assert_events_info_ok(
            info,
            registration_env=events_info_interval_point(timestamp=2),
        )

    def test_registration_env_multiple_registration_envs(self):
        response = [
            event_item(name=EVENT_ACTION, timestamp=1, value='account_create', user_ip=TEST_IP),
            event_item(name=EVENT_USERINFO_FT, timestamp=2, user_ip='3.3.3.3'),
        ]

        info = self.load_and_analyze_events(registration_env=True, events=response)
        self.assert_events_info_ok(
            info,
            registration_env=events_info_interval_point(timestamp=1),
        )


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class AccountCreateDeleteAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_account_create_delete_only_userinfo_ft(self):
        create_event = event_item(
            name=EVENT_USERINFO_FT,
            timestamp=1,
            hintq='99:q',
            hinta='answer',
            user_ip=TEST_IP,
        )
        response = [create_event]

        info = self.load_and_analyze_events(account_create_delete_events=True, events=response)
        self.assert_events_info_ok(
            info,
            account_create_event=create_event,
            account_delete_event=None,
        )

    def test_account_create_delete_registration_events_repair(self):
        create_event_userinfo_ft = event_item(
            name=EVENT_USERINFO_FT,
            timestamp=1,
            hintq='99:q',
            hinta='answer',
            user_ip=TEST_IP,
        )
        create_event = event_item(name=EVENT_ACTION, timestamp=1.1, value=ACTION_ACCOUNT_CREATE_PREFIX)
        response = [
            create_event_userinfo_ft,
            event_item(name=EVENT_INFO_HINTA, value='answer', timestamp=1.1),
            event_item(name=EVENT_INFO_HINTQ, value='99:q', timestamp=1.1),
            create_event,
        ]

        info = self.load_and_analyze_events(account_create_delete_events=True, events=response)
        self.assert_events_info_ok(
            info,
            account_create_event=dict(create_event, timestamp=1),
            account_delete_event=None,
        )

    def test_account_create_delete_both_events(self):
        create_event = event_item(
            name=EVENT_ACTION,
            timestamp=1,
            value=ACTION_ACCOUNT_CREATE_PREFIX,
        )
        delete_event = event_item(
            timestamp=2,
            name=EVENT_ACTION,
            value=ACTION_ACCOUNT_DELETE,
        )
        response = [
            create_event,
            event_item(name=EVENT_ACTION, value=ACTION_ACCOUNT_CHANGE_PASSWORD, timestamp=2),
            delete_event,
        ]

        info = self.load_and_analyze_events(account_create_delete_events=True, events=response)
        self.assert_events_info_ok(
            info,
            account_create_event=create_event,
            account_delete_event=delete_event,
        )

    def test_account_create_delete_multiple_events(self):
        create_event = event_item(
            name=EVENT_USERINFO_FT,
            timestamp=2,
            hintq='99:q',
            hinta='answer',
            user_ip=TEST_IP,
        )
        delete_event = event_item(
            timestamp=3,
            name=EVENT_ACTION,
            value=ACTION_ACCOUNT_DELETE,
        )
        response = [
            event_item(name=EVENT_ACTION, value=ACTION_ACCOUNT_CHANGE_PASSWORD, timestamp=1),
            event_item(name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX, timestamp=1),
            create_event,
            delete_event,
            delete_event,
        ]

        info = self.load_and_analyze_events(account_create_delete_events=True, events=response)
        self.assert_events_info_ok(
            info,
            account_create_event=create_event,
            account_delete_event=delete_event,
        )


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class AccountEnabledStatusAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_account_status_live(self):
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(name=EVENT_INFO_ENA, value='1'),
            event_item(name=EVENT_INFO_KARMA, value='0'),
            event_item(name=EVENT_INFO_KARMA_PREFIX, value='0'),
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_LIVE,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 3600},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 3600},
                ],
            ),
        )

    def test_account_status_registration_events_repair(self):
        response = [
            event_item(
                name=EVENT_USERINFO_FT,
                timestamp=1,
                hintq='99:q',
                hinta='answer',
                user_ip=TEST_IP,
            ),
            event_item(name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX, timestamp=1.1),
            event_item(name=EVENT_INFO_ENA, value='1', timestamp=1.1),
            event_item(name=EVENT_INFO_KARMA, value='0', timestamp=1.1),
            event_item(name=EVENT_INFO_KARMA_PREFIX, value='0', timestamp=1.1),
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_LIVE,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                ],
            ),
        )

    def test_account_status_disabled(self):
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
            # Блокировка и разблокировка в истории
            event_item(timestamp=2, name=EVENT_INFO_ENA, value='0', admin='alexco', comment='disable spammer', user_ip=TEST_IP),
            event_item(timestamp=3, name=EVENT_INFO_ENA, value='1', admin='alexco', comment='enable spammer', user_ip=TEST_IP),
            # Очернение, блокировка саппортом
            event_item(timestamp=4, name=EVENT_INFO_KARMA_PREFIX, value='1', admin='alexco', comment='spammer'),
            event_item(timestamp=5, name=EVENT_INFO_ENA, value='0', admin='alexco', comment='disable spammer', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_DISABLED,
                admin='alexco',
                comment='disable spammer',
                timestamp=5,
                user_ip=TEST_IP,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                    {'comment': 'spammer', 'admin': 'alexco', 'karma_prefix': 1, 'timestamp': 4},
                ],
            ),
        )

    def test_account_status_disabled_on_support_link_generation(self):
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
            # Выписывание ссылки на восстановление саппортом
            event_item(
                timestamp=2,
                name=EVENT_ACTION,
                value=ACTION_RESTORE_SUPPORT_LINK_CREATED,
                admin='alexco',
                comment='restore',
                user_ip=TEST_IP,
            ),
            event_item(timestamp=2, name=EVENT_INFO_ENA, value='0'),
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_DISABLED,
                admin='alexco',
                comment='restore',
                timestamp=2,
                user_ip=TEST_IP,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                ],
            ),
        )

    def test_account_status_live_unblocked(self):
        response = [
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
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_LIVE_UNBLOCKED,
                admin='support',
                comment='enable spammer',
                timestamp=4,
                user_ip=TEST_IP,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                    {'comment': 'spammer', 'admin': 'alexco', 'karma_prefix': 1, 'timestamp': 2},
                    {'comment': 'enable spammer', 'admin': 'support', 'karma_prefix': 2, 'timestamp': 4},
                ],
            ),
        )

    def test_account_status_live_unblocked_empty_karma_prefix(self):
        """В истории может быть пустое значение префикса кармы"""
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
            # Очернение, блокировка саппортом
            event_item(timestamp=2, name=EVENT_INFO_KARMA_PREFIX, value='1', admin='alexco', comment='spammer'),
            event_item(timestamp=3, name=EVENT_INFO_ENA, value='0', admin='alexco', comment='disable spammer'),
            # Разблокировка, префикс кармы с пустым значением
            event_item(timestamp=4, name=EVENT_INFO_ENA, value='1', admin='support', comment='enable spammer', user_ip=TEST_IP),
            event_item(timestamp=4, name=EVENT_INFO_KARMA_PREFIX, value=None, admin='support', comment='enable spammer'),
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_LIVE_UNBLOCKED,
                admin='support',
                comment='enable spammer',
                timestamp=4,
                user_ip=TEST_IP,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                    {'comment': 'spammer', 'admin': 'alexco', 'karma_prefix': 1, 'timestamp': 2},
                    {'comment': 'enable spammer', 'admin': 'support', 'karma_prefix': 0, 'timestamp': 4},
                ],
            ),
        )

    def test_account_status_deleted(self):
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
            # Очернение, блокировка саппортом
            event_item(timestamp=2, name=EVENT_INFO_KARMA_PREFIX, value='1', admin='alexco', comment='spammer'),
            event_item(timestamp=3, name=EVENT_INFO_ENA, value='0', admin='alexco', comment='disable spammer'),
            # Обеление, разблокировка
            event_item(timestamp=4, name=EVENT_INFO_ENA, value='1', admin='support', comment='enable spammer'),
            event_item(timestamp=4, name=EVENT_INFO_KARMA_PREFIX, value='2', admin='support', comment='enable spammer'),
            # Удаление пользователем
            event_item(timestamp=5, name=EVENT_ACTION, value=ACTION_ACCOUNT_DELETE, user_ip=TEST_IP)
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_DELETED,
                timestamp=5,
                user_ip=TEST_IP,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                    {'comment': 'spammer', 'admin': 'alexco', 'karma_prefix': 1, 'timestamp': 2},
                    {'comment': 'enable spammer', 'admin': 'support', 'karma_prefix': 2, 'timestamp': 4},
                ],
            ),
        )

    def test_account_status_deleted_with_unexpected_extra_events(self):
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(timestamp=1, name=EVENT_INFO_FIRSTNAME, value='abcd1'),
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
            # Удаление пользователем
            event_item(timestamp=5, name=EVENT_ACTION, value=ACTION_ACCOUNT_DELETE, user_ip=TEST_IP),
            event_item(timestamp=6, name=EVENT_INFO_ENA, value='1'),
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_DELETED,
                timestamp=5,
                user_ip=TEST_IP,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                ],
            ),
        )

    def test_account_status_disabled_on_delete(self):
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
            # Блокировка при удалении пользователем
            event_item(timestamp=5, name=EVENT_ACTION, value=ACTION_ACCOUNT_DELETE, user_ip=TEST_IP),
            event_item(timestamp=5, name=EVENT_INFO_ENA, value='0'),
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_DISABLED_ON_DELETE,
                timestamp=5,
                user_ip=TEST_IP,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                ],
            ),
        )

    def test_account_status_deleted_by_support(self):
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
            # Удален саппортом
            event_item(timestamp=5, name=EVENT_ACTION, value=ACTION_ACCOUNT_DELETE, admin='support', user_ip=TEST_IP),
        ]

        info = self.load_and_analyze_events(account_enabled_status=True, events=response)
        self.assert_events_info_ok(
            info,
            account_enabled_status=dict(
                status=ACCOUNT_STATUS_DELETED_BY_SUPPORT,
                admin='support',
                comment=None,
                timestamp=5,
                user_ip=TEST_IP,
                karma_events=[
                    {'comment': None, 'admin': None, 'karma': 0, 'timestamp': 1},
                    {'comment': None, 'admin': None, 'karma_prefix': 0, 'timestamp': 1},
                ],
            ),
        )
