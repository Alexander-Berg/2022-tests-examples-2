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
class HistoryPaginationTestCase(BaseHistoryParserTestCase):
    def test_pagination_all(self):
        all_events = []
        expected_timestamps = list(range(99))
        for i in range(99):
            events = self.make_historydb_events(
                {
                    'info.hinta': int(i),
                },
                timestamp=i,
                user_agent=True,
            )
            all_events.extend(events)

        self.set_response_value(all_events)

        actual_timestamps = []
        next_page_timestapm = None
        for i in range(50):
            parsed_events = self.account_history.list(to_ts=next_page_timestapm, limit=2)

            for e in parsed_events:
                actual_timestamps.append(e.timestamp)

            next_page_timestapm = self.account_history.next_page_timestamp

        eq_(expected_timestamps, actual_timestamps[::-1])

    def test_pagination_float_timestamps(self):
        all_events = []
        expected_timestamps = [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]
        for timestamp in expected_timestamps:
            events = self.make_historydb_events(
                {
                    'info.hinta': int(timestamp),
                },
                timestamp=timestamp,
                user_agent=True,
            )
            all_events.extend(events)

        self.set_response_value(all_events)

        actual_timestamps = []
        next_page_timestapm = None
        for i in range(len(expected_timestamps) // 2):
            parsed_events = self.account_history.list(to_ts=next_page_timestapm, limit=2)

            eq_(len(parsed_events), 2)

            for e in parsed_events:
                actual_timestamps.append(e.timestamp)

            next_page_timestapm = self.account_history.next_page_timestamp

        parsed_events = self.account_history.list(to_ts=next_page_timestapm, limit=2)
        eq_(len(parsed_events), 1)
        actual_timestamps.append(parsed_events[0].timestamp)

        eq_(expected_timestamps, actual_timestamps[::-1])
