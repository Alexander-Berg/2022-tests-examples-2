import numpy as np
from nile.api.v1 import Record

from zoo.utils.statistics.mr.common import defaults

import base


TEST_DIFF_PRECISION = 1e-5
DEFAULT_TEST_ONE_JOB_ITERS_COUNT = 100


class MemoryTest(base.MemoryTest):
    def __init__(
            self,
            name,
            tasks_number,
            iters_count,
            sim_distribution_test,
            extract_test_id,
            extract_key,
            extract_value,
            detect_group,
            value_dtype=np.float64,
            memory_limit=defaults.MEMORY_LIMIT,
            max_group_size=defaults.MAX_GROUP_SIZE
    ):
        super(MemoryTest, self).__init__(
            name=name,
            extract_test_id=extract_test_id,
            extract_key=extract_key,
            extract_value=extract_value,
            detect_group=detect_group,
            value_dtype=value_dtype,
            memory_limit=memory_limit,
            max_group_size=max_group_size
        )

        self.iters_count = iters_count
        self.tasks_number = tasks_number
        self.sim_distribution_test = sim_distribution_test

    def _calc_preparations(self, *args):
        return (
            self.sim_distribution_test.get_diff(*args),
            self.sim_distribution_test.get_distribution(*args)
        )

    def multiply_data(self, records):
        for record in records:
            for task_num in xrange(self.tasks_number):
                yield Record(record, task_num=task_num)

    def _calc_part_data(self, groups):
        seed = self.sim_distribution_test.random_state
        values = self._generate_test_control_pairs(
            groups, is_lazy_arrays=not self.use_test_id
        )
        for group_key, test_control_tuple in values:
            self.sim_distribution_test.random_state = seed + group_key.task_num
            diff, distribution = self._calc_preparations(*test_control_tuple)
            yield Record(
                group_key,
                diff=diff,
                distribution=distribution.astype(self.value_dtype).tobytes()
            )
            self.sim_distribution_test.random_state = seed

    def _calc_test_result(self, groups):
        for group_key, records in groups:
            distribution = []
            final_diff = None
            for record in records:
                if (
                    final_diff is not None
                    and abs(final_diff - record.diff) > TEST_DIFF_PRECISION
                ):
                    raise ValueError('wrong diffs')
                final_diff = record.diff
                arr = np.fromstring(
                    record.distribution,
                    dtype=self.value_dtype
                )
                distribution.extend(arr)
            yield Record(
                group_key,
                **vars(self.sim_distribution_test.get_result_from_stats(
                    final_diff,
                    np.array(distribution[:self.iters_count])
                ))
            )

    def _calc_4_table(self, table):
        return self._to_required_format(table).map(
            self.multiply_data
        ).groupby('test_id', 'task_num').sort('key', 'value').reduce(
            self._calc_part_data,
            memory_limit=self.memory_limit,
            intensity='ultra_cpu'
        ).groupby('test_id').reduce(
            self._calc_test_result,
            memory_limit=self.memory_limit
        )
