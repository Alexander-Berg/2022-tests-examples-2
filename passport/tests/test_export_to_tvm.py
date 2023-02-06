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


class TestExportTVM(TestCase):
    maxDiff = None
    fixtures = ['default.json']
    namespace = 'tvm-api'

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
        namespace = Namespace.objects.get(name=self.namespace)

        export_utils.export_tvm_api_grants_to_file(environment=environment, namespace=namespace, file_=file_)
        self.assertEqual(json.loads(''.join(file_.buflist)),
        {
            'tvm_consumer': {
                'grants': {
                    'tvm_api': [
                        'manage_clients'
                    ]
                },
                'networks': [
                    '2a02:6b8:0:811::/64'
                ]
            }
        })

    def test_network_resolver_error(self):
        file_ = StringIO()
        environment = Environment.objects.get(id=1)
        namespace = Namespace.objects.get(name=self.namespace)

        get_ips_adr = 'passport_grants_configurator.apps.core.network_apis.NetworkResolver.get_ips'
        with patch(get_ips_adr, Mock(side_effect=NetworkResolveError('test'))):
            exported = export_utils.export_tvm_api_grants_to_file(
                environment=environment,
                file_=file_,
                namespace=namespace,
            )

        self.assertEqual(
            exported,
            {
                'errors': [],
                'manual_resolve': [
                    'ОШИБКА - сеть "2a02:6b8:0:811::/64", потребитель "tvm_consumer": test',
                ],
                'warnings': [],
            }
        )
