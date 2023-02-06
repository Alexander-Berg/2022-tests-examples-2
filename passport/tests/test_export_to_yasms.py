# -*- coding: utf-8 -*-
import json

from StringIO import StringIO
from django.test import TestCase
from mock import (
    Mock,
    patch,
)

import passport_grants_configurator.apps.core.export_utils as export_utils
from passport_grants_configurator.apps.core.models import (
    Environment,
    Namespace,
)
from passport_grants_configurator.apps.core.exceptions import NetworkResolveError
from passport_grants_configurator.apps.core.test.utils import (
    MockRedis,
    MockNetworkApi,
)
from .test_data import *


class TestExportYaSMS(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.redis = MockRedis()
        self.redis.start()

        self.network_api = MockNetworkApi()
        self.network_api.start()

        self.setup_macros()
        self.setup_network_responses()

    def setup_macros(self):
        macro_map = {
            '_C_PASSPORT_GRANTUSHKA_STABLE_': [
                TEST_GRANTS_HOST1,
                TEST_GRANTS_HOST2,
            ],
        }
        self.network_api.setup_response(
            'expand_firewall_macro',
            macro_map,
        )

    def setup_network_responses(self):
        ip_map = {
            TEST_GRANTS_HOST1: [TEST_GRANTS_IP1],
            TEST_GRANTS_HOST2: [TEST_GRANTS_IP2],
        }
        self.network_api.setup_response('getipsfromaddr', ip_map)

    def tearDown(self):
        self.network_api.stop()
        self.redis.stop()

    def test_export(self):
        file_ = StringIO()
        environment = Environment.objects.get(id=1)  # localhost production
        namespace = Namespace.objects.get(name='yasms')

        export_utils.export_passport_like_grants_to_file(
            environment=environment,
            namespace=namespace,
            file_=file_,
            prefix='old_yasms_grants_'
        )
        self.assertEqual(
            json.loads(''.join(file_.buflist)),
            {
                'old_yasms_grants_yasms_consumer': {
                    'client': {},
                    'grants': {
                        'old_yasms_grants_yasms_grant': ['yasms_action'],
                    },
                    'networks': [
                        TEST_GRANTS_IP1,
                        TEST_GRANTS_IP2,
                        '2a02:6b8:0:107:c9d7:f28e:6e24:876f',
                        '2a02:6b8:0:811::/64',
                        '77.88.40.96/28',
                    ],
                },
                'old_yasms_grants_yasms_consumer_with_client': {
                    'grants': {
                        'old_yasms_grants_yasms_grant': ['yasms_action'],
                    },
                    'networks': [],
                    'client': {
                        'client_id': 1,
                        'client_name': 'Test Yasms Client With Consumer',
                    },
                },
            },
        )

    def test_network_resolver_error(self):
        file_ = StringIO()
        environment = Environment.objects.get(id=1)
        namespace = Namespace.objects.get(name='yasms')

        get_ips_adr = 'passport_grants_configurator.apps.core.network_apis.NetworkResolver.get_ips'
        with patch(get_ips_adr, Mock(side_effect=NetworkResolveError('test'))):
            exported = export_utils.export_passport_like_grants_to_file(
                environment=environment,
                file_=file_,
                namespace=namespace,
            )

        self.assertEqual(
            exported,
            {
                u'errors': [],
                u'warnings': [],
                u'manual_resolve': [
                    u'ОШИБКА - сеть "_C_PASSPORT_GRANTUSHKA_STABLE_", потребитель "yasms_consumer": test',
                    u'ОШИБКА - сеть "77.88.40.96/28", потребитель "yasms_consumer": test',
                    u'ОШИБКА - сеть "2a02:6b8:0:107:c9d7:f28e:6e24:876f", потребитель "yasms_consumer": test',
                    u'ОШИБКА - сеть "2a02:6b8:0:811::/64", потребитель "yasms_consumer": test',
                ],
            },
        )
