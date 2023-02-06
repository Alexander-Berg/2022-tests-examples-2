import datetime
import typing as tp
import uuid

import pytest

from taxi_driver_metrics.common.constants import driver_event as constants
from taxi_driver_metrics.common.models import DmsEventsProvider
from taxi_driver_metrics.common.models import Events

ORDER_ID = 'df308741efd553b6b97416880b6ac8d8'
ORDER_ID2 = '8f26fac34e52185c95a5e3806ec49d85'
UDID = '5b05621ee6c22ea2654849c0'
TST_DRIVER_ID = '100700_5b05621ee6c22ea2654849c0'
TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)
TST_LICENSE = 'license3'
TST_ZONE = 'zone3'
TST_EVENT_ID = '743'


@pytest.mark.filldb()
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                USE_ORDER_CORE_PY3={'driver-metrics': {'enabled': True}},
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                USE_ORDER_CORE_PY3={'driver-metrics': {'enabled': False}},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'order_id, raw_event, expected',
    [
        (
            ORDER_ID,
            {
                'v': 2,
                'timestamp': str(TIMESTAMP),
                'handler': 'complete',
                'order_id': ORDER_ID,
                'reason_code': None,
                'reason': None,
                'update_index': 1,
                'udid': UDID,
                'candidate_index': 0,
                'driver_id': TST_DRIVER_ID,
                'license': TST_LICENSE,
                'zone': TST_ZONE,
                'dp_values': {},
                'distance_to_a': 1110,
                'time_to_a': 110,
                'payment_type': 'cash',
                'taxi_status': 'waiting',
            },
            {
                'event_name': Events.OrderEventType.COMPLETE.value,
                'tags': {
                    'dispatch_short',
                    'new_gen',
                    'tariff_econom',
                    'is_prediction_fallback',
                },
                'activity': 90,
                'distance': 174,
                'time_to_a': 94,
                'driver_tags': ['vasyl!', 'gena'],
                'rider_tags': ['t2'],
                'driver_id': '400000039360_09e3f01aa64759cf24cd87f8df36c0cb',
                'dbid_uuid': (
                    'd4158ba9e98c4b0882c4157782e0237d_'
                    '09e3f01aa64759cf24cd87f8df36c0cb'
                ),
                'udid': '5b05621ee6c22ea2654849c1',
            },
        ),
        (
            ORDER_ID,
            {
                'candidate_index': 1,
                'order_id': ORDER_ID,
                'timestamp': str(TIMESTAMP),
                'reason_code': 'reject',
                'reason': 'autocancel',
                'driver_id': TST_DRIVER_ID,
                'dp_values': {
                    'a': -2,
                    'c': 10,
                    'o': -2,
                    'n': -2,
                    'p': 0,
                    'r': -2,
                },
                'update_index': 3,
                'license': TST_LICENSE,
                'udid': UDID,
                'handler': 'offer_reject',
                'v': 2,
                'zone': TST_ZONE,
                'tariff_class': 'vip',
                'extra_field': 'some_value',
                'properties': [constants.EventTags.LONG_WAITING],
                'taxi_status': None,
            },
            {
                'event_name': Events.OrderEventType.REJECT_AUTO_CANCEL.value,
                'tags': {'tariff_econom', constants.EventTags.LONG_WAITING},
                'activity': 100,
                'distance': 80,
                'time_to_a': 47,
                'driver_tags': [],
                'rider_tags': ['t2'],
                'driver_id': '400000039360_6a55a1de3c5e65c0b633fd325706e4a4',
                'dbid_uuid': (
                    'd4158ba9e98c4b0882c4157782e0237d_'
                    '6a55a1de3c5e65c0b633fd325706e4a4'
                ),
                'udid': '5b05621ee6c22ea2654849c0',
            },
        ),
        (
            ORDER_ID,
            {
                'candidate_index': 2,
                'order_id': ORDER_ID,
                'timestamp': str(TIMESTAMP),
                'reason_code': 'achtung',
                'reason': 'autocancel',
                'driver_id': TST_DRIVER_ID,
                'dp_values': {
                    'a': -2,
                    'c': 10,
                    'o': -2,
                    'n': -2,
                    'p': 0,
                    'r': -2,
                },
                'update_index': 8,
                'license': TST_LICENSE,
                'udid': UDID,
                'handler': 'achtung',
                'v': 2,
                'zone': TST_ZONE,
            },
            None,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_TAG_LIST_TO_STORE={
        'driver': ['vasyl!', 'gena'],
        'rider': ['t2'],
    },
)
async def test_from_order_proc(
        order_id,
        raw_event,
        expected,
        stq3_context,
        dms_mockserver,
        order_core_mock,
):
    event = await Events.OrderEvent.make_from_raw_event(
        stq3_context, order_id, raw_event,
    )

    assert bool(event) == bool(expected)

    event_provider = DmsEventsProvider(stq3_context)

    if not event:
        return

    assert event
    assert event.driver_id == expected.get('driver_id')
    assert event.descriptor.event_name == expected['event_name']

    await event_provider.save_event(event)

    unprocessed_list = await event_provider.fetch_unprocessed_events(
        {'worker_id': 1, 'workers_count': 2},
    )

    assert len(unprocessed_list) == 1
    assert len(unprocessed_list[0].events) == 1

    res = unprocessed_list[0].events[0]
    res = tp.cast(Events.OrderEvent, res)

    assert res
    assert res.driver_id == expected.get('driver_id')
    assert res.descriptor.event_name == expected['event_name']
    assert sorted(res.tags) == sorted(expected['tags'])
    assert res.activity_value == expected['activity']
    assert res.zone == TST_ZONE
    assert res.order_alias_id == 'fde4e486f1ec5f66ab8b5947b8f6d01a'
    assert res.tariff_class == event.tariff_class
    assert res.distance_to_a == expected['distance']
    assert res.time_to_a == expected['time_to_a']
    assert res.driver_tags == expected.get('driver_tags')
    assert res.rider_tags == expected.get('rider_tags')
    assert res.dbid == 'd4158ba9e98c4b0882c4157782e0237d'
    assert res.extra_data_json.get('sp') == 1.0
    assert res.extra_data_json.get('sp_alpha') == 0
    assert 'tariff_' + str(event.tariff_class) in res.tags

    assert res.dbid_uuid == expected.get('dbid_uuid')

    res = await event_provider.events_history(
        expected['udid'], datetime.datetime.min,
    )

    assert not res

    await event_provider.complete_event(
        event_id=unprocessed_list[0].events[0].event_id,
        entity_id=expected['udid'],
        ticket_id=unprocessed_list[0].extra['ticket_id'],
    )

    res = await event_provider.events_history(
        expected['udid'], datetime.datetime.min,
    )

    assert res
    assert res[0].timestamp == TIMESTAMP

    res = await event_provider.fetch_unprocessed_events(
        {'worker_id': 1, 'workers_count': 2},
    )
    assert not res


@pytest.mark.parametrize(
    'event',
    [
        Events.ServiceManualEvent(
            timestamp=TIMESTAMP,
            entity_id=UDID,
            zone=TST_ZONE,
            event_id=uuid.uuid4().hex,
            value=12,
            mode=Events.ManualValueMode.ADDITIVE,
            reason='Tst reason',
        ),
        Events.UnifiedEvent(
            timestamp=TIMESTAMP,
            entity_id=UDID,
            zone=TST_ZONE,
            event_id=uuid.uuid4().hex,
            dbid_uuid='123_e33',
            order_alias_id='alias',
            descriptor=Events.EventTypeDescriptor('some_strange_type'),
            event_type='super_event',
            extra_data={'if_first': True},
        ),
    ],
)
async def test_serialization(
        event, stq3_context, web_context, dms_mockserver, event_equals,
):
    event.event_id = '1'

    event_provider = DmsEventsProvider(stq3_context)

    await event_provider.save_event(event)

    unprocessed_list = await event_provider.fetch_unprocessed_events(
        params={'max_batch_size': 100, 'worker_id': 1, 'workers_count': 2},
    )
    assert len(unprocessed_list) == 1
    assert len(unprocessed_list[0].events) == 1

    res = unprocessed_list[0].events[0]

    event_equals(res, event)

    await event_provider.complete_event(
        event_id=res.event_id,
        entity_id=UDID,
        ticket_id=0,
        params={'activity_change': 44},
    )

    res = await event_provider.events_history(UDID, datetime.datetime.min)

    if event.event_type == Events.EventType.ORDER_EVENT:
        event_equals(event, res[0])

    event = Events.OrderEvent(
        timestamp=TIMESTAMP,
        entity_id=UDID,
        zone=TST_ZONE,
        event_id='2',
        activity_value=22,
        descriptor=Events.EventTypeDescriptor(
            Events.OrderEventType.REJECT_WRONG_WAY.value,
            tags=[constants.EventTags.CHAINED_ORDER],
        ),
        rider_tags=[],
        driver_tags=['velerun', 'krakozyabr'],
        tariff_class='va',
        additional_data={},
    )

    await event_provider.save_event(event)

    unprocessed_list = await event_provider.fetch_unprocessed_events(
        params={'max_batch_size': 100, 'worker_id': 1, 'workers_count': 2},
    )
    assert len(unprocessed_list) == 1
    assert len(unprocessed_list[0].events) == 1

    res = unprocessed_list[0].events[0]

    event_equals(event, res)

    await event_provider.complete_event(
        event_id=res.event_id,
        entity_id=UDID,
        ticket_id=0,
        params={'activity_change': 44},
    )

    res = await event_provider.events_history(UDID, datetime.datetime.min)

    event_equals(event, res[1])


@pytest.mark.parametrize('request_param_error', [True, False])
@pytest.mark.parametrize('internal_server_error', [True, False])
async def test_save_to_dms(
        request_param_error, internal_server_error, web_context, mockserver,
):

    event_provider = DmsEventsProvider(web_context)

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    async def _request(*args, **kwargs):
        if internal_server_error:
            return mockserver.make_response(status=500)
        if request_param_error:
            return mockserver.make_response(status=400)
        return {}

    event = Events.OrderEvent(
        event_id='event',
        timestamp=datetime.datetime.now(),
        activity_value=100,
        dbid_uuid='1_1',
        driver_id='100500_3960bb1be4254e0eae9c65122656f912',
        descriptor=Events.EventTypeDescriptor(
            Events.OrderEventType.COMPLETE.value,
        ),
        zone='moscow',
        order_id='d0061468211427938d62b9d86930dcce',
        tariff_class='econom',
        entity_id='5b05621ee6c22ea2654849c0',
    )

    try:
        await event_provider.save_event(event)
        assert not (internal_server_error or request_param_error)
    except Events.BaseError:
        assert internal_server_error or request_param_error
