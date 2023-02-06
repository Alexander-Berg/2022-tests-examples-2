# coding: utf-8
from unittest import TestCase
from connection.zendesk import ZendeskDataIncrement
from dmp_suite import datetime_utils as dtu


class DataIncrementTest(TestCase):
    def test_extracts_data_correctly(self):
        first_page = {'records': ['A', 'B'], 'count': 2, 'end_time': 456}
        second_page = {'records': ['C', 'D', 'E'], 'count': 3, 'end_time': 789}
        increment = ZendeskDataIncrement(
            [first_page, second_page], 123, entity_key='records'
        )

        self.assertRaises(RuntimeError, getattr, increment, 'last_load_date')
        self.assertEqual([next(increment), next(increment)], ['A', 'B'])
        self.assertRaises(RuntimeError, getattr, increment, 'last_load_date')
        self.assertEqual(list(increment), ['C', 'D', 'E'])
        self.assertEqual(increment.last_load_date, dtu.timestamp2dttm(789))

    def test_handles_empty_response_correctly(self):
        empty_page = {'records': [], 'count': 0, 'end_time': None}
        increment = ZendeskDataIncrement(
            [empty_page], 123, entity_key='records'
        )

        self.assertEqual(list(increment), [])
        self.assertEqual(increment.last_load_date, dtu.timestamp2dttm(123))

    def test_handles_empty_last_page_correctly(self):
        first_page = {'records': ['A', 'B'], 'count': 2, 'end_time': 456}
        empty_page = {'records': [], 'count': 0, 'end_time': None}
        increment = ZendeskDataIncrement(
            [first_page, empty_page], 123, entity_key='records'
        )

        self.assertEqual(list(increment), ['A', 'B'])
        self.assertEqual(increment.last_load_date, dtu.timestamp2dttm(456))
