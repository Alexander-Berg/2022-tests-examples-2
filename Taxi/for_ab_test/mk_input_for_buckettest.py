import argparse
import datetime
from collections import OrderedDict

from nile.api.v1 import Record
from nile.api.v1 import aggregators as na
from nile.api.v1 import extractors as ne
from nile.api.v1 import filters as nf
from qb2.api.v1 import filters as qf

from projects.autoorder.project_config import get_project_cluster
from projects.common.nile.dates import range_selector


def diff_reducer(periods_dict, fields):
    def reducer(groups):
        for key, records in groups:
            periods = list(periods_dict.keys())
            sums = {k: {field: 0 for field in fields} for k in periods}
            for record in records:
                for k in periods:
                    if (
                            periods_dict[k][0]
                            <= record['date']
                            <= periods_dict[k][1]
                    ):
                        for field in fields:
                            sums[k][field] += record[field] or 0
            diffs = {k: {field: 0 for field in fields} for k in periods[1:]}
            for i in range(1, len(periods)):
                for field in fields:
                    diffs[periods[i]][field] = (
                        sums[periods[i]][field] - sums[periods[i - 1]][field]
                    )
            for period in ['AA', 'AB']:
                yield Record(
                    key,
                    period=period,
                    **{
                        '{}_diff'.format(field): diffs[period][field]
                        for field in fields
                    },
                )

    return reducer


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--begin', type=str, required=True)
    parser.add_argument('--end', type=str, required=True)
    parser.add_argument('--aa-begin', type=str, required=True)
    parser.add_argument('--aa-end', type=str, required=True)
    parser.add_argument('--metrics-path', type=str, required=True)
    parser.add_argument('--split-path', type=str, required=True)
    parser.add_argument('--result-path', type=str, required=True)
    parser.add_argument(
        '--shelf-life-slices', type=str, required=False, default='',
    )
    parser.add_argument('--last-week-delta', type=int, required=True)

    args = parser.parse_args()

    shelf_life_slices = (
        []
        if args.shelf_life_slices == '-'
        else [int(s) for s in args.shelf_life_slices.split(',')]
    )

    cluster = get_project_cluster(parallel_operations_limit=20, pool='taxi_ml')
    job = cluster.job()
    job = job.env(bytes_decode_mode='strict')

    begin_dt = args.begin
    end_dt = args.end

    begin = datetime.datetime.strptime(begin_dt, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_dt, '%Y-%m-%d')

    aa_begin_dt = args.aa_begin
    aa_end_dt = args.aa_end

    aa_begin = datetime.datetime.strptime(aa_begin_dt, '%Y-%m-%d')
    aa_end = datetime.datetime.strptime(aa_end_dt, '%Y-%m-%d')

    last_week_delta = args.last_week_delta

    full_metrics = (
        job.table(
            args.metrics_path.format(
                range_selector(
                    aa_begin - datetime.timedelta(days=last_week_delta),
                    end,
                    '%Y-%m',
                ),
            ),
            ignore_missing=True,
        )
        .filter(
            nf.and_(
                qf.compare(
                    'date',
                    '>=',
                    value=(
                        aa_begin - datetime.timedelta(days=last_week_delta)
                    ).strftime('%Y-%m-%d'),
                ),
                qf.compare('date', '<=', value=end_dt),
            ),
        )
        .project(
            ne.all(),
            lavka_id='organization_id',
            gmv=ne.custom(
                lambda x, y: x * y if y is not None else 0,
                'n_units_of_sku',
                'sales_price',
            ),
            loss_sum_cnt=ne.custom(
                lambda x, y: (x or 0) + (y or 0),
                'undersales_cnt',
                'writeoff_cnt',
            ),
            profit=ne.custom(
                lambda x, y, z: x - y - z,
                'gmv',
                'writeoff_loss',
                'discounts_loss',
            ),
            profit_cnt=ne.custom(
                lambda x, y: x - y, 'n_units_of_sku', 'writeoff_cnt',
            ),
            writeoff_disc_sum=ne.custom(
                lambda x, y: x + y, 'writeoff_loss', 'discounts_loss',
            ),
        )
    )

    periods_dict = OrderedDict(
        before_AA=[
            (aa_begin - datetime.timedelta(days=last_week_delta)).strftime(
                '%Y-%m-%d',
            ),
            (aa_end - datetime.timedelta(days=last_week_delta)).strftime(
                '%Y-%m-%d',
            ),
        ],
        AA=[aa_begin_dt, aa_end_dt],
        before_AB=[
            (begin - datetime.timedelta(days=last_week_delta)).strftime(
                '%Y-%m-%d',
            ),
            (end - datetime.timedelta(days=last_week_delta)).strftime(
                '%Y-%m-%d',
            ),
        ],
        AB=[begin_dt, end_dt],
    )

    print(periods_dict)

    diff_fields = [
        'gmv',
        'n_units_of_sku',
        'loss_sum',
        'undersales_loss',
        'writeoff_loss',
        'undersales_cnt',
        'writeoff_cnt',
        'loss_sum_cnt',
        'profit',
        'profit_cnt',
        'writeoff_disc_sum',
    ]

    difference = full_metrics.groupby('code', 'lavka_id').reduce(
        diff_reducer(periods_dict, diff_fields),
    )

    metrics = (
        full_metrics.filter(
            nf.or_(
                nf.and_(
                    qf.compare('date', '>=', value=aa_begin_dt),
                    qf.compare('date', '<=', value=aa_end_dt),
                ),
                nf.and_(
                    qf.compare('date', '>=', value=begin_dt),
                    qf.compare('date', '<=', value=end_dt),
                ),
            ),
        ).project(
            ne.all(),
            period=ne.custom(
                lambda x: 'AB' if begin_dt <= x <= end_dt else 'AA', 'date',
            ),
        )
    )

    splits = job.table(args.split_path).project(
        ne.all(),
        code_lavka=ne.custom(
            lambda x, y: str(x) + '_' + str(y), 'code', 'lavka_id',
        ),
    )

    result = (
        metrics.join(
            splits,
            by=['code', 'lavka_id'],
            type='inner',
            assume_unique_right=True,
        )
        .groupby('code_lavka', 'period', 'group', 'code', 'lavka_id')
        .aggregate(
            shelf_life=na.min('shelf_life'),
            **{
                field: na.sum(field)
                for field in [
                    'gmv',
                    'loss_sum',
                    'n_units_of_sku',
                    'undersales_loss',
                    'writeoff_loss',
                    'undersales_cnt',
                    'writeoff_cnt',
                    'loss_sum_cnt',
                    'profit',
                    'profit_cnt',
                    'writeoff_disc_sum',
                ]
            },
        )
        .project(
            'gmv',
            'loss_sum',
            'n_units_of_sku',
            'undersales_loss',
            'writeoff_loss',
            'period',
            'code',
            'lavka_id',
            'undersales_cnt',
            'writeoff_cnt',
            'loss_sum_cnt',
            'profit',
            'profit_cnt',
            'writeoff_disc_sum',
            key='code_lavka',
            groups=ne.custom(lambda x, y: [x + '_' + y], 'period', 'group'),
            life=ne.custom(
                lambda x: [
                    'l{}'.format(sl) for sl in shelf_life_slices if x <= sl
                ],
                'shelf_life',
            ),
        )
        .join(
            difference,
            by=['code', 'lavka_id', 'period'],
            assume_unique=True,
            type='inner',
        )
    )

    result.put(args.result_path)

    job.run()
