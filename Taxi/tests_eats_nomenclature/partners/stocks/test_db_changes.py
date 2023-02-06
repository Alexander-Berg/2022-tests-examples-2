# pylint: disable=too-many-lines, import-error
import datetime as dt

import pytest
import pytz

from ... import utils

PLACE_ID = 1
BRAND_ID = 777

S3_STOCKS_PATH = 'stocks/stocks_1.json'
S3_OLD_STOCKS_PATH = 'old_stocks/stocks_1.json'
OLD_S3_AVAILABILITY_PATH = 'old_availability/availability_1.json'
STOCK_TASK_TYPE = 'stock'
AVAILABILITY_TASK_TYPE = 'availability'
MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
OLD_FORCE_UNAVAILABLE_UNTIL = '2017-01-01T01:00:00+00:00'
TEST_DATETIME = '2021-03-01T10:45:00+03:00'
TEST_DATETIME_2 = '2021-03-01T11:45:00+03:00'
TEST_DATETIME_3 = '2021-03-01T09:45:00+03:00'


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_update_db_values(
        put_stock_data_to_s3,
        stock_enqueue,
        assert_stock_file_in_s3_and_db,
        sql_add_place_product,
        sql_get_stocks,
):
    place_id = PLACE_ID
    brand_id = BRAND_ID
    old_brand_id = 888
    # Add product with the same origin_id and place_id but different brand_id.
    sql_add_place_product('item_origin_5', place_id, old_brand_id)
    item_with_wrong_brand_stock = None

    assert (
        _exract_stocks_values(
            sql_get_stocks(place_id),
            ['item_origin_3', 'item_origin_5', 'INVALID_ORIGIN_ID'],
        )
        == [
            ('item_origin_3', 30, brand_id),
            ('item_origin_5', None, brand_id),
            ('item_origin_5', item_with_wrong_brand_stock, old_brand_id),
        ]
    )

    new_stocks_data = [
        {'origin_id': 'item_origin_3', 'stocks': '3'},
        {'origin_id': 'item_origin_5', 'stocks': '5'},
        {'origin_id': 'INVALID_ORIGIN_ID', 'stocks': '42'},
    ]
    await put_stock_data_to_s3(new_stocks_data, S3_STOCKS_PATH)
    await stock_enqueue(1, S3_STOCKS_PATH, TEST_DATETIME, '1')

    assert (
        _exract_stocks_values(
            sql_get_stocks(place_id),
            ['item_origin_3', 'item_origin_5', 'INVALID_ORIGIN_ID'],
        )
        == [
            ('item_origin_3', 3, brand_id),
            ('item_origin_5', 5, brand_id),
            ('item_origin_5', item_with_wrong_brand_stock, old_brand_id),
        ]
    )

    assert_stock_file_in_s3_and_db(
        place_id, S3_OLD_STOCKS_PATH, TEST_DATETIME, new_stocks_data,
    )

    # enqueue a newer file
    new_stocks_data_2 = [
        {'origin_id': 'item_origin_3', 'stocks': '1'},
        {'origin_id': 'item_origin_5', 'stocks': '2'},
        {'origin_id': 'INVALID_ORIGIN_ID', 'stocks': '42'},
    ]

    await put_stock_data_to_s3(new_stocks_data_2, S3_STOCKS_PATH)
    await stock_enqueue(1, S3_STOCKS_PATH, TEST_DATETIME_2, '1')

    expected_stocks = [
        ('item_origin_3', 1, brand_id),
        ('item_origin_5', 2, brand_id),
        ('item_origin_5', item_with_wrong_brand_stock, old_brand_id),
    ]
    assert (
        _exract_stocks_values(
            sql_get_stocks(place_id),
            ['item_origin_3', 'item_origin_5', 'INVALID_ORIGIN_ID'],
        )
        == expected_stocks
    )
    assert_stock_file_in_s3_and_db(
        place_id, S3_OLD_STOCKS_PATH, TEST_DATETIME_2, new_stocks_data_2,
    )

    # enqueue an older file
    new_stocks_data_3 = [
        {'origin_id': 'item_origin_3', 'stocks': '333'},
        {'origin_id': 'item_origin_5', 'stocks': '555'},
        {'origin_id': 'INVALID_ORIGIN_ID', 'stocks': '42'},
    ]

    await put_stock_data_to_s3(new_stocks_data_3, S3_STOCKS_PATH)
    await stock_enqueue(1, S3_STOCKS_PATH, TEST_DATETIME_3, '1')

    # the stocks and last processed file are the same as in the previous case
    assert (
        _exract_stocks_values(
            sql_get_stocks(place_id),
            ['item_origin_3', 'item_origin_5', 'INVALID_ORIGIN_ID'],
        )
        == expected_stocks
    )
    assert_stock_file_in_s3_and_db(
        place_id, S3_OLD_STOCKS_PATH, TEST_DATETIME_2, new_stocks_data_2,
    )


