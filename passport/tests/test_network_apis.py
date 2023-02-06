# -*- coding: utf-8 -*-
import socket

from copy import deepcopy
from dns.exception import (
    DNSException,
    Timeout,
)
from dns.resolver import NXDOMAIN

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from django.test import TestCase

from passport_grants_configurator.apps.core.exceptions import (
    APIRequestFailedError,
    NetworkResolveError,
    UnknownNetworkTypeError,
    NotFoundError,
)
from passport_grants_configurator.apps.core.models import (
    network_unicode,
    Network,
)
from passport_grants_configurator.apps.core.network_apis import (
    check_ipnetworks_permissions,
    get_hostname_responsible_people,
    NetworkResolver,
    is_valid_address,
    _looks_like_conductor_group,
    _looks_like_hostname,
    _looks_like_ip_address,
    _looks_like_ip_network,
    _looks_like_macro,
    _looks_like_trypo_support_network,
    looks_like_old_conductor_macro,
    looks_like_server_macro,
    parse_macro_responsible,
    parse_user_staff_groups,
)
from passport_grants_configurator.apps.core.test.utils import (
    MockRequests,
    MockRedis,
    MockNetworkApi,
)
from .test_data import *

LOCALHOST = socket.gethostbyaddr('127.0.0.1')[0]


def test_validate_address__ok():
    """Правильный адрес проходит без изменений"""
    valid_list = [
        'www.yandex.ru',
        u'грантушка.паспорт.яндекс.рф',
    ]

    for address in valid_list:
        actual = is_valid_address(address)
        yield eq_, actual, True


def test_validate_address__errors():
    """Неправильный адрес заменяется на пустую строчку"""
    invalid_list = [
        'www..yandex.ru',  # Этот адрес не получится закодировать в idna
    ]

    for address in invalid_list:
        actual = is_valid_address(address)
        yield eq_, actual, False


def test_looks_like_ip_address():
    good_cases = [
        '127.0.0.1',
        '192.168.1.1',
        '2a02:6b8:0:1a71::29b6',
    ]
    bad_cases = [
        'badaddress',
        '127001',
        '192.168.0.0/24',
    ]

    for case in good_cases:
        yield eq_, _looks_like_ip_address(case), True

    for case in bad_cases:
        yield eq_, _looks_like_ip_address(case), False


def test_looks_like_ip_network():
    good_cases = [
        '127.0.0.1/8',
        '192.168.1.1/24',
        'fe80::/10',
    ]
    bad_cases = [
        'badnetwork',
        '127001',
    ]

    for case in good_cases:
        yield eq_, _looks_like_ip_network(case), True

    for case in bad_cases:
        yield eq_, _looks_like_ip_network(case), False


def test_looks_like_trypo_support_network():
    good_cases = [
        '123@::1',
        '788@dead::beaf',
        '788@dead::80/40',
        'f@123:123::/65',
        '7fffffff@123:123::/65',
    ]
    bad_cases = [
        '127.0.0.1/8',
        '192.168.1.1/24',
        'fe80::/10',
        'badnetwork@',
        '127001',
        '@123:123::/65',
        '7fffffff1@123:123::/65',
    ]

    for case in good_cases:
        yield eq_, _looks_like_trypo_support_network(case), True

    for case in bad_cases:
        yield eq_, _looks_like_trypo_support_network(case), False


def test_looks_like_macro():
    good_cases = [
        '_PASSPORT_',
        '_passport_',
        '_C_PASSPORT_GRANTUSHKA_STABLE_',
    ]
    bad_cases = [
        'badmacro',
        '_',
        '192.168.0.0/24',
        '127.0.0.1',
    ]

    for case in good_cases:
        yield eq_, _looks_like_macro(case), True

    for case in bad_cases:
        yield eq_, _looks_like_macro(case), False


