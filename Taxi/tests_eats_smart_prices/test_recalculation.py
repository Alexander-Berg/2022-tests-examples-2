import pytest

from tests_eats_smart_prices import utils


@pytest.mark.config(
    EATS_SMART_PRICES_YT_SETTINGS={
        'enabled': True,
        'yt_clusters': ['hahn'],
        'yt_path': '//home/testsuite/static/smart_prices',
        'yt_read_batch': 1000,
        'sleep_s': 600,
    },
)
@pytest.mark.yt(
    schemas=['yt_recalculator_schema.yaml'],
    static_table_data=['yt_recalculator_data.yaml'],
)
@pytest.mark.eats_catalog_storage_cache(
    utils.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.now('2022-03-31T19:00:00+00:00')
async def test_recalculation(
        taxi_eats_smart_prices, eats_smart_prices_cursor, yt_apply,
):
    # add recalculating settings
    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='1',
        status=utils.PlaceRecalcStatus.success,
        updated_at='2022-03-25T19:00:00+00:00',
    )  # will not be recalculated
    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='2',
        status=utils.PlaceRecalcStatus.success,
        updated_at='2022-03-20T19:00:00+00:00',
    )  # will be recalculated because of updated_at

    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='3',
        status=utils.PlaceRecalcStatus.need_recalculation,
        updated_at='2022-03-28T19:00:00+00:00',
    )  # will be recalculated bacause of status

    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='4',
        status=utils.PlaceRecalcStatus.need_recalculation,
        updated_at='2022-03-28T19:00:00+00:00',
    )  # will not be recalculater because no data it YT

    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='1',
        item_id='11',
        dynamic_part='13',
        start_time='2022-03-25T19:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # active

    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='3',
        item_id='31',
        dynamic_part='23',
        start_time='2022-03-30T00:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # active

    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='3',
        item_id='32',
        dynamic_part='23',
        start_time='2022-03-30T00:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # active

    await taxi_eats_smart_prices.run_task('smart-prices-yt-recalculator')

    eats_smart_prices_cursor.execute(
        'SELECT place_id, update_status, status_time '
        'FROM eats_smart_prices.place_recalculation '
        'ORDER BY place_id',
    )
    places = eats_smart_prices_cursor.fetchall()
    assert len(places) == 4

    # not updated
    assert places[0]['place_id'] == '1'
    assert places[0]['update_status'] == utils.PlaceRecalcStatus.success.name
    assert str(places[0]['status_time']) == '2022-03-25 22:00:00+03:00'

    assert places[1]['place_id'] == '2'
    assert places[1]['update_status'] == utils.PlaceRecalcStatus.success.name
    assert str(places[1]['status_time']) == '2022-03-24 22:00:00+03:00'

    assert places[2]['place_id'] == '3'
    assert places[2]['update_status'] == utils.PlaceRecalcStatus.success.name
    assert str(places[2]['status_time']) == '2022-03-24 22:00:00+03:00'

    assert places[3]['place_id'] == '4'
    assert (
        places[3]['update_status']
        == utils.PlaceRecalcStatus.need_recalculation.name
    )
    assert str(places[3]['status_time']) == '2022-03-28 22:00:00+03:00'

    eats_smart_prices_cursor.execute(
        'SELECT place_id, item_id, experiment_tag, dynamic_price_part, '
        'start_time, end_time FROM eats_smart_prices.items_settings '
        'ORDER BY place_id, item_id, start_time, experiment_tag',
    )
    items = eats_smart_prices_cursor.fetchall()

    assert len(items) == 6

    assert items[0]['item_id'] == '11'
    assert items[0]['place_id'] == '1'
    assert items[0]['experiment_tag'] is None
    assert str(items[0]['dynamic_price_part']) == '13.00'
    assert str(items[0]['start_time']) == '2022-03-25 22:00:00+03:00'
    assert items[0]['end_time'] is None

    assert items[1]['item_id'] == '22'
    assert items[1]['place_id'] == '2'
    assert items[1]['experiment_tag'] == 'exp1'
    assert str(items[1]['dynamic_price_part']) == '122.00'
    assert str(items[1]['start_time']) == '2022-04-01 02:00:00+03:00'
    assert items[1]['end_time'] is None

    assert items[2]['item_id'] == '31'
    assert items[2]['place_id'] == '3'
    assert items[2]['experiment_tag'] is None
    assert str(items[2]['dynamic_price_part']) == '23.00'
    assert str(items[2]['start_time']) == '2022-03-30 03:00:00+03:00'
    # because stop all items in place
    assert str(items[2]['end_time']) == '2022-04-01 02:00:00+03:00'

    assert items[3]['item_id'] == '32'
    assert items[3]['place_id'] == '3'
    assert items[3]['experiment_tag'] is None
    assert str(items[3]['dynamic_price_part']) == '23.00'
    assert str(items[3]['start_time']) == '2022-03-30 03:00:00+03:00'
    assert str(items[3]['end_time']) == '2022-04-01 02:00:00+03:00'

    assert items[4]['item_id'] == '32'
    assert items[4]['place_id'] == '3'
    assert items[4]['experiment_tag'] == 'exp1'
    assert str(items[4]['dynamic_price_part']) == '132.00'
    assert str(items[4]['start_time']) == '2022-04-01 02:00:00+03:00'
    assert items[4]['end_time'] is None

    assert items[5]['item_id'] == '32'
    assert items[5]['place_id'] == '3'
    assert items[5]['experiment_tag'] == 'exp2'
    assert str(items[5]['dynamic_price_part']) == '133.00'
    assert str(items[5]['start_time']) == '2022-04-01 02:00:00+03:00'
    assert items[5]['end_time'] is None
