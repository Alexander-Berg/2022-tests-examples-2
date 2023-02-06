from __future__ import print_function

import sys
import traceback
import copy
import itertools
import hashlib

import numpy as np
from nile.api.v1 import Record
from nile.api.v1 import aggregators as na
from nile.api.v1 import extractors as ne
from nile.api.v1 import filters as nf
from qb2.api.v1 import extractors as qe
from qb2.api.v1 import filters as qf

from zoo.utils.nile_helpers import mappers as zm

from zoo.utils.statistics.mr.common.base_test import BaseTest
from zoo.utils.statistics.local.sum_ratio_tests import TTest, SumRatioTestError


EMPTY_BUCKET_WARNING = 'Empty bucket appeared. Test may be incorrect'


def convert(values):
    return np.nan_to_num(np.array(values, dtype=float))


class Test(BaseTest):
    def __init__(
            self,
            name,
            eval_metric_function=None,
            extract_test_id=None,
            detect_group=None,
            extract_key=None,
            default_value=None,
            calculate_test=None,
            buckets_number=100,
            bucket_hash_salt=''
    ):
        """
        :param name: string
        :param eval_metric_function:
        evaluates statistics for each bucket and group
        eval_metric_function(table, *group_fields)
        table - raw table with events
        group_fields - fields to group by (bucket_num, test_id, group, ...)
        :param extract_test_id: field or nile extractor
        :param detect_group: field or nile extractor
        :param extract_key: field or nile extractor
        :param calculate_test: statistical test
        :param buckets_number: int
        :param bucket_hash_salt: string or int
        """
        if extract_key is None:
            extract_key = qe.row_index('key')
            print(
                'extract_key is None so all events are independent. '
                'Do you really need BucketTest? '
                'The result may be not reproducible.',
                file=sys.stderr
            )
        super(Test, self).__init__(
            name=name,
            extract_test_id=extract_test_id,
            extract_key=extract_key,
            extract_value=None,
            detect_group=detect_group
        )
        self.default_value = default_value
        self.calculate_test = calculate_test
        self.eval_metric_function = eval_metric_function
        self.buckets_number = buckets_number
        self.hash_salt = bucket_hash_salt

    @staticmethod
    def _get_hash(string):
        return int(hashlib.md5(string).hexdigest(), 16)

    def _get_bucket_number(self, key, test_id):
        return self._get_hash('{}_{}_{}'.format(
            key, self._get_hash(str(test_id)), self.hash_salt
        )) % self.buckets_number

    def _calc_4_table(self, table):
        bucketed_data = table.project(
            ne.all(),
            group=self.detect_group,
            _key=self.extract_key,
            test_id=self.extract_test_id
        ).filter(
            nf.custom(self.group_validation, 'group')
        ).project(
            ne.all('_key'),
            bucket_num=ne.custom(
                self._get_bucket_number, '_key', 'test_id'
            ).add_hints(type=int)
        )
        return self.eval_metric_function(
            bucketed_data, 'test_id', 'group', 'bucket_num'
        ).groupby('test_id').sort('bucket_num').reduce(self._calc_result)

    def _calc_metrics(self, test_values, control_values):
        raise NotImplementedError()

    def _calc_result(self, groups):
        for group_key, records in groups:
            test_values = [None] * self.buckets_number
            control_values = [None] * self.buckets_number
            for record in records:
                if record.group:
                    test_values[record.bucket_num] = record.value
                else:
                    control_values[record.bucket_num] = record.value
            try:
                bucket_warning = None
                for i in xrange(self.buckets_number):
                    if test_values[i] is None:
                        test_values[i] = copy.deepcopy(self.default_value)
                        bucket_warning = EMPTY_BUCKET_WARNING
                    if control_values[i] is None:
                        control_values[i] = copy.deepcopy(self.default_value)
                        bucket_warning = EMPTY_BUCKET_WARNING
                output = self._calc_metrics(test_values, control_values)
                if bucket_warning:
                    output['warning'] = bucket_warning
                for name, calc_test in self.calculate_test.iteritems():
                    try:
                        output[name] = dict(vars(
                            calc_test(test_values, control_values)
                        ))
                    except SumRatioTestError as e:
                        output[name] = {'error': repr(e)}
                yield Record(group_key, **output)
            except Exception as e:
                yield Record(
                    group_key,
                    exception=repr(e),
                    traceback=traceback.format_exc()
                )


