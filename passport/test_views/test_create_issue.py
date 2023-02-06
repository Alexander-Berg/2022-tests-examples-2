# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.test import (
    Client,
    TestCase,
)
from passport_grants_configurator.apps.core.models import Namespace

from passport_grants_configurator.apps.core.test.utils import MockUserPermissions
from passport_grants_configurator.apps.core.tests.test_views import TEST_LOGIN


class IssueFormCase(TestCase):
    maxDiff = None
    fixtures = ['default.json']
    namespace_consumers = [
        {
            u'consumers': {
                u'bb_consumer': {
                    u'description': u'bb consumer',
                    u'id': 3,
                },
                u'bb_empty_consumer': {
                    u'description': u'bb consumer',
                    u'id': 7,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
                {
                    u'description': u'intranet production',
                    u'id': 4,
                },
                {
                    u'description': u'stress',
                    u'id': 7,
                },
                {
                    u'description': u'other production',
                    u'id': 8,
                },
            ],
            'id': 7,
            'name': u'blackbox',
            'by_client': False,
            'client_required': False,
        },
        {
            u'consumers': {
                u'blackbox_by_client_consumer': {
                    u'description': u'blackbox_by_client consumer description',
                    u'id': 10,
                },
            },
            u'environments': [
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
            ],
            u'id': 10,
            u'name': u'blackbox_by_client',
            u'by_client': True,
            'client_required': True,
        },
        {
            u'by_client': True,
            u'client_required': False,
            u'consumers': {
                u'hdb_consumer_with_client': {
                    u'description': u'HistoryDB Consumer With Client',
                    u'id': 12,
                },
                u'hdb_consumer': {
                    u'description': u'HistoryDB Consumer',
                    u'id': 13,
                },
            },
            u'environments': [{u'description': u'testing', u'id': 2}],
            u'id': 11,
            u'name': u'historydb',
        },
        {
            u'consumers': {
                u'oauth_consumer': {
                    u'description': u'oauth consumer description',
                    u'id': 9,
                },
                u'oauth_consumer_with_client': {
                    u'description': u'Oauth Consumer With Client',
                    u'id': 15,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
                {
                    u'description': u'intranet production',
                    u'id': 4,
                },
                {
                    u'description': u'stress',
                    u'id': 7,
                },
            ],
            u'id': 8,
            u'name': u'oauth',
            u'by_client': True,
            'client_required': False,
        },
        {
            u'consumers': {
                u'empty_passport_consumer': {
                    u'description': u'empty passport consumer',
                    u'id': 8,
                },
                u'some_consumer': {
                    u'description': u'Это some_consumer',
                    u'id': 1,
                },
                'consumer_with_client': {
                    'description': 'Passport Consumer With Client',
                    'id': 11,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
                {
                    u'description': u'intranet production',
                    u'id': 4,
                },
                {
                    u'description': u'intranet testing',
                    u'id': 5,
                },
                {
                    u'description': u'intranet development',
                    u'id': 6,
                },
                {
                    u'description': u'stress',
                    u'id': 7,
                },
            ],
            u'id': 1,
            u'name': u'passport',
            u'by_client': True,
            'client_required': False,
        },

        {
            u'consumers': {
                u'social_api_consumer': {
                    u'description': u'social api cnsumer',
                    u'id': 4,
                },
                u'social_api_consumer_with_client': {
                    u'description': u'Social API Consumer With Client',
                    u'id': 16,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
            ],
            u'id': 4,
            u'name': u'social api',
            u'by_client': True,
            'client_required': False,
        },
        {
            u'consumers': {
                u'social_proxy_consumer': {
                    u'description': u'social proxy consumer',
                    u'id': 5,
                },
                u'social_proxy_consumer_with_client': {
                    u'description': u'Social Proxy Consumer With Client',
                    u'id': 17,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
            ],
            u'id': 5,
            u'name': u'social proxy',
            u'by_client': True,
            'client_required': False,
        },
        {
            u'consumers': {
                u'space2_consumer': {
                    u'description': u'space2 consumer',
                    u'id': 2,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
            ],
            u'id': 2,
            u'name': u'space2',
            u'by_client': False,
            'client_required': False,
        },
        {
            u'consumers': {
                u'takeout_consumer': {
                    u'description': u'Takeout Consumer',
                    u'id': 19,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
            ],
            u'id': 13,
            u'name': u'takeout',
            u'by_client': True,
            'client_required': False,
        },
        {
            u'consumers': {
                u'tvm_consumer': {
                    u'description': u'tvm consumer description',
                    u'id': 14,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
            ],
            u'id': 12,
            u'name': u'tvm-api',
            u'by_client': False,
            'client_required': False,
        },
        {
            u'consumers': {
                u'yasms_consumer': {
                    u'description': u'yasms_consumer',
                    u'id': 6,
                },
                u'yasms_consumer_with_client': {
                    u'description': u'Yasms Consumer With Client',
                    u'id': 18,
                },
            },
            u'environments': [
                {
                    u'description': u'production',
                    u'id': 1,
                },
                {
                    u'description': u'testing',
                    u'id': 2,
                },
                {
                    u'description': u'development',
                    u'id': 3,
                },
                {
                    u'description': u'rc',
                    u'id': 9,
                },
            ],
            u'id': 6,
            u'name': u'yasms',
            u'by_client': True,
            'client_required': False,
        },
    ]
    url = '/grants/issue/edit/'
    clone_url = '/grants/issue/clone/'

    def setUp(self):
        self.client = Client()
        self.mock_user_permissions = MockUserPermissions(
            'passport_grants_configurator.apps.core.permissions.UserPermissions',
        )
        self.mock_user_permissions.start()

    def tearDown(self):
        self.mock_user_permissions.stop()

    def test_create_issue(self):

        admin_namespaces = ['blackbox']

        with self.settings(
            PASSPORT_TEAM_ADMIN=['test-admin'],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            context = self.client.get(self.url).context
            self.assertEqual(json.loads(
                context['editable_namespaces']),
                [n.id for n in Namespace.objects.exclude(name__in=admin_namespaces)],
            )
            self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
            self.assertEqual(json.loads(context['issue']), {
                u'consumer_description': u'',
                u'consumer_description_new': u'',
                u'consumer_name': u'',
                u'consumer_name_new': u'',
                u'environments_id': [1],
                u'id': None,
                u'namespace': 7,  # ordering by alphabet
                u'type': u'C',
            })

        with self.settings(
            PASSPORT_TEAM_ADMIN=[TEST_LOGIN, 'test-admin'],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            context = self.client.get(self.url).context
            self.assertEqual(json.loads(
                context['editable_namespaces']),
                [n.id for n in Namespace.objects.all()],
            )

    def test_create_issue_with_issue(self):
        admin_namespaces = ['blackbox']

        with self.settings(
            PASSPORT_TEAM_ADMIN=['test-admin'],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            context = self.client.get('%s?issue=1' % self.url).context
            self.assertEqual(json.loads(
                context['editable_namespaces']),
                [n.id for n in Namespace.objects.exclude(name__in=admin_namespaces)],
            )
            self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
            self.assertEqual(json.loads(context['issue']), {
            u'clients': {},
            u'consumer_description': u'',
            u'consumer_description_new': u'',
            u'consumer_name': u'new_consumer',
            u'consumer_name_new': u'',
            u'emails': [],
            u'environments_id': [1],
            u'expiration_date': None,
            u'id': 1,
            u'namespace': 1,
            u'type': u'C',
        })

        with self.settings(
            PASSPORT_TEAM_ADMIN=[TEST_LOGIN],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            context = self.client.get('%s?issue=1' % self.url).context
            self.assertEqual(json.loads(
                context['editable_namespaces']),
                [n.id for n in Namespace.objects.all()],
            )
            self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
            self.assertEqual(json.loads(context['issue']), {
                u'clients': {},
                u'consumer_description': u'',
                u'consumer_description_new': u'',
                u'consumer_name': u'new_consumer',
                u'consumer_name_new': u'',
                u'emails': [],
                u'environments_id': [1],
                u'expiration_date': None,
                u'id': 1,
                u'namespace': 1,
                u'type': u'C',
            })

    def test_create_issue_with_consumer(self):
        admin_namespaces = ['blackbox']

        with self.settings(
                PASSPORT_TEAM_ADMIN=['test-admin'],
                NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            context = self.client.get('%s?issue=2' % self.url).context
            self.assertEqual(json.loads(
                context['editable_namespaces']),
                [n.id for n in Namespace.objects.exclude(name__in=admin_namespaces)],
            )
            self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
            self.assertEqual(json.loads(context['issue']), {
            u'clients': {},
            u'consumer_description': u'Это some_consumer',
            u'consumer_description_new': u'changed description',
            u'consumer_name': u'some_consumer',
            u'consumer_name_new': u'new_name',
            u'emails': [],
            u'environments_id': [1],
            u'expiration_date': None,
            u'id': 2,
            u'namespace': 1,
            u'type': u'M',
        })

        with self.settings(
                PASSPORT_TEAM_ADMIN=[TEST_LOGIN],
                NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            context = self.client.get('%s?issue=2' % self.url).context

            self.assertEqual(json.loads(
                context['editable_namespaces']),
                [n.id for n in Namespace.objects.all()],
            )
            self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
            self.assertEqual(json.loads(context['issue']), {
                u'clients': {},
                u'consumer_description': u'Это some_consumer',
                u'consumer_description_new': u'changed description',
                u'consumer_name': u'some_consumer',
                u'consumer_name_new': u'new_name',
                u'emails': [],
                u'environments_id': [1],
                u'expiration_date': None,
                u'id': 2,
                u'namespace': 1,
                u'type': u'M',
            })

    def test_clone_issue_with_consumer(self):
        admin_namespaces = ['passport']
        with self.settings(
            PASSPORT_TEAM_ADMIN=['test-admin'],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            context = self.client.get(self.clone_url, {
                'consumer': 1,
                'environment': 3,
            }).context
            self.assertEqual(json.loads(
                context['editable_namespaces']),
                [n.id for n in Namespace.objects.exclude(name__in=admin_namespaces)],
            )
            self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
            self.assertEqual(json.loads(context['issue']), {
                u'clients': {},
                u'consumer_description': u'Это some_consumer',
                u'consumer_description_new': u'Это some_consumer',
                u'consumer_name': u'some_consumer',
                u'consumer_name_new': u'',
                u'environments_id': [3],
                u'id': None,
                u'namespace': 1,
                u'type': u'CC',
            })

        with self.settings(
            PASSPORT_TEAM_ADMIN=[TEST_LOGIN],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            context = self.client.get(self.clone_url, {
                'consumer': 1,
                'environment': 3,
            }).context
            self.assertEqual(json.loads(
                context['editable_namespaces']),
                [n.id for n in Namespace.objects.all()],
            )
            self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
            self.assertEqual(json.loads(context['issue']), {
                u'clients': {},
                u'consumer_description': u'Это some_consumer',
                u'consumer_description_new': u'Это some_consumer',
                u'consumer_name': u'some_consumer',
                u'consumer_name_new': u'',
                u'environments_id': [3],
                u'id': None,
                u'namespace': 1,
                u'type': u'CC',
            })

    def test_create_issue_request_environment_consumer_and_namespace(self):
        context = self.client.get(self.url, {
            'consumer': 1,
            'environment': 3,
            'namespace': 1
        }).context

        self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
        self.assertEqual(json.loads(context['issue']), {
            u'clients': {},
            u'consumer_description': u'Это some_consumer',
            u'consumer_description_new': u'Это some_consumer',
            u'consumer_name': u'some_consumer',
            u'consumer_name_new': u'',
            u'environments_id': [3],
            u'id': None,
            u'namespace': 1,
            u'type': u'M',
        })

    def test_nonexistent_id(self):
        request = self.client.get(self.url, {'issue': 100500})

        self.assertEqual(request.status_code, 404)

    def test_create_issue_with_client(self):
        context = self.client.get(self.url, {
            'consumer': 11,
            'environment': 1,
            'namespace': 1,
        }).context

        self.assertEqual(json.loads(context['namespace_consumers']), self.namespace_consumers)
        self.assertEqual(json.loads(context['issue']), {
            'clients': {
                '1': {
                    'id': 4,
                    'name': 'Test Passport Client With Consumer',
                    'client_id': 2,
                },
            },
            'consumer_description': 'Passport Consumer With Client',
            'consumer_description_new': 'Passport Consumer With Client',
            'consumer_name': 'consumer_with_client',
            'consumer_name_new': '',
            'environments_id': [1],
            'id': None,
            'namespace': 1,
            'type': u'M',
        })
