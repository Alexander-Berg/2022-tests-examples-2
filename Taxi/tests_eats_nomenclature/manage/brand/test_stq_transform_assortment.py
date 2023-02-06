import datetime as dt

import dateutil as du
import pytest

QUEUE_NAME = 'eats_nomenclature_transform_assortment'
TEST_DATETIME = '2021-06-02T14:35:44+03:00'
S3_BRAND_NOMENCLATURE_PATH = '/some/path/brand_nomenclature.json'
ASSORTMENT_NAME = 'test_1'

CATEGORIES_QUERY = """
    select name, origin_id
    from eats_nomenclature.categories
"""


def processing_settings(
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


def timeouts_settings(assortment_enrichment_timeout):
    return {
        'EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS': {
            'assortment_enrichment_timeout': assortment_enrichment_timeout,
        },
    }


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=processing_settings(max_retries_on_error=2),
    EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS={
        'assortment_enrichment_timeout_in_min': 90,
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stq_error_limit(
        task_enqueue_v2,
        taxi_config,
        testpoint,
        get_active_assortment,
        get_in_progress_assortment,
        insert_enrichment_status,
        mocked_time,
        brand_task_enqueue,
        get_uploaded_file_path,
):
    @testpoint('eats-nomenclature-transform-assortment::fail-after-generated')
    def task_testpoint(param):
        return {'inject_failure': True}

    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']

    config2 = taxi_config.get('EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS')
    assortment_enrichment_timeout = config2[
        'assortment_enrichment_timeout_in_min'
    ]

    place_id = 1
    brand_id = 1
    await brand_task_enqueue(
        task_id='task',
        brand_id=str(brand_id),
        place_ids=[str(place_id)],
        file_datetime=TEST_DATETIME,
        call_transform_assortment=False,
    )
    processed_path = get_uploaded_file_path(place_id)

    active_assortment_id = get_active_assortment(place_id)
    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )
    task_id = str(active_assortment_id)
    kwargs = {'assortment_s3_url': processed_path, 'brand_id': brand_id}

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME,
            task_id=task_id,
            kwargs=kwargs,
            expect_fail=True,
            exec_tries=i,
        )
        outdated_assortment_id = get_in_progress_assortment(place_id)
        insert_enrichment_status(
            outdated_assortment_id,
            mocked_time.now()
            - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
        )

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs=kwargs,
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=processing_settings(max_retries_on_busy=2),
    EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS={
        'assortment_enrichment_timeout_in_min': 90,
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stq_busy_limit(
        mockserver,
        task_enqueue_v2,
        taxi_config,
        mocked_time,
        sql_set_assortment_busy,
        sql_is_assortment_busy,
        insert_enrichment_status,
        get_in_progress_assortment,
        brand_task_enqueue,
        get_uploaded_file_path,
):
    config = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')['__default__']
    max_retries_on_busy = config['max_retries_on_busy']
    retry_on_busy_delay_ms = config['retry_on_busy_delay_ms']

    config2 = taxi_config.get('EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS')
    timeout_in_minutes = config2['assortment_enrichment_timeout_in_min']

    place_id = 1
    brand_id = 1
    await brand_task_enqueue(
        task_id='task',
        brand_id=str(brand_id),
        place_ids=[str(place_id)],
        file_datetime=TEST_DATETIME,
    )
    processed_path = get_uploaded_file_path(place_id)

    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now() - dt.timedelta(minutes=timeout_in_minutes + 1),
    )
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
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
    )
    assert mock_stq_reschedule.times_called == 0

    in_progress_assortment_id = get_in_progress_assortment(place_id, True)
    assert sql_is_assortment_busy(
        in_progress_assortment_id, timeout_in_minutes,
    )
    prev_ip_assortment_id = in_progress_assortment_id

    for i in range(max_retries_on_busy):
        await task_enqueue_v2(
            QUEUE_NAME,
            task_id=task_id,
            kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
            reschedule_counter=i,
        )
        assert mock_stq_reschedule.times_called == i + 1
        in_progress_assortment_id = get_in_progress_assortment(place_id, True)
        assert in_progress_assortment_id == prev_ip_assortment_id
        assert sql_is_assortment_busy(
            in_progress_assortment_id, timeout_in_minutes,
        )

    # Exceed max busy retries
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        reschedule_counter=max_retries_on_busy,
    )
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    in_progress_assortment_id = get_in_progress_assortment(place_id, True)
    assert in_progress_assortment_id == prev_ip_assortment_id
    assert sql_is_assortment_busy(
        in_progress_assortment_id, timeout_in_minutes,
    )

    # Expire the busy status
    sql_set_assortment_busy(in_progress_assortment_id, 3 * timeout_in_minutes)
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        reschedule_counter=0,
    )
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    in_progress_assortment_id = get_in_progress_assortment(place_id, True)
    assert in_progress_assortment_id != prev_ip_assortment_id
    assert sql_is_assortment_busy(
        in_progress_assortment_id, timeout_in_minutes,
    )


