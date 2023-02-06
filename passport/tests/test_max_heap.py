# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.utils.max_heap import MaxHeap
from six import iteritems


class TestMaxHeap(unittest.TestCase):
    def setUp(self):
        self.heap = MaxHeap()

    def test_basic_usage(self):
        ok_(not self.heap)
        elements = {75: 'second', 100: 'first', 50: 'third'}
        for priority, elem in iteritems(elements):
            self.heap.push(priority, elem)
        eq_(len(self.heap), 3)

        expected = [
            (100, 'first'),
            (75, 'second'),
            (50, 'third'),
        ]
        eq_(self.heap.nlargest(), expected)
        eq_(self.heap.nlargest(2), expected[:2])
        eq_(self.heap.nlargest(1), expected[:1])

        for i in range(len(self.heap)):
            eq_(self.heap.pop(), expected[i][1])

        eq_(str(self.heap), '[]')

    def test_merge(self):
        other = MaxHeap()
        elements = {75: 'second', 100: 'first', 50: 'third'}
        for priority, elem in iteritems(elements):
            self.heap.push(priority, elem)

        elements = {12: 'last', 15: 'before_last', 90: 'new_second'}
        for priority, elem in iteritems(elements):
            other.push(priority, elem)

        self.heap.merge(other)
        expected = [
            (100, 'first'),
            (90, 'new_second'),
            (75, 'second'),
            (50, 'third'),
            (15, 'before_last'),
            (12, 'last'),
        ]
        eq_(self.heap.nlargest(), expected)
