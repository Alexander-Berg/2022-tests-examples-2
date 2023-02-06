from unittest import mock

import aiohttp
import pytest

from taxi.clients import tvm
from taxi.clients import uantifraud


async def test_uantifraud_v1_subvention_check_order_queries_remote_body(
        uantifraud_service, client,
):
    request = _build_request()
    await client.check_order_for_subvention(request)
    assert uantifraud_service.times_called == 1
    request = uantifraud_service.next_call()['request']
    assert request.json == {
        'order': {
            'id': 'order_id',
            'transporting_time': 60,
            'transporting_distance': 1000,
        },
        'subvention': {'type': 'single_ride'},
    }


@pytest.mark.parametrize(
    'header,value',
    (('Content-Type', 'application/json'), ('X-Ya-Service-Ticket', 'bla-bla')),
)
async def test_uantifraud_v1_subvention_check_order_queries_remote_headers(
        uantifraud_service, client, header, value,
):
    request = _build_request()
    await client.check_order_for_subvention(request)
    assert uantifraud_service.times_called == 1
    request = uantifraud_service.next_call()['request']
    assert request.headers[header] == value


@pytest.mark.parametrize(
    'status,expected',
    (
        ('allow', uantifraud.AntiFraudDecision.ALLOW),
        ('block', uantifraud.AntiFraudDecision.BLOCK),
    ),
)
async def test_uantifraud_v1_subvention_check_order_check_decision(
        mockserver, client, status, expected,
):
    @mockserver.json_handler('/uantifraud/v1/subvention/check_order')
    def _handler(request):
        return {'status': status}

    request = _build_request()
    response = await client.check_order_for_subvention(request)
    assert response.status == expected


async def test_uantifraud_v1_subvention_check_order_retries_when_fails(
        mockserver, client,
):
    @mockserver.json_handler('/uantifraud/v1/subvention/check_order')
    def _handler(request):
        return mockserver.make_response(
            status=500, json={'status': 'error', 'code': 'oops'},
        )

    request = _build_request()
    with pytest.raises(uantifraud.RequestRetriesExceeded):
        await client.check_order_for_subvention(request)
    assert _handler.times_called == 3


@pytest.fixture(name='uantifraud_service')
def make_uantifraud_service(mockserver):
    @mockserver.json_handler('/uantifraud/v1/subvention/check_order')
    def _handler(request):
        return {'status': 'allow'}

    yield _handler


def _build_request():
    return uantifraud.SubventionCheckOrderRequest(
        order=uantifraud.AntiFraudOrder(
            order_id='order_id', duration=60, distance=1000,
        ),
        subvention=uantifraud.AntiFraudSubvention(type='single_ride'),
    )


@pytest.fixture(name='client')
def make_client(session, tvm_client):
    return uantifraud.UAntiFraudClient(
        session=session,
        tvm_client=tvm_client,
        cfg=mock.Mock(
            UANTIFRAUD_CLIENT_QOS={
                '__default__': {'attempts': 3, 'timeout-ms': 200},
            },
        ),
    )


@pytest.fixture(name='session')
async def make_session():
    session = aiohttp.client.ClientSession()
    yield session
    await session.close()


@pytest.fixture(name='tvm_client')
def make_tvm_client(session):
    return tvm.TVMClient(
        service_name='test',
        secdist={
            'settings_override': {
                'TVM_SERVICES': {'uantifraud': {'id': 1, 'secret': 'secret'}},
            },
        },
        config=mock.Mock(
            TVM_RULES=[{'dst': 'uantifraud', 'src': 'test'}],
            TVM_REQUEST_RETRY=1,
            TVM_REQUEST_TIMEOUT=1000,
        ),
        session=session,
    )


@pytest.fixture(autouse=True)
def tvm_service(patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'bla-bla'}
