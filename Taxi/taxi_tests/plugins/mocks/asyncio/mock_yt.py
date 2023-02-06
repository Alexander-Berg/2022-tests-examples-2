import json
import os.path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List

import aiohttp.web
import bson
import pytest
import yt.yson


class ResponseRecorder:
    def __init__(self, json_loader: Callable) -> None:
        self._json_loader: Callable = json_loader
        self._lookup_rows_responses: Dict[str, bytes] = {}
        self._select_rows_responses: Dict[str, bytes] = {}

    def add_lookup_rows_response(self, source_data: Any, filename: str):
        source_data = str(source_data)
        self._lookup_rows_responses[source_data] = self._load_reply(
            filename,
        )

    def get_lookup_rows_response(self, bin_yson: bytes) -> bytes:
        source_data = _convert_bin_yson_to_str(bin_yson)
        return self._lookup_rows_responses.get(source_data, b'{}')

    def add_select_rows_response(self, query: str, filename: str):
        self._select_rows_responses[query] = self._load_reply(filename)

    def get_select_rows_response(self, query: str) -> bytes:
        return self._select_rows_responses.get(query, b'{}')

    def _load_reply(self, filename: str) -> bytes:
        data = self._json_loader(filename)
        if isinstance(data, dict):
            reply = _dump_item(data)
        elif isinstance(data, list):
            reply = b';'.join([_dump_item(item) for item in data])
        else:
            raise RuntimeError(
                'YT mock data must be an object or array of objects',
            )
        return reply


@pytest.fixture(scope='session')
def yt_host(testsuite_session_context):
    return '%s:%d/yt' % (
        testsuite_session_context.mockserver.host,
        testsuite_session_context.mockserver.port,
    )


@pytest.fixture
def mock_yt(mockserver, load_json, yt_host):
    recorder = ResponseRecorder(load_json)
    api_v3_response = _get_api_v3()

    @mockserver.json_handler('/yt/hosts')
    def hosts(request):
        return [yt_host]

    @mockserver.json_handler('/yt/api/v3')
    def api_v3(request):
        return api_v3_response

    @mockserver.json_handler('/yt/api/v3/select_rows')
    async def select_rows(request):
        if 'X-YT-Parameters' not in request.headers:
            return {}

        yt_parameters = yt.yson.loads(
            request.headers['X-YT-Parameters'].encode(),
        )
        if 'query' not in yt_parameters:
            return {}

        query = yt_parameters['query']
        return aiohttp.web.Response(
            body=recorder.get_select_rows_response(query),
            content_type='application/x-yt-yson-binary',
        )

    @mockserver.json_handler('/yt/api/v3/lookup_rows', raw_request=True)
    async def lookup_rows(request):
        bin_yson = await request.read()
        return aiohttp.web.Response(
            body=recorder.get_lookup_rows_response(bin_yson),
            content_type='application/x-yt-yson-binary',
        )

    return recorder


def _get_api_v3() -> List[dict]:
    api_json_path = os.path.join(
        os.path.dirname(__file__), 'static', 'yt_api_v3.json',
    )
    with open(api_json_path, 'r') as fstream:
        api_v3 = json.load(fstream)
    return api_v3


def _convert_bin_yson_to_str(bin_yson: bytes) -> str:
    return str(list(yt.yson.loads(bin_yson, yson_type='list_fragment')))


def _dump_item(data: Dict[str, Any]) -> bytes:
    result = {}
    for key, value in data.items():
        # 'doc' field in YT is a raw bson document
        if key == 'doc' or key.endswith('.doc'):
            value = bson.BSON.encode(value)
        elif isinstance(value, str):
            value = value.encode()
        elif not isinstance(value, int) and value is not None:
            raise RuntimeError('Invalid YT value %s' % value)
        result[key.encode()] = value
    return yt.yson.dumps(result, yson_format='binary', encoding=None)
