import aiohttp
import bson
import pytest
import yt.yson

pytest_plugins = ['taxi_tests.plugins.mocks.mock_yt']


@pytest.fixture(scope='session')
def _api_url(testsuite_session_context):
    return testsuite_session_context.mockserver.base_url + 'yt/api/v3'


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


async def test_select_rows(loop, mock_yt, load_json, _api_url):
    mock_yt.add_select_rows_response(
        query='some FROM [//some/path] WHERE some="some_id"',
        filename='select_rows_response.json',
    )
    async with aiohttp.ClientSession(loop=loop) as session:
        response = await session.get(
            _api_url + '/select_rows',
            headers={
                'X-YT-Parameters': yt.yson.dumps(
                    {'query': 'some FROM [//some/path] WHERE some="some_id"'},
                ).decode('utf-8'),
            },
        )
    content = yt.yson.loads(await response.read())
    assert content == load_json('select_rows_response.json')


def _decode_docs(obj):
    for key in obj:
        if key.endswith('doc'):
            obj[key] = bson.BSON(obj[key].encode()).decode()
    return obj