def test_looks_like_hostname():
    good_cases = [
        'mail.yandex.ru',
        'passportdev-python.yandex.net',
    ]
    bad_cases = [
        'badaddress',
        '_',
        '192.168.0.0/24',
        '127.0.0.1',
    ]

    for case in good_cases:
        yield eq_, _looks_like_hostname(case), True

    for case in bad_cases:
        yield eq_, _looks_like_hostname(case), False


def test_looks_like_conductor_group():
    good_cases = [
        '%passport-front-stable',
        '%passport_front-stable',
        '%passport',
    ]
    bad_cases = [
        'badaddress',
        '_%passport',
        '%passport-STABLE',
    ]

    for case in good_cases:
        yield eq_, _looks_like_conductor_group(case), True

    for case in bad_cases:
        yield eq_, _looks_like_conductor_group(case), False


def test_looks_like_old_conductor_macro():
    good_cases = [
        '_C_',
        '_C_ACCENTURE_DEV_',
        '_c_test_',
        '_C_test_',
    ]
    bad_cases = [
        '_C_PASS',
        '%passport',
        '_CACC_',
        'C_CAPC_',
        '_B_',
    ]
    for case in good_cases:
        yield eq_, looks_like_old_conductor_macro(case), True

    for case in bad_cases:
        yield eq_, looks_like_old_conductor_macro(case), False


def test_looks_like_server_macro():
    good_cases = [
        '_PASSPORT_SRV_',
        '_passport_srv_',
        'C_PASSPORT_GRANTUSHKASRV',
        'C_PASSPORT_GRANTUSHKAsrv_',
    ]
    bad_cases = [
        'PASSPORT_GRANTUSHKAsvr',
        'PASSPORT_GRANTUSHKAS',
        'PASSPORT_GRANTUSHKA_SR',
    ]

    for case in good_cases:
        yield eq_, looks_like_server_macro(case), True

    for case in bad_cases:
        yield eq_, looks_like_server_macro(case), False


def test_parse_macro_responsible():
    good_responses = [
        (
            '{"status": "success", "responsibles": ["%squirrel%", "%beaver%"]}',
            (
                False,
                dict(
                    people={'squirrel', 'beaver'},
                ),
            ),
        ),
        (
            '{"status": "success", "responsibles": []}',
            (
                False,
                dict(
                    people=set(),
                ),
            ),
        ),
    ]

    for response, expected in good_responses:
        yield eq_, parse_macro_responsible(response), expected

    error_string = '{"status": "error"}'
    assert_raises(APIRequestFailedError, parse_macro_responsible, error_string)


def test_parse_user_staff_groups():
    response = [
        {
            'group': {
                'url': 'yandex_search_tech_searchinfradev',
                'ancestors': [
                    {'url': 'yandex'},
                    {'url': 'yandex_main_searchadv'},
                ],
            },
        },
        {
            'group': {
                'url': 'yandex_search_tech_test',
                'ancestors': [
                    {'url': 'yandex_main_searchadv_test'},
                ],
            },
        },
    ]
    expected = [
        'yandex_search_tech_searchinfradev',
        'yandex',
        'yandex_main_searchadv',
        'yandex_search_tech_test',
        'yandex_main_searchadv_test',
    ]
    eq_(sorted(parse_user_staff_groups(response)), sorted(expected))

    empty_responses = [
        [],
        [{'smth': []}],
        [
            {
                'group': {
                    'smth': [],
                },
            },
        ],
        [
            {
                'group': {
                    'url': None,
                    'ancestors': [
                        {'smth': None},
                    ],
                },
            },
        ],
    ]
    for response in empty_responses:
        yield ok_, not parse_user_staff_groups(response)


