import json

import pytest


_PIPELINE_CONFIG = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'eventus-adjust-taxi'},
        'root': {
            'sink_name': 'tags_sink',
            'arguments': {
                'provider_id': 'test_provider',
                'bulk_size_threshols': 2,
                'bulk_duration_of_data_collection_ms': 100,
            },
        },
        'name': 'eventus-adjust-taxi',
    },
]


@pytest.mark.now('2021-11-01T18:00:00+0000')
async def test_tags_sink(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        make_order_event,
        order_events_gen,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        mockserver,
        tags_upload_comparer,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def tags_upload(request):
        return mockserver.make_response(status=200, json={})

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _PIPELINE_CONFIG,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'eventus-adjust-taxi',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_transporting',
                        user_id='user-1',
                        db_id='dbid1',
                        driver_uuid='driveruuid1',
                        topic='smth',
                        tags=['test1', 'test2'],
                        provider_id='test_provider',
                        driver_profile_id='test_driver_id1',
                        park_id='test_park_id1',
                    ),
                    make_order_event(
                        event_key='handle_transporting',
                        user_id='user-1',
                        db_id='dbid1',
                        driver_uuid='driveruuid1',
                        topic='smth',
                        tags=['test1', 'test2'],
                        provider_id='test_provider',
                        driver_profile_id='test_driver_id1',
                        park_id='test_park_id1',
                    ),
                    make_order_event(
                        event_key='handle_transporting',
                        user_id='user-1',
                        db_id='dbid1',
                        driver_uuid='driveruuid1',
                        topic='smth',
                        tags=['test3', 'test4'],
                        tags_apply_policy='remove',
                        provider_id='test_provider',
                        park_driver_profile_id='test_park_id1_test_driver_id1',
                    ),
                    make_order_event(
                        event_key='handle_transporting',
                        user_id='user-3',
                        db_id='dbid3',
                        driver_uuid='driveruuid3',
                        topic='smth',
                        tags=['test5', 'test6'],
                        provider_id='test_provider',
                        driver_profile_id='test_driver_id3',
                        park_id='test_park_id3',
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie_for_tags_sink_0',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_tags_sink_0'
    tags_request = (await tags_upload.wait_call())['request']
    assert 'X-Idempotency-Token' in tags_request.headers
    assert (
        tags_request.headers['X-Idempotency-Token']
        == 'test_provider:2021-11-01T18:00:00+0000'
    )
    assert tags_request.json == {
        'provider_id': 'test_provider',
        'append': [
            {
                'entity_type': 'dbid_uuid',
                'tags': tags_upload_comparer(
                    [
                        {
                            'name': 'test1',
                            'entity': 'test_park_id1_test_driver_id1',
                        },
                        {
                            'name': 'test2',
                            'entity': 'test_park_id1_test_driver_id1',
                        },
                        {
                            'name': 'test5',
                            'entity': 'test_park_id3_test_driver_id3',
                        },
                        {
                            'name': 'test6',
                            'entity': 'test_park_id3_test_driver_id3',
                        },
                    ],
                ),
            },
        ],
        'remove': [
            {
                'entity_type': 'dbid_uuid',
                'tags': tags_upload_comparer(
                    [
                        {
                            'name': 'test3',
                            'entity': 'test_park_id1_test_driver_id1',
                        },
                        {
                            'name': 'test4',
                            'entity': 'test_park_id1_test_driver_id1',
                        },
                    ],
                ),
            },
        ],
    }

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'eventus-adjust-taxi',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_transporting',
                        user_id='user-2',
                        db_id='dbid2',
                        driver_uuid='driveruuid2',
                        topic='smth',
                        tags=['test1'],
                        tags_ttl_seconds=60,
                        tags_ttl_until='2021-12-01T18:00:00+0000',
                        driver_profile_id='test_driver_id2',
                        park_id='test_park_id2',
                        idempotency_token='test_token2',
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie_for_tags_sink_0',
            },
        ),
    )
    assert response.status_code == 200
    assert (await commit.wait_call())['data'] == 'cookie_for_tags_sink_0'
    tags_request = (await tags_upload.wait_call())['request']
    assert 'X-Idempotency-Token' in tags_request.headers
    assert (
        tags_request.headers['X-Idempotency-Token']
        == 'test_provider:2021-11-01T18:00:00+0000'
    )
    assert tags_request.json == {
        'provider_id': 'test_provider',
        'append': [
            {
                'entity_type': 'dbid_uuid',
                'tags': tags_upload_comparer(
                    [
                        {
                            'name': 'test1',
                            'entity': 'test_park_id2_test_driver_id2',
                            'ttl': 60,
                            'until': '2021-12-01T18:00:00+0000',
                        },
                    ],
                ),
            },
        ],
    }
