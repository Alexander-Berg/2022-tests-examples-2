#!/usr/bin/env python

import yatest.common
import logging
import shutil
import os

from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.common.kikimr_runner import KikimrRunner
from robot.rthub.test.turbo.medium.turbo_test_lib import turbo_test


def test_rthub_turbo_pages():
    logger = logging.getLogger('rthub_test_logger')
    logger.info('rthub_test_turbo_pages')
    table_yql = yatest.common.source_path('robot/rthub/test/turbo/yql/table.yql')
    data_yql = yatest.common.work_path('test_data/data.yql')

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    parser_orig_config = yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-parser-worker.pb.txt')
    postprocess_orig_config = yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-postprocess-worker.pb.txt.gen')

    udfs_path = yatest.common.build_path('robot/rthub/packages/full_turbo_udfs')
    proto_path = yatest.common.build_path('robot/rthub/packages/full_web_protos')
    libraries_path = yatest.common.source_path('robot/rthub/yql/libraries')
    queries_path = yatest.common.source_path('robot/rthub/yql/queries')
    test_data = yatest.common.work_path('test_data')
    parser_output = yatest.common.work_path('parser_output')
    output = yatest.common.work_path('output')

    # Gather resources
    res_dir = yatest.common.work_path('resources')
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)

    os.mkdir(res_dir)
    turbo_test.unpack_standard_resources(res_dir)

    kikimr_runner = KikimrRunner(table_yql, data_yql)
    kikimr_runner.setup()

    try:
        logger.info("Running Parser RTHub...")
        rthub_runner_parser = RTHubRunner(rthub_bin, parser_orig_config, test_data, parser_output)
        rthub_runner_parser.update_config(udfs_path, proto_path, res_dir,
                                          libraries_path, queries_path, 6)

        rthub_runner_parser.set_env_variable('KIKIMR_PROXY', kikimr_runner.get_endpoint())
        rthub_runner_parser.set_env_variable('KIKIMR_DATABASE', "local")
        rthub_runner_parser.set_env_variable('MDS_INFO_TABLE', "MdsInfoTable")
        rthub_runner_parser.set_env_variable("AUTOPARSER_FLAGS_TABLE", "autoparser_flags")
        rthub_runner_parser.set_env_variable("FEED_HASHES_TABLE", "feed_hashes")
        rthub_runner_parser.set_env_variable("BUTTON_FILTER_TABLE", "top_filter")
        rthub_runner_parser.set_env_variable("YQL_CONFIG_NAME", "testing")
        rthub_runner_parser.set_env_variable("TEST_TIMESTAMP", "0")
        rthub_runner_parser.set_env_variable("YDB_CLIENT_TIMEOUT_MS", "300000")
        rthub_runner_parser.save_config()
        rthub_runner_parser.run_rthub(binary=False)

        logger.info("Running Postprocess RTHub...")
        rthub_runner_postprocess = RTHubRunner(rthub_bin, postprocess_orig_config, parser_output, output)
        rthub_runner_postprocess.update_config(udfs_path, proto_path, res_dir,
                                               libraries_path, queries_path, 6)
        rthub_runner_postprocess.set_env_variable('KIKIMR_PROXY', kikimr_runner.get_endpoint())
        rthub_runner_postprocess.set_env_variable('KIKIMR_DATABASE', "local")
        rthub_runner_postprocess.set_env_variable('MDS_INFO_TABLE', "MdsInfoTable")
        rthub_runner_postprocess.set_env_variable("AUTOPARSER_FLAGS_TABLE", "autoparser_flags")
        rthub_runner_postprocess.set_env_variable("FEED_HASHES_TABLE", "feed_hashes")
        rthub_runner_postprocess.set_env_variable("BUTTON_FILTER_TABLE", "top_filter")
        rthub_runner_postprocess.set_env_variable("YQL_CONFIG_NAME", "testing")
        rthub_runner_postprocess.set_env_variable("TEST_TIMESTAMP", "0")
        rthub_runner_postprocess.set_env_variable("REQUEST_IMAGE_RATIO", "1")
        rthub_runner_postprocess.set_env_variable("CMNT_HOSTS", "drive2.ru drive2.com povarenok.ru")
        rthub_runner_postprocess.set_env_variable("YDB_CLIENT_TIMEOUT_MS", "300000")
        rthub_runner_postprocess.save_config()
        rthub_runner_postprocess.run_rthub(binary=False)
    finally:
        kikimr_runner.stop()

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')

    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner_postprocess.get_config()])
