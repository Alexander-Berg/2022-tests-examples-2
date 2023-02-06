import pytest

from tests_driver_categories_api import category_utils

HANDLER_URL = 'v2/car/categories'

CARS_CATEGORIES_ENV = [
    # categories
    'INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES'
    '(\'econom\', \'e\', NOW(), \'{}\'),'
    '(\'business\', \'b\', NOW(), \'{}\'),'
    '(\'child\', \'c\', NOW(), \'{}\'),'
    '(\'wagon\', \'c\', NOW(), \'{}\'),'
    '(\'minibus\', \'c\', NOW(), \'{}\');',
    # car_categories
    'INSERT INTO categories.car_categories'
    '(car_id, park_id, categories, updated_at, jdoc) VALUES'
    '(\'car0\', \'db2\', \'{"business","child","econom"}\', NOW(), \'{}\');',
]


@pytest.mark.parametrize('config_enabled', [False, True])
@pytest.mark.parametrize('stq_enabled', [False, True])
@pytest.mark.pgsql('driver-categories-api', queries=CARS_CATEGORIES_ENV)
async def test_car_categories(
        taxi_driver_categories_api,
        taxi_config,
        experiments3,
        stq,
        mongodb,
        config_enabled,
        stq_enabled,
):
    params = {'park_id': 'db2', 'car_id': 'car0'}

    taxi_config.set_values(
        {
            'DRIVER_CATEGORIES_API_TAG_MAKER_ENABLED': {
                'enabled': config_enabled,
            },
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_categories_tag_maker_segmentation',
        consumers=['driver-categories-api/tag-maker'],
        clauses=[],
        default_value={'enabled': stq_enabled},
    )
    await taxi_driver_categories_api.invalidate_caches()

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

    params = {'car_id': 'car0', 'park_id': 'db2'}
    data = {
        'categories': [
            {'name': 'business'},
            {'name': 'minibus'},
            {'name': 'wagon'},
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
            {'name': 'minibus', 'type': 'c'},
            {'name': 'wagon', 'type': 'c'},
        ],
    }

    assert stq.driver_categories_tag_maker.times_called == (
        stq_enabled and config_enabled
    )
    if stq_enabled and config_enabled:
        next_call = stq.driver_categories_tag_maker.next_call()
        assert next_call['kwargs']['type'] == 'car_category'


@pytest.mark.pgsql('driver-categories-api', queries=CARS_CATEGORIES_ENV)
async def test_car_categories_get(taxi_driver_categories_api, mongodb):
    params = {'park_id': 'db2', 'car_id': 'car0'}

    await taxi_driver_categories_api.invalidate_caches()

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


@pytest.mark.pgsql('driver-categories-api', queries=CARS_CATEGORIES_ENV)
@pytest.mark.parametrize('config_enabled', [False, True])
@pytest.mark.parametrize('stq_enabled', [False, True])
@pytest.mark.parametrize('use_optimized_bulk', [False, True])
@pytest.mark.parametrize('use_metrics', [False, True])
@pytest.mark.parametrize('use_locked_queries', [False, True])
async def test_car_categories_bulk(
        taxi_driver_categories_api,
        taxi_config,
        experiments3,
        pgsql,
        stq,
        config_enabled,
        stq_enabled,
        use_optimized_bulk,
        use_metrics,
        use_locked_queries,
):
    taxi_config.set_values(
        {
            'DRIVER_CATEGORIES_API_TAG_MAKER_ENABLED': {
                'enabled': config_enabled,
            },
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_categories_tag_maker_segmentation',
        consumers=['driver-categories-api/tag-maker'],
        clauses=[],
        default_value={'enabled': stq_enabled},
    )

    taxi_config.set_values(
        category_utils.get_bulk_metrics_config(
            use_optimized_bulk, use_metrics,
        ),
    )
    taxi_config.set_values(
        category_utils.config_use_locked_queries(use_locked_queries),
    )

    await taxi_driver_categories_api.invalidate_caches()

    data = {
        'items': [
            {
                'park_id': 'db2',
                'car_id': 'car0',
                'categories': [{'name': 'business'}, {'name': 'econom'}],
            },
            {
                'park_id': 'db2',
                'car_id': 'car1',
                'categories': [{'name': 'econom'}],
            },
        ],
    }
    response = await taxi_driver_categories_api.put(
        'v2/car/categories_bulk', json=data,
    )
    assert response.status_code == 200

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.get(
        'v2/car/categories', params={'park_id': 'db2', 'car_id': 'car0'},
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
        'v2/car/categories', params={'park_id': 'db2', 'car_id': 'car1'},
    )
    assert response.status_code == 200

    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {'categories': [{'name': 'econom', 'type': 'e'}]}

    times_called = (
        len(data['items']) if (stq_enabled and config_enabled) else 0
    )
    assert stq.driver_categories_tag_maker.times_called == times_called
    if stq_enabled and config_enabled:
        for _item in data['items']:
            next_call = stq.driver_categories_tag_maker.next_call()
            assert next_call['kwargs']['type'] == 'car_category'
