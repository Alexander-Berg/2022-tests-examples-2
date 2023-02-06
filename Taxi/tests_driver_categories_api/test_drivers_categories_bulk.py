import pytest

# pylint: disable=E0401
import driver_categories_api.yandex.taxi.fbs.categories.AllCategories as fbCtg


@pytest.mark.pgsql(
    'driver-categories-api', files=['test_drivers_categories_bulk.sql'],
)
@pytest.mark.parametrize(
    'data',
    [
        pytest.param({}, id='No revisions in data'),
        pytest.param(
            {'revisions': {'drivers': '0', 'parks': '0', 'cars': 'aaa'}},
            id='Not an integer in revisions',
        ),
        pytest.param(
            {
                'revisions': {'drivers': '0', 'parks': '0', 'cars': '0'},
                'limits': {'drivers': 0, 'parks': 'bbb', 'cars': 0},
            },
            id='Not an integer in limits',
        ),
        pytest.param(
            {'revisions': {'drivers': '0', 'parks': '-1', 'cars': '12'}},
            id='Integer below 0 in revisions',
        ),
        pytest.param(
            {
                'revisions': {'drivers': '0', 'parks': '0', 'cars': '0'},
                'limits': {'drivers': -10, 'parks': 0, 'cars': 0},
            },
            id='Integer below 0 in limits',
        ),
    ],
)
async def test_bad_data(taxi_driver_categories_api, data):
    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        'v1/drivers/categories/bulk', json=data,
    )
    assert response.status_code == 400


async def _check_single_request(
        taxi_driver_categories_api,
        revisions,
        category_types,
        limits,
        expected_json_response,
):
    await taxi_driver_categories_api.invalidate_caches()

    data = {'revisions': revisions}
    if limits is not None:
        data['limits'] = limits
    if category_types is not None:
        data['category_types'] = category_types
    response = await taxi_driver_categories_api.post(
        'v1/drivers/categories/bulk', json=data,
    )
    assert response.status_code == 200

    fbb = fbCtg.AllCategories.GetRootAsAllCategories(response.content, 0)

    res = {'blocked_by_driver': [], 'cars': [], 'parks': []}
    for i in range(0, fbb.BlockedByDriverLength()):
        driver = fbb.BlockedByDriver(i)
        categories = []
        for j in range(0, driver.CategoriesLength()):
            categories.append(driver.Categories(j).decode('utf-8'))
        categories.sort()
        res['blocked_by_driver'].append(
            {
                'park_id': driver.ParkId().decode('utf-8'),
                'driver_id': driver.DriverId().decode('utf-8'),
                'categories': categories,
            },
        )
    for i in range(0, fbb.CarsClassesInParkLength()):
        car = fbb.CarsClassesInPark(i)
        categories = []
        for j in range(0, car.CategoriesLength()):
            categories.append(car.Categories(j).decode('utf-8'))
        categories.sort()
        res['cars'].append(
            {
                'park_id': car.ParkId().decode('utf-8'),
                'car_id': car.CarId().decode('utf-8'),
                'categories': categories,
            },
        )
    for i in range(0, fbb.AvailableInParkLength()):
        park = fbb.AvailableInPark(i)
        categories = []
        for j in range(0, park.CategoriesLength()):
            categories.append(park.Categories(j).decode('utf-8'))
        categories.sort()
        res['parks'].append(
            {
                'park_id': park.ParkId().decode('utf-8'),
                'categories': categories,
            },
        )

    assert (
        res['blocked_by_driver'] == expected_json_response['blocked_by_driver']
    )
    assert res['cars'] == expected_json_response['cars']
    assert res['parks'] == expected_json_response['parks']
    assert int(fbb.DriversRevision()) > 0
    assert int(fbb.ParksRevision()) > 0
    assert int(fbb.CarsRevision()) > 0

    drivers_revision = str(fbb.DriversRevision().decode('utf-8'))
    parks_revision = str(fbb.ParksRevision().decode('utf-8'))
    cars_revision = str(fbb.CarsRevision().decode('utf-8'))

    assert response.headers['X-YaTaxi-Drivers-Revision'] == drivers_revision
    assert response.headers['X-YaTaxi-Parks-Revision'] == parks_revision
    assert response.headers['X-YaTaxi-Cars-Revision'] == cars_revision

    return {
        'drivers': drivers_revision,
        'parks': parks_revision,
        'cars': cars_revision,
    }


