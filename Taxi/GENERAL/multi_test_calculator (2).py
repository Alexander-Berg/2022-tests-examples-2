import collections
import itertools
from typing import List, Dict, Optional, Any, NamedTuple, Generator
from six import ensure_binary, ensure_str
from copy import deepcopy

import numpy as np
from nile.api.v1 import Record
from qb2.api.v1 import extractors as qe
from nile.processing.stream import RecordsIterator
from nile.api.v1.stream import Stream

from taxi_pyml.common.hashes import HashWrapper
from taxi.ml.nirvana.common.statistics.objects.aggregator_keys import (
    SimpleAggregatorKey,
    SliceAggregatorKey,
    GroupAggregatorKey,
)
from taxi.ml.nirvana.common.statistics.mr_operations.base_calculator import (
    BaseCalculator,
    METRIC_RESULT_KEY,
)
from taxi.ml.nirvana.common.statistics.mr_operations.aggregator import SumAggregator
from taxi.ml.nirvana.common.statistics.objects.metrics import (
    Feature,
    MetricParams,
    MetricStorage,
)
from taxi.ml.nirvana.common.statistics.local_tests import replace_nan_it, replace_nan
from taxi.ml.nirvana.common.statistics.objects.helpers import iterable_to_bytes
from taxi.ml.nirvana.common.nile.reducers import outer_join_reducer


CALC_VALUES_KEY = '__calc_values'


class MetricCalculatorResult(NamedTuple):
    test_value: Optional[float]
    control_value: Optional[float]
    diff_value: Optional[float]
    relative_diff_percent: Optional[float]
    test_buckets: Optional[List[float]]
    control_buckets: Optional[List[float]]


class MetricCalculator:
    def __init__(self, return_buckets: bool = False):
        self.return_buckets = return_buckets

    def __call__(
            self, test_metric: MetricStorage, control_metric: MetricStorage,
    ) -> MetricCalculatorResult:
        test_value = test_metric.eval(
            [np.sum(val) for val in test_metric.get_values()],
        )
        control_value = control_metric.eval(
            [np.sum(val) for val in control_metric.get_values()],
        )
        diff_value = test_value - control_value
        relative_diff_percent = diff_value / control_value * 100.0
        if self.return_buckets:
            test_buckets = replace_nan_it(
                test_metric.eval(test_metric.get_values()),
            )
            control_buckets = replace_nan_it(
                control_metric.eval(control_metric.get_values()),
            )
        else:
            test_buckets, control_buckets = None, None
        return MetricCalculatorResult(
            test_value=replace_nan(test_value),
            control_value=replace_nan(control_value),
            diff_value=replace_nan(diff_value),
            relative_diff_percent=replace_nan(relative_diff_percent),
            test_buckets=test_buckets,
            control_buckets=control_buckets,
        )


class MultiTestCalculator(BaseCalculator):
    def __init__(
            self,
            stat_tests: Dict[str, Any],
            metrics: List[MetricParams],
            features: List[Feature],
            group_column: str,
            groups: List[SliceAggregatorKey.OuterType],
            group_pairs: List[List[SliceAggregatorKey.OuterType]],
            slices: Optional[List[SliceAggregatorKey]],
            key_column: str,
            metrics_vertically: bool = True,
            hash_salt: Optional[str] = None,
            n_buckets: int = 100,
            return_buckets: bool = False,
            combiner_batch_size: int = 1000,
    ):
        super().__init__(
            stat_tests=deepcopy(stat_tests),
            metrics=metrics,
            features=features,
            slices=slices,
            key_column=key_column,
            hash_salt=hash_salt,
            n_buckets=n_buckets,
        )
        self.metrics_vertically = metrics_vertically
        self.combiner_batch_size = combiner_batch_size
        self.group_column = group_column
        self.stat_tests[CALC_VALUES_KEY] = MetricCalculator(return_buckets)
        self.groups = list(iterable_to_bytes(groups))
        self.group_mapping = collections.defaultdict(set)
        self.hasher = HashWrapper(mod=n_buckets, salt=self.hash_salt)
        if group_pairs is None:
            # `len(self.groups) == 2` expected
            group_pairs = [(self.groups[0], self.groups[1])]
        elif group_pairs == 'all':
            group_pairs = list(itertools.combinations(self.groups, 2))
        elif group_pairs == 'first_vs_rest':
            group_pairs = [(groups[0], x) for x in self.groups[1:]]
        elif isinstance(group_pairs, List):
            pairs = []
            for pair in group_pairs:
                pairs.append(tuple(iterable_to_bytes(pair)))
            group_pairs = pairs
        for group_pair in group_pairs:
            self.group_mapping[group_pair[0]].add((False, group_pair))
            self.group_mapping[group_pair[1]].add((True, group_pair))

        self.bucket_aggregator = SumAggregator(
            feature_names=[feature.name for feature in self.features],
            keys=[
                SimpleAggregatorKey(self.key_column),
                GroupAggregatorKey(
                    self.group_column, list(self.group_mapping.keys()),
                ),
                *self.slices,
            ],
            combiner_batch_size=self.combiner_batch_size,
        )

    @staticmethod
    def _metrics_vertically_mapper(
            records: RecordsIterator,
    ) -> Generator[Record, None, None]:
        for record in records:
            row_dict = record.to_dict()
            metric_result = row_dict.pop(METRIC_RESULT_KEY, dict())
            calc_value_result = metric_result.pop(CALC_VALUES_KEY, dict())
            if not calc_value_result:
                calc_value_result = metric_result.pop(
                    ensure_binary(CALC_VALUES_KEY), dict(),
                )
            yield Record(**row_dict, **metric_result, **calc_value_result)

    @staticmethod
    def _metrics_horizontal_mapper(
            records: RecordsIterator,
    ) -> Generator[Record, None, None]:
        for record in records:
            row_dict = record.to_dict()
            metric_result = row_dict.pop(METRIC_RESULT_KEY, dict())
            calc_value_result = metric_result.pop(CALC_VALUES_KEY, dict())
            if not calc_value_result:
                calc_value_result = metric_result.pop(
                    ensure_binary(CALC_VALUES_KEY), dict(),
                )
            metric_result.update(calc_value_result)
            metric_name = row_dict.pop('metric')
            if isinstance(metric_name, bytes):
                metric_name = ensure_str(metric_name)
            row_dict[metric_name] = metric_result
            yield Record.from_dict(row_dict)

    def __call__(
            self, events: Stream, map_intensity='data', reduce_intensity='cpu',
    ) -> Stream:
        table = self._preprocess(events, map_intensity)
        table = table.project(
            qe.all(),
            qe.custom(
                self.key_column, self.hasher.get_percent, self.key_column,
            ),
        )
        table = self.bucket_aggregator(table, map_intensity)
        table = self._calculate_metrics(table, reduce_intensity)
        if self.metrics_vertically:
            table = table.map(self._metrics_vertically_mapper)
        else:
            table = (
                table.map(self._metrics_horizontal_mapper)
                .groupby('control_group', 'test_group', *self.slice_columns)
                .reduce(outer_join_reducer, intensity=reduce_intensity)
            )

        return table
