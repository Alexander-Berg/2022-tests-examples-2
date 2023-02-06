# pylint: disable=protected-access, C1801, C0103,
# pylint: disable=too-many-lines, R0915, unused-variable
import dataclasses
import datetime
import json
import uuid

import bson
import pytest

from metrics_processing.rules.common import RuleType
from metrics_processing.tagging import utils as tags_utils
from taxi.clients import stq_agent
from taxi.util import dates

from taxi_driver_metrics.common.constants import (
    driver_event as driver_event_constants,
)
from taxi_driver_metrics.common.models import Blocking
from taxi_driver_metrics.common.models import BlockingType
from taxi_driver_metrics.common.models import DmsEventsProvider
from taxi_driver_metrics.common.models import DriverDataError
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import ItemBasedEntityProcessor
from taxi_driver_metrics.common.models import run_dms_processing
from taxi_driver_metrics.common.models.processing_items import (
    ActivityProcessingItem,
)
from taxi_driver_metrics.common.models.rules import rule_utils


TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)
TWO_DAYS_BEFORE = TIMESTAMP - datetime.timedelta(days=2)
ONE_SEC_AFTER = (TIMESTAMP + datetime.timedelta(seconds=1)).replace(
    microsecond=0,
)
ONE_HOUR_AFTER = TIMESTAMP + datetime.timedelta(hours=1)
TEN_SEC_AFTER = TIMESTAMP + datetime.timedelta(seconds=10)
BAD_DRIVER_ID = '5b05621ee6c22ea2654849c0'
TST_DRIVER_ID = '5b05621ee6c22ea2654849c7'
TST_PROFILE = '3900923892034823ff092390920f90'
TANKER_KEY = 'key'
TEST_REF_ID = 'ref_id'
TST_RULE_NAME = 'tst_rule'
NEW_TST_RULE_NAME = 'new_blocking_rule'
TST_ZONE = 'bangladesh'
TST_ZONE2 = 'urupinsk'
TST_TAG = '\'lucky\' OR \'talented\''
TST_EVENT_DESCR = Events.EventTypeDescriptor(
    Events.OrderEventType.OFFER_TIMEOUT.value,
)
TST_EVENT_DESCR2 = Events.EventTypeDescriptor(
    Events.OrderEventType.COMPLETE.value,
)
TST_EVENT_DESCR3 = Events.EventTypeDescriptor(
    Events.OrderEventType.SEEN_TIMEOUT.value,
)
TST_EVENT_REF_ID = 'sodfjasiaioid3i3i3'
TST_EVENT_REF_ID2 = 'sodfjasiaioid3i3i4'
TST_EVENT_REF_ID3 = 'sodfjasiaioid3i3i6'
TST_EVENT_REF_ID4 = 'sodfjasiaioid3i3i8s'

DP_FIRST_VALUE = 66
DEFAULT = '__default__'
TEST_AMNESTY_DP = 77
TST_UDID = '5b05621ee6c22ea2654849c9'
TST_DBID_UUID = '0203212s032_32c342fg3d3'

ACTIVITY_BLOCKING_THRESHOLD = 30
ACTIVITY_AMNESTY_DEFAULT = 60


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_unblocking(
        stq3_context, entity_processor, patch, dms_mockserver,
):
    @patch('taxi_driver_metrics.common.models.blocking_journal.reset_blocking')
    async def reset_blocking(db, blocking, **kwargs):
        return

    entity_processor._event_timestamp = TIMESTAMP
    entity_processor._context = DriverInfo(
        BAD_DRIVER_ID,
        current_blocking=sorted(
            [
                Blocking(
                    TWO_DAYS_BEFORE,
                    BlockingType.BY_ACTIONS,
                    zone='2',
                    rule_name=TST_RULE_NAME,
                    reason='a',
                ),
                Blocking(
                    TWO_DAYS_BEFORE + datetime.timedelta(seconds=10),
                    BlockingType.BY_ACTIVITY,
                    zone='1',
                    rule_name=TST_RULE_NAME,
                    reason='a',
                ),
                Blocking(
                    TIMESTAMP + datetime.timedelta(seconds=1),
                    BlockingType.BY_ACTIVITY,
                    zone='3',
                    rule_name=TST_RULE_NAME,
                    reason='a',
                ),
            ],
            key=lambda x: x.until,
            reverse=True,
        ),
        activity=10,
        blocking_history=[
            Blocking(
                TWO_DAYS_BEFORE + datetime.timedelta(seconds=5),
                BlockingType.BY_ACTIVITY,
                zone='4',
                rule_name=TST_RULE_NAME,
                reason='a',
            ),
        ],
    )
    await entity_processor._process_unblocking()
    calls = reset_blocking.calls
    assert len(calls) == 2
    assert calls[0]['blocking'].zone == '1'
    assert calls[1]['blocking'].zone == '2'
    assert len(entity_processor.driver.current_blocking) == 1
    assert entity_processor.driver.get_active_blocking(
        BlockingType.BY_ACTIVITY,
    )
    assert not entity_processor.driver.get_active_blocking(
        BlockingType.BY_ACTIONS,
    )
    assert len(entity_processor.driver.blocking_history) == 3
    assert entity_processor.driver.blocking_history[0].zone == '1'
    assert entity_processor.driver.blocking_history[1].zone == '4'
    assert entity_processor.driver.blocking_history[2].zone == '2'
    assert entity_processor.driver.activity == 10
    assert dms_mockserver.event_new.times_called == 2


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_unblocking_too_early(stq3_context, fake_event_provider, patch):
    @patch('taxi_driver_metrics.common.models.blocking_journal.reset_blocking')
    async def reset_blocking(db, blocking, **kwargs):
        return

    processor = ItemBasedEntityProcessor(stq3_context, fake_event_provider([]))
    processor._event_timestamp = TIMESTAMP
    processor._context = DriverInfo(
        BAD_DRIVER_ID,
        current_blocking=sorted(
            [
                Blocking(
                    TIMESTAMP + datetime.timedelta(seconds=1),
                    BlockingType.BY_ACTIVITY,
                    zone='3',
                    reason='reason',
                    rule_name=TST_RULE_NAME,
                ),
            ],
            key=lambda x: x.until,
            reverse=True,
        ),
        blocking_state=Blocking(
            TIMESTAMP + datetime.timedelta(seconds=1),
            BlockingType.BY_ACTIVITY,
            reason='reason',
            rule_name=TST_RULE_NAME,
        ),
        activity=40,
        blocking_history=[],
    )
    await processor._process_unblocking()
    await processor._apply_blocking_state()
    calls = reset_blocking.calls
    assert not calls
    assert len(processor.driver.current_blocking) == 1
    assert processor.driver.get_active_blocking(BlockingType.BY_ACTIVITY)
    assert not processor.driver.blocking_history
    assert processor.driver.activity == 40


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.parametrize('activity', [10, 100])
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_new_blocking(
        stq3_context,
        dms_mockserver,
        entity_processor,
        stq_client_patched,
        patch,
        activity,
        fake_event_provider,
        cached_drivers,
        predict_activity,
):
    entity_processor._event_timestamp = TIMESTAMP
    entity_processor._context = DriverInfo(
        BAD_DRIVER_ID,
        current_blocking=sorted(
            [
                Blocking(
                    TWO_DAYS_BEFORE,
                    BlockingType.BY_ACTIONS,
                    zone='2',
                    reason='test_reason',
                    rule_name=TST_RULE_NAME,
                ),
            ],
            key=lambda x: x.until,
            reverse=True,
        ),
        blocking_history=[
            Blocking(
                TWO_DAYS_BEFORE + datetime.timedelta(seconds=5),
                BlockingType.BY_ACTIVITY,
                zone='1',
                rule_name=TST_RULE_NAME,
                reason='cause',
            ),
        ],
        activity=activity,
        tags=set(),
    )
    dispatch_id = await predict_activity(
        BAD_DRIVER_ID, {'order_reject_manual': -90, 'order_complete': 100},
    )
    event = Events.UnifiedEvent(
        event_id='1', entity_id=TST_UDID, timestamp=TIMESTAMP,
    )
    entity_processor._event = event
    item = ActivityProcessingItem(
        stq3_context,
        context=entity_processor.driver,
        event=event,
        now=dates.utcnow(),
        event_timestamp=event.timestamp,
    )
    await entity_processor._process_blocking_items([item])
    await entity_processor._apply_blocking_state()

    if activity < 70:
        assert entity_processor.driver.get_active_blocking(
            BlockingType.BY_ACTIVITY,
        )
        assert (
            entity_processor.driver.current_blocking[0].rule_name
            == 'TooLowActivity'
        )
        assert entity_processor.driver.current_blocking[1].zone == '2'
    else:
        assert entity_processor.driver.get_active_blocking(
            BlockingType.BY_ACTIONS,
        )
        assert entity_processor.driver.current_blocking[0].zone == '2'

    assert len(entity_processor.driver.blocking_history) == 1

    test_driver = await DriverInfo.make(
        stq3_context, BAD_DRIVER_ID, fake_event_provider([]), TIMESTAMP,
    )

    blocking = test_driver.blocking_state
    assert blocking

    if activity < 70:
        expected_type = BlockingType.BY_ACTIVITY
        expected_until = ONE_HOUR_AFTER
        await entity_processor._event_provider.save_event(
            Events.OrderEvent(
                descriptor=Events.EventTypeDescriptor(
                    Events.OrderEventType.REJECT_MANUAL.value,
                ),
                dispatch_id=dispatch_id,
                timestamp=TIMESTAMP,
                zone=TST_ZONE2,
                event_id='2',
                driver_id=BAD_DRIVER_ID,
                entity_id=BAD_DRIVER_ID,
                order_id='393j3393j939j393',
            ),
        )
        await run_dms_processing(stq3_context, 1)
        test_driver = cached_drivers[-1]
        assert len(test_driver.current_blocking) == 1
    else:
        expected_type = BlockingType.BY_ACTIONS
        expected_until = TWO_DAYS_BEFORE
    assert blocking.type == expected_type
    assert blocking.until == expected_until

    if activity < 70:
        await entity_processor._event_provider.save_event(
            Events.OrderEvent(
                descriptor=Events.EventTypeDescriptor(
                    Events.OrderEventType.COMPLETE.value,
                ),
                dispatch_id=dispatch_id,
                timestamp=TIMESTAMP,
                zone=TST_ZONE2,
                event_id='2',
                driver_id=BAD_DRIVER_ID,
                entity_id=BAD_DRIVER_ID,
                order_id='393j3393j939j393',
            ),
        )
        await run_dms_processing(stq3_context, 1)
        test_driver = cached_drivers[-1]
        assert not test_driver.get_active_blocking(BlockingType.BY_ACTIVITY)


