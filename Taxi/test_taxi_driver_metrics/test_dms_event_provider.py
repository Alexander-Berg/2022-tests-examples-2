# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
import datetime
import functools
import json

import pytest

from taxi.clients import driver_metrics_storage as dms
from taxi.clients.helpers import base as api_utils
from taxi.util import dates

from taxi_driver_metrics.common.models import DmsEventsProvider
from taxi_driver_metrics.common.models import Events


TST_EVENT_TYPE = 'tst_event_type'
TST_TIMESTAMP = datetime.datetime.utcnow()
TST_UDID = '5f8e02ef8f32ca50b5df3cd6'
TST_EVENT_ID = '884'
TST_TOKEN = 'unique_token'
TST_ORDER_ALIAS_ID = 'unique_alias'
TST_ORDER_ID = 'order_id'
TST_DBID_UUID = '0203212s032_32c342fg3d3'
TST_EVENT_DESCRIPTOR = {'name': 'event_name', 'tags': ['event_tags']}


@pytest.fixture
def dms_client(web_context):
    return DmsEventsProvider(web_context)


def mark_default_config(func):
    @functools.wraps(func)
    @pytest.mark.config(
        DRIVER_METRICS_STORAGE_CLIENT_SETTINGS={
            '__default__': {
                '__default__': {
                    'num_retries': 0,
                    'retry_delay_ms': [50],
                    'request_timeout_ms': 250,
                },
            },
        },
    )
    async def _wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return _wrapper


