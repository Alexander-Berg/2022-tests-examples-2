import pytest


@pytest.mark.parametrize(
    [
        'request_json',
        'eats_user_header',
        'expected_response_code',
        'expected_rows_count',
    ],
    [
        (
            {
                'place_id': '49000',
                'place_slug': 'kfc',
                'place_name': 'КФС',
                'place_business_type': 'restaurant',
                'location': [49.21738, 18.27184],
                'surge_level': 2,
                'delivery_time': '2019-12-31T23:58:59+00:00',
            },
            'user_id=24171285, personal_phone_id=phone_id',
            200,
            1,
        ),
        (
            {
                'place_id': '49000',
                'place_slug': 'kfc',
                'place_name': 'КФС',
                'place_business_type': 'restaurant',
                'location': [49.21738, 18.27184],
                'surge_level': 2,
                'delivery_time': '2019-12-31T23:58:59+00:00',
            },
            '',
            401,
            0,
        ),
    ],
    ids=['200 response', '401 response'],
)
@pytest.mark.pgsql('eats_surge_notify')
async def test_get_surge_subscribe(
        # ---- fixtures ----
        taxi_eats_surge_notify,
        pgsql,
        # ---- parameters ----
        request_json,
        eats_user_header,
        expected_response_code,
        expected_rows_count,
):
    response = await taxi_eats_surge_notify.post(
        '/internal/eats-surge-notify/v1/surge-subscribe',
        headers={
            'X-Idempotency-Token': '123456789.0123456',
            'X-Device-Id': 'device_id',
            'X-Eats-Session': '7217218579821',
            'X-Eats-User': eats_user_header,
        },
        json=request_json,
    )
    assert response.status_code == expected_response_code

    cursor = pgsql['eats_surge_notify'].cursor()
    cursor.execute('SELECT COUNT(*) from eats_surge_notify.subscriptions')
    rows_inserted = list(cursor)[0][0]
    assert rows_inserted == expected_rows_count
