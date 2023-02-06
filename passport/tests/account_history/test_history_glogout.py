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
class HistoryParseHintTestCase(BaseHistoryParserTestCase):
    def test_glogout(self):
        events = self.make_historydb_events(
            {
                'info.glogout': '1463659432',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'global_logout')
        eq_(
            parsed_events[0].actions,
            [{
                'type': 'global_logout',
            }],
        )

    def test_web_sessions_revoke(self):
        events = self.make_historydb_events(
            {
                'info.web_sessions_revoked': '1463659432',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'global_logout')
        eq_(
            parsed_events[0].actions,
            [{
                'type': 'web_sessions_revoked',
            }],
        )

    def test_tokens_revoke(self):
        events = self.make_historydb_events(
            {
                'info.tokens_revoked': '1463659432',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'global_logout')
        eq_(
            parsed_events[0].actions,
            [{
                'type': 'tokens_revoked',
            }],
        )

    def test_app_passwords_revoke(self):
        events = self.make_historydb_events(
            {
                'info.app_passwords_revoked': '1463659432',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'global_logout')
        eq_(
            parsed_events[0].actions,
            [{
                'type': 'app_passwords_revoked',
            }],
        )

    def test_glogout_tokens_and_app_passwords(self):
        events = self.make_historydb_events(
            {
                'info.tokens_revoked': '1463659432',
                'info.app_passwords_revoked': '1463659432',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)
        eq_(parsed_events[0].event_type, 'global_logout')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'app_passwords_revoked',
                },
                {
                    'type': 'tokens_revoked',
                },
            ],
        )
