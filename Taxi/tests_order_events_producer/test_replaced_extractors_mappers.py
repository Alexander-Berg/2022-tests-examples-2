import json
import math
import time

import pytest

from tests_order_events_producer import pipeline_tools


def get_oep_pipelines_config(
        custom_name, add_rms_ops=None, add_clickhouse_ops=None,
):
    switch_options = [
        {
            'arguments': {
                'dst_key': 'event.descriptor',
                'value': '{"name": "cawabanga"}',
                'policy': 'set',
            },
            'filters': [
                {
                    'arguments': {
                        'src': 'event_key',
                        'match_with': 'handle_cancel_by_user',
                    },
                    'operation_name': 'string_equal',
                    'type': 'filter',
                },
            ],
        },
        {
            'arguments': {
                'dst_key': 'event.filtered_out',
                'value': '{}',
                'policy': 'set',
            },
            'filters': [],
        },
    ]

    rms_pipeline = pipeline_tools.get_oe_pipeline_for_orch(
        'rms_sink',
        switch_options,
        pipeline_name='rms-' + custom_name,
        add_ops_before_sink=add_rms_ops,
    )
    ch_pipeline = pipeline_tools.get_oe_pipeline_for_orch(
        'clickhouse_sink',
        switch_options,
        pipeline_name='clickhouse-' + custom_name,
        add_ops_before_sink=add_clickhouse_ops,
    )
    return [rms_pipeline, ch_pipeline]


def _get_extra_data_mapper(fields):
    return {
        'name': 'copy-extra-data-fields',
        'operation_variant': {
            'arguments': {
                'src_keys_mapping': fields,
                'dst_key': ['extra_data'],
            },
            'operation_name': 'copy_fields_to_subobject',
            'type': 'mapper',
        },
    }


def _get_join_strings_mapper(dst_key, src_keys, separator):
    return {
        'name': 'join-strings',
        'operation_variant': {
            'arguments': {
                'dst_key': dst_key,
                'src_keys': src_keys,
                'separator': separator,
            },
            'operation_name': 'join_strings',
            'type': 'mapper',
        },
    }


def _get_strings_filtered_mapper(dst_key, src_key, policy, filter_values):
    return {
        'name': 'str-arr-filtered-mapper',
        'operation_variant': {
            'arguments': {
                'src_key': src_key,
                'dst_key': dst_key,
                'filter_values': filter_values,
                'policy': policy,
            },
            'operation_name': 'strings_array_filtered',
            'type': 'mapper',
        },
    }


