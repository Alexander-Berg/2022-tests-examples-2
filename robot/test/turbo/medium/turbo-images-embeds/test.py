#!/usr/bin/env python
import yatest.common
from os.path import join as pj
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TContentPluginsResult
)
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TProcessingDocument
)
import json
from quality.functionality.turbo.common.python.lib import base64_tools


def test_upload_embeddings_to_json_doc():
    # ARRANGE
    turbo_test = TurboTest(data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/turbo-images-embeds/data.yql"),
                           output=yatest.common.work_path("test_upload_layer_features_to_json_doc"))
    docs = [
        _create_document('https://example.com/one_image', ["https://example.com/image1.jpg"]),
        _create_document('https://example.com/two_image', ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]),
        _create_document('https://example.com/small_image', ["https://example.com/small_image.jpg"]),
        _create_document('https://example.com/image_without_embeds', ["https://example.com/image_without_embeds.jpg"]),
        _create_document('https://example.com/doc_without_images', []),
        _create_document('https://example.com/image_with_alias', ['https://example.com/image_with_alias.jpg']),
        _create_document('https://example.com/not_yml_page', ['https://example.com/image1.jpg'], False)
    ]
    docs_without_embeddings = ['https://example.com/small_image', 'https://example.com/doc_without_images',
                               'https://example.com/image_without_embeds', 'https://example.com/not_yml_page']

    expected_docs_urls = ['https://example.com/one_image',
                          'https://example.com/two_image',
                          'https://example.com/small_image',
                          'https://example.com/image_without_embeds',
                          'https://example.com/doc_without_images',
                          'https://example.com/image_with_alias',
                          'https://example.com/not_yml_page']

    # ACT
    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        turbo_test.unpack_standard_resources()

        turbo_test.run_rthub_postprocess({"REQUEST_IMAGE_RATIO": "1"})
        docs = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)

    # ASSERT
    actual_doc_urls = [doc.Document for doc in docs]

    assert sorted(expected_docs_urls) == sorted(actual_doc_urls)
    for doc in docs:
        doc_json = json.loads(doc.FinalJson)
        if doc.Document in docs_without_embeddings:
            assert 'main_image_embeddings' not in doc_json
        else:
            assert 'main_image_embeddings' in doc_json[0]
            assert len(doc_json[0]['main_image_embeddings']) == 2
            assert 'prod_v10_enc_i2t_v12_200_img' in doc_json[0]['main_image_embeddings']
            assert 'prod_v10_enc_toloka_192' in doc_json[0]['main_image_embeddings']

            expected_list_1 = [0.1111,  -0.2222, 0.3333, -0.4444, 0.5555]
            actual_list_1 = base64_tools.float_vector_from_base64(doc_json[0]['main_image_embeddings']['prod_v10_enc_i2t_v12_200_img'])
            assert compare_two_float_list(actual_list_1, expected_list_1)

            expected_list_2 = [0.6666, -0.7777, 0.8888, -0.9999]
            actual_list_2 = base64_tools.float_vector_from_base64(doc_json[0]['main_image_embeddings']['prod_v10_enc_toloka_192'])
            assert compare_two_float_list(actual_list_2, expected_list_2)


def compare_two_float_list(a, b, e=0.0001):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if abs(a[i] - b[i]) > e:
            return False
    return True


def _create_document(url, images, is_yml=True):
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
    doc.FeedUrl = url + "/feed"
    doc.SamovarImageFeedName = "images-turbo-rss"
    doc.IsFast = True
    doc.ItemSource = 5 if is_yml else 1
    return doc
