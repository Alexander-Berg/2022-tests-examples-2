# pylint: disable=redefined-outer-name, protected-access
import asyncio

import pytest

from taxi import config
from taxi import settings
from taxi.clients import http_client
from taxi.clients import tvm

from taxi_corp.clients import corp_integration_api


URL = 'http://corp-integration-api.taxi.dev.yandex.net'


@pytest.fixture
async def client(loop, db, simple_secdist):
    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield corp_integration_api.CorpIntegrationApiClient(
            settings=settings.Settings(),
            config=config.Config(db),
            session=session,
            tvm_client=tvm.TVMClient(
                service_name=corp_integration_api.TVM_SERVICE_NAME,
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


@pytest.mark.parametrize(
    ['request_example'],
    [
        (
            {
                'client_id': 'client_id',
                'source_app': 'corpweb',
                'route': [{'geopoint': [10, 10]}],
                'order_price': '100.00',
                'tariff_class': 'class',
            },
        ),
        ({'retries_cnt': 10, 'retry_interval': 1000, 'timeout': 1},),
    ],
)
async def test_corp_paymentmethods(
        client,
        patch_aiohttp_session,
        response_mock,
        request_example,
        mockserver,
):
    response_example = {
        'methods': [
            {
                'type': 'corp',
                'id': 'corp-client_id',
                'label': 'label',
                'description': '',
                'cost_center': 'error',
                'cost_center_fields': [
                    {
                        'id': 'cost_center',
                        'title': 'Центр затрат',
                        'value': 'командировка',
                    },
                ],
                'hide_user_cost': False,
                'user_id': 'user_id',
                'client_comment': 'comment',
                'currency': 'RUB',
                'can_order': False,
                'order_disable_reason': 'You can\'t order',
                'zone_available': True,
            },
        ],
    }

    @mockserver.json_handler('/corp-int-api/v1/corp_paymentmethods')
    def patch_request(*args, **kwargs):
        return response_example

    response = await client.corp_paymentmethods('phone_id', **request_example)
    assert response == response_example
    assert patch_request.has_calls


async def test_get_contract_by_client_id(
        client, patch_aiohttp_session, response_mock, mockserver,
):

    client_id = '9638b1c2d4004bb5b42f5f5c668c0319'
    response_example = {
        'client_id': '9638b1c2d4004bb5b42f5f5c668c0319',
        'contract_id': '73734/17',
    }

    @mockserver.json_handler('/corp-int-api/v1/client')
    def patch_request(*args, **kwargs):
        return response_example

    response = await client.get_contract_by_client_id(client_id)
    assert response == response_example['contract_id']
    assert patch_request.has_calls


async def test_retry_timeout(
        client, patch, patch_aiohttp_session, response_mock, mockserver,
):
    @patch(
        'taxi_corp.clients.corp_integration_api.CorpIntegrationApiClient.'
        '_raise_for_status',
    )
    def _raise_for_status(*args, **kwargs):
        raise asyncio.TimeoutError()

    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    with pytest.raises(corp_integration_api.RequestRetriesExceeded) as exc:
        await client._request(
            'POST',
            '/1.0/location',
            data={},
            retries_cnt=10,
            retry_interval=0,
            timeout=0,
        )

    assert 'retries' in str(exc)
    assert len(_raise_for_status.calls) == 10
