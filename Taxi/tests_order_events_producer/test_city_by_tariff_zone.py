import asyncio
import json
import time

import pytest

_OEP_PIPELINES = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'communal-events'},
        'root': {
            'output': {'sink_name': 'rms_sink'},
            'operations': [
                {
                    'name': 'topic-filter',
                    'operation_variant': {
                        'arguments': {'src': 'topic', 'match_with': 'smth'},
                        'operation_name': 'string_equal',
                        'type': 'filter',
                    },
                },
                {
                    'name': 'add-seq-num',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_seq_num',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'add-proc-timestamp',
                    'operation_variant': {
                        'arguments': {},
                        'operation_name': 'set_proc_timestamp',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'city-by-tariff-zone',
                    'operation_variant': {
                        'arguments': {'src': 'tariff_zone', 'dst': 'city_id'},
                        'operation_name': 'tariff_zone_to_city_name',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'copy-extra-data-fields',
                    'operation_variant': {
                        'arguments': {
                            'src_keys_mapping': ['city_id'],
                            'dst_key': ['extra_data'],
                        },
                        'operation_name': 'copy_fields_to_subobject',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'communal-events',
    },
]

# tariff settings are taken from somewhere in library
# from the file named tariff_settings.json
@pytest.mark.tariff_settings
@pytest.mark.parametrize(
    'tariff_zone, should_find',
    [
        pytest.param('moscow', True, id='known zone'),
        pytest.param('winterfell', False, id='unknown zone'),
    ],
)
async def test_city_by_tariff_zone(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        tariff_zone,
        should_find,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _OEP_PIPELINES,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'communal-events',
                'data': order_events_gen(
                    make_order_event(topic='smth', tariff_zone=tariff_zone),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie_for_rms_sink_',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_rms_sink_'

    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and taxi_rider_metrics_storage_mock.times_called < 1
    ):
        await asyncio.sleep(0.05)
    assert taxi_rider_metrics_storage_mock.times_called == 1
    if not should_find:
        assert (
            'extra_data'
            not in taxi_rider_metrics_storage_mock.calls[0]['events'][0]
        )
    else:
        assert (
            taxi_rider_metrics_storage_mock.calls[0]['events'][0][
                'extra_data'
            ]['city_id']
            == 'Москва'
        )
