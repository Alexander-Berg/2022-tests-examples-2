# pylint: disable=import-error
# pylint: disable=too-many-lines
import base64
import copy
import datetime as dt

from arc_market.idx.datacamp.proto.api import ExportMessage_pb2
import dateutil as du
from google.protobuf import json_format
import pytest
import pytz


BRAND_ID = 777
BRAND_ID_2 = 778
S3_PRICES_PATH = 'prices/prices_1.json'
S3_OLD_PRICES_PATH = 'old_prices/prices_1.json'
QUEUE_NAME = 'eats_nomenclature_update_prices'
PLACE_UPDATE_STATUS_PREFIX = 'price'
PRICE_TASK_TYPE = 'price'
MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
TEST_DATETIME = '2021-03-01T10:45:00+03:00'
TEST_DATETIME_2 = '2021-03-01T11:45:00+03:00'
TEST_DATETIME_3 = '2021-03-01T09:45:00+03:00'


def settings(
        max_retries_on_error=3,
        max_retries_on_busy=3,
        max_busy_time_in_ms=100000,
        retry_on_busy_delay_ms=1000,
):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'max_retries_on_busy': max_retries_on_busy,
            'max_busy_time_in_ms': max_busy_time_in_ms,
            'retry_on_busy_delay_ms': retry_on_busy_delay_ms,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_force_unavailable_products.sql',
        'fill_product_with_null_price.sql',
    ],
)
async def test_prices_merge(
        pgsql,
        taxi_config,
        put_prices_data_to_s3,
        prices_enqueue,
        assert_price_file_in_s3_and_db,
        get_in_progress_assortment,
        insert_enrichment_status,
        sql_get_place_processing_last_status,
        sql_get_place_processing_last_status_history,
        sql_add_place_product,
):
    place_id = 1
    old_brand_id = 888
    brand_id = 777

    # Delete place_product for product_id = 5.
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        delete from eats_nomenclature.stocks
        where place_product_id = 5
        """,
    )
    cursor.execute(
        """
        delete from eats_nomenclature.places_products
        where product_id = 5
        """,
    )

    # Add product with the same origin_id and place_id but different brand_id.
    sql_add_place_product('item_origin_1', place_id, old_brand_id, price=10)
    product_w_wrong_brand = (
        'item_origin_1',
        10.0,
        None,
        None,
        None,
        None,
        old_brand_id,
    )

    in_progress_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(in_progress_assortment_id, dt.datetime.now())

    # init prices
    prices_data = get_prices_data()
    await put_prices_data_to_s3(prices_data)
    await prices_enqueue()
    assert_price_file_in_s3_and_db(
        place_id, S3_OLD_PRICES_PATH, TEST_DATETIME, prices_data,
    )
    assert sql_get_prices(pgsql) == [
        ('item_origin_1', 10.0, 20, 10, 999.0, 999.0, brand_id),
        product_w_wrong_brand,
        ('item_origin_2', 30.0, None, None, None, None, brand_id),
        ('item_origin_3', 40.0, None, 5, 999.0, 999.0, brand_id),
        ('item_origin_4', 999.0, None, 30, 999.0, 999.0, brand_id),
        ('item_origin_5', 123.0, 234, None, 999.0, 999.0, brand_id),
        (
            'item_origin_6_force_unavailable',
            623.0,
            234,
            None,
            999.0,
            999.0,
            brand_id,
        ),
        (
            'item_origin_7_force_unavailable',
            723.0,
            234,
            None,
            999.0,
            999.0,
            brand_id,
        ),
        ('item_origin_8', 60, None, None, None, None, brand_id),
    ]

    # change prices and send newer file
    prices_data[0]['price'] = '11'
    prices_data[0]['old_price'] = '21'
    prices_data[0]['vat'] = '20'
    prices_data[1]['price'] = '31'
    prices_data[1]['full_price'] = '31'
    await put_prices_data_to_s3(prices_data, S3_PRICES_PATH)
    await prices_enqueue(place_id, S3_PRICES_PATH, TEST_DATETIME_2)
    assert_price_file_in_s3_and_db(
        place_id, S3_OLD_PRICES_PATH, TEST_DATETIME_2, prices_data,
    )
    assert sql_get_prices(pgsql) == [
        ('item_origin_1', 11.0, 21, 20, 999.0, 999.0, brand_id),
        product_w_wrong_brand,
        ('item_origin_2', 31.0, None, None, 31.0, None, brand_id),
        ('item_origin_3', 40.0, None, 5, 999.0, 999.0, brand_id),
        ('item_origin_4', 999.0, None, 30, 999.0, 999.0, brand_id),
        ('item_origin_5', 123.0, 234, None, 999.0, 999.0, brand_id),
        (
            'item_origin_6_force_unavailable',
            623.0,
            234,
            None,
            999.0,
            999.0,
            brand_id,
        ),
        (
            'item_origin_7_force_unavailable',
            723.0,
            234,
            None,
            999.0,
            999.0,
            brand_id,
        ),
        ('item_origin_8', 60, None, None, None, None, brand_id),
    ]

    # change again, but send file with same datetime
    prices_data[0]['price'] = '12'
    prices_data[1]['old_full_price'] = '12'
    await put_prices_data_to_s3(prices_data, S3_PRICES_PATH)
    await prices_enqueue(place_id, S3_PRICES_PATH, TEST_DATETIME_2)
    assert_price_file_in_s3_and_db(
        place_id, S3_OLD_PRICES_PATH, TEST_DATETIME_2, prices_data,
    )
    last_sql_prices = [
        ('item_origin_1', 12.0, 21, 20, 999.0, 999.0, brand_id),
        product_w_wrong_brand,
        ('item_origin_2', 31.0, None, None, 31.0, 12.0, brand_id),
        ('item_origin_3', 40.0, None, 5, 999.0, 999.0, brand_id),
        ('item_origin_4', 999.0, None, 30, 999.0, 999.0, brand_id),
        ('item_origin_5', 123.0, 234, None, 999.0, 999.0, brand_id),
        (
            'item_origin_6_force_unavailable',
            623.0,
            234,
            None,
            999.0,
            999.0,
            brand_id,
        ),
        (
            'item_origin_7_force_unavailable',
            723.0,
            234,
            None,
            999.0,
            999.0,
            brand_id,
        ),
        ('item_origin_8', 60, None, None, None, None, brand_id),
    ]
    assert sql_get_prices(pgsql) == last_sql_prices

    # change again, but send file with older datetime
    prices_data_2 = copy.deepcopy(prices_data)
    prices_data_2[0]['price'] = '13'
    await put_prices_data_to_s3(prices_data_2, S3_PRICES_PATH)
    await prices_enqueue(place_id, S3_PRICES_PATH, TEST_DATETIME_3)
    # last processed file and prices are not changed
    assert_price_file_in_s3_and_db(
        place_id, S3_OLD_PRICES_PATH, TEST_DATETIME_2, prices_data,
    )
    assert sql_get_prices(pgsql) == last_sql_prices

    last_status = {
        'status': 'processed',
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    expected_place_proc_statuses = [last_status]

    assert (
        sql_get_place_processing_last_status(place_id, PRICE_TASK_TYPE)
        == last_status
    )

    assert (
        sql_get_place_processing_last_status_history(place_id, PRICE_TASK_TYPE)
        == expected_place_proc_statuses
    )


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stq_error_limit(
        task_enqueue_v2,
        pgsql,
        mds_s3_storage,
        taxi_config,
        put_prices_data_to_s3,
):
    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']
    task_id = '1'
    place_id = '1'
    kwargs = {
        'place_id': place_id,
        's3_path': S3_PRICES_PATH,
        'file_datetime': TEST_DATETIME,
    }
    invalid_prices_data = 1
    await put_prices_data_to_s3(invalid_prices_data)

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME,
            task_id=task_id,
            kwargs=kwargs,
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs=kwargs,
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    # no old price files should be created
    assert_no_old_price_files(pgsql, mds_s3_storage)


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(
        max_retries_on_busy=2, max_busy_time_in_ms=100000,
    ),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stq_busy_limit(
        mockserver,
        task_enqueue_v2,
        taxi_config,
        put_prices_data_to_s3,
        assert_price_file_in_s3_and_db,
        sql_set_place_busy,
        sql_is_place_busy,
):
    config = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')['__default__']
    max_retries_on_busy = config['max_retries_on_busy']
    max_busy_time_in_ms = config['max_busy_time_in_ms']
    retry_on_busy_delay_ms = config['retry_on_busy_delay_ms']
    task_id = '1'
    place_id = '1'
    kwargs = {
        'place_id': place_id,
        's3_path': S3_PRICES_PATH,
        'file_datetime': TEST_DATETIME,
    }
    prices_data = get_prices_data()
    await put_prices_data_to_s3(prices_data)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def mock_stq_reschedule(request):
        data = request.json
        assert data['queue_name'] == QUEUE_NAME
        assert data['task_id'] == task_id

        eta = du.parser.parse(data['eta']).replace(tzinfo=None)
        assert (
            eta - dt.datetime.now()
        ).total_seconds() < retry_on_busy_delay_ms

        return {}

    # initialize data
    await task_enqueue_v2(QUEUE_NAME, task_id=task_id, kwargs=kwargs)

    assert_price_file_in_s3_and_db(
        place_id, S3_OLD_PRICES_PATH, TEST_DATETIME, prices_data,
    )

    sql_set_place_busy(PLACE_UPDATE_STATUS_PREFIX, place_id)

    assert mock_stq_reschedule.times_called == 0

    for i in range(max_retries_on_busy):
        await task_enqueue_v2(
            QUEUE_NAME, task_id=task_id, kwargs=kwargs, reschedule_counter=i,
        )
        assert mock_stq_reschedule.times_called == i + 1
        assert sql_is_place_busy(PLACE_UPDATE_STATUS_PREFIX, place_id)

    # Exceed max busy retries
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs=kwargs,
        reschedule_counter=max_retries_on_busy,
    )
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    assert sql_is_place_busy(PLACE_UPDATE_STATUS_PREFIX, place_id)

    # Expire the busy status
    sql_set_place_busy(
        PLACE_UPDATE_STATUS_PREFIX, place_id, 3 * max_busy_time_in_ms,
    )
    await task_enqueue_v2(
        QUEUE_NAME, task_id=task_id, kwargs=kwargs, reschedule_counter=0,
    )
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    assert not sql_is_place_busy(PLACE_UPDATE_STATUS_PREFIX, place_id)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'is_assortment_enrichment_complete',
    [
        pytest.param(True, id='assortment enrichment complete'),
        pytest.param(False, id='assortment enrichment in progress'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_finish_processing(
        stq,
        stq_call_forward,
        testpoint,
        complete_enrichment_status,
        put_prices_data_to_s3,
        prices_enqueue,
        assert_price_file_in_s3_and_db,
        sql_mark_assortment_in_progress,
        renew_in_progress_assortment,
        duplicate_assortment_data,
        sql_are_prices_ready,
        # parametrize params
        is_assortment_enrichment_complete,
):
    place_id = 1

    in_progress_assortment_id = renew_in_progress_assortment(place_id)
    sql_mark_assortment_in_progress(in_progress_assortment_id)
    complete_enrichment_status(
        place_id,
        {
            'prices': False,
            'custom_assortment': is_assortment_enrichment_complete,
        },
    )

    duplicate_assortment_data(in_progress_assortment_id, 1)

    await put_prices_data_to_s3([])
    await prices_enqueue()

    assert_price_file_in_s3_and_db(place_id, S3_OLD_PRICES_PATH, TEST_DATETIME)

    # prices should be marked ready
    # only after assortment enrichment is complete
    assert sql_are_prices_ready(place_id) == is_assortment_enrichment_complete

    assert (
        stq.eats_nomenclature_assortment_activation_notifier.has_calls
        == is_assortment_enrichment_complete
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize('prices_have_changed', [True, False])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_lb_prices_have_changed(
        testpoint, put_prices_data_to_s3, prices_enqueue, prices_have_changed,
):
    place_id = 1

    @testpoint('yt-logger-new-prices')
    def yt_logger(data):
        del data['timestamp_raw']
        assert data == {
            'place_id': str(place_id),
            'timestamp': MOCK_NOW.strftime('%Y-%m-%dT%H:%M:%S'),
        }

    prices_data = []
    if prices_have_changed:
        prices_data = get_prices_data()
    await put_prices_data_to_s3(prices_data)
    await prices_enqueue()

    assert yt_logger.has_calls == prices_have_changed


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'should_include_pennies_in_price',
    [
        pytest.param(False, id='PRICE_ROUNDING config disabled'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_NOMENCLATURE_PRICE_ROUNDING={
                    '777': {'should_include_pennies_in_price': True},
                },
            ),
            id='PRICE_ROUNDING config with enabled brand',
        ),
    ],
)
@pytest.mark.parametrize('prices_have_changed', [True, False])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_products.sql',
        'fill_force_unavailable_products.sql',
    ],
)
async def test_market_log_place_products(
        testpoint,
        sql_add_place_product,
        put_prices_data_to_s3,
        prices_enqueue,
        should_include_pennies_in_price,
        prices_have_changed,
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

    # Add product with the same origin_id and place_id but different brand_id.
    sql_add_place_product('item_origin_1', 1, 888)

    prices_data = []
    if prices_have_changed:
        prices_data = get_prices_data()
    await put_prices_data_to_s3(prices_data)
    await prices_enqueue()

    assert logbroker_producer.has_calls == prices_have_changed

    expected_result = get_expected_logged_data(
        prices_have_changed, should_include_pennies_in_price,
    )

    assert (
        sorted(logged_data, key=lambda item: item['offer']['offerId'])
        == expected_result
    )


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
    files=[
        'fill_dictionaries.sql',
        'fill_place_products.sql',
        'fill_force_unavailable_products.sql',
        'fill_data_for_brand_778.sql',
    ],
)
async def test_market_log_place_products_black_list(
        testpoint,
        put_prices_data_to_s3,
        prices_enqueue,
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

    prices_data_1 = get_prices_data(BRAND_ID)
    await put_prices_data_to_s3(prices_data_1, place_id=1)
    await prices_enqueue(place_id=1, task_id='1')
    expected_result = get_expected_logged_data(True, False)
    expected_times_called = len(expected_result)
    assert logbroker_producer.times_called == expected_times_called
    assert sorted(
        logged_data, key=lambda item: item['offer']['offerId'],
    ) == sorted(expected_result, key=lambda item: item['offer']['offerId'])
    logged_data.clear()
    expected_result.clear()

    prices_data_2 = get_prices_data(BRAND_ID_2)
    await put_prices_data_to_s3(prices_data_2, place_id=2)
    await prices_enqueue(place_id=2, task_id='2')
    if BRAND_ID_2 not in brand_ids_black_list:
        expected_result = _get_expected_offer_for_brand_2()
        expected_times_called += len(expected_result)
    assert logbroker_producer.times_called == expected_times_called
    assert sorted(
        logged_data, key=lambda item: item['offer']['offerId'],
    ) == sorted(expected_result, key=lambda item: item['offer']['offerId'])


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_enqueue_fts_indexer_stq(
        pgsql,
        put_prices_data_to_s3,
        prices_enqueue,
        stq,
        stq_call_forward,
        complete_enrichment_status,
        sql_mark_assortment_in_progress,
        renew_in_progress_assortment,
        duplicate_assortment_data,
):
    place_id = 1
    place_slug = '1'
    in_progress_assortment_id = renew_in_progress_assortment(place_id)
    sql_mark_assortment_in_progress(in_progress_assortment_id)
    complete_enrichment_status(
        place_id, {'prices': False, 'custom_assortment': True},
    )

    duplicate_assortment_data(in_progress_assortment_id, 1)

    prices_data = get_prices_data()
    await put_prices_data_to_s3(prices_data)
    await prices_enqueue(place_id=place_id)

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


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_task_with_not_found_file(pgsql, prices_enqueue):
    place_id = 1
    wrong_path = 'wrong_path'

    await prices_enqueue(place_id, s3_path=wrong_path)

    assert sql_get_errors(pgsql, place_id=place_id) == (
        'failed',
        'Prices file is not found',
        'Prices file is not found at path ' + wrong_path,
    )


def get_prices_data(brand_id=BRAND_ID):
    if brand_id == BRAND_ID:
        return [
            {
                'origin_id': 'item_origin_1',
                'price': '10',
                'old_price': '20',
                'currency': 'RUB',
                'vat': '10',
                'full_price': '999',
                'old_full_price': '999',
            },
            {'origin_id': 'item_origin_2', 'price': '30', 'currency': 'RUB'},
            {
                'origin_id': 'item_origin_3',
                'price': '40',
                'currency': 'RUB',
                'vat': '5',
                'full_price': '999',
                'old_full_price': '999',
            },
            {
                'origin_id': 'item_origin_5',
                'price': '123',
                'old_price': '234',
                'currency': 'RUB',
                'full_price': '999',
                'old_full_price': '999',
            },
            {
                'origin_id': 'item_origin_6_force_unavailable',
                'price': '623',
                'old_price': '234',
                'currency': 'RUB',
                'full_price': '999',
                'old_full_price': '999',
            },
            {
                'origin_id': 'item_origin_7_force_unavailable',
                'price': '723',
                'old_price': '234',
                'currency': 'RUB',
                'full_price': '999',
                'old_full_price': '999',
            },
            {'origin_id': 'item_origin_8', 'price': '60', 'currency': 'RUB'},
            {
                'origin_id': 'INVALID_ORIGIN_ID',
                'price': '42',
                'old_price': '20',
                'currency': 'RUB',
                'full_price': '999',
                'old_full_price': '999',
            },
        ]
    return [
        {
            'origin_id': 'item_origin_8_additional',
            'price': '123',
            'old_price': '234',
            'currency': 'RUB',
            'full_price': '999',
            'old_full_price': '999',
        },
    ]


def sql_get_errors(pgsql, place_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select status, task_error, task_error_details
        from eats_nomenclature.places_processing_last_status_v2
        where place_id = {place_id}
        """,
    )
    return cursor.fetchone()


