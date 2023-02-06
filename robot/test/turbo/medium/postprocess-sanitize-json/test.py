#!/usr/bin/env python

import yatest.common
import logging
import shutil
import tarfile
import tempfile
import json
import os

import google.protobuf.text_format as text_format

from os.path import join as pj, isfile
from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.common.kikimr_runner import KikimrRunner
from robot.rthub.yql.protos.content_plugins_pb2 import TContentPluginsResult, TProcessingDocument


def unpack_resources(resources_path, res_dir):
    for arc in os.listdir(resources_path):
        if '.tar' in arc:
            with tarfile.open(pj(resources_path, arc), 'r') as t:
                t.extractall(res_dir)
        elif isfile(pj(resources_path, arc)):
            shutil.copy(pj(resources_path, arc), pj(res_dir, arc))
        else:
            shutil.copytree(pj(resources_path, arc), pj(res_dir, arc))


def run_with_wrapper(test_name, table_yql, data_yql, test_fn):
    logger = logging.getLogger('rthub_test_logger')
    logger.info(test_name)

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')
    postprocess_orig_config = yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-postprocess-worker.pb.txt.gen')
    udfs_path = yatest.common.build_path('robot/rthub/packages/full_turbo_udfs')
    proto_path = yatest.common.build_path('robot/rthub/packages/full_web_protos')
    libraries_path = yatest.common.source_path('robot/rthub/yql/libraries')
    queries_path = yatest.common.source_path('robot/rthub/yql/queries')

    output = yatest.common.work_path('output')
    if os.path.exists(output):
        shutil.rmtree(output)
    os.mkdir(output)

    json_input_dir = yatest.common.work_path(test_name)
    if os.path.exists(json_input_dir):
        shutil.rmtree(json_input_dir)

    # Gather resources
    res_dir = yatest.common.work_path('resources')
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)

    os.mkdir(res_dir)
    unpack_resources(yatest.common.work_path('.'), res_dir)
    unpack_resources(yatest.common.build_path('robot/rthub/packages/resources/saas'), pj(res_dir, 'saas'))
    unpack_resources(yatest.common.source_path('robot/rthub/packages/resources/turbo-pages'), res_dir)
    unpack_resources(yatest.common.source_path('quality/functionality/turbo/page_linter/config'), res_dir)

    kikimr_runner = KikimrRunner(table_yql, data_yql)
    kikimr_runner.setup()

    try:
        logger.info("Running Postprocess RTHub...")
        rthub_runner_postprocess = RTHubRunner(rthub_bin, postprocess_orig_config, json_input_dir, output)
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
        test_fn(logger, kikimr_runner, rthub_runner_postprocess, json_input_dir, output)
    finally:
        kikimr_runner.stop()


def test_sanitize_turbo_json():
    def fn(logger, kikimr_runner, rthub_runner_postprocess, json_input_dir, output):
        input_data = [
            _get_postprocess_input_rec("https://www.broken-url-1.ru/", json.dumps([])),
            _get_postprocess_input_rec("https://www.broken-url-2.ru/", json.dumps([{}])),
            _get_postprocess_input_rec("https://www.broken-url-3.ru/", json.dumps([{"title": "abc"}])),
            _get_postprocess_input_rec("https://www.broken-url-4.ru/", json.dumps([{"url": "https://www.broken-url-4.ru/"}])),
            _get_postprocess_input_rec("https://www.ok-url-1.ru/", json.dumps([{"title": "abc", "url": "https://www.ok-url-1.ru/", "content": []}])),
        ]
        _write_items_to_input_feed(json_input_dir, input_data)
        rthub_runner_postprocess.run_rthub(binary=False)

        actual_has_final_json = {}
        output_path = pj(output, "rthub-turbo--turbo-documents")
        with open(output_path, "r") as f:
            text = f.read()
            for item in text.split('===\n'):
                if item:
                    item = text_format.Parse(item, TProcessingDocument())
                    actual_has_final_json[item.Document] = len(item.FinalJson) > 0

        expected_has_final_json = {
            'https://www.ok-url-1.ru/': True,
            'https://www.broken-url-1.ru/': False,
            'https://www.broken-url-2.ru/': False,
            'https://www.broken-url-3.ru/': False,
            'https://www.broken-url-4.ru/': False
        }
        assert actual_has_final_json == expected_has_final_json

    table_yql = yatest.common.source_path('robot/rthub/test/turbo/yql/table.yql')
    empty_data_yql = tempfile.NamedTemporaryFile(prefix="empty_data", suffix=".yql")
    run_with_wrapper('test_sanitize_turbo_json', table_yql, empty_data_yql.name, fn)


def test_autodeleted_turbo_json():
    def fn(logger, kikimr_runner, rthub_runner_postprocess, json_input_dir, output):
        some_nasty_content = ' '.join(['<div></div>']*10)
        paragraphs = [
            {
                "content_type": "paragraph",
                "content": some_nasty_content
            }
        ]
        input_data = [
            _get_postprocess_input_rec("https://www.broken-url-1.ru/", json.dumps([{"title": "abc", "url": "https://www.broken-url-1.ru", "content": paragraphs}])),
            _get_postprocess_input_rec("https://www.ok-url-1.ru/", json.dumps([{"title": "abc", "url": "https://www.ok-url-1.ru/", "content": []}])),
        ]
        _write_items_to_input_feed(json_input_dir, input_data)
        rthub_runner_postprocess.run_rthub(binary=False)

        output_path = pj(output, "rthub-turbo--turbo-documents")
        count = 0
        with open(output_path, "r") as f:
            text = f.read()
            for item in text.split('===\n'):
                if item:
                    doc = text_format.Parse(item, TProcessingDocument())
                    assert doc.Status == 'ok'
                    if ('broken' in doc.Document):
                        assert doc.Action == 'atDelete'
                        meta = json.loads(doc.Meta)
                        assert isinstance(meta, dict) and meta.get('deletion_reason') == 'page_linter:markup'
                    else:
                        assert doc.Action == 'atModify'
                    count += 1
        assert count == 2

    table_yql = yatest.common.source_path('robot/rthub/test/turbo/yql/table.yql')
    empty_data_yql = tempfile.NamedTemporaryFile(prefix="empty_data", suffix=".yql")
    run_with_wrapper('test_autodeleted_turbo_json', table_yql, empty_data_yql.name, fn)


def _get_postprocess_input_rec(url, data):
    return TContentPluginsResult(Url=url,
                                 SaasKey=url,
                                 ItemSource=0,
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
                                 Json=data,
                                 AttemptsCount=0
                                 )


def _write_items_to_input_feed(dir, items):
    res = "===\n".join([str(x) for x in items])

    os.makedirs(dir)
    filename = pj(dir, "rthub--turbo-json")
    with(open(filename, 'w+')) as f:
        f.write(res)
