import datetime as dt

import dateutil as du
import pytest
import pytz


QUEUE_NAME = 'eats_nomenclature_add_custom_assortment'
CATEGORIES_QUERY = """
    select name, assortment_id, is_custom
    from eats_nomenclature.categories
"""
MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
S3_OLD_PRICES_PATH = 'old_prices/prices_1.json'
S3_OLD_AVAILABILITY_PATH = 'old_availability/availability_1.json'
S3_OLD_STOCKS_PATH = 'old_stocks/stocks_1.json'
OLD_DATA_UPDATE_DELAY_IN_MIN = 10
UNAVAILABLE_PRODUCTS_ERROR_TYPE = (
    'New assortment has too much unavailable products'
)
UNAVAILABLE_PRODUCTS_ERROR_DETAILS = (
    '100% of products in new assortment are unavailable'
)
ZERO_PRICES_ERROR_TYPE = (
    'New assortment has too much products with zero prices'
)
ZERO_PRICES_ERROR_DETAILS = (
    '100% of products in new assortment have zero prices'
)
ASSORTMENT_NAME = 'test_1'


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


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_stq_error_limit(task_enqueue_v2, taxi_config):

    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']
    task_id = '1'
    bad_assortment_id = 123
    kwargs = {'assortment_id': bad_assortment_id}

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


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_busy=2),
    EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS={
        'assortment_enrichment_timeout_in_min': 90,
    },
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_stq_busy_limit(mockserver, task_enqueue_v2, pgsql, taxi_config):

    config = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')['__default__']
    max_retries_on_busy = config['max_retries_on_busy']
    retry_on_busy_delay_ms = config['retry_on_busy_delay_ms']

    config2 = taxi_config.get('EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS')
    timeout_in_minutes = config2['assortment_enrichment_timeout_in_min']

    assortment_id = 1
    task_id = '1'

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
    await task_enqueue_v2(QUEUE_NAME, task_id=task_id)

    assert mock_stq_reschedule.times_called == 0

    sql_set_custom_assortment_busy(pgsql, assortment_id)

    for i in range(max_retries_on_busy):
        await task_enqueue_v2(
            QUEUE_NAME, task_id=task_id, reschedule_counter=i,
        )
        assert mock_stq_reschedule.times_called == i + 1
        assert sql_is_custom_assortment_busy(pgsql, assortment_id)

    # Exceed max busy retries
    await task_enqueue_v2(
        QUEUE_NAME, task_id=task_id, reschedule_counter=max_retries_on_busy,
    )
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    assert sql_is_custom_assortment_busy(pgsql, assortment_id)

    # Expire the busy status
    sql_set_custom_assortment_busy(
        pgsql, assortment_id, 3 * timeout_in_minutes,
    )
    await task_enqueue_v2(QUEUE_NAME, task_id=task_id, reschedule_counter=0)
    # For this queue expire doesn't work
    # because checking of enrichment_started_at is implemented
    # in another way here
    # so busy status is not really expired
    assert mock_stq_reschedule.times_called == max_retries_on_busy + 1
    # and custom assortment is still busy
    assert sql_is_custom_assortment_busy(pgsql, assortment_id)


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize(
    'is_active, are_custom_categories_ready',
    [(False, True), (True, False), (True, True)],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_no_processing(
        stq_runner,
        sql_fill_custom_assortment,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        # parametrize params
        use_assortment_name,
        is_active,
        are_custom_categories_ready,
):
    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    place_id = 1
    old_assortment_id = 1
    sql_fill_custom_assortment(old_assortment_id)
    old_categories = sql_read_data(CATEGORIES_QUERY)

    # Add assortment which shouldn't be processed.
    assortment_id = sql_fill_enrichment_status(
        place_id, is_active, are_custom_categories_ready,
    )

    # Task is not processed with status "already being processed"
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id},
        expect_fail=False,
    )

    # New data wasn't uploaded to db.
    assert sql_read_data(CATEGORIES_QUERY) == old_categories


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize(
    'is_place_enrichment_complete, is_place_enabled, is_vendor_place',
    [
        pytest.param(True, True, False, id='place_enrichment_complete'),
        pytest.param(False, True, False, id='place_enrichment_in_progress'),
        pytest.param(
            False, True, True, id='vendor_place_enrichment_in_progress',
        ),
        pytest.param(
            False, False, False, id='disabled_place_enrichment_in_progress',
        ),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_finish_processing(
        pgsql,
        stq_runner,
        stq,
        complete_enrichment_status,
        testpoint,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        put_stock_data_to_s3,
        sql_are_custom_categories_ready,
        stocks_enqueue,
        # parametrize params
        use_assortment_name,
        is_place_enrichment_complete,
        is_place_enabled,
        is_vendor_place,
):
    place_id = 1

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    assortment_id = sql_fill_enrichment_status(
        place_id,
        is_active=False,
        are_custom_categories_ready=False,
        enrichment_started_at=MOCK_NOW,
    )
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    complete_enrichment_status(
        place_id,
        {
            'custom_assortment': False,
            'availabilities': is_place_enrichment_complete,
            'stocks': is_place_enrichment_complete,
        },
    )
    sql_set_place_data(pgsql, place_id, is_vendor_place, is_place_enabled)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': assortment_id},
    )

    # After processing are_custom_categories_ready should be true.
    assert sql_are_custom_categories_ready(assortment_id) is True

    # insert dummy stocks to run assortment activation
    await put_stock_data_to_s3([], place_id=place_id)
    await stocks_enqueue(place_id)

    assert (
        stq.eats_nomenclature_assortment_activation_notifier.has_calls
        == is_place_enrichment_complete
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_STOCKS_AND_AVAILABILITY_UPDATE_SETTINGS={
        'maximum_update_interval_in_min': 60,
        'old_data_update_delay_in_min': OLD_DATA_UPDATE_DELAY_IN_MIN,
    },
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_call_update_entities(
        load_json,
        stq_runner,
        stq,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        assert_and_call_entity_task,
        enqueue_verified_prices,
        enqueue_verified_availability,
        enqueue_verified_stocks,
        sql_are_prices_ready,
        sql_are_availabilities_ready,
        sql_are_stocks_ready,
        get_active_assortment,
        get_in_progress_assortment,
        sql_are_custom_categories_ready,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        complete_enrichment_status,
        # parametrize params
        use_assortment_name,
):
    place_id = 1

    await enqueue_verified_prices(file_datetime=MOCK_NOW.isoformat())
    await enqueue_verified_availability(file_datetime=MOCK_NOW.isoformat())
    await enqueue_verified_stocks(file_datetime=MOCK_NOW.isoformat())

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    assortment_id = sql_fill_enrichment_status(
        place_id,
        is_active=False,
        are_custom_categories_ready=False,
        enrichment_started_at=MOCK_NOW,
    )
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    complete_enrichment_status(
        place_id,
        {
            'custom_assortment': False,
            'prices': False,
            'availabilities': False,
            'stocks': False,
        },
    )
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': assortment_id},
    )

    # After processing are_custom_categories_ready should be true.
    assert sql_are_custom_categories_ready(assortment_id) is True

    # Prices, availability and stocks update tasks should have been run
    assert stq.eats_nomenclature_update_prices.times_called == 1
    assert stq.eats_nomenclature_update_availability.times_called == 1
    assert stq.eats_nomenclature_update_stocks.times_called == 1
    await assert_and_call_entity_task(
        'price',
        stq.eats_nomenclature_update_prices,
        place_id,
        S3_OLD_PRICES_PATH,
        MOCK_NOW,
        load_json('s3_prices.json')['items'],
        call_at=MOCK_NOW + dt.timedelta(minutes=OLD_DATA_UPDATE_DELAY_IN_MIN),
    )
    await assert_and_call_entity_task(
        'availability',
        stq.eats_nomenclature_update_availability,
        place_id,
        S3_OLD_AVAILABILITY_PATH,
        MOCK_NOW,
        load_json('s3_availability.json')['items'],
        call_at=MOCK_NOW + dt.timedelta(minutes=OLD_DATA_UPDATE_DELAY_IN_MIN),
    )
    await assert_and_call_entity_task(
        'stock',
        stq.eats_nomenclature_update_stocks,
        place_id,
        S3_OLD_STOCKS_PATH,
        MOCK_NOW,
        load_json('s3_stocks.json')['items'],
        call_at=MOCK_NOW + dt.timedelta(minutes=OLD_DATA_UPDATE_DELAY_IN_MIN),
    )
    assert sql_are_prices_ready(place_id) is True
    assert sql_are_availabilities_ready(place_id) is True
    assert sql_are_stocks_ready(place_id) is True

    # Assortment should be activated
    active_assortment_id = get_active_assortment(place_id)
    assert active_assortment_id == assortment_id
    assert not get_in_progress_assortment(place_id)

    last_status = {
        'assortment_id': assortment_id,
        'status': 'processed',
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    assert sql_get_place_assortment_proc_last_status(place_id) == last_status
    assert sql_get_place_assortment_last_status_history(place_id) == [
        last_status,
    ]


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_abort_processing_on_zero_price(
        pgsql,
        stq_runner,
        stq,
        complete_enrichment_status,
        sql_is_in_progress,
        testpoint,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        fill_brand_custom_categories,
        put_stock_data_to_s3,
        sql_are_custom_categories_ready,
        stocks_enqueue,
        # parametrize params
        use_assortment_name,
):
    place_id = 1

    @testpoint('eats-nomenclature_only-zero-price-products')
    def failed_on_zero_price(data):
        pass

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    assortment_id = sql_fill_enrichment_status(
        place_id,
        is_active=False,
        are_custom_categories_ready=False,
        enrichment_started_at=MOCK_NOW,
    )
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    complete_enrichment_status(
        place_id,
        {'custom_assortment': False, 'availabilities': True, 'stocks': True},
    )
    sql_set_place_data(pgsql, place_id, is_vendor=False, is_enabled=True)

    sql_zero_all_prices(pgsql)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': assortment_id},
    )

    # After processing are_custom_categories_ready should be true.
    assert sql_are_custom_categories_ready(assortment_id) is True

    # insert dummy stocks to run assortment activation
    await put_stock_data_to_s3([], place_id=place_id)
    await stocks_enqueue(place_id)

    assert failed_on_zero_price.has_calls

    last_status = {
        'assortment_id': assortment_id,
        'status': 'failed',
        'task_error': ZERO_PRICES_ERROR_TYPE,
        'task_error_details': ZERO_PRICES_ERROR_DETAILS,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    assert sql_get_place_assortment_proc_last_status(place_id) == last_status
    assert sql_get_place_assortment_last_status_history(place_id) == [
        last_status,
    ]

    assert sql_is_in_progress(assortment_id)
    assert (
        stq.eats_nomenclature_assortment_activation_notifier.times_called == 0
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_abort_processing_on_not_available(
        pgsql,
        stq_runner,
        stq,
        complete_enrichment_status,
        sql_is_in_progress,
        testpoint,
        sql_fill_custom_assortment,
        sql_fill_not_custom_categories,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        fill_brand_custom_categories,
        put_stock_data_to_s3,
        sql_are_custom_categories_ready,
        stocks_enqueue,
        # parametrize params
        use_assortment_name,
):
    place_id = 1

    @testpoint('eats-nomenclature_no-available-products')
    def failed_on_no_products(data):
        pass

    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    assortment_id = sql_fill_enrichment_status(
        place_id,
        is_active=False,
        are_custom_categories_ready=False,
        enrichment_started_at=MOCK_NOW,
    )
    sql_fill_custom_assortment(assortment_id)
    sql_fill_not_custom_categories(assortment_id)

    complete_enrichment_status(
        place_id,
        {'custom_assortment': False, 'availabilities': True, 'stocks': True},
    )
    sql_set_place_data(pgsql, place_id, is_vendor=False, is_enabled=True)
    sql_zero_all_availabilities(pgsql)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': assortment_id},
    )

    # After processing are_custom_categories_ready should be true.
    assert sql_are_custom_categories_ready(assortment_id) is True

    # insert dummy stocks to run assortment activation
    await put_stock_data_to_s3([], place_id=place_id)
    await stocks_enqueue(place_id)

    assert failed_on_no_products.has_calls

    last_status = {
        'assortment_id': assortment_id,
        'status': 'failed',
        'task_error': UNAVAILABLE_PRODUCTS_ERROR_TYPE,
        'task_error_details': UNAVAILABLE_PRODUCTS_ERROR_DETAILS,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    assert sql_get_place_assortment_proc_last_status(place_id) == last_status
    assert sql_get_place_assortment_last_status_history(place_id) == [
        last_status,
    ]

    assert sql_is_in_progress(assortment_id)
    assert (
        stq.eats_nomenclature_assortment_activation_notifier.times_called == 0
    )


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize('assortment_enrichment_timeout', [30, 60])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_assortment.sql'])
async def test_enrichment_timeout(
        taxi_config,
        stq_runner,
        assortment_enrichment_timeout,
        mocked_time,
        sql_fill_custom_assortment,
        sql_fill_products_and_pictures,
        sql_fill_enrichment_status,
        fill_brand_custom_categories,
        sql_read_data,
        use_assortment_name,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS': {
                'assortment_enrichment_timeout': assortment_enrichment_timeout,
            },
        },
    )
    # Fill brand custom categories.
    sql_fill_products_and_pictures()
    await fill_brand_custom_categories(
        ASSORTMENT_NAME if use_assortment_name else None,
    )

    # Fill old assortment.
    place_id = 1
    old_assortment_id = 1
    sql_fill_custom_assortment(old_assortment_id)
    old_categories = sql_read_data(CATEGORIES_QUERY)

    # Set inactive outdated assortment.
    assortment_id = sql_fill_enrichment_status(
        place_id,
        False,
        False,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id},
        expect_fail=False,
    )

    # New data wasn't uploaded to db.
    assert sql_read_data(CATEGORIES_QUERY) == old_categories


