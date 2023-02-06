# pylint: disable=too-many-lines, import-error
import base64
import datetime as dt

from arc_market.idx.datacamp.proto.api import ExportMessage_pb2
from google.protobuf import json_format
import pytest
import pytz

from ... import utils

BRAND_ID = 777
BRAND_ID_2 = 778
BUSINESS_ID = 10
BUSINESS_ID_2 = 40
S3_STOCKS_PATH = 'stocks/stocks_1.json'
MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
OLD_FORCE_UNAVAILABLE_UNTIL = '2017-01-01T01:00:00+00:00'
FUTURE_FORCE_UNAVAILABLE_UNTIL = MOCK_NOW + dt.timedelta(days=2)


@pytest.mark.parametrize(**utils.gen_bool_params('ignore_available_from'))
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_empty_place.sql'],
)
async def test_availability_changes(
        testpoint,
        put_stock_data_to_s3,
        stock_enqueue,
        pg_cursor,
        update_taxi_config,
        # parametrize
        ignore_available_from,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {'ignore_available_from': ignore_available_from},
    )

    place_id = 1
    old_brand_id = 888

    expected_origin_ids = []

    @testpoint('stocks-origin_ids-with-changed-availabilities')
    def tp_changed_availabilies(data):
        # use list to detect duplicate entries
        assert sorted(data['origin_ids']) == sorted(expected_origin_ids)

    new_data = []

    # these should not affect availability

    _sql_add_product_for_availability_test(
        pg_cursor, 'unchanged_zero', place_id, stocks=0, is_available=False,
    )
    new_data += [{'origin_id': 'unchanged_zero', 'stocks': '0'}]

    _sql_add_product_for_availability_test(
        pg_cursor, 'unchanged_null', place_id, stocks=None, is_available=True,
    )
    new_data += [{'origin_id': 'unchanged_null'}]

    _sql_add_product_for_availability_test(
        pg_cursor, 'unchanged_nonzero', place_id, stocks=1, is_available=True,
    )
    new_data += [{'origin_id': 'unchanged_nonzero', 'stocks': '1'}]

    _sql_add_product_for_availability_test(
        pg_cursor,
        'raw_changed_from_null_to_nonzero',
        place_id,
        stocks=None,
        is_available=True,
    )
    new_data += [
        {'origin_id': 'raw_changed_from_null_to_nonzero', 'stocks': '1'},
    ]

    _sql_add_product_for_availability_test(
        pg_cursor,
        'raw_changed_from_nonzero_to_nonzero',
        place_id,
        stocks=1,
        is_available=True,
    )
    new_data += [
        {'origin_id': 'raw_changed_from_nonzero_to_nonzero', 'stocks': '2'},
    ]

    _sql_add_product_for_availability_test(
        pg_cursor,
        'raw_changed_from_nonzero_to_null',
        place_id,
        stocks=1,
        is_available=True,
    )
    new_data += [{'origin_id': 'raw_changed_from_nonzero_to_null'}]

    _sql_add_product_for_availability_test(
        pg_cursor,
        'force_unavailability_already_started',
        place_id,
        stocks=None,
        is_available=True,
        need_recalculation=False,
        force_unavailable_until=FUTURE_FORCE_UNAVAILABLE_UNTIL,
    )
    new_data += [{'origin_id': 'force_unavailability_already_started'}]

    _sql_add_product_for_availability_test(
        pg_cursor,
        'change_with_wrong_brand',
        place_id,
        brand_id=BRAND_ID,
        stocks=None,
        is_available=True,
    )
    _sql_add_product_for_availability_test(
        pg_cursor,
        'change_with_wrong_brand',
        place_id,
        brand_id=old_brand_id,
        stocks=0,
        is_available=True,
    )
    new_data += [{'origin_id': 'change_with_wrong_brand'}]

    # these should affect availability

    _sql_add_product_for_availability_test(
        pg_cursor,
        'changed_from_zero_to_null',
        place_id,
        stocks=0,
        is_available=True,
    )
    new_data += [{'origin_id': 'changed_from_zero_to_null'}]
    expected_origin_ids += ['changed_from_zero_to_null']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'changed_from_zero_to_nonzero',
        place_id,
        stocks=0,
        is_available=True,
    )
    new_data += [{'origin_id': 'changed_from_zero_to_nonzero', 'stocks': '1'}]
    expected_origin_ids += ['changed_from_zero_to_nonzero']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'changed_from_nonzero_to_zero',
        place_id,
        stocks=1,
        is_available=True,
    )
    new_data += [{'origin_id': 'changed_from_nonzero_to_zero', 'stocks': '0'}]
    expected_origin_ids += ['changed_from_nonzero_to_zero']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'changed_from_null_to_zero',
        place_id,
        stocks=None,
        is_available=True,
    )
    new_data += [{'origin_id': 'changed_from_null_to_zero', 'stocks': '0'}]
    expected_origin_ids += ['changed_from_null_to_zero']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'force_unavailability_just_started',
        place_id,
        stocks=None,
        is_available=True,
        need_recalculation=True,
        force_unavailable_until=FUTURE_FORCE_UNAVAILABLE_UNTIL,
    )
    new_data += [{'origin_id': 'force_unavailability_just_started'}]
    expected_origin_ids += ['force_unavailability_just_started']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'force_unavailability_just_ended',
        place_id,
        stocks=None,
        is_available=True,
        need_recalculation=False,
        force_unavailable_until=OLD_FORCE_UNAVAILABLE_UNTIL,
    )
    new_data += [{'origin_id': 'force_unavailability_just_ended'}]
    expected_origin_ids += ['force_unavailability_just_ended']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'changed_from_zero_to_null_duplicate',
        place_id,
        stocks=0,
        is_available=True,
    )
    new_data += [{'origin_id': 'changed_from_zero_to_null_duplicate'}]
    new_data += [{'origin_id': 'changed_from_zero_to_null_duplicate'}]
    expected_origin_ids += ['changed_from_zero_to_null_duplicate']

    # conditional

    _sql_add_product_for_availability_test(
        pg_cursor,
        'raw_changed_from_nonzero_to_zero',
        place_id,
        stocks=1,
        is_available=False,
    )
    new_data += [
        {'origin_id': 'raw_changed_from_nonzero_to_zero', 'stocks': '0'},
    ]
    if ignore_available_from:
        expected_origin_ids += ['raw_changed_from_nonzero_to_zero']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'raw_changed_from_zero_to_nonzero',
        place_id,
        stocks=0,
        is_available=False,
    )
    new_data += [
        {'origin_id': 'raw_changed_from_zero_to_nonzero', 'stocks': '1'},
    ]
    if ignore_available_from:
        expected_origin_ids += ['raw_changed_from_zero_to_nonzero']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'raw_changed_from_zero_to_null',
        place_id,
        stocks=0,
        is_available=False,
    )
    new_data += [{'origin_id': 'raw_changed_from_zero_to_null'}]
    if ignore_available_from:
        expected_origin_ids += ['raw_changed_from_zero_to_null']

    _sql_add_product_for_availability_test(
        pg_cursor,
        'raw_changed_from_null_to_zero',
        place_id,
        stocks=None,
        is_available=False,
    )
    new_data += [{'origin_id': 'raw_changed_from_null_to_zero', 'stocks': '0'}]
    if ignore_available_from:
        expected_origin_ids += ['raw_changed_from_null_to_zero']

    await put_stock_data_to_s3(new_data, S3_STOCKS_PATH)
    await stock_enqueue(s3_path=S3_STOCKS_PATH)
    assert tp_changed_availabilies.has_calls


