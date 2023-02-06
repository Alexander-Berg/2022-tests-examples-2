# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory

from passport_grants_configurator.apps.core.models import Action, Grant
from passport_grants_configurator.apps.core.views import grant_create


class CreateGrantCase(TestCase):
    fixtures = ['default.json']
    url = '/grants/grant/'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(id=3)

        self.data = {
            'grant_name': 'new grant',
            'grant_namespace': 1,
            'name': 'new action',
            'description': 'a new action',
        }

    def test_create(self):
        request = self.factory.post(self.url, self.data)
        request.user = self.user

        response = grant_create(request)

        self.assertEqual(json.loads(response.content), {
            'success': True,
        })

        try:
            grant = Grant.objects.get(name='new grant', namespace=1)
        except Grant.DoesNotExist as e:
            self.fail(e.message)

        try:
            action = Action.objects.get(name='new action', grant=grant)
        except Action.DoesNotExist as e:
            self.fail(e.message)

        self.assertEqual(action.description, 'a new action')

    def test_create_action_for_old_grant(self):
        self.data['grant_name'] = 'password'

        request = self.factory.post(self.url, self.data)
        request.user = self.user

        response = grant_create(request)

        self.assertEqual(json.loads(response.content), {
            'success': True,
        })

        try:
            grant = Grant.objects.get(name='password', namespace=1)
        except Grant.DoesNotExist as e:
            self.fail(e.message)

        self.assertEqual(grant.description, '')

        try:
            action = Action.objects.get(name='new action', grant=grant)
        except Action.DoesNotExist as e:
            self.fail(e.message)

        self.assertEqual(action.description, 'a new action')

    def test_no_permissions_to_create(self):
        request = self.factory.post(self.url, self.data)
        request.user = User.objects.get(id=1)

        response = grant_create(request)

        self.assertEqual(json.loads(response.content), {
            'errors': ['У Вас нет прав для добавления гранта в проект passport'],
            'success': False,
        })

    def test_invalid_form(self):
        self.data.pop('grant_name')
        request = self.factory.post(self.url, self.data)
        request.user = self.user

        response = grant_create(request)

        self.assertEqual(json.loads(response.content), {
            'errors': ['grant_name: Обязательное поле.'],
            'success': False,
        })
