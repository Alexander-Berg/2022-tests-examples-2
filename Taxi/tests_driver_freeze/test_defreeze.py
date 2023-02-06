import pytest


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({}, 400),
        ({'unique_driver_id': 'id1'}, 400),
        ({'unique_driver_id': 'id1', 'car_id': 'car1'}, 400),
        (
            {
                'unique_driver_id': 'id1',
                'car_id': 'car1',
                'order_id': 'order1',
            },
            200,
        ),
        (
            {
                'unique_driver_id': 'id2',
                'car_id': 'car1',
                'order_id': 'order1',
            },
            404,
        ),
        (
            {
                'unique_driver_id': 'id1',
                'car_id': 'car1',
                'order_id': 'order2',
            },
            404,
        ),
    ],
)
async def test_response_code(
        taxi_driver_freeze, mongodb, request_body, response_code,
):
    response = await taxi_driver_freeze.post('defreeze', json=request_body)
    assert response.status_code == response_code
    if response_code == 200:
        assert not mongodb.frozen_contractors.find_one({})
    else:
        assert mongodb.frozen_contractors.find_one({})


@pytest.mark.parametrize(
    'driver_id, car_id, order_id, response_code',
    [
        ('id1', 'car1', 'order1', 200),
        ('id2', 'car1', 'order1', 404),
        ('id1', 'car2', 'order1', 404),
        ('id1', 'car1', 'order2', 404),
        ('id1', '', 'order2', 404),
        ('id1', 'car2', '', 404),
        ('id1', '', 'order1', 404),
        ('id1', 'car1', '', 404),
        ('id1', '', '', 404),
    ],
)
async def test_defreeze_params_mongo(
        taxi_driver_freeze,
        mongodb,
        driver_id,
        car_id,
        order_id,
        response_code,
):
    params = {
        'unique_driver_id': driver_id,
        'car_id': car_id,
        'order_id': order_id,
    }
    response = await taxi_driver_freeze.post('defreeze', json=params)
    assert response.status_code == response_code
    if response_code == 200:
        assert not mongodb.frozen_contractors.find_one({})
    else:
        assert response_code == 404
        assert mongodb.frozen_contractors.find_one({})
