from __future__ import print_function

import collections
import itertools
import json

from nile.api.v1 import Record

from zoo.utils.nile_helpers import reducers as zr
from zoo.utils.statistics.mr.cluster_tests.bucket_test import SumRatioTest
from zoo.utils.statistics.local import sum_ratio_tests


def get_default_sum_ratio_mr_test(
        name='sum_ratio_bucket_test',
        buckets_number=100,
        combiner_batch_size=1000,
        bootstrap_iters_count=1000
):
    return SumRatioTest(
        name=name,
        extract_test_id='test_id',
        extract_key='key',
        detect_group='group',
        extract_numerator='numerator',
        extract_denominator='denominator',
        buckets_number=buckets_number,
        combiner_batch_size=combiner_batch_size,
        calculate_test={
            'SumBootstrapTest': sum_ratio_tests.SumBootstrapTest(
                normalize=True, iters_count=bootstrap_iters_count
            ),
            'TTest': sum_ratio_tests.TTest(
                normalize=True, equal_var=False
            ),
            'MannWhitneyuUTest': sum_ratio_tests.MannWhitneyUTest(
                normalize=True,
                use_continuity=True, alternative='two-sided'
            )
        }
    )


class ExperimentParamsValidationError(Exception):
    pass


class MultiTestValidator(object):
    def __init__(self, simulation_mode=False):
        self.simulation_mode = simulation_mode

    @staticmethod
    def __validate_metric(metrics):
        NUM = 'num'
        AGG = 'aggregation'
        DEN = 'denom'
        MEAN = 'mean'
        RATIO = 'ratio'
        if not isinstance(metrics, dict):
            raise ExperimentParamsValidationError(
                'metrics param must be dictionary'
            )
        if not metrics:
            raise ExperimentParamsValidationError(
                'Metrics dictionary must contain at least one'
            )
        for metric, value in metrics.iteritems():
            if not isinstance(metric, str):
                raise ExperimentParamsValidationError(
                    '"{}": metric name must be string'
                )
            for x in [NUM, AGG]:
                if value.get(x) is None:
                    raise ExperimentParamsValidationError(
                        '"{}" metric must contain "{}"'.format(metric, x)
                    )
            for key in value:
                if key not in {NUM, AGG, DEN}:
                    raise ExperimentParamsValidationError(
                        'Unknown key "{}" in metric "{}"'.format(key, metric)
                    )
            if value.get(AGG) not in {MEAN, RATIO}:
                raise ExperimentParamsValidationError(
                    '"{}" aggregation type must be "{}" or "{}"'.format(
                        metric, MEAN, RATIO
                    )
                )
            if not isinstance(value.get(NUM), str):
                raise ExperimentParamsValidationError(
                    '"{}" numerator value must be string'.format(metric)
                )
            if (value.get(AGG) == RATIO and not
                        isinstance(value.get(DEN), str)):
                    raise ExperimentParamsValidationError(
                        'You must define "{}" column in "{}" '
                        'if aggregation type is "ratio"'.format(DEN, metric)
                    )
            if value.get(AGG) == MEAN and value.get(DEN) is not None:
                    raise ExperimentParamsValidationError(
                        '"{}" aggregation type is "{}". '
                        'You don`t need the "{}"'.format(metric, MEAN, DEN)
                    )

    @staticmethod
    def __validate_groups(groups):
        if not hasattr(groups, '__iter__'):
            raise ExperimentParamsValidationError('groups param must be list')

    @staticmethod
    def __validate_group_pairs(group_pairs, groups):
        if not (group_pairs == 'all' or group_pairs == 'first_vs_rest' or
                isinstance(group_pairs, list) or
                (len(groups) == 2 and group_pairs is None)):
            raise ExperimentParamsValidationError(
                '`group_pairs` param can be "all", '
                '"first_vs_rest" or non empty list of group pairs. '
                '`group_pairs` can be skipped only if `groups` param '
                'contains exactly 2 groups'
            )
        if isinstance(group_pairs, list):
            if not group_pairs:
                raise ExperimentParamsValidationError(
                    '`group_pairs` list must contain at least one group pair'
                )
            for pair in group_pairs:
                if not isinstance(pair, (list, tuple, set)):
                    raise ExperimentParamsValidationError(
                        'group pairs must be list or tuple'
                    )
                if len(pair) != 2:
                    raise ExperimentParamsValidationError(
                        '{}: you can compare only two groups at once'.format(
                            pair)
                    )
                for x in pair:
                    if x not in groups:
                        raise ExperimentParamsValidationError(
                            '"{}" not in "groups" param'.format(x)
                        )

    @staticmethod
    def __validate_slices(slices):
        if slices is not None:
            if not hasattr(slices, '__iter__'):
                raise ExperimentParamsValidationError(
                    '"slices" param must be list or dict'
                )

    def validate_params(self, metrics, groups, group_pairs, slices, key):
        if not isinstance(key, str):
            raise ExperimentParamsValidationError('"key" param must be string')
        self.__validate_metric(metrics)
        self.__validate_slices(slices)
        if not self.simulation_mode:
            self.__validate_groups(groups)
            self.__validate_group_pairs(group_pairs, groups)

    def validate_schema(self, schema, metrics, groups_column, slices, key):
        msg = 'There is no "{}" column in input table'

        columns = {col['name'] for col in schema}
        if key not in columns:
            raise ExperimentParamsValidationError(msg.format(key))
        if not self.simulation_mode and groups_column not in columns:
            raise ExperimentParamsValidationError(msg.format(groups_column))
        if slices is not None:
            for slice_name in slices:
                if slice_name not in columns:
                    raise ExperimentParamsValidationError(msg.format(slice_name))
        for name, metric in metrics.iteritems():
            num = metric.get('num')
            denom = metric.get('denom')
            if num not in columns:
                raise ExperimentParamsValidationError(msg.format(num))
            if denom is not None and denom not in columns:
                raise ExperimentParamsValidationError(msg.format(denom))


