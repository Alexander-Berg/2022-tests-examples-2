import pytest


BASE_TAXI_LIMIT = {
    'title': 'Регулярные поездки',
    'service': 'taxi',
    'categories': ['business'],
    'limits': {},
}

EATS2_LIMIT_WITH_QR = {
    'title': 'Оплата по qr разрешена.',
    'service': 'eats2',
    'limits': {},
    'geo_restrictions': [],
    'time_restrictions': [],
    'is_qr_enabled': True,
}

EATS2_LIMIT_WITH_QR_FALSE = {
    'title': 'Оплата по qr разрешена.',
    'service': 'eats2',
    'limits': {},
    'geo_restrictions': [],
    'time_restrictions': [],
    'is_qr_enabled': False,
}

EATS2_LIMIT_WITHOUT_QR = {
    'title': 'Оплата по qr разрешена.',
    'service': 'eats2',
    'limits': {},
    'geo_restrictions': [],
    'time_restrictions': [],
}

BASE_LIMIT_RESPONSE = {
    'can_edit': True,
    'categories': ['econom'],
    'client_id': 'client1',
    'geo_restrictions': [
        {
            'destination': 'destination_restriction_id',
            'source': 'source_restriction_1',
        },
    ],
    'id': 'limit1',
    'limits': {
        'orders_amount': {'period': 'day', 'value': 12},
        'orders_cost': {'period': 'month', 'value': '1000'},
    },
    'service': 'taxi',
    'time_restrictions': [
        {
            'days': ['mo', 'tu', 'we', 'th', 'fr'],
            'end_time': '18:40:00',
            'start_time': '10:30:00',
            'type': 'weekly_date',
        },
    ],
    'title': 'limit',
}


