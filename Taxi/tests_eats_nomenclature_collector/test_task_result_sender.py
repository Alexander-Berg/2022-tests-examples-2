# pylint: disable=too-many-lines
import copy
import datetime as dt
import json

import pytest
import pytz

from . import utils


MOCK_NOW = dt.datetime(2020, 3, 2, 12, tzinfo=pytz.UTC)
STQ_STOCKS_NAME = 'eats_nomenclature_update_stocks'
STOCK_MAX_VALUE = 100000000


@pytest.mark.parametrize(**utils.gen_bool_params('enable_nmn_call'))
@pytest.mark.parametrize(**utils.gen_bool_params('enable_vwr_call'))
@pytest.mark.parametrize(
    'config_name, table_name, data_filename, periodic_name, nmn_stq_name, vwr_stq_name',  # noqa: E501
    [
        pytest.param(
            'EATS_NOMENCLATURE_COLLECTOR_AVAILABILITY_TASK_RESULT_SENDER_SETTINGS',  # noqa: E501
            'availability_tasks',
            'test_availability1.json',
            'availability-task-result-sender',
            'eats_nomenclature_update_availability',
            'eats_nomenclature_viewer_update_availabilities',
            id='availability',
        ),
        pytest.param(
            'EATS_NOMENCLATURE_COLLECTOR_PRICE_TASK_RESULT_SENDER_SETTINGS',
            'price_tasks',
            'test_prices1.json',
            'price-task-result-sender',
            'eats_nomenclature_update_prices',
            'eats_nomenclature_viewer_update_prices',
            id='price',
        ),
        pytest.param(
            'EATS_NOMENCLATURE_COLLECTOR_STOCK_TASK_RESULT_SENDER_SETTINGS',
            'stock_tasks',
            'test_stocks1.json',
            'stock-task-result-sender',
            'eats_nomenclature_update_stocks',
            'eats_nomenclature_viewer_update_stocks',
            id='stock',
        ),
    ],
)
@pytest.mark.now(MOCK_NOW.isoformat())
async def test_sender_settings(
        taxi_eats_nomenclature_collector,
        load,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        update_taxi_config,
        # parametrize params
        enable_nmn_call,
        enable_vwr_call,
        config_name,
        table_name,
        data_filename,
        periodic_name,
        nmn_stq_name,
        vwr_stq_name,
):
    update_taxi_config(
        config_name,
        {'enabled': enable_nmn_call, 'vwr_enabled': enable_vwr_call},
    )

    s3path = 'some_path/file.json'

    mds_s3_storage.put_object(s3path, load(data_filename).encode('utf-8'))

    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(_):
        pass

    _sql_add_tasks(
        pg_cursor,
        table_name,
        [
            _generate_task(
                task_id='uuid',
                place_id=1,
                file_path=f'https://eda-integration.s3.mdst.yandex.net/{s3path}',  # noqa: E501
            ),
        ],
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )
    assert handle_task_finished.has_calls == (
        enable_nmn_call or enable_vwr_call
    )
    assert _count_processed(pg_cursor, table_name) == (
        enable_nmn_call or enable_vwr_call
    )

    assert (
        len(_get_all_stq_calls(getattr(stq, nmn_stq_name))) == enable_nmn_call
    )
    assert (
        len(_get_all_stq_calls(getattr(stq, vwr_stq_name))) == enable_vwr_call
    )


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_VALIDATION={
        '1': {
            'zero_prices_limit_in_percent': 60,
            'zero_stocks_limit_in_percent': 60,
            'unavailable_products_limit_in_percent': 60,
        },
    },
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'table_name, filename_tmpl, s3_path_tmpl, periodic_name, stq_name',
    [
        pytest.param(
            'price_tasks',
            'test_prices{}.json',
            'prices/prices_{}.json',
            'price-task-result-sender',
            'eats_nomenclature_update_prices',
            id='nmn price',
        ),
        pytest.param(
            'stock_tasks',
            'test_stocks{}.json',
            'stocks/stocks_{}.json',
            'stock-task-result-sender',
            STQ_STOCKS_NAME,
            id='nmn stock',
        ),
        pytest.param(
            'availability_tasks',
            'test_availability{}.json',
            'availability/availability_{}.json',
            'availability-task-result-sender',
            'eats_nomenclature_update_availability',
            id='nmn availability',
        ),
        pytest.param(
            'price_tasks',
            'test_prices{}.json',
            'viewer/new/price/{}.json',
            'price-task-result-sender',
            'eats_nomenclature_viewer_update_prices',
            id='vwr price',
        ),
        pytest.param(
            'stock_tasks',
            'test_stocks{}.json',
            'viewer/new/stock/{}.json',
            'stock-task-result-sender',
            'eats_nomenclature_viewer_update_stocks',
            id='vwr stock',
        ),
        pytest.param(
            'availability_tasks',
            'test_availability{}.json',
            'viewer/new/availability/{}.json',
            'availability-task-result-sender',
            'eats_nomenclature_viewer_update_availabilities',
            id='vwr availability',
        ),
    ],
)
async def test_normal(
        taxi_eats_nomenclature_collector,
        load_json,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        update_taxi_config,
        # parametrize params
        table_name,
        filename_tmpl,
        s3_path_tmpl,
        periodic_name,
        stq_name,
):
    is_vwr_queue = stq_name.startswith('eats_nomenclature_viewer')
    if is_vwr_queue:
        update_taxi_config(
            'EATS_NOMENCLATURE_COLLECTOR_AVAILABILITY_TASK_RESULT_SENDER_SETTINGS',  # noqa: E501
            {'enabled': False, 'vwr_enabled': True},
        )
        update_taxi_config(
            'EATS_NOMENCLATURE_COLLECTOR_PRICE_TASK_RESULT_SENDER_SETTINGS',
            {'enabled': False, 'vwr_enabled': True},
        )
        update_taxi_config(
            'EATS_NOMENCLATURE_COLLECTOR_STOCK_TASK_RESULT_SENDER_SETTINGS',
            {'enabled': False, 'vwr_enabled': True},
        )

    if is_vwr_queue:
        # vwr queue recieves int place_id
        place_id_1 = 1
        place_id_2 = 2
    else:
        # nmn queue recieves str place_id
        place_id_1 = '1'
        place_id_2 = '2'

    uuid_place_1 = 'uuid_3'
    uuid_place_2 = 'uuid_4'
    uuid_place_1_overwrite = 'uuid_5'

    sender_stq = getattr(stq, stq_name)

    filename_1 = filename_tmpl.format(place_id_1)
    filename_2 = filename_tmpl.format(place_id_2)
    filename_3 = filename_tmpl.format(f'{place_id_1}_overwrite')

    data_1 = load_json(filename_1)
    data_2 = load_json(filename_2)
    data_3 = load_json(filename_3)

    # make zero price for first item, so 33% of items has zero price
    # and it's less than limit, so it isn't an error
    if table_name == 'price_tasks':
        data_2['items'][0]['price'] = '0'

    mds_s3_storage.put_object(
        f'some_path/{filename_1}', json.dumps(data_1).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        f'some_path/{filename_2}', json.dumps(data_2).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        f'some_path/{filename_3}', json.dumps(data_3).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    # Process tasks for different places

    _sql_add_tasks(
        pg_cursor,
        table_name,
        [
            _generate_task(
                task_id=uuid_place_1,
                place_id=place_id_1,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename_1}',
            ),
            _generate_task(
                task_id=uuid_place_2,
                place_id=place_id_2,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename_2}',
            ),
        ],
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )
    assert handle_task_finished.has_calls

    assert _count_processed(pg_cursor, table_name) == 2

    stq_calls = _get_all_stq_calls(sender_stq)
    assert len(stq_calls) == 2

    stq_data = [
        _generate_data_from_stq_task(i, mds_s3_storage) for i in stq_calls
    ]
    expected_data = [
        _generate_expected_data(
            task_id=uuid_place_1,
            place_id=place_id_1,
            s3_path=s3_path_tmpl.format(place_id_1),
            expected_data=data_1,
        ),
        _generate_expected_data(
            task_id=uuid_place_2,
            place_id=place_id_2,
            s3_path=s3_path_tmpl.format(place_id_2),
            expected_data=data_2,
        ),
    ]
    assert _sorted_by_id(stq_data) == _sorted_by_id(expected_data)

    # Process tasks for the same place (should overwrite data)

    _sql_add_tasks(
        pg_cursor,
        table_name,
        [
            _generate_task(
                task_id=uuid_place_1_overwrite,
                place_id=place_id_1,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename_3}',
            ),
        ],
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )
    assert handle_task_finished.has_calls

    assert _count_processed(pg_cursor, table_name) == 3

    stq_calls = _get_all_stq_calls(sender_stq)
    assert len(stq_calls) == 1

    stq_data = [
        _generate_data_from_stq_task(i, mds_s3_storage) for i in stq_calls
    ]
    expected_data = [
        _generate_expected_data(
            task_id=uuid_place_1_overwrite,
            place_id=place_id_1,
            s3_path=s3_path_tmpl.format(place_id_1),
            expected_data=data_3,
        ),
    ]
    assert _sorted_by_id(stq_data) == _sorted_by_id(expected_data)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'table_name, filename_tmpl, s3_path_tmpl, periodic_name, stq_name',
    [
        pytest.param(
            'price_tasks',
            'test_prices{}.json',
            'prices/prices_{}.json',
            'price-task-result-sender',
            'eats_nomenclature_update_prices',
            id='price',
        ),
        pytest.param(
            'stock_tasks',
            'test_stocks{}.json',
            'stocks/stocks_{}.json',
            'stock-task-result-sender',
            STQ_STOCKS_NAME,
            id='stock',
        ),
        pytest.param(
            'availability_tasks',
            'test_availability{}.json',
            'availability/availability_{}.json',
            'availability-task-result-sender',
            'eats_nomenclature_update_availability',
            id='availability',
        ),
    ],
)
async def test_merge_last_status(
        taxi_eats_nomenclature_collector,
        load_json,
        testpoint,
        pg_cursor,
        mds_s3_storage,
        sql_get_place_tasks_last_status,
        sql_get_place_tasks_last_status_history,
        mocked_time,
        to_utc_datetime,
        # parametrize params
        table_name,
        filename_tmpl,
        s3_path_tmpl,
        periodic_name,
        stq_name,
):
    place_id = '1'
    task_type = table_name.split('_')[0]
    uuid_task_processed_1 = 'uuid_3'
    uuid_task_failed_1 = 'uuid_4'
    uuid_task_failed_2 = 'uuid_5'
    uuid_task_processed_2 = 'uuid_6'
    filename = filename_tmpl.format(place_id)

    # pylint: disable=unused-variable
    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    async def update_data(data, uuid):
        mds_s3_storage.put_object(
            f'some_path/{filename}', json.dumps(data).encode('utf-8'),
        )
        _sql_add_tasks(
            pg_cursor,
            table_name,
            [
                _generate_task(
                    task_id=uuid,
                    place_id=place_id,
                    file_path='https://eda-integration.s3.mdst.yandex.net/'
                    + f'some_path/{filename}',
                ),
            ],
        )
        await taxi_eats_nomenclature_collector.run_periodic_task(
            f'eats-nomenclature-collector_{periodic_name}',
        )

    # insert default status to table
    old_status_or_text_changed_at = '2020-01-01T00:45:00+00:00'
    pg_cursor.execute(
        f"""
        insert into eats_nomenclature_collector.place_tasks_last_status(
            place_id, task_type, status, status_or_text_changed_at
        ) values (
            {place_id},
            '{task_type}',
            'processed',
            '{old_status_or_text_changed_at}'
        )
        """,
    )

    # leave processed status
    default_data = load_json(filename)
    await update_data(default_data, uuid_task_processed_1)

    assert sql_get_place_tasks_last_status(pg_cursor, place_id, task_type) == {
        'status': 'processed',
        'task_error': None,
        'task_warnings': None,
        'status_or_text_changed_at': to_utc_datetime(
            old_status_or_text_changed_at,
        ),
    }
    # nothing will be inserted into place_tasks_last_status_history,
    # as place_tasks_last_status row didn't change
    # pylint: disable=invalid-name
    expected_place_tasks_last_status_history = []
    assert (
        sql_get_place_tasks_last_status_history(pg_cursor, place_id, task_type)
        == expected_place_tasks_last_status_history
    )

    # processed to failed status
    data_failed_1 = copy.deepcopy(default_data)
    if task_type == 'price':
        data_failed_1['items'][0]['price'] = '-10'
        error_message = 'Has negative prices'
    elif task_type == 'stock':
        data_failed_1.pop('items', None)
        error_message = 'No stocks'
    else:
        data_failed_1.pop('items', None)
        error_message = 'No availability'

    new_mock_now = MOCK_NOW + dt.timedelta(minutes=5)
    mocked_time.set(new_mock_now)
    await update_data(data_failed_1, uuid_task_failed_1)

    place_task_last_status = {
        'status': 'failed',
        'task_error': error_message,
        'task_warnings': None,
        'status_or_text_changed_at': new_mock_now,
    }
    expected_place_tasks_last_status_history.append(place_task_last_status)
    assert (
        sql_get_place_tasks_last_status(pg_cursor, place_id, task_type)
        == place_task_last_status
    )
    assert (
        sql_get_place_tasks_last_status_history(pg_cursor, place_id, task_type)
        == expected_place_tasks_last_status_history
    )

    # another error message
    data_failed_2 = copy.deepcopy(default_data)
    if task_type == 'price':
        for item in data_failed_2['items']:
            item['price'] = '0'
        error_message = 'All prices are zero'
    elif task_type == 'stock':
        for item in data_failed_2['items']:
            item['stocks'] = '0'
        error_message = 'All stocks are zero'
    else:
        for item in data_failed_2['items']:
            item['available'] = False
        error_message = 'All availability false'

    new_mock_now += dt.timedelta(minutes=5)
    mocked_time.set(new_mock_now)
    await update_data(data_failed_2, uuid_task_failed_2)

    place_task_last_status = {
        'status': 'failed',
        'task_error': error_message,
        'task_warnings': None,
        'status_or_text_changed_at': new_mock_now,
    }
    expected_place_tasks_last_status_history.append(place_task_last_status)
    assert (
        sql_get_place_tasks_last_status(pg_cursor, place_id, task_type)
        == place_task_last_status
    )
    assert (
        sql_get_place_tasks_last_status_history(pg_cursor, place_id, task_type)
        == expected_place_tasks_last_status_history
    )

    # change to processed status
    new_mock_now += dt.timedelta(minutes=5)
    mocked_time.set(new_mock_now)
    await update_data(default_data, uuid_task_processed_2)

    place_task_last_status = {
        'status': 'processed',
        'task_error': None,
        'task_warnings': None,
        'status_or_text_changed_at': new_mock_now,
    }
    assert (
        sql_get_place_tasks_last_status(pg_cursor, place_id, task_type)
        == place_task_last_status
    )
    expected_place_tasks_last_status_history.append(place_task_last_status)
    assert (
        sql_get_place_tasks_last_status_history(pg_cursor, place_id, task_type)
        == expected_place_tasks_last_status_history
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    """
    table_name,
    filename_tmpl,
    s3_path_tmpl,
    periodic_name,
    stq_name,
    config_name
    """,
    [
        (
            'price_tasks',
            'test_prices{}.json',
            'prices/prices_{}.json',
            'price-task-result-sender',
            'eats_nomenclature_update_prices',
            'EATS_NOMENCLATURE_COLLECTOR_'
            + 'PRICE_TASK_RESULT_SENDER_SETTINGS',
        ),
        (
            'stock_tasks',
            'test_stocks{}.json',
            'stocks/stocks_{}.json',
            'stock-task-result-sender',
            STQ_STOCKS_NAME,
            'EATS_NOMENCLATURE_COLLECTOR_'
            + 'STOCK_TASK_RESULT_SENDER_SETTINGS',
        ),
        (
            'availability_tasks',
            'test_availability{}.json',
            'availability/availability_{}.json',
            'availability-task-result-sender',
            'eats_nomenclature_update_availability',
            'EATS_NOMENCLATURE_COLLECTOR_'
            + 'AVAILABILITY_TASK_RESULT_SENDER_SETTINGS',
        ),
    ],
)
async def test_processing_started_at(
        taxi_eats_nomenclature_collector,
        load_json,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        taxi_config,
        sql_get_place_tasks_last_status,
        to_utc_datetime,
        # parametrize params
        table_name,
        filename_tmpl,
        s3_path_tmpl,
        periodic_name,
        stq_name,
        config_name,
):
    processing_timeout_threshold = dt.timedelta(seconds=10)

    update_config = taxi_config.get(config_name)
    update_config.update(
        {
            'processing_timeout_in_sec': (
                processing_timeout_threshold / dt.timedelta(seconds=1)
            ),
        },
    )
    taxi_config.set(**{config_name: update_config})

    place_id_1 = '1'
    place_id_2 = '2'
    place_id_3 = '3'

    uuid_not_processed = 'uuid_3'
    uuid_timed_out = 'uuid_4'
    uuid_in_progress = 'uuid_5'

    sender_stq = getattr(stq, stq_name)

    filename_1 = filename_tmpl.format(place_id_1)
    filename_2 = filename_tmpl.format(place_id_2)
    filename_3 = filename_tmpl.format(place_id_3)

    data_1 = load_json(filename_1)
    data_2 = load_json(filename_2)
    data_3 = load_json(filename_3)

    mds_s3_storage.put_object(
        f'some_path/{filename_1}', json.dumps(data_1).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        f'some_path/{filename_2}', json.dumps(data_2).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        f'some_path/{filename_3}', json.dumps(data_3).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    _sql_add_tasks(
        pg_cursor,
        table_name,
        [
            _generate_task(
                task_id=uuid_not_processed,
                place_id=place_id_1,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename_1}',
                processing_started_at=None,
            ),
            _generate_task(
                task_id=uuid_timed_out,
                place_id=place_id_2,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename_2}',
                processing_started_at=MOCK_NOW
                - processing_timeout_threshold * 2,
            ),
            _generate_task(
                task_id=uuid_in_progress,
                place_id=place_id_3,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename_3}',
                processing_started_at=MOCK_NOW
                - processing_timeout_threshold / 2,
            ),
        ],
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )
    assert handle_task_finished.has_calls

    assert _count_processed(pg_cursor, table_name) == 2

    stq_calls = _get_all_stq_calls(sender_stq)
    assert len(stq_calls) == 2

    stq_data = [
        _generate_data_from_stq_task(i, mds_s3_storage) for i in stq_calls
    ]
    expected_data = [
        _generate_expected_data(
            task_id=uuid_not_processed,
            place_id=place_id_1,
            s3_path=s3_path_tmpl.format(place_id_1),
            expected_data=data_1,
        ),
        _generate_expected_data(
            task_id=uuid_timed_out,
            place_id=place_id_2,
            s3_path=s3_path_tmpl.format(place_id_2),
            expected_data=data_2,
        ),
    ]
    assert _sorted_by_id(stq_data) == _sorted_by_id(expected_data)

    task_statuses = _sql_get_task_status(
        pg_cursor,
        table_name,
        [uuid_not_processed, uuid_timed_out, uuid_in_progress],
    )
    assert task_statuses[uuid_not_processed]['status'] == 'processed'
    assert not task_statuses[uuid_not_processed]['processing_started_at']
    assert task_statuses[uuid_timed_out]['status'] == 'processed'
    assert not task_statuses[uuid_timed_out]['processing_started_at']
    assert task_statuses[uuid_in_progress]['status'] == 'finished'
    assert task_statuses[uuid_in_progress]['processing_started_at']

    for place_id in [1, 2]:
        task_type = table_name.split('_')[0]
        current_place_tasks_last_status = sql_get_place_tasks_last_status(
            pg_cursor, place_id, task_type,
        )
        expected_last_status = {
            'status': 'processed',
            'task_error': None,
            'task_warnings': None,
            'status_or_text_changed_at': to_utc_datetime(MOCK_NOW),
        }
        assert current_place_tasks_last_status == expected_last_status


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_VALIDATION={
        '1': {
            'zero_prices_limit_in_percent': 50,
            'zero_stocks_limit_in_percent': 50,
            'unavailable_products_limit_in_percent': 50,
        },
    },
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    """
    table_name,
    filename_tmpl,
    s3_path_tmpl,
    periodic_name,
    stq_name
    """,
    [
        (
            'price_tasks',
            'test_prices{}.json',
            'prices/prices_{}.json',
            'price-task-result-sender',
            'eats_nomenclature_update_prices',
        ),
        (
            'stock_tasks',
            'test_stocks{}.json',
            'stocks/stocks_{}.json',
            'stock-task-result-sender',
            STQ_STOCKS_NAME,
        ),
        (
            'availability_tasks',
            'test_availability{}.json',
            'availability/availability_{}.json',
            'availability-task-result-sender',
            'eats_nomenclature_update_availability',
        ),
    ],
)
async def test_parsing_errors(
        taxi_eats_nomenclature_collector,
        load_json,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        sql_get_place_tasks_last_status,
        # parametrize params
        table_name,
        filename_tmpl,
        s3_path_tmpl,
        periodic_name,
        stq_name,
):
    place_id_1 = '1'
    place_id_2 = '2'
    place_id_3 = '3'

    uuid_no_items = 'uuid_3'
    uuid_all_values_zero = 'uuid_4'
    uuid_negative_values = 'uuid_5'
    task_uuids = [uuid_no_items, uuid_all_values_zero]
    if periodic_name != 'stock-task-result-sender':
        task_uuids.append(uuid_negative_values)

    sender_stq = getattr(stq, stq_name)

    filename_1 = filename_tmpl.format(place_id_1)
    filename_2 = filename_tmpl.format(place_id_2)
    if periodic_name != 'stock-task-result-sender':
        filename_3 = filename_tmpl.format(place_id_3)

    data_no_items = load_json(filename_1)
    data_no_items['items'] = []

    data_most_values_zero = load_json(filename_2)
    for item in data_most_values_zero['items']:
        if table_name == 'price_tasks':
            item['price'] = '0'
        if table_name == 'stock_tasks':
            item['stocks'] = '0'
        if table_name == 'availability_tasks':
            item['available'] = False

    if periodic_name != 'stock-task-result-sender':
        data_negative_values = load_json(filename_3)

    if table_name == 'price_tasks':
        data_negative_values['items'][0]['price'] = '-10'
        # make one price non zero, so 66% of values are zeros
        data_most_values_zero['items'][0]['price'] = '10'

    if table_name == 'stock_tasks':
        # make one stock non zero, so 66% of values are zeros
        data_most_values_zero['items'][0]['stocks'] = '10'

    if table_name == 'availability_tasks':
        # there's no negative values in availability
        # so just fail task for tests
        data_negative_values['items'] = []
        # make one product available, so 66% of products are unavailable
        data_most_values_zero['items'][0]['available'] = True

    mds_s3_storage.put_object(
        f'some_path/{filename_1}', json.dumps(data_no_items).encode('utf-8'),
    )
    mds_s3_storage.put_object(
        f'some_path/{filename_2}',
        json.dumps(data_most_values_zero).encode('utf-8'),
    )
    if periodic_name != 'stock-task-result-sender':
        mds_s3_storage.put_object(
            f'some_path/{filename_3}',
            json.dumps(data_negative_values).encode('utf-8'),
        )

    # pylint: disable=unused-variable
    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    tasks = [
        _generate_task(
            task_id=uuid_no_items,
            place_id=place_id_1,
            file_path='https://eda-integration.s3.mdst.yandex.net/'
            + f'some_path/{filename_1}',
        ),
        _generate_task(
            task_id=uuid_all_values_zero,
            place_id=place_id_2,
            file_path='https://eda-integration.s3.mdst.yandex.net/'
            + f'some_path/{filename_2}',
        ),
    ]
    if periodic_name != 'stock-task-result-sender':
        tasks.append(
            _generate_task(
                task_id=uuid_negative_values,
                place_id=place_id_3,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename_3}',
            ),
        )

    _sql_add_tasks(pg_cursor, table_name, tasks)

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )
    assert handle_task_finished.has_calls

    assert sender_stq.times_called == 0

    task_statuses = _sql_get_task_status(pg_cursor, table_name, task_uuids)
    for task_uuid in task_uuids:
        assert task_statuses[task_uuid]['status'] == 'failed'

    if table_name == 'price_tasks':
        assert task_statuses[uuid_no_items]['reason'] == 'No prices'
        assert (
            task_statuses[uuid_all_values_zero]['reason']
            == 'All prices are zero'
        )
        assert (
            task_statuses[uuid_negative_values]['reason']
            == 'Has negative prices'
        )
        place_to_errors_messages = {
            place_id_1: 'No prices',
            place_id_2: 'All prices are zero',
            place_id_3: 'Has negative prices',
        }

        for place_id in place_to_errors_messages:
            current_place_tasks_last_status = sql_get_place_tasks_last_status(
                pg_cursor, place_id, 'price',
            )
            expected_last_status = {
                'status': 'failed',
                'task_error': place_to_errors_messages[place_id],
                'task_warnings': None,
                'status_or_text_changed_at': MOCK_NOW,
            }
            assert current_place_tasks_last_status == expected_last_status

    if table_name == 'stock_tasks':
        assert task_statuses[uuid_no_items]['reason'] == 'No stocks'
        assert (
            task_statuses[uuid_all_values_zero]['reason']
            == 'All stocks are zero'
        )
        place_to_errors_messages = {
            place_id_1: 'No stocks',
            place_id_2: 'All stocks are zero',
        }
        for place_id in place_to_errors_messages:
            current_place_tasks_last_status = sql_get_place_tasks_last_status(
                pg_cursor, place_id, 'stock',
            )
            expected_last_status = {
                'status': 'failed',
                'task_error': place_to_errors_messages[place_id],
                'task_warnings': None,
                'status_or_text_changed_at': MOCK_NOW,
            }
            assert current_place_tasks_last_status == expected_last_status

    if table_name == 'availability_tasks':
        assert task_statuses[uuid_no_items]['reason'] == 'No availability'
        assert (
            task_statuses[uuid_all_values_zero]['reason']
            == 'All availability false'
        )
        place_to_errors_messages = {
            place_id_1: 'No availability',
            place_id_2: 'All availability false',
        }
        for place_id in place_to_errors_messages:
            current_place_tasks_last_status = sql_get_place_tasks_last_status(
                pg_cursor, place_id, 'availability',
            )
            expected_last_status = {
                'status': 'failed',
                'task_error': place_to_errors_messages[place_id],
                'task_warnings': None,
                'status_or_text_changed_at': MOCK_NOW,
            }
            assert current_place_tasks_last_status == expected_last_status


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    """
    table_name,
    filename_tmpl,
    s3_path_tmpl,
    periodic_name,
    stq_name
    """,
    [
        (
            'stock_tasks',
            'test_stocks{}.json',
            'stocks/stocks_{}.json',
            'stock-task-result-sender',
            STQ_STOCKS_NAME,
        ),
    ],
)
async def test_parsing_negative_stocks(
        taxi_eats_nomenclature_collector,
        load_json,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        # parametrize params
        table_name,
        filename_tmpl,
        s3_path_tmpl,
        periodic_name,
        stq_name,
):
    place_id_3 = '3'
    uuid_negative_values = 'uuid_5'
    task_uuids = [uuid_negative_values]

    sender_stq = getattr(stq, stq_name)

    filename_3 = filename_tmpl.format(place_id_3)

    data_negative_values = load_json(filename_3)
    data_negative_values['items'][0]['stocks'] = '-10'
    mds_s3_storage.put_object(
        f'some_path/{filename_3}',
        json.dumps(data_negative_values).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    tasks = [
        _generate_task(
            task_id=uuid_negative_values,
            place_id=place_id_3,
            file_path='https://eda-integration.s3.mdst.yandex.net/'
            + f'some_path/{filename_3}',
        ),
    ]

    _sql_add_tasks(pg_cursor, table_name, tasks)

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )
    assert handle_task_finished.has_calls

    stq_calls = _get_all_stq_calls(sender_stq)
    assert len(stq_calls) == 1

    stq_data = [
        _generate_data_from_stq_task(i, mds_s3_storage) for i in stq_calls
    ]

    # check that negative stock was converted to 0
    assert _sorted_by_id(stq_data)[0]['s3_data']['items'][0]['stocks'] == '0'

    task_statuses = _sql_get_task_status(pg_cursor, table_name, task_uuids)
    for task_uuid in task_uuids:
        assert task_statuses[task_uuid]['status'] == 'processed'


