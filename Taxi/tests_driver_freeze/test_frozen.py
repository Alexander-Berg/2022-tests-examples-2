import gzip

import pytest


@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_cache(taxi_driver_freeze, load_binary):
    params = {
        'unique_driver_id': '56f968f07c0aa65c44998e4b',
        'car_id': '123',
        'order_id': '22',
        'freeze_time': 30,
    }
    response = await taxi_driver_freeze.post('freeze', json=params)
    assert response.status_code == 200

    await taxi_driver_freeze.invalidate_caches()

    response = await taxi_driver_freeze.get('frozen')

    assert response.status_code == 200
    assert gzip.decompress(response.content) == load_binary('answer1.fb')

    response = await taxi_driver_freeze.post('defreeze', json=params)
    assert response.status_code == 200

    params = {
        'drivers': [
            {
                'unique_driver_id': '56f968f07c0aa65c44998e4e',
                'car_id': 'car_id2',
                'order_id': 'order2',
                'freeze_time': 30,
            },
            {
                'unique_driver_id': '56f968f07c0aa65c44998e4f',
                'car_id': 'car_id3',
                'order_id': 'order3',
                'freeze_time': 30,
            },
        ],
    }
    response = await taxi_driver_freeze.post('freeze-bulk', json=params)
    assert response.status_code == 200

    await taxi_driver_freeze.invalidate_caches()

    response = await taxi_driver_freeze.get('frozen')

    assert response.status_code == 200
    data = gzip.decompress(response.content)
    assert data == load_binary('answer2a.fb') or data == load_binary(
        'answer2b.fb',
    )
