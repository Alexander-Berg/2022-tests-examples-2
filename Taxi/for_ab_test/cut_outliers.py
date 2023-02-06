import argparse

from nile.api.v1 import extractors as ne
from nile.api.v1 import filters as nf

from projects.autoorder.project_config import get_project_cluster


PATH_AB_GOLDEN = '//home/eda-analytics/lavka/stores_top_sku_ab_split'
PATH_GOLDEN_GOODS = (
    '//home/taxi_ml/dev/kozlatkis/lavka_sandbox/ab_split/golden_codes'
)


def get_golden_goods():
    gold = job.table(PATH_GOLDEN_GOODS).project('code', is_golden=ne.const(1))
    gold_ab = (
        job.table(PATH_AB_GOLDEN)
        .filter(nf.equals('group', 'B'))
        .project(
            lavka_id='place_id', is_golden=ne.const(1), golden_group='group',
        )
    )
    return gold.join(
        gold_ab, by=['is_golden'], type='inner', assume_small=True,
    ).project('lavka_id', 'code', 'golden_group')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--path-from', type=str, required=True)
    parser.add_argument('--path-to', type=str, required=True)

    args = parser.parse_args()

    cluster = get_project_cluster(parallel_operations_limit=20, pool='taxi_ml')
    job = cluster.job()
    job = job.env(bytes_decode_mode='strict')

    outliers_blacklist = (
        job.table(args.path_from)
        .filter(
            nf.custom(lambda groups: groups[0] in {'AA_A', 'AA_B'}),
            nf.custom(lambda gmv: gmv == 0),
        )
        .project('code', 'lavka_id')
        .unique('code', 'lavka_id')
    )

    golden_groups = get_golden_goods()

    job.table(args.path_from).join(
        outliers_blacklist,
        by=['code', 'lavka_id'],
        type='left_only',
        assume_small_right=True,
    ).join(
        golden_groups,
        by=['code', 'lavka_id'],
        type='left',
        assume_small_right=True,
    ).project(
        ne.all('golden_group'),
        golden_group=ne.custom(lambda x: [x or 'not_golden'], 'golden_group'),
    ).put(
        args.path_to,
    )

    job.run()
