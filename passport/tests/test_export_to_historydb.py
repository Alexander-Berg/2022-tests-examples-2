# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from StringIO import StringIO
import json

from django.test import TestCase

import passport_grants_configurator.apps.core.export_utils as export_utils
from passport_grants_configurator.apps.core.models import Environment, Namespace
from passport_grants_configurator.apps.core.test.utils import (
    MockRequests,
    MockRedis,
)


class TestExportHistorydb(TestCase):
    maxDiff = None
    fixtures = ['default.json']

    def setUp(self):
        self.requests = MockRequests()
        self.requests.start()
        self.redis = MockRedis()
        self.redis.start()

        self.mock_file = StringIO()
        self.environment = Environment.objects.get(id=2)    # localhost testing
        self.namespace = Namespace.objects.get(name='historydb')

    def tearDown(self):
        self.redis.stop()
        self.requests.stop()

    def test_export_to_file(self):
        export_utils.export_passport_like_grants_to_file(
            self.environment,
            self.mock_file,
            namespace=self.namespace,
        )
        self.assertItemsEqual(
            json.loads(''.join(self.mock_file.buflist)),
            {
                'hdb_consumer_with_client': {
                    'client': {
                        'client_id': 2,
                        'client_name': u'Test HistoryDB Client With Consumer',
                    },
                    'grants': {'account': ['auths']},
                    u'networks': [],
                },
                'hdb_consumer': {
                    'client': {},
                    'grants': {'account': ['events']},
                    'networks': [
                        '77.88.40.96/28',
                        '2a02:6b8:0:811::/64',
                    ],
                },
            },
        )
