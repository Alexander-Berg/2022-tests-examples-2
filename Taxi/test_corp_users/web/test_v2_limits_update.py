import pytest


BASE_TAXI_LIMIT = {
    'title': 'Регулярные поездки',
    'client_id': 'client1',
    'service': 'taxi',
    'categories': ['business'],
    'limits': {},
}

BASE_ORDERS_LIMIT = {
    'orders_cost': {'value': '1000', 'period': 'month'},
    'orders_amount': {'value': 2, 'period': 'day'},
}

BASE_DRIVE_LIMIT = {
    'client_id': 'client1',
    'title': 'Лимит на драйв',
    'service': 'drive',
    'cities': ['msk'],
    'tariffs': ['standart_offer'],
    'cars_classes': ['everyday'],
    'limits': {'orders_cost': {'value': '1000', 'period': 'month'}},
}

EATS_LIMIT_WITH_QR = {
    'client_id': 'client1',
    'title': 'Можно оплачивать вендоматы qr',
    'service': 'eats2',
    'is_qr_enabled': True,
    'limits': {'orders_cost': {'value': '1000', 'period': 'day'}},
}

EATS_LIMIT_WITHOUT_QR = {
    'client_id': 'client1',
    'title': 'Можно оплачивать вендоматы qr',
    'service': 'eats2',
    'is_qr_enabled': False,
    'limits': {'orders_cost': {'value': '1000', 'period': 'day'}},
}

BASE_TANKER_LIMIT = {
    'title': 'Лимит на заправки',
    'client_id': 'client1',
    'service': 'tanker',
    'limits': {'orders_cost': {'value': '1000', 'period': 'day'}},
    'fuel_types': ['a95', 'a100_premium'],
}

BASE_TIME_RESTRICTIONS = [
    {
        'days': ['we', 'tu', 'th', 'sa', 'fr'],
        'start_time': '00:00:00',
        'end_time': '03:00:00',
        'type': 'weekly_date',
    },
]

PROHIBITING_GEO_RESTRICTIONS = [
    {
        'source': 'source_restriction_1',
        'destination': 'destination_restriction_id',
        'prohibiting_restriction': True,
    },
]

GET_SERVICES_MOCK_DATA = {
    'taxi': {'is_active': True, 'is_visible': True},
    'drive': {'is_active': True, 'is_visible': True},
    'tanker': {'is_active': True, 'is_visible': True},
    'eats2': {'is_active': True, 'is_visible': True},
}

GET_CLIENT_MOCK_DATA = {'id': 'client1', 'country': 'rus'}

DRIVE_TASK_MOCK_ID = 'drive_task_id'


