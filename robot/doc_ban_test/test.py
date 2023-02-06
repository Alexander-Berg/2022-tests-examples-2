#!/usr/bin/env python
import yatest.common
from os.path import join as pj
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TProcessingDocument,
    TContentPluginsResult
)


def test_docs_with_one_domain():
    # ARRANGE
    turbo_test = TurboTest(data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-cache-settings/doc_ban_test/data.yql"),
                           output=yatest.common.work_path("doc_without_settings"))
    docs = [
        _create_document("https://ban-doc.test/baned-doc"),
        _create_document("https://ban-doc.test/not-banned-doc")
    ]

    # ACT
    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        _unpack_resources(turbo_test)
        turbo_test.run_rthub_postprocess()

    # ASSERT
    docs_status = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)
    docs_status = sorted([(doc.Document, doc.Errors) for doc in docs_status], key=lambda x: x[0])

    assert docs_status == [("https://ban-doc.test/baned-doc", "[{\"code\":\"Banned.Document\"}]"),
                           ("https://ban-doc.test/not-banned-doc", "[]")]


def _create_document(url):
    doc = TContentPluginsResult()
    doc.Url = url
    doc.SaasKey = url
    doc.Json = '[]'
    doc.FeedUrl = url + "/feed"
    return doc


def _unpack_resources(turbo_test):
    turbo_test.unpack_standard_resources()