@pytest.mark.parametrize(
    'add_operations,expected_field,expected_value',
    [
        (
            [_get_extra_data_mapper(['event_key look_key'])],
            'look_key',
            'handle_cancel_by_user',
        ),
        (
            [_get_extra_data_mapper(['driver_uuid'])],
            'driver_uuid',
            'driveruuid1',
        ),
        ([_get_extra_data_mapper(['uuid'])], 'uuid', 'driveruuid2'),
        (
            [
                _get_join_strings_mapper(
                    'look_key', ['db_id', 'driver_uuid'], '_',
                ),
                _get_extra_data_mapper(['look_key']),
            ],
            'look_key',
            'dbid1_driveruuid1',
        ),
        (
            [
                _get_join_strings_mapper('look_key', ['db_id', 'uuid'], '_'),
                _get_extra_data_mapper(['look_key']),
            ],
            'look_key',
            'dbid1_driveruuid2',
        ),
        (
            [
                _get_strings_filtered_mapper(
                    'look_key',
                    'tags',
                    'accept_only',
                    ['tags_pick1', 'tags_pick2'],
                ),
                _get_extra_data_mapper(['look_key']),
            ],
            'look_key',
            ['tags_pick1', 'tags_pick2'],
        ),
    ],
)
async def test_sink_parameters_fetch(
        taxi_order_events_producer,
        taxi_eventus_orchestrator_mock,
        testpoint,
        taxi_config,
        taxi_rider_metrics_storage_mock,
        make_order_event,
        order_events_gen,
        add_operations,
        expected_field,
        expected_value,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    processed = []

    @testpoint('rms-bulk-sink-sender::rms_sink')
    def events_processed(data):
        if 'events' in data:
            for event in data['events']:
                print('\n\nEvent {}\n\n'.format(event))
                processed.append(event)

    pipelines_config = get_oep_pipelines_config(
        'pipeline-{}'.format(expected_value), add_operations,
    )
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )

    await taxi_order_events_producer.run_task('invalidate-seq_num')

    taxi_rider_metrics_storage_mock.expect_times_called(1)
    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_cancel_by_user',
                        user_id='user-1',
                        db_id='dbid1',
                        driver_uuid='driveruuid1',
                        driver_id='driverclid1_driveruuid2',
                        user_phone_id='oneonethree',
                        destinations_geopoint=[[37.69411325, 55.78685382]],
                        tags=['tags_pick1', 'tags_pick2', 'tags_skipped'],
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    assert response.status_code == 200

    await commit.wait_call()
    await events_processed.wait_call()
    assert processed

    for event in processed:
        assert 'extra_data' in event
        assert expected_field in event['extra_data']
        if isinstance(expected_value, list):
            assert sorted(event['extra_data'][expected_field]) == sorted(
                expected_value,
            )
        else:
            assert event['extra_data'][expected_field] == expected_value


def _get_leave_fields_mapper(fields):
    return {
        'name': 'filter-fields-for-sink',
        'operation_variant': {
            'arguments': {'leave_keys_list': fields},
            'operation_name': 'filter_fields',
            'type': 'mapper',
        },
    }


def _get_rename_fields_mapper(fields):
    return {
        'name': 'copy-fields-with-new-name',
        'operation_variant': {
            'arguments': {'src_keys_mapping': fields},
            'operation_name': 'copy_fields_to_subobject',
            'type': 'mapper',
        },
    }


@pytest.mark.parametrize(
    'add_operations,expected_field,expected_value',
    [
        (
            [
                _get_rename_fields_mapper(['oep_processing_time look_key']),
                _get_leave_fields_mapper(['look_key']),
            ],
            'look_key',
            0.0,
        ),
    ],
)
async def test_sink_parameters_fetch_processing_timepoint(
        taxi_order_events_producer,
        taxi_eventus_orchestrator_mock,
        testpoint,
        taxi_config,
        taxi_rider_metrics_storage_mock,
        make_order_event,
        order_events_gen,
        add_operations,
        expected_field,
        expected_value,
        mocked_time,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    processed = []

    @testpoint('clickhouse-sink-sender::clickhouse_sink')
    def events_processed(data):
        processed.append(data)

    pipelines_config = get_oep_pipelines_config(
        'pipeline-processing-timepoint', add_clickhouse_ops=add_operations,
    )
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )

    await taxi_order_events_producer.run_task('invalidate-seq_num')

    timestamp = mocked_time.now()

    taxi_rider_metrics_storage_mock.expect_times_called(1)
    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_cancel_by_user',
                        user_id='user-1',
                        db_id='dbid1',
                        driver_uuid='driveruuid1',
                        driver_id='driverclid1_driveruuid2',
                        user_phone_id='oneonethree',
                        destinations_geopoint=[[37.69411325, 55.78685382]],
                        tags=['tags_pick1', 'tags_pick2', 'tags_skipped'],
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )

    assert response.status_code == 200

    await commit.wait_call()
    await events_processed.wait_call()

    # NOTE: mktime creates time with current timezone, so, substract tz
    unix_timestamp = (
        time.mktime(timestamp.timetuple())
        + (math.floor(float(timestamp.microsecond) / 1000.0) / 1000.0)
        - time.timezone
    )
    assert processed

    for value in processed:
        assert value == [{'look_key': unix_timestamp}]
