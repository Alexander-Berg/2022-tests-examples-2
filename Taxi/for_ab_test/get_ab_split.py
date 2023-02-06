import argparse

from nile.api.v1 import filters as nf

from projects.autoorder.project_config import get_project_cluster
from projects.common.nile.dates import range_selector

BLACKLIST_START = '2020-09-12'
BLACKLIST_END = '2020-09-17'
BLACKLIST_GROUP = 'B'

AB_TEST_LOG = '//home/lavka/testing/autoorders/predictions/ab_test_log/{}'


def get_split(job, start_date, end_date, group=None):
    result = job.table(
        AB_TEST_LOG.format(range_selector(start_date, end_date, '%Y-%m-%d')),
        ignore_missing=True,
    )
    if group is not None:
        result = result.filter(nf.equals('group', group)).unique(
            'lavka_id', 'code',
        )
    else:
        result = result.unique('group', 'lavka_id', 'code')
    return result


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--start-date', type=str, required=True)
    parser.add_argument('--end-date', type=str, required=True)

    args = parser.parse_args()

    cluster = get_project_cluster(parallel_operations_limit=20, pool='taxi_ml')
    job = cluster.job()
    job = job.env(bytes_decode_mode='strict')

    blacklist = get_split(
        job, BLACKLIST_START, BLACKLIST_END, BLACKLIST_GROUP,
    ).put(args.path + '_blacklist')

    current_split = (
        get_split(job, args.start_date, args.end_date, group=None)
        .join(
            blacklist,
            by=['lavka_id', 'code'],
            type='left_only',
            assume_unique=True,
        )
        .put(args.path)
    )

    job.run()
