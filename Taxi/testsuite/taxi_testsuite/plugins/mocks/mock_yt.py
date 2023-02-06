import json
import pathlib
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
import warnings

import aiohttp.web
import bson
import pytest
import yt.yson

from testsuite.utils import http


YT_YSON_BINARY_CONTENT_TYPE = 'application/x-yt-yson-binary'
YT_YSON_TEXT_CONTENT_TYPE = 'application/x-yt-yson-text'
JSON_CONTENT_TYPE = 'application/json'


class ResponseRecorder:
    def __init__(self, json_loader: Callable) -> None:
        self._json_loader: Callable = json_loader
        self._lookup_rows_responses: Dict[
            Tuple[Optional[str], str], bytes,
        ] = {}
        self._select_rows_responses: Dict[
            Tuple[Optional[str], str], bytes,
        ] = {}
        self._existing_paths: Dict[str, Any] = {}

    def add_lookup_rows_response(
            self, source_data: Any, filename: str, table: Optional[str] = None,
    ):
        if not table:
            warnings.warn(
                'please specify which table to mock', DeprecationWarning,
            )
        source_data = str(source_data)
        self._lookup_rows_responses[(table, source_data)] = self._load_reply(
            filename,
        )

    def get_lookup_rows_response(
            self, bin_yson: bytes, table: Optional[str] = None,
    ) -> bytes:
        if not table:
            warnings.warn(
                'please specify which table you want to fetch results from',
                DeprecationWarning,
            )
        source_data = _convert_bin_yson_to_str(bin_yson)
        fallback = self._lookup_rows_responses.get((None, source_data), b'{}')
        return self._lookup_rows_responses.get((table, source_data), fallback)

    def add_select_rows_response(
            self, query: str, filename: str, table: Optional[str] = None,
    ):
        if not table:
            warnings.warn(
                'please specify which table to mock', DeprecationWarning,
            )
        self._select_rows_responses[(table, query)] = self._load_reply(
            filename,
        )

    def get_select_rows_response(
            self, query: str, table: Optional[str] = None,
    ) -> bytes:
        if not table:
            warnings.warn(
                'please specify which table you want to fetch results from',
                DeprecationWarning,
            )
        fallback = self._lookup_rows_responses.get((None, query), b'{}')
        return self._select_rows_responses.get((table, query), fallback)

    # NOTE: we support only nodes with 'table' type now, no nested map_nodes
    def add_path(self, path: str, attributes: dict = None):
        if attributes is None:
            attributes = {}
        self._existing_paths[path] = attributes

    def check_existing_path(self, path: str) -> bool:
        if path.endswith('/@'):
            path = path[:-2]
        return path in self._existing_paths

    def _filter_attributes(self, path: str, attributes: List[str]):
        _path_attributes = self._existing_paths[path]
        return {
            attr: _path_attributes[attr]
            for attr in attributes
            if attr in _path_attributes
        }

    def get_content(self, path: str, attributes: List[str] = None):
        if path.endswith('/@'):
            path = path[:-2]
            _path_attributes = self._existing_paths[path]

            # for /@ path we return all attributes on the first level
            # if no filter applied
            if not attributes:
                return _path_attributes

            # if all attributes filters were inconsistent,
            # return empty content
            return self._filter_attributes(path, attributes)

        if not attributes:
            # on plain get we return empty attributes by default in
            # 'attributes' key
            return {'attributes': {}}

        return {'attributes': self._filter_attributes(path, attributes)}

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
def yt_host(mockserver_info):
    return '%s:%d/yt' % (mockserver_info.host, mockserver_info.port)


@pytest.fixture
def mock_yt(mockserver, load_json, yt_host):
    recorder = ResponseRecorder(load_json)
    api_v3_response = _get_api_v3()

    @mockserver.json_handler('/yt/hosts')
    def _hosts(request):
        return [yt_host]

    @mockserver.json_handler('/yt/api/v3')
    def _api_v3(request):
        return api_v3_response

    @mockserver.json_handler('/yt/api/v3/select_rows')
    async def _select_rows(request):
        yt_parameters = _get_yt_parameters(request)
        if 'query' not in yt_parameters:
            return {}

        query = yt_parameters['query']
        table = yt_parameters.get('path', None)
        return mockserver.make_response(
            recorder.get_select_rows_response(query, table),
            content_type=YT_YSON_BINARY_CONTENT_TYPE,
        )

    @mockserver.aiohttp_json_handler('/yt/api/v3/lookup_rows')
    async def _lookup_rows(request: aiohttp.web.Request):
        table = _get_yt_parameters(request).get('path', None)
        bin_yson = await request.read()
        return mockserver.make_response(
            recorder.get_lookup_rows_response(bin_yson, table),
            content_type=YT_YSON_BINARY_CONTENT_TYPE,
        )

    @mockserver.json_handler('/yt/api/v3/exists')
    async def _exists(request):
        yt_parameters = _get_yt_parameters(request)
        if 'path' not in yt_parameters:
            return {}

        # NOTE: we can support yt_parameters['output_format'], but it would
        #  be overkill for this mock

        path = yt_parameters['path']
        value = recorder.check_existing_path(path)
        return mockserver.make_response(
            yt.yson.dumps(value), content_type=YT_YSON_TEXT_CONTENT_TYPE,
        )

    @mockserver.json_handler('/yt/api/v3/get')
    async def _get(request):
        yt_parameters = _get_yt_parameters(request)
        if 'path' not in yt_parameters:
            return {}

        path = yt_parameters['path']
        if not recorder.check_existing_path(path):
            # 500 - Error resolving path
            return _make_yt_error_response(500, yt_parameters)

        attributes = yt_parameters.get('attributes')
        content = recorder.get_content(path, attributes)
        return mockserver.make_response(
            yt.yson.dumps(content), content_type=YT_YSON_TEXT_CONTENT_TYPE,
        )

    return recorder


def _get_api_v3() -> List[dict]:
    api_json_path = pathlib.Path(__file__).parent / 'static/yt_api_v3.json'
    with api_json_path.open() as fstream:
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


def _get_yt_parameters(request) -> Dict[str, Any]:
    if 'X-YT-Parameters' not in request.headers:
        return {}

    return yt.yson.loads(request.headers['X-YT-Parameters'].encode())


def _make_yt_error_response(yt_response_code, yt_parameters):
    error_str = json.dumps(
        {'code': yt_response_code, 'attributes': {}, 'message': 'error'},
    )
    return http.make_response(
        error_str,
        content_type=JSON_CONTENT_TYPE,
        headers={
            # all values must be strings
            'X-YT-Header-Format': '<format=text>yson',
            'X-YT-Parameters': yt.yson.dumps(yt_parameters).decode('utf-8'),
            'X-YT-Response-Code': str(yt_response_code),
            'X-YT-Error': error_str,
        },
        # https://wiki.yandex-team.ru/yt/userdoc/http/#kodyvozvrata
        status=400,
    )
