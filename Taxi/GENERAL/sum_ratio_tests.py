from __future__ import print_function

import sys
import collections

import numpy as np
from scipy.stats import mannwhitneyu, ttest_ind, shapiro, levene
from statsmodels.stats.weightstats import DescrStatsW, CompareMeans


RESULT_FIELDS = [
    'pvalue',
    'test_conf_intervals', 'control_conf_intervals', 'diff_conf_intervals',
    'warning'
]
DISTRIBUTION_FIELDS = [
    'test_distribution', 'control_distribution', 'diff_distribution'
]
ParamTestResult = collections.namedtuple(
    'BaseParamTestResult', RESULT_FIELDS + ['statistic']
)
SumBootstrapTestResult = collections.namedtuple(
    'SumBootstrapTestResult', RESULT_FIELDS
)
SumBootstrapTestResultDistribution = collections.namedtuple(
    'SumBootstrapTestResultDistribution', RESULT_FIELDS + DISTRIBUTION_FIELDS
)
ShapiroWilkTestResult = collections.namedtuple(
    'ShapiroWilkTestResult', ['pvalue_control', 'pvalue_test']
)
LeveneTestResult = collections.namedtuple(
    'LeveneTestResult', ParamTestResult._fields
)

ALPHA = [0.05, 0.01]

ZERO_DENOMINATOR_MSG = 'Zero denominator appeared. Test may be incorrect.'
ABSENT_DENOMINATOR_MSG = (
    'You must pass denominators to calc mean metric value'
)
UNEQUAL_SIZES_MSG = 'Unequal {} num and denom sizes: {} != {}'


class SumRatioTestError(Exception):
    pass


def replace_nan(array):
    return [x if np.isfinite(x) else None for x in array]


class BaseTest(object):
    """
    Interface for statistic test comparing two groups.
    The test will divide `*_numerators` by `*_denominators` elementwise
    and compare test mean and control mean if `normalize=True`.
    The test will compare `test_numerators` sum and `control_numerators` sum
    if `normalize=False`.
    Test will calculate confidence intervals if it is possible by design.
    """
    def __init__(self, normalize=True, alpha=ALPHA):
        """
        :param normalize: bool
        :param alpha: confidence level, float or list of floats
        """
        self.normalize = normalize
        self.alpha = alpha

    def __call__(self, test_numerators, control_numerators,
                 test_denominators=None, control_denominators=None):
        """
        :param test_numerators: float list
        :param control_numerators: float list
        :param test_denominators: optional float list
        :param control_denominators: optional float list
        :return:
        """
        raise NotImplementedError()

# TODO
# ShapiroWilkTest and LeveneTest revealed problems
# in BaseParamTest interface. It need's to be reworked
# while moving to Python 3


class BaseParamTest(BaseTest):
    def _calc_test(self, test, control):
        """
        :param test: numpy array or float list
        :param control: numpy array or float list
        :return: statistic (numpy float), pvalue (numpy float)
        """
        raise NotImplementedError()

    def _calc_conf_intervals(self, test, control):
        """
        :param test: numpy array
        :param control: numpy array
        :return:
        """
        raise NotImplementedError()

    @staticmethod
    def _normalize_values(numerators, denominators):
        if np.any(denominators == 0):
            raise SumRatioTestError(ZERO_DENOMINATOR_MSG)
        return numerators / denominators

    def _preprocess_samples(self, test_numerators, control_numerators,
                            test_denominators=None, control_denominators=None):
        test_values = np.array(test_numerators, dtype=float)
        control_values = np.array(control_numerators, dtype=float)
        if self.normalize:
            if test_denominators is None or control_denominators is None:
                raise SumRatioTestError(ABSENT_DENOMINATOR_MSG)
            test_values = self._normalize_values(
                test_values, np.array(test_denominators, dtype=float)
            )
            control_values = self._normalize_values(
                control_values, np.array(control_denominators, dtype=float)
            )
        return test_values, control_values

    @staticmethod
    def _replace_nan(value):
        if value is not None and not np.isfinite(value):
            return None
        return value

    def __call__(self, test_numerators, control_numerators,
                 test_denominators=None, control_denominators=None):
        test_values, control_values = self._preprocess_samples(
            test_numerators, control_numerators,
            test_denominators, control_denominators
        )
        statistic, pvalue = self._calc_test(test_values, control_values)
        statistic = self._replace_nan(statistic)
        pvalue = self._replace_nan(pvalue)
        test_ints, control_ints, diff_ints = self._calc_conf_intervals(
            test_values, control_values
        )
        return ParamTestResult(
            pvalue, test_ints, control_ints, diff_ints, None, statistic
        )


