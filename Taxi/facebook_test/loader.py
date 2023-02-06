# coding: utf-8
from dmp_suite.task.cron import Cron
from dmp_suite.task.execution import run_task
from dmp_suite import datetime_utils as dtu

from dmp_suite.yt.task.etl import nile_transform, transform
from dmp_suite.scales import DayScale

from nile.api.v1 import aggregators as na

from .table import Dst


@nile_transform.nile_source(
    facebook=transform.ext_date_range(
        '//statbox/cube/daily/ads_groups/Mediaservices/facebook/v2',
        scale=DayScale(),
        date_formatter=dtu.format_date,
        period=transform.Period('2022-02-18', '2022-02-20')
    )
)
def prepare_fb(args, facebook):
    return facebook \
        .groupby('campaign_name') \
        .aggregate(
            cnt=na.count()
        )


facebook_transform = transform.replace_by_snapshot(
    'test_task',
    prepare_fb,
    Dst
).set_scheduler(
    Cron('0 12 * * *'),
)


if __name__ == '__main__':
    run_task(facebook_transform)