@pytest.mark.parametrize(
    [
        'passport_mock',
        'corp_users_response',
        'expected_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client1',
            EATS2_LIMIT_WITH_QR,
            200,
            EATS2_LIMIT_WITH_QR,
            id='eats_with_qr',
        ),
        pytest.param(
            'client1',
            EATS2_LIMIT_WITH_QR_FALSE,
            200,
            EATS2_LIMIT_WITH_QR_FALSE,
            id='eats_with_qr_false',
        ),
        pytest.param(
            'client1',
            EATS2_LIMIT_WITHOUT_QR,
            200,
            EATS2_LIMIT_WITHOUT_QR,
            id='eats_without_qr',
        ),
        pytest.param(
            'client1',
            BASE_LIMIT_RESPONSE,
            200,
            BASE_LIMIT_RESPONSE,
            id='success-path',
        ),
        pytest.param(
            'client1',
            {
                'message': 'Not found',
                'code': 'NOT_FOUND',
                'reason': 'Limit client1 not found',
            },
            404,
            {
                'message': 'Not found',
                'code': 'NOT_FOUND',
                'reason': 'Limit client1 not found',
            },
            id='not-found',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_get_limit_proxy(
        taxi_corp_real_auth_client,
        mock_corp_users,
        passport_mock,
        corp_users_response,
        expected_code,
        expected_response,
):
    mock_corp_users.data.get_limit_response = corp_users_response
    mock_corp_users.data.get_limit_code = expected_code

    response = await taxi_corp_real_auth_client.get(
        '/2.0/limits/{}'.format('limit1'),
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_response


@pytest.mark.parametrize(
    ['passport_mock', 'limit_id', 'status_code'],
    [
        pytest.param('client1', 'not_existed_limit', 404, id='not found'),
        pytest.param('client1', 'limit3_3', 403, id='not client1 limit'),
    ],
    indirect=['passport_mock'],
)
async def test_get_limit_fail(
        taxi_corp_real_auth_client, passport_mock, limit_id, status_code,
):
    response = await taxi_corp_real_auth_client.get(
        '/2.0/limits/{}'.format(limit_id),
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    [
        'passport_mock',
        'corp_users_search_response',
        'expected_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client3',
            {
                'limits': [BASE_LIMIT_RESPONSE],
                'limit': 1,
                'offset': 0,
                'total_amount': 1,
            },
            200,
            {
                'limits': [BASE_LIMIT_RESPONSE],
                'limit': 1,
                'offset': 0,
                'total_amount': 1,
            },
            id='common-flow',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_search_limits_proxy(
        taxi_corp_real_auth_client,
        mock_corp_users,
        passport_mock,
        corp_users_search_response,
        expected_code,
        expected_response,
):
    mock_corp_users.data.search_limit_response = corp_users_search_response
    mock_corp_users.data.search_limit_code = expected_code

    params = {'limit': '1', 'offset': '0', 'service': 'taxi'}
    response = await taxi_corp_real_auth_client.get(
        '/2.0/limits', params=params,
    )
    response_data = await response.json()
    assert response.status == expected_code, response_data
    assert response_data == expected_response

    assert mock_corp_users.search_limits.next_call()['request'].query == dict(
        params, client_id='client3', performer_department_id='dep1',
    )


@pytest.mark.parametrize(
    [
        'passport_mock',
        'post_content',
        'corp_users_response',
        'status_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client1',
            BASE_TAXI_LIMIT,
            {'id': 'new_limit'},
            200,
            {'id': 'new_limit'},
            id='success-path',
        ),
        pytest.param(
            'client1',
            EATS2_LIMIT_WITH_QR,
            {'id': 'new_limit'},
            200,
            {'id': 'new_limit'},
            id='success-path',
        ),
        pytest.param(
            'client1',
            BASE_TAXI_LIMIT,
            {
                'message': 'Limit validation error',
                'code': 'limit-validation-error',
                'reason': 'Geo restrictions not found',
            },
            400,
            {
                'message': 'Limit validation error',
                'code': 'limit-validation-error',
                'reason': 'Geo restrictions not found',
            },
            id='bad-request',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_create_limit_proxy(
        taxi_corp_real_auth_client,
        passport_mock,
        mock_corp_users,
        post_content,
        corp_users_response,
        status_code,
        expected_response,
):
    mock_corp_users.data.create_limit_response = corp_users_response
    mock_corp_users.data.create_limit_code = status_code

    response = await taxi_corp_real_auth_client.post(
        '/2.0/limits', json=post_content,
    )

    response_data = await response.json()
    assert response.status == status_code, response_data
    assert response_data == expected_response


@pytest.mark.parametrize(
    [
        'passport_mock',
        'limit_id',
        'post_content',
        'corp_users_response',
        'status_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client1',
            'limit1',
            BASE_TAXI_LIMIT,
            {},
            200,
            {},
            id='success-path',
        ),
        pytest.param(
            'client1',
            'limit1',
            BASE_TAXI_LIMIT,
            {
                'message': 'Limit with name already exists',
                'code': 'limit-duplicate-error',
                'reason': 'Limit with name already exists',
            },
            200,
            {
                'message': 'Limit with name already exists',
                'code': 'limit-duplicate-error',
                'reason': 'Limit with name already exists',
            },
            id='bad-requests',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_update_limit_proxy(
        taxi_corp_real_auth_client,
        passport_mock,
        mock_corp_users,
        limit_id,
        post_content,
        corp_users_response,
        status_code,
        expected_response,
):
    mock_corp_users.data.update_limit_response = corp_users_response
    mock_corp_users.data.update_limit_code = status_code

    response = await taxi_corp_real_auth_client.put(
        '/2.0/limits/{}'.format(limit_id), json=post_content,
    )

    response_data = await response.json()
    assert response.status == status_code, response_data
    assert response_data == expected_response


@pytest.mark.parametrize(
    [
        'passport_mock',
        'limit_id',
        'corp_users_response',
        'status_code',
        'expected_response',
    ],
    [
        pytest.param('client1', 'limit1', {}, 200, {}, id='success-path'),
        pytest.param(
            'client3',
            'limit3_3',
            None,
            404,
            {
                'code': 'GENERAL',
                'errors': [
                    {'code': 'GENERAL', 'text': 'Department not found'},
                ],
                'message': 'Department not found',
            },
            id='other dep',
        ),
        pytest.param(
            'client3',
            'limit3_2_with_users',
            {
                'message': 'Limit has users',
                'code': 'limit-has-users',
                'reason': 'Limit 80624ca913ad44258808aed7c53a3d071 has users',
            },
            400,
            {
                'message': 'Limit has users',
                'code': 'limit-has-users',
                'reason': 'Limit 80624ca913ad44258808aed7c53a3d071 has users',
            },
            id='limit has users',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_delete_limit_proxy(
        taxi_corp_real_auth_client,
        mock_corp_users,
        passport_mock,
        limit_id,
        corp_users_response,
        status_code,
        expected_response,
):
    mock_corp_users.data.delete_limit_response = corp_users_response
    mock_corp_users.data.delete_limit_code = status_code

    response = await taxi_corp_real_auth_client.delete(
        '/2.0/limits/{}'.format(limit_id),
    )

    response_data = await response.json()
    assert response.status == status_code, response_data
    assert response_data == expected_response
