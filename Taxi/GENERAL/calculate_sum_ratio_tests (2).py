#!/usr/bin/env python2

import sys
import json
import argparse

from nile.api.v1 import clusters
from qb2.api.v1 import typing as qt

from zoo.utils.argparse_helpers import str2bool
from zoo.utils.nile_helpers import configure_environment, get_requirement
from zoo.utils.nile_helpers.external import get_schema as read_schema
from zoo.utils.experiments_helpers.multi_test_calculator import (
    MultiTestCalculator, ExperimentParamsValidationError,
    check_unique_keys_hook
)
from zoo.utils.statistics.mr.cluster_tests.bucket_test import SumRatioTest
from zoo.utils.statistics.local.sum_ratio_tests import (
    MannWhitneyUTest, TTest, SumBootstrapTest, ShapiroWilkTest, LeveneTest
)


def make_schema(input_dict, metrics_vertically, return_buckets, tests):
    if metrics_vertically:
        output_schema = {
            'control_value': qt.Float,
            'diff_value': qt.Float,
            'test_value': qt.Float,
            'relative_diff_percent': qt.Float,
            'control_counts': qt.Yson,
            'test_counts': qt.Yson,
            'metric': qt.String,
            'exception': qt.Yson,
            'traceback': qt.Yson,
            'warning': qt.Optional[qt.String]
        }
        if return_buckets:
            output_schema.update({
                'test_buckets': qt.Yson,
                'control_buckets': qt.Yson
            })
        output_schema.update(dict.fromkeys(tests, qt.Yson))
    else:
        output_schema = dict.fromkeys(input_dict['metrics'], qt.Yson)
    output_schema['control_group'] = qt.Yson
    output_schema['test_group'] = qt.Yson
    if input_dict.get('slices') is not None:
        output_schema.update(dict.fromkeys(input_dict['slices'], qt.Yson))
        if metrics_vertically:
            output_schema['slices'] = qt.Yson
    return output_schema


def main(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('--cluster', required=False, default='Hahn')
    parser.add_argument('--input-path', required=True,
                        help='Input table YT path')
    parser.add_argument('--output-path', required=True,
                        help='Result table YT path')
    parser.add_argument('--groups-column', required=True,
                        help='Column name containing experiment groups')
    parser.add_argument('--key-column', required=True,
                        help='Column name containing object key')
    parser.add_argument('--n-buckets', type=int, default=100,
                        help='Number of buckets')
    parser.add_argument('--ttest', nargs='?', const=True, default=False,
                        help='Use ttest', type=str2bool)
    parser.add_argument('--ttest-equal-var', nargs='?', const=True,
                        default=False, type=str2bool,
                        help='Ttest equal variance parameter, bool')
    parser.add_argument('--mannwhitneyu', nargs='?', const=True, default=False,
                        help='Use mann whitney U test', type=str2bool)
    parser.add_argument('--mannwhitneyu-use-continuity', nargs='?', const=True,
                        default=False, type=str2bool,
                        help='Mann Whitney U test parameter, bool')
    parser.add_argument('--mannwhitneyu-alternative', default='two-sided',
                        choices=['two-sided', 'less', 'greater'],
                        help='"two-sided" for the two-sided hypothesis; '
                             '"less" or "greater" for the one-sided')
    parser.add_argument('--bootstrap', nargs='?', const=True, default=False,
                        help='Use bootstrap test', type=str2bool)
    parser.add_argument('--bootstrap-n-iters', type=int, default=10000,
                        help='Bootstrap iterations number')
    parser.add_argument('--alpha', type=float, default=0.05,
                        help='Confidence level for ttest and '
                             'bootstrap confidence intervals')
    parser.add_argument('--combiner-batch-size', type=int, default=1000,
                        help='Batch size for custom combiner')
    parser.add_argument('--unfold-total-slice', type=str2bool,
                        nargs='?', const=True, default=False,
                        help='True will add total slice for each event, bool.')
    parser.add_argument('--total-slice', default=None,
                        help='The value representing total slice; '
                             '"__total__" by default.')
    parser.add_argument('--metrics-vertically', type=str2bool,
                        nargs='?', const=True, default=False,
                        help='True for metrics listed in a column')
    parser.add_argument('--return-buckets', nargs='?', const=True,
                        default=False, type=str2bool,
                        help='Return metric value for each bucket')
    parser.add_argument('--shapiro', nargs='?', const=True,
                        default=False, type=str2bool,
                        help='Use Shapiro-Wilk test for normality')
    parser.add_argument('--levene', nargs='?', const=True,
                        default=False, type=str2bool,
                        help='Use Levene test for variance equality')
    parser.add_argument('--levene-center', default='median',
                        choices=['median', 'mean', 'trimmed'],
                        help='"median" for skewed distributions; '
                             '"mean" for symmetric, moderate-tailed distributions; '
                             '"trimmed" for heavy-tailed distributions.')
    parser.add_argument('--levene-proportiontocut', type=float, default=0.05,
                        help='The proportion of data to cut '
                             'from each end for "trimmed" center')
    parser.add_argument('--config-path', required=True, help='Path to config')
    args = parser.parse_args(arguments)

    with open(args.config_path) as config_json:
        inputs = config_json.read()

    input_dict = json.loads(inputs, object_pairs_hook=check_unique_keys_hook)

    tests = {}
    if args.ttest:
        tests['ttest'] = TTest(
            normalize=True,
            equal_var=args.ttest_equal_var,
            alpha=args.alpha
        )
    if args.mannwhitneyu:
        tests['mannwhitneyu'] = MannWhitneyUTest(
            normalize=True,
            use_continuity=args.mannwhitneyu_use_continuity,
            alternative=args.mannwhitneyu_alternative
        )
    if args.bootstrap:
        tests['bootstrap'] = SumBootstrapTest(
            normalize=True,
            iters_count=args.bootstrap_n_iters,
            alpha=args.alpha
        )
    if args.shapiro:
        tests['shapiro'] = ShapiroWilkTest(normalize=True)
    if args.levene:
        tests['levene'] = LeveneTest(
            normalize=True, center=args.levene_center,
            proportiontocut=args.levene_proportiontocut
        )
    if not tests:
        raise ExperimentParamsValidationError(
            'At least one statistical test must be used'
        )

    cluster = clusters.yt.YT(args.cluster)

    experiment = MultiTestCalculator(
        mr_test=SumRatioTest(
            name='sum_ratio_bucket_bootstrap_test',
            extract_test_id='test_id',
            extract_key='key',
            detect_group='group',
            extract_numerator='numerator',
            extract_denominator='denominator',
            buckets_number=args.n_buckets,
            combiner_batch_size=args.combiner_batch_size,
            calculate_test=tests,
            return_buckets=args.return_buckets
        ),
        metrics=input_dict['metrics'],
        group_column=args.groups_column,
        groups=input_dict['groups'],
        group_pairs=input_dict.get('group_pairs'),
        slices=input_dict.get('slices'),
        key=args.key_column,
        unfold_total_slice=args.unfold_total_slice,
        total_slice=args.total_slice,
        schema=read_schema(cluster, args.input_path),
        metrics_vertically=args.metrics_vertically
    )

    job = configure_environment(
        cluster.job(),
        extra_requirements=[get_requirement('statsmodels')]
    )

    experiment(job.table(args.input_path)).put(
        args.output_path, schema=make_schema(
            input_dict, args.metrics_vertically, args.return_buckets, tests
        )
    )

    job.run()


if __name__ == '__main__':
    main(sys.argv[1:])
