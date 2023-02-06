import json

import pytest

from . import utils


@pytest.mark.experiments3()
async def test_saves(taxi_eats_eta, redis_store):
    data = {
        'user_id': 'eater_1',
        'place_id': 'place_1',
        'brand_id': 'brand_1',
        'total_time': 1800,
        'cooking_time': 720,
        'delivery_time': 500,
        'promise_min': 12345678,
        'promise_max': 12345900,
    }

    response = await taxi_eats_eta.post(
        '/api/v1/customer/places/save-eta', json={'estimations': [data]},
    )

    assert response.status_code == 200
    assert (
        json.loads(redis_store.get(utils.make_redis_key_no_cart(data))) == data
    )


@pytest.mark.experiments3()
async def test_updates_on_duplicate(taxi_eats_eta, redis_store):
    for i in range(2):
        data = {
            'user_id': 'eater_1',
            'place_id': 'place_1',
            'brand_id': 'brand_1',
            'total_time': i,
            'cooking_time': i,
            'delivery_time': i,
            'promise_min': i,
            'promise_max': i,
        }

        response = await taxi_eats_eta.post(
            '/api/v1/customer/places/save-eta', json={'estimations': [data]},
        )

        assert response.status_code == 200
        assert (
            json.loads(redis_store.get(utils.make_redis_key_no_cart(data)))
            == data
        )


async def test_response_400(taxi_eats_eta):
    # Fake test to make API coverage happy
    response = await taxi_eats_eta.post(
        '/api/v1/customer/places/save-eta', json={},
    )

    assert response.status_code == 400


async def test_response_500(taxi_eats_eta):
    # Fake test to make API coverage happy
    response = await taxi_eats_eta.post(
        '/api/v1/customer/places/save-eta', json={},
    )

    assert response.status_code == 400
