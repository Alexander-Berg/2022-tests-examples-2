from tests_driver_categories_api import category_utils

ENDPOINT = '/v1/robot'

HEADERS = {'Content-Type': 'application/json'}

PARK_ID = 'park_0'
DRIVER_ID = 'driver_0'


async def test_enabled(
        taxi_driver_categories_api,
        candidates,
        driver_authorizer,
        driver_tags,
        fleet_parks,
        parks,
        redis_store,
):
    category_utils.set_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['robot', 'econom', 'business'],
    )

    params = {'park_id': PARK_ID, 'driver_id': DRIVER_ID}

    response = await taxi_driver_categories_api.get(
        ENDPOINT, headers=HEADERS, params=params,
    )
    assert response.status_code == 200
    assert response.json() == {'is_enabled': True}


async def test_disabled(
        taxi_driver_categories_api,
        candidates,
        driver_authorizer,
        driver_tags,
        fleet_parks,
        parks,
        redis_store,
):
    category_utils.set_redis_restrictions(
        redis_store, PARK_ID, DRIVER_ID, ['econom', 'business'],
    )

    params = {'park_id': PARK_ID, 'driver_id': DRIVER_ID}

    response = await taxi_driver_categories_api.get(
        ENDPOINT, headers=HEADERS, params=params,
    )
    assert response.status_code == 200
    assert response.json() == {'is_enabled': False}
