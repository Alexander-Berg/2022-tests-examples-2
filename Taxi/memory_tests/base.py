import numpy as np

from zoo.utils.statistics.mr.common.base_test import BaseTest


class MemoryTest(BaseTest):
    def __init__(
            self,
            name,
            extract_test_id,
            extract_key,
            extract_value,
            detect_group,
            value_dtype,
            memory_limit,
            max_group_size
    ):
        super(MemoryTest, self).__init__(
            name=name,
            extract_test_id=extract_test_id,
            extract_key=extract_key,
            extract_value=extract_value,
            detect_group=detect_group,
        )
        self.value_dtype = value_dtype
        self.memory_limit = memory_limit
        self.max_stored_group_size = max_group_size

    def _get_test_control_arrays(self, records):
        control = np.zeros(self.max_stored_group_size, dtype=self.value_dtype)
        test = np.zeros(self.max_stored_group_size, dtype=self.value_dtype)
        if self.use_key:
            control_keys = np.zeros(self.max_stored_group_size, dtype=int)
            test_keys = np.zeros(self.max_stored_group_size, dtype=int)
            last_control_key, last_test_key = None, None
            last_control_key_num, last_test_key_num = -1, -1
        control_index, test_index = 0, 0

        for record in records:
            if max(test_index, control_index) >= self.max_stored_group_size:
                raise ValueError(
                    'max group size exceeded: {}'.format(
                        max(test_index, control_index)
                    )
                )
            if record.group:
                test[test_index] = record.value
                if self.use_key:
                    if last_test_key != record.key:
                        last_test_key = record.key
                        last_test_key_num += 1
                    test_keys[test_index] = last_test_key_num
                test_index += 1
            else:
                control[control_index] = record.value
                if self.use_key:
                    if last_control_key != record.key:
                        last_control_key = record.key
                        last_control_key_num += 1
                    control_keys[control_index] = last_control_key_num
                control_index += 1

        if self.use_key:
            return (
                test[:test_index], test_keys[:test_index],
                control[:control_index], control_keys[:control_index]
            )
        else:
            return test[:test_index], control[:control_index]

    def _generate_test_control_pairs(self, groups, is_lazy_arrays=False):
        result = None
        for group_key, records in groups:
            if not is_lazy_arrays or result is None:
                result = self._get_test_control_arrays(records)
            yield group_key, result

    def _calc_4_table(self, table):
        raise NotImplementedError()
