# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    events_response,
    FakeHistoryDBApi,
)
from passport.backend.core.historydb.account_history.account_history import AccountHistory
from passport.backend.core.models.account import Account
from six import iteritems


TEST_HISTORYDB_API_URL = 'http://historydb-api-url/'
TEST_DEFAULT_REGISTRATION_DATETIME = '2010-10-10 10:20:30'
TEST_CLIENT_NAME = u'passport'
TEST_HOST_ID = u'140'
TEST_USER_IP = u'2a02:6b8:0:40c:40b5:42ae:c26c:1a71'
TEST_GEO_ID = u'9999'
TEST_AS_LIST = u'AS13238'
TEST_YANDEXUID = u'629203331460392130'
TEST_TIMESTAMP = 1461226823.417519
TEST_USER_AGENT = u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.91 YaBrowser/16.4.0.6108 (beta) Safari/537.36'

TEST_EMAIL = 'vasily@yandex-team.ru'
TEST_PUNICODE_EMAIL = u'%s@%s' % ('vasily', u'админкапдд.рф'.encode('idna').decode('utf-8'))
TEST_MASKED_EMAIL = 'v***y@y***.ru'
TEST_MASKED_PUNICODE_EMAIL = u'v***y@а***.рф'


class BaseHistoryParserTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_historydb = FakeHistoryDBApi()
        self.fake_historydb.start()
        self.fake_historydb.set_response_value('events', events_response(events=[]))
        self.account = Account().parse(
            get_parsed_blackbox_response(
                'userinfo',
                blackbox_userinfo_response(dbfields={'userinfo.reg_date.uid': TEST_DEFAULT_REGISTRATION_DATETIME}),
            ),
        )
        self.account_history = AccountHistory(uid=self.account.uid)

    def tearDown(self):
        self.fake_historydb.stop()
        del self.fake_historydb

    @staticmethod
    def make_historydb_events(
            data,
            timestamp=TEST_TIMESTAMP,
            geo_id=TEST_GEO_ID,
            user_ip=TEST_USER_IP,
            host_id=TEST_HOST_ID,
            client_name=TEST_CLIENT_NAME,
            yandexuid=TEST_YANDEXUID,
            as_list=TEST_AS_LIST,
            user_agent=True
    ):
        constant_part = {
            u'ip.geoid': geo_id,
            u'ip.as_list': as_list,
            u'user_ip': user_ip,
            u'client_name': client_name,
            u'host_id': host_id,
            u'yandexuid': yandexuid,
            u'timestamp': timestamp,
        }
        events = []
        for key, value in iteritems(data):
            events.append(dict(name=key, value=value, **constant_part))
        if user_agent:
            events.append(dict(name=u'user_agent', value=TEST_USER_AGENT, **constant_part))
        return events

    def set_response_value(self, events):
        self.fake_historydb.set_response_value('events', events_response(events=events))

    @staticmethod
    def assert_events_equal(a, b):
        # в py2 и в py3 списки словарей имеют разный порядок, поэтому
        # выделен отдельный метод для их сравнения
        a_ = sorted(a, key=lambda d: d['type'])
        b_ = sorted(b, key=lambda d: d['type'])
        assert a_ == b_
