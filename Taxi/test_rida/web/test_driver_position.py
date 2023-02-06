import pytest

from test_rida import helpers


async def test_driver_position(taxi_rida_web, mongodb):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/driver/position',
        headers=headers,
        json={'position': [56.45, 45.56], 'heading': 1.234},
    )
    assert response.status == 200

    doc = mongodb.rida_drivers.find_one(
        {'guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'}, {'location': 1},
    )
    assert doc['location']['coordinates'] == [56.45, 45.56]


@pytest.mark.config(
    RIDA_RATE_LIMITER_SETTINGS={
        'v3/driver/position': {
            'rules': [{'max_number_of_requests': 1, 'period_s': 1}],
        },
    },
)
async def test_driver_position_frequent_requests(taxi_rida_web, mongodb):
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/driver/position',
        headers=headers,
        json={'position': [56.45, 45.56], 'heading': 1.234},
    )
    assert response.status == 200

    response = await taxi_rida_web.post(
        '/v3/driver/position',
        headers=headers,
        json={'position': [86.45, 45.56], 'heading': 1.234},
    )
    assert response.status == 200
    doc = mongodb.rida_drivers.find_one(
        {'guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'}, {'location': 1},
    )
    assert doc['location']['coordinates'] == [56.45, 45.56]


@pytest.mark.config(
    RIDA_RATE_LIMITER_SETTINGS={
        'v3/driver/position': {
            'rules': [{'max_number_of_requests': 1, 'period_s': 1}],
        },
    },
)
async def test_rate_limiter_unauthorized_request(taxi_rida_web):
    response = await taxi_rida_web.post(
        '/v3/driver/position',
        headers=helpers.get_auth_headers(1337),  # nonexistent user_id
        json={'position': [56.45, 45.56], 'heading': 1.234},
    )
    assert response.status == 200


@pytest.mark.parametrize(
    ['user_id', 'expected_response_status'],
    [
        pytest.param(1337, 401, id='user_not_found'),
        pytest.param(1234, 200, id='user_device_mismatch'),
    ],
)
async def test_unauthorized_drivers(
        taxi_rida_web, user_id: int, expected_response_status: int,
):
    headers = helpers.get_auth_headers(
        user_id=user_id, device_uuid='unknown_device_uuid',
    )
    response = await taxi_rida_web.post(
        '/v3/driver/position',
        headers=headers,
        json={'position': [56.45, 45.56], 'heading': 1.234},
    )
    assert response.status == expected_response_status