@pytest.mark.parametrize(**utils.gen_bool_params('merge_availability_file'))
@pytest.mark.parametrize(**utils.gen_bool_params('cause_availability_changes'))
@pytest.mark.parametrize(**utils.gen_bool_params('change_stock_value'))
@pytest.mark.parametrize(**utils.gen_bool_params('log_stock_changes'))
@pytest.mark.parametrize(
    **utils.gen_bool_params('has_active_place_categories'),
)
@pytest.mark.parametrize(
    **utils.gen_bool_params(
        'is_assortment_enrichment_complete', 'enrichment complete',
    ),
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_empty_place.sql'],
)
async def test_stock_change_side_effects(
        testpoint,
        put_stock_data_to_s3,
        update_taxi_config,
        taxi_config,
        get_in_progress_assortment,
        sql_mark_assortment_in_progress,
        complete_enrichment_status,
        sql_update_all_places_categories,
        stock_enqueue,
        pg_cursor,
        # parametrize params
        change_stock_value,
        cause_availability_changes,
        log_stock_changes,
        has_active_place_categories,
        is_assortment_enrichment_complete,
        merge_availability_file,
):
    brand_id = BRAND_ID
    place_id = 1

    if log_stock_changes:
        taxi_config.set_values(
            {
                'EATS_NOMENCLATURE_BRANDS_WITH_STOCK_LOG': {
                    'brand_ids': [brand_id],
                },
            },
        )
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {'should_merge_availabilities_in_stocks_stq': merge_availability_file},
    )

    @testpoint('yt-logger-stock-change')
    def yt_logger(data):
        assert data['place_id'] == str(place_id)
        assert data['changed_at'] == MOCK_NOW.strftime('%Y-%m-%dT%H:%M:%S')

    @testpoint('yt-logger-new-availability-new')
    def yt_logger_availability(data):
        del data['timestamp_raw']
        assert data == {
            'place_id': str(place_id),
            'timestamp': MOCK_NOW.strftime('%Y-%m-%dT%H:%M:%S'),
        }

    @testpoint('update-category-active-items-for-active')
    def categories_updater_for_active(data):  # pylint: disable=C0103
        pass

    @testpoint('update-category-active-items-for-in-progress')
    def categories_updater_for_in_progress(data):  # pylint: disable=C0103
        pass

    @testpoint('place-product-data-producer')
    def logbroker_producer(data):  # pylint: disable=C0103
        pass

    in_progress_assortment_id = get_in_progress_assortment(place_id)
    sql_mark_assortment_in_progress(in_progress_assortment_id)
    complete_enrichment_status(
        place_id,
        {
            'stocks': False,
            'custom_assortment': is_assortment_enrichment_complete,
        },
    )

    new_data = []
    expected_logs = []

    if change_stock_value:
        _sql_add_product_for_availability_test(
            pg_cursor, 'changed', place_id, stocks=1, is_available=True,
        )
        new_data += [{'origin_id': 'changed', 'stocks': '2'}]
        expected_logs += [('changed', 1, 2)]
    else:
        _sql_add_product_for_availability_test(
            pg_cursor, 'unchanged', place_id, stocks=1, is_available=True,
        )
        new_data += [{'origin_id': 'unchanged', 'stocks': '1'}]

    if cause_availability_changes:
        _sql_add_product_for_availability_test(
            pg_cursor,
            'availability_changed',
            place_id,
            stocks=0,
            is_available=True,
        )
        new_data += [{'origin_id': 'availability_changed'}]
        expected_logs += [('availability_changed', 0, None)]

    if not log_stock_changes:
        expected_logs = []

    sql_update_all_places_categories(
        place_id, 1 if has_active_place_categories else 0,
    )

    await put_stock_data_to_s3(new_data, S3_STOCKS_PATH)
    await stock_enqueue(s3_path=S3_STOCKS_PATH)

    assert yt_logger.times_called == len(expected_logs)
    logs = []
    for _ in range(yt_logger.times_called):
        data = yt_logger.next_call()['data']
        logs.append(
            (
                data['origin_id'],
                data['old_value'] if 'old_value' in data else None,
                data['new_value'] if 'new_value' in data else None,
            ),
        )
    assert sorted(logs, key=lambda item: item[0]) == sorted(
        expected_logs, key=lambda item: item[0],
    )

    assert yt_logger_availability.has_calls == (
        merge_availability_file
        and (cause_availability_changes or not has_active_place_categories)
    )

    assert categories_updater_for_active.has_calls == (
        cause_availability_changes or not has_active_place_categories
    )
    assert categories_updater_for_in_progress.has_calls == (
        (cause_availability_changes or not has_active_place_categories)
        and is_assortment_enrichment_complete
    )

    assert logbroker_producer.has_calls == cause_availability_changes


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data_for_category_availability.sql',
    ],
)
async def test_category_availability_changes(
        pgsql, put_stock_data_to_s3, get_active_assortment, stock_enqueue,
):
    place_id = 1
    active_assortment_id = get_active_assortment(place_id)

    async def post_new_data(new_stocks, place_id=1):
        await put_stock_data_to_s3(
            new_stocks, s3_path=S3_STOCKS_PATH, place_id=place_id,
        )
        await stock_enqueue(place_id=place_id, s3_path=S3_STOCKS_PATH)

    def verify_category_availability(
            expected_data,
            place_id=place_id,
            assortment_id=active_assortment_id,
    ):
        sql_data = _sql_get_place_categories(pgsql, place_id, assortment_id)
        # categories are not removed from db, hence can't use plain `==`
        assert all(
            x in sql_data for x in expected_data
        ), f'expected:\n\t{expected_data}\nrecieved:\n\t{sql_data}'

    # Make all products available via available_from
    for origin_id in [
            'item_origin_1',
            'item_origin_2',
            'item_origin_3',
            'item_origin_4',
            'item_origin_5',
            'item_origin_6',
    ]:
        _sql_set_availability_value(
            pgsql, place_id, active_assortment_id, origin_id, True,
        )

    # reset stocks
    await post_new_data(
        [
            {'stocks': '0', 'origin_id': 'item_origin_1'},
            {'stocks': '0', 'origin_id': 'item_origin_2'},
            {'stocks': '0', 'origin_id': 'item_origin_3'},
            {'stocks': '0', 'origin_id': 'item_origin_4'},
            {'stocks': '0', 'origin_id': 'item_origin_5'},
            {'stocks': '0', 'origin_id': 'item_origin_6'},
        ],
    )

    verify_category_availability(
        [
            {'category_id': 1, 'active_items_count': 0},
            {'category_id': 2, 'active_items_count': 0},
            {'category_id': 3, 'active_items_count': 0},
        ],
    )

    # check 0->2, 0->1 active items
    await post_new_data(
        [
            # category 1
            {'stocks': '1', 'origin_id': 'item_origin_1'},
            {'stocks': '1', 'origin_id': 'item_origin_2'},
            # category 2
            {'stocks': '1', 'origin_id': 'item_origin_4'},
        ],
    )
    expected_categories = [
        {'category_id': 1, 'active_items_count': 1},
        {'category_id': 2, 'active_items_count': 1},
        {'category_id': 3, 'active_items_count': 0},
    ]
    verify_category_availability(expected_categories)

    # check 2->3, 1->2 active items
    await post_new_data(
        [
            # category 1
            {'stocks': '1', 'origin_id': 'item_origin_1'},
            {'stocks': '1', 'origin_id': 'item_origin_2'},
            {'stocks': '1', 'origin_id': 'item_origin_3'},
            # category 2
            {'stocks': '1', 'origin_id': 'item_origin_4'},
            {'stocks': '1', 'origin_id': 'item_origin_5'},
        ],
    )
    expected_categories = [
        {'category_id': 1, 'active_items_count': 1},
        {'category_id': 2, 'active_items_count': 1},
        {'category_id': 3, 'active_items_count': 0},
    ]
    verify_category_availability(expected_categories)

    # check 3->2, 2->0 active items
    await post_new_data(
        [
            # category 1
            {'stocks': '1', 'origin_id': 'item_origin_1'},
            {'stocks': '1', 'origin_id': 'item_origin_2'},
            {'stocks': '0', 'origin_id': 'item_origin_3'},
            # category 2
            {'stocks': '0', 'origin_id': 'item_origin_4'},
            {'stocks': '0', 'origin_id': 'item_origin_5'},
        ],
    )
    expected_categories = [
        {'category_id': 1, 'active_items_count': 1},
        {'category_id': 2, 'active_items_count': 0},
        {'category_id': 3, 'active_items_count': 0},
    ]
    verify_category_availability(expected_categories)

    # check 2->0, 0->0, 0->1 active items
    await post_new_data(
        [
            # category 1
            {'stocks': '1', 'origin_id': 'item_origin_1'},
            {'stocks': '1', 'origin_id': 'item_origin_2'},
            {'stocks': '0', 'origin_id': 'item_origin_3'},
            # category 2
            {'stocks': '0', 'origin_id': 'item_origin_4'},
            {'stocks': '0', 'origin_id': 'item_origin_5'},
            # category 3 (child of category 1)
            {'stocks': '1', 'origin_id': 'item_origin_6'},
        ],
    )
    expected_categories = [
        {'category_id': 1, 'active_items_count': 1},
        {'category_id': 2, 'active_items_count': 0},
        {'category_id': 3, 'active_items_count': 1},
    ]
    verify_category_availability(expected_categories)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data_for_place_active_items_count.sql',
    ],
)
async def test_place_active_items_count_changes(
        pgsql, put_stock_data_to_s3, get_active_assortment, stock_enqueue,
):
    place_id = 1
    trait_id_1 = 1
    active_assortment_id = get_active_assortment(place_id)

    async def post_new_data(new_stocks):
        await put_stock_data_to_s3(
            new_stocks, s3_path=S3_STOCKS_PATH, place_id=place_id,
        )
        await stock_enqueue(place_id=place_id, s3_path=S3_STOCKS_PATH)

    # Make all products available via available_from
    for origin_id in [
            'item_origin_1',
            'item_origin_2',
            'item_origin_3',
            'item_origin_4',
            'item_origin_5',
            'item_origin_6',
    ]:
        _sql_set_availability_value(
            pgsql, place_id, active_assortment_id, origin_id, True,
        )

    # reset stocks
    await post_new_data(
        [
            {'stocks': '0', 'origin_id': 'item_origin_1'},
            {'stocks': '0', 'origin_id': 'item_origin_2'},
            {'stocks': '0', 'origin_id': 'item_origin_3'},
            {'stocks': '0', 'origin_id': 'item_origin_4'},
            {'stocks': '0', 'origin_id': 'item_origin_5'},
            {'stocks': '0', 'origin_id': 'item_origin_6'},
        ],
    )
    expected_data = [
        {'place_id': place_id, 'trait_id': None, 'active_items_count': 0},
        {'place_id': place_id, 'trait_id': 1, 'active_items_count': 0},
    ]
    expected_history = []
    expected_history += expected_data
    assert _sql_get_places_stats(pgsql) == expected_data
    assert _sql_get_places_stats_history(pgsql) == expected_history

    # check 0->3, 0->1 active items
    await post_new_data(
        [
            {'stocks': '1', 'origin_id': 'item_origin_1'},
            {'stocks': '1', 'origin_id': 'item_origin_2'},
            {'stocks': '1', 'origin_id': 'item_origin_4'},
        ],
    )
    expected_data = [
        {'place_id': place_id, 'trait_id': None, 'active_items_count': 3},
        {
            'place_id': place_id,
            'trait_id': trait_id_1,
            'active_items_count': 1,
        },
    ]
    expected_history += expected_data
    assert _sql_get_places_stats(pgsql) == expected_data
    assert _sql_get_places_stats_history(pgsql) == expected_history

    # check 3->5, 1->2 active items
    await post_new_data(
        [
            {'stocks': '1', 'origin_id': 'item_origin_1'},
            {'stocks': '1', 'origin_id': 'item_origin_2'},
            {'stocks': '1', 'origin_id': 'item_origin_3'},
            {'stocks': '1', 'origin_id': 'item_origin_4'},
            {'stocks': '1', 'origin_id': 'item_origin_5'},
        ],
    )
    expected_data = [
        {'place_id': place_id, 'trait_id': None, 'active_items_count': 5},
        {
            'place_id': place_id,
            'trait_id': trait_id_1,
            'active_items_count': 2,
        },
    ]
    expected_history += expected_data
    assert _sql_get_places_stats(pgsql) == expected_data
    assert _sql_get_places_stats_history(pgsql) == expected_history

    # check 5->5, 2->2 active items (nothing changes)
    await post_new_data(
        [
            {'stocks': '1', 'origin_id': 'item_origin_1'},
            {'stocks': '1', 'origin_id': 'item_origin_2'},
            {'stocks': '1', 'origin_id': 'item_origin_3'},
            {'stocks': '1', 'origin_id': 'item_origin_4'},
            {'stocks': '1', 'origin_id': 'item_origin_5'},
        ],
    )
    assert _sql_get_places_stats(pgsql) == expected_data
    assert _sql_get_places_stats_history(pgsql) == expected_history

    # check 5->2, 2->0 active items
    await post_new_data(
        [
            {'stocks': '1', 'origin_id': 'item_origin_1'},
            {'stocks': '1', 'origin_id': 'item_origin_2'},
            {'stocks': '0', 'origin_id': 'item_origin_3'},
            {'stocks': '0', 'origin_id': 'item_origin_4'},
            {'stocks': '0', 'origin_id': 'item_origin_5'},
        ],
    )
    expected_data = [
        {'place_id': place_id, 'trait_id': None, 'active_items_count': 2},
        {
            'place_id': place_id,
            'trait_id': trait_id_1,
            'active_items_count': 0,
        },
    ]
    expected_history += expected_data
    assert _sql_get_places_stats(pgsql) == expected_data
    assert _sql_get_places_stats_history(pgsql) == expected_history


