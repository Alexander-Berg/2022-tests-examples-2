# -*- coding: utf-8 -*-

import unittest

import netaddr
from nose.tools import ok_
from passport.backend.core.types.ip.ip import IP
from passport.backend.core.utils.ip_cache import IPAddress


class TestIpCache(unittest.TestCase):
    def test_ip_cache_works(self):
        address_1 = IPAddress('1.1.1.1')
        ok_(address_1 is IPAddress('1.1.1.1'))
        address_2 = IPAddress(IP('2.2.2.2'))
        ok_(address_1 is IPAddress('1.1.1.1'))
        ok_(address_2 is IPAddress('2.2.2.2'))

    def test_ip_cache_skip(self):
        address = netaddr.IPAddress('1.1.1.1')

        ok_(address is IPAddress(address))
