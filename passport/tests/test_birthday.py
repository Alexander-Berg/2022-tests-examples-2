# -*- coding: utf-8 -*-

import unittest

from nose.tools import ok_
from passport.backend.core.types.birthday import Birthday


class TestBirthday(unittest.TestCase):

    def test_eq_ne(self):
        b1 = Birthday.parse('2011-11-01')
        b2 = Birthday.parse('2011-11-01')

        ok_(b1 == b2)
        ok_(b1 == '2011-11-01')
        ok_(not b1 == '2012-11-01')
        ok_(not b1 != b2)

    def test_repr(self):
        b = Birthday.parse('2011-11-01')
        ok_(repr(b))

    def test_is_year_set(self):
        ok_(Birthday(year=2000, month=1, day=1).is_year_set)
        ok_(not Birthday(month=1, day=1).is_year_set)

    def test_is_date_full(self):
        ok_(not Birthday(year=2000, month=0, day=1).is_date_full)
        ok_(not Birthday(year=2000, month=1, day=0).is_date_full)
        ok_(not Birthday(year=2000, month=1).is_date_full)
        ok_(not Birthday(month=1, day=1).is_date_full)
        ok_(Birthday(year=2000, month=1, day=1).is_date_full)

    def test_parse_none(self):
        with self.assertRaises(ValueError):
            Birthday.parse(None)
