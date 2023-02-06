# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json
import time
import unittest

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.api.common.historydb_api import (
    auths_aggregated_runtime,
    AuthsAggregatedRuntimeInfo,
    get_historydb_events_info,
)
from passport.backend.api.test.views import ViewsTestEnvironment
import passport.backend.core.authtypes as authtypes
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.builders.historydb_api import HistoryDBApiTemporaryError
from passport.backend.core.builders.historydb_api.build_requests import ORDER_BY_TIMESTAMP_ASCENDING
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    auth_successful_aggregated_browser_info,
    auth_successful_aggregated_os_info,
    auth_successful_aggregated_runtime_auth_item,
    auth_successful_aggregated_runtime_auths_item,
    auth_successful_aggregated_runtime_ip_info,
    auths_successful_aggregated_runtime_response,
    events_response,
)
from passport.backend.core.models.account import Account
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)
from passport.backend.utils.time import DEFAULT_FORMAT


TEST_UID = 1
TEST_REG_TS = 1286654400  # 10 Oct 2010


@with_settings_hosts(HISTORYDB_API_URL='http://localhost/')
class HistoryDbApiAuthsAggregatedRuntimeTestCase(unittest.TestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(),
        )
        self.expected_url = 'http://localhost/2/auths/aggregated/runtime/'

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok_with_check_depth(self):
        OFFSET_IN_DAYS = 365
        account = Account().parse(get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                dbfields={'userinfo.reg_date.uid': datetime.fromtimestamp(TEST_REG_TS).strftime(DEFAULT_FORMAT)},
            ),
        ))

        status, envs = auths_aggregated_runtime(account, check_depth=OFFSET_IN_DAYS)

        ok_(status)
        eq_(envs, json.loads(auths_successful_aggregated_runtime_response())['history'])
        requests = self.env.historydb_api.requests
        eq_(len(requests), 1)
        requests[0].assert_url_starts_with(self.expected_url)
        requests[0].assert_query_equals({
            'uid': str(TEST_UID),
            'from_ts': TimeSpan(
                time.time() - timedelta(OFFSET_IN_DAYS).total_seconds(),
            ),
            'to_ts': TimeNow(),
            'consumer': 'passport',
        })

    def test_ok_with_account_registration_time_and_limit(self):
        OFFSET_IN_DAYS = 10
        account = Account().parse(get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                dbfields={'userinfo.reg_date.uid': datetime.now().strftime(DEFAULT_FORMAT)},
            ),
        ))

        status, envs = auths_aggregated_runtime(account, check_depth=OFFSET_IN_DAYS, limit=10)

        ok_(status)
        eq_(envs, json.loads(auths_successful_aggregated_runtime_response())['history'])
        requests = self.env.historydb_api.requests
        eq_(len(requests), 1)
        requests[0].assert_url_starts_with(self.expected_url)
        requests[0].assert_query_equals({
            'uid': str(TEST_UID),
            'from_ts': TimeNow(),
            'to_ts': TimeNow(),
            'limit': '10',
            'consumer': 'passport',
        })

    def test_ok_with_historydb_error(self):
        self.env.historydb_api.set_response_side_effect(
            'auths_aggregated_runtime',
            HistoryDBApiTemporaryError,
        )

        OFFSET_IN_DAYS = 10
        account = Account().parse(get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        ))

        status, envs = auths_aggregated_runtime(account, OFFSET_IN_DAYS)

        eq_(status, False)
        eq_(envs, [])


@with_settings_hosts(HISTORYDB_API_URL='http://localhost/')
class HistoryDbApiAuthsAggregatedRuntimeInfoTestCase(unittest.TestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(),
        )
        self.account = Account().parse(get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        ))

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_with_empty_data(self):
        info = AuthsAggregatedRuntimeInfo(self.account)
        eq_(list(info), [])

    def test_with_data(self):
        self.env.historydb_api.set_response_value(
            'auths_aggregated_runtime',
            auths_successful_aggregated_runtime_response(items=[
                auth_successful_aggregated_runtime_auths_item(
                    auth_items=[
                        auth_successful_aggregated_runtime_auth_item(
                            authtype=authtypes.AUTH_TYPE_IMAP,
                            status='successful',
                            os_info=auth_successful_aggregated_os_info(),
                        ),
                        auth_successful_aggregated_runtime_auth_item(
                            ip_info=auth_successful_aggregated_runtime_ip_info(),
                            browser_info=auth_successful_aggregated_browser_info(yandexuid='1'),
                            count=10,
                        ),
                    ],
                    timestamp=10,
                ),
                auth_successful_aggregated_runtime_auths_item(timestamp=0),
            ]),
        )
        info = AuthsAggregatedRuntimeInfo(self.account)
        eq_(
            list(info),
            [
                (
                    10,
                    {
                        u'status': u'successful',
                        u'ip': {},
                        u'authtype': authtypes.AUTH_TYPE_IMAP,
                        u'os': auth_successful_aggregated_os_info(),
                        u'browser': {},
                    },
                    1,
                ),
                (
                    10,
                    {
                        u'status': u'ses_create',
                        u'ip': auth_successful_aggregated_runtime_ip_info(),
                        u'authtype': authtypes.AUTH_TYPE_WEB,
                        u'os': {},
                        u'browser': auth_successful_aggregated_browser_info(yandexuid='1'),
                    },
                    10,
                ),
                (
                    0,
                    {
                        u'status': u'ses_create',
                        u'ip': {},
                        u'authtype': authtypes.AUTH_TYPE_WEB,
                        u'os': {},
                        u'browser': {},
                    },
                    1,
                ),
            ],
        )


@with_settings_hosts(HISTORYDB_API_URL='http://localhost/')
class HistoryDbApiEventsInfoTestCase(unittest.TestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.historydb_api.set_response_value(
            'events',
            events_response(),
        )

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_ok_with_limit_overflow(self):
        account = Account().parse(get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                dbfields={'userinfo.reg_date.uid': datetime.fromtimestamp(TEST_REG_TS).strftime(DEFAULT_FORMAT)},
            ),
        ))

        status, events_info = get_historydb_events_info(account, limit=1, names=True)

        ok_(status)
        requests = self.env.historydb_api.requests
        eq_(len(requests), 1)
        requests[0].assert_url_starts_with('http://localhost/2/events/')
        requests[0].assert_query_equals({
            'uid': str(TEST_UID),
            'from_ts': TimeSpan(TEST_REG_TS),
            'to_ts': TimeNow(),
            'consumer': 'passport',
            'limit': '1',
            'name': 'info.firstname,info.lastname,userinfo_ft',
            'order_by': ORDER_BY_TIMESTAMP_ASCENDING,
        })

    def test_ok_with_historydb_error(self):
        self.env.historydb_api.set_response_side_effect(
            'events',
            HistoryDBApiTemporaryError,
        )
        account = Account().parse(get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID),
        ))

        status, events_info = get_historydb_events_info(account)

        eq_(status, False)
        assert_is_none(events_info)