@pytest.mark.pgsql(
    'driver-categories-api', files=['test_drivers_categories_bulk.sql'],
)
@pytest.mark.parametrize(
    'expected_json_responses,category_types,limits',
    [
        pytest.param(
            [
                {
                    'blocked_by_driver': [
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver1',
                            'categories': ['business', 'child', 'econom'],
                        },
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver2',
                            'categories': ['minibus'],
                        },
                        {
                            'park_id': 'park_2',
                            'driver_id': 'driver3',
                            'categories': ['econom', 'wagon'],
                        },
                    ],
                    'cars': [
                        {
                            'park_id': 'park_1',
                            'car_id': 'car1',
                            'categories': [
                                'business',
                                'comfort',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'pool',
                                'trucking',
                                'vip',
                                'wagon',
                            ],
                        },
                        {
                            'car_id': 'car2',
                            'park_id': 'park_1',
                            'categories': [
                                'business',
                                'comfort',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minibus',
                                'minivan',
                                'pool',
                                'trucking',
                                'vip',
                                'wagon',
                            ],
                        },
                        {
                            'car_id': 'car3',
                            'park_id': 'park_1',
                            'categories': [
                                'comfort',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minivan',
                                'pool',
                                'trucking',
                                'vip',
                            ],
                        },
                    ],
                    'parks': [
                        {
                            'park_id': 'park_1',
                            'categories': [
                                'business',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minibus',
                                'minivan',
                                'pool',
                                'wagon',
                            ],
                        },
                        {'park_id': 'park_2', 'categories': ['child']},
                    ],
                },
                {
                    'blocked_by_driver': [
                        {
                            'park_id': 'park_2',
                            'driver_id': 'driver3',
                            'categories': ['econom', 'wagon'],
                        },
                    ],
                    'cars': [
                        {
                            'car_id': 'car3',
                            'park_id': 'park_1',
                            'categories': [
                                'comfort',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minivan',
                                'pool',
                                'trucking',
                                'vip',
                            ],
                        },
                    ],
                    'parks': [{'park_id': 'park_2', 'categories': ['child']}],
                },
            ],
            [],
            None,
            id='All category types, "category_types" is empty array',
        ),
        pytest.param(
            [
                {
                    'blocked_by_driver': [
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver1',
                            'categories': ['econom'],
                        },
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver2',
                            'categories': [],
                        },
                        {
                            'park_id': 'park_2',
                            'driver_id': 'driver3',
                            'categories': ['econom'],
                        },
                    ],
                    'cars': [
                        {
                            'park_id': 'park_1',
                            'car_id': 'car1',
                            'categories': ['econom'],
                        },
                        {
                            'park_id': 'park_1',
                            'car_id': 'car2',
                            'categories': ['econom'],
                        },
                        {
                            'park_id': 'park_1',
                            'car_id': 'car3',
                            'categories': ['econom'],
                        },
                    ],
                    'parks': [
                        {'park_id': 'park_1', 'categories': ['econom']},
                        {'park_id': 'park_2', 'categories': []},
                    ],
                },
                {
                    'blocked_by_driver': [
                        {
                            'park_id': 'park_2',
                            'driver_id': 'driver3',
                            'categories': ['econom'],
                        },
                    ],
                    'cars': [
                        {
                            'park_id': 'park_1',
                            'car_id': 'car3',
                            'categories': ['econom'],
                        },
                    ],
                    'parks': [{'park_id': 'park_2', 'categories': []}],
                },
            ],
            None,
            None,
            id='Only category type "yandex", "category_types" is null',
        ),
        pytest.param(
            [
                {
                    'blocked_by_driver': [
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver1',
                            'categories': ['business'],
                        },
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver2',
                            'categories': [],
                        },
                        {
                            'park_id': 'park_2',
                            'driver_id': 'driver3',
                            'categories': [],
                        },
                    ],
                    'cars': [
                        {
                            'park_id': 'park_1',
                            'car_id': 'car1',
                            'categories': ['business', 'pool'],
                        },
                        {
                            'park_id': 'park_1',
                            'car_id': 'car2',
                            'categories': ['business', 'pool'],
                        },
                        {
                            'park_id': 'park_1',
                            'car_id': 'car3',
                            'categories': ['pool'],
                        },
                    ],
                    'parks': [
                        {
                            'park_id': 'park_1',
                            'categories': ['business', 'pool'],
                        },
                        {'park_id': 'park_2', 'categories': []},
                    ],
                },
                {
                    'blocked_by_driver': [
                        {
                            'park_id': 'park_2',
                            'driver_id': 'driver3',
                            'categories': [],
                        },
                    ],
                    'cars': [
                        {
                            'park_id': 'park_1',
                            'car_id': 'car3',
                            'categories': ['pool'],
                        },
                    ],
                    'parks': [{'park_id': 'park_2', 'categories': []}],
                },
            ],
            ['b', 'p'],
            None,
            id='Some category types',
        ),
        pytest.param(
            [
                {
                    'blocked_by_driver': [
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver1',
                            'categories': ['business', 'child', 'econom'],
                        },
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver2',
                            'categories': ['minibus'],
                        },
                    ],
                    'cars': [
                        {
                            'park_id': 'park_1',
                            'car_id': 'car1',
                            'categories': [
                                'business',
                                'comfort',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'pool',
                                'trucking',
                                'vip',
                                'wagon',
                            ],
                        },
                        {
                            'park_id': 'park_1',
                            'car_id': 'car2',
                            'categories': [
                                'business',
                                'comfort',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minibus',
                                'minivan',
                                'pool',
                                'trucking',
                                'vip',
                                'wagon',
                            ],
                        },
                    ],
                    'parks': [
                        {
                            'park_id': 'park_1',
                            'categories': [
                                'business',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minibus',
                                'minivan',
                                'pool',
                                'wagon',
                            ],
                        },
                    ],
                },
                {
                    'blocked_by_driver': [
                        {
                            'park_id': 'park_1',
                            'driver_id': 'driver2',
                            'categories': ['minibus'],
                        },
                        {
                            'park_id': 'park_2',
                            'driver_id': 'driver3',
                            'categories': ['econom', 'wagon'],
                        },
                    ],
                    'cars': [
                        {
                            'car_id': 'car2',
                            'park_id': 'park_1',
                            'categories': [
                                'business',
                                'comfort',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minibus',
                                'minivan',
                                'pool',
                                'trucking',
                                'vip',
                                'wagon',
                            ],
                        },
                        {
                            'car_id': 'car3',
                            'park_id': 'park_1',
                            'categories': [
                                'comfort',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minivan',
                                'pool',
                                'trucking',
                                'vip',
                            ],
                        },
                    ],
                    'parks': [
                        {
                            'park_id': 'park_1',
                            'categories': [
                                'business',
                                'comfort_plus',
                                'econom',
                                'limousine',
                                'minibus',
                                'minivan',
                                'pool',
                                'wagon',
                            ],
                        },
                    ],
                },
            ],
            [],
            {'drivers': 2, 'parks': 1, 'cars': 2},
            id='Use limits in request',
        ),
    ],
)
@pytest.mark.parametrize('car_cache_usage_percent', [0, 100])
@pytest.mark.parametrize('drivers_cache_usage_percent', [0, 100])
@pytest.mark.parametrize('parks_cache_usage_percent', [0, 100])
async def test_bulk_driver_aggregations(
        taxi_driver_categories_api,
        taxi_config,
        expected_json_responses,
        category_types,
        limits,
        car_cache_usage_percent,
        drivers_cache_usage_percent,
        parks_cache_usage_percent,
):
    cache_settings_index = (
        car_cache_usage_percent < 100
        or drivers_cache_usage_percent < 100
        or parks_cache_usage_percent < 100
    )
    taxi_config.set_values(
        {
            'DRIVER_CATEGORIES_API_PG_CACHE_SETTINGS': {
                'handlers': (
                    (
                        {},
                        {
                            '/v1/categories/get': {
                                'car_categories': {
                                    'cache_usage_percent': (
                                        car_cache_usage_percent
                                    ),
                                },
                                'driver_restrictions': {
                                    'cache_usage_percent': (
                                        drivers_cache_usage_percent
                                    ),
                                },
                                'park_categories': {
                                    'cache_usage_percent': (
                                        parks_cache_usage_percent
                                    ),
                                },
                            },
                        },
                    )[cache_settings_index]
                ),
            },
        },
    )
    await taxi_driver_categories_api.invalidate_caches()

    new_revisions = await _check_single_request(
        taxi_driver_categories_api,
        {'drivers': '0', 'parks': '0', 'cars': '0'},
        category_types,
        limits,
        expected_json_responses[0],
    )
    await _check_single_request(
        taxi_driver_categories_api,
        new_revisions,
        category_types,
        limits,
        expected_json_responses[1],
    )