def sql_get_prices(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select p.origin_id, pp.price, pp.old_price, pp.vat, pp.full_price,
        pp.old_full_price, p.brand_id
        from eats_nomenclature.places_products pp
            join eats_nomenclature.products p on pp.product_id = p.id
        """,
    )
    return sorted(list(cursor), key=lambda row: (row[0], row[6]))


def metrics_config(name, max_dead_tuples_):
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


def assert_no_old_price_files(pgsql, mds_s3_storage):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select count(*)
        from eats_nomenclature.price_files
        """,
    )
    assert list(cursor)[0][0] == 0
    assert list(mds_s3_storage.storage.keys()) == [S3_PRICES_PATH]


def get_expected_logged_data(
        prices_have_changed, should_include_pennies_in_price,
):
    if not prices_have_changed:
        return []
    all_offers = [
        {
            'offer': {
                'businessId': 10,
                'offerId': '11111111-1111-1111-1111-111111111111',
                'originalSku': 'item_origin_1',
                'shopId': 20,
                'feedId': 30,
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 20,
                        'price': {
                            'currency': 'RUR',
                            'price': '9990000000',
                            'oldPrice': '9990000000',
                        },
                        'vat': 'VAT_10',
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
                'businessId': 10,
                'offerId': '22222222-2222-2222-2222-222222222222',
                'originalSku': 'item_origin_2',
                'shopId': 20,
                'feedId': 30,
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 20,
                        'price': {'currency': 'RUR', 'price': '300000000'},
                        'vat': 'NO_VAT',
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
                'businessId': 10,
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
                            'price': '9990000000',
                            'oldPrice': '9990000000',
                        },
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
                'businessId': 10,
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
                            'price': '4995000000',
                            'oldPrice': '4995000000',
                        },
                        'vat': 'NO_VAT',
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
                'businessId': 10,
                'offerId': '66666666-6666-6666-6666-666666666666',
                'originalSku': 'item_origin_6_force_unavailable',
                'shopId': 20,
                'feedId': 30,
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 20,
                        'price': {
                            'currency': 'RUR',
                            'price': '4995000000',
                            'oldPrice': '4995000000',
                        },
                        'vat': 'NO_VAT',
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
                'businessId': 10,
                'offerId': '77777777-7777-7777-7777-777777777777',
                'originalSku': 'item_origin_7_force_unavailable',
                'shopId': 20,
                'feedId': 30,
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 20,
                        'price': {
                            'currency': 'RUR',
                            'price': '4995000000',
                            'oldPrice': '4995000000',
                        },
                        'vat': 'NO_VAT',
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

    if not should_include_pennies_in_price:
        for item in all_offers:
            i_price = item['offer']['shopPrices'][0]['price']
            if i_price['price'] == '4995000000':
                i_price['price'] = '5000000000'
            if 'oldPrice' in i_price and i_price['oldPrice'] == '4995000000':
                i_price['oldPrice'] = '5000000000'
    return all_offers


def _get_expected_offer_for_brand_2():
    return [
        {
            'offer': {
                'businessId': 40,
                'offerId': '00000000-0000-0000-0000-000000000008',
                'shopId': 50,
                'feedId': 60,
                'originalSku': 'item_origin_8_additional',
                'shopPrices': [
                    {
                        'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                        'shopId': 50,
                        'price': {
                            'currency': 'RUR',
                            'price': '5000000000',
                            'oldPrice': '5000000000',
                        },
                        'vat': 'NO_VAT',
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
    ]