@pytest.mark.parametrize(
    'should_include_pennies_in_price',
    [
        pytest.param(False, id='price rounding(-)'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_NOMENCLATURE_PRICE_ROUNDING={
                    str(BRAND_ID): {'should_include_pennies_in_price': True},
                },
            ),
            id='price rounding(+)',
        ),
    ],
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_market_products.sql'],
)
async def test_market_log_place_products(
        testpoint,
        put_stock_data_to_s3,
        stock_enqueue,
        should_include_pennies_in_price,
):
    logged_data = []

    @testpoint('place-product-data-producer')
    def logbroker_producer(data):
        decoded_data = base64.b64decode(data)
        export_message = ExportMessage_pb2.ExportMessage()
        export_message.ParseFromString(decoded_data)
        message_dict = json_format.MessageToDict(
            export_message, use_integers_for_enums=False,
        )
        logged_data.append(message_dict)

    new_stocks_data = [
        {'origin_id': 'item_origin_1', 'stocks': '10'},
        {'origin_id': 'item_origin_2', 'stocks': '0'},
        {'origin_id': 'item_origin_3', 'stocks': '30'},
        {'origin_id': 'item_origin_4', 'stocks': '0'},
        {'origin_id': 'item_origin_5', 'stocks': '0'},
    ]

    await put_stock_data_to_s3(new_stocks_data, S3_STOCKS_PATH)
    await stock_enqueue(s3_path=S3_STOCKS_PATH)

    expected_result = _get_expected_market_data(business_ids=[BUSINESS_ID])
    assert logbroker_producer.times_called == len(expected_result)

    if not should_include_pennies_in_price:
        for item in expected_result:
            i_price = item['offer']['shopPrices'][0]['price']
            if i_price['price'] == '4995000000':
                i_price['price'] = '5000000000'
            if 'oldPrice' in i_price and i_price['oldPrice'] == '4995000000':
                i_price['oldPrice'] = '5000000000'
    assert sorted(
        logged_data, key=lambda item: item['offer']['offerId'],
    ) == sorted(expected_result, key=lambda item: item['offer']['offerId'])


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'brand_ids_black_list',
    [
        pytest.param([], id='BLACK_LIST config disabled'),
        pytest.param([BRAND_ID_2], id='BLACK_LIST config enabled'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_market_products.sql'],
)
async def test_market_log_place_products_black_list(
        testpoint,
        put_stock_data_to_s3,
        stock_enqueue,
        update_taxi_config,
        # parametrize params
        brand_ids_black_list,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_EXPORT_TO_MARKET_BRANDS_BLACK_LIST',
        {'brand_ids': brand_ids_black_list},
    )
    logged_data = []

    @testpoint('place-product-data-producer')
    def logbroker_producer(data):
        decoded_data = base64.b64decode(data)
        export_message = ExportMessage_pb2.ExportMessage()
        export_message.ParseFromString(decoded_data)
        message_dict = json_format.MessageToDict(
            export_message, use_integers_for_enums=False,
        )
        logged_data.append(message_dict)

    new_stocks_data = [
        {'origin_id': 'item_origin_1', 'stocks': '10'},
        {'origin_id': 'item_origin_2', 'stocks': '0'},
        {'origin_id': 'item_origin_3', 'stocks': '30'},
        {'origin_id': 'item_origin_4', 'stocks': '0'},
        {'origin_id': 'item_origin_5', 'stocks': '0'},
    ]

    await put_stock_data_to_s3(new_stocks_data, place_id=1)
    await stock_enqueue(place_id=1, task_id='1')
    expected_data = _get_expected_market_data([BUSINESS_ID])
    expected_times_called = len(expected_data)
    assert logbroker_producer.times_called == expected_times_called
    assert sorted(
        logged_data, key=lambda item: item['offer']['offerId'],
    ) == sorted(expected_data, key=lambda item: item['offer']['offerId'])
    logged_data.clear()
    expected_data.clear()

    new_stocks_data_2 = [{'origin_id': 'item_origin_6', 'stocks': '100'}]
    await put_stock_data_to_s3(new_stocks_data_2, place_id=2)
    await stock_enqueue(place_id=2, task_id='2')
    if BRAND_ID_2 not in brand_ids_black_list:
        expected_data = _get_expected_market_data([BUSINESS_ID_2])
        expected_times_called += len(expected_data)
    assert logbroker_producer.times_called == expected_times_called
    assert sorted(
        logged_data, key=lambda item: item['offer']['offerId'],
    ) == sorted(expected_data, key=lambda item: item['offer']['offerId'])


def _sql_add_product_for_availability_test(
        pg_cursor,
        origin_id,
        place_id,
        brand_id=BRAND_ID,
        is_available=True,
        stocks=None,
        need_recalculation=False,
        force_unavailable_until=False,
):
    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.products(
            origin_id,
            description,
            shipping_type_id,
            vendor_id,
            name,
            quantum,
            measure_unit_id,
            measure_value,
            adult,
            is_catch_weight,
            is_choosable,
            brand_id
        )
        values (
            '{origin_id}',
            'descr_{origin_id}',
            1,
            1,
            'name_{origin_id}',
            0.2,
            1,
            1000,
            false,
            false,
            true,
            {brand_id}
        )
        returning id
    """,
    )
    product_id = pg_cursor.fetchone()[0]

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.categories_products(
            assortment_id,
            category_id,
            product_id,
            sort_order
        )
        values (1, 1, {product_id}, 1)
    """,
    )

    force_unavailable_until_str = (
        f'\'{force_unavailable_until}\'' if force_unavailable_until else 'null'
    )
    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.places_products(
            place_id,
            product_id,
            origin_id,
            price,
            available_from,
            force_unavailable_until
        )
        values (
            {place_id},
            {product_id},
            '{origin_id}',
            999,
            {f"'{MOCK_NOW}'" if is_available else 'null'},
            {force_unavailable_until_str}
        )
        returning id
    """,
    )
    place_product_id = pg_cursor.fetchone()[0]

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.stocks (place_product_id, value)
        values ({place_product_id}, {'null' if stocks is None else stocks})
    """,
    )

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.autodisabled_products(
            place_id,
            product_id,
            disabled_count,
            last_disabled_at,
            need_recalculation
        )
        values (
            {place_id},
            {product_id},
            0,
            null,
            {need_recalculation}
        )
    """,
    )


def _sql_get_place_categories(pgsql, place_id, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select category_id, active_items_count
        from eats_nomenclature.places_categories
        where place_id = {place_id} and assortment_id = {assortment_id}
        """,
    )
    return [{'category_id': i[0], 'active_items_count': i[1]} for i in cursor]


