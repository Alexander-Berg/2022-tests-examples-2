# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.conf import settings
from django.test import (
    RequestFactory,
    TestCase,
)

from mock import patch

from passport_grants_configurator.apps.core.test.utils import (
    MockNetworkApi,
    MockRedis,
    MockRequests,
)
from passport_grants_configurator.apps.core.views import consumer_suggest


def get_network_redis_key(name):
    return '%s:%s:%s' % (settings.REDIS_KEY_PREFIX, settings.REDIS_NETWORK_PREFIX, name)


TEST_REDIS_CACHE = {
    get_network_redis_key('known_network_list'): json.dumps([
        '77.88.40.96/28',
        '93.158.133.0/26',
        '2a02:6b8:0:212::/64',
        '_kopalka_',
        '%passport-grantushka-stable',
        'grantushka.yandex-team.ru',
    ]),
    get_network_redis_key('known_ip_network_list'): json.dumps([
        '77.88.40.96/28',
        '93.158.133.0/26',
        '2a02:6b8:0:212::/64',
    ]),
    get_network_redis_key('all_conductor_groups_list'): json.dumps([
        '%passport-grantushka-stable',
    ]),
    get_network_redis_key('_kopalka_'): json.dumps({
        'id': 7,
        'descendant_ids': [4],
        'parent_ids': [],
        'type': 'F',
        'children': [],
        'string': '_kopalka_',
    }),
    get_network_redis_key('grantushka.yandex-team.ru'): json.dumps({
        'id': 5,
        'descendant_ids': [],
        'parent_ids': [7],
        'type': 'H',
        'children': [],
        'string': 'grantushka.yandex-team.ru',
    }),
    get_network_redis_key('77.88.40.96/28'): json.dumps({
        'id': 4,
        'descendant_ids': [],
        'parent_ids': [7],
        'type': u'N',
        'children': [],
        'string': u'77.88.40.96/28',
    }),
}