@pytest.mark.now(MOCK_NOW.isoformat())
async def test_null_stocks(
        taxi_eats_nomenclature_collector,
        load_json,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
):
    table_name = 'stock_tasks'
    s3_path_tmpl = 'stocks/stocks_{}.json'
    periodic_name = 'stock-task-result-sender'
    stq_name = STQ_STOCKS_NAME
    place_id = '1'
    uuid_place = 'uuid_3'

    sender_stq = getattr(stq, stq_name)

    filename = 'test_null_stocks.json'
    data = load_json(filename)

    mds_s3_storage.put_object(
        f'some_path/{filename}', json.dumps(data).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    _sql_add_tasks(
        pg_cursor,
        table_name,
        [
            _generate_task(
                task_id=uuid_place,
                place_id=place_id,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename}',
            ),
        ],
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )
    assert handle_task_finished.has_calls

    assert _count_processed(pg_cursor, table_name) == 1

    stq_calls = _get_all_stq_calls(sender_stq)
    assert len(stq_calls) == 1

    stq_data = [
        _generate_data_from_stq_task(i, mds_s3_storage) for i in stq_calls
    ]
    expected_data = [
        _generate_expected_data(
            task_id=uuid_place,
            place_id=place_id,
            s3_path=s3_path_tmpl.format(place_id),
            expected_data=data,
        ),
    ]
    assert _sorted_by_id(stq_data) == _sorted_by_id(expected_data)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'too_big_stocks_limit, should_fail',
    [
        pytest.param(0, True, id='0'),
        pytest.param(10, True, id='10'),
        pytest.param(100, False, id='100-no-fail'),
    ],
)
async def test_too_big_stocks(
        taxi_eats_nomenclature_collector,
        load_json,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        sql_get_place_tasks_last_status,
        update_taxi_config,
        # parametrize params
        too_big_stocks_limit,
        should_fail,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_COLLECTOR_VALIDATION',
        {'1': {'too_big_stocks_limit_in_percent': too_big_stocks_limit}},
    )

    table_name = 'stock_tasks'
    periodic_name = 'stock-task-result-sender'
    stq_name = STQ_STOCKS_NAME
    place_id = '1'
    uuid_place = 'uuid_3'
    s3_path_tmpl = 'stocks/stocks_{}.json'

    sender_stq = getattr(stq, stq_name)

    filename = 'test_too_big_stocks.json'
    data = load_json(filename)

    mds_s3_storage.put_object(
        f'some_path/{filename}', json.dumps(data).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    _sql_add_tasks(
        pg_cursor,
        table_name,
        [
            _generate_task(
                task_id=uuid_place,
                place_id=place_id,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename}',
            ),
        ],
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )

    assert handle_task_finished.has_calls

    too_big_stocks_reason = 'Stock value is too big'
    task_statuses = _sql_get_task_status(pg_cursor, table_name, [uuid_place])
    if should_fail:
        assert task_statuses[uuid_place]['status'] == 'failed'
        assert task_statuses[uuid_place]['reason'] == too_big_stocks_reason
        assert not sender_stq.has_calls
    else:
        assert task_statuses[uuid_place]['status'] == 'processed'
        stq_calls = _get_all_stq_calls(sender_stq)
        assert len(stq_calls) == 1
        stq_data = [
            _generate_data_from_stq_task(i, mds_s3_storage) for i in stq_calls
        ]
        expected_data = [
            _generate_expected_data(
                task_id=uuid_place,
                place_id=place_id,
                s3_path=s3_path_tmpl.format(place_id),
                expected_data=data,
            ),
        ]
        assert _sorted_by_id(stq_data) == _sorted_by_id(expected_data)

    current_place_tasks_last_status = sql_get_place_tasks_last_status(
        pg_cursor, place_id, 'stock',
    )
    if should_fail:
        expected_last_status = {
            'status': 'failed',
            'task_error': too_big_stocks_reason,
            'task_warnings': None,
            'status_or_text_changed_at': MOCK_NOW,
        }
    else:
        expected_last_status = {
            'status': 'processed',
            'task_error': None,
            'task_warnings': None,
            'status_or_text_changed_at': MOCK_NOW,
        }
    assert current_place_tasks_last_status == expected_last_status


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize('place_id', ['1', '2'])
async def test_full_prices(
        taxi_eats_nomenclature_collector,
        load_json,
        testpoint,
        pg_cursor,
        stq,
        mds_s3_storage,
        place_id,
):
    table_name = 'price_tasks'
    filename_tmpl = 'test_full_prices{}.json'
    s3_path_tmpl = 'prices/prices_{}.json'
    periodic_name = 'price-task-result-sender'
    stq_name = 'eats_nomenclature_update_prices'
    uuid_place = 'uuid_3'

    sender_stq = getattr(stq, stq_name)
    filename = filename_tmpl.format(place_id)
    data = load_json(filename)
    mds_s3_storage.put_object(
        f'some_path/{filename}', json.dumps(data).encode('utf-8'),
    )

    # pylint: disable=unused-variable
    @testpoint(f'eats_nomenclature_collector::{periodic_name}')
    def handle_task_finished(arg):
        pass

    # Process task

    _sql_add_tasks(
        pg_cursor,
        table_name,
        [
            _generate_task(
                task_id=uuid_place,
                place_id=place_id,
                file_path='https://eda-integration.s3.mdst.yandex.net/'
                + f'some_path/{filename}',
            ),
        ],
    )

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{periodic_name}',
    )
    assert handle_task_finished.has_calls

    # negative full price
    if place_id == '2':
        task_statuses = _sql_get_task_status(
            pg_cursor, table_name, [uuid_place],
        )
        assert task_statuses[uuid_place]['status'] == 'failed'
        assert task_statuses[uuid_place]['reason'] == 'Has negative prices'
        return

    # positive full price
    stq_data = [
        _generate_data_from_stq_task(sender_stq.next_call(), mds_s3_storage),
    ]
    expected_data = [
        _generate_expected_data(
            task_id=uuid_place,
            place_id=place_id,
            s3_path=s3_path_tmpl.format(place_id),
            expected_data=data,
        ),
    ]
    assert _sorted_by_id(stq_data) == _sorted_by_id(expected_data)


