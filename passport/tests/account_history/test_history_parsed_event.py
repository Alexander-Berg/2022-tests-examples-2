# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.historydb.account_history.account_history import EventEntry
from passport.backend.core.historydb.account_history.event_parsers.base import (
    filter_yandex_server,
    HistoryDbParsedEvent,
)
from passport.backend.core.historydb.account_history.event_parsers.parser import parse_event
from passport.backend.core.test.test_utils import with_settings

from .base import (
    TEST_GEO_ID,
    TEST_USER_AGENT,
    TEST_USER_IP,
)


TEST_OS_NAME = 'Mac OS X El Capitan'
TEST_OS_VERSION = '10.11.4'

TEST_BROWSER_NAME = 'YandexBrowser'
TEST_BROWSER_VERSION = '16.4.0.6108'

TEST_AS_LIST = ['AS12345', 'AS67890']


@with_settings
class HistoryParsedEventTestCase(unittest.TestCase):
    def test_from_historydb_event(self):
        event = EventEntry(
            timestamp=1,
            client_name='client',
            data={
                'key_1': 'value_1',
                'key_2': 'value_2',
                'user_agent': TEST_USER_AGENT,
            },
            geo_id=TEST_GEO_ID,
            user_ip=TEST_USER_IP,
            as_list=TEST_AS_LIST,
        )
        parsed_event = HistoryDbParsedEvent.from_historydb_event(event)
        eq_(parsed_event.event_type, None)
        eq_(parsed_event.timestamp, 1)
        eq_(parsed_event.actions, [])
        eq_(parsed_event.ip._asdict(), {'ip': TEST_USER_IP, 'AS': 12345, 'geoid': TEST_GEO_ID})
        eq_(parsed_event.os._asdict(), {'name': TEST_OS_NAME, 'version': TEST_OS_VERSION})
        eq_(parsed_event.browser._asdict(), {'name': TEST_BROWSER_NAME, 'version': TEST_BROWSER_VERSION})

    def test_user_ip_is_localhost_ipv4(self):
        event = EventEntry(
            timestamp=1,
            client_name='client',
            data={
                'key_1': 'value_1',
                'key_2': 'value_2',
                'user_agent': TEST_USER_AGENT,
            },
            geo_id=TEST_GEO_ID,
            user_ip='127.0.0.1',
            as_list=TEST_AS_LIST,
        )
        parsed_event = HistoryDbParsedEvent.from_historydb_event(event)
        eq_(parsed_event.ip._asdict(), {'ip': None, 'AS': None, 'geoid': None})

    def test_user_ip_is_localhost_ipv6(self):
        event = EventEntry(
            timestamp=1,
            client_name='client',
            data={
                'key_1': 'value_1',
                'key_2': 'value_2',
                'user_agent': TEST_USER_AGENT,
            },
            geo_id=TEST_GEO_ID,
            user_ip='::1',
            as_list=TEST_AS_LIST,
        )
        parsed_event = HistoryDbParsedEvent.from_historydb_event(event)
        eq_(parsed_event.ip._asdict(), {'ip': None, 'AS': None, 'geoid': None})

    def test_user_ip_no_address(self):
        event = EventEntry(
            timestamp=1,
            client_name='client',
            data={
                'key_1': 'value_1',
                'key_2': 'value_2',
                'user_agent': TEST_USER_AGENT,
            },
            geo_id=TEST_GEO_ID,
            user_ip=None,
            as_list=TEST_AS_LIST,
        )
        parsed_event = HistoryDbParsedEvent.from_historydb_event(event)
        eq_(parsed_event.ip._asdict(), {'ip': None, 'AS': None, 'geoid': None})

    def test_user_ip_is_garbage(self):
        event = EventEntry(
            timestamp=1,
            client_name='client',
            data={
                'key_1': 'value_1',
                'key_2': 'value_2',
                'user_agent': TEST_USER_AGENT,
            },
            geo_id=TEST_GEO_ID,
            user_ip='trollface',
            as_list=TEST_AS_LIST,
        )
        parsed_event = HistoryDbParsedEvent.from_historydb_event(event)
        eq_(parsed_event.ip._asdict(), {'ip': None, 'AS': None, 'geoid': None})

    def test_filter_yandex_server(self):
        eq_(filter_yandex_server('not-an-ip'), None)

    def test_as_dict(self):
        event = EventEntry(
            timestamp=1,
            client_name='client',
            data={
                'key_1': 'value_1',
                'key_2': 'value_2',
                'user_agent': TEST_USER_AGENT,
            },
            geo_id=TEST_GEO_ID,
            user_ip=TEST_USER_IP,
            as_list=TEST_AS_LIST,
        )
        parsed_event = HistoryDbParsedEvent.from_historydb_event(event)
        parsed_event_as_dict = parsed_event._asdict()
        eq_(
            parsed_event_as_dict,
            {
                'event_type': None,
                'timestamp': 1,
                'actions': [],
                'ip': {
                    'ip': TEST_USER_IP,
                    'AS': 12345,
                    'geoid': TEST_GEO_ID,
                },
                'os': {
                    'name': TEST_OS_NAME,
                    'version': TEST_OS_VERSION,
                },
                'browser': {
                    'name': TEST_BROWSER_NAME,
                    'version': TEST_BROWSER_VERSION,
                },
            },
        )

    def test_repr(self):
        event = EventEntry(
            timestamp=1,
            client_name='client',
            data={
                'key_1': 'value_1',
                'key_2': 'value_2',
                'user_agent': TEST_USER_AGENT,
            },
            geo_id=TEST_GEO_ID,
            user_ip=TEST_USER_IP,
            as_list=TEST_AS_LIST,
        )
        parsed_event = HistoryDbParsedEvent.from_historydb_event(event)
        parsed_event.actions.append({'foo': 'bar'})

        eq_(
            repr(parsed_event),
            '<HistoryDbParsedEvent timestamp=1 event_type=None actions=[{\'foo\': \'bar\'}]>',
        )

    def test_ignore_account_register(self):
        # Тип события не должен определяться, если это account_register
        event = EventEntry(
            timestamp=1,
            client_name='client',
            data={
                u'action': u'account_register',
                u'alias.portal.add': u'foo',
                u'consumer': u'passport',
                u'info.country': u'ru',
                u'info.ena': u'1',
                u'info.firstname': u'firstname',
                u'info.hinta': u'foo',
                u'info.hintq': u'bar',
                u'info.karma': u'0',
                u'info.karma_prefix': u'0',
                u'info.lang': u'ru',
                u'info.lastname': u'lastname',
                u'info.login': u'foo',
                u'info.login_wanted': u'foo',
                u'info.password': u'pwd',
                u'info.password_quality': u'100',
                u'info.password_update_time': u'1466509277',
                u'info.reg_date': u'2016-06-21 14:41:17',
                u'info.sex': u'0',
                u'mail.add': u'3004000313,1034',
                u'sid.add': u'8|foo,2',
            },
            geo_id=TEST_GEO_ID,
            user_ip=TEST_USER_IP,
            as_list=TEST_AS_LIST,
        )
        parsed_event = parse_event(event)
        ok_(parsed_event.actions)  # не смотря на то, что что-то попарсилось
        eq_(parsed_event.event_type, None)  # всё равно отказываемся определять тип, игнорируем
