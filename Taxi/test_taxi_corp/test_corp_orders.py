import typing

import pytest

from taxi_corp.clients import corp_orders

BASE_RESPONSE: typing.Dict[str, typing.List[typing.Dict[str, str]]] = {
    'orders': [],
}
REQUEST_ERROR = {
    'code': 'GENERAL',
    'errors': [{'code': 'GENERAL', 'text': 'Request error'}],
    'message': 'Request error',
}


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    ['params', 'expected_request_params', 'expected_json', 'expected_code'],
    [
        pytest.param(
            {'user_id': 'user1'},
            {
                'client_id': 'client1',
                'limit': 100,
                'offset': 0,
                'user_id': 'user1',
            },
            BASE_RESPONSE,
            200,
            id='list_success',
        ),
        pytest.param(
            {'department_id': 'dep1_1'},
            {
                'client_id': 'client1',
                'limit': 100,
                'offset': 0,
                'department_id': 'dep1_1',
            },
            BASE_RESPONSE,
            200,
            id='list_success_by_department',
        ),
        pytest.param(
            {},
            {'client_id': 'client1', 'limit': 100, 'offset': 0},
            REQUEST_ERROR,
            400,
            id='list_error',
        ),
    ],
)
async def test_orders_eats_find(
        taxi_corp_real_auth_client,
        patch,
        params,
        expected_request_params,
        passport_mock,
        expected_json,
        expected_code,
):
    @patch('taxi_corp.clients.corp_orders.CorpOrdersClient._request')
    async def _request(*args, **kwargs):
        if not params:
            raise corp_orders.RequestError
        return BASE_RESPONSE

    response = await taxi_corp_real_auth_client.get(
        f'/1.0/client/{passport_mock}/eats/orders', params=params,
    )

    assert (await response.json()) == expected_json
    assert response.status == expected_code

    assert _request.calls[0]['kwargs']['params'] == expected_request_params


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    ['params', 'expected_request_params', 'expected_json', 'expected_code'],
    [
        pytest.param(
            {'limit': 2, 'offset': 0},
            {'client_id': 'client1', 'limit': '2', 'offset': '0'},
            {'limit': 2, 'offset': 0, 'orders': []},
            200,
            id='list_success',
        ),
        pytest.param(
            {'limit': 2, 'offset': 0, 'department_id': 'dep1'},
            {
                'client_id': 'client1',
                'limit': '2',
                'offset': '0',
                'department_id': 'dep1',
            },
            {'limit': 2, 'offset': 0, 'orders': []},
            200,
            id='list_success_by_departments',
        ),
        pytest.param(
            {},
            {'client_id': 'client1', 'limit': 100, 'offset': 0},
            REQUEST_ERROR,
            400,
            id='list_error',
        ),
    ],
)
async def test_orders_drive_find(
        taxi_corp_real_auth_client,
        patch,
        params,
        expected_request_params,
        passport_mock,
        expected_json,
        expected_code,
):
    @patch('taxi_corp.clients.corp_orders.CorpOrdersClient._request')
    async def _request(*args, **kwargs):
        if not params:
            raise corp_orders.RequestError
        return {'limit': 2, 'offset': 0, 'orders': []}

    response = await taxi_corp_real_auth_client.get(
        f'/1.0/client/{passport_mock}/drive/orders', params=params,
    )

    assert (await response.json()) == expected_json
    assert response.status == expected_code

    assert _request.calls[0]['kwargs']['params'] == expected_request_params


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    ['params', 'expected_request_params', 'expected_json', 'expected_code'],
    [
        pytest.param(
            {'user_id': 'user1'},
            {
                'client_id': 'client1',
                'limit': 100,
                'offset': 0,
                'user_id': 'user1',
            },
            BASE_RESPONSE,
            200,
            id='list_success',
        ),
        pytest.param(
            {'department_id': 'dep1_1'},
            {
                'client_id': 'client1',
                'limit': 100,
                'offset': 0,
                'department_id': 'dep1_1',
            },
            BASE_RESPONSE,
            200,
            id='list_success_by_department',
        ),
        pytest.param(
            {},
            {'client_id': 'client1', 'limit': 100, 'offset': 0},
            REQUEST_ERROR,
            400,
            id='list_error',
        ),
    ],
)
async def test_orders_tanker_find(
        taxi_corp_real_auth_client,
        patch,
        params,
        expected_request_params,
        passport_mock,
        expected_json,
        expected_code,
):
    @patch('taxi_corp.clients.corp_orders.CorpOrdersClient._request')
    async def _request(*args, **kwargs):
        if not params:
            raise corp_orders.RequestError
        return BASE_RESPONSE

    response = await taxi_corp_real_auth_client.get(
        f'/1.0/client/{passport_mock}/tanker/orders', params=params,
    )

    assert (await response.json()) == expected_json
    assert response.status == expected_code

    assert _request.calls[0]['kwargs']['params'] == expected_request_params
