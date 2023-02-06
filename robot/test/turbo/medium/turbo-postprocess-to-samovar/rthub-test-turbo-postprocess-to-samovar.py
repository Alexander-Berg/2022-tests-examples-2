#!/usr/bin/env python

import yatest.common
import logging
import shutil
import tempfile
import os

import google.protobuf.text_format as text_format

from os.path import join as pj
from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.common.kikimr_runner import KikimrRunner
from robot.rthub.yql.protos.content_plugins_pb2 import TContentPluginsResult
from robot.protos.crawl.compatibility.feeds_pb2 import TFeedExt
from robot.rthub.test.turbo.medium.turbo_test_lib import turbo_test


def test_rthub_turbo_postprocess_to_samovar(links):
    logger = logging.getLogger('rthub_test_logger')
    logger.info('test_rthub_turbo_samovarfeed_output')
    table_yql = yatest.common.source_path('robot/rthub/test/turbo/yql/table.yql')
    test_data = yatest.common.work_path('test_data')
    empty_data_yql = tempfile.NamedTemporaryFile(prefix="empty_data", dir=test_data, suffix=".yql")

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    postprocess_orig_config = yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-postprocess-worker.pb.txt.gen')

    udfs_path = yatest.common.build_path('robot/rthub/packages/full_turbo_udfs')
    proto_path = yatest.common.build_path('robot/rthub/packages/full_web_protos')
    libraries_path = yatest.common.source_path('robot/rthub/yql/libraries')
    queries_path = yatest.common.source_path('robot/rthub/yql/queries')
    output1 = yatest.common.work_path('output/1')
    output2 = yatest.common.work_path('output/2')

    # input feed
    json_input_dir_1 = yatest.common.work_path('test_samovar_input/1')
    urls_for_launch_1 = [
        _get_content_plugin_result_with_url_source("https://www.test-url-1-rss.ru/", 0),                # OK
        _get_content_plugin_result_with_url_source("https://www.test-url-2-api.ru/", 1),                # OK
        _get_content_plugin_result_with_url_source("https://www.test-url-3-api-debug.ru/", 2),          # BAD, EFS_API_DEBUG
        _get_content_plugin_result_with_url_source("https://www.test-url-4-autoparser.ru/", 3),         # BAD, EFS_AUTOPARSER
        _get_content_plugin_result_with_url_source("https://www.test-url-5-autoparser-button.ru/", 4),  # BAD, EFS_AUTOPARSER_BUTTON
        _get_content_plugin_result_with_url_source("https://www.test-url-6-yml.ru/", 5),                # OK
    ]
    _write_items_to_input_feed(json_input_dir_1, urls_for_launch_1)

    json_input_dir_2 = yatest.common.work_path('test_samovar_input/2')
    urls_for_launch_2 = [
        _get_content_plugin_result_with_url_source("https://www.test-url-1-rss.ru/", 0),        # BAD, already viewed
        _get_content_plugin_result_with_url_source("https://www.test-url-7-yml.ru/", 5),        # OK
        _get_content_plugin_result_with_url_source(
            "https://www.test-url-8-yml.ru/", 5, attempts_count=1),                             # BAD, attempts_count > 0
    ]
    _write_items_to_input_feed(json_input_dir_2, urls_for_launch_2)

    expected_output_after_first_launch = [
        ("https://www.test-url-1-rss.ru/", "turbo-url-from-rss"),
        ("https://www.test-url-2-api.ru/", "turbo-url-from-rss"),
        ("https://www.test-url-6-yml.ru/", "turbo-url-from-yml")
    ]
    expected_output_after_second_launch = [
        ("https://www.test-url-7-yml.ru/", "turbo-url-from-yml")
    ]

    # Gather resources
    res_dir = yatest.common.work_path('resources')
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)

    os.mkdir(res_dir)
    turbo_test.unpack_standard_resources(res_dir)

    kikimr_runner = KikimrRunner(table_yql, empty_data_yql.name)
    kikimr_runner.setup()

    try:
        logger.info("Running Postprocess RTHub #1 ...")
        rthub_runner_postprocess = RTHubRunner(rthub_bin, postprocess_orig_config, json_input_dir_1, output1)
        rthub_runner_postprocess.update_config(udfs_path, proto_path, res_dir,
                                               libraries_path, queries_path, 6)
        rthub_runner_postprocess.set_env_variable('KIKIMR_PROXY', kikimr_runner.get_endpoint())
        rthub_runner_postprocess.set_env_variable('KIKIMR_DATABASE', "local")
        rthub_runner_postprocess.set_env_variable('MDS_INFO_TABLE', "mds")
        rthub_runner_postprocess.set_env_variable("AUTOPARSER_FLAGS_TABLE", "autoparser_flags")
        rthub_runner_postprocess.set_env_variable("FEED_HASHES_TABLE", "feed_hashes")
        rthub_runner_postprocess.set_env_variable("BUTTON_FILTER_TABLE", "top_filter")
        rthub_runner_postprocess.set_env_variable("YQL_CONFIG_NAME", "testing")
        rthub_runner_postprocess.set_env_variable("TEST_TIMESTAMP", "0")
        rthub_runner_postprocess.save_config()
        rthub_runner_postprocess.run_rthub(binary=False)

        logger.info("Running Postprocess RTHub #2...")
        rthub_runner_postprocess = RTHubRunner(rthub_bin, postprocess_orig_config, json_input_dir_2, output2)
        rthub_runner_postprocess.update_config(udfs_path, proto_path, res_dir,
                                               libraries_path, queries_path, 6)
        rthub_runner_postprocess.set_env_variable('KIKIMR_PROXY', kikimr_runner.get_endpoint())
        rthub_runner_postprocess.set_env_variable('KIKIMR_DATABASE', "local")
        rthub_runner_postprocess.set_env_variable('MDS_INFO_TABLE', "mds")
        rthub_runner_postprocess.set_env_variable("AUTOPARSER_FLAGS_TABLE", "autoparser_flags")
        rthub_runner_postprocess.set_env_variable("FEED_HASHES_TABLE", "feed_hashes")
        rthub_runner_postprocess.set_env_variable("BUTTON_FILTER_TABLE", "top_filter")
        rthub_runner_postprocess.set_env_variable("YQL_CONFIG_NAME", "testing")
        rthub_runner_postprocess.set_env_variable("TEST_TIMESTAMP", "0")
        rthub_runner_postprocess.save_config()
        rthub_runner_postprocess.run_rthub(binary=False)
    finally:
        kikimr_runner.stop()

    actual_output_after_first_launch = _get_items_from_output(output1)
    actual_output_after_second_launch = _get_items_from_output(output2)

    assert actual_output_after_first_launch == expected_output_after_first_launch
    assert actual_output_after_second_launch == expected_output_after_second_launch


