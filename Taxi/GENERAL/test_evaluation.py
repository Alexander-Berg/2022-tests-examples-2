import argparse

from nile.api.v1 import extractors as ne
from nile.api.v1 import Record

from zoo.eats.ranking.project_config import get_project_cluster
from zoo.eats.ranking.monitoring.v1 import stats_evaluation

from zoo.utils.experiments_helpers import multi_test_calculator as stat_tests


def slices_mapper(records):
    for record in records:
        yield Record(
            record,
            slices=list(stats_evaluation.get_agents_slices(record))
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--session-metrics-path', type=str, required=True)
    parser.add_argument('--output-path', type=str, required=True)

    args = parser.parse_args()

    input_dict = {
        'metrics': {
            name: {
                'num': num,
                'denom': denom,
                'aggregation': 'ratio',
            }
            for name, (num, denom) in stats_evaluation.get_ratio_metrics([1, 3]).items()
        },
        'groups': [
            'heuristic_v2_cxx',
            'personal_v1_top0', 'personal_v1_top1',
            'personal_v1_top2', 'personal_v1_top3'
        ],
        'group_pairs': [
            ('personal_v1_top0', 'personal_v1_top1'),
            ('personal_v1_top0', 'personal_v1_top2'),
            ('personal_v1_top0', 'personal_v1_top3'),
            ('personal_v1_top1', 'personal_v1_top3'),
            ('heuristic_v2_cxx', 'personal_v1_top1'),
            ('heuristic_v2_cxx', 'personal_v1_top3')
        ],
        'slices': ['slices']
    }

    experiment = stat_tests.MultiTestCalculator(
        mr_test=stat_tests.get_default_sum_ratio_mr_test(
            combiner_batch_size=1000000
        ),
        metrics=input_dict.get('metrics'),
        group_column='last_exp_list',
        groups=input_dict.get('groups'),
        group_pairs=input_dict.get('group_pairs'),
        slices=input_dict.get('slices'),
        key='user_uid',
        metrics_vertically=False
    )

    job = get_project_cluster(parallel_operations_limit=10).job()

    experiment(
        job.table(args.session_metrics_path).project(
            ne.all(),
            intensity='cpu',
            **stats_evaluation.get_stats_projections([1, 3])
        ).map(slices_mapper, intensity='cpu'),
        intensity='cpu'
    ).put(args.output_path)

    job.run()