def _generate_data_from_stq_task(task, mds_s3_storage):
    return {
        'id': task['id'],
        'place_id': task['kwargs']['place_id'],
        's3_path': task['kwargs']['s3_path'],
        'file_datetime': task['kwargs']['file_datetime'],
        's3_data': json.loads(
            mds_s3_storage.storage[task['kwargs']['s3_path']].data,
        ),
    }


@pytest.mark.parametrize(
    'periodic_name',
    [
        pytest.param('price-task-result-sender', id='price'),
        pytest.param('stock-task-result-sender', id='stock'),
        pytest.param('availability-task-result-sender', id='availability'),
    ],
)
async def test_periodic_metrics(verify_periodic_metrics, periodic_name):
    await verify_periodic_metrics(
        f'eats-nomenclature-collector_{periodic_name}', is_distlock=False,
    )


def _round_expected_data(src_stocks):
    rounded_stocks = copy.deepcopy(src_stocks)
    for item_stock in rounded_stocks['items']:
        if 'stocks' not in item_stock:
            continue
        if (
                item_stock['stocks'] is None
                or float(item_stock['stocks']) >= STOCK_MAX_VALUE
        ):
            del item_stock['stocks']
        else:
            item_stock['stocks'] = str(int(float(item_stock['stocks'])))
    return rounded_stocks


