from __future__ import print_function

from nile.api.v1 import clusters

from zoo.utils.nile_helpers import configure_environment, get_requirement
from zoo.utils.nile_helpers.external import get_schema as read_schema
from zoo.utils.experiments_helpers.multi_test_calculator import MultiTestCalculator
from zoo.utils.statistics.mr.cluster_tests.bucket_test import SumRatioTest
from zoo.utils.statistics.local.sum_ratio_tests import MannWhitneyUTest, TTest, SumBootstrapTest

INPUT_PATH = (
    '//home/taxi_ml/dev/nirvana_bucket_multitest/develop/input_three_groups'
)
OUTPUT_PATH = (
    '//home/taxi_ml/dev/nirvana_bucket_multitest/develop/output'
)

input_dict = {
    'metrics': {
        'order_conversion': {
            'num': 'success_order_flg',
            'aggregation': 'mean'
        },
        'order_cost_ru': {
            'num': 'order_cost_ru',
            'aggregation': 'mean'
        },
        'order_smth': {
            'num': 'success_order_flg',
            'aggregation': 'ratio',
            'denom': 'order_cost_ru'
        }
    },
    'groups': ['no_altpins', 'old_altpins', 'new_altpins'],
    'group_pairs': [('no_altpins', 'old_altpins'), ('no_altpins', 'new_altpins')],
    'slices': {'application_platform': ['iphone'], 'attr_countries': None}
}


def main():
    experiment = MultiTestCalculator(
        mr_test=SumRatioTest(
            name='sum_ratio_bucket_bootstrap_test',
            extract_test_id='test_id',
            extract_key='key',
            detect_group='group',
            extract_numerator='numerator',
            extract_denominator='denominator',
            buckets_number=100,
            combiner_batch_size=1000,
            calculate_test={
                'SumBootstrapTest': SumBootstrapTest(
                    normalize=True, iters_count=1000
                ),
                'TTest': TTest(
                    normalize=True, equal_var=False
                ),
                'MannWhitneyuUTest': MannWhitneyUTest(
                    normalize=True,
                    use_continuity=True, alternative='two-sided'
                )
            }
        ),
        metrics=input_dict.get('metrics'),
        group_column='group',
        groups=input_dict.get('groups'),
        group_pairs=input_dict.get('group_pairs'),
        slices=input_dict.get('slices'),
        key='user_phone_id',
        schema=read_schema(clusters.yt.Hahn(), INPUT_PATH),
        metrics_vertically=False
    )

    job = configure_environment(
        clusters.yt.Hahn().job(),
        extra_requirements=[get_requirement('statsmodels')]
    )

    experiment(
        job.table(INPUT_PATH)
    ).put(OUTPUT_PATH)

    job.run()


if __name__ == '__main__':
    main()
