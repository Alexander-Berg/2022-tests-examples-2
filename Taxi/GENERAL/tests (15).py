from __future__ import print_function

from collections import namedtuple
import sys

import numpy as np


DEFAULT_MAX_ELEMENTS_COUNT = 100000000


class SimulatedDistributionTest(object):
    def __init__(
            self, calc_function, iters_count,
            max_elements_count=DEFAULT_MAX_ELEMENTS_COUNT,
            random_state=42, verbose=False, return_distribution=False
    ):
        self.calc_function = calc_function
        self.iters_count = iters_count
        self.max_elements_count = max_elements_count
        self.random_state = random_state
        self.verbose = verbose
        self.return_distribution = return_distribution

    def get_diff(self, fst, snd):
        raise NotImplementedError()

    @staticmethod
    def get_result_from_stats(diff, distribution):
        raise NotImplementedError()

    def get_result_from_data(self, fst, snd):
        return self.get_result_from_stats(
            diff=self.get_diff(fst, snd),
            distribution=self.get_distribution(fst, snd)
        )

    def _iter_calculation(self, fst, snd, gen, iter_size):
        raise NotImplementedError()

    def get_distribution(self, fst, snd):
        gen = np.random.RandomState(self.random_state)
        max_iter_size = max(1, self.max_elements_count / (len(fst) + len(snd)))
        calculations = []
        for iter_num in xrange(0, self.iters_count, max_iter_size):
            if self.verbose:
                print(iter_num, 'of', self.iters_count, file=sys.stderr)
            iter_size = min(max_iter_size, self.iters_count - iter_num)
            iter_calculation = self._iter_calculation(fst, snd, gen, iter_size)
            if iter_calculation.shape != (iter_size,):
                raise ValueError('calc_function returned invalid shape')
            calculations.extend(iter_calculation)
        return np.array(calculations)


def mean_bootstrap_calculation(fst, snd):
    return fst.mean(axis=1) - snd.mean(axis=1)


def median_bootstrap_calculation(fst, snd):
    return np.median(fst, axis=1) - np.median(snd, axis=1)


def std_bootstrap_calculation(fst, snd):
    return np.std(fst, axis=1) - np.std(snd, axis=1)


BootstrapTestResult = namedtuple(
    'BootstrapTestResult',
    'diff pvalue distribution'
)


class BootstrapTest(SimulatedDistributionTest):
    def __init__(
            self, calc_function=mean_bootstrap_calculation,
            iters_count=100, max_elements_count=DEFAULT_MAX_ELEMENTS_COUNT,
            random_state=42, verbose=False, return_distribution=False
    ):
        super(BootstrapTest, self).__init__(
            calc_function=calc_function, iters_count=iters_count,
            max_elements_count=max_elements_count,
            random_state=random_state, verbose=verbose,
            return_distribution=return_distribution
        )

    def _iter_calculation(self, fst, snd, gen, iter_size):
        return self.calc_function(
            gen.choice(fst, size=(iter_size, len(fst)), replace=True),
            gen.choice(snd, size=(iter_size, len(snd)), replace=True)
        )

    def get_diff(self, fst, snd):
        return self.calc_function(fst[np.newaxis, :], snd[np.newaxis, :])[0]

    def get_result_from_stats(self, diff, distribution):
        neg_fraction = (distribution < 0).mean()
        pvalue = min(neg_fraction, 1. - neg_fraction) * 2.
        if not self.return_distribution:
            distribution = None
        return BootstrapTestResult(diff, pvalue, distribution)


def bootstrap(
        fst, snd, calc_function=mean_bootstrap_calculation,
        iters_count=100, max_elements_count=DEFAULT_MAX_ELEMENTS_COUNT,
        random_state=42, verbose=False
):
    return BootstrapTest(
        calc_function, iters_count,
        max_elements_count, random_state, verbose
    ).get_distribution(fst, snd)