@pytest.mark.config(DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100)
@pytest.mark.parametrize('activity', [10, 100])
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_new_blocking_by_items(
        stq3_context,
        dms_mockserver,
        item_entity_processor,
        stq_client_patched,
        patch,
        activity,
        fake_event_provider,
        cached_drivers,
        predict_activity,
):
    item_entity_processor._event_timestamp = TIMESTAMP
    item_entity_processor._context = DriverInfo(
        BAD_DRIVER_ID,
        current_blocking=sorted(
            [
                Blocking(
                    TWO_DAYS_BEFORE,
                    BlockingType.BY_ACTIONS,
                    zone='2',
                    reason='test_reason',
                    rule_name=TST_RULE_NAME,
                ),
            ],
            key=lambda x: x.until,
            reverse=True,
        ),
        blocking_history=[
            Blocking(
                TWO_DAYS_BEFORE + datetime.timedelta(seconds=5),
                BlockingType.BY_ACTIVITY,
                zone='1',
                rule_name=TST_RULE_NAME,
                reason='cause',
            ),
        ],
        activity=activity,
        tags=set(),
    )
    dispatch_id = await predict_activity(
        BAD_DRIVER_ID, {'order_reject_manual': -90, 'order_complete': 100},
    )
    event = Events.UnifiedEvent(
        event_id='1', entity_id=TST_UDID, timestamp=TIMESTAMP,
    )
    item_entity_processor._event = event
    await item_entity_processor._process_blocking_items(
        [item_entity_processor._make_item(ActivityProcessingItem)],
    )
    await item_entity_processor._apply_blocking_state()

    if activity < 70:
        assert item_entity_processor.driver.get_active_blocking(
            BlockingType.BY_ACTIVITY,
        )
        assert (
            item_entity_processor.driver.current_blocking[0].rule_name
            == 'TooLowActivity'
        )
        assert item_entity_processor.driver.current_blocking[1].zone == '2'
    else:
        assert item_entity_processor.driver.get_active_blocking(
            BlockingType.BY_ACTIONS,
        )
        assert item_entity_processor.driver.current_blocking[0].zone == '2'

    assert len(item_entity_processor.driver.blocking_history) == 1

    test_driver = await DriverInfo.make(
        stq3_context, BAD_DRIVER_ID, fake_event_provider([]), TIMESTAMP,
    )

    blocking = test_driver.blocking_state
    assert blocking

    if activity < 70:
        expected_type = BlockingType.BY_ACTIVITY
        expected_until = ONE_HOUR_AFTER
        await item_entity_processor._event_provider.save_event(
            Events.OrderEvent(
                descriptor=Events.EventTypeDescriptor(
                    Events.OrderEventType.REJECT_MANUAL.value,
                ),
                dispatch_id=dispatch_id,
                timestamp=TIMESTAMP,
                zone=TST_ZONE2,
                event_id='2',
                driver_id=BAD_DRIVER_ID,
                entity_id=BAD_DRIVER_ID,
                order_id='393j3393j939j393',
            ),
        )
        await run_dms_processing(stq3_context, 1)
        test_driver = cached_drivers[-1]
        assert len(test_driver.current_blocking) == 1
    else:
        expected_type = BlockingType.BY_ACTIONS
        expected_until = TWO_DAYS_BEFORE
    assert blocking.type == expected_type
    assert blocking.until == expected_until

    if activity < 70:
        await item_entity_processor._event_provider.save_event(
            Events.OrderEvent(
                descriptor=Events.EventTypeDescriptor(
                    Events.OrderEventType.COMPLETE.value,
                ),
                dispatch_id=dispatch_id,
                timestamp=TIMESTAMP,
                zone=TST_ZONE2,
                event_id='2',
                driver_id=BAD_DRIVER_ID,
                entity_id=BAD_DRIVER_ID,
                order_id='393j3393j939j393',
            ),
        )
        await run_dms_processing(stq3_context, 1)
        test_driver = cached_drivers[-1]
        assert not test_driver.get_active_blocking(BlockingType.BY_ACTIVITY)


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_manual_unblocking(stq3_context, fake_event_provider, patch):
    driver = DriverInfo(
        BAD_DRIVER_ID,
        current_blocking=sorted(
            [
                Blocking(
                    ONE_SEC_AFTER,
                    BlockingType.BY_ACTIONS,
                    zone='2',
                    rule_name=TST_RULE_NAME,
                    reason='a',
                ),
                Blocking(
                    ONE_SEC_AFTER + datetime.timedelta(seconds=10),
                    BlockingType.BY_ACTIVITY,
                    zone='1',
                    rule_name=TST_RULE_NAME,
                    reason='a',
                ),
                Blocking(
                    ONE_SEC_AFTER + datetime.timedelta(seconds=1),
                    BlockingType.BY_ACTIVITY,
                    zone='3',
                    rule_name=TST_RULE_NAME,
                    reason='a',
                ),
            ],
            key=lambda x: x.until,
            reverse=True,
        ),
        activity=20,
        blocking_history=[
            Blocking(
                TWO_DAYS_BEFORE + datetime.timedelta(seconds=5),
                BlockingType.BY_ACTIVITY,
                zone='4',
                reason='a',
            ),
        ],
    )
    driver.set_loaded()

    @patch('taxi_driver_metrics.common.models.blocking_journal.reset_blocking')
    async def reset_blocking(db, blocking, **kwargs):
        return

    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor._acquire_context',
    )
    async def fake_fetch_data(*args, **kwargs):
        return driver

    @patch(
        'taxi_driver_metrics.common.models.'
        '_blocking_journal.fetch_current_blocking',
    )
    async def fake_fetch_blocking(*args, **kwargs):
        return [
            Blocking(
                ONE_SEC_AFTER,
                BlockingType.BY_ACTIONS,
                zone='2',
                rule_name=TST_RULE_NAME,
                reason='a',
            ),
        ]

    @patch(
        'taxi_driver_metrics.common.models.'
        'driver_info.DriverInfo._commit_unique_driver_changes',
    )
    async def fake_update_unique(*args, **kwargs):
        return True

    processor = ItemBasedEntityProcessor(stq3_context, fake_event_provider([]))
    processor._event_timestamp = TIMESTAMP
    await processor.process_unblocking(BAD_DRIVER_ID, force_unblock=True)
    calls = reset_blocking.calls
    assert len(calls) == 3
    call = fake_update_unique.calls
    assert len(call) == 3
    assert fake_fetch_data.calls
    assert not processor.driver.current_blocking
    assert not processor.driver.get_active_blocking(BlockingType.BY_ACTIVITY)
    assert not processor.driver.get_active_blocking(BlockingType.BY_ACTIONS)
    assert len(processor.driver.blocking_history) == 4
    assert processor.driver.activity == 20


@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTION_BLOCKING_RULES={
        rule_utils.CONFIG_DEFAULT: [],
        TST_ZONE: [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'blocking_duration_sec': 3,
                                'max_blocked_cnt': 3,
                                'type': 'blocking',
                                'tanker_key_template': TANKER_KEY,
                            },
                        ],
                    },
                ],
                'events': [{'name': 'offer_timeout', 'topic': 'order'}],
                'events_to_trigger_cnt': 1,
                'name': TST_RULE_NAME,
            },
        ],
    },
)
async def test_blocking_limit(
        stq3_context,
        fake_event_provider,
        stq_client_patched,
        patch,
        dms_mockserver,
        entity_processor,
):
    counters = [3, 1]
    for counter in counters:

        @patch('taxi_driver_metrics.common.models.blocking_stats.get_counter')
        async def get_counter(*args, counter=counter, **kwargs):
            return counter

        event = Events.OrderEvent(
            descriptor=Events.EventTypeDescriptor(
                Events.OrderEventType.OFFER_TIMEOUT.value,
            ),
            timestamp=TIMESTAMP,
            zone=TST_ZONE,
            event_id=TST_EVENT_REF_ID2,
            driver_id=TST_DRIVER_ID,
            entity_id=BAD_DRIVER_ID,
            order_id='393j3393j939j394',
            activity_value=10,
        )
        await entity_processor._event_provider.save_event(event)
        await run_dms_processing(stq3_context, 1)

        driver = await DriverInfo.make(
            stq3_context, BAD_DRIVER_ID, fetch_events_history=False,
        )

        assert (
            not driver.current_blocking
            if counter == 3
            else driver.current_blocking
        )
        assert (
            not driver.blocking_state
            if counter == 3
            else driver.blocking_state
        )


