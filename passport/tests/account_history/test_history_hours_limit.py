# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.core.historydb.account_history.account_history import HALF_A_YEAR_AGO
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base import (
    BaseHistoryParserTestCase,
    TEST_HISTORYDB_API_URL,
)


@with_settings_hosts(
    HISTORYDB_API_URL=TEST_HISTORYDB_API_URL,
)
class HistoryHoursLimitTestCase(BaseHistoryParserTestCase):
    def test_hours_limit_no(self):
        self.account_history.list()
        eq_(len(self.fake_historydb.requests), 1)
        request = self.fake_historydb.requests[0]
        request.assert_query_contains({
            'from_ts': TimeNow(offset=-HALF_A_YEAR_AGO),
            'to_ts': TimeNow(),
        })

    def test_hours_limit_ok(self):
        self.account_history.list(hours_limit=5)
        eq_(len(self.fake_historydb.requests), 1)
        request = self.fake_historydb.requests[0]
        request.assert_query_contains({
            'from_ts': TimeNow(offset=-5 * 3600),
            'to_ts': TimeNow(),
        })

    def test_hours_limit_over_limit(self):
        self.account_history.list(hours_limit=HALF_A_YEAR_AGO / 3600 + 1)
        eq_(len(self.fake_historydb.requests), 1)
        request = self.fake_historydb.requests[0]
        request.assert_query_contains({
            'from_ts': TimeNow(offset=-HALF_A_YEAR_AGO),
            'to_ts': TimeNow(),
        })
