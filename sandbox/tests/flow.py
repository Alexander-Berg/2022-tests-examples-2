# -*- coding: utf-8 -*-

import unittest

from sandbox.projects.sandbox_ci.utils import flow


class TestFlow(unittest.TestCase):
    def test_parallel_success(self):
        expected = [0, 1, 2, 3, 4]

        actual = flow.parallel(
            func=lambda index: index,
            tasks=[0, 1, 2, 3, 4],
            threads_count=2,
        )

        self.assertEquals(actual, expected)

    def test_parallel_success_where_threads_count_is_none(self):
        expected = [0, 1, 2, 3, 4]

        actual = flow.parallel(
            func=lambda index: index,
            tasks=[0, 1, 2, 3, 4],
        )

        self.assertEquals(actual, expected)

    def test_parallel_should_throw_error_when_threads_less_than_one(self):
        with self.assertRaises(ValueError):
            flow.parallel(
                func=lambda index: index,
                tasks=[0, 1, 2, 3, 4],
                threads_count=0,
            )

    def test_parallel_should_throw_error_when_one_of_threads_throw_error(self):
        with self.assertRaises(flow.ThreadError) as cm:
            flow.parallel(
                func=lambda index: index / 0,
                tasks=[0, 1],
                threads_count=1,
            )

        self.assertIsInstance(cm.exception.cause, ZeroDivisionError)