# Too many local variables (>20)
# pylint: disable=R0914
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAGGING_RULES=True)
@pytest.mark.rules_config(
    TAGGING={
        TST_ZONE2: [
            {
                'name': 'some_rule',
                'events_period_sec': 7200,
                'events_to_trigger_cnt': 2,
                'events': [{'topic': 'order', 'name': 'complete'}],
                'tags': '\'tags::a\' AND \'tags::b\' AND NOT \'tags::c\'',
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'udid',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [
                                    {'name': 'tag1'},
                                    {'name': 'lucky', 'ttl': 300},
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                'name': 'other_rule',
                'events_period_sec': '7200',
                'events_to_trigger_cnt': '1',
                'events': [{'topic': 'order', 'name': 'complete'}],
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'provider_id': 'efficiency',
                                'tags': [{'name': 'f'}],
                            },
                        ],
                    },
                ],
            },
            {
                'name': 'other_events',
                'events_period_sec': '7200',
                'events_to_trigger_cnt': '2',
                'events': [
                    {
                        'topic': 'reposition',
                        'tags': """ 'event::cool' AND 'event::looc' """,
                    },
                ],
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'provider_id': 'driver-metrics',
                                'entity_type': 'dbid_uuid',
                                'tags': [{'name': 'tag_for_reposition_event'}],
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
async def test_process_new_events(
        stq3_context,
        entity_processor,
        patch,
        tags_service_mock,
        dms_mockserver,
        cached_journals,
):
    def upload_check(*args, **kwargs):
        request = args[0]
        data = request.json
        assert data
        assert data['tags']
        entity_id = data['tags'][0]['match']['id']
        entity_type = data['entity_type']
        if entity_type == 'udid':
            assert entity_id == BAD_DRIVER_ID
        elif entity_type == 'dbid_uuid':
            assert entity_id == TST_DBID_UUID

    driver_tags = {'a', 'b', 'd', 'tags::a', 'tags::b', 'tags::d'}

    @patch(
        'taxi_driver_metrics.common.models.ItemBasedEntityProcessor'
        '._acquire_context',
    )
    async def full_data(*args, **kwargs):
        driver = DriverInfo(
            BAD_DRIVER_ID,
            activity=90,
            current_blocking=[],
            blocking_history=[],
            tags=driver_tags,
        )
        driver.append_event(processed_event)
        driver._loaded = True
        return driver

    @patch('taxi_driver_metrics.common.models.DriverInfo.fetch_tags')
    async def _fetch_tags(*args, **kwargs):
        return

    @patch(
        'taxi_driver_metrics.common.models.'
        '_processor.Processor.make_entity_processor',
    )
    def make_entity_processor(*args, **kwargs):
        return entity_processor

    tags_patch = tags_service_mock(upload_check=upload_check)

    processed_event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor(
            Events.OrderEventType.COMPLETE.value, tags=['test'],
        ),
        timestamp=TIMESTAMP,
        zone=TST_ZONE2,
        event_id=TST_EVENT_REF_ID2,
        driver_id=TST_DRIVER_ID,
        entity_id=BAD_DRIVER_ID,
        order_id='393j3393j939j394',
        activity_value=10,
    )

    order_event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor(
            Events.OrderEventType.COMPLETE.value, tags=['test'],
        ),
        timestamp=TIMESTAMP,
        zone=TST_ZONE2,
        event_id=TST_EVENT_REF_ID,
        driver_id=TST_DRIVER_ID,
        entity_id=BAD_DRIVER_ID,
        order_id='393j3393j939j393',
        activity_value=10,
    )

    unified_event = Events.UnifiedEvent(
        descriptor=Events.EventTypeDescriptor(
            'reposition-event', tags=['cool', 'looc'],
        ),
        timestamp=TIMESTAMP,
        zone=TST_ZONE2,
        event_id=TST_EVENT_REF_ID3,
        entity_id=BAD_DRIVER_ID,
        order_id='order_id_23423',
        dbid_uuid=TST_DBID_UUID,
        event_type='reposition',
    )

    unified_event_2 = Events.UnifiedEvent(
        descriptor=Events.EventTypeDescriptor(
            'reposition-event', tags=['cool', 'looc'],
        ),
        timestamp=TIMESTAMP,
        zone=TST_ZONE2,
        event_id=TST_EVENT_REF_ID4,
        entity_id=BAD_DRIVER_ID,
        order_id='order_id_23423',
        dbid_uuid=TST_DBID_UUID,
        event_type='reposition',
    )

    await entity_processor._event_provider.save_event(order_event)
    await entity_processor._event_provider.save_event(unified_event)
    await entity_processor._event_provider.save_event(unified_event_2)
    await run_dms_processing(stq3_context, 10)

    # Count of calls and tagging of the last processed event
    assert tags_patch.tags_upload.times_called == 3
    tagging_actions = entity_processor._action_journal.actions[
        RuleType.TAGGING
    ]
    assert len(tagging_actions) == 2
    assert len(tagging_actions[0].action.tags) == 2
    assert (
        tagging_actions[0].action.merge_policy
        == tags_utils.TagMergePolicy.APPEND
    )
    assert tagging_actions[0].action.tags[0]['name'] == 'tag1'
    assert tagging_actions[0].action.tags[1]['name'] == 'lucky'
    assert tagging_actions[1].action.tags[0]['name'] == 'f'
    activity = entity_processor._action_journal.actions[RuleType.ACTIVITY]
    assert len(activity) == 1
    event_provider = DmsEventsProvider(stq3_context)
    unprocessed_list = await event_provider.fetch_unprocessed_events(
        params={'limit': 10, 'worker_id': 1, 'workers_count': 2},
    )
    assert not unprocessed_list

    processed = await entity_processor._event_provider.events_history(
        BAD_DRIVER_ID, TWO_DAYS_BEFORE,
    )
    order_ids = [event.order_id for event in processed]
    assert unified_event.order_id in order_ids
    assert unified_event_2.order_id in order_ids

    assert 'tags::f' in entity_processor.driver.tags
    assert 'tags::tag_for_reposition_event' in entity_processor.driver.tags

    assert len(entity_processor.driver.blocking_history) == 0


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.parametrize(
    'new_activity, expected_activity, should_unblock',
    [(0, 0, False), (100, 100, True), (-100, 0, False), (330, 100, True)],
)
async def test_manual_activity(
        stq3_context,
        dms_mockserver,
        entity_processor,
        patch,
        new_activity,
        should_unblock,
        expected_activity,
):
    @patch('taxi_driver_metrics.common.models.blocking_journal.reset_blocking')
    async def reset_blocking(db, blocking, **kwargs):
        return

    @patch(
        'taxi_driver_metrics.common.models.'
        '_processor.Processor.make_entity_processor',
    )
    def make_entity_processor(*args, **kwargs):
        return entity_processor

    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor.'
        '_acquire_context',
    )
    async def _acquire_context(*args, **kwargs):
        driver = DriverInfo(
            BAD_DRIVER_ID,
            current_blocking=sorted(
                [
                    Blocking(
                        ONE_SEC_AFTER + datetime.timedelta(seconds=1),
                        BlockingType.BY_ACTIVITY,
                        zone='3',
                        rule_name=TST_RULE_NAME,
                    ),
                ],
                key=lambda x: x.until,
                reverse=True,
            ),
            activity=20,
            blocking_history=[],
        )
        driver._loaded = True
        return driver

    @patch(
        'taxi_driver_metrics.common.models.DriverInfo._apply_blocking_state',
    )
    async def apply_blocking_state(app, blocking, *args, **kwargs):
        return True

    event = Events.ServiceManualEvent(
        timestamp=TIMESTAMP,
        entity_id=BAD_DRIVER_ID,
        event_id='__',
        value=new_activity,
        mode=Events.ManualValueMode.ABSOLUTE,
        reason='Tst reason_commit_unique_driver_changes',
    )

    await entity_processor._event_provider.save_event(event)
    await run_dms_processing(stq3_context, 1)
    entity_processor._action_journal.modify_local_context()

    if should_unblock:
        calls = reset_blocking.calls
        assert len(calls) == 1
        calls2 = apply_blocking_state.calls
        assert calls2[1]['blocking'] is None

    assert bool(entity_processor.driver.current_blocking) != should_unblock
    assert entity_processor.driver.activity == expected_activity

    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor.'
        '_acquire_context',
    )
    async def _acquire_context_2(*args, **kwargs):
        driver = DriverInfo(
            BAD_DRIVER_ID,
            current_blocking=sorted(
                [
                    Blocking(
                        ONE_SEC_AFTER + datetime.timedelta(seconds=1),
                        BlockingType.BY_ACTIVITY,
                        zone='3',
                        rule_name=TST_RULE_NAME,
                    ),
                ],
                key=lambda x: x.until,
                reverse=True,
            ),
            activity=expected_activity,
            blocking_history=[],
        )
        driver._loaded = True
        return driver

    event = Events.ServiceManualEvent(
        timestamp=TIMESTAMP,
        entity_id=BAD_DRIVER_ID,
        event_id='event_id',
        value=-7,
        mode=Events.ManualValueMode.ADDITIVE,
        reason='Tst reason_commit_unique_driver_changes',
    )
    await entity_processor._event_provider.save_event(event)
    await run_dms_processing(stq3_context, 1)

    entity_processor._action_journal.modify_local_context()

    assert entity_processor.driver.activity == max(0, expected_activity - 7)


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.parametrize('loyalty_change', [0, 100500])
async def test_manual_loyalty(
        stq3_context,
        dms_mockserver,
        entity_processor,
        fake_event_provider,
        patch,
        loyalty_change,
        cached_journals,
):
    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor.'
        '_acquire_context',
    )
    async def _acquire_context(*args, **kwargs):
        driver = DriverInfo(
            BAD_DRIVER_ID,
            current_blocking=sorted(
                [
                    Blocking(
                        ONE_SEC_AFTER + datetime.timedelta(seconds=1),
                        BlockingType.BY_ACTIVITY,
                        zone='3',
                        rule_name=TST_RULE_NAME,
                        reason='some_reason',
                    ),
                ],
                key=lambda x: x.until,
                reverse=True,
            ),
            activity=20,
            blocking_history=[],
        )
        driver._loaded = True
        return driver

    event = Events.ServiceManualEvent(
        timestamp=TIMESTAMP,
        entity_id=BAD_DRIVER_ID,
        operation=Events.ServiceManualEventType.SET_LOYALTY_VALUE,
        event_id='__',
        value=loyalty_change,
        reason='Tst reason_commit_unique_driver_changes',
    )

    await entity_processor._event_provider.save_event(event)
    await run_dms_processing(stq3_context, 1)

    journal = cached_journals[0].actions[RuleType.LOYALTY]

    assert len(journal) == 1
    assert journal[0].action.result == loyalty_change


