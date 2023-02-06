# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from passport_grants_configurator.apps.core.models import (
    Action,
    ActiveAction,
    ActiveMacros,
    Client,
    Consumer,
    Environment,
    Issue,
    Macros,
    Namespace,
    NamespaceEnvironments,
    Network,
)
from passport_grants_configurator.apps.core.test.utils import MockUserPermissions
from passport_grants_configurator.apps.core.utils import deep_merge
from passport_grants_configurator.apps.core.views import issue_review

TEST_CLIENT_PK_WITH_CONSUMER = 1
TEST_CONSUMER_PK_WITH_CLIENT = 10
TEST_CLIENT_PK = 2


class GetConsumerDataCase(TestCase):
    fixtures = ['default.json']
    maxDiff = None

    url = '/grants/issue/review/'

    def setUp(self):
        self.mock_user_permissions = MockUserPermissions(
            'passport_grants_configurator.apps.core.views.issue.UserPermissions'
        )
        self.mock_user_permissions.start()
        self.factory = RequestFactory()
        self.user = User.objects.get(id=1)

    def tearDown(self):
        self.mock_user_permissions.stop()

    def make_request(self, data):
        request = self.factory.post(self.url, data)
        self.user.is_superuser = True
        self.user.save()
        request.user = self.user
        return issue_review(request)

    def test_review_consumer_creation_issue(self):
        data = {
            'issue': 1,
            'result': 'confirmed',
        }

        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'confirmed',
        })

        namespace = Namespace.objects.get(id=1)
        environment = Environment.objects.get(id=1)
        consumer = Consumer.objects.get(name='new_consumer', namespace=namespace)

        self.assertEqual(
            set(Action.objects.filter(activeaction__consumer=consumer, activeaction__environment=environment)),
            {
                Action.objects.get(name='create', grant__name='session'),
                Action.objects.get(name='validate', grant__name='password')
            },
        )
        self.assertEqual(
            set(Macros.objects.filter(activemacros__consumer=consumer, activemacros__environment=environment)),
            {Macros.objects.get(name='some_macros2')},
        )
        self.assertEqual(
            set(Network.objects.filter(activenetwork__consumer=consumer, activenetwork__environment=environment)),
            {Network.objects.get(string='127.0.0.2', type=Network.IP)}
        )

    def test_review_consumer_alteration_issue(self):
        namespace = Namespace.objects.get(id=1)
        environment = Environment.objects.get(id=1)
        consumer = Consumer.objects.get(name='some_consumer', namespace=namespace)

        data = {
            'issue': 2,
            'result': 'confirmed',
        }

        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'confirmed',
        })

        self.assertEqual(
            set(Action.objects.filter(activeaction__consumer=consumer, activeaction__environment=environment)),
            {
                Action.objects.get(name='create', grant__name='session'),
                Action.objects.get(name='check', grant__name='session'),
                Action.objects.get(name='is_changing_required', grant__name='password'),
                Action.objects.get(name='something.create', grant__name='subscription'),
            },
        )
        self.assertEqual(
            set(Macros.objects.filter(activemacros__consumer=consumer, activemacros__environment=environment)),
            {Macros.objects.get(name='some_macros2')}
        )
        self.assertEqual(
            set(Network.objects.filter(activenetwork__consumer=consumer, activenetwork__environment=environment)),
            {
                Network.objects.get(string='127.0.0.2', type=Network.IP),
                Network.objects.get(string='127.0.0.3', type=Network.IP),
                Network.objects.get(string='grantushka.yandex-team.ru', type=Network.HOSTNAME),
                Network.objects.get(string='%passport-grantushka-stable', type=Network.CONDUCTOR),
                Network.objects.get(string='_KOPALKA_', type=Network.FIREWALL),
            }
        )

    def test_review_temporal_grants_assignment_issue(self):
        namespace = Namespace.objects.get(id=1)
        consumer = Consumer.objects.get(name='some_consumer', namespace=namespace)

        data = {
            'issue': 4,
            'result': 'confirmed',
        }

        actions_pre_approve_values = [
            {
                'action_id': 2,
                'consumer_id': 1,
                'environment_id': 1,
                'expiration': None,
                'id': 1,
            },
            {
                'action_id': 3,
                'consumer_id': 1,
                'environment_id': 1,
                'expiration': None,
                'id': 2,
            },
            {
                'action_id': 5,
                'consumer_id': 1,
                'environment_id': 1,
                'expiration': None,
                'id': 3,
            },
            {
                'action_id': 7,
                'consumer_id': 1,
                'environment_id': 1,
                'expiration': None,
                'id': 4,
            },
            {
                'action_id': 15,
                'consumer_id': 1,
                'environment_id': 1,
                'expiration': None,
                'id': 11,
            },
        ]
        macroses_pre_approve_values = [{
            'consumer_id': 1,
            'environment_id': 1,
            'expiration': None,
            'id': 1,
            'macros_id': 1
        }]

        self.assertEqual(
            list(ActiveAction.objects.filter(consumer=consumer).values().order_by('id')),
            actions_pre_approve_values,
        )
        self.assertEqual(
            list(ActiveMacros.objects.filter(consumer=consumer).values().order_by('id')),
            macroses_pre_approve_values,
        )
        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'confirmed',
        })

        self.assertEqual(
            list(ActiveAction.objects.filter(consumer=consumer).values().order_by('id')),
            deep_merge(actions_pre_approve_values, [
                None,
                None,
                None,
                {
                    'expiration': datetime.date(2016, 10, 20),
                },
                None,
                {
                    'action_id': 6,
                    'consumer_id': 1,
                    'environment_id': 1,
                    'expiration': datetime.date(2016, 10, 20),
                    'id': ActiveAction.objects.latest('id').id,
                }
            ])
        )
        self.assertEqual(
            list(ActiveMacros.objects.filter(consumer=consumer).values().order_by('id')),
            deep_merge(macroses_pre_approve_values, [
                None,
                {
                    'consumer_id': 1,
                    'environment_id': 1,
                    'expiration': datetime.date(2016, 10, 20),
                    'id': 6,
                    'macros_id': 2
                }
            ])
        )

    def test_reject_consumer_creation_issue(self):
        data = {
            'issue': 1,
            'result': 'rejected',
        }

        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'rejected',
        })

        namespace = Namespace.objects.get(id=1)
        self.assertRaises(Consumer.DoesNotExist, Consumer.objects.get, **dict(name='new consumer', namespace=namespace))

    def test_no_id_in_params(self):
        data = {
            'result': 'confirmed',
        }

        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [u'issue: Обязательное поле.'],
            'success': False,
        })

    def test_issue_with_nonexistent_id(self):
        data = {
            'issue': 100500,
            'result': 'confirmed',
        }

        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [u'issue: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'],
            'success': False,
        })

    def test_confirmation_without_access_rights(self):
        data = {
            'issue': 1,
            'result': 'confirmed',
        }
        self.mock_user_permissions.UserPermissions.do_not_have.return_value = [NamespaceEnvironments.objects.get(id=1)]

        request = self.factory.post(self.url, data)
        request.user = self.user

        response = issue_review(request)

        self.assertEqual(json.loads(response.content), {
            'errors': [u'У Вас нет прав для действий с заявкой в окружении(ях): passport - production'],
            'success': False,
        })

    def test_try_to_approve_draft(self):
        data = {
            'issue': 1,
            'result': 'confirmed',
        }

        issue = Issue.objects.get(id=1)
        issue.status = Issue.DRAFT
        issue.save()

        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [u'issue: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'],
            'success': False,
        })

    def test_review_without_status(self):
        data = {'issue': 1}

        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [u'result: Обязательное поле.'],
            'success': False,
        })

    def test_review_with_clients_approved(self):
        client = Client.objects.get(pk=TEST_CLIENT_PK)
        self.assertIsNone(client.consumer)
        data = {
            'issue': 5,
            'result': 'confirmed',
        }

        with self.settings(
            PASSPORT_TEAM_ADMIN=[self.user.username],
            NAMESPACES_FOR_ADMINS=['blackbox_by_client'],
        ):
            response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'confirmed',
        })

        namespace = Namespace.objects.get(id=10)
        environment = Environment.objects.get(id=2)
        consumer = Consumer.objects.get(name='new_consumer', namespace=namespace)
        client = Client.objects.get(pk=TEST_CLIENT_PK)
        self.assertEqual(client.consumer, consumer)

        self.assertEqual(
            set(Action.objects.filter(activeaction__consumer=consumer, activeaction__environment=environment)),
            {
                Action.objects.get(name='*', grant__name='allowed_attributes'),
                Action.objects.get(name='*', grant__name='can_delay'),
            },
        )
        self.assertEqual(
            set(Network.objects.filter(activenetwork__consumer=consumer, activenetwork__environment=environment)),
            {Network.objects.get(string='127.0.0.1', type=Network.IP)}
        )

    def test_review_with_clients_approved_with_consumer(self):
        data = {
            'issue': 6,
            'result': 'confirmed',
        }

        response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [
                '__all__: Клиенты уже привязаны к потребителям; '
                'client_id: 1 - consumer: blackbox_by_client_consumer',
            ],
            'success': False,
        })

    def test_review_with_client_rejected(self):
        client = Client.objects.get(pk=TEST_CLIENT_PK)
        self.assertIsNone(client.consumer)
        data = {
            'issue': 5,
            'result': 'rejected',
        }

        with self.settings(
            PASSPORT_TEAM_ADMIN=[self.user.username],
            NAMESPACES_FOR_ADMINS=['passport'],
        ):
            response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'rejected',
        })

        client = Client.objects.get(pk=TEST_CLIENT_PK)
        self.assertIsNone(client.consumer)

    def test_review_with_old_clients_unlinked_approved(self):
        client = Client.objects.get(pk=TEST_CLIENT_PK_WITH_CONSUMER)
        consumer = Consumer.objects.get(pk=TEST_CONSUMER_PK_WITH_CLIENT)
        self.assertEqual(client.consumer, consumer)
        data = {
            'issue': 7,
            'result': 'confirmed',
        }

        with self.settings(
            PASSPORT_TEAM_ADMIN=[self.user.username],
            NAMESPACES_FOR_ADMINS=['blackbox', 'blackbox_by_client'],
        ):
            response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'confirmed',
        })

        namespace = Namespace.objects.get(id=10)
        environment = Environment.objects.get(id=2)
        consumer = Consumer.objects.get(name='blackbox_by_client_consumer', namespace=namespace)
        client = Client.objects.get(pk=TEST_CLIENT_PK)
        self.assertEqual(client.consumer, consumer)

        self.assertEqual(
            set(Action.objects.filter(activeaction__consumer=consumer, activeaction__environment=environment)),
            {
                Action.objects.get(name='*', grant__name='allowed_attributes'),
                Action.objects.get(name='*', grant__name='can_delay'),
            },
        )

    def test_review_issue_with_clone_consumer(self):
        data = {
            'issue': 11,
            'result': 'confirmed',
        }

        with self.settings(
            PASSPORT_TEAM_ADMIN=[self.user.username],
            NAMESPACES_FOR_ADMINS=['passport'],
        ):
            response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'confirmed',
        })

        issue = Issue.objects.get(id=11)
        self.assertEqual(issue.status, Issue.APPROVED)

        namespace = Namespace.objects.get(id=10)
        environment = Environment.objects.get(id=2)
        consumer = Consumer.objects.get(name='blackbox_by_client_consumer_new', namespace=namespace)
        client = Client.objects.get(pk=TEST_CLIENT_PK)
        self.assertEqual(client.consumer, consumer)

        self.assertEqual(
            set(Action.objects.filter(activeaction__consumer=consumer, activeaction__environment=environment)),
            {
                Action.objects.get(name='*', grant__name='can_delay'),
            },
        )

    def test_can_review_namespace_issue(self):
        admin_namespaces = ['passport']
        data = {
            'issue': 1,
            'result': 'confirmed',
        }

        with self.settings(
            PASSPORT_TEAM_ADMIN=[self.user.username],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'success': True,
            'result': 'confirmed',
        })

    def test_cant_review_namespace_issue(self):
        admin_namespaces = ['passport']
        data = {
            'issue': 1,
            'result': 'confirmed',
        }

        with self.settings(
            PASSPORT_TEAM_ADMIN=['admin'],
            NAMESPACES_FOR_ADMINS=admin_namespaces,
        ):
            response = self.make_request(data)

        self.assertEqual(json.loads(response.content), {
            'errors': ['У Вас нет прав для действий с заявками в этом проекте'],
            'success': False,
        })
