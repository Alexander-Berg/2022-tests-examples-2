from django.test import TestCase
import unittest
from gap.views import difference_hours, get_type_intersection
from datetime import datetime


class MyFuncTestCase(unittest.TestCase):
    def testBasic(self):
        self.assertEqual(
            difference_hours(
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
            ),
            3,
        )
        self.assertEqual(
            get_type_intersection(
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
            ),
            'exactly',
        )
        self.assertEqual(
            get_type_intersection(
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
                datetime(2020, 5, 1, 15, 0, 00),
                datetime(2020, 5, 1, 16, 00, 00),
            ),
            'not_intersection',
        )
        self.assertEqual(
            get_type_intersection(
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
                datetime(2020, 5, 1, 14, 0, 00),
                datetime(2020, 5, 1, 16, 00, 00),
            ),
            'left',
        )
        self.assertEqual(
            get_type_intersection(
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
                datetime(2020, 5, 1, 10, 0, 00),
                datetime(2020, 5, 1, 13, 00, 00),
            ),
            'right',
        )
        self.assertEqual(
            get_type_intersection(
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
                datetime(2020, 5, 1, 11, 0, 00),
                datetime(2020, 5, 1, 16, 00, 00),
            ),
            'inside',
        )
        self.assertEqual(
            get_type_intersection(
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
                datetime(2020, 5, 1, 12, 30, 00),
                datetime(2020, 5, 1, 13, 00, 00),
            ),
            'outside',
        )
        self.assertEqual(
            get_type_intersection(
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 15, 00, 00),
                datetime(2020, 5, 1, 12, 00, 00),
                datetime(2020, 5, 1, 17, 00, 00),
            ),
            'inside',
        )
