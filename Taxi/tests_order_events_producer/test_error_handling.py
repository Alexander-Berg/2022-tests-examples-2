import json

import pytest

_OEP_PIPELINE_WITH_WARNING = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'order-events'},
        'root': {
            'output': {'sink_name': 'rms_sink'},
            'operations': [
                {
                    'name': 'fetch_user_phone_id',
                    'operation_variant': {
                        'arguments': {'default_phone_type': 'yandex'},
                        'operation_name': 'remote::fetch_user_phone_id',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'order-events',
    },
]


@pytest.mark.parametrize(
    'mock_return_code, warning_count, error_count',
    [
        pytest.param(200, 0, 0, id='no errors'),
        pytest.param(500, 0, 1, id='error we want to know about'),
        # case below has one error from case above, since
        # statistics are not reset between cases
        pytest.param(404, 1, 1, id='warning'),
    ],
)
async def test_warnings(
        taxi_order_events_producer,
        taxi_order_events_producer_monitor,
        testpoint,
        taxi_config,
        make_order_event,
        order_events_gen,
        taxi_rider_metrics_storage_mock,
        taxi_eventus_orchestrator_mock,
        mockserver,
        mock_return_code,
        warning_count,
        error_count,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('eventus-statistics::get_pipeline_stats')
    def get_pipeline_stats(data):
        pass

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def _(_):
        if mock_return_code == 200:
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
        return mockserver.make_response(
            response=json.dumps(
                {
                    'code': 'more machine-readable error codes, more, please',
                    'message': 'human-readable message',
                },
            ),
            content_type='application/json',
            status=mock_return_code,
        )

    await taxi_order_events_producer.tests_control(reset_metrics=True)
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _OEP_PIPELINE_WITH_WARNING,
    )

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-events',
                'data': order_events_gen(
                    make_order_event(
                        event_key='handle_transporting',
                        user_id='user-1',
                        db_id='dbid1',
                        driver_uuid='driveruuid1',
                        status_updated=1571253356.368,
                        personal_phone_id='custom-user-phone-id',
                        destinations_geopoint=[[37.69411325, 55.78685382]],
                        topic='smth',
                    ),
                ).cast('json'),
                'topic': 'smth',
                'cookie': 'cookie_for_rms_sink_0',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_rms_sink_0'

    _ = await taxi_order_events_producer_monitor.get_metrics()
    pipeline_stats = (await get_pipeline_stats.wait_call())['data']
    pipeline_stats = pipeline_stats['order-events']
    assert pipeline_stats['aggregated_errors'] == error_count
    assert pipeline_stats['aggregated_warnings'] == warning_count
