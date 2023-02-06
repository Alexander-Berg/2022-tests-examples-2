import pytest

from taxi_driver_metrics.common.models._dist_tasks_params import get_param
from taxi_driver_metrics.stq.workers._sql_query import _MASTER_NAME
from taxi_driver_metrics.stq.workers._sql_query import (
    QueryProcessingMasterWorker,
)

DRIVER_ID = '5b05621ee6c22ea2654849c9'
RIDER_ID = '5b05621ee6c22ea2654849c9'
TST_ZONE = 'burgund'
CH_DATA = [
    {
        'driver_id': DRIVER_ID,
        'rider_id': RIDER_ID,
        'event_type': 'order',
        'name': 'complete',
        'order_id': 'dlsjfslkfj',
        'zone': TST_ZONE,
        'event_timestamp': 1594024649,
        'eventus_recv_timestamp': 1594024659,
    },
    {
        'driver_id': DRIVER_ID,
        'rider_id': RIDER_ID,
        'event_type': 'order',
        'name': 'seen_timeout',
        'order_id': 'dlsjfslkfj',
        'zone': TST_ZONE,
        'event_timestamp': 1594024849,
        'eventus_recv_timestamp': 1594024859,
    },
]


async def _get_cursor_data(mongo, version):
    cursor = await get_param(
        mongo, f'query_processing_settings_{version}', 'cursor_value',
    )

    cursor_type = await get_param(
        mongo, f'query_processing_settings_{version}', 'cursor_type',
    )
    return cursor, cursor_type


@pytest.mark.now('2020-07-16T12:00:00Z')
@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_QUERY_PROCESSING_SETTINGS={
        'chunk_size': 10,
        'stq_task_delay_ms': 20,
        'cursor_limit_ms': 1000,
        'cursor_limit_count': 1000,
        'master_task_interval_ms': 400,
        'tasks_take_delay_sec': 2000,
        'settings_context': {'order_metrics': 'db1.order_metrics'},
    },
)
async def test_run_processing_base(
        stq3_context,
        mongo,
        stq,
        mock_clickhouse_host,
        response_mock,
        tags_service_mock,
):
    # pylint: disable=protected-access
    def _build_meta(data):
        return {
            'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
            'meta': [],
            'data': data,
            'rows': 1,
        }

    def upload_check(*args, **kwargs):
        request = args[0]
        data = request.json
        assert data
        assert data['tags'] == [
            {'match': {'id': '5b05621ee6c22ea2654849c9'}, 'name': 'seen_5'},
        ]

    tags_service_mock(upload_check=upload_check)

    def response(*args, data=None, **kwargs):
        result = []

        if not data:
            return response_mock(json=_build_meta([]))

        if 'MAX(event_timestamp)' in data:
            result = [{'event_timestamp': 1594024649}]

        if '1594024649' in data:
            result = CH_DATA

        return response_mock(json=_build_meta(result))

    def empty_response(*args, **kwargs):
        return response_mock(json=_build_meta([]))

    def check_upper_limit(*args, data=None, **kwargs):
        assert (
            data == 'SELECT order_id, event_timestamp, unique_driver_id, '
            'user_phone_id, user_id, park_driver_profile_id, tariff_zone '
            'FROM db1.order_metrics WHERE event_timestamp > 1594024849.0'
            ' AND event_timestamp <= 1594898800.0 '
            'ORDER BY event_timestamp LIMIT 1000 FORMAT JSON'
        )
        return response_mock(json=_build_meta([]))

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(response, host_list[0])

    # Step 1. Init cursor from event in mongo

    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)

    cursor, cursor_type = await _get_cursor_data(mongo, 2)
    cursor_3, cursor_type_3 = await _get_cursor_data(mongo, 3)

    assert cursor == '1594024649'
    # cannot set cursor while initializing
    assert cursor_3 is None
    assert cursor_type == 'period'
    assert cursor_type_3 == 'period'
    # self reschedule
    assert stq.driver_metrics_query_processing.times_called == 1

    # Step 1. Run processing by initted cursor

    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)

    cursor, cursor_type = await _get_cursor_data(mongo, 2)
    cursor_3, cursor_type_3 = await _get_cursor_data(mongo, 3)

    assert cursor == '1594024849'
    assert cursor_type == 'period'
    assert cursor_3 == '1594024859'
    assert cursor_type_3 == 'period'
    # 2 self reschedules + one slave
    assert stq.driver_metrics_query_processing.times_called == 3

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(empty_response(), host_list[0])

    # initted empty data
    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)

    cursor, cursor_type = await _get_cursor_data(mongo, 2)
    cursor_3, cursor_type_3 = await _get_cursor_data(mongo, 3)
    assert cursor == '1594024849'
    assert cursor_type == 'limit'
    assert cursor_3 == '1594024859'
    assert cursor_type_3 == 'limit'

    assert stq.driver_metrics_query_processing.times_called == 4

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(check_upper_limit, host_list[0])
    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)
    # assert inside check_upper_limit mock


