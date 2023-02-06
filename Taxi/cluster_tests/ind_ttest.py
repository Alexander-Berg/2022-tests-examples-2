from decimal import Decimal

from nile.api.v1 import Record
from nile.api.v1 import aggregators as na
from scipy.stats import ttest_ind_from_stats

from zoo.utils.nile_helpers.operations import mapper_2_reducer
from zoo.utils.nile_helpers import aggregators as za

from zoo.utils.statistics.mr.common.base_test import BaseTest


class Test(BaseTest):

    def __init__(
            self,
            name,
            extract_test_id=None,
            extract_value=None,
            detect_group=None,
            equal_var=True,
            use_long_arithmetic=False
    ):
        super(Test, self).__init__(
            name=name,
            extract_test_id=extract_test_id,
            extract_key=None,
            extract_value=extract_value,
            detect_group=detect_group
        )
        self.equal_var = equal_var
        self.use_long_arithmetic = use_long_arithmetic

    def _aggregate_stats(self, grouped_table):
        if self.use_long_arithmetic:
            aggr_func = za.decimal_sum
            deserialize_type = Decimal
        else:
            aggr_func = za.sum
            deserialize_type = float
        return grouped_table.aggregate(
            group_size=na.count(),
            values_sum=aggr_func('value'),
            values_sq_sum=aggr_func(
                field='value',
                prepare_func=lambda x: deserialize_type(x) ** 2
            )
        )

    def _calc_4_table(self, table):
        return self._aggregate_stats(
            self._to_required_format(table).groupby('test_id', 'group')
        ).groupby('test_id').reduce(self._calc_result)

    @staticmethod
    def calc_nobs_mean_std(record):
        nobs = record.group_size
        mean = float(
            Decimal(record.values_sum) / Decimal(nobs))
        std = (
            float((Decimal(record.values_sq_sum)
                   / Decimal(nobs) - Decimal(mean) ** 2).sqrt())
        )
        return nobs, mean, std

    def _calc_result(self, groups):
        for group_key, records in groups:
            group_stats_records = list(records)
            if group_stats_records[0].group:
                group_stats_records = group_stats_records[::-1]

            control_stats_record, test_stats_record = group_stats_records
            nobs1, mean1, std1 = self.calc_nobs_mean_std(control_stats_record)
            nobs2, mean2, std2 = self.calc_nobs_mean_std(test_stats_record)

            yield Record(
                group_key,
                diff=mean2 - mean1,
                **vars(ttest_ind_from_stats(
                    mean2, std2, nobs2, mean1, std1, nobs1, self.equal_var
                ))
            )
