# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import RequestFactory
from mock import patch, Mock

from passport_grants_configurator.apps.core.models import Namespace, NamespaceEnvironments, Environment
from passport_grants_configurator.apps.core.permissions import UserPermissions, namespace_selection


class TestNamespaceSelection(TestCase):
    fixtures = ['default.json']

    def test(self):
        namespaces = Namespace.objects.all()

        request = RequestFactory().get('/', {})
        self.assertEqual(namespace_selection(request)['namespace'], namespaces[0])

        request = RequestFactory().get('/', {'namespace_id': 100500})
        self.assertEqual(namespace_selection(request)['namespace'], namespaces[0])

        request = RequestFactory().get('/', {'namespace_id': 2})
        self.assertEqual(namespace_selection(request)['namespace'], namespaces.get(id=2))

        namespaces.delete()
        request = RequestFactory().get('/', {'namespace_id': 1})
        self.assertEqual(namespace_selection(request)['namespace'], None)


class TestUserPermissions(TestCase):
    fixtures = ['default']

    def setUp(self):
        self.mock_get_objects = Mock(return_value=NamespaceEnvironments.objects.all())
        self.patch_get_objects = patch(
            'passport_grants_configurator.apps.core.permissions.get_objects_for_user',
            self.mock_get_objects,
        )
        self.patch_get_objects.start()

    def tearDown(self):
        self.patch_get_objects.stop()

    def test_have_all(self):
        self.assertEqual(UserPermissions(user=None).have_all(
            namespace=Namespace.objects.get(id=1),
            environments=Namespace.objects.get(id=1).environments.all()
        ), True)

        self.assertEqual(UserPermissions(user=None).have_all(
            namespace=Namespace.objects.get(id=1),
            environments=Environment.objects.filter(id=1)
        ), True)

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.filter(namespace=2, environment=2)
        self.assertEqual(UserPermissions(user=None).have_all(
            namespace=Namespace.objects.get(id=1),
            environments=Environment.objects.filter(id=1)
        ), False)

    def test_do_not_have(self):
        self.assertEqual(UserPermissions(user=None).do_not_have(
            namespace=Namespace.objects.get(id=1),
            environments=Namespace.objects.get(id=1).environments.all()
        ), [])

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.filter(namespace=1, environment=1)
        self.assertEqual(set(UserPermissions(user=None).do_not_have(
            namespace=Namespace.objects.get(id=1),
            environments=Namespace.objects.get(id=1).environments.all()
        )), set(NamespaceEnvironments.objects.filter(namespace=1, environment__in=[2, 3, 4, 5, 6, 7])))

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.none()
        self.assertEqual(set(UserPermissions(user=None).do_not_have(
            namespace=Namespace.objects.get(id=1),
            environments=Namespace.objects.get(id=1).environments.all()
        )), set(NamespaceEnvironments.objects.filter(namespace=1, environment__in=[1, 2, 3, 4, 5, 6, 7])))

    def test_intersect_grouped(self):
        self.assertEqual(
            list(UserPermissions(user=None).intersect_grouped(namespaces=Namespace.objects.filter(id=1))),
            [(Namespace.objects.get(id=1), list(Namespace.objects.get(id=1).environments.all()))],
        )

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.filter(namespace=1, environment=1)
        self.assertEqual(
            list(UserPermissions(user=None).intersect_grouped(namespaces=Namespace.objects.filter(id=1))),
            [(Namespace.objects.get(id=1), [Environment.objects.get(id=1)])],
        )

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.filter(namespace=2, environment=1)
        self.assertEqual(
            list(UserPermissions(user=None).intersect_grouped(namespaces=Namespace.objects.filter(id=1))),
            [],
        )

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.none()
        self.assertEqual(
            list(UserPermissions(user=None).intersect_grouped(namespaces=Namespace.objects.filter(id=1))),
            [],
        )

    def test_get_q(self):
        self.assertEqual(
            str(UserPermissions(user=None).Q()),
            ''.join([
                '(OR: (AND: ), ',
                '(AND: (\'environments__in\', [1, 3, 2, 5, 4, 7, 6]), (\'namespace\', 1)), ',
                '(AND: (\'environments__in\', [1, 3, 2]), (\'namespace\', 2)), ',
                '(AND: (\'environments__in\', [1, 3, 2]), (\'namespace\', 4)), ',
                '(AND: (\'environments__in\', [1, 2, 3]), (\'namespace\', 5)), ',
                '(AND: (\'environments__in\', [1, 9, 3, 2]), (\'namespace\', 6)), ',
                '(AND: (\'environments__in\', [1, 3, 2, 4, 7, 8]), (\'namespace\', 7)), ',
                '(AND: (\'environments__in\', [1, 2, 3, 4, 7]), (\'namespace\', 8)), ',
                '(AND: (\'environments__in\', [3, 2]), (\'namespace\', 10)), ',
                '(AND: (\'environments__in\', [2]), (\'namespace\', 11)), ',
                '(AND: (\'environments__in\', [1]), (\'namespace\', 12)), ',
                '(AND: (\'environments__in\', [1, 2, 3]), (\'namespace\', 13)))',
            ])
        )

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.filter(namespace=1, environment=1)
        self.assertEqual(
            str(UserPermissions(user=None).Q()),
            '(OR: (AND: ), (AND: (\'environments__in\', [1]), (\'namespace\', 1)))',
        )

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.filter(namespace=2, environment=1)
        self.assertEqual(
            str(UserPermissions(user=None).Q()),
            '(OR: (AND: ), (AND: (\'environments__in\', [1]), (\'namespace\', 2)))',
        )

        self.mock_get_objects.return_value = NamespaceEnvironments.objects.none()
        self.assertEqual(
            str(UserPermissions(user=None).Q()),
            '(AND: )',
        )
