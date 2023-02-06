import os
import pytest
import logging
import demjson
import tempfile
import shutil
from textwrap import dedent

import library.python.resource as lpr
from sandbox.projects.yabs.qa.utils.general import encode_text
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.compare import _compare_data, _compare_multiple
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.diff_methods import DiffMethods


def construct_block(data, diff_method=DiffMethods.no_diff):
    return {
        "diff_method": diff_method.name,
        "diff_data": encode_text(data),
    }


@pytest.mark.parametrize(("pre", "test", "expected_result"), [
    (
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
        },
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
        },
        {
            "has_diff": False
        }
    ),
    (
        {
            "request": construct_block("GET /"),
            "code": construct_block("200", diff_method=DiffMethods.text_diff),
            "handler": construct_block("meta"),
        },
        {
            "request": construct_block("GET /"),
            "code": construct_block("204", diff_method=DiffMethods.text_diff),
            "handler": construct_block("meta"),
        },
        {
            "has_diff": True
        }
    ),
    (
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("{test:1}", diff_method=DiffMethods.json_string_diff)
        },
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("{test:1}", diff_method=DiffMethods.json_string_diff)
        },
        {
            "has_diff": False,
            "diff_tags": set()
        }
    ),
    (
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("({test:2e9000000000001})", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("({test:2e9000000000000})", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "has_diff": True,
            "diff_tags": {"invalid_jsonp", "response_data"}
        }
    ),
    (
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("({test:2e9000000000000})", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("({test:2e9000000000000})", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "has_diff": False,
            "diff_tags": set()
        }
    ),
    (
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("('{test:2e9}')", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("({test:2e9})", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "has_diff": False,
        }
    ),
    (
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("callback('{\"test\":2e9}')", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("Ya[123]({\"test\":2e9})", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "has_diff": True,
        }
    ),
    pytest.param(
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("callback('{test: 2e9}')", diff_method=DiffMethods.jsonp_string_diff)
        },
        {
            "request": construct_block("GET /"),
            "code": construct_block("200"),
            "handler": construct_block("meta"),
            "response_data": construct_block("{\n\"test\":2e9\n}", diff_method=DiffMethods.json_string_diff)
        },
        {
            "has_diff": False,
        },
        marks=pytest.mark.xfail()
    ),
])
def test_compare_one_result(pre, test, expected_result):
    result = _compare_data(pre, test, 0, None, jsonp_parser=demjson.decode, comparison_flags=None)
    logging.info(result)
    for k, v in expected_result.items():
        assert getattr(result, k) == v


TEST_IDS = ['30002', '9983', '1891800067504']


@pytest.fixture
def request_data_in_fs():
    def write_resource(dirname, resource_name, test_id):
        request_data = lpr.find(resource_name)
        with open(os.path.join(dirname, str(test_id)), 'wb') as f:
            f.write(request_data)
    pre_dir = tempfile.mkdtemp(prefix='pre_')
    test_dir = tempfile.mkdtemp(prefix='test_')

    for test_id in TEST_IDS:
        if test_id == '30002':  # this is for testing equal request files
            resource_name = '/pre_{}.json'.format(test_id)
            write_resource(pre_dir, resource_name, test_id)
            write_resource(test_dir, resource_name, test_id)
        else:
            write_resource(pre_dir, '/pre_{}.json'.format(test_id), test_id)
            write_resource(test_dir, '/test_{}.json'.format(test_id), test_id)

    yield pre_dir, test_dir
    shutil.rmtree(pre_dir)
    shutil.rmtree(test_dir)


def test_compare_multiple_produces_cli_diff(request_data_in_fs):
    # this test does not validate produced cli diff, just checks produced files
    pre_dir, test_dir = request_data_in_fs

    tempfile.tempdir = '/tmp'
    _, _, chunks_data = _compare_multiple(
        pre_path=pre_dir, test_path=test_dir,
        test_ids=TEST_IDS,
        statistics_aggregation_config=dict(),
        n_jobs=2,  # set 1 while debugging to see full tracebacks, 2 otherwise
        enable_profiler=False,
    )
    assert set(os.listdir(chunks_data.get_cli_diffs_dir())) == set(['3.diff', '3.requests', '4.diff', '4.requests', '62.diff', '62.requests'])
    report_index_expected = dedent("""\
        request.id: 9983; status: failed; handler: page; pre.code: 200; test.code: 200; tags: exts_base_info, exts_query_data, exts_request_data, logs_data; chunk_path: cli_diff/3.diff;
        dd if=cli_diff/3.diff ibs=1 skip=0 count=1035 2> /dev/null
        dd if=cli_diff/3.requests ibs=1 skip=0 count=3055 2> /dev/null

        request.id: 1891800067504; status: failed; handler: count; pre.code: 200; test.code: 200; tags: logs_data; chunk_path: cli_diff/4.diff;
        dd if=cli_diff/4.diff ibs=1 skip=0 count=608 2> /dev/null
        dd if=cli_diff/4.requests ibs=1 skip=0 count=3488 2> /dev/null

        request.id: 30002; status: passed; handler: ; pre.code: 200; test.code: 200; tags: ;

    """)
    with open(chunks_data.get_cli_diffs_index(), 'r') as f:
        report_index_text = f.read()
        assert report_index_text == report_index_expected
    chunks_data.clear()