class TestNetworkTypeGetterCase(TestCase):
    fixtures = ['default.json']
    maxDiff = None

    def setUp(self):
        self.requests = MockRequests()
        self.requests.start()
        self.redis = MockRedis()
        self.redis.start()
        self.network_api = MockNetworkApi()
        self.network_api.start()

    def tearDown(self):
        self.network_api.stop()
        self.redis.stop()
        self.requests.stop()

    def get_warnings(self):
        return {
            'auto_resolve': [],
            'manual_resolve': [],
            'excluded': [],
            'decreased': {},
        }

    def test_is_ipnetwork(self):
        ipnetworks = [
            '0.0.0.0/0',
            '213.180.193.0/25',
            '4130@2a02:6b8:c00::/40',
            'ff@2a02:6b8:0::/40',
            'a@fe80::/10',
        ]
        for ipnetwork in ipnetworks:
            self.assertTrue(NetworkResolver.get_type(ipnetwork))

    def test_detect_type_ip(self):
        ips = [
            '192.168.0.1',
            '95.108.222.186',
            '95.108.230.35',
            '178.154.246.118',
            '77.88.34.36',
        ]
        for ip in ips:
            self.assertEqual(NetworkResolver.get_type(ip), Network.IP)

    def test_detect_type_host(self):
        hosts = [
            'phone-passport-test.yandex.ru',
            'passport-test.yandex.ru',
            'social-dev.yandex.ru',
            'pperekalov.dev.yandex.net',
        ]
        # Отобразим все имена в "реальный" IP
        ip_map = {host: ['192.168.1.1'] for host in hosts}
        self.network_api.setup_response('getipsfromaddr', ip_map)

        for host in hosts:
            self.assertEqual(NetworkResolver.get_type(host), Network.HOSTNAME)

    def test_detect_type_network(self):
        ipnetworks = [
            '0.0.0.0/0',
            '77.88.20.128/25',
            '213.180.193.0/25',
            '4130@2a02:6b8:c00::/40',
            'ff@2a02:6b8:0::/40',
        ]
        for ipnetwork in ipnetworks:
            self.assertEqual(NetworkResolver.get_type(ipnetwork), Network.IPNETWORK)

    def test_detect_type_firewall_macro(self):
        firewall_macros = [
            (
                '_KOPALKA_',
                [
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
                    '123@2a02:6b8:0::/40',
                ],
            ),
        ]

        for macro, object_list in firewall_macros:
            self.network_api.setup_response(
                'expand_firewall_macro',
                {macro: object_list},
            )
            self.assertEqual(NetworkResolver.get_type(macro), Network.FIREWALL)

    def test_detect_type_firewall__known_name__ok(self):
        """
        Определяем тип сети. Макрос
        Строка выглядит как макрос,
        HBF вернул список сетей этого макроса - это макрос
        """
        macro_name = '_KOPALKA_'
        self.network_api.setup_response(
            'expand_firewall_macro',
            {macro_name: ['123@2a02:6b8:0::/40']},
        )

        network_type = NetworkResolver.get_type(macro_name)

        self.assertEqual(network_type, Network.FIREWALL)

    def test_detect_type_unknown(self):
        invalid_objects = [
            '1234hjkl',
            '\][]435$#%',
        ]

        for network_name in invalid_objects:
            self.assertRaises(UnknownNetworkTypeError, NetworkResolver.get_type, network_name)

    def test_get_type_conductor_group(self):
        conductor_groups = [
            '%500px-testing',
            '%passport-front-stable',
        ]
        for conductor_group in conductor_groups:
            network_type, _ = NetworkResolver.get_type_and_children(conductor_group)
            self.assertEqual(network_type, Network.CONDUCTOR)

    def test_bad_firewall_macro(self):
        macro_name = '_ASDFGHJKL_'
        self.setup_macro_server_responses(macro_name=macro_name, values=[])
        self.assertRaises(UnknownNetworkTypeError, NetworkResolver.get_type, macro_name)

    def test_not_found_firewall_macro(self):
        macro_name = '_ASDFGHJKL_'
        self.network_api.setup_response(
            'expand_firewall_macro',
            {macro_name: NotFoundError()},
        )
        self.assertRaises(NotFoundError, NetworkResolver.get_type, macro_name)

    def test_check_ipnetwork_permissions(self):
        ipnetwork_response = (
            ('37.140.181.0/28', '5.45.248.128/26\tno\n', False),
            ('37.140.181.0/28', '5.45.248.128/26\tunknown\n', None),
            ('87.250.232.64/27', '87.250.232.64/27\tyes\n', True),
        )

        for string, response, expected in ipnetwork_response:
            self.requests.response.text = response

            check_result, message = NetworkResolver.check_permissions(
                Network.IPNETWORK,
                string,
                'username',
            )
            self.assertEqual(check_result, expected)

    def test_check_hostname_permissions(self):
        hostname_response = (
            ('tech2e.ps-cloud.yandex.net', 'prius,askort\n', False),
            ('tech1e.ps-cloud.yandex.net', 'username,askort\n', True),
        )

        for string, response, expected in hostname_response:
            self.requests.response.text = response
            check_result, message = NetworkResolver.check_permissions(
                Network.HOSTNAME,
                string,
                'username',
            )
            self.assertEqual(
                check_result,
                expected,
            )

    def test_check_hostname_permissions_empty_response__not_allowed(self):
        self.requests.response.text = '\n'
        check_result, _ = NetworkResolver.check_permissions(
            Network.HOSTNAME,
            'grantushka.yandex-team.ru',
            'username',
        )
        self.assertFalse(check_result)

    def setup_macro_server_responses(self, macro_name, values=None):
        default_values = [
            TEST_GRANTS_HOST1,
            TEST_GRANTS_HOST2,
        ]
        values = values if values is not None else default_values
        self.network_api.setup_response(
            'expand_firewall_macro',
            {macro_name: values},
        )

        # Результат получения адресов хостов
        self.network_api.setup_response('getipsfromaddr', {
            TEST_GRANTS_HOST1: [TEST_GRANTS_IP1],
            TEST_GRANTS_HOST2: [TEST_GRANTS_IP2],
        })

        hostname_response = (
            (TEST_GRANTS_HOST1, 'prius,askort\n'),
            (TEST_GRANTS_HOST2, 'username,askort\n'),
        )

        for _, responsible in hostname_response:
            self.requests.set_response_value_for_host(
                'ro.admin.yandex-team.ru',
                responsible,
            )

    def test_firewall_permissions_server_macro_not_allowed(self):
        macro_name = '_TEST_SRV_'
        self.setup_macro_server_responses(macro_name)

        check_result, _ = NetworkResolver.check_permissions(
            Network.FIREWALL,
            macro_name,
            'username',
        )

        self.assertFalse(check_result)

    def test_firewall_permissions_server_macro_ok(self):
        macro_name = '_TEST_SRV_'
        self.setup_macro_server_responses(macro_name)

        check_result, _ = NetworkResolver.check_permissions(
            Network.FIREWALL,
            macro_name,
            'askort',
        )

        self.assertTrue(check_result)

    def test_firewall_permissions(self):
        self.requests.response.text = '{"status": "success", "responsibles": ["%demian%", "%shchukin%"]}'

        cases = (
            (
                '_TECH_NONPROD_',
                'shchukin',
                True,
            ),
            (
                '_TECH_NONPROD_',
                'demian',
                True,
            ),
        )
        for macro, user, expected in cases:
            check_result, message = NetworkResolver.check_permissions(
                Network.FIREWALL,
                macro,
                user,
            )

            self.assertEqual(check_result, expected)

    def test_firewall_permissions_error(self):
        self.requests.response.text = '{"status": "error", "responsibles": ["%demian%", "%shchukin%"]}'

        cases = (
            (
                '_TECH_NONPROD_',
                'shchukin',
            ),
            (
                '_TECH_NONPROD_',
                'demian',
            ),
        )
        for macro, user in cases:
            with self.assertRaises(APIRequestFailedError):
                NetworkResolver.check_permissions(
                    Network.FIREWALL,
                    macro,
                    user,
                )

    def test_conductor_permissions(self):
        # Результат раскрытия группы
        self.network_api.setup_response('get_conductor_group_hosts', {
            '%passport-grantushka-stable': [TEST_GRANTS_HOST1],
            '%passport-grantushka-unstable': [TEST_GRANTS_HOST2],
        })
        # Результат получения адресов хостов
        self.network_api.setup_response('getipsfromaddr', {
            TEST_GRANTS_HOST1: [TEST_GRANTS_IP1],
            TEST_GRANTS_HOST2: [TEST_GRANTS_IP2],
        })
        cases = (
            (
                '%passport-grantushka-stable',
                TEST_GRANTS_HOST1,
                'someuser2\n',
                False,
            ),
            (
                '%passport-grantushka-unstable',
                TEST_GRANTS_HOST2,
                'someuser2,someuser\n',
                True,
            ),
        )
        for c_group, qs_re, response, expected in cases:
            self.requests.set_response_value_for_host('ro.admin.yandex-team.ru', response, qs_re=qs_re)
            check_result, message = NetworkResolver.check_permissions(
                Network.CONDUCTOR,
                c_group,
                'someuser',
            )
            self.assertEqual(check_result, expected)

    def test_exclude_forbidden_ips_and_nets(self):
        all_good = ['23@ff::/23', '1::/40', '123.213.90.12']
        clean, excluded = NetworkResolver.get_clean_ips_and_excluded_nets(all_good)
        ok_(not excluded)
        self.assertItemsEqual(clean, all_good)

        mixed = ['23@ff::/23', '127.0.0.8', '::/0']
        clean, excluded = NetworkResolver.get_clean_ips_and_excluded_nets(mixed)
        self.assertItemsEqual(excluded, ['127.0.0.8', '::/0'])
        self.assertItemsEqual(clean, ['23@ff::/23'])

        all_bad = [TEST_IP_LOCALHOST_4, TEST_ALL_NETS_6, TEST_ALL_NETS_4, TEST_IP_LOCALHOST_6]
        clean, excluded = NetworkResolver.get_clean_ips_and_excluded_nets(all_bad)
        ok_(not clean)
        self.assertItemsEqual(excluded, all_bad)

    def test_get_ips_from_hosts(self):
        self.network_api.setup_response('getipsfromaddr', {
            'grantushka.yandex-team.ru': ['93.158.157.124'],
            'localhost': [TEST_IP_LOCALHOST_6, TEST_IP_LOCALHOST_4],
            'pperekalov.dev.yandex.net': ['2a02:6b8:0:1a16:556::24', TEST_ALL_NETS_6],
        })

        hosts = [
            ('grantushka.yandex-team.ru', ['93.158.157.124'], []),
            ('localhost', [], [TEST_IP_LOCALHOST_6, TEST_IP_LOCALHOST_4]),
            ('pperekalov.dev.yandex.net', ['2a02:6b8:0:1a16:556::24'], [TEST_ALL_NETS_6]),
        ]

        for hostname, expected_ip_list, excluded in hosts:
            network = Network.objects.get(string=hostname)
            resolved, unresolved = NetworkResolver.get_ips(network)
            eq_(
                sorted(resolved),
                sorted(expected_ip_list),
            )
            warnings = self.get_warnings()
            warnings['excluded'].extend(excluded)
            self.assertItemsEqual(unresolved, warnings)

    def test_get_ips_from_hosts__ok(self):
        bad_hosts = {
            'grantushka.yandex-team.ru': NXDOMAIN(),
            'pperekalov.dev.yandex.net': Timeout(),
            'localhost': DNSException(),
        }
        self.network_api.setup_response('getipsfromaddr', bad_hosts)

        for hostname, expected_response in bad_hosts.iteritems():
            network = Network.objects.get(string=hostname)
            expected_warnings = self.get_warnings()
            expected_warnings['auto_resolve'].append(hostname)

            resolved, unresolved = NetworkResolver.get_ips(network)
            eq_(resolved, [])
            eq_(unresolved, expected_warnings)

    def test_get_ips_from_conductor_groups(self):
        conductor_groups = [
            ('%passport-grantushka-stable', [TEST_GRANTS_IP1, TEST_GRANTS_IP2], []),
            ('%passport-grantushka-unstable', [], ['%passport-grantushka-unstable']),
        ]
        # Подразумеваю, что кондукторные группы содержат только хосты
        self.network_api.setup_response('get_conductor_group_hosts', {
            '%passport-grantushka-stable': [
                TEST_GRANTS_HOST1,
                TEST_GRANTS_HOST2,
            ],
            '%passport-grantushka-unstable': NotFoundError(),
        })
        self.network_api.setup_response('getipsfromaddr', {
            TEST_GRANTS_HOST1: [TEST_GRANTS_IP1],
            TEST_GRANTS_HOST2: [TEST_GRANTS_IP2],
        })

        for group, resolved_list, unresolved_list in conductor_groups:
            network = Network.objects.get(string=group)
            resolved, unresolved = NetworkResolver.get_ips(network)
            self.assertEqual(resolved, resolved_list)
            warnings = self.get_warnings()
            warnings.update(manual_resolve=unresolved_list)
            self.assertEqual(unresolved, warnings)

    def test_get_ips_from_conductor_groups_excluded(self):
        conductor_groups = [
            (
                '%passport-grantushka-stable',
                [
                    TEST_ALL_NETS_4,
                    TEST_IP_LOCALHOST_4,
                    TEST_ALL_NETS_6,
                    TEST_IP_LOCALHOST_6,
                ],
            ),
        ]
        # Подразумеваю, что кондукторные группы содержат только хосты
        self.network_api.setup_response('get_conductor_group_hosts', {
            '%passport-grantushka-stable': [
                TEST_GRANTS_HOST1,
                TEST_GRANTS_HOST2,
            ],
        })
        self.network_api.setup_response('getipsfromaddr', {
            TEST_GRANTS_HOST1: [TEST_ALL_NETS_4, TEST_IP_LOCALHOST_4],
            TEST_GRANTS_HOST2: [TEST_ALL_NETS_6, TEST_IP_LOCALHOST_6],
        })

        for group, expected in conductor_groups:
            network = Network.objects.get(string=group)
            resolved, unresolved = NetworkResolver.get_ips(network)
            self.assertEqual(resolved, [])
            warnings = self.get_warnings()
            warnings['excluded'].extend(expected)
            self.assertItemsEqual(unresolved, warnings)

    def test_get_ips_from_conductor_groups_warnings(self):
        conductor_groups = [
            ('%passport-grantushka-stable', [TEST_GRANTS_HOST1, TEST_GRANTS_HOST2]),
        ]
        # Подразумеваю, что кондукторные группы содержат только хосты
        self.network_api.setup_response('get_conductor_group_hosts', {
            '%passport-grantushka-stable': [
                TEST_GRANTS_HOST1,
                TEST_GRANTS_HOST2,
            ],
        })
        self.network_api.setup_response('getipsfromaddr', {
            TEST_GRANTS_HOST1: NetworkResolveError(),
            TEST_GRANTS_HOST2: NetworkResolveError(),
        })

        for group, expected_list in conductor_groups:
            network = Network.objects.get(string=group)
            resolved, unresolved = NetworkResolver.get_ips(network)
            self.assertEqual(resolved, [])
            warns = self.get_warnings()
            warns['auto_resolve'].extend(expected_list)
            self.assertEqual(unresolved, warns)

    def test_get_ips_from_conductor_group__error(self):
        bad_groups = [
            '%passport-grantushka-stable',
            '%passport-grantushka-unstable',
        ]
        self.network_api.setup_response(
            'get_conductor_group_hosts',
            dict.fromkeys(bad_groups, NetworkResolveError('test')),
        )

        for host in bad_groups:
            network = Network.objects.get(string=host)
            with self.assertRaises(NetworkResolveError):
                NetworkResolver.get_ips(network)

    def test_get_ips_from_ip(self):
        ips = [
            (TEST_GRANTS_IP1, [TEST_GRANTS_IP1]),
            (TEST_ALL_NETS_6, [TEST_ALL_NETS_6]),
            (TEST_ALL_NETS_4, [TEST_ALL_NETS_4]),
            (TEST_IP_LOCALHOST_4, [TEST_IP_LOCALHOST_4]),
            ('127.123.90.9', ['127.123.90.9']),
        ]

        for ip, expected_list in ips:
            network = Network.objects.get(string=ip)
            resolved, unresolved = NetworkResolver.get_ips(network)
            self.assertEqual(resolved, expected_list)
            self.assertEqual(unresolved, self.get_warnings())

    def test_get_ipnetworks_from_firewall_macro(self):
        self.network_api.setup_response('getipsfromaddr', {
            'tech1e.ps-cloud.yandex.net': ['87.250.252.17', '2a02:6b8:0:1626::8'],
            'tech2e.ps-cloud.yandex.net': ['87.250.252.28', '123@2a02:6b8:0::/40'],
        })

        firewall_macro = [
            (
                '_KOPALKA_',
                [
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
                ],
                [
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
                ],
            ),
            (
                '_TECH_NONPROD_SRV_',
                [
                    '87.250.252.17',
                    '87.250.252.28',
                    '2a02:6b8:0:1626::8',
                    '123@2a02:6b8:0::/40',
                ],
                [
                    'tech1e.ps-cloud.yandex.net',
                    'tech2e.ps-cloud.yandex.net',
                ],
            ),
        ]

        for macro, expected_list, expanded in firewall_macro:
            self.network_api.setup_response(
                'expand_firewall_macro',
                {macro: expanded},
            )
            network = Network.objects.get(string=macro)

            actual_list, unresolved_data = NetworkResolver.get_ips(network)
            self.assertEqual(set(actual_list), set(expected_list))
            self.assertEqual(unresolved_data, self.get_warnings())

    def test_get_ipnetworks_from_firewall_macro_excluded(self):

        firewall_macro = [
            (
                '_KOPALKA_',
                [
                    '37.140.181.0/28',
                ],
                [
                    '37.140.181.0/28',
                    TEST_IP_LOCALHOST_6,
                ],
                [
                    TEST_IP_LOCALHOST_6,
                ],
            ),
            (
                '_TECH_NONPROD_SRV_',
                [
                    '87.250.252.17',
                    '2a02:6b8:0:1626::8',
                    '123@2a02:6b8:0::/40',
                ],
                [
                    '87.250.252.17',
                    TEST_ALL_NETS_4,
                    '2a02:6b8:0:1626::8',
                    '123@2a02:6b8:0::/40',
                ],
                [
                    TEST_ALL_NETS_4,
                ],
            ),
        ]

        for macro, expected_list, expanded, excluded in firewall_macro:
            self.network_api.setup_response(
                'expand_firewall_macro',
                {macro: expanded},
            )
            network = Network.objects.get(string=macro)

            actual_list, unresolved_data = NetworkResolver.get_ips(network)
            self.assertEqual(set(actual_list), set(expected_list))
            warnings = self.get_warnings()
            warnings['excluded'].extend(excluded)
            self.assertEqual(unresolved_data, warnings)

    def test_get_macro_with_decreased_by_trypo(self):
        macro_name = '_MACRO_WITHOUT_TRYPO_'

        children = [
            '37.140.181.0/28',
            '123@2a02:6b8:0:1626::8/40',
        ]

        network = Network.objects.get(string=macro_name)

        self.network_api.setup_response(
            'expand_firewall_macro',
            {macro_name: children},
        )
        actual_list, unresolved_data = NetworkResolver.get_ips(network)

        self.assertEqual(set(actual_list), set(children))
        self.assertEqual(unresolved_data, self.get_warnings())

    def test_get_macro_with_decreased_children(self):
        self.network_api.setup_response('getipsfromaddr', {
            'tech1e.ps-cloud.yandex.net': ['87.250.252.17', '2a02:6b8:0:1626::8'],
        })

        macro_name = '_YET_ANOTHER_TEST_MACRO_'

        firewall_macro = [
            (
                [
                    '37.140.181.0/28',
                ],
                [
                    '37.140.181.0/28',
                ],
            ),
            (
                [
                    '87.250.252.17',
                    '2a02:6b8:0:1626::8',
                ],
                [
                    'tech1e.ps-cloud.yandex.net',
                ],
            ),
        ]

        network = Network.objects.get(string=macro_name)

        for expected_list, expanded in firewall_macro:
            self.network_api.setup_response(
                'expand_firewall_macro',
                {macro_name: expanded},
            )
            actual_list, unresolved_data = NetworkResolver.get_ips(network)

            self.assertEqual(set(actual_list), set(expected_list))
            warnings = deepcopy(self.get_warnings())
            warnings['decreased'].update(
                name=macro_name,
                old=[
                    '87.250.252.17',
                    '2a02:6b8:0:1626::8',
                    '123@2a02:6b8:0::/40',
                    'test.com',
                    'fake.test.com',
                    'fake.com',
                ],
                new=expanded,
            )
            self.assertEqual(unresolved_data, warnings)


