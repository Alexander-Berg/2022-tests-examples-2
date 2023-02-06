# coding=utf-8

import argparse
import datetime
import itertools

from nile.api.v1 import Record
from nile.api.v1 import aggregators as na
from nile.api.v1 import statface as ns
from qb2.api.v1 import filters as qf

import zoo.utils.nile_helpers.filters as zf
from zoo.nirvana_bucket_test.project_config import (
    get_project_cluster, STATFACE_PATH_TEMPLATE
)
from zoo.utils.time_helpers import argparse_date_tuple, parse_datetime
from zoo.utils.experiments_helpers.calculate_sr_tests_nv_wrapper import LOG_PATH


DELTA_DAYS = [1, 7, 14, 28]
DATE_FORMAT = '%Y-%m-%d'


def dt_range(start, end, step=datetime.timedelta(days=1)):
    date = start
    while date <= end:
        yield date
        date += step


class Events(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.dt_range = list(dt_range(self.start_date, self.end_date))

    def mapper(self, records):
        for record in records:
            rec_dt = parse_datetime(record.utc_start_date, format=DATE_FORMAT)
            for delta, report_dt in itertools.product(
                    DELTA_DAYS, self.dt_range
            ):
                if (report_dt - datetime.timedelta(days=delta) <
                        rec_dt <= report_dt):
                    yield Record(
                        record,
                        fielddate=report_dt.strftime(DATE_FORMAT),
                        n_observation_days=delta
                    )

    def __call__(self, job):
        return job.table(LOG_PATH).filter(
            qf.defined('utc_start_date'),
            qf.defined('block_code'),  # filter local debug
            zf.dttm_between(
                self.start_date - datetime.timedelta(days=max(DELTA_DAYS)),
                self.end_date,
                'utc_start_dttm'
            )
        ).project(
            'success',
            'owner',
            'duration',
            'utc_start_date'
        ).map(
            self.mapper
        ).groupby('fielddate', 'n_observation_days').aggregate(
            unique_users=na.count_distinct(
                'owner', in_memory=True, predicate=qf.defined('owner')
            ),
            success_count=na.count(predicate=qf.equals('success', True)),
            mean_success_duration=na.mean(
                'duration', predicate=qf.equals('success', True)
            ),
            median_success_duration=na.median_estimate(
                'duration', predicate=qf.equals('success', True)
            ),
            mean_fail_duration=na.mean(
                'duration', predicate=qf.equals('success', False)
            ),
            median_fail_duration=na.median_estimate(
                'duration', predicate=qf.equals('success', False)
            ),
            run_count=na.count()
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', type=argparse_date_tuple,
                        required=True)
    parser.add_argument('--end-date', type=argparse_date_tuple,
                        required=True)
    args = parser.parse_args()

    events = Events(args.start_date, args.end_date)

    statface_client = ns.StatfaceClient(proxy='upload.stat.yandex-team.ru')
    report = ns.StatfaceReport().path(
        STATFACE_PATH_TEMPLATE.format('usage_report')
    ).title(
        'Использование Bucket Test'
    ).scale('daily').dimensions(
        ns.Date('fielddate').replaceable(),
        ns.StringSelector('n_observation_days').replaceable()
    ).measures(
        ns.Number('unique_users'),
        ns.Number('success_count'),
        ns.Number('run_count'),
        ns.Float('mean_success_duration', precision=2),
        ns.Float('median_success_duration', precision=2),
        ns.Float('mean_fail_duration', precision=4),
        ns.Float('median_fail_duration', precision=4)
    ).client(statface_client)

    job = get_project_cluster().job()
    events(job).publish(report)
    job.run()


if __name__ == '__main__':
    main()
