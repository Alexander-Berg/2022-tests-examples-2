import collections
import copy
import json

import pytest

from taxi.clients import yt


RequestArgs = collections.namedtuple(
    'RequestParams',
    ['method', 'command', 'headers', 'data', 'parse_rows', 'params_update'],
)


YT_CONFIG = {
    'foo': {
        'prefix': '//test/',
        'token': 'abc',
        'api_version': 'v0',
        'proxy': {'url': 'foo.yt.net'},
    },
    'bar': {
        'prefix': '//test/',
        'token': 'abc',
        'api_version': 'v0',
        'proxy': {'url': 'bar.yt.net'},
    },
}


TEST_PATH = 'test_path'
SAMPLE_REQUEST_HEADERS = {
    'X-YT-Header-Format': '"json"',
    'X-YT-Output-Format': '"json"',
    'X-YT-Input-Format': '"json"',
    'X-YT-Parameters': {
        'format': 'json',
        'output_format': {
            '$attributes': {'encode_utf8': False},
            '$value': 'json',
        },
        'input_format': {
            '$attributes': {'encode_utf8': False},
            '$value': 'json',
        },
    },
    'Authorization': 'OAuth ' + YT_CONFIG['foo']['token'],  # type: ignore
}


class MockSession:
    async def close(self):
        pass


def parse_data(data):
    parsed_rows = []
    for row in data.splitlines():
        doc = json.loads(row)
        parsed_rows.append(doc)
    return parsed_rows


def encode_data(data):
    json_encoded = []
    for row in data:
        json_encoded.append(
            json.dumps(row, ensure_ascii=False).encode('utf-8'),
        )
    return b''.join(json_encoded)


