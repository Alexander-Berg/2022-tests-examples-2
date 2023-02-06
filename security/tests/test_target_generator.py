

import ipaddress
from app.engines.utils import target_generator, target_generator_helper, target_generator_for_domain_name, is_exclude
from app.engines.utils import target_generator_for_ip_or_subnet, is_ip_or_subnet, taget_generator_to_ip_and_subnets


def test_target_generator():
    input_ = ['127.0.0.1', '::1', 'ya.ru', '_DEBBY_TEST_IPV4_', '192.168.0.0/31']
    output = [
        ['127.0.0.1', '87.250.250.242', '5.255.255.5', '192.168.0.0', '192.168.0.1'],
        ['::1', '2a02:6b8::2:242']
    ]
    results = list()
    for res in target_generator(input_):
        results.append(res)

    assert len(results) == 2
    assert results[0] == output[0]
    assert results[1] == output[1]


def test_target_generator_helper():
    input_ = ['127.0.0.1', '::1', 'ya.ru', '_DEBBY_TEST_IPV4_', '192.168.0.0/31']
    output = ['127.0.0.1', '::1', '87.250.250.242', '2a02:6b8::2:242', '5.255.255.5', '192.168.0.0', '192.168.0.1']

    results = list()

    for res in target_generator_helper(input_):
        results.append(res)

    assert results == output


def test_target_generator_for_domain_name():
    input = 'ya.ru'
    output = ['87.250.250.242', '2a02:6b8::2:242']

    results = list()

    for res in target_generator_for_domain_name(input):
        results.append(res)

    assert results == output


def test_target_generator_for_ip_or_subnet_IPv4():
    ip = '10.0.3.4'
    assert [ip] == list(target_generator_for_ip_or_subnet(ip))


def test_target_generator_for_ip_or_subnet_IPv6():
    ip = '2001::123:1'
    assert [ip] == list(target_generator_for_ip_or_subnet(ip))


def test_target_generator_for_ip_or_subnet_SUBNET_4():
    subnet = '192.168.0.0/30'
    expected = ['192.168.0.0', '192.168.0.1', '192.168.0.2', '192.168.0.3']
    assert expected == list(target_generator_for_ip_or_subnet(subnet))
    subnet = '192.168.0.3/30'
    expected = ['192.168.0.0', '192.168.0.1', '192.168.0.2', '192.168.0.3']
    assert expected == list(target_generator_for_ip_or_subnet(subnet))


def test_target_generator_for_ip_or_subnet_SUBNET_6():
    subnet = '2001::123:0/126'
    expected = ['2001::123:0', '2001::123:1', '2001::123:2', '2001::123:3']
    assert expected == list(target_generator_for_ip_or_subnet(subnet))
    subnet = '2001::123:2/126'
    expected = ['2001::123:0', '2001::123:1', '2001::123:2', '2001::123:3']
    assert expected == list(target_generator_for_ip_or_subnet(subnet))


def test_is_ip_or_subnet():
    assert is_ip_or_subnet('123.34.43.4') is True
    assert is_ip_or_subnet('123.34.43.4/10') is True
    assert is_ip_or_subnet('2002::2002') is True
    assert is_ip_or_subnet('2002::2002/30') is True
    assert is_ip_or_subnet('ya.ru') is False
    assert is_ip_or_subnet('_MACRO_') is False
    assert is_ip_or_subnet('R@ndom_String.123.123.123.::0') is False


def test_taget_generator_to_ip_and_subnets():
    input_ = ['127.0.0.1', '::1', 'ya.ru', '_DEBBY_TEST_IPV4_', '192.168.0.0/31']
    excpected_ips = [
        ipaddress.ip_address('127.0.0.1'),
        ipaddress.ip_address('::1'),
        ipaddress.ip_address('87.250.250.242'),
        ipaddress.ip_address('2a02:6b8::2:242'),
        ipaddress.ip_address('5.255.255.5'),
    ]
    excpected_nets = [
        ipaddress.ip_network('192.168.0.0/31')
    ]

    out_ips, out_nets = taget_generator_to_ip_and_subnets(input_)

    assert out_ips == excpected_ips
    assert out_nets == excpected_nets
    assert ([], []) == taget_generator_to_ip_and_subnets([])


def test_is_exclude():
    exclude_list = ['127.0.0.1', '::1', 'ya.ru', '_DEBBY_TEST_IPV4_', '192.168.0.1/31']
    exc_ips, exc_nets = taget_generator_to_ip_and_subnets(exclude_list)

    assert is_exclude('192.168.0.0', exc_ips, exc_nets) is True
    assert is_exclude('192.168.0.1', exc_ips, exc_nets) is True
    assert is_exclude('127.0.0.1', exc_ips, exc_nets) is True
    assert is_exclude('127.0.0.2', exc_ips, exc_nets) is False
    assert is_exclude('RANDOM', exc_ips, exc_nets) is False
