# -*- coding: utf-8 -*-

from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_info_interval_point,
)
from passport.backend.core.historydb.events import (
    ACTION_ACCOUNT_CHANGE_PASSWORD,
    ACTION_ACCOUNT_PASSWORD,
    ACTION_ACCOUNT_REGISTER_PREFIX,
    ACTION_RESTORE_PASSED_BY_METHOD_PREFIX,
    EVENT_ACTION,
    EVENT_INFO_ENA,
    EVENT_INFO_KARMA,
    EVENT_INFO_KARMA_PREFIX,
    EVENT_INFO_PASSWORD,
    EVENT_RESTORE_METHOD_PASSED,
    EVENT_SID_LOGIN_RULE,
    EVENT_USER_AGENT,
    PASSWORD_CHANGE_TYPE_FORCED,
    PASSWORD_CHANGE_TYPE_RESTORE,
    PASSWORD_CHANGE_TYPE_VOLUNTARY,
)
from passport.backend.core.test.test_utils import with_settings_hosts

from ..data import (
    TEST_IP,
    TEST_IP_2,
    TEST_USER_AGENT,
    TranslationSettings,
)
from ..test_events import BaseEventsAnalyzerTestCase


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class PasswordChangesAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_password_change_no_changes(self):
        response = [
            # Срез событий, пишущихся при регистрации
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_REGISTER_PREFIX),
            event_item(timestamp=1, name=EVENT_INFO_ENA, value='1'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA, value='0'),
            event_item(timestamp=1, name=EVENT_INFO_KARMA_PREFIX, value='0'),
        ]

        info = self.load_and_analyze_events(password_changes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_change_requests=[],
            password_changes=[],
        )

    def test_password_change_change_required(self):
        response = [
            event_item(
                timestamp=1,
                name=EVENT_ACTION,
                value=ACTION_ACCOUNT_PASSWORD,
                admin='alexco',
                comment='broken',
                user_ip=TEST_IP,
            ),
            event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|5'),
        ]

        info = self.load_and_analyze_events(password_changes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_change_requests=[{
                'change_required': True,
                'comment': 'broken',
                'admin': 'alexco',
                'origin_info': events_info_interval_point(),
            }],
            password_changes=[],
        )

    def test_password_change_change_not_required_by_admin(self):
        response = [
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_PASSWORD, admin='alexco', comment='broken', user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|5'),
            event_item(timestamp=2, name=EVENT_ACTION, value=ACTION_ACCOUNT_PASSWORD, admin='alexco', comment='not broken', user_ip=TEST_IP_2),
            event_item(timestamp=2, name=EVENT_SID_LOGIN_RULE, value='8|1'),
            event_item(timestamp=2, name=EVENT_USER_AGENT, value=TEST_USER_AGENT),
        ]

        info = self.load_and_analyze_events(password_changes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_change_requests=[
                {
                    'change_required': True,
                    'comment': 'broken',
                    'admin': 'alexco',
                    'origin_info': events_info_interval_point(),
                },
                {
                    'change_required': False,
                    'comment': 'not broken',
                    'admin': 'alexco',
                    'origin_info': events_info_interval_point(user_ip=TEST_IP_2, timestamp=2, user_agent=TEST_USER_AGENT),
                },
            ],
            password_changes=[],
        )

    def test_password_change_password_changed_by_user_but_not_required(self):
        """Пользователь выполнил принудительную смену пароля, но в логе нет информации о принуждении"""
        response = [
            event_item(timestamp=1, name=EVENT_USER_AGENT, value=TEST_USER_AGENT),
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_CHANGE_PASSWORD, user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|1'),
        ]

        info = self.load_and_analyze_events(password_changes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_change_requests=[],
            password_changes=[
                {
                    'change_type': PASSWORD_CHANGE_TYPE_FORCED,
                    'origin_info': events_info_interval_point(user_agent=TEST_USER_AGENT),
                },
            ],
        )

    def test_password_change_voluntary_password_change(self):
        response = [
            event_item(timestamp=1, name=EVENT_ACTION, value=ACTION_ACCOUNT_CHANGE_PASSWORD, user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_USER_AGENT, value=TEST_USER_AGENT),
            event_item(timestamp=1, name=EVENT_INFO_PASSWORD, value='12345'),
            event_item(timestamp=2, name=EVENT_SID_LOGIN_RULE, value='8|1'),
        ]

        info = self.load_and_analyze_events(password_changes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_change_requests=[],
            password_changes=[
                {
                    'change_type': PASSWORD_CHANGE_TYPE_VOLUNTARY,
                    'origin_info': events_info_interval_point(user_agent=TEST_USER_AGENT),
                },
            ],
        )

    def test_password_change_on_old_restore(self):
        response = [
            event_item(timestamp=1, name=EVENT_ACTION, value='some action'),  # событие игнорируется
            event_item(timestamp=1, name=EVENT_RESTORE_METHOD_PASSED, value='key', user_ip=TEST_IP),
            event_item(timestamp=1, name=EVENT_INFO_PASSWORD, value='12345'),
            event_item(timestamp=1, name=EVENT_USER_AGENT, value=TEST_USER_AGENT),
            event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|1'),
        ]

        info = self.load_and_analyze_events(password_changes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_change_requests=[],
            password_changes=[
                {
                    'change_type': PASSWORD_CHANGE_TYPE_RESTORE,
                    'restore_method': 'key',
                    'origin_info': events_info_interval_point(user_agent=TEST_USER_AGENT),
                },
            ],
        )

    def test_password_change_on_new_restore(self):
        response = [
            event_item(
                timestamp=1,
                name=EVENT_ACTION,
                value=ACTION_RESTORE_PASSED_BY_METHOD_PREFIX + '_hint',
                user_ip=TEST_IP,
            ),
            event_item(timestamp=1, name=EVENT_INFO_PASSWORD, value='12345'),
            event_item(timestamp=1, name=EVENT_USER_AGENT, value=TEST_USER_AGENT),
            event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|1'),
        ]

        info = self.load_and_analyze_events(password_changes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_change_requests=[],
            password_changes=[
                {
                    'change_type': PASSWORD_CHANGE_TYPE_RESTORE,
                    'restore_method': 'hint',
                    'origin_info': events_info_interval_point(user_agent=TEST_USER_AGENT),
                },
            ],
        )

    def test_password_change_unknown_reason(self):
        response = [
            event_item(timestamp=1, name=EVENT_INFO_PASSWORD, value='12345'),
            event_item(timestamp=1, name=EVENT_SID_LOGIN_RULE, value='8|1'),
        ]

        info = self.load_and_analyze_events(password_changes=True, events=response)
        self.assert_events_info_ok(
            info,
            password_change_requests=[],
            password_changes=[],
        )
