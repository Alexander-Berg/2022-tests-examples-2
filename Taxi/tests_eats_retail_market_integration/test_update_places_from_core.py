import datetime as dt

import pytest


CORE_RETAIL_SYNC_HANDLER = '/eats-core-retail/v1/brand/places/retrieve'

PERIODIC_NAME = 'update-places-from-core-periodic'


@pytest.mark.config(
    EATS_RETAIL_MARKET_INTEGRATION_PERIODICS={
        'update-places-from-core-periodic': {
            'is_enabled': True,
            'period_in_sec': 1800,
        },
    },
)
@pytest.mark.pgsql('eats_retail_market_integration')
async def test_updating_places_from_core(
        pg_cursor,
        mockserver,
        taxi_eats_retail_market_integration,
        to_utc_datetime,
):
    known_brands = [
        {'id': 5, 'is_enabled': True},
        {'id': 6, 'is_enabled': True},
        {'id': 7, 'is_enabled': False},
    ]
    _sql_set_brands(pg_cursor, known_brands)

    old_places = [
        {
            'brand_id': '5',
            'place_id': '1',
            'place_slug': '5_1_should_change_slug',
            'is_enabled': True,
        },
        {
            'brand_id': '5',
            'place_id': '2',
            'place_slug': '5_2_should_remain_unchanged',
            'is_enabled': True,
        },
        {
            'brand_id': '5',
            'place_id': '3',
            'place_slug': '5_3_should_change_brand',
            'is_enabled': True,
        },
        {
            'brand_id': '5',
            'place_id': '4',
            'place_slug': '5_4_should_enable',
            'is_enabled': False,
        },
        {
            'brand_id': '5',
            'place_id': '5',
            'place_slug': '5_5_should_disable_by_changing',
            'is_enabled': True,
        },
        {
            'brand_id': '5',
            'place_id': '6',
            'place_slug': '5_6_should_disable_by_deleting',
            'is_enabled': True,
        },
        {
            'brand_id': '5',
            'place_id': '8',
            'place_slug': '5_8_should_remain_unchanged',
            'is_enabled': False,
        },
    ]
    old_updated_at = '2021-01-01T00:45:00+00:00'
    _sql_set_places(pg_cursor, old_places, old_updated_at)

    places_from_core = [
        {
            'brand_id': '5',
            'place_id': '1',
            'place_slug': '5_1_new_slug',
            'enabled': True,
        },
        {
            'brand_id': '5',
            'place_id': '2',
            'place_slug': '5_2_should_remain_unchanged',
            'enabled': True,
        },
        {
            'brand_id': '6',
            'place_id': '3',
            'place_slug': '6_3_new_brand',
            'enabled': True,
        },
        {
            'brand_id': '5',
            'place_id': '4',
            'place_slug': '5_4_should_enable',
            'enabled': True,
        },
        {
            'brand_id': '5',
            'place_id': '5',
            'place_slug': '5_5_should_disable_by_changing',
            'enabled': False,
        },
        {
            'brand_id': '5',
            'place_id': '7',
            'place_slug': '5_7_new_place',
            'enabled': True,
        },
        {
            'brand_id': '7',
            'place_id': '1',
            'place_slug': '7_1_disabled_brand',
            'enabled': True,
        },
    ]

    @mockserver.json_handler(CORE_RETAIL_SYNC_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        places = [
            place
            for place in places_from_core
            if place['brand_id'] == request.query['brand_id']
        ]
        return {
            'places': [
                {
                    'id': place['place_id'],
                    'slug': place['place_slug'],
                    'enabled': place['enabled'],
                    'brand_id': place['brand_id'],
                    'parser_enabled': True,
                }
                for place in places
            ],
            'meta': {'limit': len(places)},
        }

    await taxi_eats_retail_market_integration.run_distlock_task(PERIODIC_NAME)

    now_date = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    old_date = to_utc_datetime(old_updated_at).strftime('%Y-%m-%dT%H:%M')
    expected_places = [
        {
            'brand_id': '5',
            'place_id': '1',
            'place_slug': '5_1_new_slug',
            'is_enabled': True,
            'updated_at': now_date,
        },
        {
            'brand_id': '5',
            'place_id': '2',
            'place_slug': '5_2_should_remain_unchanged',
            'is_enabled': True,
            'updated_at': old_date,
        },
        {
            'brand_id': '6',
            'place_id': '3',
            'place_slug': '6_3_new_brand',
            'is_enabled': True,
            'updated_at': now_date,
        },
        {
            'brand_id': '5',
            'place_id': '4',
            'place_slug': '5_4_should_enable',
            'is_enabled': True,
            'updated_at': now_date,
        },
        {
            'brand_id': '5',
            'place_id': '5',
            'place_slug': '5_5_should_disable_by_changing',
            'is_enabled': False,
            'updated_at': now_date,
        },
        {
            'brand_id': '5',
            'place_id': '6',
            'place_slug': '5_6_should_disable_by_deleting',
            'is_enabled': False,
            'updated_at': now_date,
        },
        {
            'brand_id': '5',
            'place_id': '7',
            'place_slug': '5_7_new_place',
            'is_enabled': True,
            'updated_at': now_date,
        },
        {
            'brand_id': '5',
            'place_id': '8',
            'place_slug': '5_8_should_remain_unchanged',
            'is_enabled': False,
            'updated_at': old_date,
        },
    ]

    # Verify places
    sql_places = _sql_get_places(pg_cursor, to_utc_datetime)
    assert sorted_by_place_id(sql_places) == sorted_by_place_id(
        expected_places,
    )


@pytest.mark.pgsql('eats_retail_market_integration')
async def test_periodic_metrics(mockserver, verify_periodic_metrics):
    @mockserver.json_handler(CORE_RETAIL_SYNC_HANDLER)
    def _mock_eats_core_retail_mapping(request):
        return {}

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def sorted_by_place_id(places):
    return sorted(places, key=lambda item: item['place_id'])


def _sql_set_brands(pg_cursor, brands):
    for brand in brands:
        slug = 'slug_%(brand["id"])'
        pg_cursor.execute(
            """
            insert into eats_retail_market_integration.brands
                (id, slug, is_enabled)
            values (%s, %s, %s)
            """,
            (brand['id'], slug, brand['is_enabled']),
        )


def _sql_set_places(pg_cursor, places, updated_at):
    for place in places:
        pg_cursor.execute(
            """
            insert into eats_retail_market_integration.places (
                id, slug, brand_id, is_enabled, created_at, updated_at
            )
            values (%s, %s, %s, %s, %s, %s)
                """,
            (
                place['place_id'],
                place['place_slug'],
                place['brand_id'],
                place['is_enabled'],
                updated_at,
                updated_at,
            ),
        )


def _sql_get_places(pg_cursor, to_utc_datetime):
    pg_cursor.execute(
        """
        select id, slug, brand_id, is_enabled, updated_at
        from eats_retail_market_integration.places
        """,
    )
    return [
        {
            'place_id': i[0],
            'place_slug': i[1],
            'brand_id': i[2],
            'is_enabled': i[3],
            'updated_at': to_utc_datetime(i[4]).strftime('%Y-%m-%dT%H:%M'),
        }
        for i in pg_cursor
    ]
