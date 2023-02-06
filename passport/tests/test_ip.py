# -*- coding: utf-8 -*-

import unittest

from netaddr import IPAddress
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.types.ip.ip import IP


class TestIP(unittest.TestCase):
    def test_init_from_string(self):
        ip = IP('127.0.0.1')

        ok_(ip)
        eq_(str(ip), '127.0.0.1')

    def test_init_from_ip(self):
        ip1 = IP('127.0.0.1')
        ip = IP(ip1)

        ok_(ip)
        eq_(str(ip), '127.0.0.1')

    def test_init_from_ip_bytes(self):
        ip1 = IP(b'127.0.0.1')
        ip = IP(ip1)

        ok_(ip)
        eq_(str(ip), '127.0.0.1')

    def test_init_from_empty_string(self):
        ip = IP('')

        ok_(not ip)
        eq_(str(ip), '')
        eq_(ip.normalized, '')
        eq_(ip.truncated, '')
        ok_(not ip.is_loopback)

    def test_init_from_none(self):
        ip = IP(None)

        ok_(not ip)
        eq_(ip.normalized, None)
        eq_(ip.truncated, None)
        ok_(not ip.is_loopback)

    def test_init_from_zero_ip(self):
        ip = IP('0.0.0.0')

        ok_(not ip)
        eq_(ip.normalized, '0.0.0.0')
        eq_(ip.truncated, '0.0.0.0')
        ok_(not ip.is_loopback)

    def test_loopback_ipv6(self):
        ip = IP('::1')
        ok_(ip.is_loopback)

    def test_loopback_ipv4(self):
        ip = IP('127.0.0.1')
        ok_(ip.is_loopback)

    def test_not_loopback_ipv6(self):
        ip = IP('2a02:6b8:b040:1600:225:90ff:feeb:90e8')
        ok_(not ip.is_loopback)

    def test_not_loopback_ipv4(self):
        ip = IP('192.168.0.1')
        ok_(not ip.is_loopback)

    def test_normalized_ipv6(self):
        ip = IP('1111::1111')
        eq_(ip.normalized, '1111::1111')

    def test_truncated_ipv6(self):
        ip = IP('1111::1111')
        eq_(ip.truncated, '0')

    def test_normalized_ipv4(self):
        ip = IP('127.0.0.1')
        eq_(ip.normalized, '127.0.0.1')

    def test_truncated_ipv4(self):
        ip = IP('127.0.0.1')
        eq_(ip.truncated, '127.0.0.1')

    def test_normalized_ipv4_mapped(self):
        ip = IP('::ffff:127.0.0.1')
        eq_(ip.normalized, '127.0.0.1')

    def test_truncated_ipv4_mapped(self):
        ip = IP('::ffff:127.0.0.1')
        eq_(ip.truncated, '127.0.0.1')

    def test_repr(self):
        ip = IP('127.0.0.1')
        ok_(repr(ip))

    def test_eq_ne(self):
        ip1 = IP('127.0.0.1')
        ip2 = IP('127.0.0.1')

        ok_(ip1 == ip2)
        ok_(ip1 == IPAddress('127.0.0.1'))
        ok_(not ip1 == '123')
        ok_(not ip1 == IP('127.0.0.2'))
        ok_(not ip1 != ip2)

    def test_version(self):
        ip1 = IP('127.0.0.1')
        assert ip1.version == 4

        ip2 = IP('2a02:6b8:b040:1600:225:90ff:feeb:90e8')
        assert ip2.version == 6
