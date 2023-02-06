import json

_OEP_PIPELINES = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'eventus-adjust-taxi'},
        'root': {'sink_name': 'drivers_adjust_sink'},
        'name': 'eventus-adjust-taxi',
    },
]


async def test_drivers_adjust_sink(
        taxi_order_events_producer,
        testpoint,
        taxi_config,
        stq,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _OEP_PIPELINES,
    )

    event = {
        'driver_uuid': 'driver_uuid',
        'adjust_app_name': 'app_name',
        'adjust_app_token': 'app_token',
        'adjust_event_token': 'event_token',
        'status_updated': 1608729070.303,
        'order_id': 'order_id',
        'tariff_class': 'tariff_class',
        'driver_license_personal_id': 'driver_license_personal_id',
        'driver_mm_device_id': 'driver_mm_device_id',
        'unique_driver_id': 'unique_driver_id',
        'order_type': 'taximeter',
    }

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'eventus-adjust-taxi',
                'data': json.dumps(event),
                'topic': 'smth',
                'cookie': 'cookie_for_adjust_sink_0',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_adjust_sink_0'

    assert stq.driver_adjust_events.times_called == 1
    call_args = stq.driver_adjust_events.next_call()
    if 'log_extra' in call_args['kwargs']:
        del call_args['kwargs']['log_extra']
    assert call_args['queue'] == 'driver_adjust_events'
    assert call_args['id'] == 'driver_uuid'
    assert call_args['kwargs'] == {
        'adjust_user_id': 'driver_uuid',
        'app_name': 'app_name',
        'app_token': 'app_token',
        'event_token': 'event_token',
        'created_at': {'$date': '2020-12-23T13:11:10.000Z'},
        'callback_params': {
            'order_id': 'order_id',
            'driver_uuid': 'driver_uuid',
            'tariff_class': 'tariff_class',
            'driver_license_personal_id': 'driver_license_personal_id',
            'driver_mm_device_id': 'driver_mm_device_id',
            'unique_driver_id': 'unique_driver_id',
            'order_type': 'taximeter',
        },
        'partner_params': {'order_type': 'taximeter'},
    }
