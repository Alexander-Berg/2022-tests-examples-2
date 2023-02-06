# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory

from passport_grants_configurator.apps.core.models import Issue
from passport_grants_configurator.apps.core.utils import deep_merge
from passport_grants_configurator.apps.core.views import get_grants_list


class GetConsumerGrantsListCase(TestCase):
    maxDiff = None
    fixtures = ['default.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(id=1)

        self.data = {
            'consumer': 1,
        }
        self.default_response = {
            'consumer_grants': {
                'clients': {},
                'grants': [
                    {
                        'actions': [
                            {
                                'active_by': dict.fromkeys('1234567', False),
                                'active_new_by': dict.fromkeys('1234567', False),
                                'dangerous': False,
                                'description': 'Запросы к серверу капчи',
                                'expiration_by': dict.fromkeys('1234567', None),
                                'expiration_new_by': dict.fromkeys('1234567', None),
                                'id': 3,
                                'name': '*',
                            },
                        ],
                        'name': 'captcha',
                    },
                    {
                        'actions': [
                            {
                                'active_by': dict.fromkeys('1234567', False),
                                'active_new_by': dict.fromkeys('1234567', False),
                                'dangerous': False,
                                'description': 'Предложить возможный вариант логина',
                                'expiration_by': dict.fromkeys('1234567', None),
                                'expiration_new_by': dict.fromkeys('1234567', None),
                                'id': 4,
                                'name': 'suggest',
                            },
                            {
                                'active_by': dict.fromkeys('1234567', False),
                                'active_new_by': dict.fromkeys('1234567', False),
                                'dangerous': False,
                                'description': 'Проверить правильность логина',
                                'expiration_by': dict.fromkeys('1234567', None),
                                'expiration_new_by': dict.fromkeys('1234567', None),
                                'id': 5,
                                'name': 'validate',
                            },
                        ],
                        'name': 'login',
                    },
                    {
                        'actions': [
                            {
                                'active_by': dict.fromkeys('1234567', False),
                                'active_new_by': dict.fromkeys('1234567', False),
                                'dangerous': False,
                                'description': 'Требование сменить пароль на аккаунте',
                                'expiration_by': dict.fromkeys('1234567', None),
                                'expiration_new_by': dict.fromkeys('1234567', None),
                                'id': 2,
                                'name': 'is_changing_required',
                            },
                            {
                                'active_by': dict.fromkeys('1234567', False),
                                'active_new_by': dict.fromkeys('1234567', False),
                                'dangerous': False,
                                'description': 'Валидация пароля',
                                'expiration_by': dict.fromkeys('1234567', None),
                                'expiration_new_by': dict.fromkeys('1234567', None),
                                'id': 1,
                                'name': 'validate',
                            },
                        ],
                        'name': 'password',
                    },
                    {
                        'actions': [
                            {
                                'active_by': dict.fromkeys('1234567', False),
                                'active_new_by': dict.fromkeys('1234567', False),
                                'dangerous': False,
                                'description': 'Проверка cookie session_id',
                                'expiration_by': dict.fromkeys('1234567', None),
                                'expiration_new_by': dict.fromkeys('1234567', None),
                                'id': 7,
                                'name': 'check',
                            },
                            {
                                'active_by': dict.fromkeys('1234567', False),
                                'active_new_by': dict.fromkeys('1234567', False),
                                'dangerous': False,
                                'description': 'Создание сессии',
                                'expiration_by': dict.fromkeys('1234567', None),
                                'expiration_new_by': dict.fromkeys('1234567', None),
                                'id': 6,
                                'name': 'create',
                            },
                        ],
                        'name': 'session',
                    },
                    {
                        'actions': [
                            {
                                'active_by': dict.fromkeys('1234567', False),
                                'active_new_by': dict.fromkeys('1234567', False),
                                'dangerous': True,
                                'description': 'passport subscription grant',
                                'expiration_by': dict.fromkeys('1234567', None),
                                'expiration_new_by': dict.fromkeys('1234567', None),
                                'id': 15,
                                'name': 'something.create',
                            },
                        ],
                        'name': 'subscription'
                    },
                ],
                'macroses': [
                    {
                        'active_by': dict.fromkeys('1234567', False),
                        'active_new_by': dict.fromkeys('1234567', False),
                        'description': 'Группа грантов some_macros1',
                        'expiration_by': dict.fromkeys('1234567', None),
                        'expiration_new_by': dict.fromkeys('1234567', None),
                        'grants': [
                            {
                                'actions': [
                                    {
                                        'name': '*',
                                    },
                                ],
                                'name': 'captcha',
                            },
                            {
                                'actions': [
                                    {
                                        'name': 'suggest',
                                    },
                                ],
                                'name': 'login',
                            },
                            {
                                'actions': [
                                    {
                                        'name': 'check',
                                    },
                                    {
                                        'name': 'create',
                                    },
                                ],
                                'name': 'session',
                            },
                        ],
                        'id': 1,
                        'name': 'some_macros1',
                    },
                    {
                        'active_by': dict.fromkeys('1234567', False),
                        'active_new_by': dict.fromkeys('1234567', False),
                        'description': 'Группа грантов some_macros2',
                        'expiration_by': dict.fromkeys('1234567', None),
                        'expiration_new_by': dict.fromkeys('1234567', None),
                        'grants': [
                            {
                                'actions': [
                                    {
                                        'name': 'is_changing_required',
                                    },
                                    {
                                        'name': 'validate',
                                    },
                                ],
                                'name': 'password',
                            },
                        ],
                        'id': 2,
                        'name': 'some_macros2',
                    },
                ],
                'networks': dict.fromkeys('1234567', []),
            },
            'errors': [],
            'success': True,
        }

    def test_new_consumer_new_issue(self):
        self.data['consumer_name'] = 'new consumer'

        request = self.factory.get('/grants/get_full_consumer_data/', {'namespace': 1})
        request.user = self.user

        response = get_grants_list(request)

        self.assertEqual(json.loads(response.content), self.default_response)
        self.assertEqual(response.status_code, 200)

    def test_existing_consumer_new_issue(self):
        request = self.factory.get('/grants/get_grants_list/', self.data)
        request.user = self.user

        response = get_grants_list(request)

        self.assertEqual(json.loads(response.content), deep_merge(self.default_response, {
            'consumer_grants': {
                'grants': [
                    {
                        'name': 'captcha',
                        'actions': [
                            {
                                'name': '*',
                                'active_by': {
                                    '1': True,
                                },
                                'active_new_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                    {
                        'name': 'login',
                        'actions': [
                            None,
                            {
                                'name': 'validate',
                                'active_by': {
                                    '1': True,
                                },
                                'active_new_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                    {
                        'name': 'password',
                        'actions': [
                            {
                                'name': 'is_changing_required',
                                'active_by': {
                                    '1': True,
                                },
                                'active_new_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                    {
                        'name': 'session',
                        'actions': [
                            {
                                'name': 'check',
                                'active_by': {
                                    '1': True,
                                },
                                'active_new_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                    {
                        'name': 'subscription',
                        'actions': [
                            {
                                'name': 'something.create',
                                'active_by': {
                                    '1': True,
                                },
                                'active_new_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                ],
                'macroses': [
                    {
                        'name': 'some_macros1',
                        'active_by': {
                            '1': True,
                        },
                        'active_new_by': {
                            '1': True
                        },
                    },
                ],
                'networks': {
                    '1': [
                        {
                            'active': True,
                            'type': 'I',
                            'id': 1,
                            'string': '127.0.0.1',
                            'active_new': True,
                        },
                        {
                            'active': True,
                            'type': 'I',
                            'id': 3,
                            'string': '127.0.0.3',
                            'active_new': True,
                        },
                        {
                            'active': True,
                            'type': 'N',
                            'id': 4,
                            'string': '77.88.40.96/28',
                            'active_new': True,
                        },
                        {
                            'active': True,
                            'type': 'F',
                            'id': 7,
                            'string': '_KOPALKA_',
                            'active_new': True,
                        },
                    ],
                },
            },
        }))
        self.assertEqual(response.status_code, 200)

    def test_new_consumer_existing_issue(self):
        Issue.objects.filter(id=1).update(status=Issue.DRAFT)
        issue = Issue.objects.get(id=1)
        issue.consumer_name = 'new consumer'
        issue.save()

        request = self.factory.get('/grants/get_grants_list/', {'issue': 1})
        request.user = self.user

        response = get_grants_list(request)

        self.assertEqual(json.loads(response.content), deep_merge(self.default_response, {
            'consumer_grants': {
                'grants': [
                    None,
                    None,
                    {
                        'name': 'password',
                        'actions': [
                            None,
                            {
                                'name': 'validate',
                                'active_new_by': dict.fromkeys('1234567', True)
                            },
                        ],
                    },
                    {
                        'name': 'session',
                        'actions': [
                            None,
                            {
                                'name': 'create',
                                'active_new_by': dict.fromkeys('1234567', True)
                            },
                        ],
                    },
                ],
                'networks': {
                    '1': [
                        {
                            'active': False,
                            'type': 'I',
                            'id': 2,
                            'string': '127.0.0.2',
                            'active_new': True,
                        },
                    ],
                },
                'macroses': [
                    None,
                    {
                        'name': 'some_macros2',
                        'active_new_by': dict.fromkeys('1234567', True),
                    },
                ],
            },
        }))
        self.assertEqual(response.status_code, 200)

    def test_existing_consumer_existing_issue(self):
        Issue.objects.filter(id=2).update(status=Issue.DRAFT)

        request = self.factory.get('/grants/get_grants_list/', {'issue': 2})
        request.user = self.user

        response = get_grants_list(request)

        self.assertEqual(json.loads(response.content), deep_merge(self.default_response, {
            'consumer_grants': {
                'grants': [
                    {
                        'name': 'captcha',
                        'actions': [
                            {
                                'name': '*',
                                'active_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                    {
                        'name': 'login',
                        'actions': [
                            None,
                            {
                                'name': 'validate',
                                'active_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                    {
                        'name': 'password',
                        'actions': [
                            {
                                'name': 'is_changing_required',
                                'active_by': {
                                    '1': True,
                                },
                                'active_new_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                    {
                        'name': 'session',
                        'actions': [
                            {
                                'name': 'check',
                                'active_by': {
                                    '1': True,
                                },
                                'active_new_by': {
                                    '1': True,
                                },
                            },
                            {
                                'name': 'create',
                                'active_new_by': dict.fromkeys('1234567', True)
                            },
                        ],
                    },
                    {
                        'name': 'subscription',
                        'actions': [
                            {
                                'name': 'something.create',
                                'active_by': {
                                    '1': True,
                                },
                                'active_new_by': {
                                    '1': True,
                                },
                            },
                        ],
                    },
                ],
                'networks': {
                    '1': [
                        {
                            'active': False,
                            'type': 'C',
                            'id': 6,
                            'string': '%passport-grantushka-stable',
                            'active_new': True,
                        },
                        {
                            'active': True,
                            'type': 'I',
                            'id': 1,
                            'string': '127.0.0.1',
                            'active_new': False,
                        },
                        {
                            'active': False,
                            'type': 'I',
                            'id': 2,
                            'string': '127.0.0.2',
                            'active_new': True,
                        },
                        {
                            'active': True,
                            'type': 'I',
                            'id': 3,
                            'string': '127.0.0.3',
                            'active_new': True,
                        },
                        {
                            'active': True,
                            'type': 'N',
                            'id': 4,
                            'string': '77.88.40.96/28',
                            'active_new': False,
                        },
                        {
                            'active': True,
                            'type': 'F',
                            'id': 7,
                            'string': '_KOPALKA_',
                            'active_new': True,
                        },
                        {
                            'active': False,
                            'type': 'H',
                            'id': 5,
                            'string': 'grantushka.yandex-team.ru',
                            'active_new': True,
                        },
                    ],
                },
                'macroses': [
                    {
                        'name': 'some_macros1',
                        'active_by': {
                            '1': True,
                        },
                    },
                    {
                        'name': 'some_macros2',
                        'active_new_by': dict.fromkeys('1234567', True),
                    },
                ],
            },
        }))
        self.assertEqual(response.status_code, 200)

    def test_if_non_creator_opens_editable_issue(self):
        Issue.objects.filter(id=1).update(status=Issue.DRAFT)
        user = User.objects.get(id=2)

        request = self.factory.get('/grants/get_grants_list/', {'issue': 1})
        request.user = user

        response = get_grants_list(request)

        self.assertEqual(json.loads(response.content), {
            'errors': ['Вы не являетесь создателем этой заявки'],
            'success': False,
        })
        self.assertEqual(response.status_code, 200)

    def test_request_inactive_issue(self):
        self.data['issue'] = 1

        request = self.factory.get('/grants/get_grants_list/', self.data)
        request.user = self.user

        for i in (1, 2):
            issue = Issue.objects.get(id=1)
            issue.status = {1: Issue.REJECTED, 2: Issue.APPROVED}[i]
            issue.save()

            response = get_grants_list(request)

            self.assertEqual(json.loads(response.content), {
                'errors': ['issue: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'],
                'success': False,
            })
            self.assertEqual(response.status_code, 200)

    def test_bad_issue_id(self):
        self.data['issue'] = 100500

        request = self.factory.get('/grants/get_grants_list/', self.data)
        request.user = self.user

        response = get_grants_list(request)

        self.assertEqual(json.loads(response.content), {
            'errors': ['issue: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'],
            'success': False,
        })
        self.assertEqual(response.status_code, 200)

    def test_wrong_issue_type(self):
        self.data['issue'] = 'I am not a number'

        request = self.factory.get('/grants/get_grants_list/', self.data)
        request.user = self.user

        response = get_grants_list(request)

        self.assertEqual(json.loads(response.content), {
            'errors': ['issue: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'],
            'success': False,
        })
        self.assertEqual(response.status_code, 200)
