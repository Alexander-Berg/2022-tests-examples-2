#!/usr/bin/env python

import yatest.common
import logging
import shutil
import tarfile
import os

from os.path import join as pj
from robot.rthub.test.common.rthub_runner import RTHubRunner


THREADS_COUNT = 16


def test_rthub_pages():
    os.environ['RTHUB_TEST_MODE'] = "true"

    logger = logging.getLogger("rthub_test_logger")

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/conf/conf-production/video-meta-fresh.pb.txt')
    resources_tar_path = yatest.common.build_path('robot/rthub/packages/resources/video-meta')
    udfs_path = yatest.common.build_path('robot/rthub/packages/full_video_meta_udfs')
    proto_path = yatest.common.build_path('robot/rthub/packages/full_web_protos')
    libraries_path = yatest.common.source_path('robot/rthub/yql/libraries')
    queries_path = yatest.common.source_path('robot/rthub/yql/queries')
    test_data = yatest.common.work_path('test_data')
    output = yatest.common.work_path('output')

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')

    # Gather resources
    res_dir = yatest.common.work_path('resources')
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)

    os.mkdir(yatest.common.work_path('resources'))
    for arc in os.listdir(resources_tar_path):
        if '.tar' in arc:
            with tarfile.open(pj(resources_tar_path, arc), 'r') as t:
                t.extractall(res_dir)
        else:
            shutil.copy(pj(resources_tar_path, arc), pj(res_dir, arc))

    rthub_runner = RTHubRunner(rthub_bin, orig_config, test_data, output)

    rthub_runner.update_config(udfs_path, proto_path, res_dir, libraries_path, queries_path, THREADS_COUNT)
    rthub_runner.save_config()

    logger.info("Launching RTHub...")

    rthub_runner.run_rthub(binary=False)

    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner.get_config()])