TEST_ORDER_ID = 'test_order_id'
TEST_ORDER_ALIAS_ID = 'test_order_alias_id'
TEST_CITY_ID = 'test_city_id'
TEST_ZONE = 'test_nearest_zone'
TEST_DRIVER_ID = 'test_driver_id'
TEST_PARK_ID = 'test_park_id'
TEST_LICENSE = 'test_license'
TEST_DRIVER_EVENT_ID = 'test_driver_event_id'
TEST_UNIQUE_DRIVER_ID = 'test_unique_driver_id'
TEST_DB_ID = 'test_db_id'


class UniqueDriver:
    def __init__(self, dp, udid=None):
        self.driver_points = dp
        self.id = udid
        if not self.id:
            self.id = bson.ObjectId()

    async def save_to_db(self, db, license_):
        updater = dict()
        updater['_id'] = self.id

        if self.driver_points:
            updater['dp'] = self.driver_points

        updater['licenses'] = [{'license': license_}]
        await db.unique_drivers.save(updater)


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.parametrize('use_new_block', [True, False])
@pytest.mark.parametrize(
    'unique,driver_event,result',
    [
        # Breathing test
        (UniqueDriver(93), ['n', 0], (93, False)),
        (UniqueDriver(None), ['c', 10], (DP_FIRST_VALUE + 10, True)),
        # Simple block
        (
            UniqueDriver(TEST_AMNESTY_DP),
            ['a', -20],
            (TEST_AMNESTY_DP - 20, True),
        ),
        # Do not unblock, process wallet
        (UniqueDriver(100), ['c', 10], (100, False)),
        # If dp is 0
        (UniqueDriver(100), ['a', 0], (100, False)),
        # If dp is 0
        (UniqueDriver(100), ['a', -100], (0, True)),
    ],
)
@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            {
                'name': TST_RULE_NAME,
                'events': [{'topic': 'order', 'name': 'complete'}],
                'actions': [
                    {
                        'tags': """ 'event::a' """,
                        'action': [{'type': 'loyalty', 'value': 100}],
                    },
                    {
                        'tags': """ 'event::tariff_vip' """,
                        'action': [{'type': 'loyalty', 'value': -100}],
                    },
                    {'action': [{'type': 'loyalty', 'value': 0}]},
                ],
            },
        ],
    },
)
@pytest.mark.config(
    DRIVER_POINTS_AMNESTY_DEFAULT={DEFAULT: TEST_AMNESTY_DP},
    DRIVER_POINTS_FIRST_VALUE={DEFAULT: DP_FIRST_VALUE},
    DRIVER_POINTS_MIN_RULES={DEFAULT: TEST_AMNESTY_DP},
    DRIVER_POINTS_DISABLE_STEPS_RULES={DEFAULT: [60 * 60 * 24]},
)
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_processing_with_events(
        stq3_context,
        dms_mockserver,
        unique,
        driver_event,
        result,
        patch,
        use_new_block,
        entity_processor,
        cached_journals,
):
    @patch(
        'taxi_driver_metrics.common.utils.'
        '_tags_manager.TagsManager'
        '.fetch_experiment_tags',
    )
    def _fetch_experiment_tags(*args, **kwargs):
        return {'experiment::activity_blocking_rule'}

    driver_license = uuid.uuid4().hex

    await unique.save_to_db(stq3_context.mongo, driver_license)
    if unique.driver_points is not None:
        dms_mockserver.init_activity({str(unique.id): unique.driver_points})

    dscr = Events.__CODE_TO_EVENT[driver_event[0]][0].descriptor
    new_dscr = Events.EventTypeDescriptor(
        event_name=dscr.event_name, tags=['tariff_vip'],
    )
    new_event = Events.OrderEvent(
        event_id='123123',
        entity_id=str(unique.id),
        timestamp=TIMESTAMP,
        zone=TEST_ZONE,
        order_id=TEST_ORDER_ID,
        order_alias_id=TEST_ORDER_ALIAS_ID,
        descriptor=new_dscr,
        activity_value=unique.driver_points,
    )

    await entity_processor._event_provider.save_event(new_event)
    await run_dms_processing(stq3_context, 1)

    test_driver = await DriverInfo.make(
        stq3_context,
        str(unique.id),
        entity_processor._event_provider,
        TIMESTAMP,
    )

    activity_changed = test_driver.activity != unique.driver_points
    assert len(cached_journals) == 1
    activity_log = cached_journals[-1].actions[RuleType.ACTIVITY]
    if unique.driver_points is not None:
        assert activity_changed == (
            bool(activity_log) and (activity_log[0].action.result != 0)
        )

    assert (driver_event[0] == 'c') == bool(
        cached_journals[-1].actions[RuleType.LOYALTY],
    )


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            {
                'id': 'i_am_id',
                'name': 'some_rule',
                'zone': 'default',
                'events_period_sec': 3600,
                'type': 'loyalty',
                'events': [{'topic': 'order', 'tags': '\'event::good\''}],
                'actions': [{'action': [{'type': 'loyalty', 'value': 1}]}],
            },
        ],
        'spb': [
            {
                'id': 'i_am_id',
                'name': 'some_rule',
                'zone': 'spb',
                'events_period_sec': 3600,
                'type': 'loyalty',
                'events': [{'topic': 'order', 'tags': '\'event::good\''}],
                'actions': [{'action': [{'type': 'loyalty', 'value': 10}]}],
            },
            {
                'id': 'i_am_id',
                'name': 'best rule',
                'zone': 'spb',
                'type': 'loyalty',
                'events': [{'topic': 'order'}],
                'actions': [{'action': [{'type': 'loyalty', 'value': 15}]}],
            },
        ],
    },
)
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_processing_loyalty_rules_config(
        stq3_context, entity_processor, dms_mockserver, cached_journals,
):
    event_provider = DmsEventsProvider(stq3_context)
    await event_provider.save_event(
        Events.UnifiedEvent(
            event_id='400',
            entity_id=BAD_DRIVER_ID,
            timestamp=TIMESTAMP,
            event_type='order',
            zone='spb',
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.OrderEventType.COMPLETE.value,
            ),
        ),
    )

    await run_dms_processing(stq3_context, 1)
    loyalty_actions = cached_journals[0].actions[RuleType.LOYALTY]
    assert len(loyalty_actions) == 1
    assert loyalty_actions[0].action_result == 15

    await event_provider.save_event(
        Events.UnifiedEvent(
            event_id='401',
            entity_id=BAD_DRIVER_ID,
            timestamp=TIMESTAMP,
            event_type='order',
            zone='hell',
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.OrderEventType.COMPLETE.value, tags=['good'],
            ),
        ),
    )

    await run_dms_processing(stq3_context, 1)
    loyalty_actions = cached_journals[1].actions[RuleType.LOYALTY]
    assert len(loyalty_actions) == 1
    assert loyalty_actions[0].action_result == 1

    await event_provider.save_event(
        Events.UnifiedEvent(
            event_id='402',
            entity_id=BAD_DRIVER_ID,
            timestamp=TIMESTAMP,
            event_type='order',
            zone='hell',
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.OrderEventType.COMPLETE.value,
            ),
        ),
    )

    await run_dms_processing(stq3_context, 1)
    loyalty_actions = cached_journals[2].actions[RuleType.LOYALTY]
    assert len(loyalty_actions) == 0

    await event_provider.save_event(
        Events.UnifiedEvent(
            event_id='402',
            entity_id=BAD_DRIVER_ID,
            timestamp=TIMESTAMP,
            event_type='order',
            zone='spb',
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.OrderEventType.COMPLETE.value, tags=['good'],
            ),
        ),
    )

    await run_dms_processing(stq3_context, 1)
    loyalty_actions = cached_journals[3].actions[RuleType.LOYALTY]
    assert len(loyalty_actions) == 2
    assert loyalty_actions[0].action_result == 10
    assert loyalty_actions[1].action_result == 15


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        rule_utils.CONFIG_DEFAULT: [
            {
                'name': TST_RULE_NAME,
                'events': [{'topic': 'order', 'name': 'complete'}],
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 2,
                'actions': [{'action': [{'type': 'activity', 'value': 90}]}],
            },
        ],
    },
)
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_new_activity_predictions(
        stq3_context, dms_mockserver, patch, entity_processor,
):
    app = stq3_context
    driver = UniqueDriver(77)
    dms_mockserver.init_activity({str(driver.id): 77})

    driver_license = uuid.uuid4().hex
    db = app.mongo
    await driver.save_to_db(db, driver_license)

    events = [
        Events.OrderEvent(
            descriptor=TST_EVENT_DESCR2,
            timestamp=(TIMESTAMP - datetime.timedelta(minutes=90)),
            entity_id=str(driver.id),
            event_id=TST_EVENT_REF_ID,
        ),
        Events.OrderEvent(
            descriptor=TST_EVENT_DESCR2,
            timestamp=(TIMESTAMP - datetime.timedelta(minutes=5)),
            entity_id=str(driver.id),
            event_id=TST_EVENT_REF_ID2,
        ),
        Events.OrderEvent(
            descriptor=TST_EVENT_DESCR2,
            timestamp=TIMESTAMP,
            entity_id=str(driver.id),
            event_id=TST_EVENT_REF_ID3,
            zone='bangladesh',
        ),
    ]

    driver_info = await DriverInfo.make(
        stq3_context,
        str(driver.id),
        entity_processor._event_provider,
        TWO_DAYS_BEFORE,
    )
    entity_processor._context = driver_info

    driver_info.update_event(events[0])
    driver_info.update_event(events[1])

    entity_processor._event = driver_info.last_event
    item = ActivityProcessingItem(
        app,
        context=driver_info,
        event=driver_info.last_event,
        now=dates.utcnow(),
        event_timestamp=driver_info.last_event.timestamp,
    )
    res = await item._predict_single_value()
    res = res.value
    assert res == 0

    driver_info.update_event(events[2])
    entity_processor._event = driver_info.last_event
    entity_processor._event_timestamp = entity_processor._event.timestamp
    item = ActivityProcessingItem(
        app,
        context=driver_info,
        event=driver_info.last_event,
        now=dates.utcnow(),
        event_timestamp=driver_info.last_event.timestamp,
    )
    res = await item._predict_single_value()
    res = res.value
    assert res == 90


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 1}},
            'letter_events': {'c': {'activity': 1}},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 300,
        'tags': {'order': {'reject_manual': ['chained_order']}},
    },
)
@pytest.mark.filldb(unique_drivers='common')
async def test_activity_with_new_events(
        stq3_context,
        dms_mockserver,
        patch,
        cached_journals,
        event_provider,
        predict_activity,
):
    dms_mockserver.init_activity({BAD_DRIVER_ID: 10})
    dispatch_id = await predict_activity(
        BAD_DRIVER_ID,
        {'order_reject_manual_chained_order': 7, 'order_reject_manual': 0},
    )
    await event_provider.save_event(
        Events.OrderEvent(
            timestamp=TIMESTAMP,
            entity_id=BAD_DRIVER_ID,
            zone=TST_ZONE,
            event_id=TST_EVENT_REF_ID4,
            activity_value=10,
            dispatch_id=dispatch_id,
            descriptor=Events.EventTypeDescriptor(
                Events.OrderEventType.REJECT_MANUAL.value,
                tags=[driver_event_constants.EventTags.CHAINED_ORDER],
            ),
        ),
    )
    await run_dms_processing(stq3_context, 1)
    actions = cached_journals[-1].actions
    assert len(actions) == 17
    assert len(actions[RuleType.ACTIVITY]) == 2
    # because we recalculate activity every time now
    assert actions[RuleType.ACTIVITY][0].action.result == 50
    assert actions[RuleType.ACTIVITY][1].action.result == 7

    driver = await DriverInfo.make(
        stq3_context,
        BAD_DRIVER_ID,
        event_provider,
        TIMESTAMP,
        False,
        False,
        False,
    )
    assert driver.activity == 67


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTION_BLOCKING_RULES={
        rule_utils.CONFIG_DEFAULT: [],
        TST_ZONE2: [
            {
                'name': NEW_TST_RULE_NAME,
                'events_period_sec': 4000,
                'events_to_trigger_cnt': 2,
                'events': [{'topic': 'order', 'name': 'complete'}],
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'blocking',
                                'tanker_key_template': TANKER_KEY,
                                'max_blocked_cnt': 2,
                                'blocking_duration_sec': 10,
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
@pytest.mark.filldb(unique_drivers='common')
async def test_process_events(
        stq3_context,
        dms_mockserver,
        patch,
        entity_processor,
        fake_event_provider,
):
    @patch(
        'taxi_driver_metrics.common.models.ItemBasedEntityProcessor'
        '._fetch_full_driver_data',
    )
    async def _full_data(*args, **kwargs):
        return

    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor._fetch_full_driver_data',
    )
    async def _full_data_new(*args, **kwargs):
        return

    @patch(
        'taxi_driver_metrics.common.models.'
        'processing_items.BlockingProcessingItem._check_block',
    )
    def _(*args, **kwargs):
        return True

    @patch(
        'taxi_driver_metrics.common.models.'
        '_processor.Processor.make_entity_processor',
    )
    def make_entity_processor(*args, **kwargs):
        return entity_processor

    await entity_processor._event_provider.save_event(
        Events.OrderEvent(
            descriptor=Events.EventTypeDescriptor(
                Events.OrderEventType.COMPLETE.value, tags=['test'],
            ),
            timestamp=TIMESTAMP,
            zone=TST_ZONE2,
            event_id=TST_EVENT_REF_ID,
            driver_id=TST_DRIVER_ID,
            entity_id=BAD_DRIVER_ID,
            order_id='393j3393j939j393',
            activity_value=100,
        ),
    )

    await entity_processor._event_provider.save_event(
        Events.OrderEvent(
            descriptor=Events.EventTypeDescriptor(
                Events.OrderEventType.COMPLETE.value, tags=['test'],
            ),
            timestamp=TIMESTAMP,
            zone=TST_ZONE2,
            event_id=TST_EVENT_REF_ID2,
            driver_id=TST_DRIVER_ID,
            entity_id=BAD_DRIVER_ID,
            order_id='393j3393j939j394',
            activity_value=100,
        ),
    )

    entity_processor._context = DriverInfo(
        udid=BAD_DRIVER_ID, tags=set(), activity=100,
    )

    await run_dms_processing(stq3_context, 2)

    assert len(entity_processor.driver.current_blocking) == 1
    assert not entity_processor.driver.get_active_blocking(
        BlockingType.BY_ACTIVITY,
    )
    assert entity_processor.driver.get_active_blocking(BlockingType.BY_ACTIONS)
    assert entity_processor.driver.current_blocking[0].zone == TST_ZONE2
    assert entity_processor.driver.blocking_state
    assert entity_processor.driver.blocking_state.until == TEN_SEC_AFTER
    assert (
        entity_processor.driver.blocking_state.rule_name == NEW_TST_RULE_NAME
    )

    test_driver = await DriverInfo.make(
        stq3_context, BAD_DRIVER_ID, fake_event_provider([]), TIMESTAMP,
    )

    blocking = test_driver.blocking_state
    assert blocking
    assert blocking.type == BlockingType.BY_ACTIONS
    assert blocking.reason == rule_utils.DEFAULT_TANKER_KEY_TEMPLATE
    assert blocking.until == TEN_SEC_AFTER
    assert not test_driver.get_expired_blocking_count(BlockingType.BY_ACTIONS)
    assert test_driver.current_blocking
    assert test_driver.current_blocking[0].type == BlockingType.BY_ACTIONS
    assert test_driver.current_blocking[0].until == TEN_SEC_AFTER

    # check if race happened with blocking state
    entity_processor.driver.blocking_state = None
    with pytest.raises(DriverDataError):
        await entity_processor.driver._apply_blocking_state(
            stq3_context.mongo,
            Blocking(
                until=TIMESTAMP,
                type=BlockingType.BY_ACTIONS,
                reason='rere',
                zone=TST_ZONE,
                rule_name=TST_RULE_NAME,
            ),
        )


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_CONFIG_SERVICE_USAGE_SETTINGS={
        '__default__': ['blocking', 'loyalty', 'tagging'],
    },
)
@pytest.mark.rules_config(
    BLOCKING={
        'default': [],
        TST_ZONE2: [
            {
                'name': NEW_TST_RULE_NAME,
                'events_period_sec': 4000,
                'events_to_trigger_cnt': 1,
                'events': [{'topic': 'dm_service_manual'}],
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'blocking',
                                'tanker_key_template': TANKER_KEY,
                                'max_blocked_cnt': 2,
                                'blocking_duration_sec': 10,
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
@pytest.mark.filldb(unique_drivers='common')
async def test_block_for_all_events(
        stq3_context,
        dms_mockserver,
        patch,
        response_mock,
        entity_processor,
        fake_event_provider,
        cached_drivers,
):
    event_provider = DmsEventsProvider(stq3_context)

    @patch(
        'taxi_driver_metrics.common.models.ItemBasedEntityProcessor'
        '._fetch_full_driver_data',
    )
    async def _full_data(*args, **kwargs):
        return

    @patch('taxi_driver_metrics.common.models.blocking_journal.reset_blocking')
    async def _reset_blocking(db, blocking, **kwargs):
        return

    @patch(
        'taxi_driver_metrics.common.models.DriverInfo.'
        '_commit_unique_driver_changes',
    )
    async def _fake_commit_changes(*args, **kwargs):
        return

    @patch(
        'taxi_driver_metrics.common.models.DriverInfo._apply_blocking_state',
    )
    async def apply_blocking_state(app, blocking, *args, **kwargs):
        return True

    await event_provider.save_event(
        Events.ServiceManualEvent(
            timestamp=TIMESTAMP,
            entity_id=BAD_DRIVER_ID,
            event_id='__',
            value=10,
            mode=Events.ManualValueMode.ABSOLUTE,
            zone=TST_ZONE2,
            reason='Tst reason_commit_unique_driver_changes',
        ),
    )

    await run_dms_processing(stq3_context, 1)

    calls2 = apply_blocking_state.calls
    assert calls2
    driver = cached_drivers[-1]
    assert driver.get_active_blocking(BlockingType.BY_ACTIONS)


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAGGING_RULES=True)
@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'name': 'some_rule',
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 2,
                'protected': True,
                'events': [
                    {
                        'topic': 'order',
                        'name': 'seen_timeout',
                        'tags': '\'event::dispatch_short\'',
                    },
                    {'name': 'set_activity_value'},
                ],
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'entity_type': 'udid',
                                'merge_policy': 'append',
                                'provider_id': 'efficiency',
                                'tags': [
                                    {'name': 'tag1'},
                                    {'name': 'lucky', 'ttl': 300},
                                ],
                            },
                            {'type': 'push', 'code': 840},
                        ],
                    },
                ],
            },
        ],
    },
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now('2019-09-04T20:55:00')
async def test_processing_dms(
        stq3_context,
        dms_mockserver,
        patch_aiohttp_session,
        patch,
        response_mock,
        entity_processor,
        tags_service_mock,
        fake_event_provider,
):
    tags_patch = tags_service_mock()

    @patch('generated.clients.client_notify.ClientNotifyClient.v2_push_post')
    async def patch_send(*args, body, **kwargs):
        return body

    @patch(
        'taxi_driver_metrics.common.models.'
        '_processor.Processor.make_entity_processor',
    )
    def make_entity_processor(*args, **kwargs):
        return entity_processor

    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor.'
        '_acquire_context',
    )
    async def _acquire_context(*args, **kwargs):
        driver = DriverInfo(
            udid='5b0561a4e6c22ea26547d372',
            tags={'experiment::activity_blocking_rule'},
            activity=90,
        )
        driver._loaded = True
        return driver

    @patch(
        'taxi_driver_metrics.common.models._new_processor.'
        'ItemBasedEntityProcessor._acquire_context',
    )
    async def _acquire_context_new(*args, **kwargs):
        driver = DriverInfo(
            udid='5b0561a4e6c22ea26547d372',
            tags={'experiment::activity_blocking_rule'},
            activity=90,
        )
        driver._loaded = True
        return driver

    dms_mockserver.init_from_json()
    await entity_processor._event_provider.save_event(
        Events.OrderEvent(
            descriptor=Events.EventTypeDescriptor(
                Events.OrderEventType.COMPLETE.value, tags=['test'],
            ),
            timestamp=TIMESTAMP,
            zone=TST_ZONE2,
            event_id=TST_EVENT_REF_ID,
            driver_id=TST_DRIVER_ID,
            entity_id=BAD_DRIVER_ID,
            order_id='393j3393j939j393',
            activity_value=10,
        ),
    )

    events_num_1 = len(dms_mockserver.state.unprocessed)
    await run_dms_processing(stq3_context, 2)
    events_num_2 = len(dms_mockserver.state.unprocessed)
    assert events_num_1 - 2 == events_num_2
    assert len(dms_mockserver.state.processed) == 2
    assert (
        tags_patch.tags_upload.next_call()['_args'][0].query['provider_id']
        == 'driver-metrics-audited'
    )
    assert patch_send.calls
    assert not entity_processor.driver.get_active_blocking(
        BlockingType.BY_ACTIVITY,
    )


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.now(TEN_SEC_AFTER.isoformat())
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAGGING_RULES=True)
@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'name': 'some_rule',
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 2,
                'events': [
                    {'topic': 'reposition'},
                    {'topic': 'order', 'tags': '\'event::long_waiting\''},
                ],
                'actions': [
                    {
                        'action': [
                            {'type': 'tagging', 'tags': [{'name': 'tag1'}]},
                        ],
                    },
                ],
            },
            {
                'name': 'best rule',
                'events_to_trigger_cnt': 2,
                'events': [
                    {
                        'topic': 'dm_service_manual',
                        'name': 'set_activity_value',
                    },
                    {'topic': 'blocking', 'name': 'unblock'},
                ],
                'actions': [
                    {
                        'action': [
                            {'type': 'tagging', 'tags': [{'name': 'tag7'}]},
                        ],
                    },
                ],
            },
        ],
    },
)
async def test_processing_scenario(
        stq3_context,
        dms_mockserver,
        tags_service_mock,
        cached_journals,
        entity_processor,
):
    dms_mockserver.init_activity({BAD_DRIVER_ID: 10, TST_UDID: 93})
    dms_mockserver.init_complete_scores({BAD_DRIVER_ID: 0, TST_UDID: 0})

    tags_patch = tags_service_mock()
    # events for the first driver
    await entity_processor._event_provider.save_event(
        Events.UnifiedEvent(
            event_id='400',
            entity_id=BAD_DRIVER_ID,
            timestamp=TEN_SEC_AFTER,
            event_type='reposition',
        ),
    )
    await entity_processor._event_provider.save_event(
        Events.OrderEvent(
            event_id='88005',
            entity_id=BAD_DRIVER_ID,
            timestamp=TIMESTAMP,
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.OrderEventType.COMPLETE.value,
                tags=['long_waiting'],
            ),
        ),
    )
    # events for the second driver
    await entity_processor._event_provider.save_event(
        Events.ServiceManualEvent(
            timestamp=TIMESTAMP,
            entity_id=TST_UDID,
            event_id='300',
            value=99,
            mode=Events.ManualValueMode.ABSOLUTE,
            operation=Events.ServiceManualEventType.SET_ACTIVITY_VALUE,
            reason='Tst reason_commit_unique_driver_changes',
            descriptor=Events.EventTypeDescriptor(
                Events.ServiceManualEventType.SET_ACTIVITY_VALUE.value,
            ),
        ),
    )
    # this event should not be captured in "processed" because it's too old
    await entity_processor._event_provider.save_event(
        Events.BlockingEvent(
            event_id='200',
            entity_id=TST_UDID,
            timestamp=TWO_DAYS_BEFORE,
            zone='america',
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.BlockingEventName.UNBLOCK.value,
            ),
        ),
    )

    await run_dms_processing(stq3_context, 1)
    assert not tags_patch.tags_upload.times_called  # no rules apply here
    assert not any(
        values
        for cls, values in cached_journals[-1].actions.items()
        if cls != RuleType.COMPLETE_SCORES
    )
    await run_dms_processing(stq3_context, 3)
    assert (
        tags_patch.tags_upload.times_called == 1
    )  # only one rule should apply
    for config, actions in cached_journals[-1].actions.items():
        if config == RuleType.ACTIVITY:
            assert len(actions) == 1
            assert actions[0].action.result == 6
        elif config != RuleType.COMPLETE_SCORES:
            assert not actions


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.now(TEN_SEC_AFTER.isoformat())
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAGGING_RULES=True)
@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'name': 'tagging_1',
                'events': [
                    {'topic': 'order'},
                    {'topic': 'secret', 'name': 'report'},
                ],
                'actions': [
                    {'action': [{'type': 'tagging', 'tags': [{'name': 'A'}]}]},
                ],
            },
        ],
    },
    LOYALTY={
        'default': [
            {
                'name': 'tagging_1',
                'events': [{'topic': 'order', 'name': 'complete'}],
                'actions': [{'action': [{'type': 'loyalty', 'value': 33}]}],
            },
        ],
    },
)
async def test_processing_with_action_journal(
        stq3_context,
        dms_mockserver,
        tags_service_mock,
        cached_journals,
        event_provider,
):
    tags_service_mock()
    app = stq3_context
    dms_mockserver.init_activity({TST_UDID: 93})

    # it's empty at the start
    assert not cached_journals

    await run_dms_processing(app, 100)
    # no events, still empty
    assert not cached_journals

    await event_provider.save_event(
        event=Events.OrderEvent(
            event_id='1',
            timestamp=TIMESTAMP,
            entity_id=TST_UDID,
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.OrderEventType.COMPLETE.value,
            ),
        ),
    )
    await run_dms_processing(app, 100)
    assert len(cached_journals) == 1
    assert len(cached_journals[-1].actions) == 17
    # order event triggers loyalty and activity increments, and tagging/push
    for config, actions in cached_journals[-1].actions.items():
        if config == RuleType.ACTIVITY:
            assert len(actions) == 1
            assert actions[0].action.result == 0
        elif config == RuleType.LOYALTY:
            assert len(actions) == 1
            assert actions[0].action.result == 33
        elif config == RuleType.TAGGING:
            assert len(actions) == 1
        elif config == RuleType.PUSH:
            assert not actions

    await event_provider.save_event(
        event=Events.UnifiedEvent(
            event_id='2',
            timestamp=TIMESTAMP,
            entity_id=TST_UDID,
            descriptor=Events.EventTypeDescriptor(event_name='report'),
            event_type='secret',
        ),
    )

    await run_dms_processing(app, 100)
    assert len(cached_journals) == 2

    assert len(cached_journals[-1].actions) == 17
    # only tagging is triggered because it's not an order-event
    for config, actions in cached_journals[-1].actions.items():
        if config == RuleType.TAGGING:
            assert len(actions) == 1
        elif config != RuleType.COMPLETE_SCORES:
            assert not actions


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            {
                'actions': [
                    {
                        'action': [{'type': 'loyalty', 'value': 44}],
                        'tags': '\'rider::vasya\'',
                    },
                    {
                        'action': [{'type': 'loyalty', 'value': 5}],
                        'tags': (
                            '(\'tags::selfemployed\' OR '
                            '\'tags::individual_entrepreneur\') '
                            'AND \'event::tariff_business\''
                        ),
                    },
                    {
                        'action': [{'type': 'loyalty', 'value': 4}],
                        'tags': '\'event::tariff_business\'',
                    },
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'LoyaltyAccrual7',
            },
        ],
    },
)
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAG_FETCHER=True)
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.parametrize(
    'rider_tags, expected_loyalty', [(['vasya'], 44), (None, 5)],
)
async def test_loyalty_case(
        stq3_context,
        dms_mockserver,
        rider_tags,
        expected_loyalty,
        tags_service_mock,
        entity_processor,
        cached_journals,
):
    tags_service_mock(tags=['individual_entrepreneur'])

    await entity_processor._event_provider.save_event(
        event=Events.OrderEvent(
            event_id='123',
            timestamp=TIMESTAMP,
            entity_id=TST_UDID,
            zone=TEST_ZONE,
            descriptor=Events.EventTypeDescriptor(event_name='complete'),
            tariff_class='business',
            rider_tags=rider_tags,
        ),
    )

    await run_dms_processing(stq3_context, 1)
    loyalty = cached_journals[0].actions[RuleType.LOYALTY]
    assert len(loyalty) == 1
    assert loyalty[0].action.result == expected_loyalty


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            # should not fire if tags from event, because only one event
            # includes the tag
            {
                'actions': [{'action': [{'type': 'loyalty', 'value': 10}]}],
                'events': [
                    {
                        'name': 'complete',
                        'topic': 'order',
                        'tags': '(\'tags::individual_entrepreneur\') ',
                    },
                ],
                'events_to_trigger_cnt': 2,
                'name': 'LoyaltyAccrual6',
            },
            {
                'actions': [
                    {
                        'action': [{'type': 'loyalty', 'value': 10}],
                        'tags': '\'tags::selfemployed\'',
                    },
                    {
                        'action': [{'type': 'loyalty', 'value': 5}],
                        'tags': '\'tags::individual_entrepreneur\'',
                    },
                ],
                'events': [
                    {
                        'name': 'complete',
                        'topic': 'order',
                        'tags': (
                            '(\'tags::selfemployed\' OR '
                            '\'tags::individual_entrepreneur\') '
                            'AND \'event::tariff_business\' '
                            'AND \'rider::vasya\''
                        ),
                    },
                ],
                'events_to_trigger_cnt': 2,
                'name': 'LoyaltyAccrual7',
            },
        ],
    },
)
@pytest.mark.config(
    DRIVER_METRICS_ENABLE_TAG_FETCHER=True,
    DRIVER_METRICS_USE_TAGS_FROM_EVENTS=True,
)
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_tags_from_events(
        tags_service_mock,
        dms_mockserver,
        entity_processor,
        stq3_context,
        cached_journals,
):
    tags_service_mock(tags=['individual_entrepreneur'])

    await entity_processor._event_provider.save_event(
        event=Events.OrderEvent(
            event_id='123',
            timestamp=TIMESTAMP,
            entity_id=TST_UDID,
            zone=TEST_ZONE,
            descriptor=Events.EventTypeDescriptor(
                event_name='complete', tags=['tariff_business'],
            ),
            tariff_class='business',
            rider_tags=['vasya'],
        ),
    )

    await run_dms_processing(stq3_context, 1)
    loyalty = cached_journals[0].actions[RuleType.LOYALTY]
    assert len(loyalty) == 0

    await entity_processor._event_provider.save_event(
        event=Events.OrderEvent(
            event_id='1234',
            timestamp=TIMESTAMP,
            entity_id=TST_UDID,
            zone=TEST_ZONE,
            descriptor=Events.EventTypeDescriptor(
                event_name='complete', tags=['tariff_business'],
            ),
            tariff_class='business',
            rider_tags=['vasya'],
            driver_tags=['selfemployed'],
        ),
    )
    await run_dms_processing(stq3_context, 1)
    loyalty = cached_journals[1].actions[RuleType.LOYALTY]
    assert len(loyalty) == 1
    assert loyalty[0].action.result == 5


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.now(TEN_SEC_AFTER.isoformat())
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAGGING_RULES=True)
@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'id': 'i_am_id',
                'name': 'some_rule',
                'zone': 'default',
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 2,
                'type': 'tagging',
                'events': [
                    {'topic': 'reposition'},
                    {'topic': 'order', 'tags': '\'event::wow\''},
                ],
                'actions': [
                    {
                        'action': [
                            {'type': 'tagging', 'tags': [{'name': 'tag1'}]},
                        ],
                    },
                ],
            },
        ],
        'spb': [
            {
                'id': 'i_am_id',
                'name': 'some_rule',
                'zone': 'spb',
                'events_period_sec': 3600,
                'type': 'tagging',
                'events': [{'topic': 'reposition'}],
                'actions': [
                    {
                        'action': [
                            {'type': 'tagging', 'tags': [{'name': 'tag4'}]},
                        ],
                    },
                ],
            },
            {
                'id': 'i_am_id',
                'name': 'best rule',
                'zone': 'spb',
                'type': 'tagging',
                'events': [{'topic': 'reposition', 'tags': '\'event::wow\''}],
                'actions': [
                    {
                        'action': [
                            {'type': 'tagging', 'tags': [{'name': 'tag7'}]},
                        ],
                    },
                ],
            },
        ],
    },
)
async def test_processing_scenario_new_configs(
        stq3_context,
        dms_mockserver,
        tags_service_mock,
        cached_journals,
        entity_processor,
):
    dms_mockserver.init_activity({BAD_DRIVER_ID: 10, TST_UDID: 93})

    tags_patch = tags_service_mock()
    # events for the first driver
    await entity_processor._event_provider.save_event(
        Events.UnifiedEvent(
            event_id='400',
            entity_id=BAD_DRIVER_ID,
            timestamp=TEN_SEC_AFTER,
            event_type='reposition',
            zone='spb',
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.OrderEventType.COMPLETE.value, tags=['wow'],
            ),
        ),
    )

    await entity_processor._event_provider.save_event(
        Events.OrderEvent(
            event_id='88005',
            entity_id=BAD_DRIVER_ID,
            zone=None,
            timestamp=TIMESTAMP,
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.OrderEventType.COMPLETE.value, tags=['wow'],
            ),
        ),
    )

    # events for the second driver
    await entity_processor._event_provider.save_event(
        Events.ServiceManualEvent(
            timestamp=TIMESTAMP,
            entity_id=TST_UDID,
            event_id='300',
            value=99,
            mode=Events.ManualValueMode.ABSOLUTE,
            operation=Events.ServiceManualEventType.SET_ACTIVITY_VALUE,
            reason='Tst reason_commit_unique_driver_changes',
            descriptor=Events.EventTypeDescriptor(
                Events.ServiceManualEventType.SET_ACTIVITY_VALUE.value,
            ),
        ),
    )
    # this event should not be captured in "processed" because it's too old
    await entity_processor._event_provider.save_event(
        Events.BlockingEvent(
            event_id='200',
            entity_id=TST_UDID,
            timestamp=TWO_DAYS_BEFORE,
            zone='america',
            descriptor=Events.EventTypeDescriptor(
                event_name=Events.BlockingEventName.UNBLOCK.value,
            ),
        ),
    )

    await run_dms_processing(stq3_context, 1)
    assert not tags_patch.tags_upload.times_called  # no rules apply here
    assert not any(
        values
        for cls, values in cached_journals[-1].actions.items()
        if cls != RuleType.COMPLETE_SCORES
    )

    await run_dms_processing(stq3_context, 3)
    assert tags_patch.tags_upload.times_called == 2
    for config, actions in cached_journals[-1].actions.items():
        if config == RuleType.ACTIVITY:
            assert len(actions) == 1
            assert actions[0].action.result == 6
        elif config != RuleType.COMPLETE_SCORES:
            assert not actions


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.parametrize('unblocking_event', (True, False))
@pytest.mark.parametrize('blocked', ('activity', 'actions', False))
@pytest.mark.parametrize('activity', (10, 30, 50, 80))
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_process_unblocking_event(
        stq3_context,
        dms_mockserver,
        fake_event_provider,
        unblocking_event,
        blocked,
        activity,
        entity_processor,
):
    """
    expected behaviour is:
    if driver is not blocked:
        activity < blocking threshold => increase activity (amnesty)
        activity >= blocking threshold => process normally
    """

    app = stq3_context

    event = Events.UnifiedEvent(
        event_id=TST_EVENT_REF_ID, timestamp=TIMESTAMP, entity_id=TST_UDID,
    )
    if unblocking_event:
        event = Events.BlockingEvent(
            event_id=TST_EVENT_REF_ID, timestamp=TIMESTAMP, entity_id=TST_UDID,
        )

    await entity_processor._event_provider.save_event(event)

    driver = await DriverInfo.make(
        app, TST_UDID, fake_event_provider([]), TIMESTAMP,
    )
    assert not driver.current_blocking
    dms_mockserver.init_activity({TST_UDID: activity})

    if blocked:
        blocking = Blocking(
            until=TWO_DAYS_BEFORE,
            type=BlockingType(blocked),
            reason='reason',
            rule_name='rule_name',
        )
        await driver.apply_blocking(
            app,
            blocking,
            rule_descr='test',
            beginning_time=TWO_DAYS_BEFORE,
            event=Events.UnifiedEvent(
                event_id=TST_EVENT_REF_ID,
                timestamp=TIMESTAMP,
                entity_id=TST_UDID,
            ),
        )
    driver = await DriverInfo.make(
        app, TST_UDID, fake_event_provider([]), TIMESTAMP,
    )

    assert driver.activity == activity
    assert bool(driver.current_blocking) == bool(blocked)
    if blocked:
        assert driver.current_blocking[0].type == BlockingType(blocked)

    entity_processor._context = driver
    entity_processor._event = event
    driver.update_event(event)

    await run_dms_processing(app, 1)
    driver = await DriverInfo.make(
        app, TST_UDID, fake_event_provider([]), TIMESTAMP,
    )

    expected_new_activity = activity

    if blocked != 'activity' and activity < ACTIVITY_BLOCKING_THRESHOLD:
        expected_new_activity = ACTIVITY_AMNESTY_DEFAULT

    assert dms_mockserver.event_complete.times_called == 1
    complete_call = dms_mockserver.event_complete.next_call()['request'].json

    activity_change = expected_new_activity - activity
    if activity_change:
        assert complete_call.get('activity')
        assert complete_call['activity']['increment'] == activity_change
        assert (
            complete_call['activity']['value_to_set'] == expected_new_activity
        )
    else:
        assert not complete_call.get('activity', {})

    assert driver.activity == expected_new_activity

    driver = await DriverInfo.make(
        app, TST_UDID, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.activity == expected_new_activity


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_no_activity_for_action_unblock(
        stq3_context, dms_mockserver, fake_event_provider,
):

    app = stq3_context
    dms_mockserver.init_activity({BAD_DRIVER_ID: 10})

    driver = await DriverInfo.make(
        app, BAD_DRIVER_ID, fake_event_provider([]), TIMESTAMP,
    )

    action_blocking = Blocking(
        until=TWO_DAYS_BEFORE,
        type=BlockingType.BY_ACTIONS,
        reason='bad_actions',
        rule_name='action_rule',
    )
    activity_blocking = Blocking(
        until=TEN_SEC_AFTER,
        type=BlockingType.BY_ACTIVITY,
        reason='low_activity',
        rule_name='activity_rule',
    )
    for blocking in action_blocking, activity_blocking:
        await driver.apply_blocking(
            app,
            blocking,
            rule_descr='test',
            beginning_time=TWO_DAYS_BEFORE,
            event=Events.UnifiedEvent(
                event_id=TST_EVENT_REF_ID,
                timestamp=TIMESTAMP,
                entity_id=BAD_DRIVER_ID,
            ),
        )

    event = Events.BlockingEvent(
        event_id=TST_EVENT_REF_ID,
        timestamp=TIMESTAMP,
        entity_id=BAD_DRIVER_ID,
        blocking_type=BlockingType.BY_ACTIONS,
    )

    event_provider = DmsEventsProvider(app)

    await event_provider.save_event(event)

    starting_activity = driver.activity
    assert starting_activity <= 10

    driver = await DriverInfo.make(
        app, BAD_DRIVER_ID, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.activity == starting_activity
    assert len(driver.current_blocking) == 2
    assert driver.current_blocking[0].type == BlockingType.BY_ACTIVITY
    assert driver.current_blocking[0].until > TIMESTAMP
    assert driver.current_blocking[1].type == BlockingType.BY_ACTIONS
    assert driver.current_blocking[1].until < TIMESTAMP

    await run_dms_processing(app, 1)

    driver = await DriverInfo.make(
        app, BAD_DRIVER_ID, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.activity == starting_activity
    assert len(driver.current_blocking) == 2
    assert driver.current_blocking[0].type == BlockingType.BY_ACTIVITY
    assert driver.current_blocking[0].until > TIMESTAMP
    assert driver.current_blocking[1].type == BlockingType.BY_ACTIONS
    assert driver.current_blocking[1].until < TIMESTAMP


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(DRIVER_METRICS_STOP_ACTIVITY_BLOCKING=True)
async def test_disable_activity_blocking_config(
        stq3_context, dms_mockserver, fake_event_provider, patch,
):
    app = stq3_context
    event = Events.ServiceManualEvent(
        timestamp=TIMESTAMP,
        entity_id=TST_UDID,
        event_id='asd',
        value=5,
        mode=Events.ManualValueMode.ABSOLUTE,
        reason='block driver',
    )

    event_provider = DmsEventsProvider(app)

    await event_provider.save_event(event)

    driver = await DriverInfo.make(
        app, TST_UDID, fake_event_provider([]), TIMESTAMP,
    )

    assert not driver.current_blocking

    @patch('taxi_driver_metrics.common.models.blocking_journal.save_to_db')
    async def save_blocking(*args, **kwargs):
        return

    await run_dms_processing(app, 1)

    assert not save_blocking.calls


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(
    DRIVER_METRICS_CONFIG_SERVICE_USAGE_SETTINGS={
        '__default__': ['stq_callback', 'loyalty'],
    },
)
@pytest.mark.rules_config(
    STQ_CALLBACK={
        'default': [
            {
                'name': 'some_rule',
                'events': [{'topic': 'order', 'name': 'complete'}],
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 1,
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'stq_callback',
                                'queues': [
                                    {
                                        'name': 'driver_metrics_client',
                                        'delay': 1,
                                        'data': [
                                            {
                                                'name': 'order_id',
                                                'expr': 'event.order_id',
                                            },
                                        ],
                                        'default_data_policy': 'update',
                                    },
                                    {
                                        'name': 'driver_metrics_client',
                                        'delay': 1,
                                        'data': [
                                            {
                                                'name': 'order_id',
                                                'expr': 'event.order_id',
                                            },
                                        ],
                                        'default_data_policy': 'replace',
                                    },
                                    {
                                        'name': 'driver_metrics_processing',
                                        'data': [
                                            {
                                                'name': 'extra_data',
                                                'expr': (
                                                    'event.extra_data_json'
                                                ),
                                            },
                                            {
                                                'name': 'secret_key',
                                                'expr': 'event.secret_key',
                                            },
                                        ],
                                    },
                                    {'name': 'cool_queue'},
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                'name': 'another_rule',
                'events': [{'topic': 'order', 'name': 'complete'}],
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 1,
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'stq_callback',
                                'default_data': [],
                                'queues': [
                                    {
                                        'name': 'kwargs_only_queue',
                                        'kwargs': [
                                            {
                                                'name': 'extra_data',
                                                'expr': (
                                                    'event.extra_data_json'
                                                ),
                                            },
                                            {
                                                'name': 'order_id',
                                                'expr': 'event.order_id',
                                                'required': True,
                                            },
                                            {
                                                'name': 'some_name',
                                                'expr': (
                                                    'f\'{event.event_id}_'
                                                    'some_string\''
                                                ),
                                                'required': True,
                                            },
                                            {
                                                'name': (
                                                    'nested_type.from.'
                                                    'descriptor.type'
                                                ),
                                                'expr': (
                                                    'event.extra_data_json['
                                                    '\'descriptor\'][\'type\']'
                                                ),
                                            },
                                            {
                                                'name': (
                                                    'nested_type.from.'
                                                    'descriptor.entity_id'
                                                ),
                                                'expr': 'event.entity_id',
                                            },
                                            {
                                                'name': (
                                                    'nested_type.from.order_id'
                                                ),
                                                'expr': 'event.order_id',
                                            },
                                        ],
                                    },
                                    {
                                        'name': (
                                            'kwargs_only_queue_'
                                            'without_required'
                                        ),
                                        'kwargs': [
                                            {
                                                'name': 'extra_data',
                                                'expr': (
                                                    'event.extra_data_json'
                                                ),
                                            },
                                            {
                                                'name': 'now_existing_key',
                                                'expr': (
                                                    'event.now_existing_key'
                                                ),
                                                'required': True,
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
async def test_callback_action(
        stq3_context,
        dms_mockserver,
        fake_event_provider,
        entity_processor,
        stq,
):
    app = stq3_context

    event = Events.OrderEvent(
        order_id='123',
        timestamp=TIMESTAMP,
        entity_id=TST_UDID,
        event_id='asd',
        activity_value=4,
        tariff_class='awesome',
        surge_value=1,
        descriptor=Events.EventTypeDescriptor(
            event_name=Events.OrderEventType.COMPLETE.value, tags=['wow'],
        ),
        additional_data={},
    )
    await entity_processor._event_provider.save_event(event)

    await run_dms_processing(app, 1)
    assert stq.driver_metrics_client.times_called == 2
    assert stq.driver_metrics_processing.times_called == 1

    expected_res = dataclasses.asdict(event)
    #  dms does it by itself
    expected_res['event_id'] = '1'
    expected_res['modified'] = {'activity': 100}
    expected_res.pop('timestamp')
    expected_res.pop('stable_random')
    for _ in range(2):
        task = stq.driver_metrics_client.next_call()
        #  strange datetime format
        #  doesnt matter
        task['args'][0].pop('timestamp', None)
        task['args'][0].pop('stable_random', None)
        expected_res['order_id'] = '123'
        kwargs = task.pop('kwargs', {})
        assert task.pop('eta')
        assert 'log_extra' in kwargs
        assert task == {
            'id': '1',
            'args': [expected_res],
            'queue': 'driver_metrics_client',
        }
        #  second time we remove default data
        expected_res = {}

    task = stq.driver_metrics_processing.next_call()
    kwargs = task.pop('kwargs', {})
    assert 'log_extra' in kwargs
    assert task == {
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'id': '1',
        'args': [{'extra_data': event.extra_data_json, 'secret_key': None}],
        'queue': 'driver_metrics_processing',
    }
    #  if queue is not specified in stq_client
    #  put task manually
    assert stq['cool_queue'].times_called == 1
    assert stq['kwargs_only_queue'].times_called == 1
    task = stq['kwargs_only_queue'].next_call()
    assert task['kwargs'].pop('log_extra')
    assert task == {
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'id': '1',
        'args': [],
        'kwargs': {
            'some_name': '1_some_string',
            'order_id': '123',
            'extra_data': event.extra_data_json,
            'nested_type': {
                'from': {
                    'descriptor': {
                        'entity_id': TST_UDID,
                        'type': event.extra_data_json['descriptor']['type'],
                    },
                    'order_id': event.order_id,
                },
            },
        },
        'queue': 'kwargs_only_queue',
    }
    assert stq['kwargs_only_queue_without_required'].times_called == 0


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.parametrize('auth_error', [True, False])
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(
    DRIVER_METRICS_NEW_STQ_CALLBACK_RULES={
        '__default__': [
            {
                'name': 'some_rule',
                'events': [{'topic': 'order'}],
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 1,
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'stq_callback',
                                'queues': [{'name': 'cool_queue'}],
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
async def test_callback_action_no_queue(
        stq3_context, dms_mockserver, entity_processor, patch, auth_error,
):
    @patch('taxi.clients.stq_agent.StqAgentClient._make_request')
    def _patch_stq_agent(*args, data, **kwargs):
        assert data
        body = json.loads(data)
        method = args[1].split('/')
        queue_name = (
            body['queue_name'] if method[2] == 'reschedule' else method[3]
        )
        assert queue_name == 'cool_queue'
        if auth_error:
            raise stq_agent.RequestAuthError('TVM broken ololo')
        #  queue doesnt exist
        raise stq_agent.RequestError('404 queue not found')

    app = stq3_context
    event = Events.OrderEvent(
        order_id='123',
        timestamp=TIMESTAMP,
        entity_id=TST_UDID,
        event_id='asd',
        activity_value=4,
        tariff_class='awesome',
        surge_value=1,
        descriptor=Events.EventTypeDescriptor(
            event_name=Events.OrderEventType.COMPLETE.value, tags=['wow'],
        ),
    )
    await entity_processor._event_provider.save_event(event)
    try:
        await run_dms_processing(app, 1)
    except stq_agent.RequestAuthError:
        assert auth_error


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.config(
    DRIVER_METRICS_CUSTOM_ACTIVITY_RULES={
        '__default__': [
            {
                'name': 'some_rule',
                'events': [{'topic': 'reposition'}],
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 1,
                'actions': [{'action': [{'type': 'activity', 'value': 2}]}],
            },
        ],
    },
)
async def test_custom_activity(
        stq3_context, dms_mockserver, entity_processor, cached_journals,
):

    app = stq3_context
    event = Events.UnifiedEvent(
        order_id='123',
        timestamp=TIMESTAMP,
        entity_id=TST_UDID,
        event_id='asd',
        event_type='reposition',
    )
    await entity_processor._event_provider.save_event(event)

    await run_dms_processing(app, 1)

    assert cached_journals[0].actions[RuleType.ACTIVITY][-1].action_result == 2


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(dm_blocking_journal='airport')
async def test_missing_driver(
        entity_processor, dms_mockserver, mongo, stq3_context,
):
    with pytest.raises(DriverDataError):
        await DriverInfo.make(app=stq3_context, unique_driver_id=BAD_DRIVER_ID)

    driver = DriverInfo(udid=BAD_DRIVER_ID)
    await driver.fetch_blocking_info(stq3_context, {})
    assert driver.current_blocking
    await entity_processor.process_unblocking(BAD_DRIVER_ID)

    assert not entity_processor.driver.current_blocking
