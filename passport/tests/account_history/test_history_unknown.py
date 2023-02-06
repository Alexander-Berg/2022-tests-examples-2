# -*- coding: utf-8 -*-
import mock
from nose.tools import eq_
from passport.backend.core.test.test_utils import with_settings_hosts

from .base import (
    BaseHistoryParserTestCase,
    TEST_HISTORYDB_API_URL,
)


@with_settings_hosts(
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL,
)
class HistoryUnknownTestCase(BaseHistoryParserTestCase):
    def test_unknown_event(self):
        """Совсем неизвестное событие в historydb не парсится."""
        events = self.make_historydb_events(
            {
                'foo': 'bar',
            },
            user_agent=True,
        )
        self.set_response_value(events)

        parsed_events = self.account_history.list()
        eq_(parsed_events, [])

    def test_partially_unknown_event(self):
        """Событие вроде попарсилось из historydb, но контекст мы не узнали."""
        events = self.make_historydb_events(
            {
                'email.delete': '*',
            },
            user_agent=True,
        )
        self.set_response_value(events)
        parsed_events = self.account_history.list()

        eq_(len(parsed_events), 1)

        parsed_event = parsed_events[0]

        with mock.patch.object(self.account_history, '_parse_event') as mocked_parse_event:
            mocked_parse_event.return_value = parsed_event

            # event_type не получилось определить по событиям, ничего не отдастся
            parsed_event.event_type = None
            eq_([], self.account_history.list())

            # event_type получилось определить, событие отдастся
            parsed_event.event_type = 'known_context ;-)'
            eq_([parsed_event], self.account_history.list())

    def test_unknown_event_values_are_masked(self):
        events = self.make_historydb_events(
            {
                'action': 'account_register',
                'info.hinta': 'foo',
                'info.hintq': 'bar',
                'aaa': '111',
                'bbb': '222',
                'ccc': '',
            },
            user_agent=True,
        )
        self.set_response_value(events)
        logger_mock = mock.MagicMock()
        with mock.patch('passport.backend.core.historydb.account_history.account_history.log', logger_mock):
            parsed_events = self.account_history.list()
        eq_(parsed_events, [])
        eq_(len(logger_mock.warning.call_args_list), 1)
        expected_event_data = {
            'action': 'account_register',
            'info.hinta': '***',
            'info.hintq': '***',
            'aaa': '***',
            'bbb': '***',
            'ccc': '',
            'user_agent': '***',
        }
        eq_(logger_mock.warning.call_args[0][1].data, expected_event_data)