class MultiTestCalculator(object):
    validator = MultiTestValidator()

    def __init__(
            self, mr_test, metrics, group_column,
            groups, group_pairs, slices, key,
            unfold_total_slice=True, total_slice='__total__',
            schema=None, metrics_vertically=True
    ):
        """

        :param mr_test: MapReduce test instance
        :param metrics: Dictionary object with metrics description.
        The dictionary keys (str type) are the names of metrics.
        The values are dictionaries too. Each value contains "num" and
        "aggregation" fields and optionally contains "denom" field.
        "aggregation" can be "mean" or "ratio" strings. "num" and "denom"
        are strings with the metric's numerator and denominator column names.
        If "aggregation" is "mean", the metric is mean of "num" column.
        If "ratio", the metric is ratio "num"/"denom". You don't need
        to provide "denom" if "mean".::

            {
                'conversion_order_to_trip': {
                    'num': 'success_order_flg',
                    'aggregation': 'mean'
                },
                'tips_to_order_cost_ratio': {
                    'num': 'order_tips',
                    'aggregation': 'ratio',
                    'denom': 'order_cost'
                }
            }

        :param group_column: The name of the table column with the
        group name, str.
        :param groups: List of the experiment group names. These names
        will be searched for in the "group_column" column. Other groups
        will be ignored.::

            ['control_group', 'experiment_1', 'experiment_2']

        :param group_pairs: The way to combine "groups" into pairs.
        Possible values:
            - "all" string will provide all pairs of groups
            - "first_vs_rest" string will compare
            all groups with the first one
            - list of group pairs for custom combinations::

            [
                ('control_group', 'experiment_1'),
                ('control_group', 'experiment_2')
            ]

        :param slices: Slices description. Possible values:
            - None if no slices
            - List of strings with the slices column names for slices
            with unknown possible values.
            - Dictionary {str: list of str} for slices with
            known possible values. None is possible instead of list
            for slices with unknown possible values.::

            ['attr_countries', 'application_platform']

        or::

            {
                'attr_countries': None,
                'application_platform': ['iphone', 'android']
            }

        :param key: The name of column with the object id, str.
        Used to resolve events dependency.
        :param unfold_total_slice: `True` will add total slice for
        each event, bool.
        :param total_slice: The value representing total slice.
        '__total__' by default. Beware of name collision
        with some existing slice.
        :param schema: input table YT schema
        :param metrics_vertically: All metrics are listed in a column
        if `False` All metrics of each combination of group pair
        and slices values are listed in a row.
        And all metrics will be in one row
        """

        self.validator.validate_params(
            metrics, groups, group_pairs, slices, key
        )
        if schema:
            self.validator.validate_schema(
                schema, metrics, group_column, slices, key
            )
        self.mr_test = mr_test
        self.metrics = metrics
        self.group_column = group_column
        self.groups = [group.encode('utf-8')
                       if isinstance(group, unicode) else group
                       for group in groups]
        self.group_mapping = collections.defaultdict(set)
        if group_pairs is None:
            # `len(self.groups) == 2` expected
            group_pairs = [(self.groups[0], self.groups[1])]
        elif group_pairs == 'all':
            group_pairs = list(itertools.combinations(self.groups, 2))
        elif group_pairs == 'first_vs_rest':
            group_pairs = [(groups[0], x) for x in self.groups[1:]]
        elif isinstance(group_pairs, list):
            pairs = []
            for x, y in group_pairs:
                x = x.encode('utf-8') if isinstance(x, unicode) else x
                y = y.encode('utf-8') if isinstance(y, unicode) else y
                pairs.append((x, y))
            group_pairs = pairs
        for group_pair in group_pairs:
            self.group_mapping[group_pair[0]].add((False, group_pair))
            self.group_mapping[group_pair[1]].add((True, group_pair))

        if slices is None:
            slices = {}
        elif isinstance(slices, list):
            slices = {k: None for k in slices}
        self.slice_keys = collections.OrderedDict(slices)

        self.key = key
        self.unfold_total_slice = unfold_total_slice
        self.total_slice = total_slice
        self.metrics_vertically = metrics_vertically

        self.undefined_slices_list = []
        self.defined_slices_dict = collections.OrderedDict()
        for key, val in self.slice_keys.iteritems():
            if val is None:
                self.undefined_slices_list.append(key)
            else:
                val = [v.encode('utf-8')
                       if isinstance(v, unicode) else v
                       for v in val]
                if self.unfold_total_slice:
                    val.append(self.total_slice)
                self.defined_slices_dict[key] = set(val)
        self.info_to_number = {
            val: i for i, val in enumerate(
                itertools.product(
                    itertools.product(self.metrics.iterkeys(), group_pairs),
                    itertools.product(*self.defined_slices_dict.itervalues())
                )
            )
        }
        self.number_to_info = {
            v: k for k, v in self.info_to_number.iteritems()
        }

    def _keys_generator(self, record):
        value = record.get(self.key)
        if value is not None:
            yield value

    def _measures_generator(self, record):
        for name, params in self.metrics.iteritems():
            num = params.get('num')
            denom = params.get('denom')
            if denom is not None:
                value = [record.get(num), record.get(denom)]
                if value[0] is not None or value[1] is not None:
                    yield name, value
            else:
                if record.get(num) is not None:
                    yield name, [record.get(num), 1]

    def _extend_slice(self, slice_value, possible_values=None):
        if not hasattr(slice_value, '__iter__'):
            slice_value = {slice_value}
        if possible_values is not None:
            result = possible_values.intersection(slice_value)
        else:
            result = set(slice_value)
        if self.unfold_total_slice:
            result.add(self.total_slice)
        return result

    def _slices_generator(self, record):
        slice_list_cells = [
            self._extend_slice(record.get(key))
            for key in self.undefined_slices_list
        ]
        slice_dict_cells = [
            self._extend_slice(record.get(key), val)
            for key, val in self.defined_slices_dict.iteritems()
        ]
        for values in itertools.product(
                itertools.product(*slice_list_cells),
                itertools.product(*slice_dict_cells)
        ):
            yield values

    def _groups_generator(self, record):
        values = record.get(self.group_column)
        if not hasattr(values, '__iter__'):
            values = [values]
        for value in set(values):
            if value in self.group_mapping:
                for flag, pair in self.group_mapping[value]:
                    yield flag, pair

    def _pack_test_id(self, measure_name, group_pair,
                      undefined_slice_values, defined_slice_values):
        number = self.info_to_number.get(
            ((measure_name, group_pair), defined_slice_values)
        )
        if self.undefined_slices_list:
            # There are slice columns without known values set
            test_id = [number]
            test_id.extend(undefined_slice_values)
            test_id = json.dumps(test_id)
        else:
            # All slice columns have known values set
            test_id = number
        return test_id

    def _unpack_test_id(self, test_id):
        if self.undefined_slices_list:
            test_id = json.loads(test_id)
            number = test_id[0]
            undefined_slice_values = test_id[1:]
        else:
            number = test_id
            undefined_slice_values = ()
        ((measure_name, group_pair),
         defined_slice_values) = self.number_to_info.get(number)
        return (measure_name, group_pair, undefined_slice_values,
                defined_slice_values)

    def _flatten_mapper(self, records):
        for record in records:
            keys_list = list(self._keys_generator(record))
            if not keys_list:
                continue
            measures_list = list(self._measures_generator(record))
            if not measures_list:
                continue
            groups_list = list(self._groups_generator(record))
            if not groups_list:
                continue
            for (
                (undefined_slice_values, defined_slice_values),
                key,
                (measure_name, (num, denom)),
                (group_flag, group_pair)
            ) in itertools.product(
                self._slices_generator(record),
                keys_list, measures_list, groups_list
            ):
                yield Record(
                    test_id=self._pack_test_id(
                        measure_name, group_pair,
                        undefined_slice_values, defined_slice_values
                    ),
                    key=key, group=group_flag, numerator=num, denominator=denom
                )

    def _postprocessing_mapper(self, records):
        for record in records:
            (metric_name,
             (control_group, test_group),
             undefined_slice_values,
             defined_slice_values) = self._unpack_test_id(record.test_id)
            test_result = record.to_dict()
            test_result.pop('test_id')
            output = dict()
            output['test_group'] = test_group
            output['control_group'] = control_group
            slices = {}
            slices.update(itertools.izip(self.undefined_slices_list,
                                         undefined_slice_values))
            slices.update(itertools.izip(self.defined_slices_dict,
                                         defined_slice_values))
            output.update(slices)
            if self.metrics_vertically:
                output['metric'] = metric_name
                output.update(test_result)
                if slices:
                    output['slices'] = slices
            else:
                output[metric_name] = test_result
            yield Record(**output)

    def __call__(self, events, intensity='data'):
        """
        :param events: yt-table with columns mentioned in `key` param,
        metrics `num` and `denom`, `group_column`, `slices` keys
        :param intensity: flatten mapper intensity, see
        https://logos.yandex-team.ru/statbox/nile/manual_detailed.html#nile.api.v1.stream.MappableStream
        :return: yt-table with results of experiment
        """
        result = self.mr_test.calc_4_table(
            events.map(self._flatten_mapper, intensity=intensity)
        ).map(self._postprocessing_mapper)
        if self.metrics_vertically:
            return result
        return result.groupby(
            'control_group', 'test_group', *self.slice_keys
        ).reduce(
            zr.outer_join_reducer, intensity='cpu'
        )


def check_unique_keys_hook(ordered_pairs):
    res_dict = {}
    for key, value in ordered_pairs:
        if key in res_dict:
            raise KeyError('{} must be unique name'.format(key))
        if isinstance(value, unicode):
            value = str(value)
        res_dict[str(key)] = value
    return res_dict
