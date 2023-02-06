#!/usr/bin/env python

import logging
import os
from os.path import join as pj
import pytest
import shutil
import tarfile
from robot.rthub.test.common.rthub_runner import RTHubRunner, RTHubPipelineRunner
import yatest.common

THREADS_COUNT = 16
logger = logging.getLogger("rthub_test")


@pytest.fixture(scope='module')  # noqa
def setup():
    arcadia_configs = [
        ('extsearch/video/robot/rthub/config/author_json_api', 'video_configs/author_json_api'),
        ('extsearch/video/robot/rthub/config/watson', 'video_configs/watson_parsers'),
        ('extsearch/video/robot/rthub/config/xpath_parser', 'video_configs/xpath_parser'),
        ('yweb/webscripts/video/canonize/config', 'video_configs/video_media_canonizer_configs'),
        ('yweb/webscripts/video/kiwi/videojsonapitrigger', 'video_configs/videojsonapitrigger'),
    ]

    # Gather resources
    resources_path = yatest.common.work_path('resources')
    if os.path.exists(resources_path):
        shutil.rmtree(resources_path)

    os.mkdir(resources_path)
    resources_tar_path = yatest.common.build_path('robot/rthub/packages/resources/pages')
    for arc in os.listdir(resources_tar_path):
        if '.tar' in arc:
            with tarfile.open(pj(resources_tar_path, arc), 'r') as t:
                t.extractall(resources_path)
        else:
            shutil.copy(pj(resources_tar_path, arc), pj(resources_path, arc))
    for src, dst in arcadia_configs:
        spath = pj(resources_path, dst)
        os.makedirs(os.path.basename(spath))
        shutil.copytree(yatest.common.source_path(src), spath)

    return {
        'resources_path': resources_path,
        'udfs_path': yatest.common.build_path('robot/rthub/packages/full_web_udfs'),
        'proto_path': yatest.common.build_path('robot/rthub/packages/full_web_protos'),
        'libraries_path': yatest.common.source_path('robot/rthub/yql/libraries'),
        'queries_path': yatest.common.source_path('robot/rthub/yql/queries'),
    }


def test_rthub_pages(setup):
    os.environ['RTHUB_TEST_MODE'] = "true"

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    orig_config = yatest.common.source_path('robot/rthub/conf/conf-production/pages.pb.txt')
    test_data = yatest.common.work_path('test_data')
    output = yatest.common.work_path('output')

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')

    rthub_runner = RTHubRunner(rthub_bin, orig_config, test_data, output)

    rthub_runner.update_config(setup['udfs_path'], setup['proto_path'], setup['resources_path'],
                               setup['libraries_path'], setup['queries_path'], THREADS_COUNT)
    rthub_runner.save_config()

    logger.info("Launching RTHub...")

    def set_path_env(key, value):
        os.environ[key] = os.path.join(setup['resources_path'], value)

    set_path_env("UDF_TMUCALC_DATA_PATH", "AntispamRules")
    set_path_env("UDF_DEDUCECALC_DATA_PATH", "AntispamRules")
    set_path_env("UDF_KEYWORD_EXTRACT_PURE_PATH", "pure")
    set_path_env("UDF_KEYWORD_EXTRACT_STOPWORD_PATH", "stopword.lst")
    set_path_env("UDF_KEYWORD_EXTRACT_MORPHFIXLIST_PATH", "morphfixlist.txt")
    set_path_env("UDF_DIRECTTEXT_PURE_PATH", "pure/pure.trie")
    set_path_env("UDF_DIRECTTEXT_CONFIG_PATH", "direct_text_config")
    set_path_env("UDF_DIRECTTEXT_SEOLNK_PATH", "seolnk")
    set_path_env("UDF_DSSM_OPT_RTHUB_MODEL_PATH", "WEB_RTHUB_OPTIMIZED_MODELS_DSSM_PACK/optimized_rthub_model.dssm")
    set_path_env("UDF_DSSM_BLENDER_NEWS_JUDGEMENT_PATH", "JUPITER_BLENDER_NEWS_JUDGEMENT")

    rthub_runner.run_rthub(binary=False)

    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner.get_config()], diff_tool_timeout=360)


@pytest.mark.parametrize('env', ['conf-production'])
def test_rthub_pages_cfg(setup, env):
    orig_config = yatest.common.source_path('robot/rthub/conf/{}/pages.pb.txt'.format(env))
    runner = RTHubPipelineRunner(orig_config)

    runner.update_config(setup['udfs_path'], setup['proto_path'], setup['resources_path'],
                         setup['libraries_path'], setup['queries_path'])
    runner.save_config()

    logger.info("Launching RTHubPipeline check for env {}".format(env))

    runner.run()
