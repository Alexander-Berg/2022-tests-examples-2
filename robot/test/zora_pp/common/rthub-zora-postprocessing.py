#!/usr/bin/env python

import yatest.common
import logging
import os
import shutil
import tarfile

from os.path import join as pj
from robot.rthub.test.common.rthub_runner import RTHubRunner


THREADS_COUNT = 16


def copy_resources(dir, res_dir):
    for arc in os.listdir(dir):
        if '.tar' in arc:
            with tarfile.open(pj(dir, arc), 'r') as t:
                t.extractall(res_dir)
        else:
            if not os.path.exists(pj(res_dir, arc)):
                if os.path.isdir(pj(dir, arc)):
                    shutil.copytree(pj(dir, arc), pj(res_dir, arc))
                else:
                    shutil.copy(pj(dir, arc), pj(res_dir, arc))


def test_rthub_zora_postprocessing():
    os.environ['RTHUB_TEST_MODE'] = "true"

    logger = logging.getLogger("rthub_test_logger")

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/zora/conf/static/cloud/production/rthub_zora_pp_nocompress.config')
    resources_path_files = yatest.common.source_path('robot/zora/postprocessing/files')
    resources_path_build = yatest.common.build_path('robot/zora/postprocessing/files')
    udfs_path = yatest.common.build_path('robot/zora/postprocessing/udfs')
    proto_path = yatest.common.build_path('robot/zora/packages/protos')
    libraries_path = yatest.common.source_path('robot/zora/postprocessing/libraries_nocompress')
    queries_path = yatest.common.source_path('robot/zora/postprocessing/queries_nocompress')
    test_data = yatest.common.work_path('test_data')
    output = yatest.common.work_path('output')

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')

    # Gather resources
    res_dir = yatest.common.work_path('resources')
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)

    os.mkdir(yatest.common.work_path('resources'))
    copy_resources(resources_path_build, res_dir)
    copy_resources(resources_path_files, res_dir)

    rthub_runner = RTHubRunner(rthub_bin, orig_config, test_data, output)
    rthub_runner.set_env_variable('TEST_TIMESTAMP', "1552383263")
    rthub_runner.update_config(udfs_path, proto_path, res_dir, libraries_path, queries_path, THREADS_COUNT)
    rthub_runner.save_config()

    logger.info("Launching RTHub...")

    rthub_runner.run_rthub(binary=False)
    os.remove(yatest.common.work_path('output/--'))

    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner.get_config()], diff_tool_timeout=100)
