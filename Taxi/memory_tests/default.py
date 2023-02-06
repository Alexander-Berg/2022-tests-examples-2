import traceback
import numpy as np

from nile.api.v1 import Record

from zoo.utils.statistics.mr.common import defaults

import base


class MemoryTest(base.MemoryTest):
    def __init__(
            self,
            name,
            calculate_test,
            extract_test_id=None,
            extract_key=None,
            extract_value=None,
            detect_group=None,
            value_dtype=np.float64,
            memory_limit=defaults.MEMORY_LIMIT,
            max_group_size=defaults.MAX_GROUP_SIZE,
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
        self.calculate_test = calculate_test

    def _calc_test_result(self, groups):
        values = self._generate_test_control_pairs(
            groups, is_lazy_arrays=not self.use_test_id
        )
        for group_key, test_control_tuple in values:
            try:
                yield Record(
                    group_key,
                    **vars(self.calculate_test(*test_control_tuple))
                )
            except Exception as e:
                yield Record(
                    group_key,
                    exception=repr(e),
                    traceback=traceback.format_exc()
                )

    def _calc_4_table(self, table):
        return self._to_required_format(
            table
        ).groupby('test_id').sort('key', 'value').reduce(
            self._calc_test_result,
            memory_limit=self.memory_limit,
            intensity='ultra_cpu'
        )
