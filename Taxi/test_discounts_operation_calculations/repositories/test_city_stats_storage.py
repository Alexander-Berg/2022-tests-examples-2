import operator as op

import pytest

from discounts_operation_calculations.repositories import city_stats


STATS_DATA = [
    {
        'city': 'test_city',
        'sum_gmv': 1234567,
        'city_population': 300000,
        'avg_order_cost': 500.0,
        'avg_currency_rate': 1.3,
        'trips_count': 500,
        'min_date': '2022-04-01',
    },
    {
        'city': 'other_city',
        'sum_gmv': 10000000,
        'city_population': 12345678,
        'avg_order_cost': 1000.0,
        'avg_currency_rate': 0.5,
        'trips_count': 4657,
        'min_date': '2022-04-01',
    },
]


SURGE_DATA = [
    {'city': 'test_city', 'surge': 1.2, 'trips_count': 10},
    {'city': 'test_city', 'surge': 1.5, 'trips_count': 20},
    {'city': 'test_city', 'surge': 1.7, 'trips_count': 15},
    {'city': 'test_city', 'surge': 1.9, 'trips_count': 5},
    {'city': 'other_city', 'surge': 2.3, 'trips_count': 100},
    {'city': 'other_city', 'surge': 1.8, 'trips_count': 200},
    {'city': 'other_city', 'surge': 3.0, 'trips_count': 1},
    {'city': 'other_city', 'surge': 1.9, 'trips_count': 5},
]


@pytest.mark.pgsql('discounts_operation_calculations')
async def test_city_stats_storage(web_context):
    storage = city_stats.CityStatsStorage(web_context)

    await storage.save_cities_data(STATS_DATA, SURGE_DATA)

    stats = await storage.get_city_stats('test_city')
    assert stats == city_stats.CityStats(
        'test_city', 1234567, 300000, 500.0, 1.3, 500,
    )

    surge_trips = await storage.get_surge_trips('other_city', surge=2.0)
    assert surge_trips == 101

    surge_trips = await storage.get_surge_trips('other_city', surge=10.0)
    assert surge_trips == 0


@pytest.mark.parametrize(
    'surge, expected_surge_trips',
    [(0.5, 555), (1.2, 555), (1.5, 375), (2.0, 175), (10.2, 0)],
)
@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_city_stats.sql'],
)
async def test_city_stats_storage_get_surge_trips(
        web_context, surge, expected_surge_trips,
):
    storage = city_stats.CityStatsStorage(web_context)

    surge_trips = await storage.get_surge_trips('test_city', surge=surge)
    assert surge_trips == expected_surge_trips


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_city_stats.sql'],
)
async def test_city_stats_storage_get_stats(web_context):
    storage = city_stats.CityStatsStorage(web_context)

    stats = await storage.get_city_stats('test_city')
    assert stats == city_stats.CityStats(
        'test_city', 400500.40, 100500, 680.857, 0.18, 10500,
    )

    stats = await storage.get_city_stats('test_city2')
    assert stats == city_stats.CityStats(
        'test_city2', 200600.0, 200, 333.857, 4.18, 1234,
    )


@pytest.mark.pgsql('discounts_operation_calculations')
@pytest.mark.parametrize('city', map(op.itemgetter('city'), STATS_DATA))
async def test_city_stats_storage_save_data(web_context, pgsql, city):
    storage = city_stats.CityStatsStorage(web_context)

    await storage.save_cities_data(STATS_DATA, SURGE_DATA)

    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        f'SELECT city, sum_gmv, city_population, avg_order_cost, '
        f'avg_currency_rate, trips_count, min_date '
        f'FROM discounts_operation_calculations.city_stats '
        f'WHERE city = \'{city}\'',
    )

    assert list(cursor) == list(
        tuple(d.values()) for d in STATS_DATA if d['city'] == city
    )

    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        f'SELECT city, surge, trips_count '
        f'FROM discounts_operation_calculations.city_trips_with_surge '
        f'WHERE city = \'{city}\'',
    )

    assert list(cursor) == list(
        tuple(d.values()) for d in SURGE_DATA if d['city'] == city
    )