def _sql_get_places_stats(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select place_id, trait_id, active_items_count
        from eats_nomenclature.places_stats
        order by place_id, coalesce(trait_id, -1)
        """,
    )
    return [
        {'place_id': i[0], 'trait_id': i[1], 'active_items_count': i[2]}
        for i in cursor
    ]


def _sql_get_places_stats_history(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select place_id, trait_id, active_items_count
        from eats_nomenclature.places_stats_history
        order by id
        """,
    )
    return [
        {'place_id': i[0], 'trait_id': i[1], 'active_items_count': i[2]}
        for i in cursor
    ]


def _sql_set_availability_value(
        pgsql, place_id, assortment_id, origin_id, is_available,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        update eats_nomenclature.places_products pp
        set available_from = %s
        where
          id in (
            select id
            from eats_nomenclature.categories_products cp
              join eats_nomenclature.places_products pp
                on pp.product_id = cp.product_id
            where
              pp.place_id = %s
              and cp.assortment_id = %s
              and pp.origin_id = %s
          )
        """,
        (
            MOCK_NOW if is_available else None,
            place_id,
            assortment_id,
            origin_id,
        ),
    )


def _get_expected_market_data(business_ids):
    all_offers = [
        {
            'offer': {
                'businessId': BUSINESS_ID_2,
                'offerId': '00000000-0000-0000-0000-000000000006',
                'originalSku': 'item_origin_6',
                'shopId': 50,
                'feedId': 60,
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 50,
                        'price': {
                            'currency': 'RUR',
                            'price': '2000000000',
                            'oldPrice': '1500000000',
                        },
                        'vat': 'VAT_0',
                    },
                ],
                'shopStatuses': [
                    {
                        'shopId': 50,
                        'disableStatus': {
                            3: {
                                'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                                'flag': False,
                            },
                        },
                    },
                ],
            },
        },
        {
            'offer': {
                'businessId': BUSINESS_ID,
                'offerId': '33333333-3333-3333-3333-333333333333',
                'originalSku': 'item_origin_3',
                'shopId': 20,
                'feedId': 30,
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 20,
                        'price': {
                            'currency': 'RUR',
                            'price': '2000000000',
                            'oldPrice': '1500000000',
                        },
                        'vat': 'VAT_0',
                    },
                ],
                'shopStatuses': [
                    {
                        'shopId': 20,
                        'disableStatus': {
                            3: {
                                'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                                'flag': False,
                            },
                        },
                    },
                ],
            },
        },
        {
            'offer': {
                'businessId': BUSINESS_ID,
                'offerId': '44444444-4444-4444-4444-444444444444',
                'originalSku': 'item_origin_4',
                'shopId': 20,
                'feedId': 30,
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 20,
                        'price': {'currency': 'RUR', 'price': '0'},
                        'vat': 'WRONG_VAT',
                    },
                ],
                'shopStatuses': [
                    {
                        'shopId': 20,
                        'disableStatus': {
                            3: {
                                'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                                'flag': True,
                            },
                        },
                    },
                ],
            },
        },
        {
            'offer': {
                'businessId': BUSINESS_ID,
                'offerId': '55555555-5555-5555-5555-555555555555',
                'originalSku': 'item_origin_5',
                'shopId': 20,
                'feedId': 30,
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 20,
                        'price': {
                            'currency': 'RUR',
                            'price': '2500000000',
                            'oldPrice': '2000000000',
                        },
                        'vat': 'VAT_0',
                    },
                ],
                'shopStatuses': [
                    {
                        'shopId': 20,
                        'disableStatus': {
                            3: {
                                'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                                'flag': True,
                            },
                        },
                    },
                ],
            },
        },
    ]
    return list(
        filter(
            lambda i: (i['offer']['businessId'] in business_ids), all_offers,
        ),
    )
