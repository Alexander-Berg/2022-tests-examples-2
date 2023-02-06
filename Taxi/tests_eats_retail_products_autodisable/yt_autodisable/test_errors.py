import pytest


PERIODIC_NAME = 'yt-disabled-products-sync'
MOCK_NOW = '2021-09-20T15:00:00+03:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data_with_unknown_place.yaml'],
)
async def test_ignore_info_for_unknown_place(
        pg_realdict_cursor,
        set_periodic_config,
        taxi_eats_retail_products_autodisable,
        testpoint,
        yt_apply,
):
    set_periodic_config()

    @testpoint('yt-disabled-products-sync-finished')
    def periodic_end_run(param):
        pass

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )

    assert periodic_end_run.times_called == 1
    # yt table contains only one row with place_id 2,
    # which is not in the config, so no new info appears
    assert sql_get_autodisabled_products(pg_realdict_cursor) == []


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_disable_schema.yaml'],
    static_table_data=['yt_disable_data_with_unknown_algorithm.yaml'],
)
async def test_ignore_info_for_unknown_algorithm(
        pg_realdict_cursor,
        set_periodic_config,
        taxi_eats_retail_products_autodisable,
        testpoint,
        yt_apply,
):
    set_periodic_config()

    @testpoint('yt-disabled-products-sync-finished')
    def periodic_end_run(param):
        pass

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )

    assert periodic_end_run.times_called == 1
    # yt table contains only one row with algorithm 'ml',
    # which is not in the config, so no new info appears
    assert sql_get_autodisabled_products(pg_realdict_cursor) == []


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
