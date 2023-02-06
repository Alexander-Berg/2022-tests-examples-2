# pylint: disable=invalid-name
import os

import pytest

from taxi import settings
from taxi.util import client_session

from example_service.generated.service.settings import plugin
from example_service.generated.web import run_web

pytestmark = pytest.mark.config(TVM_SERVICES={'example_service': 111})


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


@pytest.fixture(name='mockserver_client')
async def _mockserver_client(mockserver):
    # copy of testsuite fixture, implemented for aiohttp
    # move it into testsuite within TAXIPLATFORM-687 task
    async with client_session.get_client_session() as session:
        yield Client(base_url=mockserver.base_url, session=session)


@pytest.fixture(name='production_web')
def production_web_fixture(aiohttp_client, monkeypatch, loop):
    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.PRODUCTION)
    monkeypatch.setattr(
        plugin,
        'read_settings',
        lambda _: plugin.read_yaml(
            os.path.join(
                os.path.dirname(plugin.__file__), 'settings.production',
            ),
        ),
    )
    return loop.run_until_complete(aiohttp_client(run_web.create_app()))


@pytest.fixture(name='testing_web')
def testing_web_fixture(aiohttp_client, monkeypatch, loop):
    monkeypatch.setattr(settings, 'ENVIRONMENT', settings.TESTING)
    monkeypatch.setattr(
        plugin,
        'read_settings',
        lambda _: plugin.read_yaml(
            os.path.join(os.path.dirname(plugin.__file__), 'settings.testing'),
        ),
    )
    return loop.run_until_complete(aiohttp_client(run_web.create_app()))


async def make_invalid_request(client):
    return await client.get(
        '/example', params=[('name', 'John'), ('name', 'Wick')],
    )


async def make_unexpected_response(client):
    return await client.get(
        '/example', params={'name': 'John', 'sendIntResponse': 1},
    )


async def make_invalid_response(client):
    return await client.get(
        '/example', params={'name': 'John', 'sendIntBody': 1},
    )


async def test_testing_request(testing_web):
    response = await make_invalid_request(testing_web)
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {'reason': 'name: array not expected'},
    }


async def test_testing_unexpected_response(testing_web):
    response = await make_unexpected_response(testing_web)
    assert response.status == 500
    content = await response.json()
    assert content == {
        'code': 'RESPONSE_VALIDATION_ERROR',
        'message': 'Response got unexpected type',
        'details': {'reason': 'Unexpected response <class \'int\'>: 1'},
    }


async def test_testing_invalid_response(testing_web):
    response = await make_invalid_response(testing_web)
    assert response.status == 500
    content = await response.json()
    assert content == {
        'code': 'RESPONSE_VALIDATION_ERROR',
        'message': 'Response validation or serialization failed',
        'details': {
            'reason': (
                'Invalid value for body: 1 is not instance '
                'of api_module.ExampleObject'
            ),
        },
    }


async def test_production_request(production_web):
    response = await make_invalid_request(production_web)
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {},
    }


async def test_production_unexpected_response(production_web):
    response = await make_unexpected_response(production_web)
    assert response.status == 500
    content = await response.json()
    assert content == {
        'code': 'RESPONSE_VALIDATION_ERROR',
        'message': 'Response got unexpected type',
        'details': {},
    }


async def test_production_invalid_response(production_web):
    response = await make_invalid_response(production_web)
    assert response.status == 500
    content = await response.json()
    assert content == {
        'code': 'RESPONSE_VALIDATION_ERROR',
        'message': 'Response validation or serialization failed',
        'details': {},
    }


@pytest.fixture(autouse=True)
def _proxy_localizations_request(patch_aiohttp_session, mockserver_client):
    @patch_aiohttp_session(
        'http://localizations-replica.taxi.yandex.net/v1/keyset', 'GET',
    )
    def _handle_production(*args, **kwargs):
        return mockserver_client.get(
            'localizations-replica/v1/keyset', *args, **kwargs,
        )

    @patch_aiohttp_session(
        'http://localizations-replica.taxi.dev.yandex.net/v1/keyset', 'GET',
    )
    def _handle_testing(*args, **kwargs):
        return mockserver_client.get(
            'localizations-replica/v1/keyset', *args, **kwargs,
        )
