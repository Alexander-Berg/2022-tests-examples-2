# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import datetime as dt

from nile.api.v1 import clusters
from nile.api.v1 import extractors as ne

from zoo.drivers.metrics.calculate_metrics import calculate_metrics, configure_job
from zoo.drivers.metrics.tables import dim_driver
from zoo.utils.nile_helpers import configure_environment
from zoo.utils.nile_helpers import get_requirement


def prepare_environment(obj):
    return configure_environment(obj)


def get_project_cluster(pool=None, proxy='hahn.yt.yandex.net'):
    cluster = clusters.yql.YQL(pool=pool, proxy=proxy, yql_proxy='yql.yandex.net')
    
    return prepare_environment(cluster)


def main():
    cluster = get_project_cluster()
    job = cluster.job()
    date = dt.datetime(2019, 10, 1)
    configure_job(job, (date, date))
    drivers = dim_driver(job).project(
        ne.all(),
        datetime=ne.const(str(date))
    )
    
    calculate_metrics(
        drivers,
        'unique_driver_id',
        ['target_n_orders_7', 'duration_sec_7']
    ).put('//home/taxi_ml/dev/driver_target/test_metrics')
    
    job.run()


if __name__ == '__main__':
    main()