def _generate_expected_data(task_id, place_id, s3_path, expected_data):
    return {
        'id': task_id,
        'place_id': place_id,
        's3_path': s3_path,
        'file_datetime': MOCK_NOW.isoformat(),
        's3_data': (_round_expected_data(expected_data)),
    }


def _get_all_stq_calls(stq):
    return [stq.next_call() for _ in range(stq.times_called)]


def _sorted_by_id(data):
    return sorted(data, key=lambda i: i['id'])


def _count_processed(pg_cursor, table_name):
    pg_cursor.execute(
        f'select * from eats_nomenclature_collector.{table_name}',
    )
    rows = pg_cursor.fetchall()
    return sum(row['status'] == 'processed' for row in rows)


def _generate_task(
        task_id, place_id, file_path, status=None, processing_started_at=None,
):
    return {
        'id': task_id,
        'place_id': place_id,
        'file_path': file_path,
        'status': status or 'finished',
        'processing_started_at': processing_started_at,
    }


def _sql_add_tasks(pg_cursor, table_name, tasks):
    for i in tasks:
        pg_cursor.execute(
            f"""
            insert into eats_nomenclature_collector.{table_name} (
                id,
                place_id,
                file_path,
                status,
                processing_started_at
            )
            values(
                %(id)s,
                %(place_id)s,
                %(file_path)s,
                %(status)s,
                %(processing_started_at)s
            )
            """,
            i,
        )


def _sql_get_task_status(pg_cursor, table_name, ids):
    pg_cursor.execute(
        f"""
        select id, status, reason, processing_started_at
        from eats_nomenclature_collector.{table_name}
        where id = any(%s)
        """,
        (ids,),
    )

    statuses = {}
    for i in pg_cursor.fetchall():
        statuses[i['id']] = {
            'status': i['status'],
            'reason': i['reason'],
            'processing_started_at': i['processing_started_at'],
        }
    return statuses
