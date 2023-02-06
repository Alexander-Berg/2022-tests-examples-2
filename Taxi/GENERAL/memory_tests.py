from functools import partial as func_bind

from nile.api.v1 import extractors as ne
from scipy.stats import mannwhitneyu
from scipy.stats import ttest_ind

from zoo.utils.statistics.mr.memory_tests import MemoryTest
from zoo.utils.statistics.mr.memory_tests import BootstrapMemoryTest
from zoo.utils.statistics.mr.memory_tests import PermutationMemoryTest
from zoo.utils.statistics.mr.common import perform_tests
from zoo.utils.statistics.local.tests import bootstrap_test
from zoo.utils.statistics.local.tests import permutation_test


def _detect_group(group):
    if group == 'postdispatch':
        return True
    if group == 'base':
        return False


detect_group = ne.custom(_detect_group, 'group')
extract_value = 'commission'
cluster_prefix = '//home/taxi_ml/eta_last_pin/experiment_targets/'
input_table_path = cluster_prefix + 'orders_filtered'
output_path = cluster_prefix + 'orders_filtered_cluster_tests'


if __name__ == '__main__':
    perform_tests(
        tests=[
            MemoryTest(
                name='mannwhitneyu',
                calculate_test=func_bind(mannwhitneyu),
                extract_value=extract_value,
                detect_group=detect_group
            ),
            MemoryTest(
                name='ttest_ind',
                calculate_test=func_bind(ttest_ind, equal_var=False),
                extract_value=extract_value,
                detect_group=detect_group
            ),
            MemoryTest(
                name='permutation_10',
                calculate_test=func_bind(permutation_test, iters_count=10),
                extract_value=extract_value,
                detect_group=detect_group
            ),
            MemoryTest(
                name='permutation_100',
                calculate_test=func_bind(permutation_test, iters_count=100),
                extract_value=extract_value,
                detect_group=detect_group
            ),
            MemoryTest(
                name='bootstrap_10',
                calculate_test=func_bind(bootstrap_test, iters_count=10),
                extract_value=extract_value,
                detect_group=detect_group
            ),
            MemoryTest(
                name='bootstrap_100',
                calculate_test=func_bind(bootstrap_test, iters_count=100),
                extract_value=extract_value,
                detect_group=detect_group
            ),
            PermutationMemoryTest(
                name='permutation_1000',
                extract_value=extract_value,
                detect_group=detect_group,
                iters_count=1000,
                verbose=True
            ),
            BootstrapMemoryTest(
                name='bootstrap_1000',
                extract_value=extract_value,
                detect_group=detect_group,
                iters_count=1000,
                verbose=True
            ),
            PermutationMemoryTest(
                name='permutation_10000',
                extract_value=extract_value,
                detect_group=detect_group,
                iters_count=10000,
                verbose=True
            ),
            BootstrapMemoryTest(
                name='bootstrap_10000',
                extract_value=extract_value,
                detect_group=detect_group,
                iters_count=10000,
                verbose=True
            )
        ],
        input_table_path=input_table_path,
        output_path=output_path,
        parallel_operations_limit=8
    )
