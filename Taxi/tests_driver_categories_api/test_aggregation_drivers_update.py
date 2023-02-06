import time

import pytest

# pylint: disable=E0401
import driver_categories_api.yandex.taxi.fbs.categories.AllDriverRestrictions as fbs  # noqa: E501

ENDPOINT = 'v2/aggregation/drivers/update'
HOUR_NSEC = 3600000000000


def config_cache_usage(cache_usage_percent):
    cache_settings_index = cache_usage_percent < 100
    return {
        'DRIVER_CATEGORIES_API_PG_CACHE_SETTINGS': {
            'handlers': (
                (
                    {},
                    {
                        '/v1/categories/get': {
                            'car_categories': {
                                'cache_usage_percent': cache_usage_percent,
                            },
                            'driver_restrictions': {
                                'cache_usage_percent': cache_usage_percent,
                            },
                            'park_categories': {
                                'cache_usage_percent': cache_usage_percent,
                            },
                        },
                    },
                )[cache_settings_index]
            ),
        },
    }


def get_canonical_response_json(response):
    fbb = fbs.AllDriverRestrictions.GetRootAsAllDriverRestrictions(
        response.content, 0,
    )
    got_response = {
        'revision': fbb.DriversRevision().decode(
            'utf-8',
        ),  # unix-timestamp in nsec
        'data': [
            {
                'park_id': item.ParkId().decode('utf-8'),
                'driver_id': item.DriverId().decode('utf-8'),
                'categories': sorted(
                    [
                        item.Categories(i).decode('utf-8')
                        for i in range(0, item.CategoriesLength())
                    ],
                ),
            }
            for item in [
                fbb.BlockedByDriver(i)
                for i in range(0, fbb.BlockedByDriverLength())
            ]
        ],
    }
    assert (
        got_response['revision']
        == response.headers['X-YaTaxi-Drivers-Revision']
    )
    return got_response


@pytest.mark.pgsql(
    'driver-categories-api', files=['test_aggregation_drivers_update.sql'],
)
@pytest.mark.parametrize(
    'data',
    [
        # bad data
        {'request': {'revision': 111}, 'status_code': 400},  # wrong
        {
            'request': {'revision': '111', 'limit': '1'},  # wrong
            'status_code': 400,
        },
        {
            'request': {'revision': '-111', 'limit': 1},  # wrong
            'status_code': 400,
        },
        {
            'request': {'revision': '111', 'limit': -1},  # wrong
            'status_code': 400,
        },
    ],
)
async def test_bad_data(taxi_driver_categories_api, taxi_config, pgsql, data):
    await taxi_driver_categories_api.invalidate_caches()
    response = await taxi_driver_categories_api.post(ENDPOINT, data['request'])
    assert data['status_code'] == response.status_code


