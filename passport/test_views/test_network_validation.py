# -*- coding: utf-8 -*-
import ujson as json

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from guardian.shortcuts import assign_perm

from passport_backend_core.builders.staff.faker import FakeStaff
from passport_grants_configurator.apps.core.models import Namespace, Network
from passport_grants_configurator.apps.core.test.utils import (
    MockRequests,
    MockUserPermissions,
    MockRedis,
    MockNetworkApi,
)
from passport_grants_configurator.apps.core.views import network_validation

from passport_grants_configurator.apps.core.exceptions import APIRequestFailedError

from ..test_data import *


class NetworkValidationCase(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(id=1)
        self.requests = MockRequests()
        self.requests.start()

        assign_perm(Namespace.REVIEW_ISSUE, self.user, Namespace.objects.get(id=1))

        self.redis = MockRedis()
        self.redis.start()

        self.network_api = MockNetworkApi()
        self.network_api.start()

        self.staff = FakeStaff()
        self.staff.start()

        self.user_permissions = MockUserPermissions(
            'passport_grants_configurator.apps.core.views.common.UserPermissions',
        )
        self.user_permissions.start()

    def tearDown(self):
        self.user_permissions.stop()
        self.staff.stop()
        self.network_api.stop()
        self.redis.stop()
        self.requests.stop()

    def make_request(self, string):
        request = self.factory.get('/grants/network_validation/', {
            'network': string,
            'environment': 1,
            'namespace': 1
        })
        request.user = self.user
        return network_validation(request)

    def assert_valid(self, response, expected_resp, expected_type):
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        actual_network = content.get('network')
        self.assertEqual(actual_network, expected_resp)
        self.assertEqual(content['network_valid'], True)
        self.assertEqual(content['type'], expected_type)

    def test_network_validation(self):
        test_data = (
            ('93.158.157.124', None, '93.158.157.124', Network.IP),
            ('5.45.248.128/26', None, '5.45.248.128/26', Network.IPNETWORK),
            (
                'grantushka.yandex-team.ru',
                '93.158.157.124',
                {'grantushka.yandex-team.ru': ['93.158.157.124']},
                Network.HOSTNAME,
            ),
        )
        for string, mock_response, expected_network, type_ in test_data:
            self.network_api.setup_response('getipsfromaddr', {string: [mock_response]})

            resp = self.make_request(string)
            self.assert_valid(resp, expected_network, type_)

    def test_macro_validation(self):
        macro_name = '_KOPALKA_'
        macro_children = [
            '37.140.181.0/28',
            '87.250.232.64/27',
            '93.158.133.0/26',
            '95.108.158.0/26',
            '95.108.225.128/26',
            '178.154.221.128/25',
            '2a02:6b8:0:212::/64',
            '2a02:6b8:0:811::/64',
            '2a02:6b8:0:c37::/64',
            '2a02:6b8:0:142b::/64',
            '2a02:6b8:0:1a41::/64',
            '2a02:6b8:0:250b::/64',
        ]
        self.network_api.setup_response(
            'expand_firewall_macro',
            {macro_name: macro_children},
        )
        resp = self.make_request(macro_name)
        self.assert_valid(
            resp,
            {macro_name: macro_children},
            Network.FIREWALL,
        )

    def test_old_conductor_macro_validation(self):
        macro_name = '_C_ACCENTURE_DEV_'
        resp = self.make_request(macro_name)
        self.assertEqual(resp.status_code, 200)
        content = json.loads(resp.content)
        self.assertEqual(content, {
            u'errors': [u'network: Old conductor macro used %s' % macro_name],
            u'network_valid': False,
            u'success': False,
        })

    def test_conductor_group_validation(self):
        conductor_group = '%passport-stable'
        conductor_hosts = [
            TEST_GRANTS_HOST1,
            TEST_GRANTS_HOST2,
        ]
        self.network_api.setup_response(
            'get_conductor_group_hosts',
            {conductor_group: conductor_hosts},
        )
        resp = self.make_request(conductor_group)
        self.assert_valid(
            resp,
            {conductor_group: conductor_hosts},
            Network.CONDUCTOR,
        )

    def test_invalid_network(self):
        self.requests.response.text = ''
        request = self.factory.get('/grants/network_validation/', {'network': 'asdfasdfasdf'})
        request.user = self.user

        response = network_validation(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['network_valid'], False)

    def test_no_network_string_in_request(self):
        request = self.factory.get('/grants/network_validation/', {})
        request.user = self.user

        response = network_validation(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {
            u'errors': [u'network: Обязательное поле.'],
            u'network_valid': False,
            u'success': False,
        })

    def test_user_with_other_namespace(self):
        self.user_permissions.UserPermissions.have_all.return_value = False
        self.requests.set_response_value_for_host('racktables.yandex.net', '5.45.248.128/26\tno\n')

        request = self.factory.get('/grants/network_validation/', {
            'network': '5.45.248.128/26', 'environment': 1, 'namespace': 2
        })
        request.user = User()
        response = network_validation(request)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['network_valid'], True)
        self.assertEqual(content['errors'], [u'Нет прав на сеть 5.45.248.128/26'])
        self.assertEqual(content['type'], Network.IPNETWORK)
        self.assertEqual(content['success'], False)

    def setup_request(self, string):
        self.user_permissions.UserPermissions.have_all.return_value = False
        request = self.factory.get('/grants/network_validation/', {'network': string})
        request.user = User(username='someuser')
        return request

    def assert_response(self, response, errors, network_type, success, network=None):
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(content.get('network'), network)
        self.assertTrue(content['network_valid'])
        self.assertEqual(content['errors'], errors)
        self.assertEqual(content['type'], network_type)
        self.assertEqual(content['success'], success)

    def test_ip_not_permitted(self):
        string = '89.122.23.9'

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [u'Не могу проверить права на ip-адрес %s' % string],
            Network.IP,
            False,
        )

    def test_ip_network_permitted(self):
        string = '5.45.248.128/26'
        self.requests.set_response_value_for_host('racktables.yandex.net', '5.45.248.128/26\tyes\n')

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [],
            Network.IPNETWORK,
            True,
            network=string,
        )

    def test_ip_network_not_permitted(self):
        strings = [('5.45.248.128/26', 'no'), ('25.45.248.128/26', 'unknown')]

        for string, result in strings:
            self.requests.set_response_value_for_host('racktables.yandex.net', '%s\t%s\n' % (string, result))

            request = self.setup_request(string)

            response = network_validation(request)
            self.assert_response(
                response,
                [u'Нет прав на сеть %s' % string],
                Network.IPNETWORK,
                False,
            )

    def test_conductor_group_permitted(self):
        string = '%passport-stable'
        conductor_hosts = [
            TEST_GRANTS_HOST1,
            TEST_GRANTS_HOST2,
        ]
        self.network_api.setup_response(
            'get_conductor_group_hosts',
            {string: conductor_hosts},
        )
        self.network_api.setup_response(
            'getipsfromaddr',
            {
                TEST_GRANTS_HOST1: TEST_GRANTS_IP1,
                TEST_GRANTS_HOST2: TEST_GRANTS_IP2,
            },
        )
        self.requests.set_response_value_for_host('ro.admin.yandex-team.ru', 'someuser,otheruser\n')

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [],
            Network.CONDUCTOR,
            True,
            network={string: [TEST_GRANTS_HOST1, TEST_GRANTS_HOST2]},
        )

    def test_conductor_group_not_permitted(self):
        string = '%passport-dev'

        conductor_hosts = [
            TEST_GRANTS_HOST1,
            TEST_GRANTS_HOST2,
        ]
        self.network_api.setup_response(
            'get_conductor_group_hosts',
            {string: conductor_hosts},
        )
        self.network_api.setup_response(
            'getipsfromaddr',
            {
                TEST_GRANTS_HOST1: TEST_GRANTS_IP1,
                TEST_GRANTS_HOST2: TEST_GRANTS_IP2,
            },
        )
        self.requests.set_response_value_for_host('ro.admin.yandex-team.ru', 'otheruser\n')

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [u'Нет прав на хост %s' % TEST_GRANTS_HOST1, u'Нет прав на хост %s' % TEST_GRANTS_HOST2],
            Network.CONDUCTOR,
            False,
        )

    def test_host_permitted(self):
        string = 'passport-rc-na1.yandex.net'

        self.requests.set_response_value_for_host('ro.admin.yandex-team.ru', 'someuser\n')
        self.network_api.setup_response(
            'getipsfromaddr',
            {
                'passport-rc-na1.yandex.net': ['2a02:6b8:0:c34::dd66', '178.154.221.102'],
            },
        )

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [],
            Network.HOSTNAME,
            True,
            network={'passport-rc-na1.yandex.net': ['2a02:6b8:0:c34::dd66', '178.154.221.102']},
        )

    def test_host_not_permitted(self):
        string = 'passport-rc-na1.yandex.net'

        self.requests.set_response_value_for_host('ro.admin.yandex-team.ru', 'avmm,dyor\n')
        self.network_api.setup_response(
            'getipsfromaddr',
            {
                'passport-rc-na1.yandex.net': ['2a02:6b8:0:c34::dd66', '178.154.221.102'],
            },
        )

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [u'Нет прав на хост %s' % string],
            Network.HOSTNAME,
            False,
        )

    def test_macro_permitted(self):
        string = '_KOPALKA_'

        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                string: ['5.45.248.128/26', 'tech1e.ps-cloud.yandex.net'],
            },
        )
        self.requests.set_response_value_for_host(
            'puncher.yandex-team.ru',
            '{"status": "success", "responsibles": ["%someuser%", "%beaver%"]}',
        )

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [],
            Network.FIREWALL,
            True,
            network={string: [u'5.45.248.128/26', u'tech1e.ps-cloud.yandex.net']},
        )

    def test_macro_not_permitted(self):
        string = '_KOPALKA_'

        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                string: ['5.45.248.128/26', 'tech1e.ps-cloud.yandex.net'],
            },
        )
        self.requests.set_response_value_for_host(
            'puncher.yandex-team.ru',
            '{"status": "success", "responsibles": ["%beaver%"]}',
        )

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [u'Нет прав на макрос %s' % string],
            Network.FIREWALL,
            False,
        )

    def test_api_error_on_check_macro_permission(self):
        string = '_KOPALKA_'

        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                string: ['5.45.248.128/26', 'tech1e.ps-cloud.yandex.net'],
            },
        )
        self.requests.raise_for_status.side_effect = APIRequestFailedError

        request = self.setup_request(string)
        response = network_validation(request)
        self.assert_response(
            response,
            [u'Не удалось получить %s из puncher: ' % string],
            Network.FIREWALL,
            False,
        )

    def test_empty_response_for_macro_responsible(self):
        """
        Если нет пользователей, могущих редактировать firewall, вывод будет пуст.
        """
        string = '_KOPALKA_'
        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                string: ['5.45.248.128/26', 'tech1e.ps-cloud.yandex.net'],
            },
        )
        self.requests.set_response_value_for_host(
            'puncher.yandex-team.ru',
            '{"status": "success", "responsibles": []}',
        )

        request = self.setup_request(string)

        response = network_validation(request)
        self.assert_response(
            response,
            [u'Нет прав на макрос %s' % string],
            Network.FIREWALL,
            False,
        )

    def test_cannot_get_user(self):
        request = self.factory.get('/grants/network_validation/', {'network': 'grantushka.yandex-team.ru'})
        request.user = None
        response = network_validation(request)
        content = json.loads(response.content)

        self.assertEqual(content['errors'], [u'Не удалось определить Ваш логин'])
        self.assertEqual(content['success'], False)
