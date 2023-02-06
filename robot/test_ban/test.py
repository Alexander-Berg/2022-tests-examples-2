#!/usr/bin/env python

import yatest.common
import shutil
from os.path import join as pj
import os
import json

from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TContentPluginsResult,
    TProcessingDocument
)


def test_postprocess_ban():
    # ARRANGE
    custom_libraries_path = yatest.common.work_path("libraries")
    shutil.copytree(yatest.common.source_path('robot/rthub/yql/libraries'), custom_libraries_path)
    _extend_utils_sql(custom_libraries_path)

    turbo_test = TurboTest(data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-dberror/test_ban/data.yql"),
                           libraries_path=custom_libraries_path)
    docs = [
        _create_document("https://ban.test"),
        _create_document("https://throw-error.test"),
        _create_document("https://not-ban.test")
    ]

    expected_docs_to_resend = ["https://throw-error.test"]
    expected_docs_status = [("https://ban.test/feed", "error"),             # banned document
                            ("https://not-ban.test/feed", "ok"),            # no ban
                            ("https://throw-error.test/feed", "postpone")]  # no information about ban-status

    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        turbo_test.unpack_standard_resources()

        # ACT
        turbo_test.run_rthub_postprocess()

        # ASSERT
        docs_to_resend = turbo_test.restore_pb_from_file(pj(turbo_test.output, "turbo-pages@rthub--loopback-1-prestable"), TContentPluginsResult)
        docs_to_resend = sorted([doc.Url for doc in docs_to_resend])
        docs_status = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)
        docs_status = sorted([(doc.Feed, doc.Status) for doc in docs_status], key=lambda x: x[0])

    assert docs_to_resend == expected_docs_to_resend
    assert docs_status == expected_docs_status


def _create_document(url):
    doc = TContentPluginsResult()
    doc.Url = url
    doc.SaasKey = url
    doc.Json = json.dumps([{
        'url': 'url',
        'title': 'title',
        'content': []
    }])
    doc.FeedUrl = url + "/feed"
    doc.IsFast = True
    return doc


def _extend_utils_sql(libraries_path):
    file_name = pj(libraries_path, "Utils.sql")
    os.chmod(file_name, 0o777)
    with open(file_name, 'a') as fileto:
        with open(yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-dberror/Utils.sql"), 'r') as filefrom:
            fileto.write(filefrom.read())