@pytest.mark.parametrize(
    [
        'limit_id',
        'post_content',
        'status_code',
        'expected_limit',
        'expected_drive_stq_calls',
    ],
    [
        pytest.param(
            'limit1',
            BASE_TAXI_LIMIT,
            200,
            {
                '_id': 'limit1',
                'categories': ['business'],
                'client_id': 'client1',
                'department_id': None,
                'geo_restrictions': [],
                'limits': {'orders_amount': None, 'orders_cost': None},
                'service': 'taxi',
                'time_restrictions': [],
                'title': 'Регулярные поездки',
            },
            0,
            id='min fields',
        ),
        pytest.param(
            'eats2_limit_id_3',
            EATS_LIMIT_WITH_QR,
            200,
            {
                '_id': 'eats2_limit_id_3',
                'client_id': 'client3',
                'is_qr_enabled': True,
                'limits': {
                    'orders_amount': None,
                    'orders_cost': {'period': 'day', 'value': '1000'},
                },
                'service': 'eats2',
                'geo_restrictions': [],
                'time_restrictions': [],
                'title': 'Можно оплачивать вендоматы qr',
            },
            0,
            id='min fields',
        ),
        pytest.param(
            'eats2_limit_id_2',
            EATS_LIMIT_WITHOUT_QR,
            200,
            {
                '_id': 'eats2_limit_id_2',
                'client_id': 'client3',
                'is_qr_enabled': False,
                'limits': {
                    'orders_amount': None,
                    'orders_cost': {'period': 'day', 'value': '1000'},
                },
                'service': 'eats2',
                'geo_restrictions': [],
                'time_restrictions': [],
                'title': 'Можно оплачивать вендоматы qr',
            },
            0,
            id='min fields',
        ),
        pytest.param(
            'limit3_2',
            {
                **BASE_TAXI_LIMIT,
                'client_id': 'client3',
                'limits': BASE_ORDERS_LIMIT,
                'time_restrictions': BASE_TIME_RESTRICTIONS,
                'geo_restrictions': PROHIBITING_GEO_RESTRICTIONS,
                'department_id': 'dep1',
            },
            200,
            {
                '_id': 'limit3_2',
                'categories': ['business'],
                'client_id': 'client3',
                'department_id': 'dep1',
                'geo_restrictions': [
                    {
                        'destination': 'destination_restriction_id',
                        'prohibiting_restriction': True,
                        'source': 'source_restriction_1',
                    },
                ],
                'limits': {
                    'orders_amount': {'period': 'day', 'value': 2},
                    'orders_cost': {'period': 'month', 'value': '1000'},
                },
                'service': 'taxi',
                'time_restrictions': [
                    {
                        'days': ['we', 'tu', 'th', 'sa', 'fr'],
                        'end_time': '03:00:00',
                        'start_time': '00:00:00',
                        'type': 'weekly_date',
                    },
                ],
                'title': 'Регулярные поездки',
                'counters': {'users': 0},
            },
            0,
            id='taxi max fields',
        ),
        pytest.param(
            'drive_limit',
            {
                **BASE_DRIVE_LIMIT,
                'client_id': 'client3',
                'time_restrictions': BASE_TIME_RESTRICTIONS,
                'enable_toll_roads': False,
                'department_id': 'dep1',
            },
            200,
            {
                '_id': 'drive_limit',
                'cars_classes': ['everyday'],
                'cities': ['msk'],
                'client_id': 'client3',
                'department_id': 'dep1',
                'enable_toll_roads': False,
                'limits': {
                    'orders_amount': None,
                    'orders_cost': {'period': 'month', 'value': '1000'},
                },
                'service': 'drive',
                'tariffs': ['standart_offer'],
                'time_restrictions': [
                    {
                        'days': ['we', 'tu', 'th', 'sa', 'fr'],
                        'end_time': '03:00:00',
                        'start_time': '00:00:00',
                        'type': 'weekly_date',
                    },
                ],
                'title': 'Лимит на драйв',
                'counters': {'users': 1},
            },
            1,
            id='drive max fields',
        ),
        pytest.param(
            'limit3_2_tanker',
            {
                **BASE_TANKER_LIMIT,
                'client_id': 'client3',
                'time_restrictions': BASE_TIME_RESTRICTIONS,
                'department_id': 'dep1',
            },
            200,
            {
                '_id': 'limit3_2_tanker',
                'client_id': 'client3',
                'department_id': 'dep1',
                'fuel_types': ['a95', 'a100_premium'],
                'geo_restrictions': [],
                'is_default': True,
                'limits': {
                    'orders_amount': None,
                    'orders_cost': {'period': 'day', 'value': '1000'},
                },
                'service': 'tanker',
                'time_restrictions': [
                    {
                        'days': ['we', 'tu', 'th', 'sa', 'fr'],
                        'end_time': '03:00:00',
                        'start_time': '00:00:00',
                        'type': 'weekly_date',
                    },
                ],
                'title': 'Лимит на заправки',
                'counters': {'users': 1},
            },
            0,
            id='tanker max fields',
        ),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={'__default__': {'business': 'name.comfort'}},
    CORP_FUEL_TYPES={
        'rus': [
            {'type_id': 'a95', 'tanker_key': 'fuel.a95'},
            {'type_id': 'a100_premium', 'tanker_key': 'fuel.a100_premium'},
        ],
    },
)
async def test_success_put_limit(
        web_app_client,
        patch,
        mock_corp_clients,
        db,
        stq,
        limit_id,
        post_content,
        status_code,
        expected_limit,
        expected_drive_stq_calls,
):
    @patch('corp_users.helpers.limits_helper._generate_drive_task_id')
    def _generate_drive_task_id(*args, **kwargs):
        return DRIVE_TASK_MOCK_ID

    mock_corp_clients.data.get_services_response = GET_SERVICES_MOCK_DATA
    mock_corp_clients.data.get_client_response = GET_CLIENT_MOCK_DATA

    response = await web_app_client.post(
        '/v2/limits/update', params={'limit_id': limit_id}, json=post_content,
    )
    response_data = await response.json()
    assert response.status == status_code, response_data

    db_limit = await db.corp_limits.find_one(
        {'_id': limit_id}, projection={'created': False, 'updated': False},
    )
    assert db_limit == expected_limit

    assert (
        stq.corp_process_users_drive_service.times_called
        == expected_drive_stq_calls
    )
    if stq.corp_process_users_drive_service.times_called:
        stq_call = stq.corp_process_users_drive_service.next_call()
        assert stq_call['id'] == DRIVE_TASK_MOCK_ID
        assert stq_call['kwargs'] == {
            'client_id': 'client3',
            'user_ids': ['test_user_1', 'test_user_4', 'test_user_5'],
        }

        user = await db.corp_users.find_one(
            {'_id': stq_call['kwargs']['user_ids'][0]},
        )
        assert user['services']['drive']['task_id'] == DRIVE_TASK_MOCK_ID

    history_record = await db.corp_history.find_one(
        {'c': 'corp_limits', 'e._id': limit_id},
    )
    assert history_record is not None


@pytest.mark.parametrize(
    [
        'limit_id',
        'post_content',
        'corp_clients_mock',
        'status_code',
        'expected_response',
    ],
    [
        pytest.param(
            'limit3_2_eats2',
            {
                **BASE_TAXI_LIMIT,
                **{'department_id': 'dep1', 'service': 'taxi'},
            },
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Impossible change limit service',
            },
            id='forbidden to change limit service',
        ),
        pytest.param(
            'limit1',
            {
                **BASE_TAXI_LIMIT,
                **{
                    'title': 'default_limit',  # type: ignore
                },
            },
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Limit with this name already exists',
            },
            id='duplicate name',
        ),
        pytest.param(
            'limit1',
            BASE_TAXI_LIMIT,
            {
                'taxi': {'is_active': True, 'is_visible': False},
                'drive': {'is_active': True, 'is_visible': True},
                'tanker': {'is_active': True, 'is_visible': True},
            },
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'taxi is inactive',
            },
            id='inactive taxi service',
        ),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={'__default__': {'business': 'name.comfort'}},
)
async def test_fail_put_limit(
        web_app_client,
        mock_corp_clients,
        db,
        limit_id,
        post_content,
        corp_clients_mock,
        status_code,
        expected_response,
):
    mock_corp_clients.data.get_services_response = corp_clients_mock
    mock_corp_clients.data.get_client_response = GET_CLIENT_MOCK_DATA

    response = await web_app_client.post(
        '/v2/limits/update', params={'limit_id': limit_id}, json=post_content,
    )
    response_data = await response.json()
    assert response.status == status_code, response_data
    assert response_data == expected_response
