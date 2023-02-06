import argparse
import datetime
import os

from nile.api.v1 import extractors as ne
from nile.api.v1 import filters as nf
from qb2.api.v1 import filters as qf

from projects.autoorder.data_context.v2.data_context import DataContext
from projects.autoorder.data_context.v2.sources_context import dt_2_timestamp
from projects.autoorder.features_config.config_parser import JsonConfigParser
from projects.autoorder.feature_constructors import (
    get_precalc_dataset,
    construct_features_dataset,
)
from projects.autoorder.model_config import (
    MAIN_LAG,
    FEATURES_MAX_WINDOW,
    PROMO_MODEL_ALIAS_DCT,
)
from projects.autoorder.project_config import (
    DEFAULT_MEMORY_LIMIT,
    get_project_cluster,
)
from projects.common.argparse import add_bool_flag
from projects.common.nile import filters as pf

SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = 24 * 3600


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # log_end_date is interpreted as the first predicted date of the last
    # prediction date
    parser.add_argument('--log-end-date', type=str, required=True)
    parser.add_argument('--n-days', type=int, required=False, default=1)
    parser.add_argument('--result-path', type=str, required=True)
    parser.add_argument('--features-config', type=str, required=True)
    parser.add_argument('--demand-for-features-path', type=str, required=True)
    parser.add_argument(
        '--demand-for-features-field',
        type=str,
        required=False,
        default='restored_sales_p28_f0_wo_rep',
    )
    parser.add_argument(
        '--yt-pool', type=str, required=False, default='goml_adhoc',
    )
    # if True, script assumes that there is no has_history info for prediction
    # date
    add_bool_flag(parser, '--in-future', False)

    args = parser.parse_args()

    assert (
        not args.in_future or args.n_days == 1
    ), 'in_future param could only be used with n_days == 1.'

    cluster = get_project_cluster(pool=args.yt_pool)
    job = cluster.job('Autoorder make test dataset')
    job = job.env(
        bytes_decode_mode='strict', default_memory_limit=DEFAULT_MEMORY_LIMIT,
    )

    local_dir = os.path.dirname(os.path.abspath(__file__))
    config_parser = JsonConfigParser(
        cluster=cluster, yt_path=args.features_config,
    )
    features_templates = config_parser.get_features_templates()

    end = datetime.datetime.strptime(args.log_end_date, '%Y-%m-%d')
    dataset_end = end - datetime.timedelta(days=MAIN_LAG - 1)
    dataset_begin = dataset_end - datetime.timedelta(days=args.n_days)
    begin = dataset_begin - datetime.timedelta(days=FEATURES_MAX_WINDOW)

    begin_dt = begin.strftime('%Y-%m-%d')
    dataset_begin_dt = dataset_begin.strftime('%Y-%m-%d')
    dataset_end_dt = dataset_end.strftime('%Y-%m-%d')

    print(begin, dataset_begin, dataset_end, end)

    data_context = DataContext(job, cluster, begin_dt, dataset_end_dt)

    features_dataset = (
        get_precalc_dataset(
            job, args.demand_for_features_path, begin_dt, dataset_end_dt,
        ).project(
            'code',
            'organization_id',
            'date_local',
            'timestamp',
            'isoweekday_local',
            'has_history',
            'promo',
            timepoint_id=ne.custom(
                lambda x, y, z: f'{x}_{y}_{z}',
                'date_local',
                'organization_id',
                'code',
            ),
            sales=args.demand_for_features_field,
            **{
                alias: ne.custom(lambda x, y=key: int(y in x), 'promo')
                for key, alias in PROMO_MODEL_ALIAS_DCT.items()
            },
        )
    )

    if args.in_future:
        tz = data_context.get_stores_timezones()
        last_feature_date = (
            dataset_begin - datetime.timedelta(days=1)
        ).strftime('%Y-%m-%d')
        timepoints = (
            features_dataset.filter(
                nf.equals('date_local', last_feature_date),
                nf.or_(
                    nf.equals('has_history', True), qf.nonzero('true_sales'),
                ),
            ).project(
                'code',
                'organization_id',
                timestamp=ne.custom(
                    lambda x, y=tz: dt_2_timestamp(
                        dataset_begin_dt, y[x], '%Y-%m-%d',
                    ),
                    'organization_id',
                ),
                date_local=ne.const(dataset_begin_dt),
                timepoint_id=ne.custom(
                    lambda x, y: f'{dataset_begin_dt}_{x}_{y}',
                    'organization_id',
                    'code',
                ),
            )
        )
    else:
        timepoints = (
            features_dataset.filter(
                pf.dttm_between(
                    dataset_begin, dataset_end, 'date_local', '%Y-%m-%d',
                ),
                nf.equals('has_history', True),
            ).project(
                'date_local',
                'code',
                'organization_id',
                'timestamp',
                timepoint_id=ne.custom(
                    lambda x, y, z: f'{x}_{y}_{z}',
                    'date_local',
                    'organization_id',
                    'code',
                ),
            )
        )

    features = construct_features_dataset(
        job=job,
        data_context=data_context,
        timepoints=timepoints,
        dataset=features_dataset.project(ne.all('timepoint_id')),
        features_templates=features_templates,
    )

    features.put(args.result_path)

    job.run()
