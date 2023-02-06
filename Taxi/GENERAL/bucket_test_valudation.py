from __future__ import print_function

import argparse
from functools import partial as func_bind

import numpy as np
import pandas as pd
from scipy.stats import binom, ttest_ind, mannwhitneyu
from tqdm import tqdm

from zoo.utils.statistics.local.sum_ratio_tests import SumBootstrapTest
from zoo.utils.pandas_helpers import as_markup


EFFECTS = [0., 0.001, 0.01, 0.02, 0.05]
FST_SALT = 'fst'
SND_SALT = 'snd'
UNIFORM_WARNING = (
    'Please make sure that the number of groups'
    ' is divided by each number of buckets'
)


def test_wrapper(test, calc_mean=False):
    if calc_mean:
        def func(fst_nums, snd_nums, fst_denums, snd_denums):
            return test(fst_nums / fst_denums, snd_nums / snd_denums)
    else:
        def func(fst_nums, snd_nums, fst_denums, snd_denums):
            return test(fst_nums, snd_nums)
    return func


def generate(gen, groups_count, group_size,  p0, delta):
    p0_values = gen.uniform(
        p0 - delta,
        p0 + delta,
        size=groups_count
    )
    return binom.rvs(group_size, p0_values)


def aggregate(data, n_buckets, indices, calc_sum):
    nums = np.bincount(indices, weights=data, minlength=n_buckets)
    if calc_sum:
        denums = None
    else:
        denums = np.bincount(indices, minlength=n_buckets)
    return nums, denums


def create_batched_test(test, n_buckets, fst_indices, snd_indices, calc_sum):
    def func(data_fst, data_snd):
        fst_nums, fst_denums = aggregate(
            data_fst, n_buckets, fst_indices, calc_sum
        )
        snd_nums, snd_denums = aggregate(
            data_snd, n_buckets, snd_indices, calc_sum
        )
        return test(fst_nums, snd_nums, fst_denums, snd_denums).pvalue
    return func


def eval_hits_ratio(test, effect, n_groups, events_per_group,
                    mean_conversion, conversion_var, alpha, n_iter):
    hits = 0.
    count = 0.
    gen = np.random.RandomState(7)

    for _ in xrange(n_iter):
        data_fst = generate(
            gen, n_groups, events_per_group,
            mean_conversion, conversion_var
        )
        data_snd = generate(
            gen, n_groups, events_per_group,
            mean_conversion + effect, conversion_var
        )

        count += 1
        pvalue = test(data_fst, data_snd)
        if pvalue < alpha:
            hits += 1
    return hits / count


def parse_arguments(parser):
    parser.add_argument(
        '--no-hash', action='store_true',
    )
    parser.add_argument(
        '--calc-sum', action='store_true',
    )
    parser.add_argument(
        '--n-groups', type=int, default=1000
    )
    parser.add_argument(
        '--events-per-group', type=int, default=50
    )
    parser.add_argument(
        '--mean-conversion', type=float, default=0.7
    )
    parser.add_argument(
        '--conversion-var', type=float, default=0.1
    )
    parser.add_argument(
        '--bootstrap-iters', type=int, default=1000
    )
    parser.add_argument(
        '--alpha', type=float, default=0.05
    )
    parser.add_argument(
        '--n-iter', type=int, default=1000
    )
    parser.add_argument(
        '--test', type=str, choices=['Ttest', 'Bootstrap', 'MW'], required=True
    )
    parser.add_argument(
        '--n-buckets', type=int, nargs='*',
        default=[5, 10, 50, 100, 1000]
    )
    return parser.parse_args()


def main():
    args = parse_arguments(argparse.ArgumentParser())

    if args.no_hash:
        for size in args.n_buckets:
            if args.n_groups % size != 0:
                raise RuntimeError(UNIFORM_WARNING)
    calc_mean = not args.calc_sum
    if args.test == 'Ttest':
        test = test_wrapper(
            func_bind(ttest_ind, equal_var=False),
            calc_mean=calc_mean
        )
    elif args.test == 'Bootstrap':
        test = SumBootstrapTest(
            normalize=calc_mean, iters_count=args.bootstrap_iters
        )
    else:
        test = test_wrapper(
            func_bind(mannwhitneyu, alternative='two-sided'),
            calc_mean=calc_mean
        )
    group_ids = np.arange(args.n_groups)
    result = {}
    for effect in EFFECTS:
        hits_for_effect = []
        for n_buckets in tqdm(args.n_buckets):
            if args.no_hash:
                fst_indices = np.mod(np.arange(args.n_groups), n_buckets)
                snd_indices = fst_indices
            else:
                fst_indices = np.vectorize(
                    lambda x: hash(str(x) + FST_SALT) % n_buckets
                )(group_ids).astype(int)
                snd_indices = np.vectorize(
                    lambda x: hash(str(x) + SND_SALT) % n_buckets
                )(group_ids).astype(int)

            hits_for_effect.append(
                eval_hits_ratio(
                    create_batched_test(
                        test,
                        n_buckets,
                        fst_indices,
                        snd_indices,
                        args.calc_sum
                    ),
                    effect,
                    args.n_groups,
                    args.events_per_group,
                    args.mean_conversion,
                    args.conversion_var,
                    args.alpha,
                    args.n_iter
                )
            )
        result['effect: {}'.format(effect)] = hits_for_effect
    result['n_buckets'] = args.n_buckets
    print(as_markup(pd.DataFrame(result).set_index('n_buckets')))


if __name__ == '__main__':
    main()
