#!/usr/bin/env python

import yatest.common
import logging
import pytest
import shutil
import tarfile
import os
import re

from os.path import join as pj
from robot.rthub.test.common.rthub_runner import RTHubRunner, RTHubPipelineRunner
from robot.rthub.test.common.mds_runner import MdsRunner, MdsImagesFreshMockHandler

THREADS_COUNT = 16
logger = logging.getLogger("rthub_test")


@pytest.fixture(scope='module')  # noqa
def setup():
    # Gather resources
    resources_path = yatest.common.work_path('resources')
    if os.path.exists(resources_path):
        shutil.rmtree(resources_path)

    os.mkdir(resources_path)
    resources_tar_path = yatest.common.build_path('robot/rthub/packages/resources/images')
    for arc in os.listdir(resources_tar_path):
        if '.tar' in arc:
            with tarfile.open(pj(resources_tar_path, arc), 'r') as t:
                t.extractall(resources_path)
        else:
            shutil.copy(pj(resources_tar_path, arc), pj(resources_path, arc))

    images_upload_config_resource = (
        yatest.common.source_path('robot/rthub/yql/udfs/images_pic/avatars_upload/avatars_images_quick_test.conf'),
        resources_path + "/" + 'avatars_images_quick.conf'
    )
    source_resources_path = [images_upload_config_resource]
    for res, dest in source_resources_path:
        shutil.copy(res, dest)

    mds_runner = MdsRunner(handler_class=MdsImagesFreshMockHandler)

    # Fill images upload config with params
    with open(images_upload_config_resource[1], 'r') as f:
        images_upload_config = f.read()

    images_upload_config = re.sub(r'__port__', str(mds_runner.mds_server_port()), images_upload_config)

    os.chmod(images_upload_config_resource[1], 0o777)

    with open(images_upload_config_resource[1], 'w') as f:
        f.write(images_upload_config)

    yield {
        'resources_path': resources_path,
        'udfs_path': yatest.common.build_path('robot/rthub/packages/full_images_udfs'),
        'proto_path': yatest.common.build_path('robot/rthub/packages/full_web_protos'),
        'libraries_path': yatest.common.source_path('robot/rthub/yql/libraries'),
        'queries_path': yatest.common.source_path('robot/rthub/yql/queries'),
        'mds_runner': mds_runner
    }

    mds_runner.shutdown_mds_server()


def test_rthub_images_fresh(setup):
    os.environ['RTHUB_TEST_MODE'] = "true"
    os.environ['TVM_DAEMON_PORT'] = open("tvmtool.port").read()
    os.environ['QLOUD_TVM_TOKEN'] = open("tvmtool.authtoken").read()

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/conf/conf-production/images-fresh.pb.txt')
    test_data = yatest.common.work_path('test_data')
    output = yatest.common.work_path('output')

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')

    rthub_runner = RTHubRunner(rthub_bin, orig_config, test_data, output)

    rthub_runner.update_config(setup['udfs_path'], setup['proto_path'], setup['resources_path'],
                               setup['libraries_path'], setup['queries_path'], THREADS_COUNT)

    rthub_runner.save_config()
    setup['mds_runner'].startup_mds_server()

    logger.info("Launching RTHub...")

    rthub_runner.run_rthub(binary=False)

    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner.get_config()])


@pytest.mark.parametrize('env',
                         ['conf-prestable', 'conf-production'])
def test_rthub_images_fresh_cfg(setup, env):
    orig_config = yatest.common.source_path('robot/rthub/conf/{}/images-fresh.pb.txt'.format(env))
    runner = RTHubPipelineRunner(orig_config)

    runner.update_config(setup['udfs_path'], setup['proto_path'], setup['resources_path'],
                         setup['libraries_path'], setup['queries_path'])
    runner.save_config()

    logger.info("Launching RTHubPipeline check for env {}".format(env))

    runner.run()
