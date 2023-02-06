import os
import shutil
import logging
from collections import defaultdict

from sandbox.common.errors import SandboxException
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.compare_dict import compare_dicts
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.compare import (
    SingleComparisonResult,
    ChunkComparisonResult,
    ChunksData,
    REPORT_CHUNKS_COUNT
)


def compare_json(pre_dict, test_dict, request_id):
    if set(pre_dict.keys()) ^ set(test_dict.keys()):
        raise SandboxException('Different dict keys for request {}'.format(request_id))

    has_diff, diff = compare_dicts(pre_dict, test_dict)
    result = SingleComparisonResult(
        test_id=request_id,
        has_diff=has_diff,
        pre_code=200,  # TODO(bruh): add http info
        test_code=200,
        handler='/yabs_hit_models',
        diff_tags=set(),
        diff=diff,
        request="",
    )
    return result


def compare_one(pre_path, test_path, request_id):
    from google.protobuf.json_format import MessageToDict
    from search.begemot.server.proto.begemot_pb2 import TBegemotResponse

    dicts = []
    for path in [pre_path, test_path]:
        with open(os.path.join(path, request_id), 'rb') as f:
            serialized_proto = f.read()
            proto_obj = TBegemotResponse()
            proto_obj.ParseFromString(serialized_proto)
            dicts += [MessageToDict(proto_obj)]

    return compare_json(dicts[0], dicts[1], request_id)


def compare_job(pre_path, test_path, request_ids, chunk_name, chunks_data):
    logging.info('Compare job, request_ids: {}'.format(request_ids))
    chunk_comparison_result = ChunkComparisonResult()
    chunk_results = {}

    for i in request_ids:
        comparison_result = compare_one(pre_path, test_path, i)
        chunk_comparison_result.update(comparison_result)
        chunk_results[comparison_result.test_id] = comparison_result

    chunk_web_report_index = chunks_data.add_tests_chunk(chunk_results, chunk_name)
    chunks_data.add_tests_chunk(chunk_results, chunk_name)
    return chunk_comparison_result, chunk_web_report_index


def move_tests_and_diffs_chunks(chunks_data, report):
    os.rmdir(report._tests_dir)
    os.rmdir(report._diffs_dir)

    shutil.move(chunks_data.get_tests_dir(), report._tests_dir)
    shutil.move(chunks_data.get_diffs_dir(), report._diffs_dir)


def compare_responses(pre_path, test_path, request_ids, report, jobs):
    chunks_data = ChunksData()
    chunks = defaultdict(list)
    for i in request_ids:
        chunks[int(i) % REPORT_CHUNKS_COUNT].append(i)

    args_list = [(pre_path, test_path, chunk, chunk_name, chunks_data) for chunk_name, chunk in chunks.items()]

    web_report_index = []
    comparison_result = ChunkComparisonResult()

    if jobs == 1:
        for args in args_list:
            chunk_comparison_result, chunk_web_report_index = compare_job(*args)
            comparison_result.update(chunk_comparison_result)
            web_report_index.extend(chunk_web_report_index)
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed
        fs = []
        with ProcessPoolExecutor(max_workers=jobs) as process_pool:
            for args in args_list:
                fs.append(process_pool.submit(compare_job, *args))

            for f in as_completed(fs):
                exc = f.exception()
                if exc is not None:
                    raise exc
                chunk_comparison_result, chunk_web_report_index = f.result()
                comparison_result.update(chunk_comparison_result)
                web_report_index.extend(chunk_web_report_index)

    logging.info('chunks_data_tests_dir_path={}, _tests_dir={}'.format(chunks_data.get_tests_dir(), report._tests_dir))
    logging.info('chunks_data_diffs_dir_path={}, _diffs_dir={}'.format(chunks_data.get_diffs_dir(), report._diffs_dir))
    move_tests_and_diffs_chunks(chunks_data, report)

    return comparison_result, web_report_index