def _get_items_from_output(output_path):
    feed_output_path = pj(output_path, "samovar--feeds-ext")
    with open(feed_output_path, "r") as f:
        actual_output = []
        text = f.read()
        for item in text.split('===\n'):
            if item:
                feed_item = text_format.Parse(item, TFeedExt())
                actual_output.append((feed_item.Url, feed_item.FeedName))
    return sorted(actual_output, key=lambda x: x[0])


def _get_content_plugin_result_with_url_source(url, source, attempts_count=0):
    return TContentPluginsResult(Url=url,
                                 SaasKey=url,
                                 ItemSource=source,
                                 SaasAction="atModify",
                                 LastAccess=1536750972,
                                 Error="",
                                 Hash="890aeb37ecccb8a4c39ec2559afce95c",
                                 SaasTs=1536750972,
                                 DocumentErrors="[]",
                                 FeedUrl="41987d80-b67d-11e8-8047-63697acfe6bf",
                                 SamovarImageFeedName="images-turbo-api|images-turbo-api-fill-consumer|images-turbo-api-fast",
                                 Title="TITLE",
                                 ParserFinishTime=0,
                                 Json="[]",
                                 AttemptsCount=attempts_count
                                 )


def _write_items_to_input_feed(dir, items):
    res = "===\n".join([str(x) for x in items])

    os.makedirs(dir)
    filename = pj(dir, "rthub--turbo-json")
    with(open(filename, 'w+')) as f:
        f.write(res)
