import argparse
import os
import json
import datetime

from nile.api.v1 import extractors as ne
from nile.api.v1 import Record

from zoo.eats.ranking.project_config import get_project_cluster
from zoo.eats.ranking.monitoring.v2 import metrics, measures

from zoo.utils.experiments_helpers import multi_test_calculator as stat_tests


HITS_POSITIONS = (1, 3)
SUBTOTAL_THRESHOLDS = (1, 500, 1000, 1500, 2000)
REVENUE_THRESHOLDS = (1, 200, 300, 400, 500)


def slices_mapper(records):
    for record in records:
        yield Record(
            record,
            agents=list(measures.get_agents_slices(
                record, yield_total=False
            ))
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sessions-data-path', type=str, required=True)
    parser.add_argument('--output-path', type=str, required=True)
    parser.add_argument('--exp-name', type=str, required=True)
    parser.add_argument('--ttl', type=int, default=7, required=False)

    args = parser.parse_args()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    with open(
        os.path.join(script_dir, 'group_configs', args.exp_name + '.json')
    ) as config_file:
        exp_config = json.load(config_file)

    experiment = stat_tests.MultiTestCalculator(
        mr_test=stat_tests.get_default_sum_ratio_mr_test(
            combiner_batch_size=1000000
        ),
        metrics={
            metric.name: {
                'num': metric.numerator,
                'denom': metric.denominator,
                'aggregation': 'ratio',
            }
            for metric in metrics.get_session_metrics(
                HITS_POSITIONS,
                SUBTOTAL_THRESHOLDS,
                REVENUE_THRESHOLDS
            )
        },
        group_column='last_exp_list',
        groups=exp_config['groups'],
        group_pairs=exp_config['group_pairs'],
        slices={
            'agents': [
                '__total__', 'ios+android',
                'ios', 'android', 'other',
                'other:web:mobile_yes'
            ]
        },
        key='user_uid',
        metrics_vertically=False
    )

    job = get_project_cluster(parallel_operations_limit=10).job()

    experiment(
        job.table(args.sessions_data_path).project(
            ne.all(),
            intensity='cpu',
            **measures.get_session_measures(
                HITS_POSITIONS,
                SUBTOTAL_THRESHOLDS,
                REVENUE_THRESHOLDS
            )
        ).map(slices_mapper, intensity='cpu'),
        intensity='cpu'
    ).put(args.output_path, ttl=datetime.timedelta(days=args.ttl))

    job.run()