@pytest.mark.pgsql(
    'driver-categories-api', files=['test_aggregation_drivers_update.sql'],
)
@pytest.mark.parametrize('cache_usage_percent', [0, 100])
@pytest.mark.parametrize(
    'data',
    [
        # none
        {
            'request': {
                'revision': str(time.time_ns() + 2 * HOUR_NSEC),
                'limit': 100,
                'category_types': [],
            },
            'status_code': 200,
            'data': [],
        },
        # half
        {
            'request': {
                'revision': str(time.time_ns() - 2 * HOUR_NSEC),
                'limit': 100,
                'category_types': [],
            },
            'status_code': 200,
            'data': [
                {
                    'park_id': 'a1',
                    'driver_id': 'b10',
                    'categories': ['A', 'B'],
                },
                {'park_id': 'a1', 'driver_id': 'b11_empty', 'categories': []},
                {
                    'park_id': 'a1',
                    'driver_id': 'b12',
                    'categories': ['A', 'AA', 'B', 'BB', 'Y', 'YY'],
                },
            ],
        },
        {
            'request': {
                'revision': str(time.time_ns() - 2 * HOUR_NSEC),
                'limit': 100,
                # 'category_types': [], <=> yandex
            },
            'status_code': 200,
            'data': [
                {'park_id': 'a1', 'driver_id': 'b10', 'categories': []},
                {'park_id': 'a1', 'driver_id': 'b11_empty', 'categories': []},
                {
                    'park_id': 'a1',
                    'driver_id': 'b12',
                    'categories': ['Y', 'YY'],
                },
            ],
        },
        {
            'request': {
                'revision': str(time.time_ns() - 2 * HOUR_NSEC),
                'limit': 100,
                'category_types': ['yandex'],
            },
            'status_code': 200,
            'data': [
                {'park_id': 'a1', 'driver_id': 'b10', 'categories': []},
                {'park_id': 'a1', 'driver_id': 'b11_empty', 'categories': []},
                {
                    'park_id': 'a1',
                    'driver_id': 'b12',
                    'categories': ['Y', 'YY'],
                },
            ],
        },
        {
            'request': {
                'revision': str(time.time_ns() - 2 * HOUR_NSEC),
                'limit': 100,
                'category_types': ['a', 'b'],
            },
            'status_code': 200,
            'data': [
                {
                    'park_id': 'a1',
                    'driver_id': 'b10',
                    'categories': ['A', 'B'],
                },
                {'park_id': 'a1', 'driver_id': 'b11_empty', 'categories': []},
                {
                    'park_id': 'a1',
                    'driver_id': 'b12',
                    'categories': ['A', 'AA', 'B', 'BB'],
                },
            ],
        },
        # all
        {
            'request': {
                'revision': str(time.time_ns() - 4 * HOUR_NSEC),
                'limit': 100,
                'category_types': [],
            },
            'status_code': 200,
            'data': [
                {
                    'park_id': 'a0',
                    'driver_id': 'b00',
                    'categories': ['A', 'Y'],
                },
                {
                    'park_id': 'a1',
                    'driver_id': 'b10',
                    'categories': ['A', 'B'],
                },
                {'park_id': 'a1', 'driver_id': 'b11_empty', 'categories': []},
                {
                    'park_id': 'a1',
                    'driver_id': 'b12',
                    'categories': ['A', 'AA', 'B', 'BB', 'Y', 'YY'],
                },
            ],
        },
        {
            'request': {
                'revision': str(time.time_ns() - 4 * HOUR_NSEC),
                'limit': 100,
                # 'category_types': [], <=> yandex
            },
            'status_code': 200,
            'data': [
                {'park_id': 'a0', 'driver_id': 'b00', 'categories': ['Y']},
                {'park_id': 'a1', 'driver_id': 'b10', 'categories': []},
                {'park_id': 'a1', 'driver_id': 'b11_empty', 'categories': []},
                {
                    'park_id': 'a1',
                    'driver_id': 'b12',
                    'categories': ['Y', 'YY'],
                },
            ],
        },
        {
            'request': {
                'revision': str(time.time_ns() - 4 * HOUR_NSEC),
                'limit': 100,
                'category_types': ['a', 'b'],
            },
            'status_code': 200,
            'data': [
                {'park_id': 'a0', 'driver_id': 'b00', 'categories': ['A']},
                {
                    'park_id': 'a1',
                    'driver_id': 'b10',
                    'categories': ['A', 'B'],
                },
                {'park_id': 'a1', 'driver_id': 'b11_empty', 'categories': []},
                {
                    'park_id': 'a1',
                    'driver_id': 'b12',
                    'categories': ['A', 'AA', 'B', 'BB'],
                },
            ],
        },
        # limit
        {
            'request': {
                'revision': str(time.time_ns() - 4 * HOUR_NSEC),
                'limit': 2,
                'category_types': [],
            },
            'status_code': 200,
            'data': [
                {
                    'park_id': 'a0',
                    'driver_id': 'b00',
                    'categories': ['A', 'Y'],
                },
                {
                    'park_id': 'a1',
                    'driver_id': 'b10',
                    'categories': ['A', 'B'],
                },
            ],
        },
    ],
)
async def test_first(
        taxi_driver_categories_api,
        taxi_config,
        pgsql,
        data,
        cache_usage_percent,
):
    taxi_config.set_values(config_cache_usage(cache_usage_percent))
    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(ENDPOINT, data['request'])
    assert data['status_code'] == response.status_code
    if data['status_code'] != 200:
        return

    got_response = get_canonical_response_json(response)
    assert data['data'] == got_response['data']
    if not got_response['data']:
        assert data['request']['revision'] == got_response['revision']
    else:
        now_nsec = time.time_ns()
        assert now_nsec > int(got_response['revision'])
        assert int(data['request']['revision']) <= int(
            got_response['revision'],
        )
