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
    def test_old_hint(self):
        events = self.make_historydb_events(
            {
                'info.hinta': 'foo',
                'info.hintb': 'bar'
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'questions_change',
                },
            ],
        )
        eq_(parsed_events[0].event_type, 'questions')

    def test_just_question(self):
        events = self.make_historydb_events(
            {
                'info.hintq': 'foo',
            },
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'questions_change',
                },
            ],
        )
        eq_(parsed_events[0].event_type, 'questions')

    def test_remove(self):
        events = self.make_historydb_events(
            {
                'info.hinta': None,
                'info.hintq': None,
            },
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        eq_(
            parsed_events[0].actions,
            [
                {
                    'type': 'questions_remove',
                },
            ],
        )
        eq_(parsed_events[0].event_type, 'questions')
