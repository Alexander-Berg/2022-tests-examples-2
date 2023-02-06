# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from StringIO import StringIO

from django.test import TestCase
from mock import Mock, patch

import passport_grants_configurator.apps.core.export_utils as export_utils
from passport_grants_configurator.apps.core.models import Environment, Namespace
from passport_grants_configurator.apps.core.exceptions import NetworkResolveError
from passport_grants_configurator.apps.core.test.utils import (
    MockRedis,
    MockNetworkApi,
)
from .test_data import *


class TestExportSocial(TestCase):
    maxDiff = None
    fixtures = ['default.json']

    def setUp(self):
        self.redis = MockRedis()
        self.redis.start()

        self.network_api = MockNetworkApi()
        self.network_api.start()

        self.setup_macros()
        self.setup_network_responses()

    def setup_macros(self):
        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                '_C_PASSPORT_GRANTUSHKA_STABLE_': [
                    TEST_GRANTS_HOST1,
                    TEST_GRANTS_HOST2,
                ],
            },
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
        environment = Environment.objects.get(id=1)
        namespace = Namespace.objects.get(id=4)

        export_utils.export_social_grants_to_file(environment, namespace, file_)

        self.assertEqual(
            json.loads(''.join(file_.buflist)),
            {
                'social_api_consumer': {
                    'networks': [TEST_GRANTS_IP1, TEST_GRANTS_IP2],
                    'grants': [
                        'social_api_grant-social_api_action',
                        'social_api_grant_with_asterisk',
                    ],
                    'client': {},
                },
                'social_api_consumer_with_client': {
                    'networks': [],
                    'grants': ['social_api_grant-social_api_action'],
                    'client': {
                        'client_id': 1,
                        'client_name': 'Test Social API Client With Consumer',
                    },
                },
            },
        )

    def test_network_resolver_error(self):
        file_ = StringIO()
        environment = Environment.objects.get(id=1)
        namespace = Namespace.objects.get(id=4)

        get_ips_adr = 'passport_grants_configurator.apps.core.network_apis.NetworkResolver.get_ips'
        with patch(get_ips_adr, Mock(side_effect=NetworkResolveError('test'))):
            exported = export_utils.export_social_grants_to_file(environment, namespace, file_)

        self.assertEqual(
            exported,
            {
                'errors': [],
                'manual_resolve': [
                    'ОШИБКА - сеть "_C_PASSPORT_GRANTUSHKA_STABLE_", потребитель "social_api_consumer": test'
                ],
                'warnings': [],
            },
        )
