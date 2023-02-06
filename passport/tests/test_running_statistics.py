import unittest

import numpy as np
from passport.backend.library.yalearn.structures.running_statistics import RunningStatistics
from scipy.stats import describe


class TestIntervalCounters(unittest.TestCase):
    def test_append(self):
        running_stats = RunningStatistics()
        arr = [1, 2, 3, 4, 5]
        running_stats.append(arr)
        self.assertEqual(running_stats.mean(), np.mean(arr))
        self.assertEqual(running_stats.var(), np.var(arr, ddof=1))
        self.assertEqual(running_stats.std(), np.std(arr, ddof=1))
        self.assertEqual(running_stats.max(), np.max(arr))
        self.assertEqual(running_stats.min(), np.min(arr))
        self.assertEqual(running_stats.size(), len(arr))
        self.assertEqual(running_stats.skewness(), describe(arr).skewness)
        self.assertEqual(running_stats.kurtosis(), describe(arr).kurtosis)
        running_stats.clear()
        running_stats.push(1)
        self.assertTrue(np.isnan(running_stats.std()))
