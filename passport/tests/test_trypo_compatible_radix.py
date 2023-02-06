# -*- coding: utf-8 -*-
from unittest import TestCase

from netaddr import IPAddress
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.grants.trypo_compatible_radix import (
    extract_project_id,
    is_trypo_network,
    TRYPOCompatibleRadix,
)


class TestUtils(TestCase):
    def test_is_trypo_network(self):
        for good in (
            '123@2a02:6b8:0::/40',
            '1@2a02:6b8:0::/80'
            'abcdef01@2a02:6b8:0::/24'
        ):
            ok_(is_trypo_network(good), '%s should be TRYPO' % good)
        for bad in (
            '2a02:6b8:0::/40',
            '2a02:6b8:c00::1',
            '192.168.0.1/8',
            '192.168.0.1',
        ):
            ok_(not is_trypo_network(bad), '%s should not be TRYPO' % bad)

    def test_extract_project_id(self):
        for ip, expected_project_id in (
            ('::1', '0'),
            ('2a02:6b8:c0c:f80:0:1329::1', '1329'),
            ('2a02:6b8:c0c:f80:dead:beef::1', 'deadbeef'),
        ):
            eq_(extract_project_id(IPAddress(ip)), expected_project_id)


class TestTRYPOCompatibleRadix(TestCase):
    def setUp(self):
        super(TestTRYPOCompatibleRadix, self).setUp()
        self.radix = TRYPOCompatibleRadix()

    def test_single_ips_v4(self):
        ok_(self.radix.search_best('127.0.0.1') is None)
        self.radix.add('127.0.0.1')
        eq_(self.radix.search_best('127.0.0.1').prefix, '127.0.0.1/32')

    def test_single_ips_v6(self):
        ok_(self.radix.search_best('2a02:6b8::1') is None)
        self.radix.add('2a02:6b8::1')
        eq_(self.radix.search_best('2a02:6b8::1').prefix, '2a02:6b8::1/128')

    def test_classic_networks_v4(self):
        ok_(self.radix.search_best('127.0.0.1') is None)
        self.radix.add('127.0.0.0/31')
        eq_(self.radix.search_best('127.0.0.1').prefix, '127.0.0.0/31')

    def test_classic_networks_v6(self):
        ok_(self.radix.search_best('2a02:6b8::1') is None)
        self.radix.add('2a02:6b8::/127')
        eq_(self.radix.search_best('2a02:6b8::1').prefix, '2a02:6b8::/127')

    def test_trypo_networks(self):
        ok_(self.radix.search_best('2a02:6b8:c0c:f80:0:1329::1') is None)
        self.radix.add('1329@2a02:6b8:c00::/40')
        eq_(self.radix.search_best('2a02:6b8:c0c:f80:0:1329::1').prefix, '2a02:6b8:c00::/40')
        ok_(self.radix.search_best('2a02:6b8:c0c:f80:0:1328::1') is None)

    def test_mixed(self):
        self.radix.add('1329@2a02:6b8:c00::/40')
        self.radix.add('2a02:6b8:c0c::/43')
        self.radix.add('2a02:6b8:c0c:f80:0:1328::/96')
        self.radix.add('2a02:6b8:c00::1')
        self.radix.add('127.0.0.0/28')
        self.radix.add('127.0.0.1')

        eq_(self.radix.search_best('127.0.0.1').prefix, '127.0.0.1/32')
        eq_(self.radix.search_best('127.0.0.2').prefix, '127.0.0.0/28')
        eq_(self.radix.search_best('2a02:6b8:c00::1').prefix, '2a02:6b8:c00::1/128')
        eq_(self.radix.search_best('2a02:6b8:c0c:f80:0:1328::1').prefix, '2a02:6b8:c0c:f80:0:1328::/96')
        eq_(self.radix.search_best('2a02:6b8:c0c:f80:0:1329::1').prefix, '2a02:6b8:c00::/40')
