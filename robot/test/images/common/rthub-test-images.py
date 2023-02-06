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
from robot.rthub.test.common.mds_runner import MdsRunner, MdsImagesMainMockHandler

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

    avatars_upload_path = 'robot/rthub/yql/udfs/images_pic/avatars_upload/'
    images_upload_config_resource = (
        yatest.common.source_path(avatars_upload_path + 'avatars_images_main_thumbs_test.conf'),
        resources_path + "/" + 'avatars_images_main_thumbs.conf'
    )
    gif_upload_config_resource = (
        yatest.common.source_path(avatars_upload_path + 'avatars_gif_test.conf'),
        resources_path + "/" + 'avatars_gif.conf'
    )
    datacamp_upload_config_resource = (
        resources_path + "/" + 'mds_datacamp_test.conf',
        resources_path + "/" + 'mds_datacamp_test.conf',
    )

    source_resources_path = [images_upload_config_resource, gif_upload_config_resource, datacamp_upload_config_resource]
    mds_runner = MdsRunner(handler_class=MdsImagesMainMockHandler)
    port_number = str(mds_runner.mds_server_port())

    for res, dest in source_resources_path:
        # Fill images upload config with params
        with open(res, 'r') as f:
            upload_config = f.read()

        if '__port__' in upload_config:
            upload_config = re.sub(r'__port__', port_number, upload_config)
        else:
            upload_config = re.sub(r'Namespace', 'Port: %s\n    Namespace' % port_number, upload_config)

        if os.path.isfile(dest):
            os.chmod(dest, 0o777)
        with open(dest, 'w') as f:
            f.write(upload_config)

    yield {
        'resources_path': resources_path,
        'udfs_path': yatest.common.build_path('robot/rthub/packages/full_images_udfs'),
        'proto_path': yatest.common.build_path('robot/rthub/packages/full_web_protos'),
        'libraries_path': yatest.common.source_path('robot/rthub/yql/libraries'),
        'queries_path': yatest.common.source_path('robot/rthub/yql/queries'),
        'mds_runner': mds_runner
    }

    mds_runner.shutdown_mds_server()


def test_rthub_images(setup):
    os.environ['RTHUB_TEST_MODE'] = "true"
    os.environ['MDS_URL'] = "localhost:13000"

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/conf/conf-production/images.pb.txt')
    test_data = yatest.common.work_path('test_data')
    output = yatest.common.work_path('output')

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')

    rthub_runner = RTHubRunner(rthub_bin, orig_config, test_data, output)

    rthub_runner.update_config(setup['udfs_path'], setup['proto_path'], setup['resources_path'],
                               setup['libraries_path'], setup['queries_path'], THREADS_COUNT)

    rthub_runner.save_config()
    setup['mds_runner'].startup_mds_server()

    logger.info("Launching RTHub...")

    rthub_runner.run_rthub(binary=True)

    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner.get_config(), "--use-binary-format"])


@pytest.mark.parametrize('env',
                         ['conf-prestable', 'conf-production'])
def test_rthub_images_cfg(setup, env):
    orig_config = yatest.common.source_path('robot/rthub/conf/{}/images.pb.txt'.format(env))
    runner = RTHubPipelineRunner(orig_config)

    runner.update_config(setup['udfs_path'], setup['proto_path'], setup['resources_path'],
                         setup['libraries_path'], setup['queries_path'])
    runner.save_config()

    logger.info("Launching RTHubPipeline check for env {}".format(env))

    runner.run()
