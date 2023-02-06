# -*- coding: utf-8 -*-

from passport.backend.core.builders.historydb_api.faker.historydb_api import event_item
from passport.backend.core.historydb.events import (
    ACTION_ACCOUNT_CHANGE_PASSWORD,
    ACTION_RESTORE_SEMI_AUTO_DECISION,
    ACTION_RESTORE_SEMI_AUTO_REQUEST,
    ACTION_RESTORE_SUPPORT_LINK_CREATED,
    EVENT_ACTION,
    EVENT_INFO_RESTORE_ID,
    EVENT_INFO_RESTORE_REQUEST_SOURCE,
    EVENT_INFO_RESTORE_STATUS,
    EVENT_INFO_SUPPORT_LINK_TYPE,
    RESTORE_STATUS_PASSED,
    RESTORE_STATUS_PENDING,
    RESTORE_STATUS_REJECTED,
)
from passport.backend.core.support_link_types import (
    SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
    SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
    SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
)
from passport.backend.core.test.test_utils import with_settings_hosts

from ..data import TranslationSettings
from ..test_events import BaseEventsAnalyzerTestCase


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class RestorePassedAttemptsAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_no_matching_events(self):
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_RESTORE_SUPPORT_LINK_CREATED,
            ),
            event_item(
                name=EVENT_INFO_SUPPORT_LINK_TYPE,
                timestamp=2,
                value=SUPPORT_LINK_TYPE_FORCE_PHONE_RESTORATION,
            ),
        ]

        info = self.load_and_analyze_events(restore_passed_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_passed_attempts=[],
        )

    def test_multiple_passed_attempts(self):
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value='restore_passed_by_hint',
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value='restore_passed_by_phone_and_pin',
            ),
        ]

        info = self.load_and_analyze_events(restore_passed_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_passed_attempts=[
                {'timestamp': 1, 'method': u'hint'},
                {'timestamp': 2, 'method': u'phone_and_pin'},
            ],
        )

    def test_passed_attempts_with_support_link(self):
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value='restore_passed_by_hint',
            ),
            event_item(
                name=EVENT_INFO_SUPPORT_LINK_TYPE,
                timestamp=1,
                value=SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value='restore_passed_by_link',
            ),
            event_item(
                name=EVENT_INFO_SUPPORT_LINK_TYPE,
                timestamp=2,
                value=SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD,
            ),
        ]

        info = self.load_and_analyze_events(restore_passed_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_passed_attempts=[
                {'timestamp': 1, 'method': u'hint', 'link_type': SUPPORT_LINK_TYPE_FORCE_HINT_RESTORATION},
                {'timestamp': 2, 'method': u'link', 'link_type': SUPPORT_LINK_TYPE_CHANGE_PASSWORD_SET_METHOD},
            ],
        )


