import copy

import pytest


CORP_USER_PHONES_SUPPORTED = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]

BASE_CLIENT = 'client1'


BASE_REQUEST = {
    'route_type': 'ONE_A_MANY_B',
    'common_point': {
        'country': 'Россия',
        'geopoint': [37.615981, 55.767492],
        'fullname': 'Москва, ...',
    },
    'user_points': [
        {
            'user_phone': '+79997778876',
            'point': {
                'country': 'Россия',
                'geopoint': [37.625594, 55.764347],
                'fullname': 'Москва, ...',
            },
        },
        {
            'user_phone': '+79997778877',
            'point': {
                'country': 'Россия',
                'geopoint': [37.636494, 55.759846],
                'fullname': 'Москва, ...',
            },
        },
        {
            'user_phone': '+79997778878',
            'point': {
                'country': 'Россия',
                'geopoint': [37.636494, 55.759846],
                'fullname': 'Москва, ...',
            },
        },
    ],
}

BASE_RESPONSE = {
    'route_task_id': '79',
    'task_status': 'done',
    'result': {
        'route_type': 'ONE_A_MANY_B',
        'common_point': {
            'country': 'Россия',
            'geopoint': [37.615981, 55.767492],
            'fullname': 'Москва',
        },
        'routes': [
            {
                'user_points': [
                    {
                        'user_personal_phone_id': 'per_1',
                        'point': {
                            'country': 'Россия',
                            'geopoint': [37.625594, 55.764347],
                            'fullname': 'СпБ',
                        },
                    },
                ],
            },
            {
                'user_points': [
                    {
                        'user_personal_phone_id': 'per_2',
                        'point': {
                            'country': 'Россия',
                            'geopoint': [37.636494, 55.759846],
                            'fullname': 'Казань',
                        },
                    },
                    {
                        'user_personal_phone_id': 'per_1',
                        'point': {
                            'country': 'Россия',
                            'geopoint': [37.625594, 55.764347],
                            'fullname': 'СпБ',
                        },
                    },
                ],
            },
        ],
    },
}


@pytest.mark.parametrize(
    [
        'passport_mock',
        'request_body',
        'combo_response_body',
        'combo_response_status',
        'expected_response_body',
        'expected_status',
    ],
    [
        pytest.param(
            BASE_CLIENT,
            BASE_REQUEST,
            {'route_task_id': '4', 'task_status': 'queued'},
            200,
            {'route_task_id': '4', 'task_status': 'queued'},
            200,
        ),
        pytest.param(
            BASE_CLIENT,
            {**BASE_REQUEST, **{'user_points': []}},
            {},
            400,
            {
                'code': 'invalid-input',
                'details': {'user_points': ['[] is too short']},
                'message': 'Invalid input',
                'status': 'error',
            },
            400,
        ),
        pytest.param(
            BASE_CLIENT,
            BASE_REQUEST,
            {'code': 'ROUTE_TASK_ALREADY_CREATED', 'message': 'err'},
            409,
            {'code': 'ROUTE_TASK_ALREADY_CREATED', 'message': 'err'},
            409,
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED)
async def test_create_route_task(
        taxi_corp_real_auth_client,
        mockserver,
        pd_patch,
        passport_mock,
        request_body,
        combo_response_body,
        combo_response_status,
        expected_response_body,
        expected_status,
):
    @mockserver.json_handler('/corp-combo-orders/v1/routes/create')
    async def _mock_create_routes(request):
        return mockserver.make_response(
            json=combo_response_body, status=combo_response_status,
        )

    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{BASE_CLIENT}/combo_routes/create',
        json=request_body,
        headers={'X-Idempotency-Token': 'test_idempotency_token'},
    )
    response_json = await response.json()
    assert response.status == expected_status, response_json
    assert response_json == expected_response_body

    if expected_status != 400:
        combo_request_body = copy.deepcopy(request_body)
        _replace_phones_with_pd_ids(combo_request_body)
        combo_request_body['client_id'] = passport_mock
        mock_call = _mock_create_routes.next_call()
        assert mock_call['request'].json == combo_request_body
        assert (
            mock_call['request'].headers['X-Idempotency-Token']
            == 'test_idempotency_token'
        )


def _replace_phones_with_pd_ids(data: dict):
    for point in data['user_points']:
        point.pop('user_phone')
        point['user_personal_phone_id'] = 'pd_id'


def _replace_pd_ids_with_phones(data: dict):
    for route in data['result']['routes']:
        for point in route['user_points']:
            point['user_phone'] = '+' + point.pop('user_personal_phone_id')
    return data


@pytest.mark.parametrize(
    [
        'passport_mock',
        'combo_response_body',
        'combo_response_status',
        'expected_response_body',
        'expected_status',
    ],
    [
        pytest.param(
            BASE_CLIENT,
            {**BASE_RESPONSE, **{'client_id': BASE_CLIENT}},
            200,
            _replace_pd_ids_with_phones(copy.deepcopy(BASE_RESPONSE)),
            200,
        ),
        pytest.param(
            BASE_CLIENT,
            {
                'route_task_id': 'task_id',
                'task_status': 'queued',
                'client_id': BASE_CLIENT,
            },
            200,
            {'route_task_id': 'task_id', 'task_status': 'queued'},
            200,
        ),
        pytest.param(
            BASE_CLIENT,
            {'code': 'ROUTE_TASK_NOT_FOUND', 'message': ''},
            404,
            {'code': 'ROUTE_TASK_NOT_FOUND', 'message': ''},
            404,
        ),
        pytest.param(
            BASE_CLIENT,
            {
                **_replace_pd_ids_with_phones(copy.deepcopy(BASE_RESPONSE)),
                **{'client_id': 'other_client'},
            },
            200,
            {
                'code': 'ROUTES_TASK_IS_INACCESSIBLE',
                'errors': [
                    {
                        'code': 'ROUTES_TASK_IS_INACCESSIBLE',
                        'text': 'routes task is inaccessible',
                    },
                ],
                'message': 'routes task is inaccessible',
            },
            403,
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED)
async def test_get_route_task(
        taxi_corp_real_auth_client,
        mockserver,
        pd_patch,
        passport_mock,
        combo_response_body,
        combo_response_status,
        expected_response_body,
        expected_status,
):
    @mockserver.json_handler('/corp-combo-orders/v1/routes/result')
    async def _mock_result_routes(request):
        return mockserver.make_response(
            json=combo_response_body, status=combo_response_status,
        )

    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{BASE_CLIENT}/combo_routes/result',
        params={'route_task_id': '1'},
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
    assert response_json == expected_response_body
