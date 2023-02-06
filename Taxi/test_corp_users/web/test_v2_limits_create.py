import pytest


BASE_TAXI_LIMIT = {
    'title': 'Регулярные поездки',
    'client_id': 'client1',
    'service': 'taxi',
    'categories': ['business'],
    'limits': {},
}

BASE_TANKER_LIMIT = {
    'title': 'Лимит на заправки',
    'client_id': 'client1',
    'service': 'tanker',
    'limits': {'orders_cost': {'value': '1000', 'period': 'day'}},
    'fuel_types': ['a95', 'a100_premium'],
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

BASE_ORDERS_LIMIT = {
    'orders_cost': {'value': '1000', 'period': 'month'},
    'orders_amount': {'value': 2, 'period': 'day'},
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


@pytest.mark.parametrize(
    ['post_content', 'expected_result'],
    [
        pytest.param(
            BASE_TAXI_LIMIT,
            {
                'categories': ['business'],
                'client_id': 'client1',
                'counters': {'users': 0},
                'department_id': None,
                'geo_restrictions': [],
                'is_default': False,
                'limits': {'orders_amount': None, 'orders_cost': None},
                'service': 'taxi',
                'time_restrictions': [],
                'title': 'Регулярные поездки',
            },
            id='min fields',
        ),
        pytest.param(
            EATS_LIMIT_WITH_QR,
            {
                'client_id': 'client1',
                'counters': {'users': 0},
                'geo_restrictions': [],
                'department_id': None,
                'is_default': False,
                'is_qr_enabled': True,
                'limits': {
                    'orders_amount': None,
                    'orders_cost': {'period': 'day', 'value': '1000'},
                },
                'service': 'eats2',
                'time_restrictions': [],
                'title': 'Можно оплачивать вендоматы qr',
            },
            id='eats2 with qr',
        ),
        pytest.param(
            {
                **BASE_TAXI_LIMIT,
                'limits': BASE_ORDERS_LIMIT,
                'time_restrictions': BASE_TIME_RESTRICTIONS,
                'geo_restrictions': PROHIBITING_GEO_RESTRICTIONS,
                'department_id': 'dep1',
            },
            {
                'categories': ['business'],
                'client_id': 'client1',
                'counters': {'users': 0},
                'department_id': 'dep1',
                'geo_restrictions': [
                    {
                        'destination': 'destination_restriction_id',
                        'prohibiting_restriction': True,
                        'source': 'source_restriction_1',
                    },
                ],
                'is_default': False,
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
            },
            id='taxi max fields',
        ),
        pytest.param(
            {
                **BASE_DRIVE_LIMIT,
                'time_restrictions': BASE_TIME_RESTRICTIONS,
                'enable_toll_roads': False,
                'department_id': 'dep1',
            },
            {
                'cars_classes': ['everyday'],
                'cities': ['msk'],
                'client_id': 'client1',
                'counters': {'users': 0},
                'department_id': 'dep1',
                'enable_toll_roads': False,
                'is_default': False,
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
            },
            id='drive max fields',
        ),
        pytest.param(
            {
                **BASE_TANKER_LIMIT,
                'time_restrictions': BASE_TIME_RESTRICTIONS,
                'department_id': 'dep1',
            },
            {
                'client_id': 'client1',
                'counters': {'users': 0},
                'department_id': 'dep1',
                'fuel_types': ['a95', 'a100_premium'],
                'geo_restrictions': [],
                'is_default': False,
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
            },
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
async def test_success_post_limit(
        web_app_client, mock_corp_clients, db, post_content, expected_result,
):
    mock_corp_clients.data.get_client_response = GET_CLIENT_MOCK_DATA
    mock_corp_clients.data.get_services_response = GET_SERVICES_MOCK_DATA

    response = await web_app_client.post(
        '/v2/limits/create', json=post_content,
    )
    response_data = await response.json()
    assert response.status == 200, response_data

    db_limit = await db.corp_limits.find_one(
        {'_id': response_data['id']},
        projection={'_id': False, 'created': False, 'updated': False},
    )
    assert db_limit == expected_result

    history_record = await db.corp_history.find_one(
        {'c': 'corp_limits', 'e._id': response_data['id']},
    )
    assert history_record is not None


@pytest.mark.parametrize(
    ['post_content', 'corp_clients_mock', 'status_code', 'expected_response'],
    [
        pytest.param(
            {'name': 'test limit', 'service': 'taxi'},
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'categories is required property'},
                'message': 'Some parameters are invalid',
            },
            id='without base required fields',
        ),
        pytest.param(
            {**BASE_TAXI_LIMIT, **{'categories': ['not_existed_category']}},
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': (
                    '{\'not_existed_category\'} categories are not found'
                ),
            },
            id='incorrect categories',
        ),
        pytest.param(
            {**BASE_TAXI_LIMIT, **{'categories': []}},
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'empty categories',
            },
            id='empty categories',
        ),
        pytest.param(
            {**BASE_DRIVE_LIMIT, **{'limits': {}}},
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'orders_cost is required property'},
                'message': 'Some parameters are invalid',
            },
            id='drive without orders cost',
        ),
        pytest.param(
            {**BASE_DRIVE_LIMIT, **{'tariffs': ['not_existed_tariff']}},
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for tariffs_item: '
                        '\'not_existed_tariff\' '
                        'must be one of [\'standart_offer\', '
                        '\'fix_offer_regular\', '
                        '\'hourly_offer\', \'daily_offer\', '
                        '\'flexible_pack_offer\', '
                        '\'intercity_offer\', \'pack_offer\']'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
            id='incorrect drive tariffs',
        ),
        pytest.param(
            {
                **BASE_TAXI_LIMIT,
                **{
                    'time_restrictions': {  # type: ignore
                        'start_time': '00:00:00',
                        'end_time': '03:00:00',
                    },
                },
            },
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for time_restrictions: '
                        '{\'start_time\': '
                        '\'00:00:00\', \'end_time\': \'03:00:00\'}'
                        ' is not instance of '
                        'list'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
            id='incorrect time_restrictions',
        ),
        pytest.param(
            {
                **BASE_TAXI_LIMIT,
                **{
                    'geo_restrictions': [
                        {'source': 'not_existed_source'},  # type: ignore
                    ],
                },
            },
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'source or destination points are not found',
            },
            id='incorrect geo_restrictions',
        ),
        pytest.param(
            {
                **BASE_TAXI_LIMIT,
                **{
                    'limits': {'orders_amount': 'str'},  # type: ignore
                },
            },
            GET_SERVICES_MOCK_DATA,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value to deserialize OrdersAmountTaxiLimit: '
                        '\'str\' is not instance of dict'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
            id='incorrect orders_amount type',
        ),
        pytest.param(
            {
                **BASE_TAXI_LIMIT,
                **{
                    'title': 'limit',  # type: ignore
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
            id='inactive_taxi_service',
        ),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={'__default__': {'business': 'name.comfort'}},
)
async def test_fail_post_limit(
        web_app_client,
        mock_corp_clients,
        post_content,
        corp_clients_mock,
        status_code,
        expected_response,
):
    mock_corp_clients.data.get_services_response = corp_clients_mock
    mock_corp_clients.data.get_client_response = GET_CLIENT_MOCK_DATA

    response = await web_app_client.post(
        '/v2/limits/create', json=post_content,
    )
    response_data = await response.json()
    assert response.status == status_code, response_data

    assert response_data == expected_response
