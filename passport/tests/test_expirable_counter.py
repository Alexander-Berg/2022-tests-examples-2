# -*- coding: utf-8 -*-
from time import time
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.types.expirable_counter.expirable_counter import ExpirableCounter
import six


class TestIP(unittest.TestCase):
    def setUp(self):
        self.counter = ExpirableCounter(1, time() + 100)
        self.expired_counter = ExpirableCounter(2, time() - 100)

    def test_parse(self):
        counter = ExpirableCounter.parse('2:200')
        eq_(counter._value, 2)
        eq_(counter._expire_timestamp, 200)

    def test_expired(self):
        ok_(not self.counter.is_expired)
        ok_(self.expired_counter.is_expired)

    def test_value(self):
        eq_(self.counter.value, 1)
        eq_(self.expired_counter.value, 0)

        self.counter.reset()
        eq_(self.counter.value, 0)

    def test_incr(self):
        self.counter.incr(expire_in=300)
        eq_(self.counter.value, 2)
        ok_(not self.counter.is_expired)

        self.expired_counter.incr(expire_in=300)
        eq_(self.expired_counter.value, 1)  # протухшее значение не учитываем
        ok_(not self.expired_counter.is_expired)

    def test_str_unicode(self):
        counter = ExpirableCounter(1, 100)
        eq_(str(counter), '1:100')
        eq_(six.text_type(counter), u'1:100')

    def test_eq(self):
        ok_(self.counter == self.counter)
        ok_(ExpirableCounter(1, 100) == ExpirableCounter(1, 100))
        ok_(self.counter != self.expired_counter)