class ShapiroWilkTest(BaseParamTest):
    name = 'ShapiroWilkTest'

    def __init__(self, normalize=True):
        super(ShapiroWilkTest, self).__init__(normalize)

    def __call__(self, test_numerators, control_numerators,
                 test_denominators=None, control_denominators=None):
        test_values, control_values = self._preprocess_samples(
            test_numerators, control_numerators,
            test_denominators, control_denominators
        )
        try:
            _, test_pvalue = shapiro(test_values)
            _, control_pvalue = shapiro(control_values)
        except ValueError as e:
            raise SumRatioTestError(str(e))
        test_pvalue = self._replace_nan(test_pvalue)
        control_pvalue = self._replace_nan(control_pvalue)
        return ShapiroWilkTestResult(control_pvalue, test_pvalue)


class LeveneTest(BaseParamTest):
    name = 'LeveneTest'

    def __init__(self, normalize=True, center='median', proportiontocut=0.05):
        super(LeveneTest, self).__init__(normalize)
        self.center = center
        self.proportiontocut = proportiontocut

    def _calc_test(self, test, control):
        try:
            return levene(
                test, control, center=self.center,
                proportiontocut=self.proportiontocut
            )
        except ValueError as e:
            raise SumRatioTestError(str(e))

    def _calc_conf_intervals(self, test, control):
        return None, None, None


class MannWhitneyUTest(BaseParamTest):
    name = 'MannWhitneyUTest'

    def __init__(self, normalize=True, use_continuity=True,
                 alternative='two-sided'):
        super(MannWhitneyUTest, self).__init__(normalize=normalize)
        self.use_continuity = use_continuity
        self.alternative = alternative

    def _calc_test(self, test, control):
        try:
            return mannwhitneyu(
                test, control,
                use_continuity=self.use_continuity, alternative=self.alternative
            )
        except ValueError as e:
            raise SumRatioTestError(str(e))

    def _calc_conf_intervals(self, test, control):
        return None, None, None


class TTest(BaseParamTest):
    name = 'TTest'

    def __init__(self, normalize=True, equal_var=False, alpha=ALPHA):
        super(TTest, self).__init__(normalize, alpha)
        self.equal_var = equal_var
        self.usevar = 'pooled' if self.equal_var else 'unequal'

    def _calc_test(self, test, control):
        try:
            return ttest_ind(test, control, equal_var=self.equal_var)
        except ValueError as e:
            raise SumRatioTestError(str(e))

    def _conf_intervals_from_stats(
            self, test_stats, control_stats, diff_stats, alpha
    ):
        test_interval = replace_nan(test_stats.tconfint_mean(alpha))
        control_interval = replace_nan(control_stats.tconfint_mean(alpha))
        diff_interval = replace_nan(
            diff_stats.tconfint_diff(alpha, usevar=self.usevar)
        )
        return test_interval, control_interval, diff_interval

    def _calc_conf_intervals(self, test, control):
        test_stats = DescrStatsW(test)
        control_stats = DescrStatsW(control)
        diff_stats = CompareMeans(test_stats, control_stats)

        if hasattr(self.alpha, '__iter__'):
            test_intervals = []
            control_intervals = []
            diff_intervals = []
            for alpha in self.alpha:
                test_conf_int, control_conf_int, diff_conf_int = (
                    self._conf_intervals_from_stats(
                        test_stats, control_stats, diff_stats, alpha
                    )
                )
                test_intervals.append(
                    {'alpha': alpha, 'interval': test_conf_int})
                control_intervals.append(
                    {'alpha': alpha, 'interval': control_conf_int})
                diff_intervals.append(
                    {'alpha': alpha, 'interval': diff_conf_int})
            return test_intervals, control_intervals, diff_intervals
        return self._conf_intervals_from_stats(
            test_stats, control_stats, diff_stats, self.alpha
        )


