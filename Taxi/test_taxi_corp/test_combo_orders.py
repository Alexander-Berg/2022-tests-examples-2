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
    'class': 'econom',
    'route_type': 'ONE_A_MANY_B',
    'common_point': {
        'country': 'Россия',
        'geopoint': [37.615981, 55.767492],
        'fullname': 'Москва, ...',
    },
    'orders': [
        {
            'phone': '+79998887766',
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
            ],
        },
    ],
}

SUCCESS_RESPONSE = {
    '_id': 'order_id',
    'code': 'ORDER_CREATED',
    'status': {
        'description': 'active',
        'full': 'search',
        'simple': 'Такси приедет через 10 мин.',
    },
}

PAYMENT_METHODS_FAILED = {
    'code': 'GENERAL',
    'message': 'Персональный лимит на корпоративные поездки закончился',
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
            {'orders': [SUCCESS_RESPONSE]},
            200,
            {'orders': [SUCCESS_RESPONSE]},
            200,
        ),
        pytest.param(
            BASE_CLIENT,
            {**BASE_REQUEST, **{'user_points': []}},
            {},
            400,
            {
                'code': 'invalid-input',
                'details': {
                    '': [
                        'Additional properties are not allowed'
                        ' (\'user_points\' was '
                        'unexpected)',
                    ],
                },
                'message': 'Invalid input',
                'status': 'error',
            },
            400,
        ),
        pytest.param(
            BASE_CLIENT,
            {
                **BASE_REQUEST,
                **{
                    'orders': [
                        copy.deepcopy(
                            BASE_REQUEST['orders'][0],  # type: ignore
                        ),
                        copy.deepcopy(
                            BASE_REQUEST['orders'][0],  # type: ignore
                        ),
                    ],
                },
            },
            {'orders': [SUCCESS_RESPONSE, PAYMENT_METHODS_FAILED]},
            200,
            {'orders': [SUCCESS_RESPONSE, PAYMENT_METHODS_FAILED]},
            200,
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED)
async def test_create_order(
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
    @mockserver.json_handler('/corp-combo-orders/v1/orders/create')
    async def _mock_create_routes(request):
        return mockserver.make_response(
            json=combo_response_body, status=combo_response_status,
        )

    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{BASE_CLIENT}/combo_orders/create',
        json=request_body,
        headers={'X-Application-Version': '0.0.100'},
    )
    response_json = await response.json()
    assert response.status == expected_status, response_json
    assert response_json == expected_response_body

    if expected_status != 400:
        combo_request_body = copy.deepcopy(request_body)
        _replace_phones_with_pd_ids(combo_request_body)
        combo_request_body['client_id'] = passport_mock
        combo_request_body['created_by'] = '{}_uid'.format(passport_mock)
        mock_call = _mock_create_routes.next_call()
        assert mock_call['request'].json == combo_request_body


def _replace_phones_with_pd_ids(data: dict):
    for order in data['orders']:
        order['personal_phone_id'] = 'pd_id'
        for point in order['user_points']:
            point.pop('user_phone')
            point['user_personal_phone_id'] = 'pd_id'
