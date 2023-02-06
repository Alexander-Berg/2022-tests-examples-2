import pytest

USER_ID = 'user_id'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '4003514353',
    'X-Request-Language': 'ru',
}

BASIC_REQUEST = {
    'order_id': 'order_id',
    'origin_point_b': {
        'point': [45.45, 46.46],
        'address': 'Панкратьевский пер. 12',
        'walk_time': 80.00,
    },
    'route': [[45.47, 46.48], [45.49, 46.50]],
}


async def test_save(taxi_alt):
    response = await taxi_alt.post(
        'alt_b/v1/save', BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.pgsql('alt_b', files=['current_alt_b_pins_order.sql'])
@pytest.mark.parametrize(
    'order_id, expected_status, json_file',
    [
        ('not_exists', 404, ''),
        ('order_id', 200, 'expected_get_by_order_response.json'),
    ],
)
async def test_get_by_order(
        taxi_alt, load_json, order_id, expected_status, json_file,
):
    response = await taxi_alt.post(
        'alt_b/v1/get_by_order', {'order_id': order_id}, headers=PA_HEADERS,
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        expected_response = load_json(json_file)
        assert response.json() == expected_response


@pytest.mark.pgsql('alt_b', files=['current_alt_b_pins_order_finished.sql'])
@pytest.mark.parametrize(
    'order_id, expected_status, json_file',
    [('order_id', 200, 'expected_get_by_order_finished_response.json')],
)
@pytest.mark.experiments3(filename='exp3_alt_b_route.json')
async def test_get_by_finished_order(
        taxi_alt, load_json, order_id, expected_status, json_file,
):
    response = await taxi_alt.post(
        'alt_b/v1/get_by_order', {'order_id': order_id}, headers=PA_HEADERS,
    )
    assert response.status_code == expected_status

    resp_json = response.json()
    expected_response = load_json(json_file)
    assert resp_json['point'] == expected_response['point']
    assert resp_json['seconds_after_finish'] > 0
    assert resp_json['info_block'] == expected_response['info_block']


@pytest.mark.pgsql('alt_b', files=['current_alt_b_pins_user.sql'])
@pytest.mark.parametrize(
    'user_id, expected_status, json_file',
    [
        ('not_exists', 404, ''),
        ('user_id', 200, 'expected_get_by_user_response.json'),
    ],
)
async def test_get_by_user(
        taxi_alt, load_json, user_id, expected_status, json_file,
):
    response = await taxi_alt.post(
        'alt_b/v1/get_by_user', {'user_id': user_id}, headers=PA_HEADERS,
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        expected_response = load_json(json_file)
        assert response.json() == expected_response


@pytest.mark.parametrize(
    'uri, headers, body',
    [
        ('/4.0/pedestrian-route/cancel', PA_HEADERS, {'order_id': 'order_id'}),
        (
            '/internal/pedestrian-route/cancel',
            {},
            {'order_id': 'order_id', 'new_order_status': 'CANCELLED'},
        ),
        (
            '/internal/pedestrian-route/cancel',
            {},
            {'order_id': 'order_id', 'new_order_status': 'ACTIVE'},
        ),
    ],
)
@pytest.mark.pgsql('alt_b', files=['current_alt_b_pins_order.sql'])
async def test_finish(taxi_alt, uri, headers, body):
    first_get_response = await taxi_alt.post(
        'alt_b/v1/get_by_order', {'order_id': 'order_id'}, headers=PA_HEADERS,
    )
    assert first_get_response.status_code == 200

    cancel_response = await taxi_alt.post(uri, body, headers=headers)
    assert cancel_response.status_code == 200

    second_get_response = await taxi_alt.post(
        'alt_b/v1/get_by_order', {'order_id': 'order_id'}, headers=PA_HEADERS,
    )

    if (
            uri == '/internal/pedestrian-route/cancel'
            and body['new_order_status'] == 'ACTIVE'
    ):
        assert second_get_response.status_code == 200
    else:
        assert second_get_response.status_code == 404
