# coding: utf-8

import argparse

from nile.api.v1 import files as nfl
from zoo.eta.pin_correction.nirvana.utils import (
    dataset_mapper,
    mx_dataset_mapper,
)
from zoo.eta.project_config import get_project_cluster
from zoo.utils.nile_helpers import yt_path_join


def prepare_test_mx_data(job, yt_work_dir, yt_work_sub_dir, nz_path):

    nz_target = job.table(nz_path)
    cb_simple_table, cb_table = (
        job.table(yt_path_join(yt_work_dir, 'test_data'))
        .map(
            dataset_mapper, files=[nfl.StreamFile(nz_target, 'nz_base_table')],
        )
        .map(mx_dataset_mapper)
    )

    cb_simple_table.put(
        yt_path_join(yt_work_dir, yt_work_sub_dir, 'simple_dataset_cb'),
    )
    cb_table.put(yt_path_join(yt_work_dir, yt_work_sub_dir, 'dataset_cb'))

    return job


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--yt-work-dir', type=str, required=True)
    parser.add_argument('--yt-work-sub-dir', type=str, required=True)
    parser.add_argument('--nz-path', type=str, required=True)
    args = parser.parse_args()

    cluster = get_project_cluster()
    job = cluster.job('Pin ETA: prepare test data')
    job = prepare_test_mx_data(
        job=job,
        yt_work_dir=args.yt_work_dir,
        yt_work_sub_dir=args.yt_work_sub_dir,
        nz_path=args.nz_path,
    )
    job.run()
