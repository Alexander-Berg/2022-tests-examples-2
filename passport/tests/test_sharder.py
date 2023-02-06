# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    raises,
)
from passport.backend.core.dbmanager.sharder import (
    _Sharder,
    build_mod_shard_function,
    build_range_shard_function,
)


class TestSharder(unittest.TestCase):

    def setUp(self):
        self.buckets_to_db_names = {
            0: 'shard1',
            1: 'shard2',
            2: 'shard3',
            3: 'shard4',
        }

        self.sharder = _Sharder()
        self.sharder.configure(self.buckets_to_db_names)

    def test_key_to_db_name(self):
        eq_(self.sharder.key_to_db_name(0), 'shard1')
        eq_(self.sharder.key_to_db_name(1), 'shard2')
        eq_(self.sharder.key_to_db_name(2), 'shard3')
        eq_(self.sharder.key_to_db_name(3), 'shard4')
        eq_(self.sharder.key_to_db_name(4), 'shard1')

    def test_db_names(self):
        eq_(self.sharder.db_names(), ['shard%d' % i for i in range(1, 5)])

    def test_custom_shard_function(self):
        sharder = _Sharder()
        buckets_count = len(self.buckets_to_db_names)
        sharder.configure(self.buckets_to_db_names,
                          lambda key: 0 if key < 2 else key % buckets_count)

        eq_(sharder.key_to_db_name(0), 'shard1')
        eq_(sharder.key_to_db_name(1), 'shard1')
        eq_(sharder.key_to_db_name(2), 'shard3')
        eq_(sharder.key_to_db_name(3), 'shard4')
        eq_(sharder.key_to_db_name(4), 'shard1')


class TestModShardFunction(unittest.TestCase):
    def test_simple(self):
        shard_function = build_mod_shard_function(3)
        eq_(shard_function(0), 0)
        eq_(shard_function(1), 1)
        eq_(shard_function(2), 2)
        eq_(shard_function(3), 0)
        eq_(shard_function(4), 1)


class TestRangeShardFunction(unittest.TestCase):
    def setUp(self):
        self.shard_function = build_range_shard_function([
            (0, 0),
            (1, 100),
            (2, 200),
            (0, 300),
            (2, 400),
        ])

    def run_with_default_buckets(self, shard_function):
        with assert_raises(ValueError):
            shard_function(-1)
        # Диапазон [0, 100) -- 0
        eq_(shard_function(0), 0)
        eq_(shard_function(50), 0)
        eq_(shard_function(99), 0)
        # Диапазон [100, 200) -- 1
        eq_(shard_function(100), 1)
        eq_(shard_function(150), 1)
        eq_(shard_function(199), 1)
        # Диапазон [200, 300) -- 2
        eq_(shard_function(200), 2)
        eq_(shard_function(250), 2)
        eq_(shard_function(299), 2)
        # Диапазон [300, 400) -- 0
        eq_(shard_function(300), 0)
        eq_(shard_function(350), 0)
        eq_(shard_function(399), 0)
        # Диапазон [400, +oo) -- 2
        eq_(shard_function(400), 2)
        eq_(shard_function(10000), 2)

    def test_simple(self):
        self.run_with_default_buckets(self.shard_function)

    def test_sorting(self):
        shard_function = build_range_shard_function([
            (2, 400),
            (0, 300),
            (2, 200),
            (0, 0),
            (1, 100),
        ])
        self.run_with_default_buckets(shard_function)

    def test_one_range(self):
        shard_function = build_range_shard_function([(0, 0)])
        eq_(shard_function(0), 0)
        eq_(shard_function(1000), 0)

    @raises(ValueError)
    def test_key_is_none(self):
        self.shard_function(None)

    @raises(ValueError)
    def test_key_is_invalid(self):
        self.shard_function(-1)