@pytest.mark.parametrize(**utils.gen_bool_params('merge_availability'))
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_update_with_availability_file(
        update_taxi_config,
        put_availability_data_to_s3,
        put_stock_data_to_s3,
        sql_save_availability_file,
        stock_enqueue,
        assert_stock_file_in_s3_and_db,
        sql_get_stocks,
        # parametrize
        merge_availability,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {'should_merge_availabilities_in_stocks_stq': merge_availability},
    )

    place_id = PLACE_ID
    brand_id = BRAND_ID

    new_stocks_data = [
        {'origin_id': 'item_origin_1'},
        {'origin_id': 'item_origin_2', 'stocks': '0'},
        {'origin_id': 'item_origin_3', 'stocks': '0'},
        {'origin_id': 'item_origin_4', 'stocks': '1'},
        {'origin_id': 'item_origin_5', 'stocks': '2'},
    ]
    availability_data = [
        # null to zero
        {'origin_id': 'item_origin_1', 'available': False},
        # zero unchanged
        {'origin_id': 'item_origin_2', 'available': True},
        # zero unchanged
        {'origin_id': 'item_origin_3', 'available': False},
        # nonzero unchanged
        {'origin_id': 'item_origin_4', 'available': True},
        # nonzero to zero
        {'origin_id': 'item_origin_5', 'available': False},
    ]
    if merge_availability:
        expected_data = [
            ('item_origin_1', 0, brand_id),
            ('item_origin_2', 0, brand_id),
            ('item_origin_3', 0, brand_id),
            ('item_origin_4', 1, brand_id),
            ('item_origin_5', 0, brand_id),
        ]
    else:
        expected_data = [
            ('item_origin_1', None, brand_id),
            ('item_origin_2', 0, brand_id),
            ('item_origin_3', 0, brand_id),
            ('item_origin_4', 1, brand_id),
            ('item_origin_5', 2, brand_id),
        ]

    await put_availability_data_to_s3(
        availability_data, OLD_S3_AVAILABILITY_PATH, place_id, MOCK_NOW,
    )
    await sql_save_availability_file(
        place_id, OLD_S3_AVAILABILITY_PATH, MOCK_NOW,
    )

    await put_stock_data_to_s3(new_stocks_data, S3_STOCKS_PATH)
    await stock_enqueue(1, S3_STOCKS_PATH, TEST_DATETIME, '1')

    db_data = _exract_stocks_values(
        sql_get_stocks(place_id),
        [
            'item_origin_1',
            'item_origin_2',
            'item_origin_3',
            'item_origin_4',
            'item_origin_5',
        ],
    )
    assert db_data == expected_data

    # values in stock file should be unaffected
    # by values from availability file
    assert_stock_file_in_s3_and_db(
        place_id, S3_OLD_STOCKS_PATH, TEST_DATETIME, new_stocks_data,
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_update_with_duplicate_product_ids(
        put_stock_data_to_s3, stock_enqueue, sql_get_stocks,
):
    place_id = PLACE_ID
    brand_id = BRAND_ID

    assert _exract_stocks_values(
        sql_get_stocks(place_id), ['item_origin_3'],
    ) == [('item_origin_3', 30, brand_id)]

    new_stocks_data = [
        {'origin_id': 'item_origin_3', 'stocks': '3'},
        {'origin_id': 'item_origin_3', 'stocks': '3'},
    ]

    await put_stock_data_to_s3(new_stocks_data)
    await stock_enqueue()

    assert _exract_stocks_values(
        sql_get_stocks(place_id), ['item_origin_3'],
    ) == [('item_origin_3', 3, brand_id)]


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_update_with_duplicate_origin_ids(
        taxi_eats_nomenclature,
        load_json,
        put_stock_data_to_s3,
        sql_upsert_place,
        brand_task_enqueue,
        stock_enqueue,
        sql_get_stocks,
):
    place_id = PLACE_ID
    brand_id = BRAND_ID
    sql_upsert_place(place_id=place_id, place_slug='lavka_krasina')

    stock_values = [
        ('item_origin_1', 10, brand_id),
        ('item_origin_2', 20, brand_id),
    ]
    assert (
        _exract_stocks_values(
            sql_get_stocks(place_id), [i[0] for i in stock_values],
        )
        == stock_values
    )

    async def perform_test_for_data(upload_data, stock_values):
        await brand_task_enqueue('1', brand_nomenclature=upload_data)
        await taxi_eats_nomenclature.invalidate_caches()

        new_stocks = [
            {'origin_id': i[0], 'stocks': str(i[1])} for i in stock_values
        ]
        await put_stock_data_to_s3(new_stocks)
        await stock_enqueue()

        assert (
            _exract_stocks_values(
                sql_get_stocks(place_id), [i[0] for i in stock_values],
            )
            == stock_values
        )

    # Upload item with the same origin_id, but with different property value
    # (should use the same product)
    upload_data = load_json('upload_data_for_duplicate_test.json')
    stock_values = [
        ('item_origin_1', 3, brand_id),
        ('item_origin_2', 5, brand_id),
    ]
    await perform_test_for_data(upload_data, stock_values)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_update_with_null_value(
        put_stock_data_to_s3, stock_enqueue, sql_get_stocks,
):
    place_id = PLACE_ID
    brand_id = BRAND_ID

    assert (
        _exract_stocks_values(
            sql_get_stocks(place_id),
            ['item_origin_1', 'item_origin_3', 'item_origin_5'],
        )
        == [
            ('item_origin_1', 10, brand_id),
            ('item_origin_3', 30, brand_id),
            ('item_origin_5', None, brand_id),
        ]
    )

    new_stocks = [
        {'origin_id': 'item_origin_1'},
        {'origin_id': 'item_origin_3', 'stocks': None},
        {'origin_id': 'item_origin_5', 'stocks': '5'},
    ]
    await put_stock_data_to_s3(new_stocks)
    await stock_enqueue()

    assert (
        _exract_stocks_values(
            sql_get_stocks(place_id),
            ['item_origin_1', 'item_origin_3', 'item_origin_5'],
        )
        == [
            ('item_origin_1', None, brand_id),
            ('item_origin_3', None, brand_id),
            ('item_origin_5', 5, brand_id),
        ]
    )

    # Invert stock data values to validate
    # null-to-value and value-to-null merge

    new_stocks = [
        {'origin_id': 'item_origin_1', 'stocks': '1'},
        {'origin_id': 'item_origin_3', 'stocks': '3'},
        {'origin_id': 'item_origin_5'},
    ]
    await put_stock_data_to_s3(new_stocks)
    await stock_enqueue()

    assert (
        _exract_stocks_values(
            sql_get_stocks(place_id),
            ['item_origin_1', 'item_origin_3', 'item_origin_5'],
        )
        == [
            ('item_origin_1', 1, brand_id),
            ('item_origin_3', 3, brand_id),
            ('item_origin_5', None, brand_id),
        ]
    )


@pytest.mark.parametrize(**utils.gen_bool_params('merge_availability'))
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_task_last_status(
        update_taxi_config,
        put_availability_data_to_s3,
        put_stock_data_to_s3,
        sql_save_availability_file,
        stock_enqueue,
        sql_get_place_processing_last_status,
        sql_get_place_processing_last_status_history,
        # parametrize
        merge_availability,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {'should_merge_availabilities_in_stocks_stq': merge_availability},
    )

    place_id = PLACE_ID
    await put_availability_data_to_s3(
        [], OLD_S3_AVAILABILITY_PATH, place_id, MOCK_NOW,
    )
    await sql_save_availability_file(
        place_id, OLD_S3_AVAILABILITY_PATH, MOCK_NOW,
    )

    await put_stock_data_to_s3([], S3_STOCKS_PATH)
    await stock_enqueue(1, S3_STOCKS_PATH, TEST_DATETIME, '1')

    last_status = {
        'status': 'processed',
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    expected_place_proc_statuses = [last_status]
    assert (
        sql_get_place_processing_last_status(place_id, STOCK_TASK_TYPE)
        == last_status
    )
    assert (
        sql_get_place_processing_last_status_history(place_id, STOCK_TASK_TYPE)
        == expected_place_proc_statuses
    )
    if merge_availability:
        assert (
            sql_get_place_processing_last_status(
                place_id, AVAILABILITY_TASK_TYPE,
            )
            == last_status
        )
        assert (
            sql_get_place_processing_last_status_history(
                place_id, AVAILABILITY_TASK_TYPE,
            )
            == expected_place_proc_statuses
        )


@pytest.mark.parametrize(
    **utils.gen_bool_params('has_force_unavailability_just_started'),
)
@pytest.mark.parametrize(
    **utils.gen_bool_params('has_force_unavailability_just_ended'),
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data_for_force_unavailable_products.sql',
    ],
)
async def test_force_unavailable_handling(
        put_stock_data_to_s3,
        sql_set_need_recalculation,
        sql_has_need_recalculation,
        sql_set_force_unavailable_until,
        sql_get_force_unavailable_until,
        sql_is_force_unavailable,
        stock_enqueue,
        # parametrize params
        has_force_unavailability_just_started,
        has_force_unavailability_just_ended,
):
    place_id = PLACE_ID

    new_stocks_data = [
        {'origin_id': 'item_origin_6_force_unavailable', 'stocks': '10'},
        {'origin_id': 'item_origin_7_force_unavailable', 'stocks': '0'},
    ]

    if has_force_unavailability_just_started:
        sql_set_need_recalculation(place_id, 1, True)
    if has_force_unavailability_just_ended:
        sql_set_need_recalculation(place_id, 2, False)
        sql_set_force_unavailable_until(
            place_id,
            'item_origin_6_force_unavailable',
            OLD_FORCE_UNAVAILABLE_UNTIL,
        )

    await put_stock_data_to_s3(new_stocks_data, S3_STOCKS_PATH)
    await stock_enqueue(s3_path=S3_STOCKS_PATH)

    assert not sql_has_need_recalculation(place_id, 1)
    assert not sql_has_need_recalculation(place_id, 2)
    if has_force_unavailability_just_ended:
        # force unavailability has just ended only for item_origin_6
        assert not sql_get_force_unavailable_until(
            place_id, 'item_origin_6_force_unavailable',
        )
    else:
        assert sql_is_force_unavailable(
            place_id, 'item_origin_6_force_unavailable',
        )
    assert sql_is_force_unavailable(
        place_id, 'item_origin_7_force_unavailable',
    )


@pytest.mark.parametrize(
    'should_map_origin_to_product_by_brand',
    [
        pytest.param(True, id='map_product_id_by_brand'),
        pytest.param(False, id='map_product_id_by_place'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data_for_force_unavailable_products.sql',
        'fill_place_data_for_force_unavailable_products_brand.sql',
    ],
)
async def test_reset_need_recalculation_with_different_brand(
        put_stock_data_to_s3,
        sql_set_need_recalculation,
        sql_has_need_recalculation,
        taxi_config,
        stock_enqueue,
        # parametrize params
        should_map_origin_to_product_by_brand,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_TEMPORARY_CONFIGS': {
                'should_map_origin_to_product_by_brand': (
                    should_map_origin_to_product_by_brand
                ),
            },
        },
    )

    place_id = PLACE_ID

    not_changed_stocks = [
        {'origin_id': 'item_origin_6_force_unavailable', 'stocks': '10'},
        {'origin_id': 'item_origin_7_force_unavailable', 'stocks': '0'},
        {'origin_id': 'item_origin_8_force_unavailable', 'stocks': '0'},
    ]

    # set need_recalculation for both product_ids
    sql_set_need_recalculation(
        place_id, 3, True,
    )  # old product_id from previous brand
    sql_set_need_recalculation(place_id, 4, True)  # correct product_id

    await put_stock_data_to_s3(not_changed_stocks, S3_STOCKS_PATH)
    await stock_enqueue(s3_path=S3_STOCKS_PATH)

    if should_map_origin_to_product_by_brand:
        # need_recalculation is reset for correct product_id
        assert sql_has_need_recalculation(place_id, 3)
        assert not sql_has_need_recalculation(place_id, 4)
    else:
        # need_recalculation is reset for wrong product_id
        assert not sql_has_need_recalculation(place_id, 3)
        assert sql_has_need_recalculation(place_id, 4)


def _exract_stocks_values(stocks, origin_ids):
    return [s for s in stocks if s[0] in origin_ids]
