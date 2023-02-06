from __future__ import division, unicode_literals

import fractions

from sandbox.common import math as common_math


class TestMathProgress(object):

    def test__empty_process(self):
        result = common_math.progress(0, 10, 0)
        assert result == 100

    def test__full_progress(self):
        result = common_math.progress(0, 10, 10)
        assert result == 100

    def test__empty_progress(self):
        result = common_math.progress(0, 0, 10)
        assert result == 0

    def test__custom_progress(self):
        result = common_math.progress(0, 42, 100)
        assert result == 42

    def test__fractional_process(self):
        result = common_math.progress(0, fractions.Fraction(1, 3), 1)
        assert result == 33


class TestMathPercentile(object):

    def test__empty_iterable(self):
        result = common_math.percentile([], 1.0)
        assert result is None

    def test__zero_percentile(self):
        result = common_math.percentile([1, 3, 12], 0.0)
        assert result == 1

    def test__full_percentile(self):
        result = common_math.percentile([1, 3, 12], 1.0)
        assert result == 12

    def test__custom_percentile(self):
        result = common_math.percentile([1, 3, 12], 0.5)
        assert result == 3

    def test__round_percentile(self):
        result = common_math.percentile([1, 3, 12], 0.8)
        assert result == 8
