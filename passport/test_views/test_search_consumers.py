# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from passport_grants_configurator.apps.core.test.utils import MockRedis, MockRequests
from passport_grants_configurator.apps.core.utils import deep_merge

from passport_grants_configurator.apps.core.views import consumer_search


def get_network_redis_key(name):
    return '%s:%s:%s' % (settings.REDIS_KEY_PREFIX, settings.REDIS_NETWORK_PREFIX, name)


TEST_REDIS_CACHE = {
    get_network_redis_key('known_network_list'): json.dumps([
        '127.0.0.1',
        '127.0.0.3',
        '77.88.40.96/28',
        '_KOPALKA_',
        '93.158.133.0/26',
        '2a02:6b8:0:212::/64',
    ]),
    get_network_redis_key('known_ip_network_list'): json.dumps([
        '127.0.0.1',
        '127.0.0.3',
        '77.88.40.96/28',
        '93.158.133.0/26',
        '2a02:6b8:0:212::/64',
    ]),
    get_network_redis_key('2a02:6b8:0:212::/64'): json.dumps({
        'id': None,
        'descendant_ids': [],
        'parent_ids': [7],
        'type': u'N',
        'children': [],
        'string': u'2a02:6b8:0:212::/64',
    }),
    get_network_redis_key('93.158.133.0/26'): json.dumps({
        'id': None,
        'descendant_ids': [],
        'parent_ids': [7],
        'type': u'N',
        'children': [],
        'string': u'93.158.133.0/26',
    })
}

TEST_CONSUMER_GRANTS = [
    {
        'name': 'some_consumer',
        'description': 'Это some_consumer',
        'environments': [
            {
                'client': None,
                'grants': [
                    {
                        'highlighted': False,
                        'name': 'captcha',
                        'actions': [
                            {
                                'highlighted': False,
                                'dangerous': False,
                                'description': u'Запросы к серверу капчи',
                                'name': '*',
                                'expiration': None,
                            },
                        ],
                    },
                    {
                        'highlighted': False,
                        'name': 'login',
                        'actions': [
                            {
                                'highlighted': False,
                                'dangerous': False,
                                'description': u'Проверить правильность логина',
                                'name': 'validate',
                                'expiration': None,
                            },
                        ],
                    },
                    {
                        'highlighted': False,
                        'name': 'password',
                        'actions': [
                            {
                                'highlighted': False,
                                'dangerous': False,
                                'description': u'Требование сменить пароль на аккаунте',
                                'name': 'is_changing_required',
                                'expiration': None,
                            },
                        ],
                    },
                    {
                        'highlighted': False,
                        'name': 'session',
                        'actions': [
                            {
                                'highlighted': False,
                                'dangerous': False,
                                'description': u'Проверка cookie session_id',
                                'name': 'check',
                                'expiration': None,
                            },
                        ],
                    },
                    {
                        'highlighted': False,
                        'name': 'subscription',
                        'actions': [
                            {
                                'highlighted': False,
                                'dangerous': True,
                                'description': 'passport subscription grant',
                                'name': 'something.create',
                                'expiration': None,
                            },
                        ],
                    },
                ],
                'networks': [
                    {
                        'highlighted': False,
                        'string': '127.0.0.1',
                    },
                    {
                        'highlighted': False,
                        'string': '127.0.0.3',
                    },
                    {
                        'highlighted': False,
                        'string': '77.88.40.96/28',
                    },
                    {
                        'highlighted': False,
                        'string': '_KOPALKA_',
                    },
                ],
                'id': 1,
                'string': 'production',
                'macroses': [
                    {
                        'highlighted': False,
                        'grants': [
                            {
                                'name': 'captcha',
                                'actions': [
                                    {
                                        'description': u'Запросы к серверу капчи',
                                        'name': '*',
                                    },
                                ],
                            },
                            {
                                'name': 'login',
                                'actions': [
                                    {
                                        'description': u'Предложить возможный вариант логина',
                                        'name': 'suggest',
                                    },
                                ],
                            },
                            {
                                'name': 'session',
                                'actions': [
                                    {
                                        'description': u'Проверка cookie session_id',
                                        'name': 'check',
                                    },
                                    {
                                        'description': u'Создание сессии',
                                        'name': 'create',
                                    },
                                ],
                            },
                        ],
                        'description': u'Группа грантов some_macros1',
                        'name': 'some_macros1',
                        'expiration': None,
                    },
                ],
            },
        ],
        'id': 1
    },
]