class SumRatioTest(Test):
    COUNT_FIELDS = ['count_numerator', 'count_denominator', 'count_ratio']
    FIELDS = ['numerator', 'denominator']
    FIELDS.extend(COUNT_FIELDS)
    DEFAULT_VALUE = [0] * len(FIELDS)

    def __init__(
            self,
            name,
            extract_test_id=None,
            extract_numerator=None,
            extract_denominator=None,
            detect_group=None,
            extract_key=None,
            calculate_test=None,
            buckets_number=100,
            bucket_hash_salt='',
            combiner_batch_size=None,
            return_buckets=False
    ):
        """
        :param name: string
        :param extract_test_id: field or nile extractor
        :param extract_numerator: field or nile extractor
        :param extract_denominator: field or nile extractor
        :param detect_group: field or nile extractor
        :param extract_key: field or nile extractor
        :param calculate_test: statistical test,
        calculate_test(test_nums, control_nums, test_denoms, control_denoms)
        test_metric = sum(test_nums) / sum(test_denoms)
        control_metric = sum(control_nums) / sum(control_denoms)
        :param buckets_number: int
        :param bucket_hash_salt: string or int
        :param combiner_batch_size: None (without combiner) or int
        :param return_buckets: To return metric values in buckets
        """
        if calculate_test is None:
            calculate_test = {'ttest': TTest(normalize=True, equal_var=False)}
        if not isinstance(calculate_test, dict):
            calculate_test = {'test': calculate_test}
        calculate_test = {
            k: self._sum_ratio_test_decorator(v)
            for k, v in calculate_test.iteritems()
        }
        super(SumRatioTest, self).__init__(
            name=name,
            eval_metric_function=self.eval_metric_function,
            extract_test_id=extract_test_id,
            detect_group=detect_group,
            extract_key=extract_key,
            default_value=SumRatioTest.DEFAULT_VALUE,
            calculate_test=calculate_test,
            buckets_number=buckets_number,
            bucket_hash_salt=bucket_hash_salt
        )
        if extract_numerator is None:
            extract_numerator = 'value'
        if extract_denominator is None:
            extract_denominator = qe.expression(
                'denominator', qf.defined('numerator')
            )
        self.count_numerator = qe.expression(
            'count_numerator', qf.defined('numerator')
        )
        self.count_denominator = qe.expression(
            'count_denominator', qf.defined('denominator')
        )
        self.count_ratio = qe.expression(
            'count_ratio', qf.defined('numerator', 'denominator')
        )
        self.extract_numerator = extract_numerator
        self.extract_denominator = extract_denominator
        self.combiner_batch_size = combiner_batch_size
        self.use_combiner = combiner_batch_size is not None
        self.return_buckets = return_buckets

    def eval_metric_function(self, table, *group_fields):
        table = table.project(
            ne.all(), numerator=self.extract_numerator
        ).project(
            ne.all(), denominator=self.extract_denominator
        ).project(
            ne.all(),
            count_numerator=self.count_numerator,
            count_denominator=self.count_denominator,
            count_ratio=self.count_ratio
        )
        if self.use_combiner:
            table = table.map(zm.create_sum_combiner(
                key_fields=group_fields,
                value_fields=SumRatioTest.FIELDS,
                max_stored_keys=self.combiner_batch_size,
                default_values=SumRatioTest.DEFAULT_VALUE
            ))
        return table.groupby(*group_fields).aggregate(
            **{f: na.sum(f) for f in SumRatioTest.FIELDS}
        ).project(
            ne.all(exclude=SumRatioTest.FIELDS),
            qe.list_('value', *SumRatioTest.FIELDS).allow_null_dependency()
        )

    @staticmethod
    def _sum_ratio_test_decorator(calculate_test):
        def calculate(test, control):
            test_nums, test_denoms = convert(test).T[:2]
            control_nums, control_denoms = convert(control).T[:2]
            return calculate_test(test_nums, control_nums,
                                  test_denoms, control_denoms)

        return calculate

    def _calc_metrics(self, test_values, control_values):
        result = {}
        for name, values in zip(['test', 'control'],
                                [test_values, control_values]):
            if self.return_buckets:
                num, denom = np.array(values, dtype=float)[:, :2].T
                # float('inf') is possible here, can be written on YT
                distribution = [
                    x if not np.isnan(x) else None for x in (num / denom).tolist()
                ]
                result['{}_buckets'.format(name)] = distribution
            sums = convert(values).sum(0)
            result['{}_value'.format(name)] = (
                    sums[0] / float(sums[1]) if sums[1] != 0 else None
            )
            result.update({
                '{}_counts'.format(name): dict(
                    itertools.izip(SumRatioTest.COUNT_FIELDS, sums[2:])
                )
            })
        if (result['test_value'] is not None and
                result['control_value'] is not None):
            result['diff_value'] = (
                    result['test_value'] - result['control_value']
            )
            if result['control_value'] != 0:
                result['relative_diff_percent'] = (
                        result['diff_value'] / result['control_value'] * 100.
                )
        return result


class MeanTest(SumRatioTest):
    def __init__(
            self,
            name,
            extract_test_id=None,
            extract_value=None,
            detect_group=None,
            extract_key=None,
            calculate_test=None,
            buckets_number=100,
            bucket_hash_salt='',
            combiner_batch_size=None
    ):
        """
        :param name: string
        :param extract_test_id: field or nile extractor
        :param extract_value: field or nile extractor
        :param detect_group: field or nile extractor
        :param extract_key: field or nile extractor
        :param calculate_test: statistical test,
        calculate_test(test, control)
        test_metric = mean(test)
        control_metric = mean(control)
        :param buckets_number: int
        :param bucket_hash_salt: string or int
        :param combiner_batch_size: None (without combiner) or int
        """
        if calculate_test is None:
            calculate_test = {'ttest': TTest(normalize=True)}
        else:
            if not isinstance(calculate_test, dict):
                calculate_test = {'test': calculate_test}
            calculate_test = {
                k: self._mean_test_decorator(v)
                for k, v in calculate_test.iteritems()
            }
        super(MeanTest, self).__init__(
            name=name,
            extract_test_id=extract_test_id,
            extract_numerator=extract_value,
            extract_denominator=None,
            detect_group=detect_group,
            extract_key=extract_key,
            calculate_test=calculate_test,
            buckets_number=buckets_number,
            bucket_hash_salt=bucket_hash_salt,
            combiner_batch_size=combiner_batch_size
        )

    @staticmethod
    def _mean_test_decorator(calculate_test):
        def normalize(nums, denoms):
            mask = denoms > 0
            return nums[mask] * 1. / denoms[mask]

        def calculate(test_nums, control_nums, test_denoms, control_denoms):
            return calculate_test(normalize(test_nums, test_denoms),
                                  normalize(control_nums, control_denoms))

        return calculate
