import pytest

from tests_eats_retail_products_autodisable import models
from tests_eats_retail_products_autodisable.yt_autodisable import consts


PERIODIC_NAME = 'yt-disabled-products-sync'
MOCK_NOW = '2021-09-20T15:00:00+03:00'
OLD_UNAVAILABLE_UNTIL = '2021-09-20T14:00:00+03:00'
UNAVAILABLE_UNTIL_IN_FUTURE_1 = '2021-09-20T16:00:00+03:00'
UNAVAILABLE_UNTIL_IN_FUTURE_2 = '2021-09-20T17:00:00+03:00'
CURRENT_DATE = '2021-09'
ORIGIN_ID_1 = 'item_origin_1'
ORIGIN_ID_2 = 'item_origin_2'
ORIGIN_ID_3 = 'item_origin_3'
ALGORITHM_NAME_ML = 'ml'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data.yaml'],
)
async def test_merge_disable_info_with_different_algorithms(
        pg_realdict_cursor,
        save_autodisabled_products_to_db,
        set_periodic_config,
        taxi_eats_retail_products_autodisable,
        testpoint,
        to_utc_datetime,
        yt_apply,
):
    set_periodic_config(
        enabled_place_ids=[consts.PLACE_ID_1],
        enabled_algorithms=[
            consts.ALGORITHM_NAME_THRESHOLD,
            ALGORITHM_NAME_ML,
        ],
    )

    @testpoint('yt-disabled-products-sync-finished')
    def periodic_end_run(param):
        pass

    autodisabled_products = gen_disabled_products(to_utc_datetime)
    save_autodisabled_products_to_db(autodisabled_products)

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )
    assert periodic_end_run.times_called == 1

    assert (
        sql_get_disabled_products(pg_realdict_cursor)
        == get_expected_disabled_products()
    )


def gen_disabled_products(to_utc_datetime):
    return [
        # new info contains only another algorithm
        models.AutodisabledProduct(
            place_id=consts.PLACE_ID_1,
            origin_id=ORIGIN_ID_1,
            force_unavailable_until=to_utc_datetime(OLD_UNAVAILABLE_UNTIL),
            algorithm_name=consts.ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
        # new info contains both algorithms
        models.AutodisabledProduct(
            place_id=consts.PLACE_ID_1,
            origin_id=ORIGIN_ID_2,
            force_unavailable_until=to_utc_datetime(OLD_UNAVAILABLE_UNTIL),
            algorithm_name=consts.ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
        # old and new info contain both algorithms
        models.AutodisabledProduct(
            place_id=consts.PLACE_ID_1,
            origin_id=ORIGIN_ID_3,
            force_unavailable_until=to_utc_datetime(OLD_UNAVAILABLE_UNTIL),
            algorithm_name=consts.ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
        models.AutodisabledProduct(
            place_id=consts.PLACE_ID_1,
            origin_id=ORIGIN_ID_3,
            force_unavailable_until=to_utc_datetime(OLD_UNAVAILABLE_UNTIL),
            algorithm_name=ALGORITHM_NAME_ML,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
    ]


def sql_get_disabled_products(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select
            place_id,
            origin_id,
            force_unavailable_until,
            algorithm_name
        from eats_retail_products_autodisable.autodisabled_products
        """,
    )
    result = pg_realdict_cursor.fetchall()
    for row in result:
        if row['force_unavailable_until']:
            row['force_unavailable_until'] = row[
                'force_unavailable_until'
            ].isoformat('T')
    return sorted(result, key=lambda k: k['origin_id'] + k['algorithm_name'])


def get_expected_disabled_products():
    return [
        # 1632139200000: 2021.09.20 12:00:00 UTC = NOW
        # UNAVAILABLE_UNTIL_IN_FUTURE_1 = NOW + 1 hour
        # UNAVAILABLE_UNTIL_IN_FUTURE_2 = NOW + 2 hours
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_1,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_2,
            'algorithm_name': ALGORITHM_NAME_ML,
        },
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_1,
            'force_unavailable_until': OLD_UNAVAILABLE_UNTIL,
            'algorithm_name': consts.ALGORITHM_NAME_THRESHOLD,
        },
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_2,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_2,
            'algorithm_name': ALGORITHM_NAME_ML,
        },
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_2,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_1,
            'algorithm_name': consts.ALGORITHM_NAME_THRESHOLD,
        },
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_3,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_2,
            'algorithm_name': ALGORITHM_NAME_ML,
        },
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_3,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE_1,
            'algorithm_name': consts.ALGORITHM_NAME_THRESHOLD,
        },
    ]
