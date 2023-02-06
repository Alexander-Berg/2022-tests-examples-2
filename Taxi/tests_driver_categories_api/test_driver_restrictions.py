import pytest

from tests_driver_categories_api import category_utils

HANDLER_URL = 'v2/driver/restrictions'

RESTRICTION_QUERIES_GLOBAL = [
    # categories
    'INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES'
    '(\'econom\', \'e\', NOW(), \'{"restriction_value":32}\'),'
    '(\'business\', \'b\', NOW(), \'{"restriction_value":64}\');',
    # driver_restrictions
    'INSERT INTO categories.driver_restrictions'
    '(driver_id, park_id, categories, updated_at, jdoc) VALUES'
    '(\'uuid\', \'dbid\', \'{"econom"}\', NOW(), \'{}\');',
]


@pytest.mark.pgsql('driver-categories-api', queries=RESTRICTION_QUERIES_GLOBAL)
async def test_single_operations(taxi_driver_categories_api, pgsql):
    def get_collection(driver_id, park_id):
        cursor = pgsql['driver-categories-api'].cursor()
        cursor.execute(
            'select categories from categories.driver_restrictions'
            ' where park_id=\''
            + park_id
            + '\' and driver_id=\''
            + driver_id
            + '\'',
        )
        return cursor.fetchone()[0]

    params = {'driver_id': 'uuid', 'park_id': 'dbid'}
    data = {'name': 'business'}
    response = await taxi_driver_categories_api.post(
        HANDLER_URL, params=params, json=data,
    )
    assert response.status_code == 200

    assert get_collection('uuid', 'dbid') == ['business', 'econom']

    params = {'driver_id': 'uuid', 'park_id': 'dbid', 'name': 'econom'}
    response = await taxi_driver_categories_api.delete(
        HANDLER_URL, params=params,
    )
    assert response.status_code == 200
    assert get_collection('uuid', 'dbid') == ['business']


@pytest.mark.pgsql(
    'driver-categories-api',
    queries=[
        # categories
        'INSERT INTO categories.categories(name,type,updated_at,jdoc) VALUES'
        '(\'econom\', \'e\', NOW(), \'{"restriction_value":32}\'),'
        '(\'business\', \'b\', NOW(), \'{"restriction_value":64}\');',
    ],
)
async def test_bad_cases_restrictions(taxi_driver_categories_api, pgsql):
    params = {'driver_id': 'uuid', 'park_id': 'dbid'}

    data = {'name': '', 'jdoc': {'optional': 'new'}}
    response = await taxi_driver_categories_api.post(
        HANDLER_URL, params=params, json=data,
    )
    assert response.status_code == 400

    params = {'driver_id': '', 'park_id': 'dbid'}

    data = {'name': '', 'jdoc': {'optional': 'new'}}
    response = await taxi_driver_categories_api.post(
        HANDLER_URL, params=params, json=data,
    )
    assert response.status_code == 400

    params = {'driver_id': 'uuid', 'park_id': ''}

    data = {'name': '', 'jdoc': {'optional': 'new'}}
    response = await taxi_driver_categories_api.post(
        HANDLER_URL, params=params, json=data,
    )
    assert response.status_code == 400

    params = {'driver_id': 'uuid', 'park_id': 'dbid'}

    data = {'jdoc': {'optional': 'new'}}
    response = await taxi_driver_categories_api.post(
        HANDLER_URL, params=params, json=data,
    )
    assert response.status_code == 400


DRIVER_RESTRICTIONS_ENV = [
    # categories
    'INSERT INTO categories.categories(name, type, updated_at, jdoc) VALUES'
    '(\'econom\', \'e\', NOW(), \'{"restriction_value":32}\'),'
    '(\'business\', \'b\', NOW(), \'{"restriction_value":64}\'),'
    '(\'child_tariff\', \'c\', NOW(), \'{"restriction_value":262144}\');',
    # driver_restrictions
    'INSERT INTO categories.driver_restrictions'
    '(driver_id, park_id, categories, updated_at, jdoc) VALUES'
    '(\'uuid\',\'dbid\',\'{"business","child_tariff","econom"}\',NOW(),'
    '\'{}\'),'
    '(\'uuid\',\'db2\',\'{"business"}\',NOW(),\'{}\');',
]
DRIVER_RESTRICTIONS_REDIS_ENV = (
    [
        'hset',
        'RobotSettings:dbid:Settings',
        'uuid',
        '{0}'.format((0x1 << 5) + (0x1 << 6) + (0x1 << 18)),
    ],
    ['hset', 'RobotSettings:db2:Settings', 'uuid', '{0}'.format(0x1 << 6)],
)


