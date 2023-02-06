# -*- coding: utf-8 -*-
import json

from io import BytesIO
from dns.exception import DNSException
from django.test import TestCase


import passport_grants_configurator.apps.core.export_utils as export_utils
from passport_grants_configurator.apps.core.exceptions import (
    NetworkResolveError,
    NotFoundError,
)
from passport_grants_configurator.apps.core.models import (
    Environment,
    Network,
    PreviousResolve,
)
from passport_grants_configurator.apps.core.test.utils import (
    MockRedis,
    MockNetworkApi,
)
from .test_data import *


class TestExportBlackboxByClient(TestCase):
    fixtures = ['default.json']
    maxDiff = None

    def setUp(self):
        self.buffer = BytesIO()
        self.environment = Environment.objects.get(id=2)

        self.redis = MockRedis()
        self.redis.start()
        self.network = MockNetworkApi()
        self.network.start()

    def tearDown(self):
        self.network.stop()
        self.redis.stop()

    def setup_networks_response(self):
        self.redis.mock.get.side_effect = [
            json.dumps([
                '87.250.232.64/27',
                '93.158.133.0/26',
                '95.108.158.0/26',
                '95.108.225.128/26',
                '178.154.221.128/25',
                '2a02:6b8:0:212::/64',
                '2a02:6b8:0:811::/64',
                '2a02:6b8:0:c37::/64',
                '2a02:6b8:0:142b::/64',
                '2a02:6b8:0:1a41::/64',
                'pooh::/64',
                '123@2a02:6b8:0::/40',
            ]),
            json.dumps([
                '37.140.181.0/28',
            ]),
        ]
        self.network.setup_response('get_conductor_group_hosts', {
            '%passport-grantushka-stable': [
                TEST_GRANTS_HOST1,
                TEST_GRANTS_HOST2,
            ],
        })
        self.network.setup_response('getipsfromaddr', {
            'pooh::/64': ['2a02:6b8:0:811::/64'],
            'grantushka.yandex-team.ru': ['87.250.232.64/27'],
            TEST_GRANTS_HOST1: ['2a02:6b8:0:142b::/64', '2a02:6b8:0:1626::8'],
            TEST_GRANTS_HOST2: ['2a02:6b8:0:250b::/64'],
        })

    def setup_previous_response(self):
        network = Network.objects.get(string='_YET_ANOTHER_TEST_MACRO_')
        previous = PreviousResolve.objects.get(network=network)
        previous.children = json.dumps(['37.140.181.0/28'])
        previous.save()

    def expected_export(self):
        default_networks = [
            '37.140.181.0/28',
            '2a02:6b8:0:107:c9d7:f28e:6e24:876f',
            '87.250.232.64/27',
            '93.158.133.0/26',
            '95.108.158.0/26',
            '95.108.225.128/26',
            '178.154.221.128/25',
            '2a02:6b8:0:212::/64',
            '2a02:6b8:0:811::/64',
            '2a02:6b8:0:c37::/64',
            '2a02:6b8:0:142b::/64',
            '2a02:6b8:0:1a41::/64',
            '2a02:6b8:0:250b::/64',
            '2a02:6b8:0:1626::8',
            '123@2a02:6b8:0::/40',
            '::/0',
        ]
        result = {
            'blackbox_by_client_consumer': {
                'client': {
                    'client_id': 1,
                    'client_name': 'Test Client',
                },
                'grants': {
                    'can_delay': ['*'],
                    'allowed_attributes': ['*'],
                },
                'networks': sorted(default_networks),
            },
        }
        return result

    def test_export(self):
        self.setup_previous_response()
        self.setup_networks_response()
        export_utils.export_blackbox_by_client_grants_to_file(self.environment, self.buffer)
        self.assertEqual(json.loads(self.buffer.getvalue()), self.expected_export())

    def test_export_with_resolve_warnings(self):
        self.setup_previous_response()
        self.setup_networks_response()
        self.network.setup_response('get_conductor_group_hosts', {
            '%passport-grantushka-stable': NotFoundError(),
        })
        self.network.setup_response('getipsfromaddr', {
            'pooh::/64': NetworkResolveError(),
            'grantushka.yandex-team.ru': DNSException(),
        })
        result = export_utils.export_blackbox_by_client_grants_to_file(self.environment, self.buffer)
        warnings = ['grantushka.yandex-team.ru']
        expected_result = {
            u'manual_resolve': [
                export_utils.format_network_resolve_message(
                    export_utils.NETWORK_RESOLVE_ERROR,
                    '%passport-grantushka-stable',
                    'blackbox_by_client_consumer',
                    export_utils.format_unresolved_macros(),
                ),
            ],
            u'warnings': [
                export_utils.format_network_resolve_message(
                    export_utils.NETWORK_RESOLVE_WARNING,
                    '_KOPALKA_',
                    'blackbox_by_client_consumer',
                    export_utils.format_unresolved_networks(['pooh::/64']),
                ),
                export_utils.format_network_resolve_message(
                    export_utils.NETWORK_RESOLVE_WARNING,
                    'grantushka.yandex-team.ru',
                    'blackbox_by_client_consumer',
                    export_utils.format_unresolved_networks(warnings),
                ),
            ],
            u'errors': [],
        }
        self.assertDictEqual(result, expected_result)
        diff = json.loads(self.buffer.getvalue())
        diff['blackbox_by_client_consumer']['networks'].sort()
        expected_diff = self.expected_export()
        expected_diff['blackbox_by_client_consumer']['networks'].remove('2a02:6b8:0:1626::8')
        expected_diff['blackbox_by_client_consumer']['networks'].remove('2a02:6b8:0:250b::/64')
        self.assertDictEqual(diff, expected_diff)

    def test_export_with_excluded(self):
        self.setup_previous_response()
        self.setup_networks_response()
        self.network.setup_response('getipsfromaddr', {
            TEST_GRANTS_HOST1: [TEST_IP_LOCALHOST_6, '2a02:6b8:0:142b::/64', '2a02:6b8:0:1626::8'],
        })
        result = export_utils.export_blackbox_by_client_grants_to_file(self.environment, self.buffer)
        excluded = [TEST_IP_LOCALHOST_6]
        expected_result = {
            u'manual_resolve': [],
            u'warnings': [
                export_utils.format_network_resolve_message(
                    export_utils.NETWORK_RESOLVE_WARNING,
                    '%passport-grantushka-stable',
                    'blackbox_by_client_consumer',
                    export_utils.format_excluded_ips_and_nets(excluded),
                ),
            ],
            u'errors': [],
        }
        self.assertDictEqual(result, expected_result)
        diff = json.loads(self.buffer.getvalue())
        diff['blackbox_by_client_consumer']['networks'].sort()
        expected_diff = self.expected_export()
        self.assertDictEqual(diff, expected_diff)

    def test_export_with_decreased(self):
        self.setup_networks_response()
        macro_name = '_YET_ANOTHER_TEST_MACRO_'
        result = export_utils.export_blackbox_by_client_grants_to_file(self.environment, self.buffer)
        expected_result = {
            u'manual_resolve': [
                export_utils.format_network_resolve_message(
                    export_utils.NETWORK_RESOLVE_ERROR,
                    macro_name,
                    'blackbox_by_client_consumer',
                    export_utils.format_network_decreased_message(
                        'F',
                        {
                            'name': macro_name,
                            'old': [
                                '87.250.252.17',
                                '2a02:6b8:0:1626::8',
                                '123@2a02:6b8:0::/40',
                                'test.com',
                                'fake.test.com',
                                'fake.com',
                            ],
                            'new': ['37.140.181.0/28'],
                        },
                    ),
                ),
            ],
            u'warnings': [],
            u'errors': [],
        }
        self.assertDictEqual(result, expected_result)

    def test_export_with_force_update(self):
        self.setup_networks_response()
        export_utils.export_blackbox_by_client_grants_to_file(self.environment, self.buffer, force_update=True)
        expected_export = self.expected_export()
        self.assertEqual(json.loads(self.buffer.getvalue()), expected_export)
