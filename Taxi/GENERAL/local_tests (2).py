from typing import Iterable, Union, List, NamedTuple, Optional
import sys

from scipy.stats import ttest_ind, mannwhitneyu, shapiro, levene
import numpy as np
from statsmodels.stats.weightstats import DescrStatsW, CompareMeans

from projects.common.statistics.objects.metrics import MetricStorage


CONFIDENCE_LEVELS = (0.05, 0.01)
INFINITE_VALUE_MSG = 'Infinite value appeared.'
EMPTY_BUCKET_WARNING = 'Empty bucket appeared. Test may be incorrect'


class TestError(Exception):
    pass


def replace_nan(value: float):
    if value is not None and np.isfinite(value):
        return value
    return None


def replace_nan_it(values: Iterable[float]):
    return [replace_nan(x) for x in values]


class TTestResult(NamedTuple):
    statistic: Optional[float]
    pvalue: Optional[float]
    test_conf_intervals: List[Optional[float]]
    control_conf_intervals: List[Optional[float]]
    diff_conf_intervals: List[Optional[float]]


class MannWhitneyUTestResult(NamedTuple):
    statistic: Optional[float]
    pvalue: Optional[float]


class ShapiroWilkTestResult(NamedTuple):
    pvalue_control: Optional[float]
    pvalue_test: Optional[float]


class LeveneTestResult(NamedTuple):
    statistic: Optional[float]
    pvalue: Optional[float]


class SumBootstrapTestResult(NamedTuple):
    pvalue: Optional[float]
    test_conf_intervals: List[Optional[float]]
    control_conf_intervals: List[Optional[float]]
    diff_conf_intervals: List[Optional[float]]
    test_distribution: Optional[List[float]] = None
    control_distribution: Optional[List[float]] = None
    diff_distribution: Optional[List[float]] = None
    warning: Optional[str] = None


class TTest:
    def __init__(
            self,
            equal_var: bool = False,
            confidence_level: Union[float, List[float]] = CONFIDENCE_LEVELS,
    ):
        self.equal_var = equal_var
        self.usevar = 'pooled' if self.equal_var else 'unequal'
        self.confidence_level = confidence_level

    def _conf_intervals_from_stats(
            self, test_stats, control_stats, diff_stats, alpha,
    ):
        test_interval = replace_nan_it(test_stats.tconfint_mean(alpha))
        control_interval = replace_nan_it(control_stats.tconfint_mean(alpha))
        diff_interval = replace_nan_it(
            diff_stats.tconfint_diff(alpha, usevar=self.usevar),
        )
        return test_interval, control_interval, diff_interval

    def _calc_conf_intervals(self, test, control):
        test_stats = DescrStatsW(test)
        control_stats = DescrStatsW(control)
        diff_stats = CompareMeans(test_stats, control_stats)

        if isinstance(self.confidence_level, Iterable):
            test_intervals = []
            control_intervals = []
            diff_intervals = []
            for alpha in self.confidence_level:
                test_conf_int, control_conf_int, diff_conf_int = (
                    self._conf_intervals_from_stats(
                        test_stats, control_stats, diff_stats, alpha,
                    )
                )
                test_intervals.append(
                    {'alpha': alpha, 'interval': test_conf_int},
                )
                control_intervals.append(
                    {'alpha': alpha, 'interval': control_conf_int},
                )
                diff_intervals.append(
                    {'alpha': alpha, 'interval': diff_conf_int},
                )
            return test_intervals, control_intervals, diff_intervals
        return self._conf_intervals_from_stats(
            test_stats, control_stats, diff_stats, self.confidence_level,
        )

    def __call__(
            self, test_metric: MetricStorage, control_metric: MetricStorage,
    ) -> TTestResult:
        test_values = test_metric.eval_values()
        control_values = control_metric.eval_values()

        try:
            statistic, pvalue = ttest_ind(
                test_values, control_values, equal_var=self.equal_var,
            )
            test_ints, control_ints, diff_ints = self._calc_conf_intervals(
                test_values, control_values,
            )
        except ValueError as e:
            raise TestError(str(e))

        return TTestResult(
            statistic=replace_nan(statistic),
            pvalue=replace_nan(pvalue),
            test_conf_intervals=test_ints,
            control_conf_intervals=control_ints,
            diff_conf_intervals=diff_ints,
        )


class MannWhitneyUTest:
    def __init__(
            self, use_continuity: bool = True, alternative: str = 'two-sided',
    ):
        self.use_continuity = use_continuity
        self.alternative = alternative

    def __call__(
            self, test_metric: MetricStorage, control_metric: MetricStorage,
    ) -> MannWhitneyUTestResult:
        for metric in [test_metric, control_metric]:
            if not np.all(np.isfinite(metric.eval_values())):
                raise TestError(INFINITE_VALUE_MSG)
        try:
            statistic, pvalue = mannwhitneyu(
                test_metric.eval_values(),
                control_metric.eval_values(),
                use_continuity=self.use_continuity,
                alternative=self.alternative,
            )
        except ValueError as e:
            raise TestError(str(e))

        return MannWhitneyUTestResult(
            statistic=replace_nan(statistic), pvalue=replace_nan(pvalue),
        )


