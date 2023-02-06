# pylint: disable=redefined-outer-name, protected-access
import pytest

from taxi import discovery
from taxi.clients import support_gateway


@pytest.fixture
def mock_support_gateway(patch_aiohttp_session, response_mock):
    support_gateway_service = discovery.find_service('support_gateway')

    def _wrapper(expected_url, expected_kwargs, response=None):
        if response is None:
            response = {}

        @patch_aiohttp_session(support_gateway_service.url)
        def _request(method, url, **kwargs):
            assert url == support_gateway_service.url + expected_url
            assert kwargs == expected_kwargs
            return response_mock(json=response)

        return _request

    return _wrapper


@pytest.fixture
def support_gateway_client(test_taxi_app):
    support_gateway_service = discovery.find_service('support_gateway')

    client = support_gateway.SupportGatewayClient(
        support_gateway_service,
        session=test_taxi_app.session,
        tvm_client=test_taxi_app.tvm,
    )
    return client


@pytest.mark.parametrize(
    'method, url, expected_kwargs, sg_response',
    [
        (
            'get',
            '/some_url',
            {
                'headers': {'Content-Type': 'application/json'},
                'json': None,
                'data': None,
                'params': None,
            },
            {},
        ),
        (
            'post',
            '/other_url',
            {
                'headers': {'Content-Type': 'application/json'},
                'json': None,
                'data': None,
                'params': None,
            },
            {'some': 'value'},
        ),
    ],
)
async def test_request(
        mock_support_gateway,
        support_gateway_client,
        method,
        url,
        expected_kwargs,
        sg_response,
):
    sg_mock = mock_support_gateway(url, expected_kwargs, sg_response)
    response = await support_gateway_client._request(url, method=method)
    assert response == sg_response
    assert sg_mock.calls


@pytest.mark.parametrize(
    'api_method, params, expected_kwargs',
    [
        (
            'some_method',
            None,
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'method': 'some_method',
                    'params': {'service': 'taxi-support-chat'},
                },
                'data': None,
                'params': None,
            },
        ),
        (
            'another_method',
            {'some': 'value', 'another': 123},
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'method': 'another_method',
                    'params': {
                        'service': 'taxi-support-chat',
                        'some': 'value',
                        'another': 123,
                    },
                },
                'data': None,
                'params': None,
            },
        ),
    ],
)
async def test_service_request(
        mock_support_gateway,
        support_gateway_client,
        api_method,
        params,
        expected_kwargs,
):
    sg_mock = mock_support_gateway('/api/service', expected_kwargs)
    await support_gateway_client._service_request(
        api_method=api_method, params=params,
    )
    assert sg_mock.calls


@pytest.mark.parametrize(
    'kwargs, expected_kwargs',
    [
        (
            {
                'chat_id': 'test1',
                'chat_type': 'client_support',
                'event': 'new_message',
                'updated': 123456,
            },
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'method': 'notify',
                    'params': {
                        'service': 'taxi-support-chat',
                        'chat_id': 'test1',
                        'chat_type': 'client_support',
                        'event': 'new_message',
                        'updated': 123456,
                    },
                },
                'data': None,
                'params': None,
            },
        ),
        (
            {
                'chat_id': 'test2',
                'chat_type': 'driver_support',
                'event': 'read_message',
                'updated': 23451,
                'user_id': 'user1',
                'request_id': '123',
            },
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'method': 'notify',
                    'params': {
                        'service': 'taxi-support-chat',
                        'chat_id': 'test2',
                        'chat_type': 'driver_support',
                        'event': 'read_message',
                        'updated': 23451,
                        'user_id': 'user1',
                        'request_id': '123',
                    },
                },
                'data': None,
                'params': None,
            },
        ),
    ],
)
async def test_notify(
        mock_support_gateway, support_gateway_client, kwargs, expected_kwargs,
):
    sg_mock = mock_support_gateway('/api/service', expected_kwargs)
    await support_gateway_client.notify(**kwargs)
    assert sg_mock.calls