def bootstrap_test(
        test, control, calc_function=mean_bootstrap_calculation,
        iters_count=100, max_elements_count=DEFAULT_MAX_ELEMENTS_COUNT,
        random_state=42, return_distribution=False, verbose=False
):
    return BootstrapTest(
        calc_function, iters_count,
        max_elements_count, random_state, verbose, return_distribution
    ).get_result_from_data(test, control)


def bootstrap_percentiles(
        test, control, percentiles,
        calc_function=mean_bootstrap_calculation,
        iters_count=100, max_elements_count=DEFAULT_MAX_ELEMENTS_COUNT,
        random_state=42, return_distribution=False, verbose=False
):
    distribution = BootstrapTest(
        calc_function, iters_count,
        max_elements_count, random_state, verbose
    ).get_distribution(test, control)
    result = np.percentile(distribution, percentiles)
    if return_distribution:
        return result, distribution
    else:
        return result


def mean_permutation_calculation(fst, snd, mask):
    total_size = len(fst) + len(snd)
    total_sum = np.sum(fst) + np.sum(snd)
    fst_sizes = mask.sum(axis=1)
    fst_sums = (
        (fst * mask[:, :len(fst)]).sum(axis=1)
        + (snd * mask[:, len(fst):]).sum(axis=1)
    )
    return (
        fst_sums / fst_sizes
        - (total_sum - fst_sums) / (total_size - fst_sizes)
    )


def sum_permutation_calculation(fst, snd, mask):
    mask = mask * 2 - 1
    return (
        (fst * mask[:, :len(fst)]).sum(axis=1)
        + (snd * mask[:, len(fst):]).sum(axis=1)
    )


PermutationTestResult = namedtuple(
    'PermutationTestResult',
    'diff pvalue distribution'
)


class PermutationTest(SimulatedDistributionTest):
    def __init__(
            self, calc_function=mean_permutation_calculation,
            iters_count=100, max_elements_count=DEFAULT_MAX_ELEMENTS_COUNT,
            random_state=42, fst_fraction=None, verbose=False,
            return_distribution=False
    ):
        super(PermutationTest, self).__init__(
            calc_function=calc_function, iters_count=iters_count,
            max_elements_count=max_elements_count,
            random_state=random_state, verbose=verbose,
            return_distribution=return_distribution
        )
        self.fst_fraction = fst_fraction

    def _iter_calculation(self, fst, snd, gen, iter_size):
        total_size = len(fst) + len(snd)
        return self.calc_function(
            fst, snd,
            gen.uniform(size=(iter_size, total_size)) <= (
                self.fst_fraction
                if self.fst_fraction else 1. * len(fst) / total_size
            )
        )

    def get_diff(self, fst, snd):
        true_mask = np.zeros(len(fst) + len(snd), dtype=np.bool)
        true_mask[:len(fst)] = True
        return self.calc_function(
            fst, snd,
            true_mask[np.newaxis, :]
        )[0]

    def get_result_from_stats(self, diff, distribution):
        pvalue = (np.abs(distribution) > np.abs(diff)).mean()
        if not self.return_distribution:
            distribution = None
        return PermutationTestResult(diff, pvalue, distribution)


def permutate(
        fst, snd, calc_function=mean_permutation_calculation,
        iters_count=100, max_elements_count=DEFAULT_MAX_ELEMENTS_COUNT,
        random_state=42, fst_fraction=None, verbose=False
):
    return PermutationTest(
        calc_function, iters_count,
        max_elements_count, random_state,
        fst_fraction, verbose
    ).get_distribution(fst, snd)


def permutation_test(
        test, control, calc_function=mean_permutation_calculation,
        iters_count=100, max_elements_count=DEFAULT_MAX_ELEMENTS_COUNT,
        fst_fraction=None, random_state=42, verbose=False,
        return_distribution=False
):
    return PermutationTest(
        calc_function, iters_count,
        max_elements_count, random_state,
        fst_fraction, verbose, return_distribution
    ).get_result_from_data(test, control)
