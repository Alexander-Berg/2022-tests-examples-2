# -*- coding: utf-8 -*-

import unittest

from sandbox.projects.sandbox_ci.utils import list_utils


class TestList(unittest.TestCase):
    def test_none(self):
        expected = []

        actual = list_utils.flatten(None)

        self.assertListEqual(actual, expected)

    def test_non_list(self):
        expected = [1]

        actual = list_utils.flatten(1)

        self.assertListEqual(actual, expected)

    def test_list(self):
        expected = [1]

        actual = list_utils.flatten([1])

        self.assertListEqual(actual, expected)

    def test_nested_list(self):
        expected = [1, 2, 3, 4, 5, 6]

        actual = list_utils.flatten([1, [2], [3, [4], 5], 6])

        self.assertListEqual(actual, expected)

    def test_nested_list_with_none(self):
        expected = [1, 2, 3, 4, None, 5, None, 6]

        actual = list_utils.flatten([1, [2], [3, [4, None], 5], None, 6])

        self.assertListEqual(actual, expected)
