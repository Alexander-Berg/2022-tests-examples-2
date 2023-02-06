#!/usr/bin/env python

import yatest.common
import logging
import shutil
import tarfile
import os
import copy

from os.path import join as pj
from robot.rthub.protos.config_pb2 import TConfig
from robot.rthub.test.common.rthub_runner import RTHubRunner
import google.protobuf.text_format as pbtext


THREADS_COUNT = 16


def _read_config(conf_path):
    config = TConfig()
    with open(conf_path, 'r') as f:
        pbtext.Parse(f.read(), config)
    return config


def patch_config(conf, dest):
    config = _read_config(conf)
    channel = copy.copy(config.Channel[0])
    for proto_in in channel.Input:
        if proto_in.Source.Ident == 'zora':
            proto_in.ClearField('Yql')
        proto_in.Source.Ident = 'kwyt-' + proto_in.Source.Ident
        config.Channel[0].Input.extend([proto_in])
    open(dest, 'w').write(pbtext.MessageToString(config))


def test_rthub_pages():
    os.environ['RTHUB_TEST_MODE'] = "true"

    logger = logging.getLogger("rthub_test_logger")

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/conf/conf-production/pages.pb.txt')
    resources_tar_path = yatest.common.build_path('robot/rthub/packages/resources/pages')
    udfs_path = yatest.common.build_path('robot/rthub/packages/full_web_udfs')
    proto_path = yatest.common.build_path('robot/rthub/packages/full_web_protos')
    libraries_path = yatest.common.source_path('robot/rthub/yql/libraries')
    queries_path = yatest.common.source_path('robot/rthub/yql/queries')
    test_data = yatest.common.work_path('test_data')
    output = yatest.common.work_path('output')

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')

    arcadia_configs = [
        ('extsearch/video/robot/rthub/config/author_json_api', 'video_configs/author_json_api'),
        ('extsearch/video/robot/rthub/config/watson', 'video_configs/watson_parsers'),
        ('extsearch/video/robot/rthub/config/xpath_parser', 'video_configs/xpath_parser'),
        ('yweb/webscripts/video/canonize/config', 'video_configs/video_media_canonizer_configs'),
        ('yweb/webscripts/video/kiwi/videojsonapitrigger', 'video_configs/videojsonapitrigger'),
    ]

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
    for src, dst in arcadia_configs:
        spath = pj(res_dir, dst)
        os.makedirs(os.path.basename(spath))
        shutil.copytree(yatest.common.source_path(src), spath)

    patched_config = yatest.common.work_path('patched_pages.pb.txt')
    patch_config(orig_config, patched_config)
    rthub_runner = RTHubRunner(rthub_bin, patched_config, test_data, output)
    rthub_runner.update_config(udfs_path, proto_path, res_dir, libraries_path, queries_path, THREADS_COUNT)
    rthub_runner.save_config()

    logger.info("Launching RTHub...")

    rthub_runner.run_rthub(binary=False)
    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner.get_config()])
