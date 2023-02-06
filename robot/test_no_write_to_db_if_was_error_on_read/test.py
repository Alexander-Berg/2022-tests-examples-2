#!/usr/bin/env python

import yatest.common
import shutil
from os.path import join as pj
import os

from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.queries_pb2 import TTurboRSSItem
from robot.protos.crawl.zoracontext_pb2 import TUkropZoraContext
from quality.functionality.turbo.protos.turbo_context_pb2 import (
    EFeedOrigin,
    EFeedSource,
)


def test_rthub_turbo_rss_parser_with_db_error(links):
    # ARRANGE
    custom_libraries_path = yatest.common.work_path("libraries")
    shutil.copytree(yatest.common.source_path('robot/rthub/yql/libraries'), custom_libraries_path)
    _extend_utils_sql(custom_libraries_path)

    docs = [
        _create_document("https://throw-error.test"),  # Не должно писаться в базу, так как будет ошибка при чтении из базы
        _create_document("https://good-site.test")]

    expected_feed_hashes_urls = ['https://good-site.test']

    with TurboTest(libraries_path=custom_libraries_path) as turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-rss"))

        turbo_test.unpack_resources(yatest.common.work_path('.'), turbo_test.resources_dir)
        turbo_test.unpack_resources(yatest.common.build_path('robot/rthub/packages/resources/saas'), pj(turbo_test.resources_dir, 'saas'))
        turbo_test.unpack_resources(yatest.common.source_path('robot/rthub/packages/resources/turbo-pages'), turbo_test.resources_dir)

        # ACT
        turbo_test.run_rthub_parser()

        feed_hashes_db = turbo_test.kikimr_runner._driver.table_client.session().create().transaction().execute("SELECT * from feed_hashes", commit_tx=True)[0].rows
        feed_hashes_urls = [i.Url for i in feed_hashes_db]

    # ASSERT
    assert expected_feed_hashes_urls == feed_hashes_urls


def _extend_utils_sql(libraries_path):
    file_name = pj(libraries_path, "Utils.sql")
    os.chmod(file_name, 0o777)
    with open(file_name, 'a') as fileto:
        with open(yatest.common.source_path("robot/rthub/test/turbo/medium/parser-dberror/Utils.sql"), 'r') as filefrom:
            fileto.write(filefrom.read())


def _create_document(url):
    doc = TTurboRSSItem()
    doc.Url = url
    doc.HttpCode = 200
    doc.LastAccess = 123445
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
                <link>"+url+"</link>
                <description>desc</description>
                <language>ru</language>
                <item turbo=\"true\">
                    <title>title</title>
                    <link>"+url+"/0</link>
                    <turbo:topic>topic</turbo:topic>
                    <turbo:source>"+url+"/feed/rss/</turbo:source>
                    <turbo:content>
                        <![CDATA[<sender>John Smith</sender>]]>
                    </turbo:content>
                </item>
            </channel>
        </rss>"""
    return doc
