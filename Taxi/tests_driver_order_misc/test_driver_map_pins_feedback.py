import pytest


@pytest.mark.experiments3()
async def test_ok(taxi_driver_order_misc, load_json):
    response = await taxi_driver_order_misc.post(
        '/driver/v1/map_pins/v1/feedback',
        headers=load_json('auth.json'),
        json={
            'category_id': 'toilet',
            'id': 'id',
            'price': 100,
            'parking_price': 0,
            'comment': 'ololo',
        },
    )

    assert response.status_code == 200
    assert not response.text
