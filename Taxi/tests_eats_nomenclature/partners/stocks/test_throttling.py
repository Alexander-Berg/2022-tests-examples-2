import pytest


@pytest.mark.config(
    EATS_NOMENCLATURE_STOCKS_AND_AVAILABILITY_UPDATE_SETTINGS={
        'maximum_update_interval_in_min': 5,
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_db_full_throttling(
        taxi_config,
        pgsql,
        put_stock_data_to_s3,
        stock_enqueue,
        sql_get_stocks,
):
    taxi_config.set_values(_metrics_config('stock_processing', -1))
    place_id = 1
    old_stocks = sql_get_stocks(place_id)

    stocks_data = [
        {'origin_id': 'item_origin_3', 'stocks': '3'},
        {'origin_id': 'item_origin_5', 'stocks': '5'},
        {'origin_id': 'INVALID_ORIGIN_ID', 'stocks': '42'},
    ]
    await put_stock_data_to_s3(stocks_data)
    await stock_enqueue()

    assert sql_get_stocks(place_id) == old_stocks


@pytest.mark.config(
    EATS_NOMENCLATURE_STOCKS_AND_AVAILABILITY_UPDATE_SETTINGS={
        'maximum_update_interval_in_min': 5,
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_db_partial_throttling(
        taxi_config,
        pgsql,
        put_stock_data_to_s3,
        stock_enqueue,
        sql_get_stocks,
):
    taxi_config.set_values(_metrics_config('stock_processing', -1))
    place_id = 1
    old_stocks = sql_get_stocks(place_id)

    _sql_set_place_update_statuses(pgsql, interval_minutes=2)

    stocks_data = [
        {'origin_id': 'item_origin_3', 'stocks': '3'},
        {'origin_id': 'item_origin_5', 'stocks': '5'},
        {'origin_id': 'INVALID_ORIGIN_ID', 'stocks': '42'},
    ]
    await put_stock_data_to_s3(stocks_data)
    await stock_enqueue()

    assert sql_get_stocks(place_id) == old_stocks

    _sql_upd_place_update_statuses(pgsql, interval_minutes=10)

    await put_stock_data_to_s3(stocks_data)
    await stock_enqueue()

    assert sql_get_stocks(place_id) != old_stocks


def _sql_set_place_update_statuses(pgsql, interval_minutes):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.place_update_statuses
        (place_id, stock_update_started_at)
        values (1, now() - interval '{interval_minutes} minutes');""",
    )


def _sql_upd_place_update_statuses(pgsql, interval_minutes):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.place_update_statuses
        set stock_update_started_at =
            now() - interval '{interval_minutes} minutes',
            updated_at = now()
        where place_id = 1;""",
    )


def _metrics_config(name, max_dead_tuples_):
    return {
        'EATS_NOMENCLATURE_METRICS': {
            '__default__': {
                'assortment_outdated_threshold_in_hours': 2,
                'max_dead_tuples': 1000000,
            },
            name: {
                'assortment_outdated_threshold_in_hours': 2,
                'max_dead_tuples': max_dead_tuples_,
            },
        },
    }
