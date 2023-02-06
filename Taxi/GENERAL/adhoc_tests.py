from __future__ import print_function

import sys

import numpy as np

from zoo.utils.statistics.local.sum_ratio_tests import BaseSumBootstrapTest
from .tests import BootstrapTestResult

try:
    from taxi_ml_cxx.zoo.utils.statistics import adhoc_tests as adhoc_cpp_tests
except ImportError:
    print(
        'taxi_ml_cxx.zoo.utils.statistics.adhoc_tests is not available.'
        'Build taxi_ml_cxx if you need.',
        file=sys.stderr
    )


class KeyedSumBootstrapTest(object):
    name = 'KeyedSumBootstrapTest'

    def __init__(
            self,
            calc_mean=False,
            iters_count=100,
            max_elements_count=100000000,
            random_state=42,
            verbose=False,
            min_sample_size=0,
            return_distribution=False,
            int_sequence_keys=True
    ):
        self.test = BaseSumBootstrapTest(
            calc_mean=calc_mean,
            iters_count=iters_count,
            max_elements_count=max_elements_count,
            random_state=random_state,
            verbose=verbose,
            return_distribution=return_distribution
        )
        self.min_sample_size = min_sample_size
        self.int_sequence_keys = int_sequence_keys
        if not int_sequence_keys:
            raise NotImplementedError(
                'int_sequence_keys=False is not supported yet'
            )

    def __call__(
            self,
            test, test_keys,
            control, control_keys
    ):
        """
        :param test: np.array
        :param test_keys: np.array
        :param control: np.array
        :param control_keys: np.array
        :return: SumBootstrapTestResult
        """
        if len(control) < self.min_sample_size:
            raise ValueError('Control size is too small: {}<{}'.format(
                len(control), self.min_sample_size
            ))
        if len(test) < self.min_sample_size:
            raise ValueError('Test size is too small: {}<{}'.format(
                len(test), self.min_sample_size
            ))
        test_sums = np.bincount(test_keys, weights=test)
        control_sums = np.bincount(control_keys, weights=control)
        if self.test.calc_mean:
            test_counts = np.bincount(test_keys)
            control_counts = np.bincount(control_keys)
        else:
            test_counts, control_counts = None, None
        return self.test._calculate(
            test_sums, control_sums, test_counts, control_counts
        )


def cpp_bootstrap_test(
        test, control, iters_count=100, random_seed=42,
        n_jobs=1, return_distribution=False, metric='mean'
):
    """
    :param test: np.array for test
    :param control: np.array for control
    :param iters_count: number of iterations in bootstrap
    :param random_seed: seed for random
    :param n_jobs: number of async tasks
    :param return_distribution: flag to return distribution
    :param metric: one of {'sum', 'mean', 'median', 'variance', 'std'}
    :return: BootstrapTestResult
    """
    return BootstrapTestResult(
        **adhoc_cpp_tests.bootstrap_test(
            test=test, control=control, iters_count=iters_count,
            n_jobs=n_jobs, return_distribution=return_distribution,
            metric=metric, random_seed=random_seed
        )
    )
