import pytest


def make_vendor_response_json(restaurants, roles):
    return {
        'isSuccess': True,
        'payload': {
            'id': 7,
            'restaurants': restaurants,
            'isFastFood': True,
            'timezone': 'Europe/Moscow',
            'roles': roles,
            'firstLoginAt': '2020-08-28T15:11:25+03:00',
        },
    }


@pytest.mark.parametrize(
    'partner_id, roles, permissions, mock_times',
    [
        pytest.param(111, [], ['permission.restaurant.functionality'], 0),
        pytest.param(
            112,
            [{'id': 4, 'title': 'Управляющий', 'role': 'ROLE_MANAGER'}],
            ['permission.restaurant.management'],
            1,
        ),
        pytest.param(
            113,
            [
                {'id': 3, 'title': 'Оператор', 'role': 'ROLE_OPERATOR'},
                {'id': 4, 'title': 'Управляющий', 'role': 'ROLE_MANAGER'},
            ],
            ['permission.restaurant.management'],
            1,
        ),
    ],
)
@pytest.mark.redis_store(
    ['sadd', 'partner:places:111', '1', '2', '5'],
    ['sadd', 'partner:roles:111', 'ROLE_OPERATOR'],
)
async def test_response_200(
        taxi_eats_restapp_authorizer,
        partner_id,
        roles,
        permissions,
        mockserver,
        mock_times,
):
    @mockserver.json_handler(f'/eats-vendor/api/v1/server/users/{partner_id}')
    def mock_vendor(request):
        return mockserver.make_response(
            status=200, json=make_vendor_response_json([1, 2, 5], roles),
        )

    response = await taxi_eats_restapp_authorizer.post(
        '/v1/user-access/check',
        json={
            'partner_id': partner_id,
            'permissions': permissions,
            'place_ids': [1, 2, 5],
        },
    )

    assert mock_vendor.times_called == mock_times

    assert response.status_code == 200


@pytest.mark.parametrize(
    'partner_id, places, roles, permissions, mock_times, expected_places,'
    'expected_permissions',
    [
        pytest.param(
            111,
            [],
            [],
            ['permission.restaurant.management'],
            0,
            [],
            ['permission.restaurant.management'],
        ),
        pytest.param(
            112,
            [2, 6, 7],
            [
                {'id': 3, 'title': 'Оператор', 'role': 'ROLE_OPERATOR'},
                {'id': 4, 'title': 'Управляющий', 'role': 'ROLE_MANAGER'},
            ],
            ['permission.restaurant.management'],
            1,
            [6, 7],
            [],
        ),
        pytest.param(
            113,
            [2, 6, 7],
            [{'id': 3, 'title': 'Оператор', 'role': 'ROLE_OPERATOR'}],
            ['permission.restaurant.management'],
            1,
            [6, 7],
            ['permission.restaurant.management'],
        ),
    ],
)
@pytest.mark.redis_store(
    ['sadd', 'partner:places:111', '1', '2', '5'],
    ['sadd', 'partner:roles:111', 'ROLE_OPERATOR'],
)
async def test_response_403(
        taxi_eats_restapp_authorizer,
        partner_id,
        places,
        roles,
        permissions,
        mockserver,
        mock_times,
        expected_permissions,
        expected_places,
):
    @mockserver.json_handler(f'/eats-vendor/api/v1/server/users/{partner_id}')
    def mock_vendor(request):
        return mockserver.make_response(
            status=200, json=make_vendor_response_json([1, 2, 5], roles),
        )

    response = await taxi_eats_restapp_authorizer.post(
        '/v1/user-access/check',
        json={
            'partner_id': partner_id,
            'permissions': permissions,
            'place_ids': places,
        },
    )

    assert mock_vendor.times_called == mock_times

    assert response.status_code == 403
    response_json = response.json()['details']
    assert response_json['permissions'] == expected_permissions
    assert response_json['place_ids'] == expected_places