@pytest.mark.parametrize('same_trait_id', [True, False])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_in_progress_assortment(
        pgsql,
        stq_runner,
        insert_enrichment_status,
        get_in_progress_assortment,
        brand_task_enqueue,
        get_uploaded_file_path,
        same_trait_id,
):
    place_id = 1
    brand_id = 1
    await brand_task_enqueue(
        task_id='task',
        brand_id=str(brand_id),
        place_ids=[str(place_id)],
        file_datetime=TEST_DATETIME,
    )
    processed_path = get_uploaded_file_path(place_id)

    old_categories = sql_read_sorted_data(pgsql, CATEGORIES_QUERY)

    # Insert inactive assortment which is being enriched and not outdated.
    in_progress_trait_id = 1
    in_progress_assortment_id = get_in_progress_assortment(
        place_id, trait_id=in_progress_trait_id,
    )
    insert_enrichment_status(in_progress_assortment_id, dt.datetime.now())

    stq_trait_id = (
        in_progress_trait_id
        if same_trait_id
        else sql_insert_assortment_trait(pgsql)
    )
    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id=f'{processed_path}_{stq_trait_id}',
        kwargs={
            'assortment_s3_url': processed_path,
            'brand_id': brand_id,
            'trait_id': stq_trait_id,
        },
        expect_fail=False,
    )

    # New data should be uploaded only if this place
    # doesn't have assortment of requested trait_id
    # which is being enriched and not outdated.
    new_data_was_uploaded = (
        sql_read_sorted_data(pgsql, CATEGORIES_QUERY) != old_categories
    )
    assert same_trait_id != new_data_was_uploaded


