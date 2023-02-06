import pytest

from tests_eats_retail_products_autodisable import models
from tests_eats_retail_products_autodisable.yt_autodisable import consts


PERIODIC_NAME = 'yt-disabled-products-sync'
MOCK_NOW = '2021-09-20T15:00:00+03:00'
OLD_UNAVAILABLE_UNTIL = '2021-09-20T14:00:00+03:00'
UNAVAILABLE_UNTIL_IN_FUTURE = '2021-09-20T16:00:00+03:00'
CURRENT_DATE = '2021-09'
PREVIOUS_MONTH_DATE = '2021-08'
ORIGIN_ID_1 = 'item_origin_1'
ORIGIN_ID_2 = 'item_origin_2'
ORIGIN_ID_3 = 'item_origin_3'
ORIGIN_ID_4 = 'item_origin_4'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data.yaml'],
)
@pytest.mark.parametrize(
    'yt_processing_status_state', ['empty', 'outdated', 'up-to-date'],
)
async def test_update_autodisable_info_from_yt(
        pg_realdict_cursor,
        save_autodisabled_products_to_db,
        set_periodic_config,
        taxi_eats_retail_products_autodisable,
        testpoint,
        to_utc_datetime,
        yt_apply,
        yt_processing_status_state,
):
    set_periodic_config()

    @testpoint('yt-disabled-products-sync-finished')
    def periodic_end_run(param):
        pass

    if yt_processing_status_state == 'outdated':
        sql_set_yt_processing_status(
            pg_realdict_cursor, PREVIOUS_MONTH_DATE, 0,
        )
    elif yt_processing_status_state == 'up-to-date':
        sql_set_yt_processing_status(pg_realdict_cursor, CURRENT_DATE, 0)

    autodisabled_products = gen_autodisabled_products(to_utc_datetime)
    save_autodisabled_products_to_db(autodisabled_products)

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )
    assert periodic_end_run.times_called == 1

    if yt_processing_status_state == 'outdated':
        # need to launch periodic once more to start read new table
        await taxi_eats_retail_products_autodisable.run_distlock_task(
            PERIODIC_NAME,
        )
        assert periodic_end_run.times_called == 2

    assert sql_get_yt_processing_status(pg_realdict_cursor) == [
        {'last_read_table_name': CURRENT_DATE, 'row_to_read_from': 4},
    ]

    assert (
        sql_get_autodisabled_products(pg_realdict_cursor)
        == get_expected_disabled_products()
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data_outdated_table.yaml'],
)
async def test_update_autodisable_info_from_outdated_table(
        pg_realdict_cursor,
        save_autodisabled_products_to_db,
        set_periodic_config,
        taxi_eats_retail_products_autodisable,
        testpoint,
        to_utc_datetime,
        yt_apply,
):
    set_periodic_config()

    @testpoint('yt-disabled-products-sync-finished')
    def periodic_end_run(param):
        pass

    sql_set_yt_processing_status(pg_realdict_cursor, PREVIOUS_MONTH_DATE, 0)
    autodisabled_product = models.AutodisabledProduct(
        place_id=consts.PLACE_ID_1,
        origin_id=ORIGIN_ID_2,
        force_unavailable_until=to_utc_datetime(MOCK_NOW),
        algorithm_name=consts.ALGORITHM_NAME_THRESHOLD,
        last_disabled_at=to_utc_datetime(MOCK_NOW),
    )
    save_autodisabled_products_to_db([autodisabled_product])

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )

    assert periodic_end_run.times_called == 1

    assert sql_get_yt_processing_status(pg_realdict_cursor) == [
        {'last_read_table_name': CURRENT_DATE, 'row_to_read_from': 0},
    ]

    assert sql_get_autodisabled_products(pg_realdict_cursor) == [
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_2,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE,
        },
    ]


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data_read_from_exact_row.yaml'],
)
async def test_update_autodisable_info_from_exact_row(
        pg_realdict_cursor,
        save_autodisabled_products_to_db,
        set_periodic_config,
        taxi_eats_retail_products_autodisable,
        testpoint,
        to_utc_datetime,
        yt_apply,
):
    set_periodic_config()

    @testpoint('yt-disabled-products-sync-finished')
    def periodic_end_run(param):
        pass

    sql_set_yt_processing_status(pg_realdict_cursor, CURRENT_DATE, 1)
    autodisabled_product = models.AutodisabledProduct(
        place_id=consts.PLACE_ID_1,
        origin_id=ORIGIN_ID_2,
        force_unavailable_until=to_utc_datetime(MOCK_NOW),
        algorithm_name=consts.ALGORITHM_NAME_THRESHOLD,
        last_disabled_at=to_utc_datetime(MOCK_NOW),
    )
    save_autodisabled_products_to_db([autodisabled_product])

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )

    assert periodic_end_run.times_called == 1

    assert sql_get_yt_processing_status(pg_realdict_cursor) == [
        {'last_read_table_name': CURRENT_DATE, 'row_to_read_from': 3},
    ]

    # first row from yt table is ignored, so new product doesn't appear
    assert sql_get_autodisabled_products(pg_realdict_cursor) == [
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_2,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE,
        },
    ]


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def gen_autodisabled_products(to_utc_datetime):
    return [
        # unchanged
        models.AutodisabledProduct(
            place_id=consts.PLACE_ID_1,
            origin_id=ORIGIN_ID_1,
            force_unavailable_until=to_utc_datetime(OLD_UNAVAILABLE_UNTIL),
            algorithm_name=consts.ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
        # change force_unavailable_until to future
        models.AutodisabledProduct(
            place_id=consts.PLACE_ID_1,
            origin_id=ORIGIN_ID_2,
            force_unavailable_until=to_utc_datetime(MOCK_NOW),
            algorithm_name=consts.ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
        # disable: change force_unavailable_until to now
        models.AutodisabledProduct(
            place_id=consts.PLACE_ID_1,
            origin_id=ORIGIN_ID_3,
            force_unavailable_until=to_utc_datetime(
                UNAVAILABLE_UNTIL_IN_FUTURE,
            ),
            algorithm_name=consts.ALGORITHM_NAME_THRESHOLD,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
    ]


def sql_get_autodisabled_products(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select
            place_id,
            origin_id,
            force_unavailable_until
        from eats_retail_products_autodisable.autodisabled_products
        """,
    )
    result = pg_realdict_cursor.fetchall()
    for row in result:
        if row['force_unavailable_until']:
            row['force_unavailable_until'] = row[
                'force_unavailable_until'
            ].isoformat('T')
    return sorted(result, key=lambda k: k['origin_id'])


def get_expected_disabled_products():
    return [
        # 1632139200000: 2021.09.20 12:00:00 UTC = NOW
        # OLD_UNAVAILABLE_UNTIL = NOW - 1 HOUR
        # UNAVAILABLE_UNTIL_IN_FUTURE = NOW + 1 HOUR
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_1,
            'force_unavailable_until': OLD_UNAVAILABLE_UNTIL,
        },
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_2,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE,
        },
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_3,
            'force_unavailable_until': MOCK_NOW,
        },
        {
            'place_id': consts.PLACE_ID_1,
            'origin_id': ORIGIN_ID_4,
            'force_unavailable_until': UNAVAILABLE_UNTIL_IN_FUTURE,
        },
    ]


def sql_get_yt_processing_status(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select last_read_table_name, row_to_read_from
        from
        eats_retail_products_autodisable.yt_disabled_products_processing_status
        """,
    )
    result = pg_realdict_cursor.fetchall()
    return result


def sql_set_yt_processing_status(
        pg_realdict_cursor, last_read_table_name, row_to_read_from,
):
    pg_realdict_cursor.execute(
        f"""
        insert into
        eats_retail_products_autodisable.yt_disabled_products_processing_status
        (last_read_table_name, row_to_read_from)
        values (
          '{last_read_table_name}',
           {row_to_read_from}
        )
        """,
    )
