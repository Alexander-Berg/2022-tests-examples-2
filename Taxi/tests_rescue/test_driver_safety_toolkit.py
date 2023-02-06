import pytest


def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


@pytest.mark.parametrize(
    'park_id, expected_response',
    [
        ('park1', 'expected_response1.json'),
        ('park2', 'expected_response2.json'),
        ('park3', 'expected_response3.json'),
        ('unknown_park', 'expected_response4.json'),
    ],
)
async def test_driver_safety_toolkit(
        taxi_rescue,
        driver_authorizer,
        mock_fleet_parks_list,
        load_json,
        park_id,
        expected_response,
):
    driver_authorizer.set_session(park_id, 'driver_session', 'driver_uuid')

    response = await taxi_rescue.post(
        'driver/rescue/v1/safety/toolkit',
        params={'park_id': park_id},
        json={'position': [37.590533, 55.733863]},
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': 'driver_session',
        },
    )
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay'] == '4800'
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == load_json('response/' + expected_response)