@pytest.mark.config(
    DRIVER_CATEGORIES_API_DATA_SOURCE={
        '/v2/driver/restrictions GET': {'use_pg': True},
        '__default__': {'use_pg': False},
    },
)
@pytest.mark.pgsql('driver-categories-api', queries=DRIVER_RESTRICTIONS_ENV)
async def test_multi_operations(taxi_driver_categories_api, pgsql):
    await taxi_driver_categories_api.invalidate_caches()

    params = {'driver_id': 'uuid', 'park_id': 'dbid'}
    response = await taxi_driver_categories_api.get(HANDLER_URL, params=params)
    assert response.status_code == 200
    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {
        'categories': [
            {'name': 'business', 'type': 'b'},
            {'name': 'child_tariff', 'type': 'c'},
            {'name': 'econom', 'type': 'e'},
        ],
    }

    # put
    params = {'driver_id': 'uuid', 'park_id': 'dbid'}
    data = {'categories': [{'name': 'business'}, {'name': 'econom'}]}
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
        ],
    }


@pytest.mark.parametrize('use_pg', [True, False])
@pytest.mark.pgsql('driver-categories-api', queries=DRIVER_RESTRICTIONS_ENV)
@pytest.mark.redis_store(*DRIVER_RESTRICTIONS_REDIS_ENV)
async def test_drivers_restrictions_get(
        taxi_driver_categories_api, pgsql, taxi_config, use_pg,
):
    taxi_config.set(
        DRIVER_CATEGORIES_API_DATA_SOURCE={
            '/v2/driver/restrictions GET': {'use_pg': use_pg},
            '__default__': {'use_pg': False},
        },
    )

    await taxi_driver_categories_api.invalidate_caches()

    params = {'driver_id': 'uuid', 'park_id': 'dbid'}
    response = await taxi_driver_categories_api.get(HANDLER_URL, params=params)
    assert response.status_code == 200
    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {
        'categories': [
            {'name': 'business', 'type': 'b'},
            {'name': 'child_tariff', 'type': 'c'},
            {'name': 'econom', 'type': 'e'},
        ],
    }


@pytest.mark.config(
    DRIVER_CATEGORIES_API_DATA_SOURCE={
        '/v2/driver/restrictions GET': {'use_pg': True},
        '__default__': {'use_pg': False},
    },
)
@pytest.mark.pgsql('driver-categories-api', queries=DRIVER_RESTRICTIONS_ENV)
@pytest.mark.parametrize('use_optimized_bulk', [False, True])
@pytest.mark.parametrize('use_metrics', [False, True])
@pytest.mark.parametrize('use_locked_queries', [False, True])
async def test_driver_restrictions_bulk(
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
                'park_id': 'dbid',
                'driver_id': 'uuid',
                'categories': [{'name': 'business'}, {'name': 'econom'}],
            },
            {
                'park_id': 'dbid',
                'driver_id': 'uuid2',
                'categories': [{'name': 'econom'}],
            },
        ],
    }
    response = await taxi_driver_categories_api.put(
        'v2/driver/restrictions_bulk', json=data,
    )
    assert response.status_code == 200

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.get(
        'v2/driver/restrictions',
        params={'park_id': 'dbid', 'driver_id': 'uuid'},
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
        'v2/driver/restrictions',
        params={'park_id': 'dbid', 'driver_id': 'uuid2'},
    )
    assert response.status_code == 200
    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == {'categories': [{'name': 'econom', 'type': 'e'}]}
