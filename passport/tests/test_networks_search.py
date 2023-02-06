# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from django.conf import settings
from django.test import TestCase

from passport_grants_configurator.apps.core.network_search_tools import match_networks
from passport_grants_configurator.apps.core.test.utils import (
    MockNetworkApi,
    MockRedis,
)


def get_network_redis_key(name):
    return '%s:%s:%s' % (settings.REDIS_KEY_PREFIX, settings.REDIS_NETWORK_PREFIX, name)


class MatchNetworksTestCase(TestCase):
    maxDiff = None
    fixtures = ['default.json']

    def setUp(self):
        self.mock_redis = MockRedis()
        self.mock_redis.start()
        self.network_api = MockNetworkApi()
        self.network_api.start()

    def tearDown(self):
        self.network_api.stop()
        self.mock_redis.stop()

    def test_short_keyword(self):
        matched = match_networks('a')
        ok_(not matched)

    def test_no_network_matched(self):
        self.network_api.setup_response(
            'get_conductor_group_hosts',
            {},
        )
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96/28',
                '2a02:6b8:0:212::/64',
                '_TEST_CONSUMER_',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '77.88.40.96/28',
                '93.158.133.0/26',
                '2a02:6b8:0:212::/64',
            ]),
            get_network_redis_key('%passport-dev'): json.dumps({
                'id': 1,
                'descendant_ids': [],
                'parent_ids': [],
                'type': 'C',
                'children': [],
                'string': '%passport-dev',
            }),
        }
        matched = match_networks('%passport-dev')
        ok_(not matched)
        ok_(not self.network_api.mocks['get_conductor_group_hosts'].called)

    def test_ip_network_short_prefixlen(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96/28',
                '2a02:6b8:0:212::/64',
                '_TEST_CONSUMER_',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '77.88.40.96/28',
                '93.158.133.0/26',
                '2a02:6b8:0:212::/64',
            ]),
        }
        matched = match_networks('192.168.1.10/1')
        ok_(not matched)

    def test_trypo_network_short_prefixlen(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96/28',
                '2a02:6b8:0:212::/64',
                '_TEST_CONSUMER_',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '77.88.40.96/28',
                '93.158.133.0/26',
                '2a02:6b8:0:212::/64',
            ]),
        }
        matched = match_networks('13@2:2::/1')
        ok_(not matched)

    def test_no_cached_ip_networks(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96/28',
                '2a02:6b8:0:212::/64',
                '_TEST_CONSUMER_',
                '13@2:2::/40',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([]),
            get_network_redis_key('13@2:2::/40'): json.dumps({
                'id': None,
                'descendant_ids': [],
                'parent_ids': [7],
                'type': 'N',
                'children': [],
                'string': '13@2:2::/40',
            }),
        }
        matched = match_networks('13@2:2::/40')
        eq_(matched, {7})

    def test_search_trypo_no_trypo_in_cache(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96/28',
                '2a02:6b8:0:212::/64',
                '_TEST_CONSUMER_',
                '13@2:2::/40',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '77.88.40.96/28',
                '93.158.133.0/26',
                '2a02:6b8:0:212::/64',
            ]),
        }
        matched = match_networks('13@2:2::/40')
        ok_(not matched)

    def test_search_ip_no_ip_in_cache(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96',
                '_TEST_CONSUMER_',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '13@2:2::/40',
                '5@2a02:6b8:0:212::/64',
            ]),
        }
        matched = match_networks('77.88.40.96')
        ok_(not matched)

    def test_search_another_trypo(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96/28',
                '555@2a02:6b8:0:212::/64',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '13@2:2::/40',
                '5@2a02:6b8:0:212::/64',
            ]),
        }
        matched = match_networks('555@2a02:6b8:0:212::/64')
        ok_(not matched)

    def test_search_expanded_trypo(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96/28',
                '555@2a02:6b8:0:212::/64',
                '1329@2a02:6b8:c00::/40',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '13@2:2::/40',
                '5@2a02:6b8:0:212::/64',
                '1329@2a02:6b8:c00::/40',
            ]),
            get_network_redis_key('1329@2a02:6b8:c00::/40'): json.dumps({
                'id': 111,
                'descendant_ids': [],
                'parent_ids': [],
                'type': 'N',
                'children': [],
                'string': '1329@2a02:6b8:c00::/40',
            }),
        }
        matched = match_networks('2a02:6b8:c00:f80:0:1329::/96')
        ok_(matched, {111})

    def test_search_another_ip(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96/28',
                '2a02:6b8:0:212::/64',
                '_TEST_CONSUMER_',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '77.88.40.96/28',
                '93.158.133.0/26',
                '2a02:6b8:0:212::/64',
            ]),
        }
        matched = match_networks('192.168.1.10/1')
        ok_(not matched)

    def test_found_trypo(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96',
                '_TEST_CONSUMER_',
                '5@2a02:6b8:0:212::/64',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '13@2:2::/40',
                '5@2a02:6b8:0:212::/64',
            ]),
            get_network_redis_key('13@2:2::/40'): json.dumps({
                'id': 544,
                'descendant_ids': [],
                'parent_ids': [],
                'type': 'N',
                'children': [],
                'string': '13@2:2::/40',
            }),
        }
        matched = match_networks('13@2:2::/40')
        eq_(matched, {544})

    def test_found_ip(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '77.88.40.96',
                '5@2a02:6b8:0:212::/64',
            ]),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '77.88.40.96',
                '5@2a02:6b8:0:212::/64',
            ]),
            get_network_redis_key('77.88.40.96'): json.dumps({
                'id': 555,
                'descendant_ids': [],
                'parent_ids': [],
                'type': 'I',
                'children': [],
                'string': '77.88.40.96',
            }),
        }
        matched = match_networks('77.88.40.96')
        eq_(matched, {555})

    def test_mixed_descendants_trypo_overlapped(self):
        self.mock_redis.cache = {
            get_network_redis_key('known_network_list'): json.dumps([
                '_TEST_CONSUMER_',
            ]),
            get_network_redis_key('known_network_values'): json.dumps([
                {
                    'id': 3,
                    'string': '5@2a02:6b8:0:212::/64',
                    'type': 'N',
                },
                {
                    'id': 4,
                    'string': '77.88.40.96/28',
                    'type': 'N',
                }
            ]),
            get_network_redis_key('_test_consumer_'): json.dumps({
                'id': 1,
                'descendant_ids': [1, 2],
                'parent_ids': [],
                'type': 'F',
                'children': [
                    {
                        'id': None,
                        'descendant_ids': [],
                        'parent_ids': [1],
                        'type': 'N',
                        'children': [],
                        'string': '77.88.40.96/32',
                    },
                    {
                        'id': None,
                        'descendant_ids': [],
                        'parent_ids': [1],
                        'type': 'N',
                        'children': [],
                        'string': '5@2a02:6b8:0:212::/64',
                    },
                    {
                        'id': 2,
                        'descendant_ids': [2],
                        'parent_ids': [1],
                        'type': 'H',
                        'string': 'ttrust2f.balance.os.yandex.ru',
                        'children': [
                            {
                                'id': None,
                                'descendant_ids': [],
                                'parent_ids': [1, 2],
                                'type': 'I',
                                'children': [],
                                'string': '5.255.219.141',
                            },
                        ],
                    },
                ],
                'string': '_TEST_CONSUMER_',
            }),
            get_network_redis_key('known_ip_network_list'): json.dumps([
                '77.88.40.96/32',
                '5@2a02:6b8:0:212::/64',
            ]),
            get_network_redis_key('77.88.40.96/32'): json.dumps({
                'id': 3,
                'descendant_ids': [],
                'parent_ids': [],
                'type': 'N',
                'children': [],
                'string': '77.88.40.96/32',
            }),
            get_network_redis_key('5@2a02:6b8:0:212::/64'): json.dumps({
                'id': 4,
                'descendant_ids': [],
                'parent_ids': [5],
                'type': 'N',
                'children': [],
                'string': '5@2a02:6b8:0:212::/64',
            }),
            get_network_redis_key('5.255.219.141'): json.dumps({
                'id': None,
                'descendant_ids': [],
                'parent_ids': [1, 2],
                'type': 'I',
                'children': [],
                'string': '5.255.219.141',
            }),
        }
        matched = match_networks('_TEST_CONSUMER_', deep=True)
        eq_(matched, {1, 2, 5})
