import copy
import datetime

import pytest

from tests_subventions_activity_producer import common

MESSAGE_PROTO = {
    'data': {
        'drivers': [
            {
                'dbid': 'dbid',
                'uuid': 'uuid',
                'unique_driver_id': 'udid',
                'activity': 88,
            },
        ],
        'billing_types': ['geo_booking'],
        'classes': ['econom', 'business'],
        'tags': ['tag1', 'tag2'],
        'geoarea': 'zone1',
        'timestamp': '2020-01-01T12:00:00+0000',
        'payment_type_restrictions': 'online',
    },
}

EXPECTED_BILLING_EVENT = {
    'external_obj_id': (
        'taxi/geoarea_activity/unique_driver_id/udid/2020-01-01T09:00'
    ),
    'external_event_ref': 'driver_geoarea_activity/2020-01-01T09:00/1',
    'event_at': '2020-01-01T09:01:30+00:00',
    'kind': 'driver_geoarea_activity',
    'data': {
        'version': 1,
        'unique_driver_id': 'udid',
        'driver_id': 'clid_uuid',
        'driver_dbid': 'dbid',
        'tags': ['tag1', 'tag2'],
        'time_interval_start_utc': '2020-01-01T09:00:00+00:00',
        'time_interval_end_utc': '2020-01-01T09:01:00+00:00',
        'activity_points': 88.0,
        'rule_types': ['geo_booking'],
        'geoarea_activities': [
            {
                'geoareas': ['zone1'],
                'status': 'free',
                'start_at_utc': '2020-01-01T09:00:00+00:00',
                'end_at_utc': '2020-01-01T09:00:35+00:00',
            },
        ],
        'available_classes': ['econom', 'business'],
        'profile_payment_type_restrictions': 'online',
    },
}


def _make_messages():
    start_time = datetime.datetime(2020, 1, 1, 12, 0)
    messages = []
    for i in range(6):
        message = copy.deepcopy(MESSAGE_PROTO)
        time = start_time + datetime.timedelta(seconds=i * 7)
        message['data']['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%S+0300')
        messages.append(message)
    return messages


@pytest.mark.now('2020-01-01T12:01:00+03:00')
@pytest.mark.servicetest
@common.suspend_all_periodic_tasks
async def test_full_pipeline(
        taxi_subventions_activity_producer,
        testpoint,
        mockserver,
        mocked_time,
        taxi_config,
):
    @mockserver.json_handler('/billing-orders/v1/process_event')
    def _v1_process_event(request):
        doc = request.json
        assert doc == EXPECTED_BILLING_EVENT
        return {'doc': {'id': 1000}}

    messages = _make_messages()
    await common.set_logbroker_messages(
        taxi_subventions_activity_producer, messages,
    )

    await common.run_message_fetcher_once(
        taxi_subventions_activity_producer, taxi_config,
    )

    # To trigger aggregation we need emulate that some time spent
    mocked_time.sleep(30)

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer, taxi_config,
    )
    await common.run_events_sender_once(
        taxi_subventions_activity_producer, taxi_config,
    )

    assert _v1_process_event.times_called > 0
