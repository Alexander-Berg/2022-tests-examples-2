import asyncio
import json
import time

import pytest


def get_oep_pipelines_config(fetch_upi_args):
    return [
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
                            'arguments': {
                                'src': 'topic',
                                'match_with': 'smth',
                            },
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
                        'name': 'fetch_user_phone_id',
                        'operation_variant': {
                            'arguments': fetch_upi_args,
                            'operation_name': 'remote::fetch_user_phone_id',
                            'type': 'mapper',
                        },
                    },
                ],
            },
            'name': 'communal-events',
        },
    ]


@pytest.mark.parametrize(
    'default_phone_type, message_phone_type, expected_phone_type, success',
    [
        pytest.param('taxi', None, 'taxi', True, id='get default phone type'),
        pytest.param(
            'taxi', 'uber', 'uber', True, id='get phone type from message',
        ),
        pytest.param(
            None,
            'uber',
            'uber',
            True,
            id='get phone type from message without default',
        ),
        pytest.param(
            None, 228, None, False, id='phone type should not be a number',
        ),
        pytest.param(
            1337, None, None, False, id='phone type should not be a number',
        ),
        pytest.param(
            None,
            None,
            None,
            False,
            id='neither in message nor in default value',
        ),
    ],
)
async def test_fetcher(
        taxi_order_events_producer,
        taxi_rider_metrics_storage_mock,
        testpoint,
        taxi_eventus_orchestrator_mock,
        make_order_event,
        order_events_gen,
        mockserver,
        taxi_config,
        default_phone_type,
        message_phone_type,
        expected_phone_type,
        success,
):
    fetch_upi_args = {}
    if default_phone_type:
        fetch_upi_args['default_phone_type'] = default_phone_type

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_order_events_producer,
        get_oep_pipelines_config(fetch_upi_args),
    )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def handle(request):
        return mockserver.make_response(
            response=json.dumps(
                {
                    'phone': '88005553535',
                    'is_loyal': True,
                    'is_yandex_staff': True,
                    'is_taxi_staff': True,
                    'id': 'upi0',
                    'type': 'taxi',
                    'stat': {
                        'big_first_discounts': 2,
                        'complete': 2,
                        'complete_card': 8,
                        'complete_apple': 1,
                        'complete_google': 4,
                        'total': 8,
                        'fake': 8,
                    },
                },
            ),
        )

    await taxi_order_events_producer.invalidate_caches()
    await taxi_order_events_producer.enable_testpoints()
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'communal-events',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_transporting',
                        user_id='user-1',
                        db_id='dbid1',
                        driver_uuid='driveruuid1',
                        status_updated=1571253356.368,
                        # user_phone_id will be rewritten by mapper
                        user_phone_id='custom-user-phone-id',
                        destinations_geopoint=[[37.69411325, 55.78685382]],
                        topic='smth',
                        personal_phone_id='ppi0',
                        phone_type=message_phone_type,
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie_for_rms_sink_0',
            },
        ),
    )
    assert response.status_code == 200
    assert (await commit.wait_call())['data'] == 'cookie_for_rms_sink_0'

    if expected_phone_type is not None:
        user_api_request = handle.next_call()['request'].json
        assert user_api_request['personal_phone_id'] == 'ppi0'
        assert user_api_request['type'] == expected_phone_type

    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and taxi_rider_metrics_storage_mock.times_called < 1
    ):
        await asyncio.sleep(0.05)

    # reject messages on errors in next PRs
    assert taxi_rider_metrics_storage_mock.times_called == 1
    event = taxi_rider_metrics_storage_mock.calls[0]['events'][0]
    if success:
        assert event['user_id'] == 'upi0'
    else:
        assert event['user_id'] == 'custom-user-phone-id'
