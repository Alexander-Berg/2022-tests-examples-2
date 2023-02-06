import datetime as dt

import dateutil as du
import pytest

S3_STOCKS_PATH = 'stocks/stocks_1.json'
QUEUE_NAME = 'eats_nomenclature_update_stocks'
PLACE_UPDATE_STATUS_PREFIX = 'stock'
TEST_DATETIME = '2021-03-01T10:45:00+03:00'


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
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stq_error_limit(
        task_enqueue_v2, taxi_config, put_stock_data_to_s3,
):
    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']
    task_id = '1'
    place_id = '1'
    kwargs = {
        'place_id': place_id,
        's3_path': S3_STOCKS_PATH,
        'file_datetime': TEST_DATETIME,
    }
    invalid_stocks_data = [1]
    await put_stock_data_to_s3(invalid_stocks_data)

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
        put_stock_data_to_s3,
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
        's3_path': S3_STOCKS_PATH,
        'file_datetime': TEST_DATETIME,
    }
    # random non-empty data
    stocks_data = [
        {'origin_id': 'item_origin_3', 'stocks': '3'},
        {'origin_id': 'item_origin_5', 'stocks': '5'},
        {'origin_id': 'INVALID_ORIGIN_ID', 'stocks': '42'},
    ]
    await put_stock_data_to_s3(stocks_data)

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


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_task_with_not_found_file(pg_realdict_cursor, stocks_enqueue):
    place_id = 1
    wrong_path = 'wrong_path'

    await stocks_enqueue(place_id, s3_path=wrong_path)

    assert _sql_get_errors(pg_realdict_cursor, place_id=place_id) == {
        'status': 'failed',
        'task_error': 'Stocks file is not found',
        'task_error_details': f'Stocks file is not found at path {wrong_path}',
    }


def _sql_get_errors(pg_realdict_cursor, place_id):
    cursor = pg_realdict_cursor
    cursor.execute(
        f"""
        select status, task_error, task_error_details
        from eats_nomenclature.places_processing_last_status_v2
        where place_id = {place_id}
        """,
    )
    return cursor.fetchone()
