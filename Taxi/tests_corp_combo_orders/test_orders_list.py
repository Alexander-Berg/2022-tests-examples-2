import pytest

BASE_POINT = {
    'geopoint': [1.0, 2.0],
    'fullname': 'Россия, Москва, Большая Никитская улица, 13',
}


@pytest.mark.parametrize(
    ['request_body', 'expected_response'],
    [
        pytest.param(
            {'client_id': 'client_id_1'},
            {
                'orders': [
                    {
                        'id': 'order_id_3',
                        'user_points': [
                            {
                                'user_personal_phone_id': 'user_phone_id_1',
                                'point': BASE_POINT,
                            },
                            {
                                'user_personal_phone_id': 'user_phone_id_3',
                                'point': BASE_POINT,
                            },
                        ],
                    },
                    {
                        'id': 'order_id_2',
                        'user_points': [
                            {
                                'user_personal_phone_id': 'user_phone_id_3',
                                'point': BASE_POINT,
                            },
                        ],
                    },
                    {
                        'id': 'order_id_1',
                        'user_points': [
                            {
                                'user_personal_phone_id': 'user_phone_id_1',
                                'point': BASE_POINT,
                            },
                            {
                                'user_personal_phone_id': 'user_phone_id_2',
                                'point': BASE_POINT,
                            },
                        ],
                    },
                ],
            },
            id='test general',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'finished_date_from': '2021-09-15T21:00:00+00:00',
                'finished_date_to': '2021-09-16T21:00:00+00:00',
            },
            {
                'orders': [
                    {
                        'id': 'order_id_3',
                        'user_points': [
                            {
                                'user_personal_phone_id': 'user_phone_id_1',
                                'point': BASE_POINT,
                            },
                            {
                                'user_personal_phone_id': 'user_phone_id_3',
                                'point': BASE_POINT,
                            },
                        ],
                    },
                ],
            },
            id='test date',
        ),
        pytest.param(
            {'client_id': 'not_existed_client'},
            {'orders': []},
            id='test empty orders',
        ),
    ],
)
@pytest.mark.pgsql('corp_combo_orders', files=['insert_orders.sql'])
async def test_get_orders_list_by_client(
        taxi_corp_combo_orders, request_body, expected_response,
):
    response = await taxi_corp_combo_orders.post(
        '/v1/orders/list', json=request_body,
    )
    assert response.status == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    ['request_body', 'expected_response'],
    [
        pytest.param(
            {
                'user_personal_phone_id': 'user_phone_id_1',
                'client_id': 'client_id_1',
            },
            {
                'orders': [
                    {
                        'id': 'order_id_3',
                        'user_points': [
                            {
                                'user_personal_phone_id': 'user_phone_id_1',
                                'point': BASE_POINT,
                            },
                        ],
                    },
                    {
                        'id': 'order_id_1',
                        'user_points': [
                            {
                                'user_personal_phone_id': 'user_phone_id_1',
                                'point': BASE_POINT,
                            },
                        ],
                    },
                ],
            },
            id='test general',
        ),
        pytest.param(
            {
                'user_personal_phone_id': 'user_phone_id_3',
                'client_id': 'client_id_1',
                'due_date_from': '2021-09-15T20:30:15+00:00',
                'due_date_to': '2021-09-15T20:35:15+00:00',
            },
            {
                'orders': [
                    {
                        'id': 'order_id_3',
                        'user_points': [
                            {
                                'user_personal_phone_id': 'user_phone_id_3',
                                'point': BASE_POINT,
                            },
                        ],
                    },
                ],
            },
            id='test date',
        ),
        pytest.param(
            {
                'user_personal_phone_id': 'user_phone_id_1',
                'client_id': 'client_id_1',
                'limit': 1,
            },
            {
                'orders': [
                    {
                        'id': 'order_id_3',
                        'user_points': [
                            {
                                'user_personal_phone_id': 'user_phone_id_1',
                                'point': BASE_POINT,
                            },
                        ],
                    },
                ],
            },
            id='test limit',
        ),
        pytest.param(
            {
                'user_personal_phone_id': 'not_existed_user_phone_id',
                'client_id': 'client_id_1',
            },
            {'orders': []},
            id='test empty orders',
        ),
    ],
)
@pytest.mark.pgsql('corp_combo_orders', files=['insert_orders.sql'])
async def test_get_orders_list_by_user(
        taxi_corp_combo_orders, request_body, expected_response,
):
    response = await taxi_corp_combo_orders.post(
        '/v1/orders/list', json=request_body,
    )
    assert response.status == 200
    assert response.json() == expected_response
