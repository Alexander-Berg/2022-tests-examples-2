# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.ydb.declarative.custom_types import FamilyId


class TestFamilyId(PassportTestCase):
    def setUp(self):
        self.column = FamilyId()

    def tearDown(self):
        del self.column

    def test_from_pyval(self):
        self.assertEqual(self.column.from_pyval('f1'), 1)
        self.assertEqual(self.column.from_pyval('1'), 1)
        self.assertEqual(self.column.from_pyval(1), 1)
        with self.assertRaises(ValueError):
            self.column.from_pyval('a1')

    def test_to_pyval(self):
        self.assertEqual(self.column.to_pyval(1), 'f1')
