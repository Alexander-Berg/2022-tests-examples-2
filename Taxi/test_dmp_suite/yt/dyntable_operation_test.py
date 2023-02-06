# coding: utf-8
from unittest import TestCase

from dmp_suite.yt.dyntable_operation.dynamic_table_loaders import (
    GenericDataIncrement,
    DynamicIncrementLoader
)
from dmp_suite.yt.table import YTTable


class DynamicTable(YTTable):
    __dynamic__ = True


class TestGenericDataIncrement(TestCase):
    def test_preserves_data(self):
        increment = GenericDataIncrement(['A', 'B', 'C'], '2018-07-26')

        self.assertEqual(list(increment), ['A', 'B', 'C'])
        self.assertEqual(increment.last_load_date, '2018-07-26')

    def test_immutable_last_load_date(self):
        increment = GenericDataIncrement(['A', 'B', 'C'], '2018-07-26')
        self.assertRaises(
            RuntimeError,
            setattr, increment, 'last_load_date', '2018-07-27'
        )

    def test_checks_argument_types(self):
        self.assertRaises(TypeError, GenericDataIncrement, ['A', 'B', 'C'], None)
        self.assertRaises(TypeError, GenericDataIncrement, object(), '2018-07-26')


class TestDynamicIncrementLoader(TestCase):
    def test_constructor_supports_old_api(self):
        loader = DynamicIncrementLoader(DynamicTable, ['A', 'B', 'C'], '2018-07-26')

        self.assertEquals(list(loader.data), ['A', 'B', 'C'])
        self.assertRaises(TypeError, DynamicIncrementLoader, DynamicTable, [])
