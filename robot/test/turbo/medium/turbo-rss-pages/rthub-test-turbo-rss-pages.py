#!/usr/bin/env python
from __future__ import print_function

import yatest.common
import logging
import shutil
import os
import json

from os.path import join as pj
from shutil import copyfile
from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.common.kikimr_runner import KikimrRunner
from robot.rthub.test.turbo.medium.turbo_test_lib import turbo_test
from robot.rthub.yql.protos.queries_pb2 import TTurboRSSItem
from robot.rthub.yql.protos.content_plugins_pb2 import TContentPluginsResult
from robot.protos.crawl.zoracontext_pb2 import TUkropZoraContext
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from quality.functionality.turbo.protos.turbo_context_pb2 import (
    EFeedSource,
    EFeedOrigin,
)


def test_skip_empty_turbo_context():
    def _create_document(add_context):
        doc = TTurboRSSItem()
        doc.Url = "https://good-site.test"
        doc.HttpCode = 200
        doc.LastAccess = 123445
        if add_context:
            zora_ctx = TUkropZoraContext()
            turbo_ctx = zora_ctx.TurboContext
            turbo_ctx.FeedOrigin = EFeedOrigin.Value("EFO_WMC")
            turbo_ctx.FeedSource = EFeedSource.Value("EFS_RSS")
            doc.ZoraCtx = zora_ctx.SerializeToString()
        doc.Content = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n
            <rss    xmlns:yandex=\"http://news.yandex.ru\"    xmlns:media=\"http://search.yahoo.com/mrss/\" xmlns:turbo=\"http://turbo.yandex.ru\" version=\"2.0\">
                <channel>
                <turbo:cms_plugin>C125AEEC6018B4A0EF9BF40E6615DD17</turbo:cms_plugin>
                    <title>title</title>
                    <link>https://good-site.test</link>
                    <description>desc</description>
                    <language>ru</language>
                    <item turbo=\"true\">
                        <title>title</title>
                        <link>https://good-site.test/0</link>
                        <turbo:topic>topic</turbo:topic>
                        <turbo:source>https://good-site.test/feed/rss/</turbo:source>
                        <turbo:content>
                            <![CDATA[<sender>John Smith</sender>]]>
                        </turbo:content>
                    </item>
                </channel>
            </rss>"""
        return doc
    docs = [_create_document(True), _create_document(False)]
    with TurboTest(output=yatest.common.work_path('test_skip_empty_turbo_context'), test_data=yatest.common.work_path('test_data_context')) as turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-rss"))
        turbo_test.unpack_resources(yatest.common.work_path('.'), turbo_test.resources_dir)
        turbo_test.unpack_resources(yatest.common.build_path('robot/rthub/packages/resources/saas'), pj(turbo_test.resources_dir, 'saas'))
        turbo_test.unpack_resources(yatest.common.source_path('robot/rthub/packages/resources/turbo-pages'), turbo_test.resources_dir)
        # ACT
        turbo_test.run_rthub_parser()

    documents = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)
    assert len(documents) == 1

    document_error = [error["code"] for error in json.loads(documents[0].DocumentErrors)]
    assert len(document_error) == 0

    # fix for the next test
    os.remove(pj(turbo_test.output, "rthub-turbo--turbo-documents"))
    os.remove(pj(turbo_test.output, "rthub--turbo-json"))


def _patch_docs(test_data):
    out_folder = pj(test_data, "patched_data")
    os.mkdir(out_folder)

    copyfile(pj(test_data, 'data.yql'), pj(out_folder, 'data.yql'))
    copyfile(pj(test_data, 'turbo--turbo-pages-api-log'), pj(out_folder, 'turbo--turbo-pages-api-log'))
    copyfile(pj(test_data, 'zora--commodity-feeds'), pj(out_folder, 'zora--commodity-feeds'))

    # add turbo context to the documents because it is required to parse a feed
    docs_src = turbo_test.TurboTest.restore_pb_from_file(pj(test_data, 'rthub--turbo-rss'), TTurboRSSItem)
    docs_dst = []
    for doc in docs_src:
        zora_ctx = TUkropZoraContext()
        zora_ctx.ParseFromString(doc.ZoraCtx)
        turbo_ctx = zora_ctx.TurboContext
        if turbo_ctx.ByteSize() == 0:
            turbo_ctx.FeedSource = EFeedSource.Value("EFS_RSS")
            turbo_ctx.FeedOrigin = EFeedOrigin.Value("EFO_WMC")
            doc.ZoraCtx = zora_ctx.SerializeToString()
        docs_dst.append(doc)
    turbo_test.TurboTest.save_pb_to_file(docs_dst, pj(out_folder, 'rthub--turbo-rss'))

    return out_folder


def test_rthub_turbo_rss_pages(links):
    logger = logging.getLogger('rthub_test_logger')
    logger.info('rthub_test_turbo_pages')
    table_yql = yatest.common.source_path('robot/rthub/test/turbo/yql/table.yql')

    test_data = _patch_docs(yatest.common.work_path('test_data'))
    data_yql = pj(test_data, 'data.yql')

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')

    parser_orig_config = yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-rss-parser-worker.pb.txt')
    postprocess_orig_config = yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-postprocess-worker.pb.txt.gen')

    udfs_path = yatest.common.build_path('robot/rthub/packages/full_turbo_udfs')
    proto_path = yatest.common.build_path('robot/rthub/packages/full_web_protos')
    libraries_path = yatest.common.source_path('robot/rthub/yql/libraries')
    queries_path = yatest.common.source_path('robot/rthub/yql/queries')
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
        rthub_runner_parser.set_env_variable('MDS_INFO_TABLE', "mds")
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
        rthub_runner_postprocess.set_env_variable('MDS_INFO_TABLE', "mds")
        rthub_runner_postprocess.set_env_variable("AUTOPARSER_FLAGS_TABLE", "autoparser_flags")
        rthub_runner_postprocess.set_env_variable("FEED_HASHES_TABLE", "feed_hashes")
        rthub_runner_postprocess.set_env_variable("BUTTON_FILTER_TABLE", "top_filter")
        rthub_runner_postprocess.set_env_variable("YQL_CONFIG_NAME", "testing")
        rthub_runner_postprocess.set_env_variable("TEST_TIMESTAMP", "0")
        rthub_runner_postprocess.set_env_variable("YDB_CLIENT_TIMEOUT_MS", "300000")
        rthub_runner_postprocess.save_config()
        rthub_runner_postprocess.run_rthub(binary=False)
    finally:
        kikimr_runner.stop()

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')
    return {
        # 'rss_parser': yatest.common.canonical_dir(parser_output, diff_tool=[diff_tool, "--config", rthub_runner_parser.get_config()]),
        'postprocess': yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner_postprocess.get_config()]),
    }
