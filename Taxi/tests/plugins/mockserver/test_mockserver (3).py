# pylint: disable=protected-access
import aiohttp
import pytest

from taxi_tests.plugins import mockserver as mockserver_mod


class Client:
    def __init__(self, *, base_url, session):
        self._session = session
        self._base_url = base_url

    def get(self, path, **kwargs):
        return self._request('GET', path, **kwargs)

    def _request(self, method, path, **kwargs):
        url = _build_url(self._base_url, path)
        return self._session.request(method, url, **kwargs)


def _build_url(base_url, path):
    return '%s/%s' % (base_url.rstrip('/'), path.lstrip('/'))


@pytest.fixture
async def mockserver_client(mockserver):
    async with aiohttp.ClientSession() as session:
        yield Client(base_url=mockserver.base_url, session=session)


async def test_json_handler(mockserver, mockserver_client):
    @mockserver.json_handler('/foo')
    def foo_handler(request):
        return {'msg': 'hello'}

    response = await mockserver_client.get('/foo')
    assert response.status == 200
    data = await response.json()

    assert data == {'msg': 'hello'}


async def test_async_json_handler(mockserver, mockserver_client):
    @mockserver.json_handler('/foo')
    async def foo_handler(request):
        return {'msg': 'hello'}

    response = await mockserver_client.get('/foo')
    assert response.status == 200
    data = await response.json()

    assert data == {'msg': 'hello'}


async def test_handler(mockserver, mockserver_client):
    @mockserver.json_handler('/foo')
    def foo_handler(request):
        return aiohttp.web.Response(body='hello')

    response = await mockserver_client.get('/foo')
    assert response.status == 200
    data = await response.content.read()

    assert data == b'hello'


@pytest.mark.parametrize('path,expected', [('/foo', '/foo'), ('bar', '/bar')])
def test_normalize_mockserver_path(path, expected):
    assert mockserver_mod._normalize_mockserver_path(path) == expected
