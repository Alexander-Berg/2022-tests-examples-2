import typing

import pytest


ORDER_BASE: typing.Dict[str, object] = {
    'client_id': 'client_id_1',
    'final_price': '1426.29',
    'station_location': [37.64015961, 55.73690033],
    'fuel_type': 'a100_premium',
    'liters_filled': '24.04',
}

ORDER_ID_1 = {
    **ORDER_BASE,  # type: ignore
    'id': 'order_id_1',
    'user_id': 'user_id_1',
    'created_at': '2021-11-30T10:30:00.123000+03:00',
    'closed_at': '2021-11-30T10:32:00.123000+03:00',
}

ORDER_ID_3 = {
    **ORDER_BASE,  # type: ignore
    'id': 'order_id_3',
    'user_id': 'user_id_2',
    'created_at': '2021-11-30T13:30:00.123000+03:00',
    'closed_at': '2021-11-30T13:32:00.123000+03:00',
}


@pytest.mark.pgsql('corp_orders', files=('tanker_orders.sql',))
@pytest.mark.parametrize(
    ['params', 'status', 'expected_json'],
    [
        pytest.param(
            {'client_id': 'client_id_1', 'limit': 10},
            200,
            {
                'orders': [ORDER_ID_1, ORDER_ID_3],
                'last_closed_at': '2021-11-30T10:32:00.123000',
            },
            id='client',
        ),
        pytest.param(
            {'client_id': 'client_id_1', 'limit': 2, 'user_id': 'user_id_1'},
            200,
            {
                'orders': [ORDER_ID_1],
                'last_closed_at': '2021-11-30T07:32:00.123000',
            },
            id='user',
        ),
        pytest.param(
            {'client_id': 'client_id_1', 'limit': 2, 'user_id': 'user_idXXX'},
            200,
            {'orders': []},
            id='unknown_user',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'since_datetime': '2021-11-30T07:00:00',
                'till_datetime': '2021-11-30T07:40:00',
                'limit': 10,
            },
            200,
            {
                'orders': [ORDER_ID_1],
                'last_closed_at': '2021-11-30T07:32:00.123000',
            },
            id='since_and_till',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'since_datetime': '2021-11-30T07:00:00',
            },
            200,
            {
                'orders': [ORDER_ID_1, ORDER_ID_3],
                'last_closed_at': '2021-11-30T10:32:00.123000',
            },
            id='only_since',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'since_datetime': '2021-11-30T10:00:00',
            },
            200,
            {
                'orders': [ORDER_ID_3],
                'last_closed_at': '2021-11-30T10:32:00.123000',
            },
            id='since_after_order_id_1',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'since_datetime': '2021-11-30T11:32:00',
            },
            200,
            {'orders': []},
            id='since_after_all_orders',
        ),
        pytest.param(
            {'client_id': 'client_id_unknown'},
            200,
            {'orders': []},
            id='unknown_client',
        ),
        pytest.param(
            {'not_client_id': 'client_id_1'},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {'reason': 'client_id is required parameter'},
            },
            id='without_client_id',
        ),
    ],
)
async def test_v2_orders_tanker_get(
        web_app_client, params, status, expected_json,
):
    response = await web_app_client.get('/v2/orders/tanker', params=params)
    response_json = await response.json()
    assert response_json == expected_json
    assert response.status == status
