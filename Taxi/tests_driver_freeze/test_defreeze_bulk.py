import pytest


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({}, 400),
        ({'drivers': [{'unique_driver_id': 'id1'}]}, 400),
        ({'drivers': [{'unique_driver_id': 'id1', 'car_id': '123'}]}, 400),
        (
            {
                'drivers': [
                    {
                        'unique_driver_id': 'id1',
                        'car_id': '',
                        'order_id': '22',
                    },
                ],
            },
            200,
        ),
        (
            {
                'drivers': [
                    {
                        'unique_driver_id': 'id1',
                        'car_id': '123',
                        'order_id': '22',
                    },
                ],
            },
            200,
        ),
    ],
)
async def test_response_code(taxi_driver_freeze, request_body, response_code):
    response = await taxi_driver_freeze.post(
        'defreeze-bulk', json=request_body,
    )
    assert response.status_code == response_code


async def test_defreeze_bulk(taxi_driver_freeze, mongodb):
    params = {
        'drivers': [
            {
                'unique_driver_id': 'id1',
                'car_id': 'car1',
                'order_id': 'order1',
            },
            {'unique_driver_id': 'id2', 'car_id': 'car2', 'order_id': ''},
            {'unique_driver_id': 'id3', 'car_id': '', 'order_id': 'order3'},
            {
                'unique_driver_id': 'id4',
                'car_id': 'car4',
                'order_id': 'order4',
            },
        ],
    }
    response = await taxi_driver_freeze.post('defreeze-bulk', json=params)
    assert response.status_code == 200

    assert response.json() == {
        'drivers': [
            {'unique_driver_id': f'id{i}', 'defreezed': True}
            for i in range(1, 5)
        ],
    }

    assert not mongodb.frozen_contractors.find_one({'l': 'id1'})
    assert mongodb.frozen_contractors.find_one({'l': 'id2'})
    assert mongodb.frozen_contractors.find_one({'l': 'id3'})
