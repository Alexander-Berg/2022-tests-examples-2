import pytest

ORDER_1 = {
    'client_id': 'client_id_1',
    'closed_at': '2019-03-09T13:30:00+03:00',
    'courier_phone_id': '+79998887766',
    'created_at': '2019-03-09T13:30:00+03:00',
    'destination_address': 'destination_address',
    'discount': '69.0000',
    'final_cost': '220.0000',
    'vat': '44.0000',
    'final_cost_with_vat': '264.0000',
    'id': 'order_id_1',
    'order_calculation': [
        {
            'name': 'Комбо-набор 2',
            'cost': '1210.00',
            'vat': '242.0000',
            'cost_with_vat': '1452.0000',
            'modifiers': [],
            'count': 1,
        },
        {
            'name': 'Пицца Кальцоне',
            'cost': '616.00',
            'vat': '123.2000',
            'cost_with_vat': '739.2000',
            'modifiers': [],
            'count': 2,
        },
        {
            'name': 'Соус',
            'cost': '44.00',
            'vat': '8.8000',
            'cost_with_vat': '52.8000',
            'modifiers': [
                {
                    'name': 'Кисло-сладкий',
                    'cost': '0.00',
                    'vat': '0.0000',
                    'cost_with_vat': '0.0000',
                    'count': 1,
                },
                {
                    'name': 'Сырный',
                    'cost': '0.00',
                    'vat': '0.0000',
                    'cost_with_vat': '0.0000',
                    'count': 1,
                },
            ],
            'count': 1,
        },
        {
            'name': 'Доставка',
            'cost': '0.00',
            'vat': '0.0000',
            'cost_with_vat': '0.0000',
        },
    ],
    'restaurant_address': [{'title': 'Адрес', 'value': 'ул. Строителей'}],
    'restaurant_name': 'restaurant_name',
    'status': 'confirmed',
    'user_id': 'user_id_1',
    'yandex_uid': 'yandex_uid',
    'currency': 'RUB',
    'department_id': 'department_id',
}
ORDER_2 = {
    'client_id': 'client_id_1',
    'closed_at': '2019-04-10T13:30:00+03:00',
    'corp_discount': {
        'sum': '50.0000',
        'vat': '10.0000',
        'with_vat': '60.0000',
    },
    'corp_discount_reverted': False,
    'corp_discount_version': 1,
    'courier_phone_id': '+79998887766',
    'created_at': '2019-04-10T13:30:00+03:00',
    'destination_address': 'destination_address',
    'discount': '69.0000',
    'final_cost': '220.0000',
    'vat': '44.0000',
    'final_cost_with_vat': '264.0000',
    'id': 'order_id_2',
    'order_calculation': [
        {
            'cost': '40.0000',
            'name': 'Роллы',
            'vat': '8.0000',
            'cost_with_vat': '48.0000',
        },
    ],
    'restaurant_address': [{'title': 'Адрес', 'value': 'ул. Строителей'}],
    'restaurant_name': 'restaurant_name',
    'status': 'confirmed',
    'user_id': 'user_id_1',
    'yandex_uid': 'yandex_uid',
    'currency': 'RUB',
    'department_id': 'department_id',
}

ORDER_3 = {
    **ORDER_2,  # type: ignore
    'id': 'order_id_3',
    'user_id': 'user_id_2',
    'department_id': 'department_id_2',
    'created_at': '2019-05-10T13:30:00+03:00',
    'closed_at': '2019-05-10T13:30:00+03:00',
}


@pytest.mark.pgsql('corp_orders', files=('orders.sql',))
@pytest.mark.parametrize(
    'parameters, status, expected_json',
    [
        pytest.param(
            {'client_id': 'client_id_1'},
            200,
            {'orders': [ORDER_3, ORDER_2, ORDER_1]},
            id='search_by_client',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'since_datetime': '2019-03-09T00:00:00+03:00',
                'till_datetime': '2019-05-01T00:00:00+03:00',
            },
            200,
            {'orders': [ORDER_2, ORDER_1]},
            id='search_by_client_and_time_all_orders',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'since_datetime': '2019-04-01T00:00:00+03:00',
                'till_datetime': '2019-05-01T00:00:00+03:00',
            },
            200,
            {'orders': [ORDER_2]},
            id='search_by_client_and_time_filter_order',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'since_datetime': '2019-02-01T00:00:00+03:00',
                'till_datetime': '2019-03-01T00:00:00+03:00',
            },
            200,
            {'orders': []},
            id='search_by_client_and_time_no_orders',
        ),
        pytest.param(
            {'client_id': 'client_id_1', 'user_id': 'user_id_1'},
            200,
            {'orders': [ORDER_2, ORDER_1]},
            id='search_by_user',
        ),
        pytest.param(
            {'client_id': 'client_id_1', 'department_ids': 'department_id_2'},
            200,
            {'orders': [ORDER_3]},
            id='search_by_department',
        ),
        pytest.param(
            {'client_id': 'client_id_1', 'department_id': 'test'},
            200,
            {'orders': []},
            id='search_by_department_fail',
        ),
        pytest.param(
            {'client_id': 'client_id_1', 'department_id': 'department_id'},
            200,
            {'orders': [ORDER_2, ORDER_1]},
            id='search_by_department',
        ),
    ],
)
async def test_orders_eats_find(
        web_app_client, web_context, parameters, status, expected_json,
):
    response = await web_app_client.get(
        '/v1/orders/eats/find', params=parameters,
    )
    response_json = await response.json()
    assert response_json == expected_json
    assert response.status == status


@pytest.mark.pgsql('corp_orders', files=('orders.sql',))
@pytest.mark.parametrize(
    'parameters, status, expected_json',
    [
        pytest.param(
            {},
            400,
            {
                'code': 'wrong-parameters',
                'details': {},
                'message': (
                    'One of \'client_id\', \'user_id\' should be provided'
                ),
                'status': 'error',
            },
            id='wrong_params',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'since_datetime': '2019-03-09T00:00:00+03:00',
            },
            400,
            {
                'code': 'wrong-parameters',
                'details': {},
                'message': (
                    'Either both or zero datetime parameters'
                    'should be provided'
                ),
                'status': 'error',
            },
            id='only_since_datetime_param',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'till_datetime': '2019-03-09T00:00:00+03:00',
            },
            400,
            {
                'code': 'wrong-parameters',
                'details': {},
                'message': (
                    'Either both or zero datetime parameters'
                    'should be provided'
                ),
                'status': 'error',
            },
            id='only_till_datetime_param',
        ),
        pytest.param(
            {'limit': 'abc', 'offset': 'def', 'user_id': 'user_id_1'},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for limit: '
                        '\'abc\' is not instance of int'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
            id='wrong_pagination',
        ),
    ],
)
async def test_orders_eats_find_fail(
        web_app_client, web_context, parameters, status, expected_json,
):
    response = await web_app_client.get(
        '/v1/orders/eats/find', params=parameters,
    )
    response_json = await response.json()
    assert response_json == expected_json
    assert response.status == status
