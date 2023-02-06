from __future__ import print_function

import argparse
import itertools
import json

import numpy as np
import pandas as pd
from nile.api.v1 import clusters
from nile.api.v1 import Record
from nile.api.v1 import aggregators as na
from qb2.api.v1 import filters as qf

from zoo.utils.nile_helpers import dates as zd
from zoo.utils.nile_helpers import filters as zf
from zoo.utils.nile_helpers import configure_environment
from zoo.utils.time_helpers import create_date_parser
from zoo.utils.pandas_helpers import as_markup
from zoo.utils.experiments_helpers.group_detectors import ExperimentGroupDetector
from zoo.utils.statistics.local.sum_ratio_tests import SumBootstrapTest
from zoo.utils.statistics.mr.cluster_tests import SumRatioBucketTest
from zoo.utils.statistics.mr.common import TestsWithPreprocessor


ORDERS_YT_PATH = '//home/taxi-dwh/summary/dm_order'
OUTPUT_YT_PATH = '//home/taxi_ml/zoo/examples/mr_bucket_test_output'
SYMBOLS = list('0123456789abcdef')
BUCKETS_NUMBERS = [10, 100, 1000, 10000]
PVALUE_THRESHOLDS = [0.01, 0.05, 0.1, 0.25, 0.5]


def generate_detectors(count=500, percent=50, random_seed=42, salt_length=32):
    np.random.seed(random_seed)
    detectors = []
    for _ in range(count):
        salt = ''.join(np.random.choice(SYMBOLS, salt_length))
        detectors.append(ExperimentGroupDetector(0, percent, salt))
    return detectors


def prepare_data(job, dttm_from, dttm_to, group_detectors):
    def mapper(records):
        for r in records:
            for i, detector in enumerate(group_detectors):
                yield Record(
                    test_id=i, key=r.user_id, group=detector(r.user_id),
                    numerator=r.numerator, denominator=r.denominator
                )

    table_path = '{}/{}'.format(
        ORDERS_YT_PATH, zd.range_selector(
            dttm_from, dttm_to, date_format='%Y-%m'
        )
    )
    return job.table(
        table_path
    ).filter(
        zf.dttm_between(dttm_from, dttm_to, 'utc_order_dttm'),
        qf.one_of('application_platform', ['android', 'iphone'])
    ).groupby('user_id').aggregate(
        numerator=na.sum('success_order_flg'),
        denominator=na.count()
    ).map(mapper, intensity='ultra_cpu')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    dttm_parser = create_date_parser('%Y-%m-%dT%H:%M:%S')
    parser.add_argument('--dttm-from', type=dttm_parser, required=True)
    parser.add_argument('--dttm-to', type=dttm_parser, required=True)
    parser.add_argument('--splits-count', type=int, default=500)
    parser.add_argument('--percent', type=int, default=50)
    parser.add_argument('--iters-count', type=int, default=1000)
    args = parser.parse_args()


    group_detectors = generate_detectors(args.splits_count, args.percent)
    test_calculator = TestsWithPreprocessor(
        tests=[
            SumRatioBucketTest(
                name=json.dumps(dict(
                    calc_mean=calc_mean, buckets_number=buckets_number
                )),
                extract_test_id='test_id',
                extract_numerator='numerator',
                extract_denominator='denominator',
                detect_group='group',
                extract_key='key',
                buckets_number=buckets_number,
                calculate_test=SumBootstrapTest(
                    normalize=calc_mean, iters_count=args.iters_count
                ),
            )
            for calc_mean, buckets_number in itertools.product(
                [False, True], BUCKETS_NUMBERS
            )
        ]
    )
    cluster = configure_environment(
        clusters.yt.Hahn(), parallel_operations_limit=8
    )

    job = cluster.job()
    test_calculator.calc_4_table_with_name(
        prepare_data(job, args.dttm_from, args.dttm_to, group_detectors)
    ).put(OUTPUT_YT_PATH)
    job.run()

    rows = []
    for record in cluster.read(OUTPUT_YT_PATH):
        doc = json.loads(record.name)
        for thr in PVALUE_THRESHOLDS:
            doc['pvalue<{}'.format(thr)] = record.pvalue < thr
        rows.append(doc)
    df = pd.DataFrame(rows).groupby(
        by=['calc_mean', 'buckets_number']
    ).mean().reset_index()
    print(as_markup(df, use_index=False))
