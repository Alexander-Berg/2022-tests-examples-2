# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from passport_grants_configurator.apps.core.models import (
    Network,
    Issue,
    Environment,
    Namespace,
    Consumer,
    Grant,
    Action,
    Macros,
)


class TestIssueCase(TestCase):
    fixtures = ['default.json']

    def test_get_consumer_name(self):
        issue = Issue.objects.get(id=2)
        self.assertEqual(issue.get_consumer_name(), 'some_consumer')

        issue = Issue.objects.get(id=3)
        self.assertEqual(issue.get_consumer_name(), 'space2_consumer')

        issue = Issue(
            creator_id=1,
            approving_person_id=1,
            type=Issue.TO_MODIFY,
            consumer_id=0,
        )
        self.assertEqual(issue.get_consumer_name(), '')

    def test_get_consumer_description(self):
        issue = Issue.objects.get(id=2)
        self.assertEqual(issue.get_consumer_description(), 'Это some_consumer')

        issue = Issue.objects.get(id=3)
        self.assertEqual(issue.get_consumer_description(), 'space2 consumer')

        issue = Issue(
            creator_id=1,
            approving_person_id=1,
            type=Issue.TO_MODIFY,
            consumer_id=0,
        )
        self.assertEqual(issue.get_consumer_description(), '')


class ModelsNaturalKeysCase(TestCase):
    fixtures = ['default']

    def test_get_model_natural_keys(self):
        self.assertEqual(Environment.objects.get(id=1).natural_key(), ('localhost', 'production'))
        self.assertEqual(Namespace.objects.get(id=1).natural_key(), ('passport',))
        self.assertEqual(Network.objects.get(id=1).natural_key(), ('127.0.0.1', 'I'))
        self.assertEqual(Consumer.objects.get(id=1).natural_key(), ('passport', 'some_consumer'))
        self.assertEqual(Grant.objects.get(id=1).natural_key(), ('passport', 'password'))
        self.assertEqual(Action.objects.get(id=1).natural_key(), ('passport', 'password', 'validate'))
        self.assertEqual(Macros.objects.get(id=1).natural_key(), ('passport', 'some_macros1'))