@pytest.mark.now('2020-04-16T12:00:00Z')
@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_QUERY_PROCESSING_SETTINGS={
        'chunk_size': 10,
        'stq_task_delay_ms': 20,
        'cursor_limit_ms': 1000,
        'cursor_limit_count': 1000,
        'task_take_delay_sec': 2000,
        'master_task_interval_ms': 400,
        'settings_context': {'order_metrics': 'db1.order_metrics'},
    },
)
async def test_run_processing_delay(
        stq3_context,
        taxi_driver_metrics,
        mongo,
        stq,
        mock_clickhouse_host,
        response_mock,
        tags_service_mock,
):
    # pylint: disable=protected-access
    def _build_meta(data):
        return {
            'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
            'meta': [],
            'data': data,
            'rows': 1,
        }

    def response(*args, data=None, **kwargs):
        result = []

        if not data:
            return response_mock(json=_build_meta([]))

        if 'MAX(event_timestamp)' in data:
            result = [{'event_timestamp': 1594024649}]

        if '0.1' in data:
            result = CH_DATA

        return response_mock(json=_build_meta(result))

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(response, host_list[0])

    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)

    cursor, cursor_type = await _get_cursor_data(mongo, 2)

    assert cursor == '1594024649'
    assert cursor_type == 'period'

    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)

    cursor, cursor_type = await _get_cursor_data(mongo, 2)

    assert cursor == '1594024649'
    assert cursor_type == 'period'


@pytest.mark.now('2020-07-16T12:00:00Z')
@pytest.mark.config(
    DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    DRIVER_METRICS_QUERY_CURSOR_VERSION=3,
    DRIVER_METRICS_QUERY_PROCESSING_SETTINGS={
        'chunk_size': 10,
        'stq_task_delay_ms': 20,
        'cursor_limit_ms': 1000,
        'cursor_limit_count': 1000,
        'master_task_interval_ms': 400,
        'cursor_border_sec': 180,
        'settings_context': {'order_metrics': 'db1.order_metrics'},
    },
)
async def test_run_processing_base_ver3(
        stq3_context,
        mongo,
        stq,
        mock_clickhouse_host,
        response_mock,
        tags_service_mock,
):
    # pylint: disable=protected-access
    def _build_meta(data):
        return {
            'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
            'meta': [],
            'data': data,
            'rows': 1,
        }

    def upload_check(*args, **kwargs):
        request = args[0]
        data = request.json
        assert data
        assert data['tags'] == [
            {'match': {'id': '5b05621ee6c22ea2654849c9'}, 'name': 'seen_5'},
        ]

    tags_service_mock(upload_check=upload_check)

    def response(*args, data=None, **kwargs):
        result = []

        if not data:
            return response_mock(json=_build_meta([]))

        if 'MAX(eventus_recv_timestamp)' in data:
            result = [{'eventus_recv_timestamp': 1594024659}]

        if '1594024659' in data:
            result = CH_DATA

        return response_mock(json=_build_meta(result))

    def empty_response(*args, **kwargs):
        return response_mock(json=_build_meta([]))

    def check_query(*args, data=None, **kwargs):
        assert (
            data == 'SELECT event_id, order_id, event_timestamp, '
            'unique_driver_id, eventus_recv_timestamp, '
            'user_phone_id, user_id, park_driver_profile_id, '
            'tariff_zone, event_key, event_type FROM db1.order_metrics'
            ' WHERE eventus_recv_timestamp > 1594024849.0'
            ' AND event_timestamp > 1594024669.0'
            ' ORDER BY eventus_recv_timestamp LIMIT 1000 FORMAT JSON'
        )
        return response_mock(json=_build_meta([]))

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(response, host_list[0])

    # Step 1. Init cursor from event in mongo

    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)

    cursor, cursor_type = await _get_cursor_data(mongo, 3)

    assert cursor == '1594024659'
    assert cursor_type == 'period'
    # self reschedule
    assert stq.driver_metrics_query_processing.times_called == 1

    # Step 1. Run processing by initted cursor

    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)

    cursor, cursor_type = await _get_cursor_data(mongo, 3)

    assert cursor == '1594024859'
    assert cursor_type == 'period'
    # 2 self reschedules + one slave
    assert stq.driver_metrics_query_processing.times_called == 3

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(empty_response(), host_list[0])

    # initted empty data
    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)

    cursor, cursor_type = await _get_cursor_data(mongo, 3)
    assert cursor == '1594024859'
    assert cursor_type == 'limit'

    assert stq.driver_metrics_query_processing.times_called == 4

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(check_query, host_list[0])
    await QueryProcessingMasterWorker(
        context=stq3_context,
        queue=stq3_context.stq.driver_metrics_query_processing,
    ).do_work(task_id=_MASTER_NAME)
