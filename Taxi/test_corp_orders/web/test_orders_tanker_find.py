import typing

import pytest


ORDER_BASE: typing.Dict[str, object] = {
    'client_id': 'client_id_1',
    'yandex_uid': 'yandex_uid_1',
    'department_id': 'department_id_1',
    'price_per_liter': '60.23',
    'preliminary_price': '849.85',
    'final_price': '1426.29',
    'final_price_wo_discount': '1447.93',
    'events_price': '1426.29',
    'discount': '21.64',
    'currency': 'RUB',
    'station_name': 'Тестировочная №1',
    'station_address': 'Кремлевская наб. 1',
    'station_location': [37.64015961, 55.73690033],
    'station_pump': '3',
    'fuel_type': 'a100_premium',
    'fuel_name': 'АИ-100 Ultimate',
    'liters_requested': '14.11',
    'liters_filled': '24.04',
    'liters_log': [
        {'date': '2022-01-13T12:45:11.629000+03:00'},
        {'date': '2022-01-13T12:45:13.657000+03:00'},
        {'date': '2022-01-13T12:45:15.681000+03:00', 'value': 1.34},
        {'date': '2022-01-13T12:45:17.705000+03:00', 'value': 2.67},
    ],
}

ORDER_ID_1 = {
    **ORDER_BASE,  # type: ignore
    'id': 'order_id_1',
    'user_id': 'user_id_1',
    'user_info': {'fullname': 'Innokentiy', 'phone': '+79858869333'},
    'payment_method': 'corp',
    'created_at': '2021-11-30T10:30:00.123000+03:00',
    'closed_at': '2021-11-30T10:32:00.123000+03:00',
    'status': 'Completed',
}

ORDER_ID_2 = {
    **ORDER_BASE,  # type: ignore
    'id': 'order_id_2',
    'user_id': 'user_id_1',
    'user_info': {'fullname': 'Innokentiy', 'phone': '+79858869333'},
    'payment_method': 'card',
    'created_at': '2021-11-30T11:30:00.123000+03:00',
    'status': 'Fueling',
}

ORDER_ID_3 = {
    **ORDER_BASE,  # type: ignore
    'id': 'order_id_3',
    'user_id': 'user_id_2',
    'user_info': {'fullname': 'Arseniy', 'phone': '+79858869334'},
    'payment_method': 'corp',
    'created_at': '2021-11-30T13:30:00.123000+03:00',
    'closed_at': '2021-11-30T13:32:00.123000+03:00',
    'status': 'Completed',
}


@pytest.mark.pgsql('corp_orders', files=('tanker_orders.sql',))
@pytest.mark.parametrize(
    ['parameters', 'status', 'expected_json'],
    [
        (
            {'client_id': 'client_id_1', 'limit': 2, 'offset': 0},
            200,
            {'orders': [ORDER_ID_3, ORDER_ID_2]},
        ),
        (
            {
                'client_id': 'client_id_1',
                'limit': 2,
                'offset': 0,
                'user_id': 'user_id_1',
            },
            200,
            {'orders': [ORDER_ID_2, ORDER_ID_1]},
        ),
        (
            {
                'client_id': 'client_id_1',
                'limit': 2,
                'offset': 0,
                'user_id': 'user_idXXX',
            },
            200,
            {'orders': []},
        ),
        (
            {'client_id': 'client_id_1', 'limit': 1, 'offset': 1},
            200,
            {'orders': [ORDER_ID_2]},
        ),
        (
            {
                'client_id': 'client_id_1',
                'since_datetime': '2021-11-30T10:00:00+03:00',
                'till_datetime': '2021-11-30T10:40:00+03:00',
                'limit': 10,
                'offset': 0,
            },
            200,
            {'orders': [ORDER_ID_1]},
        ),
        (
            {
                'client_id': 'client_id_1',
                'since_datetime': '2021-11-30T10:00:00+03:00',
                'limit': 2,
                'offset': 0,
            },
            400,
            {
                'code': 'wrong-parameters',
                'details': {},
                'message': (
                    'Either both or zero datetime parameters '
                    'should be provided'
                ),
                'status': 'error',
            },
        ),
        ({'client_id': 'client_id_unknown'}, 200, {'orders': []}),
        (
            {'not_client_id': 'client_id_1'},
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
async def test_orders_tanker_find(
        web_app_client, web_context, parameters, status, expected_json,
):
    response = await web_app_client.get(
        '/v1/orders/tanker/find', params=parameters,
    )
    response_json = await response.json()
    assert response_json == expected_json
    assert response.status == status
