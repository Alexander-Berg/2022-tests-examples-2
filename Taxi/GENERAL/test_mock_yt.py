import json

import aiohttp
import bson
import pytest
import yt.yson

from testsuite.daemons import service_client

pytest_plugins = ['taxi_testsuite.plugins.mocks.mock_yt']


@pytest.fixture(scope='session')
def _api_url(mockserver_info):
    return mockserver_info.base_url + 'yt/api/v3'


@pytest.fixture()
def _yt_client(
        _api_url, service_client_default_headers, service_client_options,
):
    return service_client.Client(
        _api_url,
        headers=service_client_default_headers,
        **service_client_options,
    )


async def test_lookup_rows(loop, mock_yt, load_json, _api_url):
    mock_yt.add_lookup_rows_response(
        source_data=[{'some': 'some_id'}],
        filename='lookup_rows_response.json',
    )
    async with aiohttp.ClientSession(loop=loop) as session:
        response = await session.post(
            _api_url + '/lookup_rows', data=yt.yson.dumps({'some': 'some_id'}),
        )
    content = _decode_docs(yt.yson.loads(await response.read()))
    assert content == load_json('lookup_rows_response.json')


async def test_lookup_rows_with_table(loop, mock_yt, load_json, _api_url):
    path = '//some/path'
    mock_yt.add_lookup_rows_response(
        table=path,
        source_data=[{'some': 'some_id'}],
        filename='lookup_rows_response.json',
    )
    async with aiohttp.ClientSession(loop=loop) as session:
        response = await session.post(
            _api_url + '/lookup_rows',
            data=yt.yson.dumps({'some': 'some_id'}),
            headers={'X-YT-Parameters': _to_yson_str({'path': path})},
        )
    content = _decode_docs(yt.yson.loads(await response.read()))
    assert content == load_json('lookup_rows_response.json')


async def test_select_rows(loop, mock_yt, load_json, _api_url):
    mock_yt.add_select_rows_response(
        query='some FROM [//some/path] WHERE some="some_id"',
        filename='select_rows_response.json',
    )
    async with aiohttp.ClientSession(loop=loop) as session:
        response = await session.get(
            _api_url + '/select_rows',
            headers={
                'X-YT-Parameters': _to_yson_str(
                    {'query': 'some FROM [//some/path] WHERE some="some_id"'},
                ),
            },
        )
    content = yt.yson.loads(await response.read())
    assert content == load_json('select_rows_response.json')


async def test_select_rows_with_table(loop, mock_yt, load_json, _api_url):
    path = '//some/path'
    mock_yt.add_select_rows_response(
        table=path,
        query='some FROM [//some/path] WHERE some="some_id"',
        filename='select_rows_response.json',
    )
    headers = {
        'X-YT-Parameters': _to_yson_str(
            {
                'query': 'some FROM [//some/path] WHERE some="some_id"',
                'path': path,
            },
        ),
    }
    async with aiohttp.ClientSession(loop=loop) as session:
        response = await session.get(
            _api_url + '/select_rows', headers=headers,
        )
    content = yt.yson.loads(await response.read())
    assert content == load_json('select_rows_response.json')


async def _exists(path: str, _yt_client):
    response = await _yt_client.get(
        '/exists', headers={'X-YT-Parameters': _to_yson_str({'path': path})},
    )
    assert response.status == 200
    return yt.yson.loads(response.content)


async def _check_exists(path: str, is_exists: bool, _yt_client):
    plain_path_exists = await _exists(path, _yt_client)
    assert plain_path_exists == is_exists

    path_attributes_exists = await _exists(path + '/@', _yt_client)
    assert path_attributes_exists == is_exists


@pytest.mark.parametrize(
    'path, is_exists', [('//some/path', True), ('//some/unknown/path', False)],
)
async def test_exists(path, is_exists, mock_yt, _yt_client):
    if is_exists:
        mock_yt.add_path(path)
    await _check_exists(path, is_exists, _yt_client)


async def test_multiple_path_added_all_exists(mock_yt, _yt_client):
    paths = ['//path/1', '//path/2']

    # prepare all paths at once
    for path in paths:
        mock_yt.add_path(path)

    # we don't use gather for simplicity
    for path in paths:
        await _check_exists(path, True, _yt_client)

    unknown_path = '//path/3'
    await _check_exists(unknown_path, False, _yt_client)


TYPE_ATTRIBUTE = 'type'
TABLE_TYPE = 'table'


# NOTE: we support only nodes with 'table' type now, no nested map_nodes
async def test_get(mock_yt, _yt_client):
    path = '//some/table'
    node_content = {TYPE_ATTRIBUTE: TABLE_TYPE}

    mock_yt.add_path(path, node_content)

    # get without any attributes to table node returns only empty
    # attributes dict
    response = await _yt_get_request(_yt_client, path)
    content = yt.yson.loads(response.content)
    assert content == {'attributes': {}}

    # request to plain path returns only requested attributes
    response = await _yt_get_request(_yt_client, path, [TYPE_ATTRIBUTE])
    content = yt.yson.loads(response.content)
    assert content == {'attributes': {TYPE_ATTRIBUTE: TABLE_TYPE}}

    # request to plain path with unknown attribute name returns empty
    # attributes
    response = await _yt_get_request(_yt_client, path, ['unknown_attribute'])
    content = yt.yson.loads(response.content)
    assert content == {'attributes': {}}

    attributes_path = path + '/@'

    # request to /@ must return node's attributes
    response = await _yt_get_request(_yt_client, attributes_path)
    content = yt.yson.loads(response.content)
    assert content == node_content

    # request to /@ with unknown attribute name must return empty response
    response = await _yt_get_request(
        _yt_client, attributes_path, ['unknown_attribute'],
    )
    content = yt.yson.loads(response.content)
    assert content == {}

    # unknown path
    response = await _yt_get_request(
        _yt_client, '//unknown/path', expected_code=400,
    )
    assert response.headers['X-YT-Response-Code'] == '500'
    content = json.loads(response.content)
    assert content['code'] == 500


async def _yt_get_request(
        _yt_client, path: str, attributes=None, expected_code=200,
):
    params = {'path': path}
    if attributes is not None:
        params['attributes'] = attributes
    response = await _yt_client.get(
        '/get', headers={'X-YT-Parameters': _to_yson_str(params)},
    )
    assert response.status == expected_code
    return response


def _to_yson_str(obj):
    return yt.yson.dumps(obj).decode('utf-8')


def _decode_docs(obj):
    for key in obj:
        if key.endswith('doc'):
            obj[key] = bson.BSON(obj[key].encode()).decode()
    return obj