class CheckIPNetworkPermissionsCase(TestCase):
    def setUp(self):
        self.mock_requests = MockRequests()
        self.mock_requests.patch.start()

    def tearDown(self):
        self.mock_requests.patch.stop()

    def test_check_multiple_ipnetworks_permissions(self):
        self.mock_requests.response.text = '37.140.181.0/28\tno\n87.250.232.64/27\tyes\n123@2a02:6b8:0::/40\tyes'
        self.assertEqual(
            check_ipnetworks_permissions('someuser', ['37.140.181.0/28', '87.250.232.64/27', '123@2a02:6b8:0::/40']),
            [
                ('37.140.181.0/28', False),
                ('87.250.232.64/27', True),
                ('123@2a02:6b8:0::/40', True),
            ],
        )

    def test_check_ipnetworks_permissions(self):
        self.mock_requests.response.text = '37.140.181.0/28\tno\n'
        self.assertEqual(
            check_ipnetworks_permissions('someuser', '37.140.181.0/28'),
            [
                ('37.140.181.0/28', False),
            ]
        )

    def test_resolve_error(self):
        self.mock_requests.raise_for_status.side_effect = NetworkResolveError
        self.assertRaises(NetworkResolveError, check_ipnetworks_permissions, 'someuser', '37.140.181.0/28')


class GetHostnameResponsiblePeople(TestCase):
    def setUp(self):
        self.mock_requests = MockRequests()
        self.mock_requests.patch.start()

    def tearDown(self):
        self.mock_requests.patch.stop()

    def test_get_responsible_people(self):
        self.mock_requests.response.text = 'dyor,avmm\n'
        self.assertEqual(get_hostname_responsible_people('phone-passport-test.yandex.ru'), ['dyor', 'avmm'])

    def test_resolve_error(self):
        self.mock_requests.raise_for_status.side_effect = NetworkResolveError
        self.assertRaises(NetworkResolveError, get_hostname_responsible_people, 'grantushka.yandex-team.ru')


class NetworkUnicode(TestCase):
    def test_network_unicode_without_params(self):
        eq_(
            network_unicode(string='127.0.0.1', type_=Network.IP),
            u'IP адрес 127.0.0.1',
        )

    def test_network_unicode_with_params(self):
        eq_(
            network_unicode(
                string='127.0.0.2',
                type_=Network.IP,
                number='singular',
                case='genitive',
            ),
            u'IP адреса 127.0.0.2',
        )
