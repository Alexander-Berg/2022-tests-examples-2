# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from StringIO import StringIO
import json

from django.test import TestCase
from mock import Mock, patch

import passport_grants_configurator.apps.core.export_utils as export_utils
from passport_grants_configurator.apps.core.models import Environment, Namespace
from passport_grants_configurator.apps.core.exceptions import NetworkResolveError
from passport_grants_configurator.apps.core.test.utils import (
    MockRequests,
    MockRedis,
)


class TestExportOAuth(TestCase):
    maxDiff = None
    fixtures = ['default.json']

    def setUp(self):
        self.requests = MockRequests()
        self.requests.start()
        self.redis = MockRedis()
        self.redis.start()

    def tearDown(self):
        self.redis.stop()
        self.requests.stop()

    def test_export(self):
        file_ = StringIO()
        environment = Environment.objects.get(id=1)
        namespace = Namespace.objects.get(name='oauth')

        export_utils.export_oauth_grants_to_file(environment=environment, namespace=namespace, file_=file_)
        self.assertEqual(json.loads(''.join(file_.buflist)),
        {
            'oauth_consumer': {
                'client': {},
                'grants': {
                    'client': [
                        '*'
                    ],
                    'grant_type': [
                        'assertion'
                    ]
                },
                'networks': [
                    '127.0.0.1'
                ]
            },
            'oauth_consumer_with_client': {
                'client': {
                    'client_id': 1,
                    'client_name': 'Test Oauth Client With Consumer'
                },
                'grants': {
                    'grant_type': [
                        'assertion'
                    ]
                },
                'networks': []
            },
        })

    def test_network_resolver_error(self):
        file_ = StringIO()
        environment = Environment.objects.get(id=1)
        namespace = Namespace.objects.get(name='oauth')

        get_ips_adr = 'passport_grants_configurator.apps.core.network_apis.NetworkResolver.get_ips'
        with patch(get_ips_adr, Mock(side_effect=NetworkResolveError('test'))):
            exported = export_utils.export_oauth_grants_to_file(
                environment=environment,
                file_=file_,
                namespace=namespace,
            )

        self.assertEqual(
            exported,
            {
                'errors': [],
                'manual_resolve': [
                    'ОШИБКА - сеть "127.0.0.1", потребитель "oauth_consumer": test',
                ],
                'warnings': [],
            }
        )
