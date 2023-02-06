# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import date

from nose_parameterized import parameterized
from passport.backend.social.common.db.schemas import sub_table
from passport.backend.social.common.db.types import _SparseDate
from passport.backend.social.common.db.utils import database_query_to_str
from passport.backend.social.common.test.test_case import TestCase
from sqlalchemy import sql


class TestSparseDate(TestCase):
    @parameterized.expand(
        [
            (0, 0, 0, '0000-00-00'),
            (1, 0, 0, '0001-00-00'),
            (1931, 0, 0, '1931-00-00'),
            (0, 3, 12, '0000-03-12'),
            (1931, 3, 12, '1931-03-12'),
        ],
    )
    def test_dates(self, year, month, day, formatted):
        value = _SparseDate(year, month, day)
        self.assertEqual((value.year, value.month, value.day), (year, month, day))
        self.assertEqual(str(value), formatted)
        self.assertEqual(repr(value), 'datetime.date(%s, %s, %s)' % (year, month, day))
        self.assertEqual(_SparseDate.from_string(formatted), value)

    def test_equality(self):
        value = _SparseDate(0, 0, 0)
        self.assertEqual(value, value)
        self.assertEqual(value, _SparseDate(0, 0, 0))
        self.assertNotEqual(value, _SparseDate(0, 0, 1))
        self.assertNotEqual(value, _SparseDate(0, 1, 0))
        self.assertNotEqual(value, _SparseDate(1, 0, 0))
        self.assertNotEqual(value, _SparseDate(1, 1, 1))
        self.assertNotEqual(value, date(1, 1, 1))

        self.assertEqual(_SparseDate(1, 1, 1), date(1, 1, 1))

    def test_uncomparable(self):
        self.assertFalse(_SparseDate(0, 0, 0) == 1)

    def test_from_string__invalid_format(self):
        with self.assertRaises(ValueError):
            _SparseDate.from_string('0000-00')

        with self.assertRaises(ValueError):
            _SparseDate.from_string('0000')

        with self.assertRaises(ValueError):
            _SparseDate.from_string('00-00-00-00')

        with self.assertRaises(ValueError):
            _SparseDate.from_string('')

        with self.assertRaises(ValueError):
            _SparseDate.from_string(None)

        with self.assertRaises(ValueError):
            _SparseDate.from_string('000a-00-00')


class TestDatabaseQueryToStr(TestCase):
    def test(self):
        engine = self._fake_db.get_engine()
        query = (
            sub_table
            .select()
            .where(
                sql.and_(
                    sub_table.c.sid == 5,
                    sub_table.c.value.in_(['foo', 'бар']),
                ),
            )
        )
        self.assertEqual(
            database_query_to_str(query, engine=engine),
            r"SELECT subscription.profile_id, subscription.sid, subscription.value \n"
            r"FROM subscription \n"
            r"WHERE subscription.sid = 5 AND subscription.value IN ('foo', 'бар')",
        )
