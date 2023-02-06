import pytest


@pytest.mark.experiments3()
@pytest.mark.now('2021-12-25T00:00:00+00:00')
async def test_ok(
        taxi_driver_order_misc,
        driver_trackstory,
        driver_app_profiles,
        load_json,
):
    response = await taxi_driver_order_misc.get(
        '/driver/v1/map_pins/v1/nearest',
        headers=load_json('auth.json'),
        params={
            'category': 'toilet',
            'latitude': '55.706410',
            'longitude': '37.385548',
        },
    )

    assert response.status_code == 200
    assert response.json() == load_json('stub.json')
