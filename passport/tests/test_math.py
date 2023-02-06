# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.utils.math import (
    logit,
    sequence_multiply,
    sigmoid,
)


class TestMath(unittest.TestCase):
    def test_sigmoid_and_logit(self):
        for value in (0.01, 0.3, 0.99):
            self.assertAlmostEqual(value, logit(sigmoid(value)), places=5)

    def test_logit_bad_argument(self):
        for value in (-1, 0.0, 1.0, 100):
            with assert_raises(ValueError):
                logit(value)

    def test_sequence_multiply(self):
        eq_(sequence_multiply([1, 2, 3]), 6)
        eq_(sequence_multiply((1, 2, 3, 4)), 24)
        eq_(sequence_multiply({1, 2, 3.0, -4}), -24.0)
        eq_(sequence_multiply({1.0, 0.98, 0.96, 0.02}), 0.018816)
        eq_(sequence_multiply({'m', 2}), 'mm')
        with assert_raises(TypeError):
            sequence_multiply(0)
