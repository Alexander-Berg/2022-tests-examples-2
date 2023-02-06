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
    def test_totp_enabled(self):
        events = self.make_historydb_events(
            {
                'action': 'enable_otp',
                'info.totp': 'enabled',
                'info.totp_secret.28351': '*',
                'info.password_quality': None,
                'info.glogout': '1461848305',
                'info.password_update_time': None,
                'info.totp_update_time': '1461848305',
                'info.password': None,
                'info.enable_app_password': '1',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'totp_enabled')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_remove',
                },
                {
                    'type': 'totp_enabled',
                },
            ],
        )

    def test_totp_disabled(self):
        events = self.make_historydb_events(
            {
                'action': 'disable_otp',
                'info.totp': 'disabled',
                'info.totp_secret.28353': None,
                'info.password_quality': '100',
                'info.glogout': '1461849808',
                'info.password_update_time': '1461849808',
                'info.password': '$1$DW6t3nrl$5739z111QP5v41o68QXVC.',
                'info.totp_update_time': None,
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'totp_disabled')
        self.assert_events_equal(
            parsed_events[0].actions,
            [
                {
                    'type': 'global_logout',
                },
                {
                    'type': 'password_change',
                },
                {
                    'type': 'totp_disabled',
                },
            ],
        )

    def test_totp_migrated(self):
        events = self.make_historydb_events(
            {
                'action': 'migrate_otp',
                'info.totp_secret.28353': '*',
                'info.totp_secret.28351': None
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(parsed_events[0].event_type, 'totp_migrated')
        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'totp_migrated',
                },
            ],
        )
