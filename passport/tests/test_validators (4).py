# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.validators import (
    CsvSet,
    Int,
    Invalid,
)


class TestCsvSet(TestCase):
    def test_basic(self):
        self.assertEqual(CsvSet().to_python('1,2'), frozenset('12'))
        self.assertEqual(CsvSet().to_python('a, b, c'), frozenset('abc'))
        self.assertEqual(CsvSet().to_python('1,2,1'), frozenset('12'))
        self.assertEqual(CsvSet().to_python('12'), frozenset(['12']))
        self.assertEqual(CsvSet().to_python('   1,2  '), frozenset('12'))
        self.assertEqual(CsvSet().to_python(''), frozenset())
        self.assertEqual(CsvSet.if_missing, frozenset())

    def test_custom_validator(self):
        int_set_validator = CsvSet(value_validator=Int)
        self.assertEqual(int_set_validator.to_python('1,2'), frozenset([1, 2]))

        with self.assertRaises(Invalid) as assertion:
            int_set_validator.to_python('a,2,c')
        self.assertEqual(str(assertion.exception), 'The values a, c are not valid')
