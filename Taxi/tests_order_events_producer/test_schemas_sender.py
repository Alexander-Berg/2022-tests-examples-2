import json
import socket


def check_schema(schema):
    assert 'mappers' in schema
    assert 'filters' in schema
    assert 'customs' in schema
    assert 'sources' in schema
    assert 'sinks' in schema

    assert schema['mappers']
    assert len(schema['mappers']) == 41

    assert schema['filters']
    assert len(schema['filters']) == 7

    assert not schema['customs']
    assert schema['sources']
    assert schema['sinks']

    assert len(schema['sinks']) == 23

    for sink in schema['sinks']:
        if sink['name'] == 'tags_sink':
            assert sink['argument_schemas'] == [
                {
                    'default_value': 50.0,
                    'description': '',
                    'is_required': False,
                    'name': 'bulk_duration_of_data_collection_ms',
                    'type': 'number',
                },
                {
                    'default_value': 10.0,
                    'description': '',
                    'is_required': False,
                    'name': 'bulk_size_threshold',
                    'type': 'number',
                },
                {
                    'default_value': 10000.0,
                    'description': '',
                    'is_required': False,
                    'name': 'input_queue_size',
                    'type': 'number',
                },
                {
                    'default_value': 1000.0,
                    'description': '',
                    'is_required': False,
                    'name': 'output_queue_size',
                    'type': 'number',
                },
                {
                    'default_value': 3.0,
                    'description': '',
                    'is_required': False,
                    'name': 'number_of_threads',
                    'type': 'number',
                },
                {
                    'description': 'Имя поставщика тегов из админки',
                    'is_required': True,
                    'name': 'provider_id',
                    'type': 'string',
                },
            ]

        if sink['name'] == 'atlas_drivers_positions_clickhouse_mdb_sink':
            assert sink['argument_schemas'] == [
                {
                    'default_value': 50.0,
                    'description': '',
                    'is_required': False,
                    'name': 'bulk_duration_of_data_collection_ms',
                    'type': 'number',
                },
                {
                    'default_value': 10.0,
                    'description': '',
                    'is_required': False,
                    'name': 'bulk_size_threshold',
                    'type': 'number',
                },
                {
                    'default_value': 10000.0,
                    'description': '',
                    'is_required': False,
                    'name': 'input_queue_size',
                    'type': 'number',
                },
                {
                    'default_value': 1000.0,
                    'description': '',
                    'is_required': False,
                    'name': 'output_queue_size',
                    'type': 'number',
                },
                {
                    'default_value': 3.0,
                    'description': '',
                    'is_required': False,
                    'name': 'number_of_threads',
                    'type': 'number',
                },
                {
                    'description': '',
                    'is_required': False,
                    'name': 'timeout_ms',
                    'type': 'number',
                },
                {
                    'description': '',
                    'is_required': False,
                    'name': 'retries',
                    'type': 'number',
                },
            ]


async def test_schemas_sender(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        make_order_event,
        order_events_gen,
        taxi_config,
        taxi_eventus_orchestrator_mock,
):
    await taxi_order_events_producer.run_task('schema-send-task')

    assert len(taxi_eventus_orchestrator_mock.put_pipeline_schema_calls) == 1

    req = taxi_eventus_orchestrator_mock.put_pipeline_schema_calls[0]

    assert req.query['instance_name'] == 'order-events-producer'

    req_data = json.loads(req.get_data().decode('utf-8'))
    check_schema(req_data['schema'])
    assert req_data['hostname'] == socket.gethostname()
    version_numbers = list(
        map(int, req_data['build_version'].split('.', maxsplit=2)),
    )
    assert version_numbers[0] == 0
    assert version_numbers[1] == 0
    assert version_numbers[2] > 90
