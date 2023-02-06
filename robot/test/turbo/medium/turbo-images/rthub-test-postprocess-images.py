#!/usr/bin/env python
import yatest.common
from os.path import join as pj
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TContentPluginsResult,
)
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TProcessingDocument
)
import json


EFS_AUTOPARSER = 3
EFS_YML = 5
EFS_RSS = 0


def test_reuploaded_mds_json():
    turbo_test = TurboTest(
        data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/turbo-images/postproc-data.yql"),
        output=yatest.common.work_path("test_reuploaded_mds_json")
    )

    wiki_url = 'https://ru.wikipedia.org/wiki/SomePage'

    docs = [
        _create_document(wiki_url, ["https://uploads.wikimedia.org/image_mds_reupload.jpg"], EFS_AUTOPARSER),
    ]

    expected_docs_urls = [wiki_url]

    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        turbo_test.unpack_standard_resources()

        turbo_test.run_rthub_postprocess({"REQUEST_IMAGE_RATIO": "1", "UPLOAD_IMAGE_RATIO": "1"})
        docs = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)

    actual_doc_urls = [doc.Document for doc in docs]

    assert sorted(expected_docs_urls) == sorted(actual_doc_urls)

    for doc in docs:
        assert doc.Action == 'atModify'
        assert doc.Status == 'ok'


def test_wiki_robots_txt():
    # ARRANGE
    turbo_test = TurboTest(
        data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/turbo-images/postproc-data.yql"),
        output=yatest.common.work_path("test_wiki_robots_txt")
    )

    bad_wiki = 'https://ru.wikipedia.org/wiki/Bad'
    good_wiki = 'https://ru.wikipedia.org/wiki/Good'

    expected_docs_urls = [good_wiki, bad_wiki]

    docs = [
        _create_document(good_wiki, ["https://uploads.wikimedia.org/image1.jpg"], EFS_AUTOPARSER),
        _create_document(bad_wiki, ["https://uploads.wikimedia.org/image2.jpg", "https://ru.wikipedia.org/w/blabla"], EFS_AUTOPARSER)
    ]

    # ACT
    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        turbo_test.unpack_standard_resources()

        turbo_test.run_rthub_postprocess({"REQUEST_IMAGE_RATIO": "1", "UPLOAD_IMAGE_RATIO": "1"})
        docs = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)

    actual_doc_urls = [doc.Document for doc in docs]

    assert sorted(expected_docs_urls) == sorted(actual_doc_urls)

    for doc in docs:
        if (doc.Document == bad_wiki):
            assert doc.Action == 'atDelete'
        else:
            assert doc.Action == 'atModify'


def test_image_orig_urls():
    # ARRANGE
    turbo_test = TurboTest(
        data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/turbo-images/postproc-data.yql"),
        output=yatest.common.work_path("test_image_orig_urls")
    )

    yml_imgs = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]

    yml_url = 'https://example.com/two_image'
    good_wiki = 'https://ru.wikipedia.org/wiki/Good'

    expected_docs_urls = [good_wiki, yml_url]

    docs = [
        _create_document(good_wiki, ["https://uploads.wikimedia.org/image1.jpg"], EFS_AUTOPARSER),
        _create_document(yml_url, yml_imgs, EFS_YML),
    ]

    # ACT
    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        turbo_test.unpack_standard_resources()

        turbo_test.run_rthub_postprocess({"REQUEST_IMAGE_RATIO": "1", "UPLOAD_IMAGE_RATIO": "1"})
        docs = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)

    # ASSERT
    actual_doc_urls = [doc.Document for doc in docs]

    assert sorted(expected_docs_urls) == sorted(actual_doc_urls)
    for doc in docs:
        assert doc.Action == 'atModify'

        doc_json = json.loads(doc.FinalJson)

        imgs = doc_json[0]["content"][0]["content"]
        if doc.Document == yml_url:
            for img, orig in zip(doc_json[0]["content"][0]["content"], yml_imgs):
                assert '__orig' in img
                assert img['__orig'] == orig
        else:
            for img in imgs:
                assert '__orig' not in img


def _create_document(url, images, efs):
    images_list = []
    for image_url in images:
        images_list.append(
            {
                "content_type": "image",
                "src": {
                    "__image": image_url
                },
                "type": "edge"})

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
    if efs != EFS_AUTOPARSER:
        doc.FeedUrl = url + "/feed"
    doc.SamovarImageFeedName = "images-turbo-rss"
    doc.IsFast = True
    doc.ItemSource = efs
    doc.SaasAction = 'atModify'
    return doc