@with_settings_hosts(
    translations=TranslationSettings,
    HISTORYDB_API_URL='http://localhost/',
)
class RestoreSemiAutoAttemptsAnalyzerTestCase(BaseEventsAnalyzerTestCase):
    def test_restore_attempts_full_data(self):
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value='restore_id',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_REQUEST_SOURCE,
                timestamp=1,
                value='changepass',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=1,
                value=RESTORE_STATUS_PENDING,
            ),
        ]

        info = self.load_and_analyze_events(restore_semi_auto_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_semi_auto_attempts=[dict(
                timestamp=1,
                restore_id='restore_id',
                request_source='changepass',
                initial_status=RESTORE_STATUS_PENDING,
                support_decisions=[],
            )],
        )

    def test_restore_attempts_missing_data(self):
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value='restore_id',
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_ACCOUNT_CHANGE_PASSWORD,  # игнорируем не интересующие нас action'ы
            ),
        ]

        info = self.load_and_analyze_events(restore_semi_auto_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_semi_auto_attempts=[dict(
                timestamp=1,
                restore_id='restore_id',
                request_source='restore',
                initial_status=RESTORE_STATUS_REJECTED,
                support_decisions=[],
            )],
        )

    def test_restore_attempts_invalid_data(self):
        """В лог не попала запись от анкеты, но запись от саппорта есть"""
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_DECISION,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value='restore_id',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_REQUEST_SOURCE,
                timestamp=1,
                value='changepass',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=1,
                value=RESTORE_STATUS_PASSED,
            ),
        ]

        info = self.load_and_analyze_events(restore_semi_auto_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_semi_auto_attempts=[],
        )

    def test_restore_attempts_no_attempts(self):
        response = []

        info = self.load_and_analyze_events(restore_semi_auto_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_semi_auto_attempts=[],
        )

    def test_restore_attempts_multiple_attempts(self):
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value='restore_id',
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=2,
                value='restore_id_2',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_REQUEST_SOURCE,
                timestamp=2,
                value='changepass',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=2,
                value=RESTORE_STATUS_PENDING,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=3,
                value=ACTION_RESTORE_SEMI_AUTO_DECISION,
                admin='support',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=3,
                value='restore_id_2',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=3,
                value=RESTORE_STATUS_PASSED,
            ),
        ]

        info = self.load_and_analyze_events(restore_semi_auto_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_semi_auto_attempts=[
                dict(
                    timestamp=1,
                    restore_id='restore_id',
                    request_source='restore',
                    initial_status=RESTORE_STATUS_REJECTED,
                    support_decisions=[],
                ),
                dict(
                    timestamp=2,
                    restore_id='restore_id_2',
                    request_source='changepass',
                    initial_status=RESTORE_STATUS_PENDING,
                    support_decisions=[
                        dict(
                            status=RESTORE_STATUS_PASSED,
                            timestamp=3,
                            admin='support',
                        ),
                    ],
                ),
            ],
        )

    def test_restore_attempts_multiple_support_decisions(self):
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value='restore_id',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_REQUEST_SOURCE,
                timestamp=1,
                value='changepass',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=1,
                value=RESTORE_STATUS_PENDING,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_RESTORE_SEMI_AUTO_DECISION,
                admin='bad_support',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=2,
                value='restore_id',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=2,
                value=RESTORE_STATUS_REJECTED,
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=3,
                value=ACTION_RESTORE_SEMI_AUTO_DECISION,
                admin='good_support',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=3,
                value='restore_id',
            ),
            event_item(
                name=EVENT_INFO_RESTORE_STATUS,
                timestamp=3,
                value=RESTORE_STATUS_PASSED,
            ),
        ]

        info = self.load_and_analyze_events(restore_semi_auto_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_semi_auto_attempts=[
                dict(
                    timestamp=1,
                    restore_id='restore_id',
                    request_source='changepass',
                    initial_status=RESTORE_STATUS_PENDING,
                    support_decisions=[
                        dict(
                            status=RESTORE_STATUS_REJECTED,
                            timestamp=2,
                            admin='bad_support',
                        ),
                        dict(
                            status=RESTORE_STATUS_PASSED,
                            timestamp=3,
                            admin='good_support',
                        ),
                    ],
                ),
            ],
        )

    def test_restore_attempts_duplicate_request_actions(self):
        """Пришли две записи от анкеты с одинаковым restore_id, учитываем только первую запись"""
        response = [
            event_item(
                name=EVENT_ACTION,
                timestamp=1,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=1,
                value='restore_id',
            ),
            event_item(
                name=EVENT_ACTION,
                timestamp=2,
                value=ACTION_RESTORE_SEMI_AUTO_REQUEST,
            ),
            event_item(
                name=EVENT_INFO_RESTORE_ID,
                timestamp=2,
                value='restore_id',
            ),
        ]

        info = self.load_and_analyze_events(restore_semi_auto_attempts=True, events=response)
        self.assert_events_info_ok(
            info,
            restore_semi_auto_attempts=[
                dict(
                    timestamp=1,
                    restore_id='restore_id',
                    request_source='restore',
                    initial_status=RESTORE_STATUS_REJECTED,
                    support_decisions=[],
                ),
            ],
        )