def sql_set_place_data(pgsql, place_id, is_vendor, is_enabled):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.places
        set
          is_vendor = {str(is_vendor).lower()},
          is_enabled = {str(is_enabled).lower()}
        where id = {place_id}
        """,
    )


def sql_set_custom_assortment_busy(
        pgsql, assortment_id, time_difference_in_min=0,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.assortment_enrichment_statuses (
            assortment_id,
            are_custom_categories_ready,
            custom_assortment_update_in_progress,
            enrichment_started_at
        )
        values (
            '{assortment_id}',
            false,
            true,
            now() - interval
            '{time_difference_in_min * 60} second'
        )
        on conflict (assortment_id)
        do update set
        are_custom_categories_ready = excluded.are_custom_categories_ready,
        custom_assortment_update_in_progress =
            excluded.custom_assortment_update_in_progress,
        enrichment_started_at = excluded.enrichment_started_at;
        """,
    )


def sql_is_custom_assortment_busy(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select custom_assortment_update_in_progress
        from eats_nomenclature.assortment_enrichment_statuses
        where assortment_id = {assortment_id}
        """,
    )
    return list(cursor)[0][0]


def sql_zero_all_prices(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.places_products
        set price = 0, full_price = 0
        """,
    )


def sql_zero_all_availabilities(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.places_products
        set available_from = null
        """,
    )