class ShapiroWilkTest:
    def __call__(
            self, test_metric: MetricStorage, control_metric: MetricStorage,
    ) -> ShapiroWilkTestResult:
        try:
            _, test_pvalue = shapiro(test_metric.eval_values())
            _, control_pvalue = shapiro(control_metric.eval_values())
        except ValueError as e:
            raise TestError(str(e))
        return ShapiroWilkTestResult(
            pvalue_control=replace_nan(control_pvalue),
            pvalue_test=replace_nan(test_pvalue),
        )


class LeveneTest:
    def __init__(self, center='median', proportiontocut=0.05):
        self.center = center
        self.proportiontocut = proportiontocut

    def __call__(
            self, test_metric: MetricStorage, control_metric: MetricStorage,
    ) -> LeveneTestResult:
        try:
            statistic, pvalue = levene(
                test_metric.eval_values(),
                control_metric.eval_values(),
                center=self.center,
                proportiontocut=self.proportiontocut,
            )
        except ValueError as e:
            raise TestError(str(e))

        return LeveneTestResult(
            statistic=replace_nan(statistic), pvalue=replace_nan(pvalue),
        )


class SumBootstrapTest:
    def __init__(
            self,
            confidence_levels=CONFIDENCE_LEVELS,
            iters_count=100,
            max_elements_count=100000000,
            random_state=42,
            verbose=False,
            return_distribution=False,
    ):
        """
        :param confidence_levels: confidence level, float or list of floats
        :param iters_count: number of bootstrap iterations, int
        :param max_elements_count: int
        :param random_state: int
        :param verbose: bool
        :param return_distribution: return simulated test, control
        and diff distributions, bool
        """
        self.confidence_levels = confidence_levels
        self.iters_count = iters_count
        self.max_elements_count = max_elements_count
        self.random_state = random_state
        self.verbose = verbose
        self.return_distribution = return_distribution

    @staticmethod
    def _calc_pvalue(distribution):
        nan_mask = np.isnan(distribution)
        less_array = np.less(distribution, 0, where=np.logical_not(nan_mask))
        less_array[nan_mask] = False
        neg_fraction = (
            (distribution == 0).mean() / 2.0
            + nan_mask.mean() / 2.0
            + less_array.mean()
        )
        return min(neg_fraction, 1.0 - neg_fraction) * 2.0

    @staticmethod
    def _calc_percentiles(distribution, alpha):
        return replace_nan_it(
            np.percentile(distribution, [alpha * 50.0, 100 - alpha * 50.0]),
        )

    def _calc_conf_intervals(self, distribution):
        if distribution is None:
            distribution = np.nan
        if isinstance(self.confidence_levels, Iterable):
            return [
                {
                    'alpha': threshold,
                    'interval': self._calc_percentiles(
                        distribution, threshold,
                    ),
                }
                for threshold in self.confidence_levels
            ]
        return self._calc_percentiles(distribution, self.confidence_levels)

    @staticmethod
    def gen_sample(heights, width, metric, generator):
        for value in metric.get_values(
                generator.choice(width, size=heights * width, replace=True),
        ):
            yield value.reshape((heights, width)).sum(1).astype(float)

    def __call__(
            self, test_metric: MetricStorage, control_metric: MetricStorage,
    ) -> SumBootstrapTestResult:
        warning = None
        for metric in [test_metric, control_metric]:
            if not np.all(np.isfinite(metric.eval_values())):
                warning = EMPTY_BUCKET_WARNING
        gen = np.random.RandomState(self.random_state)
        test_size = test_metric.get_size()
        control_size = control_metric.get_size()

        max_iter_size = max(
            1, int(self.max_elements_count / (test_size + control_size)),
        )
        test_distribution, control_distribution = [], []
        for iter_num in range(0, self.iters_count, max_iter_size):
            if self.verbose:
                print(iter_num, 'of', self.iters_count, file=sys.stderr)
            iter_size = min(max_iter_size, self.iters_count - iter_num)
            test_distribution.extend(
                test_metric.eval(
                    list(
                        self.gen_sample(
                            iter_size, test_size, test_metric, gen,
                        ),
                    ),
                ),
            )
            control_distribution.extend(
                control_metric.eval(
                    list(
                        self.gen_sample(
                            iter_size, control_size, control_metric, gen,
                        ),
                    ),
                ),
            )

        test_distribution = np.array(test_distribution)
        control_distribution = np.array(control_distribution)
        diff_distribution = test_distribution - control_distribution
        pvalue = self._calc_pvalue(diff_distribution)
        test_intervals = self._calc_conf_intervals(test_distribution)
        control_intervals = self._calc_conf_intervals(control_distribution)
        diff_intervals = self._calc_conf_intervals(diff_distribution)
        result = SumBootstrapTestResult(
            pvalue=pvalue,
            test_conf_intervals=test_intervals,
            control_conf_intervals=control_intervals,
            diff_conf_intervals=diff_intervals,
            warning=warning,
        )
        if self.return_distribution:
            result._replace(
                test_distribution=replace_nan_it(test_distribution),
                control_distribution=replace_nan_it(control_distribution),
                diff_distribution=replace_nan_it(diff_distribution),
            )
        return result