@pytest.mark.parametrize('assortment_enrichment_timeout', [30, 60])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_after_processing(
        taxi_config,
        stq_runner,
        stq,
        pgsql,
        mocked_time,
        insert_enrichment_status,
        get_in_progress_assortment,
        get_active_assortment,
        upload_verified_nomenclature_to_s3,
        get_uploaded_file_path,
        sql_get_enrichment_status,
        stq_call_forward,
        enqueue_verified_prices,
        enqueue_verified_availability,
        enqueue_verified_stocks,
        # parametrize params
        assortment_enrichment_timeout,
):
    place_id = 1
    brand_id = 1
    await upload_verified_nomenclature_to_s3(
        task_id='task',
        brand_id=str(brand_id),
        place_ids=[str(place_id)],
        file_datetime=TEST_DATETIME,
    )

    await enqueue_verified_prices()
    await enqueue_verified_availability()
    await enqueue_verified_stocks()

    processed_path = get_uploaded_file_path(place_id)
    active_assortment_id = get_active_assortment(place_id)
    taxi_config.set_values(timeouts_settings(assortment_enrichment_timeout))
    start_time = mocked_time.now()

    # Insert in-progress assortment which is outdated.
    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id=str(active_assortment_id),
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        expect_fail=False,
    )

    in_progress_assortment_id = get_in_progress_assortment(place_id, True)

    # After processing assortment_enrichment_status should be updated.
    status = sql_get_enrichment_status(in_progress_assortment_id)
    assert status[0]
    assert not status[1]
    assert status[2].replace(tzinfo=None) > start_time

    # After processing stq task in queue add_custom_assortment
    # should be created.
    assert stq.eats_nomenclature_add_custom_assortment.times_called == 1
    task_info = stq.eats_nomenclature_add_custom_assortment.next_call()
    assert task_info['kwargs']['assortment_id'] == in_progress_assortment_id
    await stq_call_forward(task_info)

    # Prices, availability and stocks update tasks should have been run
    assert stq.eats_nomenclature_update_prices.times_called == 1
    assert stq.eats_nomenclature_update_availability.times_called == 1
    assert stq.eats_nomenclature_update_stocks.times_called == 1


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_brand_custom_groups.sql', 'fill_dictionaries.sql'],
)
async def test_call_in_handler(
        taxi_eats_nomenclature,
        load_json,
        brand_task_enqueue,
        sql_get_assortment_trait_id,
        use_assortment_name,
):
    brand_id = 1
    sql_get_assortment_trait_id(
        brand_id,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )
    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )

    place_id1 = 1
    place_id2 = 2
    await brand_task_enqueue(
        task_id='task',
        brand_id=str(brand_id),
        place_ids=[str(place_id1)],
        file_datetime=TEST_DATETIME,
        call_transform_assortment=False,
    )

    await brand_task_enqueue(
        task_id='task',
        brand_id=str(brand_id),
        place_ids=[str(place_id2)],
        file_datetime=TEST_DATETIME,
        call_transform_assortment=False,
    )

    response = await taxi_eats_nomenclature.post(
        f'/v1/manage/brand/custom_categories_groups?brand_id={brand_id}'
        + assortment_query,
        json=load_json('request.json'),
    )

    assert response.status_code == 200


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS={
        'assortment_enrichment_timeout_in_min': 90,
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_no_mark_before_merge(
        testpoint,
        stq_runner,
        mocked_time,
        insert_enrichment_status,
        get_in_progress_assortment,
        brand_task_enqueue,
        get_uploaded_file_path,
        sql_are_availabilities_ready,
        taxi_config,
):
    @testpoint('eats-nomenclature-transform-assortment::fail-after-generated')
    def task_testpoint(param):
        return {'inject_failure': True}

    config2 = taxi_config.get('EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS')
    assortment_enrichment_timeout = config2[
        'assortment_enrichment_timeout_in_min'
    ]

    place_id = '1'
    brand_id = 1
    await brand_task_enqueue(
        task_id='task',
        brand_id=str(brand_id),
        place_ids=[place_id],
        file_datetime=TEST_DATETIME,
        call_transform_assortment=False,
    )
    processed_path = get_uploaded_file_path(place_id)

    outdated_assortment_id = get_in_progress_assortment(place_id)
    insert_enrichment_status(
        outdated_assortment_id,
        mocked_time.now()
        - dt.timedelta(minutes=assortment_enrichment_timeout + 1),
    )

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id='test_task',
        kwargs={'assortment_s3_url': processed_path, 'brand_id': brand_id},
        expect_fail=True,
    )
    assert not get_in_progress_assortment(place_id, True)
    assert not sql_are_availabilities_ready(place_id)

    assert task_testpoint.times_called == 1


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_task_with_not_found_file(pgsql, stq_runner):
    place_id = 1
    brand_id = 1
    wrong_path = 'wrong_path'

    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id='test_task',
        kwargs={
            'assortment_s3_url': wrong_path,
            'brand_id': brand_id,
            'place_ids': [str(place_id)],
        },
        expect_fail=False,
    )
    assert sql_get_errors(pgsql, place_id=place_id) == (
        'failed',
        'Assortment file is not found',
        'Assortment file is not found at path ' + wrong_path,
    )


def sql_insert_assortment_trait(
        pgsql, brand_id=1, assortment_name='some_new_assortment_name',
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.assortment_traits(
            brand_id, assortment_name
        )
        values({brand_id}, '{assortment_name}')
        returning id;
        """,
    )
    return cursor.fetchone()[0]


def sql_get_errors(pgsql, place_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select status, task_error, task_error_details
        from eats_nomenclature.place_assortments_processing_last_status
        where place_id = {place_id}
        """,
    )
    return cursor.fetchone()


def sql_read_sorted_data(pgsql, query):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(query)
    data = list(cursor)
    return sorted(data, key=lambda k: k[0])
