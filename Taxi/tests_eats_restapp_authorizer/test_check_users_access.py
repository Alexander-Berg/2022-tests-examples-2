# pylint: disable=redefined-outer-name

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


@pytest.fixture
def mock_vendor_200(mockserver, request):
    @mockserver.json_handler('/eats-vendor/api/v1/server/users/112')
    def _mock_vendor_112(request):
        return mockserver.make_response(
            status=200,
            json=make_vendor_response_json(
                [1, 2, 5],
                [{'id': 4, 'title': 'Управляющий', 'role': 'ROLE_MANAGER'}],
            ),
        )

    @mockserver.json_handler('/eats-vendor/api/v1/server/users/113')
    def _mock_vendor_113(request):
        return mockserver.make_response(
            status=200,
            json=make_vendor_response_json(
                [1, 2, 5],
                [
                    {'id': 3, 'title': 'Оператор', 'role': 'ROLE_OPERATOR'},
                    {'id': 4, 'title': 'Управляющий', 'role': 'ROLE_MANAGER'},
                ],
            ),
        )

    @mockserver.json_handler('/eats-vendor/api/v1/server/users/114')
    def _mock_vendor_114(request):
        return mockserver.make_response(
            status=200,
            json=make_vendor_response_json(
                [1, 2, 5],
                [{'id': 3, 'title': 'Оператор', 'role': 'ROLE_OPERATOR'}],
            ),
        )


@pytest.mark.parametrize(
    'partner_ids, permissions',
    [
        pytest.param([111, 112], ['permission.restaurant.functionality']),
        pytest.param([112, 113], ['permission.restaurant.management']),
    ],
)
@pytest.mark.redis_store(
    ['sadd', 'partner:places:111', '1', '2', '5'],
    ['sadd', 'partner:roles:111', 'ROLE_OPERATOR'],
)
async def test_response_200(
        taxi_eats_restapp_authorizer,
        mock_vendor_200,
        partner_ids,
        permissions,
):
    response = await taxi_eats_restapp_authorizer.post(
        '/v1/user-access/check-bulk',
        json={
            'partner_ids': partner_ids,
            'permissions': permissions,
            'place_ids': [1, 2, 5],
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'partner_ids, places, permissions, expected_response',
    [
        pytest.param(
            [111, 112],
            [],
            ['permission.restaurant.management'],
            [
                {
                    'partner_id': 111,
                    'details': {
                        'permissions': ['permission.restaurant.management'],
                        'place_ids': [],
                    },
                },
            ],
        ),
        pytest.param(
            [111, 112, 113, 114],
            [2, 6, 7],
            ['permission.restaurant.management'],
            [
                {
                    'partner_id': 111,
                    'details': {
                        'permissions': ['permission.restaurant.management'],
                        'place_ids': [6, 7],
                    },
                },
                {
                    'partner_id': 112,
                    'details': {'permissions': [], 'place_ids': [6, 7]},
                },
                {
                    'partner_id': 113,
                    'details': {'permissions': [], 'place_ids': [6, 7]},
                },
                {
                    'partner_id': 114,
                    'details': {
                        'permissions': ['permission.restaurant.management'],
                        'place_ids': [6, 7],
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.redis_store(
    ['sadd', 'partner:places:111', '1', '2', '5'],
    ['sadd', 'partner:roles:111', 'ROLE_OPERATOR'],
)
async def test_response_403(
        taxi_eats_restapp_authorizer,
        mock_vendor_200,
        partner_ids,
        places,
        permissions,
        expected_response,
):
    response = await taxi_eats_restapp_authorizer.post(
        '/v1/user-access/check-bulk',
        json={
            'partner_ids': partner_ids,
            'permissions': permissions,
            'place_ids': places,
        },
    )

    assert response.status_code == 403
    response_json = response.json()['partners']
    assert response_json == expected_response
