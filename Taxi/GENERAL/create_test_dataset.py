# coding=utf-8

import os

from zoo.utils.nile_helpers import configure_environment

from zoo.suggest.nirvana.common import (
    get_dates,
    create_dataset,
    get_config,
    table_for_nirvana
)
from zoo.suggest.v2.common import hahn_main


def configure_job(job):
    job = configure_environment(job, add_taxi_ml_cxx=True)

    config = get_config()
    dates = get_dates()

    working_dir = config['train_config']['working_dir']
    orders_table_path = os.path.join(working_dir, 'orders')

    test_table_path = table_for_nirvana(working_dir, 'test_mx_ops_dataset')

    test_dataset_table = create_dataset(
        config,
        orders_table=job.table(orders_table_path),
        date_start=dates["dt_test_start"],
        date_finish=dates["dt_to"],
        is_for_train=False,
    )
    test_dataset_table.put(test_table_path)
    return job


if __name__ == '__main__':
    hahn_main(configure_job)
