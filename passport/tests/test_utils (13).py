# -*- coding: utf-8 -*-
import unittest

from passport.backend.library.historydbloader.historydb import utils


class PackIpShortestTestCase(unittest.TestCase):
    def test_pack_ip_shortest_ipv4_ok(self):
        packed = utils.pack_ip_shortest('3.2.1.1')
        self.assertEqual(packed, b'\x03\x02\x01\x01')

    def test_pack_ip_shortest_ipv6_ok(self):
        packed = utils.pack_ip_shortest('2a00:1450:4012:801::1006')
        self.assertEqual(packed, b'*\x00\x14P@\x12\x08\x01\x00\x00\x00\x00\x00\x00\x10\x06')

    def test_pack_ip_shortest_invalid_ip(self):
        packed = utils.pack_ip_shortest('999.999.999.999')
        self.assertEqual(packed, None)
