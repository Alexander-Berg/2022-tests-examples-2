import datetime as dt

import psycopg2.tz
import pytest

MOCK_NOW = dt.datetime(
    2021,
    10,
    8,
    15,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
)
RECENT_LAST_REFERENCED_AT = dt.datetime(
    2021,
    10,
    8,
    14,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
)
OLD_LAST_REFERENCED_AT = dt.datetime(
    2021,
    10,
    7,
    10,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
)


def settings(last_referenced_threshold_in_minutes=180):
    return {
        '__default__': {
            'last_referenced_update_threshold_in_minutes': (
                last_referenced_threshold_in_minutes
            ),
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.config(EATS_NOMENCLATURE_PROCESSING=settings())
@pytest.mark.parametrize('should_merge_products_usage', [False, True])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_products_usage_merging(
        pgsql,
        brand_task_enqueue,
        taxi_config,
        # parametrize params
        should_merge_products_usage,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_TEMPORARY_CONFIGS': {
                'should_merge_products_usage': should_merge_products_usage,
            },
        },
    )

    # check current data
    old_products_usage = get_products_usage(pgsql)
    assert old_products_usage == [
        (1, OLD_LAST_REFERENCED_AT),
        (2, OLD_LAST_REFERENCED_AT),
        (3, OLD_LAST_REFERENCED_AT),
        (4, RECENT_LAST_REFERENCED_AT),
        (5, OLD_LAST_REFERENCED_AT),
    ]

    # upload new nomenclature
    await brand_task_enqueue()

    # check merged data
    if should_merge_products_usage:
        # 4, 5, 6 are changed/new products
        # but 4 was changed recently
        # so only 5 and 6 are updated in products_usage
        assert get_products_usage(pgsql) == [
            (1, OLD_LAST_REFERENCED_AT),
            (2, OLD_LAST_REFERENCED_AT),
            (3, OLD_LAST_REFERENCED_AT),
            (4, RECENT_LAST_REFERENCED_AT),
            (5, MOCK_NOW),
            (6, MOCK_NOW),
        ]
    else:
        assert get_products_usage(pgsql) == old_products_usage


def get_products_usage(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        SELECT product_id, last_referenced_at
        FROM eats_nomenclature.products_usage
        order by product_id
        """,
    )
    return list(cursor)
