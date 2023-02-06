from __future__ import absolute_import

import unittest

from passport.backend.library.yalearn.structures.interval_counters import (
    StringIntervalCounters,
    UInt32IntervalCounters,
    UInt64IntervalCounters,
    UInt64PartialIntervalCounters,
)


class TestIntervalCounters(unittest.TestCase):
    def setUp(self):
        self.ic_uint32 = UInt32IntervalCounters()
        self.ic_uint64 = UInt64IntervalCounters()
        self.ic_string = StringIntervalCounters()
        self.pic_uint64 = UInt64PartialIntervalCounters()

    def check_integer(self, ic):
        ic.add(1, 1)
        ic.add(1, 3)
        ic.add(1, 3)
        ic.add(1, 7)
        ic.add(1, 10)

        ic.add(2, 2)
        ic.add(2, 3)
        ic.add(2, 13)
        ic.add(2, 17)

        self.assertEqual(ic.count(1, 2, 8), 3)
        self.assertEqual(ic.count(2, 1, 2), 0)
        self.assertEqual(ic.count(1, 7, 7), 0)
        self.assertEqual(ic.count(1, 7, 8), 1)
        self.assertEqual(ic.count(1, 3, 4), 2)
        self.assertEqual(ic.count(1, 1, 3), 1)

        self.assertEqual(ic.count_before(1, 2), 1)
        self.assertEqual(ic.count_before(2, 12), 2)
        self.assertEqual(ic.count_before(1, 3), 1)
        self.assertEqual(ic.count_before(1, 7), 3)
        self.assertEqual(ic.count_before(1, 1), 0)

        self.assertEqual(ic.count_after(1, 3), 2)
        self.assertEqual(ic.count_after(1, 1), 4)
        self.assertEqual(ic.count_after(1, 10), 0)
        self.assertEqual(ic.count_after(2, 12), 2)
        self.assertEqual(ic.count_after(1, 0), 5)

        self.assertEqual(ic.count(2, 0, 1000), 4)

    def test_partial_interval_counters(self):
        ic = self.pic_uint64
        ic.add(1, 1, 3)
        ic.add(1, 3, 7)
        ic.add(1, 7, 11)
        ic.add(1, 10, 17)

        ic.add(2, 2, 5)
        ic.add(2, 3, 9)
        ic.add(2, 3, 19)
        ic.add(2, 17, 27)

        self.assertEqual(ic.count_before(1, 1), 0)
        self.assertEqual(ic.count_before(1, 7), 10)
        self.assertEqual(ic.count_before(2, 10), 33)
        self.assertEqual(ic.count_before(2, 17), 33)

        self.assertEqual(ic.count_after(1, 1), 35)
        self.assertEqual(ic.count_after(1, 7), 17)
        self.assertEqual(ic.count_after(1, 10), 0)
        self.assertEqual(ic.count_after(1, 0), 38)

        self.assertEqual(ic.count(1, 1, 1), 0)
        self.assertEqual(ic.count(1, 1, 10), 21)
        self.assertEqual(ic.count(2, 100, 200), 0)
        self.assertEqual(ic.count(2, 1, 3), 5)
        self.assertEqual(ic.count(2, 1, 2), 0)
        self.assertEqual(ic.count(1, 1, 100), 38)

    def test_interval_counters(self):
        self.check_integer(self.ic_uint32)
        self.check_integer(self.ic_uint64)

    def test_malfunction(self):
        self.assertRaises(Exception, self.ic_uint32.add, -1, 1)
        self.assertRaises(Exception, self.ic_uint32.add, 2 ** 32, 1)
        self.assertRaises(Exception, self.ic_uint32.add, -1, 1, 1)
        self.assertRaises(Exception, self.ic_uint32.add, 2 ** 64, 1)
