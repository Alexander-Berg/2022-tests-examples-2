#!/usr/bin/env python

import yatest.common
import shutil
from os.path import join as pj
import os
import json

from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import TContentPluginsResult
from robot.protos.crawl.compatibility.feeds_pb2 import TFeedExt


def test_postprocess_docs_with_images():
    # ARRANGE
    custom_libraries_path = yatest.common.work_path("libraries")
    shutil.copytree(yatest.common.source_path('robot/rthub/yql/libraries'), custom_libraries_path)
    _extend_utils_sql(custom_libraries_path)

    docs = [
        _create_document("https://1-unknow-and-1-error.test", [
                         "https://1-unknow-and-1-error.test/1.jpg", "https://throw-error.test/1.jpg"]),
        _create_document("https://2-unknows.ru",
                         ["https://2-unknows.ru/1.jpg", "https://2-unknows.ru/2.jpg"]),
        _create_document("https://1-known.test",
                         ["https://1-known.test/1.jpg"])
    ]

    expected_docs_to_resend = [
        "https://1-unknow-and-1-error.test", "https://2-unknows.ru"]
    expected_items_to_samovar = ["https://1-unknow-and-1-error.test/1.jpg",
                                 "https://2-unknows.ru/1.jpg", "https://2-unknows.ru/2.jpg"]

    turbo_test = TurboTest(data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-dberror/test_docs_with_images/data.yql"),
                           libraries_path=custom_libraries_path)

    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        turbo_test.unpack_standard_resources()

        # ACT
        turbo_test.run_rthub_postprocess({"REQUEST_IMAGE_RATIO": "1"})

        items_to_samovar = turbo_test.restore_pb_from_file(pj(turbo_test.output, "samovar--feeds-ext"), TFeedExt)
        docs_to_resend = turbo_test.restore_pb_from_file(pj(turbo_test.output, "turbo-pages@rthub--loopback-1-prestable"), TContentPluginsResult)

    # ASSERT
    items_to_samovar = sorted([item.Url for item in items_to_samovar if item.FeedName == 'images-turbo-rss'])
    docs_to_resend = sorted([doc.Url for doc in docs_to_resend])

    assert docs_to_resend == expected_docs_to_resend
    assert items_to_samovar == expected_items_to_samovar


def _create_document(url, images):
    images_list = []
    for image_url in images:
        images_list.append(
            {"content_type": "image", "src": {"__image": image_url}, "alt": "alt"})
    json_string = [
        {
            "url": url,
            "title": "title",
            "noindex": "yandex",
            "content": [{
                "content": images_list
            }]
        }
    ]

    doc = TContentPluginsResult()
    doc.Url = url
    doc.SaasKey = url
    doc.Json = json.dumps(json_string).replace('"', '\"')
    doc.FeedUrl = url + "/feed"
    doc.SamovarImageFeedName = "images-turbo-rss"
    doc.IsFast = True
    return doc


def _extend_utils_sql(libraries_path):
    file_name = pj(libraries_path, "Utils.sql")
    os.chmod(file_name, 0o777)
    with open(file_name, 'a') as fileto:
        with open(yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-dberror/Utils.sql"), 'r') as filefrom:
            fileto.write(filefrom.read())
