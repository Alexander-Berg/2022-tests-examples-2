# -*- coding: utf-8 -*-
import itertools
from unittest import TestCase

from nose_parameterized import parameterized
from passport.backend.core.types.mail_subscriptions import UnsubscriptionList


class TestUnsubscriptionList(TestCase):
    @parameterized.expand([('',), (None,)])
    def test_create__default__empty(self, val):
        instance = UnsubscriptionList(val)
        self.assertFalse(instance.all)
        self.assertEqual(instance.values, set())

    def test_create__list__ok(self):
        instance = UnsubscriptionList('1,2,3')
        self.assertFalse(instance.all)
        self.assertEqual(instance.values, {1, 2, 3})

    def test_create__all__ok(self):
        instance = UnsubscriptionList('all')
        self.assertTrue(instance.all)
        self.assertIsNone(instance.values)

    @parameterized.expand([('invalid',), ('f,2,3',), (True,)])
    def test_create__invalid__exception(self, value):
        with self.assertRaises(ValueError):
            UnsubscriptionList(value)

    @parameterized.expand(itertools.product(
        ['all', '', '1,2,3'],
        [
            (set(), False, set(), False),
            ({1, 2}, False, {1, 2}, False),
            (None, True, None, True),
            (set(), True, None, True),
            ({1, 2}, True, None, True),
        ],
    ))
    def test_set(self, init_value, parameters):
        values, all_state, expected_values, expected_all_state = parameters
        instance = UnsubscriptionList(init_value)
        instance.set(values=values, all_=all_state)
        self.assertEqual(instance.values, expected_values)
        self.assertEqual(instance.all, expected_all_state)

    @parameterized.expand(itertools.product(
        ['all', '', '1,2,3'],
        [
            ({}, set(), False),
            ({1: False, 2: True, 3: False, 4: True}, {1, 3}, False),
            ({1: False, 2: False}, None, True),
        ],
    ))
    def test_set_by_dict(self, init_value, parameters):
        data, expected_values, expected_all_state = parameters
        instance = UnsubscriptionList(init_value)
        instance.set_by_dict(data)
        self.assertEqual(instance.values, expected_values)
        self.assertEqual(instance.all, expected_all_state)

    @parameterized.expand([('all',), ('',), ('1,2,3',)])
    def test_str(self, value):
        self.assertEqual(str(UnsubscriptionList(value)), value)

    @parameterized.expand([
        (UnsubscriptionList(''), UnsubscriptionList('')),
        (UnsubscriptionList('all'), UnsubscriptionList('all')),
        (UnsubscriptionList('1,2,3'), UnsubscriptionList('1,2,3')),
        (UnsubscriptionList('1,2,3'), UnsubscriptionList('3,2,1')),
    ])
    def test_equality__equal(self, instance1, instance2):
        self.assertEqual(instance1, instance2)

    @parameterized.expand([
        (UnsubscriptionList(''), UnsubscriptionList('all')),
        (UnsubscriptionList(''), UnsubscriptionList('1,2,3')),
        (UnsubscriptionList('1,2,3'), UnsubscriptionList('1,2,3,4')),
        (UnsubscriptionList('1,2,3'), UnsubscriptionList('all')),
        (UnsubscriptionList('1,2,3'), UnsubscriptionList('')),
        (UnsubscriptionList('all'), UnsubscriptionList('')),
        (UnsubscriptionList('all'), UnsubscriptionList('1,2,3')),
        (UnsubscriptionList('all'), 'all'),
    ])
    def test_equality__not_equal(self, instance1, instance2):
        self.assertNotEqual(instance1, instance2)

    @parameterized.expand([
        (UnsubscriptionList('1,2,3'), 1),
        (UnsubscriptionList('1,2,3'), 2),
        (UnsubscriptionList('1,2,3'), 3),
        (UnsubscriptionList('all'), 0),
        (UnsubscriptionList('all'), 1),
    ])
    def test_contains__in(self, instance, expected_in):
        self.assertIn(expected_in, instance)

    @parameterized.expand([
        (UnsubscriptionList(''), 0),
        (UnsubscriptionList(''), 1),
        (UnsubscriptionList('1,2,3'), 4),
    ])
    def test_contains__not_in(self, instance, expected_in):
        self.assertNotIn(expected_in, instance)

    @parameterized.expand([
        (UnsubscriptionList(''), False),
        (UnsubscriptionList('1,2,3'), True),
        (UnsubscriptionList('all'), True),
    ])
    def test_bool(self, instance, expected):
        self.assertIs(bool(instance), expected)