@mark_default_config
async def test_request_error(dms_client, mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def patch_request(*args, **kwargs):
        return mockserver.make_response(
            json={'code': 'error', 'message': 'error happened'}, status=400,
        )

    try:
        await dms_client.activity_values(unique_driver_ids=['udid'])
    except dms.FailedToFetchActivity:
        pass
    else:
        assert False


@mark_default_config
async def test_new_event(dms_client, mockserver):
    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    def _patch_request(*args, **kwargs):
        data = args[0].json
        assert data['idempotency_token'] == TST_TOKEN
        assert 'eid' not in data
        assert data['order_alias'] == TST_ORDER_ALIAS_ID
        assert len(data) == 7
        return {}

    await dms_client.save_event(
        Events.BaseEvent(
            event_id=TST_TOKEN,
            event_type=TST_EVENT_TYPE,
            entity_id=TST_UDID,
            timestamp=TST_TIMESTAMP,
            order_id=TST_ORDER_ID,
            order_alias_id=TST_ORDER_ALIAS_ID,
        ),
    )
    assert _patch_request.times_called


@mark_default_config
async def test_events_history(dms_client, mockserver):
    @mockserver.json_handler('/driver-metrics-storage/v2/events/history')
    def _patch_request(*args, **kwargs):
        timestring = dates.localize(TST_TIMESTAMP).isoformat()
        data = args[0].json
        assert data['unique_driver_id'] == TST_UDID
        assert datetime.datetime.fromisoformat(
            data['created_after'],
        ) == dates.localize(TST_TIMESTAMP)
        return {
            'events': [
                {
                    'created': timestring,
                    'type': 'order',
                    'event_id': 8,
                    'extra_data': json.dumps({'descriptor': {'name': 'seen'}}),
                },
            ],
        }

    hist = await dms_client.events_history(
        entity_id=TST_UDID, from_timestamp=TST_TIMESTAMP,
    )
    assert len(hist) == 1
    event = hist[0]
    assert event.timestamp == TST_TIMESTAMP
    assert event.event_type == 'order'
    assert event.entity_id == TST_UDID


@pytest.mark.parametrize('activity_to_set', [77, None])
@pytest.mark.parametrize('current_activity', [70, None])
@pytest.mark.parametrize('loyalty_change', [2, None])
@mark_default_config
async def test_complete_event(
        dms_client,
        mockserver,
        activity_to_set,
        current_activity,
        loyalty_change,
):
    @mockserver.json_handler('/driver-metrics-storage/v3/event/complete')
    def _patch_request(*args, **kwargs):
        data = args[0].json
        assert data['event_id'] is not None
        assert data['ticket_id'] is not None
        activity_entry = data.get('activity')
        if activity_entry is not None:
            assert activity_entry.get('value_to_set') is not None
            assert activity_entry.get('increment') is not None
            current = activity_entry.get('current')
            if current is not None:
                assert (
                    current + activity_entry['increment']
                    == activity_entry['value_to_set']
                )
        return {}

    activity_change = 0
    if activity_to_set is not None and current_activity is not None:
        activity_change = activity_to_set - current_activity

    await dms_client.complete_event(
        event_id=TST_EVENT_ID,
        entity_id=TST_UDID,
        ticket_id=123,
        params={
            'activity_change': activity_change,
            'activity_to_set': activity_to_set,
            'loyalty_change': loyalty_change,
        },
    )

    assert _patch_request.times_called


@mark_default_config
async def test_events_unprocessed_list(dms_client, mockserver):
    @mockserver.json_handler(
        '/driver-metrics-storage/v3/events/unprocessed/list',
    )
    def _patch_request(*args, **kwargs):
        params = args[0].json
        assert isinstance(params.get('limit'), int)
        items = [
            {
                'ticket_id': 1,
                'unique_driver_id': 'udid_1',
                'current_activity': 98,
                'events': [
                    {
                        'event_id': 4,
                        'created': api_utils.time_to_iso_string_or_none(
                            TST_TIMESTAMP,
                        ),
                        'type': 'order',
                        'descriptor': {'type': 'order'},
                    },
                ],
            },
            {
                'ticket_id': 2,
                'unique_driver_id': 'udid_2',
                'current_activity': 88,
                'events': [
                    {
                        'event_id': 64,
                        'created': api_utils.time_to_iso_string_or_none(
                            TST_TIMESTAMP,
                        ),
                        'type': 'dm_service_manual',
                        'descriptor': {'type': 'set_activity_value'},
                        'extra_data': {'operation': 'set_activity_value'},
                    },
                ],
            },
        ]
        return {'items': items}

    unprocessed = await dms_client.fetch_unprocessed_events(
        params={'max_batch_size': 2, 'worker_id': 1, 'workers_count': 2},
    )
    assert len(unprocessed) == 2
    first = unprocessed[0]
    second = unprocessed[1]
    assert first.entity_id == 'udid_1'
    assert len(first.events) == 1
    assert first.events[0].event_type == 'order'
    assert second.entity_id == 'udid_2'
    assert len(second.events) == 1
    assert second.events[0].event_type == 'dm_service_manual'


@pytest.mark.parametrize('with_additional_info', [True, False])
@mark_default_config
async def test_events_processed(dms_client, mockserver, with_additional_info):
    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    def _patch_request(*args, **kwargs):
        data = args[0].json
        assert data.get('unique_driver_id') is not None
        events = [
            {
                'event': {
                    'event_id': '4',
                    'type': 'reposition',
                    'order_id': TST_ORDER_ID,
                    'order_alias': TST_ORDER_ALIAS_ID,
                    'park_driver_profile_id': TST_DBID_UUID,
                    'tariff_zone': 'bangladesh',
                    'extra_data': json.dumps(
                        {'descriptor': {'type': 'cancel', 'tags': []}},
                    ),
                    'datetime': api_utils.time_to_iso_string_or_none(
                        TST_TIMESTAMP,
                    ),
                },
                'reason': 'no reason',
            },
        ]
        if data['with_additional_info']:
            events[0].update({'activity_change': 3, 'loyalty_change': 1})
        return {'events': events}

    res = await dms_client.processed_events_v3(
        udid=TST_UDID,
        dbid_uuid=TST_DBID_UUID,
        timestamp_from=TST_TIMESTAMP,
        timestamp_to=TST_TIMESTAMP,
        with_additional_info=with_additional_info,
        order_ids=[],
    )

    assert _patch_request.times_called
    assert len(res) == 1
    item = res[0]
    if with_additional_info:
        assert item.loyalty_change == 1
        assert item.activity_change == 3
    else:
        assert getattr(item, 'loyalty_change', 1) == 0
        assert getattr(item, 'activity_change', 3) == 0
    assert item.event.type == 'reposition'
    assert item.event.dbid_uuid == TST_DBID_UUID