class SumBootstrapTest(BaseTest):
    def __init__(
            self,
            normalize=True,
            alpha=ALPHA,
            iters_count=100,
            max_elements_count=100000000,
            random_state=42,
            verbose=False,
            return_distribution=False
    ):
        """
        :param normalize: flag to calculate mean or sum, bool
        :param alpha: confidence level, float or list of floats
        :param iters_count: number of bootstrap iterations, int
        :param max_elements_count: int
        :param random_state: int
        :param verbose: bool
        :param return_distribution: return simulated test, control
        and diff distributions, bool
        """
        super(SumBootstrapTest, self).__init__(normalize, alpha)
        self.iters_count = iters_count
        self.max_elements_count = max_elements_count
        self.random_state = random_state
        self.verbose = verbose
        self.return_distribution = return_distribution

    def _calc_bootstrapped_values(self, indices, numerators,
                                  denominators=None):
        """
        :param indices: np.array
        :param numerators: np.array
        :param denominators: np.array
        :return: np.array
        """
        size = numerators.shape[0]
        shape = (indices.shape[0] / size, size)
        values = numerators[indices].reshape(shape).sum(axis=1).astype(float)
        if self.normalize:
            denoms = denominators[indices].reshape(shape).sum(axis=1)
            mask = denoms != 0
            values = np.divide(values, denoms, where=mask)
            values[np.logical_not(mask)] = np.nan
        return values

    @staticmethod
    def _calc_pvalue(distribution):
        nan_mask = np.isnan(distribution)
        less_array = np.less(distribution, 0, where=np.logical_not(nan_mask))
        less_array[nan_mask] = False
        neg_fraction = ((distribution == 0).mean() / 2. + nan_mask.mean() / 2.
                        + less_array.mean())
        return min(neg_fraction, 1. - neg_fraction) * 2.

    @staticmethod
    def _calc_percentiles(distribution, alpha):
        return replace_nan(np.percentile(
            distribution, [alpha * 50., 100 - alpha * 50.]
        ))

    def _calc_conf_intervals(self, distribution):
        if distribution is None:
            distribution = np.nan
        if hasattr(self.alpha, '__iter__'):
            return [
                {
                    'alpha': alpha_val,
                    'interval': self._calc_percentiles(distribution, alpha_val)
                }
                for alpha_val in self.alpha
            ]
        return self._calc_percentiles(distribution, self.alpha)

    def __call__(
            self,
            test_numerators, control_numerators,
            test_denominators=None, control_denominators=None
    ):
        """
        :param test_numerators: np.array
        :param control_numerators: np.array
        :param test_denominators: np.array or None
        :param control_denominators: np.array or None
        :return:
        SumBootstrapTestResultBasic or SumBootstrapTestResultDistribution
        """
        if self.normalize:
            if test_denominators is None:
                test_denominators = np.ones_like(test_numerators)
            if control_denominators is None:
                control_denominators = np.ones_like(control_numerators)
            if len(test_numerators) != len(test_denominators):
                raise SumRatioTestError(
                    UNEQUAL_SIZES_MSG.format(
                        'test', len(test_numerators), len(test_denominators)
                    )
                )
            if len(control_numerators) != len(control_denominators):
                raise SumRatioTestError(
                    UNEQUAL_SIZES_MSG.format(
                        'control',
                        len(control_numerators),
                        len(control_denominators)
                    )
                )
        test_len = len(test_numerators)
        control_len = len(control_numerators)
        gen = np.random.RandomState(self.random_state)
        max_iter_size = max(
            1, self.max_elements_count / (test_len + control_len)
        )
        test_distribution, control_distribution = [], []
        for iter_num in xrange(0, self.iters_count, max_iter_size):
            if self.verbose:
                print(iter_num, 'of', self.iters_count, file=sys.stderr)
            iter_size = min(max_iter_size, self.iters_count - iter_num)
            test_distribution.extend(self._calc_bootstrapped_values(
                gen.choice(
                    test_len, size=iter_size * test_len, replace=True
                ),
                test_numerators,
                test_denominators
            ))
            control_distribution.extend(self._calc_bootstrapped_values(
                gen.choice(
                    control_len, size=iter_size * control_len, replace=True
                ),
                control_numerators,
                control_denominators
            ))
        test_distribution = np.array(test_distribution)
        control_distribution = np.array(control_distribution)
        diff_distribution = test_distribution - control_distribution
        pvalue = self._calc_pvalue(diff_distribution)
        test_intervals = self._calc_conf_intervals(test_distribution)
        control_intervals = self._calc_conf_intervals(control_distribution)
        diff_intervals = self._calc_conf_intervals(diff_distribution)
        warning = None
        if np.any(test_denominators == 0) or np.any(control_denominators == 0):
            warning = ZERO_DENOMINATOR_MSG
        if self.return_distribution:
            return SumBootstrapTestResultDistribution(
                pvalue, test_intervals, control_intervals, diff_intervals,
                warning, test_distribution, control_distribution,
                diff_distribution
            )
        return SumBootstrapTestResult(
            pvalue, test_intervals, control_intervals, diff_intervals, warning
        )
