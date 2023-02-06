#!/usr/bin/env python

import yatest.common
import logging
import shutil
import tarfile
import os
import pytest

from os.path import join as pj
from robot.rthub.test.common.rthub_runner import RTHubRunner


THREADS_COUNT = 16
logger = logging.getLogger("rthub_test_logger")


@pytest.fixture(scope='module')  # noqa
def setup():
    arcadia_configs = [
        ('yweb/webscripts/video/canonize/config', 'video_configs/video_media_canonizer_configs')
    ]

    # Gather resources
    resources_path = yatest.common.work_path('resources')
    if os.path.exists(resources_path):
        shutil.rmtree(resources_path)

    os.mkdir(resources_path)
    resources_tar_path = yatest.common.build_path('robot/rthub/packages/resources/sitemaps')
    for arc in os.listdir(resources_tar_path):
        if '.tar' in arc:
            with tarfile.open(pj(resources_tar_path, arc), 'r') as t:
                t.extractall(resources_path)
        else:
            shutil.copy(pj(resources_tar_path, arc), pj(resources_path, arc))
    for src, dst in arcadia_configs:
        os.makedirs(os.path.basename(pj(resources_path, dst)))
        shutil.copytree(yatest.common.source_path(src), pj(resources_path, dst))

    return {
        'resources_path': resources_path,
        'udfs_path': yatest.common.build_path('robot/rthub/packages/full_sitemaps_udfs'),
        'proto_path': yatest.common.build_path('robot/rthub/packages/full_web_protos'),
        'libraries_path': yatest.common.source_path('robot/rthub/yql/libraries'),
        'queries_path': yatest.common.source_path('robot/rthub/yql/queries'),
    }


def test_rthub_sitemaps(setup):
    os.environ['RTHUB_TEST_MODE'] = "true"

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/conf/conf-production/sitemaps.pb.txt')
    test_data = yatest.common.work_path('test_data')
    output = yatest.common.work_path('output')

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')

    rthub_runner = RTHubRunner(rthub_bin, orig_config, test_data, output)

    rthub_runner.update_config(setup['udfs_path'], setup['proto_path'], setup['resources_path'],
                               setup['libraries_path'], setup['queries_path'], THREADS_COUNT)
    rthub_runner.save_config()

    logger.info("Launching RTHub...")

    rthub_runner.run_rthub(binary=False)

    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner.get_config()], diff_tool_timeout=360)
