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


@pytest.mark.experiments3()
async def test_ok(
        taxi_driver_order_misc,
        driver_trackstory,
        driver_app_profiles,
        load_json,
):
    response = await taxi_driver_order_misc.get(
        '/driver/v1/map_pins/v1/categories', headers=load_json('auth.json'),
    )

    assert response.status_code == 200
    assert response.json() == load_json('stub.json')
    check_polling_header(response.headers['X-Polling-Power-Policy'])
