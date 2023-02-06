import itertools
import json

import pytest


from tests_order_events_producer import quadkey_extractor


def _get_pipelines_config(key_from, key_to, zoom):
    arguments = {'from': key_from, 'to': key_to}

    if zoom is not None:
        arguments['zoom'] = zoom

    pipeline = {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'order-events'},
        'root': {
            'output': {
                'sink_name': 'clickhouse_sink',
                'arguments': {
                    'bulk_size_threshold': 1,
                    'bulk_duration_of_data_collection_ms': 100,
                    'input_queue_size': 10000,
                    'output_queue_size': 1000,
                },
            },
            'operations': [
                {
                    'name': 'lonlat-to-quadkey',
                    'operation_variant': {
                        'arguments': arguments,
                        'operation_name': 'atlas::lonlat_to_quadkey',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'filter-fields-for-sink',
                    'operation_variant': {
                        'arguments': {'leave_keys_list': [key_to]},
                        'operation_name': 'filter_fields',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'order-events',
    }

    return [pipeline]


_ZOOMS = [0, 1, 5, 10, 18, 24, None]
_KEYS_FROM = ['geopoint']
_KEYS_TO = ['quadkey']

_LATS = [-100, -90, -50, 0, 50, 90, 100]
_LONS = [i for i in range(-200, 200, 66)]
_LONS.append(0)

_SPB_LATS = [59.8, 59.9, 60.0, 60.1]
_SPB_LONS = [30.2, 30.3, 30.4, 30.5, 30.6]

_COORDINATES = [(_LONS, _LATS), (_SPB_LONS, _SPB_LATS)]


@pytest.mark.suspend_periodic_tasks('send_statistics')
async def test_lonlat_to_quadkey_mapper(
        taxi_order_events_producer,
        taxi_config,
        testpoint,
        make_order_event,
        order_events_gen,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('clickhouse-sink-sender::clickhouse_sink')
    def event_processed_clickhouse(data):
        pass

    for zoom, key_from, key_to in itertools.product(
            _ZOOMS, _KEYS_FROM, _KEYS_TO,
    ):
        pipelines_config = _get_pipelines_config(key_from, key_to, zoom)
        await taxi_eventus_orchestrator_mock.set_pipelines_config(
            testpoint, taxi_order_events_producer, pipelines_config,
        )
        await taxi_order_events_producer.run_task('invalidate-seq_num')

        for lons, lats in _COORDINATES:
            for lon, lat in itertools.product(lons, lats):
                point = [lon, lat]
                response = await taxi_order_events_producer.post(
                    '/tests/logbroker/messages',
                    data=json.dumps(
                        {
                            'consumer': 'order-events',
                            'data': json.dumps({key_from: point}),
                            'topic': 'smth',
                            'cookie': 'cookie1',
                        },
                    ),
                )

                assert response.status_code == 200

                await commit.wait_call()
                assert (
                    (await event_processed_clickhouse.wait_call())['data']
                    == [
                        {
                            key_to: quadkey_extractor.quadkey_extractor(
                                point, zoom,
                            ),
                        },
                    ]
                )
