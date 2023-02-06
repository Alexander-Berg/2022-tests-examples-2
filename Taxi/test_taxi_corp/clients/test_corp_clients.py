# pylint: disable=redefined-outer-name
import pytest

from taxi.clients import http_client
from taxi.clients.helpers import base_client

BASE_URL = '$mockserver/corp-clients'


@pytest.fixture
async def client(loop, db, simple_secdist):
    from taxi import config
    from taxi.clients import tvm
    from taxi_corp.clients import corp_clients

    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield corp_clients.CorpClientsClient(
            session=session,
            tvm_client=tvm.TVMClient(
                service_name='developers',
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


async def test_get_contracts(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_contracts(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/contracts',
        },
    ]


async def test_get_contracts_is_active(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_contracts(client_id='client_id', is_active=True)
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id', 'is_active': 'True'},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/contracts',
        },
    ]


async def test_contracts_settings_update(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.update_contract_settings(
        contract_id='contract_id', data={'low_balance_threshold': '100'},
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'contract_id': 'contract_id'},
                'json': {'low_balance_threshold': '100'},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'POST',
            'url': f'{BASE_URL}/v1/contracts/settings/update',
        },
    ]


async def test_get_client(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_client(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/clients',
        },
    ]


async def test_create_client(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    data = {'name': 'Client', 'country': 'rus', 'yandex_login': 'login'}

    await client.create_client(data=data)
    assert _request.calls == [
        {
            'kwargs': {'json': data},
            'log_extra': None,
            'return_binary': False,
            'method': 'POST',
            'url': f'{BASE_URL}/v1/clients/create',
        },
    ]


async def test_update_client(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    data = {'name': 'Client', 'country': 'rus', 'yandex_login': 'login'}

    await client.update_client(
        client_id='client_id', data=data, yandex_uid='yandex_uid',
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id'},
                'json': data,
                'headers': {'X-Yandex-Uid': 'yandex_uid'},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'PATCH',
            'url': f'{BASE_URL}/v1/clients',
        },
    ]


async def test_get_services(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_services(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/services',
        },
    ]


async def test_get_service_taxi(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_service_taxi(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/services/taxi',
        },
    ]


async def test_get_service_cargo(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_service_cargo(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/services/cargo',
        },
    ]


async def test_get_service_drive(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_service_drive(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/services/drive',
        },
    ]


async def test_get_service_eats(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_service_eats(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/services/eats',
        },
    ]


async def test_get_service_eats2(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_service_eats2(client_id='client_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'client_id': 'client_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': f'{BASE_URL}/v1/services/eats2',
        },
    ]


async def test_update_service_taxi(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.update_service_taxi(
        client_id='client_id', data={'is_active': True, 'is_visible': True},
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id'},
                'json': {'is_active': True, 'is_visible': True},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'PATCH',
            'url': f'{BASE_URL}/v1/services/taxi',
        },
    ]


async def test_update_service_cargo(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.update_service_cargo(
        client_id='client_id', data={'is_active': True, 'is_visible': True},
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id'},
                'json': {'is_active': True, 'is_visible': True},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'PATCH',
            'url': f'{BASE_URL}/v1/services/cargo',
        },
    ]


async def test_update_service_drive(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.update_service_drive(
        client_id='client_id', data={'is_active': True, 'is_visible': True},
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id'},
                'json': {'is_active': True, 'is_visible': True},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'PATCH',
            'url': f'{BASE_URL}/v1/services/drive',
        },
    ]


async def test_update_service_eats(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.update_service_eats(
        client_id='client_id', data={'is_active': True, 'is_visible': True},
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id'},
                'json': {'is_active': True, 'is_visible': True},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'PATCH',
            'url': f'{BASE_URL}/v1/services/eats',
        },
    ]


async def test_update_service_eats2(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.update_service_eats2(
        client_id='client_id', data={'is_active': True, 'is_visible': True},
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id'},
                'json': {'is_active': True, 'is_visible': True},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'PATCH',
            'url': f'{BASE_URL}/v1/services/eats2',
        },
    ]