class SuggestConsumerTestCase(TestCase):
    maxDiff = None
    fixtures = ['default.json']
    url = '/grants/consumer/suggest/'

    def setUp(self):
        self.factory = RequestFactory()
        self.mock_requests = MockRequests()
        self.mock_requests.start()
        self.mock_redis = MockRedis()
        self.mock_redis.start()
        self.mock_redis.cache = TEST_REDIS_CACHE

        self.networkapi = MockNetworkApi()
        self.networkapi.start()

        self.networkapi.setup_response(
            'expand_firewall_macro',
            {'_KOPALKA_': ['77.88.40.96/28']},
        )
        self.networkapi.setup_response(
            'get_conductor_group_hosts',
            {'%passport-grantushka-stable': 'grantushka.yandex-team.ru'},
        )
        self.networkapi.setup_response(
            'getipsfromaddr',
            {'grantushka.yandex-team.ru': ['93.158.133.0/26']},
        )

    def tearDown(self):
        self.networkapi.stop()
        self.mock_redis.stop()
        self.mock_requests.stop()

    def assert_errors(self, response, status_code=200, errors=None):
        self.assertEqual(response.status_code, status_code)
        response = json.loads(response.content)

        self.assertFalse(response['success'])
        self.assertEqual(
            sorted(response['errors']),
            sorted(errors),
        )

    def assert_response_ok(self, response, status_code=200, suggestions=None, caching=False):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(json.loads(response.content), {
            'errors': [],
            'suggestions': suggestions or [],
            'success': True,
            'caching_networks': caching,
        })

    def make_request(self, **kwargs):
        request = self.factory.get(
            self.url,
            kwargs,
        )
        return request

    def test_form_invalid(self):
        request = self.make_request()
        response = consumer_suggest(request)

        self.assert_errors(response, errors=[
            'namespace: Обязательное поле.',
            'keyword: Обязательное поле.',
        ])

    def test_by_name(self):
        request = self.make_request(keyword='bb_cons', namespace=7)

        response = consumer_suggest(request)
        suggestions = [dict(
            group='Потребители:',
            description='bb consumer',
            name='bb_consumer',
        )]
        self.assert_response_ok(response, suggestions=suggestions)

    def test_suggest_by_ip(self):
        request = self.make_request(keyword='77.88.40', namespace=1)

        response = consumer_suggest(request)
        suggestions = [dict(
            group='Потребители с сетью "77.88.40.96/28":',
            description='Это some_consumer',
            name='some_consumer',
            network_type='N',
        )]
        self.assert_response_ok(response, suggestions=suggestions)

    def test_by_macro_name(self):
        request = self.make_request(keyword='palka', namespace=1)

        response = consumer_suggest(request)
        suggestions = [dict(
            group='Потребители с фаервольным макросом "_KOPALKA_":',
            description='Это some_consumer',
            name='some_consumer',
            network_type='F',
        )]
        self.assert_response_ok(response, suggestions=suggestions)

    def test_macro_keyword_stripped(self):
        request = self.make_request(keyword='_PALKA', namespace=1)
        response = consumer_suggest(request)
        suggestions = [dict(
            group='Потребители с фаервольным макросом "_KOPALKA_":',
            description='Это some_consumer',
            name='some_consumer',
            network_type='F',
        )]
        self.assert_response_ok(response, suggestions=suggestions)

    def test_c_group_keyword_stripped(self):
        request = self.make_request(keyword='%stable', namespace=10)

        response = consumer_suggest(request)
        suggestions = [
            dict(
                group='Потребители с кондукторной группой "%passport-grantushka-stable":',
                description='blackbox_by_client consumer description',
                name='blackbox_by_client_consumer',
                network_type='C',
            ),
        ]
        self.assert_response_ok(response, suggestions=suggestions)

    def test_by_hostname(self):
        request = self.make_request(keyword='team', namespace=10)

        response = consumer_suggest(request)
        suggestions = [
            dict(
                group='Потребители с хостом "grantushka.yandex-team.ru":',
                description='blackbox_by_client consumer description',
                name='blackbox_by_client_consumer',
                network_type='H',
            ),
        ]
        self.assert_response_ok(response, suggestions=suggestions)

    def test_by_conductor_group(self):
        request = self.make_request(keyword='stable', namespace=10)

        response = consumer_suggest(request)
        suggestions = [
            dict(
                group='Потребители с кондукторной группой "%passport-grantushka-stable":',
                description='blackbox_by_client consumer description',
                name='blackbox_by_client_consumer',
                network_type='C',
            ),
        ]
        self.assert_response_ok(response, suggestions=suggestions)

    def test_not_found(self):
        request = self.make_request(keyword='bb_cons', namespace=1)

        response = consumer_suggest(request)
        self.assert_response_ok(response, suggestions=[])

    def test_networks_caching__empty(self):
        self.mock_redis.cache = {}

        request = self.make_request(keyword='team', namespace=7)

        response = consumer_suggest(request)
        self.assert_response_ok(response, suggestions=[], caching=True)

    def test_networks_caching__by_name(self):
        self.mock_redis.cache = {}
        request = self.make_request(keyword='cons', namespace=1)

        response = consumer_suggest(request)
        suggestions = [
            {
                u'group': u'Потребители:',
                u'description': u'Passport Consumer With Client',
                u'name': u'consumer_with_client',
            },
            {
                u'group': u'Потребители:',
                u'description': u'empty passport consumer',
                u'name': u'empty_passport_consumer',
            },
            {
                u'group': u'Потребители:',
                u'description': u'Это some_consumer',
                u'name': u'some_consumer',
            },
        ]
        self.assert_response_ok(response, suggestions=suggestions, caching=True)

    @patch('passport_grants_configurator.apps.core.views.consumer.SUGGEST_CONSUMER_MAX_RESULTS', 3)
    def test_network_caching__within_limit(self):
        self.mock_redis.cache = {}

        request = self.make_request(keyword='cons', namespace=1)

        response = consumer_suggest(request)
        suggestions = [
            {
                u'group': u'Потребители:',
                u'description': u'Passport Consumer With Client',
                u'name': u'consumer_with_client',
            },
            {
                u'group': u'Потребители:',
                u'description': u'empty passport consumer',
                u'name': u'empty_passport_consumer',
            },
            {
                u'group': u'Потребители:',
                u'description': u'Это some_consumer',
                u'name': u'some_consumer',
            },
        ]
        self.assert_response_ok(response, suggestions=suggestions, caching=False)
