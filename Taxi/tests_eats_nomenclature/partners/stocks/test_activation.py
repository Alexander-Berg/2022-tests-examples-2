# pylint: disable=too-many-lines, import-error
import datetime as dt

import pytest
import pytz

from ... import utils

MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
OLD_S3_AVAILABILITY_PATH = 'old_availability/availability_1.json'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_enqueue_fts_indexer(
        put_stock_data_to_s3,
        stq,
        stq_call_forward,
        complete_enrichment_status,
        sql_mark_assortment_in_progress,
        renew_in_progress_assortment,
        duplicate_assortment_data,
        stock_enqueue,
):
    place_id = 1
    place_slug = '1'
    in_progress_assortment_id = renew_in_progress_assortment(place_id)
    sql_mark_assortment_in_progress(in_progress_assortment_id)
    complete_enrichment_status(
        place_id, {'stocks': False, 'custom_assortment': True},
    )

    duplicate_assortment_data(in_progress_assortment_id, 1)

    # random non-empty data
    stocks_data = [
        {'origin_id': 'item_origin_3', 'stocks': '3'},
        {'origin_id': 'item_origin_5', 'stocks': '5'},
        {'origin_id': 'INVALID_ORIGIN_ID', 'stocks': '42'},
    ]
    await put_stock_data_to_s3(stocks_data)
    await stock_enqueue()

    task_info = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    assert task_info['kwargs']['place_ids'] == [place_id]
    await stq_call_forward(task_info)

    task_info = (
        stq.eats_full_text_search_indexer_update_retail_place.next_call()
    )
    assert task_info['id'] == place_slug
    assert task_info['kwargs']['place_slug'] == place_slug


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    **utils.gen_bool_params(
        'is_assortment_enrichment_complete', 'enrichment complete',
    ),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_finish_processing(
        testpoint,
        stq,
        complete_enrichment_status,
        put_stock_data_to_s3,
        sql_mark_assortment_in_progress,
        renew_in_progress_assortment,
        duplicate_assortment_data,
        sql_are_stocks_ready,
        stock_enqueue,
        # parametrize
        is_assortment_enrichment_complete,
):
    place_id = 1

    in_progress_assortment_id = renew_in_progress_assortment(place_id)
    sql_mark_assortment_in_progress(in_progress_assortment_id)
    complete_enrichment_status(
        place_id,
        {
            'stocks': False,
            'custom_assortment': is_assortment_enrichment_complete,
        },
    )

    duplicate_assortment_data(in_progress_assortment_id, 1)

    await put_stock_data_to_s3([])
    await stock_enqueue()

    # stocks should be marked ready
    # only after assortment enrichment is complete
    assert sql_are_stocks_ready(place_id) == is_assortment_enrichment_complete

    assert (
        stq.eats_nomenclature_assortment_activation_notifier.has_calls
        == is_assortment_enrichment_complete
    )


@pytest.mark.parametrize(**utils.gen_bool_params('merge_availability'))
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_finish_processing_with_availability_file(
        update_taxi_config,
        complete_enrichment_status,
        put_stock_data_to_s3,
        put_availability_data_to_s3,
        sql_mark_assortment_in_progress,
        renew_in_progress_assortment,
        duplicate_assortment_data,
        sql_are_availabilities_ready,
        stock_enqueue,
        sql_save_availability_file,
        # parametrize
        merge_availability,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {'should_merge_availabilities_in_stocks_stq': merge_availability},
    )

    place_id = 1

    in_progress_assortment_id = renew_in_progress_assortment(place_id)
    sql_mark_assortment_in_progress(in_progress_assortment_id)
    complete_enrichment_status(place_id, {'availabilities': False})

    duplicate_assortment_data(in_progress_assortment_id, 1)

    await put_availability_data_to_s3(
        [], OLD_S3_AVAILABILITY_PATH, place_id, MOCK_NOW,
    )
    await sql_save_availability_file(
        place_id, OLD_S3_AVAILABILITY_PATH, MOCK_NOW,
    )

    await put_stock_data_to_s3([])
    await stock_enqueue()

    assert sql_are_availabilities_ready(place_id) == merge_availability
