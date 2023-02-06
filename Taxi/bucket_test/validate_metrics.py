from typing import Dict, Any
import argparse
import sys
import json

from qb2.api.v1 import typing as qt

from projects.common.argparse import add_bool_flag
from projects.common.statistics.mr_operations.metric_validator import (
    MetricValidator,
)
from projects.common.statistics.params_helpers import (
    ExperimentParamsValidationError,
    ParametersChecker,
    create_params,
    check_unique_keys_hook,
)
from projects.common.nile.external import get_schema as read_schema
from projects.common.nile.environment import DEFAULT_CLUSTER
from projects.common.statistics.local_tests import (
    TTest,
    MannWhitneyUTest,
    SumBootstrapTest,
    ShapiroWilkTest,
    LeveneTest,
)
from projects.bucket_test.project_config import get_project_cluster


N_BUCKETS = 100
BOOTSTRAP_N_ITERS = 10000
CONFIDENCE_LEVEL = 0.05
COMBINER_BATCH_SIZE = 1000
LEVENE_PROPORTION = 0.05
N_EXPERIMENTS = 1000
MINIBUCKET_MOD = 1000000
PVALUE_THRESHOLD = 0.05
PERCENT = 50


def make_schema(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    output_schema = dict(
        bad_ratio=qt.Float,
        binom_test_pvalue=qt.Float,
        hits_ratio=qt.Float,
        metric=qt.String,
        percent=qt.Integer,
        pvalue_threshold=qt.Float,
        stat_test=qt.String,
    )
    if input_dict.get('slices') is not None:
        output_schema.update(dict.fromkeys(input_dict['slices'], qt.Yson))
        output_schema['slices'] = qt.Yson
    return output_schema


def main(arguments):
    parser = argparse.ArgumentParser()
    parser.add_argument('--yt-proxy', required=False, default=DEFAULT_CLUSTER)
    parser.add_argument(
        '--input-path', required=True, help='Input table YT path',
    )
    parser.add_argument(
        '--output-path', required=True, help='Result table YT path',
    )
    parser.add_argument(
        '--key-column',
        required=True,
        help='Column name containing object key',
    )
    parser.add_argument(
        '--minibucket-mod',
        type=int,
        default=MINIBUCKET_MOD,
        help='Mini buckets limit',
    )
    parser.add_argument(
        '--n-experiments',
        type=int,
        default=N_EXPERIMENTS,
        help='Number of experiments',
    )
    parser.add_argument(
        '--n-buckets', type=int, default=N_BUCKETS, help='Number of buckets',
    )
    parser.add_argument(
        '--percents',
        type=int,
        nargs='+',
        default=[PERCENT],
        help='Each percent splits data into two parts',
    )
    parser.add_argument(
        '--pvalue-thresholds',
        type=float,
        nargs='+',
        default=[PVALUE_THRESHOLD],
        help='List of significance levels',
    )
    parser.add_argument(
        '--binom-test-alternative',
        default='larger',
        choices=['two-sided', 'smaller', 'larger'],
        help='"two-sided" for the two-sided hypothesis; '
        '"smaller" or "larger" for the one-sided',
    )
    add_bool_flag(parser, '--ttest', help='Use ttest')
    add_bool_flag(
        parser,
        '--ttest-equal-var',
        help='Ttest equal variance parameter, bool',
    )
    add_bool_flag(parser, '--mannwhitneyu', help='Use mann whitney U test')
    add_bool_flag(
        parser,
        '--mannwhitneyu-use-continuity',
        help='Mann Whitney U test parameter, bool',
    )
    parser.add_argument(
        '--mannwhitneyu-alternative',
        default='two-sided',
        choices=['two-sided', 'less', 'greater'],
        help='"two-sided" for the two-sided hypothesis; '
        '"less" or "greater" for the one-sided',
    )
    add_bool_flag(parser, '--bootstrap', help='Use bootstrap test')
    parser.add_argument(
        '--bootstrap-n-iters',
        type=int,
        default=BOOTSTRAP_N_ITERS,
        help='Bootstrap iterations number',
    )
    parser.add_argument(
        '--confidence-level',
        type=float,
        default=CONFIDENCE_LEVEL,
        help='Confidence level for ttest and '
        'bootstrap confidence intervals',
    )
    parser.add_argument(
        '--combiner-batch-size',
        type=int,
        default=COMBINER_BATCH_SIZE,
        help='Batch size for custom combiner',
    )
    add_bool_flag(
        parser,
        '--unfold-total-slice',
        help='True will add total slice for each event, bool.',
    )
    parser.add_argument(
        '--total-slice',
        default=None,
        help='The value representing total slice; "__total__" by default.',
    )
    add_bool_flag(
        parser,
        '--metrics-vertically',
        help='True for metrics listed in a column',
    )
    add_bool_flag(
        parser, '--shapiro', help='Use Shapiro-Wilk test for normality',
    )
    add_bool_flag(
        parser, '--levene', help='Use Levene test for variance equality',
    )
    parser.add_argument(
        '--levene-center',
        default='median',
        choices=['median', 'mean', 'trimmed'],
        help='"median" for skewed distributions; '
        '"mean" for symmetric, moderate-tailed distributions; '
        '"trimmed" for heavy-tailed distributions.',
    )
    parser.add_argument(
        '--levene-proportiontocut',
        type=float,
        default=LEVENE_PROPORTION,
        help='The proportion of data to cut '
        'from each end for "trimmed" center',
    )
    parser.add_argument('--config-path', required=True, help='Path to config')
    parser.add_argument('--hash-salt', required=False, default=None)
    args = parser.parse_args(arguments)

    with open(args.config_path) as config_json:
        input_dict = json.load(
            config_json, object_pairs_hook=check_unique_keys_hook,
        )

    tests = dict()
    if args.ttest:
        tests['ttest'] = TTest(
            equal_var=args.ttest_equal_var,
            confidence_level=args.confidence_level,
        )
    if args.mannwhitneyu:
        tests['mannwhitneyu'] = MannWhitneyUTest(
            use_continuity=args.mannwhitneyu_use_continuity,
            alternative=args.mannwhitneyu_alternative,
        )
    if args.bootstrap:
        tests['bootstrap'] = SumBootstrapTest(
            iters_count=args.bootstrap_n_iters,
            confidence_levels=args.confidence_level,
        )
    if args.shapiro:
        tests['shapiro'] = ShapiroWilkTest()
    if args.levene:
        tests['levene'] = LeveneTest(
            center=args.levene_center,
            proportiontocut=args.levene_proportiontocut,
        )
    if not tests:
        raise ExperimentParamsValidationError(
            'At least one statistical test must be used',
        )

    cluster = get_project_cluster(proxy=args.yt_proxy)

    parameters_checker = ParametersChecker(metric_validation_mode=True)
    parameters_checker.check_params(
        key_column=args.key_column,
        metrics=input_dict['metrics'],
        slices=input_dict.get('slices'),
    )
    parameters_checker.check_schema(
        key_column=args.key_column,
        schema=read_schema(cluster, args.input_path),
        metrics=input_dict['metrics'],
        slices=input_dict.get('slices'),
    )
    metrics, features, slices = create_params(
        metrics=input_dict['metrics'],
        slices=input_dict.get('slices'),
        unfold_total=args.unfold_total_slice,
        total_value=args.total_slice,
    )

    experiment = MetricValidator(
        minibucket_mod=args.minibucket_mod,
        n_experiments=args.n_experiments,
        percents=args.percents,
        pvalue_thresholds=args.pvalue_thresholds,
        alternative=args.binom_test_alternative,
        stat_tests=tests,
        metrics=metrics,
        features=features,
        slices=slices,
        key_column=args.key_column,
        hash_salt=args.hash_salt,
        n_buckets=args.n_buckets,
        combiner_batch_size=args.combiner_batch_size,
    )

    job = cluster.job()

    experiment(job.table(args.input_path)).put(
        args.output_path, schema=make_schema(input_dict),
    )

    job.run()


if __name__ == '__main__':
    main(sys.argv[1:])
