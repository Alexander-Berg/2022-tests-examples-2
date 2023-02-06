# pylint: disable=redefined-outer-name

import pytest

from taxi.clients import http_client
from taxi.clients.helpers import base_client


@pytest.fixture
async def client(loop, db, simple_secdist):
    from taxi import config
    from taxi.clients import tvm
    from taxi_corp.clients import corp_tariffs

    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield corp_tariffs.CorpTariffsClient(
            session=session,
            tvm_client=tvm.TVMClient(
                service_name='developers',
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


async def test_get_client_tariff_current(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={'tariff': {}}, headers={})

    await client.get_client_tariff_current(
        client_id='client_id', zone_name='zone_name', service='taxi',
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {
                    'client_id': 'client_id',
                    'zone_name': 'zone_name',
                    'application': 'taxi',
                },
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': '$mockserver/corp-tariffs/v1/client_tariff/current',
        },
    ]


async def test_get_client_tariff_plan_current(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={}, headers={})

    await client.get_client_tariff_plan_current(
        client_id='client_id', service='taxi',
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {'client_id': 'client_id', 'service': 'taxi'},
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': '$mockserver/corp-tariffs/v1/client_tariff_plan/current',
        },
    ]


async def test_get_tariff_current(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={'tariff': {}}, headers={})

    await client.get_tariff_current(
        tariff_plan_series_id='tariff_plan_series_id', zone_name='zone_name',
    )
    assert _request.calls == [
        {
            'kwargs': {
                'params': {
                    'tariff_plan_series_id': 'tariff_plan_series_id',
                    'zone_name': 'zone_name',
                },
            },
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': '$mockserver/corp-tariffs/v1/tariff/current',
        },
    ]


async def test_get_tariff(patch, client):
    @patch('taxi.clients.helpers.base_client.BaseClient.request')
    async def _request(
            method, url, log_extra=None, return_binary=False, **kwargs,
    ):
        return base_client.Response(body={'tariff': {}}, headers={})

    await client.get_tariff(tariff_id='tariff_id')
    assert _request.calls == [
        {
            'kwargs': {'params': {'id': 'tariff_id'}},
            'log_extra': None,
            'return_binary': False,
            'method': 'GET',
            'url': '$mockserver/corp-tariffs/v1/tariff',
        },
    ]
