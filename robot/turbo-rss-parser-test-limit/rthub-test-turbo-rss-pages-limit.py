#!/usr/bin/env python

import yatest.common
import logging
import shutil
import os


import google.protobuf.text_format as text_format

from os.path import join as pj
from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.common.kikimr_runner import KikimrRunner
from robot.rthub.test.turbo.medium.turbo_test_lib import turbo_test

from robot.rthub.yql.protos import content_plugins_pb2


def test_rthub_turbo_rss_parser(links):
    logger = logging.getLogger('rthub_test_logger')
    logger.info('rthub_test_turbo_pages')
    table_yql = yatest.common.source_path('robot/rthub/test/turbo/yql/table.yql')
    test_data = yatest.common.work_path('test_data')
    data_yql = pj(test_data, 'data.yql')

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    parser_orig_config = yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-rss-parser-worker.pb.txt')

    udfs_path = yatest.common.build_path('robot/rthub/packages/full_turbo_udfs')
    proto_path = yatest.common.build_path('robot/rthub/packages/full_web_protos')
    libraries_path = yatest.common.source_path('robot/rthub/yql/libraries')
    queries_path = yatest.common.source_path('robot/rthub/yql/queries')
    parser_output = yatest.common.work_path('parser_output')

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
        rthub_runner_parser.set_env_variable('MDS_INFO_TABLE', "mds")
        rthub_runner_parser.set_env_variable("AUTOPARSER_FLAGS_TABLE", "autoparser_flags")
        rthub_runner_parser.set_env_variable("FEED_HASHES_TABLE", "feed_hashes")
        rthub_runner_parser.set_env_variable("BUTTON_FILTER_TABLE", "top_filter")
        rthub_runner_parser.set_env_variable("YQL_CONFIG_NAME", "testing")
        rthub_runner_parser.set_env_variable("USE_JSON_COMPRESSION", "false")
        rthub_runner_parser.set_env_variable("TEST_TIMESTAMP", "0")
        rthub_runner_parser.save_config()
        rthub_runner_parser.run_rthub(binary=False)
    finally:
        kikimr_runner.stop()

    expected_doc_errors = [('api.good-feed-count.with-1000.com/feed', '[]'),
                           ('api.10000limit.exceeded.with-10001.com/feed',
                            '[{"code":"Fetch.QuotaExceeded.Items","current":10001,"quota":10000}]'),

                           ('api-debug.good-feed-count.with-30.com/feed', '[]'),
                           ('api-debug.50limit.exceeded.with-51.com/feed',
                            '[{"code":"Fetch.QuotaExceeded.Items","current":51,"quota":50}]'),

                           ('rss.good-feed-count.with-50.com/feed', '[]'),
                           ('rss.10000hardlimit.exceeded.with-10001.com/feed',
                            '[{"code":"Fetch.QuotaExceeded.Items","current":10001,"quota":1000}]'),
                           ('rss.1000softlimit.exceeded.with-1001.com/feed', '[{"code":"Fetch.QuotaExceeded.Items","current":1001,"quota":1000}]')]
    expected_doc_errors.sort(key=lambda x: x[0])

    expected_doc_items_count = [('api-debug.50limit.exceeded.with-51.com/feed', 50),
                                ('api-debug.good-feed-count.with-30.com/feed', 30),

                                ('api.10000limit.exceeded.with-10001.com/feed', 10000),
                                ('api.good-feed-count.with-1000.com/feed', 1000),

                                ('rss.10000hardlimit.exceeded.with-10001.com/feed', 10000),  # When hard limit exceeded, new items does't append to result
                                ('rss.1000softlimit.exceeded.with-1001.com/feed', 1001),
                                ('rss.good-feed-count.with-50.com/feed', 50)]
    expected_doc_items_count.sort(key=lambda x: x[0])

    actual_doc_errors = []
    with open(pj(parser_output, "rthub-turbo--turbo-documents"), 'r') as f:
        items = f.read().split("===\n")
        for item in items:
            if not item:
                break
            doc = text_format.Parse(item, content_plugins_pb2.TProcessingDocument())
            actual_doc_errors.append((doc.Feed, doc.Errors))
    actual_doc_errors.sort(key=lambda x: x[0])

    actual_doc_items_count = {}
    with open(pj(parser_output, "rthub--turbo-json"), 'r') as f:
        items = f.read().split("===\n")
        for item in items:
            if not item:
                break
            doc = text_format.Parse(item, content_plugins_pb2.TContentPluginsResult())
            actual_doc_items_count[doc.FeedUrl] = actual_doc_items_count.get(doc.FeedUrl, 0) + 1
    actual_doc_items_count = actual_doc_items_count.items()
    actual_doc_items_count.sort(key=lambda x: x[0])

    assert expected_doc_errors == actual_doc_errors
    assert expected_doc_items_count == actual_doc_items_count
