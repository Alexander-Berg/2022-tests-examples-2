# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.test.test_utils import with_settings_hosts

from .base import (
    BaseHistoryParserTestCase,
    TEST_HISTORYDB_API_URL,
)


@with_settings_hosts(
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL,
)
class HistoryParsePhoneTestCase(BaseHistoryParserTestCase):
    def test_app_passwords_enabled(self):
        events = self.make_historydb_events(
            {
                'action': 'app_passwords.activate',
                'info.enable_app_password': '1',
                'info.app_passwords_revoked': '1461573789',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'app_passwords_enabled')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'app_passwords_enabled',
                },
            ],
        )

    def test_app_passwords_disabled(self):
        events = self.make_historydb_events(
            {
                'action': 'app_passwords.deactivate',
                'info.enable_app_password': '0',
                'info.app_passwords_revoked': '1461574533',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'app_passwords_disabled')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'app_passwords_disabled',
                },
                {
                    'type': 'app_passwords_revoked',
                },
            ],
        )
