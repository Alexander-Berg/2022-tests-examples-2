from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network

from app.utils import is_subnet, is_valid_ipv4_address, is_valid_ipv6_address, addr_to_proto
from app.utils import str_to_ipaddress4, str_to_ipaddress6, str_to_ipaddress_any
from app.utils import str_to_ipnetwork_any, str_to_ipnetwork4, str_to_ipnetwork6
from app.utils import iterate_ports, uniq_ports, port_list_to_ports_str
from app.settings import PROTO_IPV4, PROTO_IPV6


def test_is_subnet():
    assert is_subnet('1.1.1.1/32') is True
    assert is_subnet('1.1.1.1/33') is False
    assert is_subnet('1.1.1.1/0') is True
    assert is_subnet('1.1.1.1/-1') is False
    assert is_subnet('fe00::1/-1') is False
    assert is_subnet('fe00::1/100') is True
    assert is_subnet('fe00::1/128') is True
    assert is_subnet('fe00::1/129') is False
    assert is_subnet('fe00::1/-1') is False
    assert is_subnet(list()) is False
    assert is_subnet({192,168,1,1}) is False
    assert is_subnet(set()) is False
    assert is_subnet(dict()) is False
    assert is_subnet(31337) is False
    assert is_subnet("0") is False


def test_is_valid_ipv4_address():
    assert is_valid_ipv4_address('127.0.0.1') is True
    assert is_valid_ipv4_address('127.0.0.1/0') is False
    assert is_valid_ipv4_address('::1') is False
    assert is_valid_ipv4_address('::1/0') is False


def test_is_valid_ipv6_address():
    assert is_valid_ipv6_address('127.0.0.1') is False
    assert is_valid_ipv6_address('127.0.0.1/0') is False
    assert is_valid_ipv6_address('::1') is True
    assert is_valid_ipv6_address('::1/0') is False


def test_addr_to_proto():
    assert PROTO_IPV4 != PROTO_IPV6
    assert addr_to_proto('127.0.0.1') == PROTO_IPV4
    assert addr_to_proto('192.168.0.1') == PROTO_IPV4
    assert addr_to_proto('::1') == PROTO_IPV6
    assert addr_to_proto('2000::1') == PROTO_IPV6


def test_str_to_ipaddress4():
    assert isinstance(str_to_ipaddress4('127.0.0.1'), IPv4Address)
    assert isinstance(str_to_ipaddress_any('127.0.0.1'), IPv4Address)
    assert str_to_ipaddress4('2001::1') is None
    assert isinstance(str_to_ipaddress4('127.0.0.1'), IPv4Address)
    assert isinstance(str_to_ipaddress_any('127.0.0.1'), IPv4Address)
    assert str_to_ipaddress4('2001::1') is None


def test_str_to_ipaddress6():
    assert isinstance(str_to_ipaddress6('2001::1'), IPv6Address)
    assert isinstance(str_to_ipaddress_any('2001::1'), IPv6Address)
    assert str_to_ipaddress6('10.0.0.1') is None
    assert isinstance(str_to_ipaddress6('2001::1'), IPv6Address)
    assert isinstance(str_to_ipaddress_any('2001::1'), IPv6Address)
    assert str_to_ipaddress6('10.0.0.1') is None


def test_str_to_ipnetwork4():
    assert isinstance(str_to_ipnetwork_any('10.0.0.0/24'), IPv4Network)
    assert isinstance(str_to_ipnetwork4('10.0.0.0/24'), IPv4Network)
    assert str_to_ipnetwork4('2001::/64') is None
    assert isinstance(str_to_ipnetwork_any('10.0.0.0/24'), IPv4Network)
    assert isinstance(str_to_ipnetwork4('10.0.0.0/24'), IPv4Network)
    assert str_to_ipnetwork4('2001::/64') is None


def test_str_to_ipnetwork6():
    assert isinstance(str_to_ipnetwork_any('2001::/64'), IPv6Network)
    assert isinstance(str_to_ipnetwork6('2001::/64'), IPv6Network)
    assert str_to_ipnetwork6('10.0.0.0/24') is None
    assert isinstance(str_to_ipnetwork_any('2001::/64'), IPv6Network)
    assert isinstance(str_to_ipnetwork6('2001::/64'), IPv6Network)
    assert str_to_ipnetwork6('10.0.0.0/24') is None


def test_str_to_ipaddress_and_ipnetwork():
    assert str_to_ipaddress4('10.0.0.1') in str_to_ipnetwork4('10.0.0.0/30')
    assert str_to_ipaddress4('10.0.0.128') not in str_to_ipnetwork4('10.0.0.0/25')
    assert str_to_ipaddress4('10.0.0.1') in str_to_ipnetwork4('10.0.0.0/30')
    assert str_to_ipaddress4('10.0.1.1') not in str_to_ipnetwork4('10.0.0.0/30')
    assert str_to_ipaddress_any('10.0.0.1') in str_to_ipnetwork_any('10.0.0.0/30')
    assert str_to_ipaddress_any('10.0.0.128') not in str_to_ipnetwork_any('10.0.0.0/25')
    assert str_to_ipaddress_any('10.0.0.1') in str_to_ipnetwork_any('10.0.0.0/30')
    assert str_to_ipaddress_any('10.0.1.1') not in str_to_ipnetwork_any('10.0.0.0/30')
    assert str_to_ipaddress6('2001::1') in str_to_ipnetwork6('2001::/127')
    assert str_to_ipaddress6('2001::5') not in str_to_ipnetwork6('2001::/127')


def test_iterate_ports():
    assert list(iterate_ports("5")) == [5]
    assert list(iterate_ports("1,5")) == [1, 5]
    assert list(iterate_ports("1,5, 3")) == [1, 5, 3]
    assert list(iterate_ports("1,5, 3,11-13")) == [1, 5, 3, 11, 12, 13]
    assert list(iterate_ports("1,44-46,5, 3,11-13")) == [1, 44, 45, 46, 5, 3, 11, 12, 13]


def test_uniq_ports():
    assert sorted(uniq_ports([1, 2, 33, 44, 2])) == [1, 2, 33, 44]
    assert sorted(uniq_ports(iterate_ports("1,3-7,5, 3,11-13"))) == [1, 3, 4, 5, 6, 7, 11, 12, 13]


def test_port_list_to_ports_str():
    assert port_list_to_ports_str([1, 2, 100]) == "1,2,100"
    assert port_list_to_ports_str(sorted(uniq_ports([1, 2, 33, 44, 2]))) == "1,2,33,44"
    assert port_list_to_ports_str(sorted(uniq_ports(iterate_ports("1,3-7,5, 3,11-13")))) == "1,3,4,5,6,7,11,12,13"
