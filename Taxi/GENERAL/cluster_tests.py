from functools import partial as func_bind

from nile.api.v1 import extractors as ne
from scipy.stats import mannwhitneyu
from scipy.stats import ttest_ind

from zoo.utils.statistics.mr import memory_tests
from zoo.utils.statistics.mr import cluster_tests
from zoo.utils.statistics.mr.common import perform_tests


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
            memory_tests.MemoryTest(
                name='memory_mannwhitneyu',
                calculate_test=func_bind(
                    mannwhitneyu,
                    alternative='two-sided'
                ),
                extract_value=extract_value,
                detect_group=detect_group
            ),
            cluster_tests.MannWhitneyTest(
                name='cluster_mannwhitneyu_long_arithmetic',
                extract_value=extract_value,
                detect_group=detect_group
            ),
            memory_tests.MemoryTest(
                name='memory_ttest_ind',
                calculate_test=func_bind(ttest_ind, equal_var=False),
                extract_value=extract_value,
                detect_group=detect_group
            ),
            cluster_tests.IndTTest(
                name='cluster_ttest_ind',
                extract_value=extract_value,
                detect_group=detect_group,
                equal_var=False
            ),
            cluster_tests.IndTTest(
                name='cluster_ttest_ind_long_arithmetic',
                extract_value=extract_value,
                detect_group=detect_group,
                equal_var=False,
                use_long_arithmetic=True
            )
        ],
        input_table_path=input_table_path,
        output_path=output_path,
        parallel_operations_limit=8
    )
