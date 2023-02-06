import typing

import pytest


ORDER_BASE: typing.Dict[str, object] = {
    'client_id': 'client_id',
    'user_id': 'user_id',
    'yandex_uid': 'yandex_uid',
    'account_id': 999,
    'drive_user_id': '3a896838-cdba-4d1c-9f34-af1bbb8232ae',
    'duration': 24,
    'tariff': 'Автотест _3',
    'total_sum': '100.00',
    'vat': '20.00',
    'total_sum_with_vat': '120.00',
    'finish_point_coordinates': [37.64015961, 55.73690033],
    'finish_point_address': '',
    'start_point_coordinates': [37.64015961, 55.73690033],
    'start_point_address': '',
    'city': '',
    'timezone': 'Europe/Moscow',
    'car_model': 'kia_rio',
    'car_number': 'б491вг968',
    'total_mileage': 0,
    'currency': 'RUB',
}

ORDER_000 = {
    **ORDER_BASE,  # type: ignore
    'id': '000',
    'created_at': '2020-01-12T13:00:00+0000',
    'updated_at': '2020-01-12T13:00:00+0000',
    'started_at': '2020-01-12T16:00:00+0300',
    'finished_at': '2020-01-12T16:00:00+0300',
}

ORDER_001 = {
    **ORDER_BASE,  # type: ignore
    'id': '001',
    'department_id': 'department_id',
    'created_at': '2020-01-12T14:00:00+0000',
    'updated_at': '2020-01-12T14:00:00+0000',
    'started_at': '2020-01-12T17:00:00+0300',
    'finished_at': '2020-01-12T17:00:00+0300',
}

ORDER_002 = {
    **ORDER_001,  # type: ignore
    'id': '002',
    'department_id': 'department_id_2',
    'finished_at': '2020-01-12T15:00:00+0300',
}


@pytest.mark.pgsql('corp_orders', files=('orders.sql',))
@pytest.mark.parametrize(
    ['parameters', 'status', 'expected_json'],
    [
        (
            {'client_id': 'client_id', 'limit': 2, 'offset': 0},
            200,
            {'limit': 2, 'offset': 0, 'orders': [ORDER_001, ORDER_000]},
        ),
        (
            {
                'client_id': 'client_id',
                'limit': 2,
                'offset': 0,
                'user_id': 'user_id',
            },
            200,
            {'limit': 2, 'offset': 0, 'orders': [ORDER_001, ORDER_000]},
        ),
        (
            {
                'client_id': 'client_id',
                'limit': 2,
                'offset': 0,
                'department_ids': 'department_id,department_id_2',
            },
            200,
            {'limit': 2, 'offset': 0, 'orders': [ORDER_001, ORDER_002]},
        ),
        (
            {
                'client_id': 'client_id',
                'limit': 2,
                'offset': 0,
                'user_id': 'user_idXXX',
            },
            200,
            {'limit': 2, 'offset': 0, 'orders': []},
        ),
        (
            {'client_id': 'client_id', 'limit': 1, 'offset': 1},
            200,
            {'limit': 1, 'offset': 1, 'orders': [ORDER_000]},
        ),
        (
            {
                'client_id': 'client_id',
                'since_datetime': '2020-01-12T15:30:00+0300',
                'till_datetime': '2020-01-12T16:30:00+0300',
                'limit': 10,
                'offset': 0,
            },
            200,
            {
                'limit': 10,
                'offset': 0,
                'since_datetime': '2020-01-12T15:30:00+03:00',
                'till_datetime': '2020-01-12T16:30:00+03:00',
                'orders': [ORDER_000],
            },
        ),
        (
            {
                'client_id': 'client_id',
                'since_datetime': '2020-01-12T15:59:00+0300',
                'limit': 2,
                'offset': 0,
            },
            400,
            {
                'code': 'wrong-parameters',
                'details': {},
                'message': (
                    'Either both or zero datetime parametersshould be provided'
                ),
                'status': 'error',
            },
        ),
        (
            {'client_id': 'client_id_unknown'},
            200,
            {'limit': 100, 'offset': 0, 'orders': []},
        ),
        (
            {'not_client_id': 'client_id'},
            400,
            {
                'code': 'wrong-parameters',
                'details': {},
                'message': 'client_id should be provided',
                'status': 'error',
            },
        ),
    ],
)
async def test_orders_drive_find(
        web_app_client, web_context, parameters, status, expected_json,
):
    response = await web_app_client.get(
        '/v1/orders/drive/find', params=parameters,
    )
    response_json = await response.json()
    assert response_json == expected_json
    assert response.status == status
