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


class TestExportTakeout(TestCase):
    maxDiff = None
    fixtures = ['default.json']
    namespace = 'takeout'

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

        export_utils.export_passport_like_grants_to_file(environment=environment, namespace=namespace, file_=file_)
        self.assertEqual(
            json.loads(''.join(file_.buflist)),
            {
                'takeout_consumer': {
                    'client': {},
                    'grants': {
                        u'money': [u'take'],
                    },
                    'networks': [
                        '2a02:6b8:0:107:c9d7:f28e:6e24:876f',
                    ],
                },
            },
        )
