#!/usr/bin/env python

import json
import yatest.common
from os.path import join as pj
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.protos.crawl.compatibility.feeds_pb2 import TFeedExt
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TProcessingDocument,
    TContentPluginsResult
)


def test_fact_json_with_uniq_image():
    # ARRANGE
    turbo_test = TurboTest(output=yatest.common.work_path("fact_images"))
    docs = [
        _create_document("https://example.com/fact_images"),
    ]

    # ACT
    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        turbo_test.unpack_standard_resources()
        turbo_test.run_rthub_postprocess({"REQUEST_IMAGE_RATIO": "1"})

    # ASSERT
    requested_images = turbo_test.restore_pb_from_file(pj(turbo_test.output, "samovar--feeds-ext"), TFeedExt)
    docs_to_resend = turbo_test.restore_pb_from_file(pj(turbo_test.output, "turbo-pages@rthub--loopback-3-prestable"), TContentPluginsResult)
    docs_status = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)

    assert len(requested_images) == 1
    assert requested_images[0].Url == 'https://example.com/only_fact_image'

    assert len(docs_to_resend) == 1

    assert len(docs_status) == 1
    assert json.loads(docs_status[0].FinalJson) == [{
        'url': 'url',
        'title': 'title',
        'content': []
    }]
    assert docs_status[0].Status == 'postpone'


def _create_document(url):
    doc = TContentPluginsResult()
    doc.Url = url
    doc.SaasKey = url
    doc.SamovarImageFeedName = "images-turbo-rss"
    doc.Json = json.dumps([{
        'url': 'url',
        'title': 'title',
        'content': []
    }])
    doc.FactJson = json.dumps({
        'src': {
            '__image': 'https://example.com/only_fact_image'
        }
    })
    doc.FeedUrl = url + "/feed"
    return doc