@pytest.mark.parametrize(
    'command,command_kwargs,mock_results,expected_request,exception',
    [
        (
            'lookup_rows',
            {
                'path': TEST_PATH,
                'input_data': [{'id': 'test_row_id'}],
                'column_names': ['id'],
            },
            [None],
            RequestArgs(
                yt.PUT_METHOD,
                'lookup_rows',
                None,
                data=encode_data([{'id': 'test_row_id'}]),
                parse_rows=True,
                params_update={
                    'column_names': ['id'],
                    'path': '{}{}'.format(
                        YT_CONFIG['foo']['prefix'], TEST_PATH,
                    ),
                },
            ),
            None,
        ),
        (
            'lookup_rows',
            {
                'path': TEST_PATH,
                'input_data': [{'id': 'test_row_id'}],
                'column_names': ['id'],
            },
            [None],
            RequestArgs(
                yt.PUT_METHOD,
                'lookup_rows',
                None,
                data=encode_data([{'id': 'test_row_id'}]),
                parse_rows=True,
                params_update={'column_names': ['id']},
            ),
            yt.YtRequestError,
        ),
        (
            'select_rows',
            {'query': '* FROM [//test_path]'},
            [None],
            RequestArgs(
                yt.GET_METHOD,
                'select_rows',
                None,
                data=None,
                parse_rows=True,
                params_update={
                    'query': '* FROM [//test_path]',
                    'output_row_limit': None,
                },
            ),
            None,
        ),
        (
            'insert_rows',
            {
                'path': TEST_PATH,
                'rows': [{'id': 'test_row_id', 'dummy': 'dummy'}],
            },
            [None],
            RequestArgs(
                yt.PUT_METHOD,
                'insert_rows',
                None,
                data=encode_data([{'id': 'test_row_id', 'dummy': 'dummy'}]),
                parse_rows=True,
                params_update={
                    'path': '{}{}'.format(
                        YT_CONFIG['foo']['prefix'], TEST_PATH,
                    ),
                    'update': False,
                },
            ),
            None,
        ),
        (
            'get',
            {'path': TEST_PATH},
            [None],
            RequestArgs(
                yt.GET_METHOD,
                'get',
                None,
                data=None,
                parse_rows=False,
                params_update={
                    'path': '{}{}'.format(
                        YT_CONFIG['foo']['prefix'], TEST_PATH,
                    ),
                    'max_size': None,
                    'attributes': None,
                },
            ),
            None,
        ),
        (
            'exists',
            {'path': TEST_PATH},
            [[False]],
            RequestArgs(
                yt.GET_METHOD,
                'exists',
                None,
                data=None,
                parse_rows=False,
                params_update={
                    'path': '{}{}'.format(
                        YT_CONFIG['foo']['prefix'], TEST_PATH,
                    ),
                },
            ),
            None,
        ),
        (
            'read_table',
            {'path': TEST_PATH},
            [[True], {'type': 'table'}, [{'key': 'value'}]],
            RequestArgs(
                yt.GET_METHOD,
                'read_table',
                None,
                data=None,
                parse_rows=False,
                params_update={
                    'path': '{}{}'.format(
                        YT_CONFIG['foo']['prefix'], TEST_PATH,
                    ),
                },
            ),
            None,
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_yt_client_request(
        monkeypatch,
        command,
        command_kwargs,
        mock_results,
        expected_request,
        exception,
):
    request_args = None

    async def mock_send_request(*args, **kwargs):
        nonlocal request_args
        kwargs.pop('log_extra')
        request_args = RequestArgs(*args, **kwargs, params_update=None)
        if exception:
            raise yt.YtRequestError('Test')
        return mock_results.pop(0)

    monkeypatch.setattr('aiohttp_trailers.ClientSession', MockSession)
    cluster_client = yt.YtClient(YT_CONFIG['foo'], MockSession())
    monkeypatch.setattr(cluster_client, '_send_request', mock_send_request)
    method_by_command = {
        'lookup_rows': cluster_client.lookup_rows,
        'insert_rows': cluster_client.insert_rows,
        'select_rows': cluster_client.select_rows,
        'get': cluster_client.get,
        'exists': cluster_client.exists,
        'read_table': cluster_client.read_table,
    }
    method = method_by_command[command]
    coro = method(**command_kwargs)
    if exception:
        with pytest.raises(exception):
            await coro
    else:
        await coro
        assert request_args.method == expected_request.method
        assert request_args.command == expected_request.command
        expected_headers = copy.deepcopy(SAMPLE_REQUEST_HEADERS)
        expected_headers['X-YT-Parameters'].update(
            expected_request.params_update or {},
        )
        request_args.headers['X-YT-Parameters'] = json.loads(
            request_args.headers['X-YT-Parameters'],
        )
        assert request_args.headers == expected_headers
        assert request_args.data == expected_request.data


@pytest.mark.parametrize(
    'cluster_exceptions,client_exception',
    [
        ({'foo': None, 'bar': None}, None),
        ({'foo': None, 'bar': yt.YtRequestError}, None),
        (
            {'foo': yt.YtRequestError, 'bar': yt.YtRequestError},
            yt.YtRequestError,
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_group_cluster(
        monkeypatch, cluster_exceptions, client_exception, loop,
):
    result_rows = [{'id': 'first_row'}, {'id': 'second_row'}]

    class MockYtClient:
        def __init__(self, *args, **kwargs):
            url = kwargs.get('config', {}).get('proxy', {}).get('url')
            self.name = url.split('.')[0] if url else None
            self.session = MockSession()

        async def lookup_rows(self, *args, **kwargs):
            if cluster_exceptions[self.name]:
                raise cluster_exceptions[self.name]
            return [result_rows.pop()]

    clients = []
    for cluster in ['foo', 'bar']:
        clients.append(MockYtClient(config=YT_CONFIG[cluster]))
    group_client = yt.YtGroupClient(clients, loop=loop)
    if client_exception:
        with pytest.raises(client_exception):
            await group_client.lookup_rows('test_path', [{}])
    else:
        result = await group_client.lookup_rows('test_path', [{}])
        assert result == [{'id': 'second_row'}]
