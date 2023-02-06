# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.utils.crc import (
    bit_count,
    bytes_to_long,
    crc5_epc,
    crc12,
    long_to_bytes,
)
from passport.backend.utils.common import bytes_to_hex
import six


class TestUtils(unittest.TestCase):
    def test_bit_count(self):
        eq_(bit_count(0), 0)
        eq_(bit_count(1), 1)
        eq_(bit_count(2), 2)
        eq_(bit_count(255), 8)

    def test_bytes_to_long(self):
        for from_, to_ in (
            ('00', 0),
            ('FFFF', 65535),
            ('FFFFFFFF', 4294967295),
            ('AAFF00', 11206400),
            ('010000000000000000', 16 ** 16),
        ):
            bytes_ = bytes.fromhex(from_) if six.PY3 else from_.decode('hex')
            eq_(bytes_to_long(bytes_), to_)

    def test_long_to_bytes(self):
        for from_, to_ in (
            (0, '00'),
            (65535, 'ffff'),
            (4294967295, 'ffffffff'),
            (16 ** 16, '010000000000000000'),
        ):
            bytes_ = long_to_bytes(from_)
            hex_ = bytes_to_hex(bytes_)
            eq_(hex_, to_)

    @raises(ValueError)
    def test_long_to_bytes_negative_error(self):
        long_to_bytes(-1)


class TestCrc(unittest.TestCase):
    def test_crc5_epc(self):
        eq_(crc5_epc(0), 0)
        eq_(crc5_epc(0b101001), 0)
        eq_(crc5_epc(0b101010), 3)

    def test_crc12(self):
        eq_(crc12(0), 0)
        eq_(crc12(0b1100011110011), 0)
        eq_(crc12(0b1100011110000), 3)
