import pytest

from tests_driver_categories_api import category_utils

HANDLER_URL = 'v2/park/categories'

PARKS_CATEGORIES_ENV = [
    # categories
    'INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES'
    '(\'econom\', \'e\', now(), \'{ "op":"foo"}\'),'
    '(\'business\', \'b\', now(), \'{"op":"bar"}\'),'
    '(\'child\', \'c\', now(), \'{"op":"child"}\'),'
    '(\'premium\', \'c\', now(), \'{"op":"premium"}\');',
    # park_categories
    'INSERT INTO categories.park_categories'
    '(park_id, categories, updated_at, jdoc) VALUES'
    '(\'db2\',\'{"business","child","econom"}\', now(), \'{}\');',
]


@pytest.mark.pgsql('driver-categories-api', queries=PARKS_CATEGORIES_ENV)
async def test_park_categories(taxi_driver_categories_api, pgsql):
    await taxi_driver_categories_api.invalidate_caches()

    params = {'park_id': 'db2'}
    response = await taxi_driver_categories_api.get(HANDLER_URL, params=params)
    assert response.status_code == 200
    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {
        'categories': [
            {'name': 'business', 'type': 'b'},
            {'name': 'child', 'type': 'c'},
            {'name': 'econom', 'type': 'e'},
        ],
    }

    # post
    data = {
        'categories': [
            {'name': 'business'},
            {'name': 'econom'},
            {'name': 'premium'},
        ],
    }
    response = await taxi_driver_categories_api.put(
        HANDLER_URL, params=params, json=data,
    )
    assert response.status_code == 200

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.get(HANDLER_URL, params=params)
    assert response.status_code == 200
    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {
        'categories': [
            {'name': 'business', 'type': 'b'},
            {'name': 'econom', 'type': 'e'},
            {'name': 'premium', 'type': 'c'},
        ],
    }

    cursor = pgsql['driver-categories-api'].cursor()
    cursor.execute(
        'SELECT categories from '
        'categories.park_categories where park_id=\'db2\'',
    )
    assert cursor.fetchall() == [(['business', 'econom', 'premium'],)]


@pytest.mark.pgsql('driver-categories-api', queries=PARKS_CATEGORIES_ENV)
async def test_park_categories_get(taxi_driver_categories_api, pgsql):
    await taxi_driver_categories_api.invalidate_caches()

    params = {'park_id': 'db2'}
    response = await taxi_driver_categories_api.get(HANDLER_URL, params=params)
    assert response.status_code == 200
    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {
        'categories': [
            {'name': 'business', 'type': 'b'},
            {'name': 'child', 'type': 'c'},
            {'name': 'econom', 'type': 'e'},
        ],
    }


@pytest.mark.pgsql('driver-categories-api', queries=PARKS_CATEGORIES_ENV)
@pytest.mark.parametrize('use_optimized_bulk', [False, True])
@pytest.mark.parametrize('use_metrics', [False, True])
@pytest.mark.parametrize('use_locked_queries', [False, True])
async def test_park_categories_bulk(
        taxi_driver_categories_api,
        pgsql,
        taxi_config,
        use_optimized_bulk,
        use_metrics,
        use_locked_queries,
):
    taxi_config.set_values(
        category_utils.get_bulk_metrics_config(
            use_optimized_bulk, use_metrics,
        ),
    )
    taxi_config.set_values(
        category_utils.config_use_locked_queries(use_locked_queries),
    )

    data = {
        'items': [
            {
                'park_id': 'db2',
                'categories': [{'name': 'business'}, {'name': 'econom'}],
            },
            {'park_id': 'db3', 'categories': [{'name': 'econom'}]},
        ],
    }
    response = await taxi_driver_categories_api.put(
        'v2/park/categories_bulk', json=data,
    )
    assert response.status_code == 200

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.get(
        'v2/park/categories', params={'park_id': 'db2'},
    )
    assert response.status_code == 200
    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {
        'categories': [
            {'name': 'business', 'type': 'b'},
            {'name': 'econom', 'type': 'e'},
        ],
    }

    response = await taxi_driver_categories_api.get(
        'v2/park/categories', params={'park_id': 'db3'},
    )
    assert response.status_code == 200
    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {'categories': [{'name': 'econom', 'type': 'e'}]}
