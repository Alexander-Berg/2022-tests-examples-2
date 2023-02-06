from decimal import Decimal

from nile.api.v1 import Record
from nile.api.v1 import aggregators as na
from nile.api.v1 import extractors as ne
from scipy.stats import norm as normal_distribution

from zoo.utils.nile_helpers.operations import add_ranks_2_table
from zoo.utils.nile_helpers import aggregators as za

from zoo.utils.statistics.mr.common.base_test import BaseTest


class Test(BaseTest):

    def __init__(
            self,
            name,
            extract_test_id=None,
            extract_value=None,
            detect_group=None,
            use_continuity=True,
            alternative='two-sided',
            use_long_arithmetic=True,
            value_dtype=float
    ):
        super(Test, self).__init__(
            name=name,
            extract_test_id=extract_test_id,
            extract_key=None,
            extract_value=extract_value,
            detect_group=detect_group
        )

        # TODO fix in future
        if extract_test_id is not None:
            raise NotImplementedError('extract_test_id is not supported in mw')

        if not type(use_continuity) is bool:
            raise ValueError('use_continuity must be bool')
        if alternative not in {'less', 'two-sided', 'greater'}:
            raise ValueError('Invalid alternative: {}'.format(alternative))

        self.use_continuity = use_continuity
        self.alternative = alternative
        self.use_long_arithmetic = use_long_arithmetic
        self.value_dtype = value_dtype

    def _calc_4_table(self, table):
        table = self._to_required_format(table)
        if self.value_dtype is not None:
            table = table.project(
                ne.all('value'),
                value=ne.custom(lambda value: self.value_dtype(value))
            )
        return self._calc_4_ranked_values(add_ranks_2_table(
            table,
            origin_field='value',
            rank_field='raw_rank'
        ))

    def _calc_4_ranked_values(self, ranked_values):
        if self.use_long_arithmetic:
            int_sum_aggr = za.long_sum
            int_store = str
        else:
            int_sum_aggr = za.sum
            int_store = int

        return ranked_values.groupby('value').aggregate(
            values_count=na.count(),
            min_rank=na.min('raw_rank'),
            max_rank=na.max('raw_rank'),
            true_group_count=na.sum('group')
        ).project(
            ne.all(),
            true_group_min_rank_sum=ne.custom(
                lambda min_rank, true_group_count:
                int_store(min_rank * true_group_count)
            ),
            true_group_max_rank_sum=ne.custom(
                lambda max_rank, true_group_count:
                int_store(max_rank * true_group_count)
            )
        ).groupby().aggregate(
            values_count=na.sum('values_count'),
            values_count_cube=int_sum_aggr(
                field='values_count',
                prepare_func=lambda x: int(x) ** 3
            ),
            true_group_size=na.sum('true_group_count'),
            min_rank=int_sum_aggr('true_group_min_rank_sum'),
            max_rank=int_sum_aggr('true_group_max_rank_sum'),
            intensity='data'
        ).project(
            ne.all(exclude=['min_rank', 'max_rank']),
            rank=ne.custom(
                lambda min_rank, max_rank:
                str(Decimal(int(min_rank) + int(max_rank)) / 2)
            )
        ).map(self._calc_result)

    def _calc_result(self, records):
        records = list(records)
        assert len(records) == 1
        record = records[0]

        n = int(record.values_count)
        n1 = int(record.true_group_size)
        n2 = n - n1
        r1 = Decimal(record.rank)

        u1 = n1 * n2 + n1 * (n1 + 1) / 2 - r1
        u2 = n1 * n2 - u1

        m_u = Decimal(n1 * n2 / 2. + 0.5 * self.use_continuity)
        t3_sum = Decimal(record.values_count_cube)
        t_sum = Decimal(record.values_count)
        squared_sigma_u = (n + 1 - (t3_sum - t_sum) / Decimal(
            n * (n - 1))) * n1 * n2 / Decimal(12)

        if self.alternative == 'two-sided':
            u = max(u1, u2)
        elif self.alternative == 'less':
            u = u1
        elif self.alternative == 'greater':
            u = u2
        else:
            assert False

        z = float((u - m_u) / squared_sigma_u.sqrt())
        if self.alternative == 'two-sided':
            pvalue = 2 * normal_distribution.sf(abs(z))
        else:
            pvalue = normal_distribution.sf(z)

        yield Record(statistic=float(u2), pvalue=float(pvalue))
