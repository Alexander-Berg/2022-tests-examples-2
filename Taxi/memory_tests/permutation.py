import numpy as np

from zoo.utils.statistics.mr.common import defaults

from zoo.utils.statistics.local import tests as local_tests

import sim_distribution


class MemoryTest(sim_distribution.MemoryTest):
    def __init__(
            self,
            name,
            extract_test_id=None,
            extract_key=None,
            extract_value=None,
            detect_group=None,
            memory_limit=defaults.MEMORY_LIMIT,
            calc_function=local_tests.mean_permutation_calculation,
            iters_count=100,
            fst_fraction=None,
            max_elements_count=local_tests.DEFAULT_MAX_ELEMENTS_COUNT,
            random_state=42,
            value_dtype=np.float64,
            job_iters=sim_distribution.DEFAULT_TEST_ONE_JOB_ITERS_COUNT,
            verbose=False,
            max_group_size=defaults.MAX_GROUP_SIZE
    ):
        super(MemoryTest, self).__init__(
            name=name,
            tasks_number=(iters_count + job_iters - 1) / job_iters,
            sim_distribution_test=local_tests.PermutationTest(
                calc_function, job_iters,
                max_elements_count, random_state,
                fst_fraction, verbose
            ),
            extract_test_id=extract_test_id,
            extract_key=extract_key,
            extract_value=extract_value,
            detect_group=detect_group,
            value_dtype=value_dtype,
            memory_limit=memory_limit,
            iters_count=iters_count,
            max_group_size=max_group_size
        )
