# -*- coding: utf-8 -*-

from datetime import datetime
import unittest
from urllib.parse import (
    parse_qs,
    urlparse,
)

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.adm_api.common.historydb_api import get_historydb_events_info
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import ViewsTestEnvironment
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.builders.historydb_api import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.build_requests import ORDER_BY_TIMESTAMP_ASCENDING
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    event_item,
    events_response,
)
from passport.backend.core.historydb.events import (
    EVENT_INFO_HINTA,
    EVENT_INFO_HINTQ,
)
from passport.backend.core.models.account import Account
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.utils.time import DEFAULT_FORMAT


TEST_UID = 1


@with_settings_hosts(HISTORYDB_API_URL='http://localhost/')
class HistoryDbApiTestCase(unittest.TestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_events_info_by_uid(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name=EVENT_INFO_HINTQ, value='99:q')]),
        )
        events_info = get_historydb_events_info(uid=TEST_UID, questions=True)

        requests = self.env.historydb_api.requests
        eq_(len(requests), 1)
        query = parse_qs(urlparse(requests[0]._url).query)
        eq_(query['from_ts'], ['0'])
        eq_(query['order_by'], [ORDER_BY_TIMESTAMP_ASCENDING])
        eq_(events_info.questions, ['99:q'])

    def test_events_info_by_account(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name=EVENT_INFO_HINTA, value='a')]),
        )
        TEST_TS = 1286654400
        account = Account().parse(get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                dbfields={'userinfo.reg_date.uid': datetime.fromtimestamp(TEST_TS).strftime(DEFAULT_FORMAT)},
            ),
        ))
        events_info = get_historydb_events_info(account=account, answers=True)

        requests = self.env.historydb_api.requests
        eq_(len(requests), 1)
        query = parse_qs(urlparse(requests[0]._url).query)
        eq_(query['from_ts'], [str(TEST_TS)])
        eq_(query['to_ts'], [TimeNow()])
        eq_(query['order_by'], [ORDER_BY_TIMESTAMP_ASCENDING])
        eq_(events_info.answers, ['a'])

    def test_events_info_limit_overflow(self):
        self.env.historydb_api.set_response_value(
            'events',
            events_response(events=[event_item(name=EVENT_INFO_HINTQ, value='99:q')]),
        )
        events_info = get_historydb_events_info(uid=TEST_UID, limit=1, questions=True)
        eq_(events_info.questions, ['99:q'])

    @raises(HistoryDBApiTemporaryError)
    def test_events_info_historydb_fail(self):
        self.env.historydb_api.set_response_side_effect('events', HistoryDBApiTemporaryError)
        get_historydb_events_info(uid=TEST_UID, answers=True)