class GetConsumerDataCase(TestCase):
    maxDiff = None
    fixtures = ['default.json']
    url = '/grants/consumer/search/'

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(id=1)
        self.mock_requests = MockRequests()
        self.mock_requests.set_response_value_for_host(
            'racktables.yandex.net',
            '\n'.join([
                '93.158.133.0/26',
                '2a02:6b8:0:212::/64',
            ]),
            qs_re='?macro=_KOPALKA_',
        )
        self.mock_requests.set_response_value_for_host(
            'racktables.yandex.net',
            '',
            qs_re='RKET_URLCHECKER_',
        )
        self.mock_requests.start()
        self.mock_redis = MockRedis()
        self.mock_redis.start()
        self.mock_redis.cache = TEST_REDIS_CACHE
        self.consumer_grants = TEST_CONSUMER_GRANTS

    def tearDown(self):
        self.mock_redis.stop()
        self.mock_requests.stop()

    def make_request(self, **kwargs):
        params = {
            'namespace': 1,
            'environments': [1, 2, 3, 4, 5, 6, 7],
        }
        params.update(kwargs)
        request = self.factory.get(
            self.url,
            params
        )
        request.user = self.user
        return request

    def test_get_user_data(self):
        request = self.make_request()

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': self.consumer_grants,
            'success': True,
            'pages': 1,
        })

    def test_get_user_data_empty_namespace(self):
        request = self.make_request(environments=[2])

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': [],
            'success': True,
            'pages': 1,
        })

    def test_not_finding_consumer(self):
        request = self.make_request(environments=[1], keyword='sdfghjkl')

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': [],
            'success': True,
            'pages': 1,
        })

    def test_search_by_grant_name(self):
        request = self.make_request(keyword='aptcha')

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': deep_merge(self.consumer_grants, [{
                'environments': [{
                    'grants': [{
                        'name': 'captcha',
                        'highlighted': True,
                    }],
                    'macroses': [{
                        'name': 'some_macros1',
                        'highlighted': True,
                        'grants': [{
                            'name': 'captcha'
                        }]
                    }]
                }]
            }]),
            'success': True,
            'pages': 1,
        })

    def test_search_by_action_name(self):
        request = self.make_request(keyword='hec')

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': deep_merge(self.consumer_grants, [{
                'environments': [{
                    'grants': [
                        None,
                        None,
                        None,
                        {
                            'name': 'session',
                            'actions': [
                                {
                                    'name': 'check',
                                    'highlighted': True,
                                }
                            ]
                        }
                    ],
                    'macroses': [{
                        'name': 'some_macros1',
                        'highlighted': True,
                        'grants': [
                            None,
                            None,
                            {
                                'name': 'session',
                                'actions': [{
                                    'name': 'check',
                                }]
                            }
                        ]
                    }]
                }]
            }]),
            'success': True,
            'pages': 1,
        })

    def test_search_by_macros_name(self):
        request = self.make_request(keyword='macros')

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': deep_merge(self.consumer_grants, [{
                'environments': [{
                    'macroses': [{
                        'name': 'some_macros1',
                        'highlighted': True,
                    }]
                }]
            }]),
            'success': True,
            'pages': 1,
        })

    def test_search_by_network_name(self):
        request = self.make_request(keyword='27.')

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': deep_merge(self.consumer_grants, [{
                'environments': [{
                    'networks': [
                        {
                            'highlighted': True,
                            'string': '127.0.0.1',
                        },
                        {
                            'highlighted': True,
                            'string': '127.0.0.3',
                        },
                    ]
                }]
            }]),
            'success': True,
            'pages': 1,
        })

    def test_search_by_expanded_network(self):
        request = self.make_request(keyword='2a02:6b8:0:212::/64')

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': deep_merge(self.consumer_grants, [{
                'environments': [{
                    'networks': [
                        None,
                        None,
                        None,
                        {
                            'highlighted': True,
                            'string': '_KOPALKA_',
                        },
                    ]
                }]
            }]),
            'success': True,
            'pages': 1,
        })

    def test_search_by_expanded_ipnetwork_ip(self):
        request = self.make_request(keyword='93.158.133.1')

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': deep_merge(self.consumer_grants, [{
                'environments': [{
                    'networks': [
                        None,
                        None,
                        None,
                        {
                            'highlighted': True,
                            'string': '_KOPALKA_',
                        },
                    ]
                }]
            }]),
            'success': True,
            'pages': 1,
        })

    def test_search_by_a_number__empty(self):
        """Не смогли разобрать ввод - ничего не возвращаем и не падаем"""
        request = self.make_request(keyword='471035')

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'consumer_grants': [],
            'success': True,
            'pages': 1,
        })

    def test_empty_form__error(self):
        request = self.factory.get(self.url, {})
        request.user = self.user

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'errors': [
                u'namespace: Обязательное поле.',
            ],
            'success': False,
        })

    def test_unknown_namespace__error(self):
        request = self.factory.get(self.url, {'namespace': '100500'})
        request.user = self.user

        response = consumer_search(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'errors': [
                u'namespace: Выберите корректный вариант. Вашего варианта нет среди допустимых значений.',
            ],
            'success': False,
        })
