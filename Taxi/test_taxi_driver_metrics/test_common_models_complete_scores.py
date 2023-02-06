#  pylint: disable=protected-access

import datetime

from bson import ObjectId
import pytest

from taxi.clients.helpers import base as api_utils

from taxi_driver_metrics.common.models import Blocking
from taxi_driver_metrics.common.models import BlockingType
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import run_dms_processing
from taxi_driver_metrics.common.models.rules import rule_utils


TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)

HANDLER_PATH = 'v2/lookup_info/'
DRIVER_UDID = '5b05621ee6c22ea2654849c9'
TST_ZONE = 'burgund'
TST_DESTINATION = 'moon'
TST_ORDER_ID = 'dlsjfslkfj'
TST_ALIAS_ID = 'tstalias'
WRONG_APP_VERSION = '9.92.7707'


class Const:
    TARIFF_CLASS_EXPRESS = 'express'
    TARIFF_CLASS_ECONOM = 'econom'
    TARIFF_CLASS_BUSINESS = 'business'
    TARIFF_CLASS_COMFORTPLUS = 'comfortplus'
    TARIFF_CLASS_VIP = 'vip'
    TARIFF_CLASS_MINIVAN = 'minivan'
    TARIFF_CLASS_UNIVERSAL = 'universal'
    TARIFF_CLASS_POOL = 'pool'


def get_exp_template(tags=None):
    return dict(
        consumer='driver-metrics',
        experiment_name='replace_activity_with_priority',
        args=[
            {
                'name': 'version',
                'type': 'application_version',
                'value': '9.92.7707',
            },
            {
                'name': 'unique_driver_id',
                'type': 'string',
                'value': DRIVER_UDID,
            },
            {'name': 'geoarea', 'type': 'string', 'value': TST_ZONE},
            {'name': 'driver_tags', 'type': 'set_string', 'value': tags or []},
            {'name': 'zones', 'type': 'set_string', 'value': [TST_ZONE]},
        ],
        value={'enabled': True},
    )


@pytest.mark.parametrize(
    'tst_request, tst_event, driver_tags, driver_tags_after, tst_cs_result',
    [
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': Const.TARIFF_CLASS_MINIVAN,
                },
            },
            Events.EventTypeDescriptor(Events.OrderEventType.COMPLETE.value),
            set(),
            set(),
            3,
            marks=pytest.mark.client_experiments3(**get_exp_template()),
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': Const.TARIFF_CLASS_MINIVAN,
                },
            },
            Events.EventTypeDescriptor(
                Events.OrderEventType.OFFER_TIMEOUT.value,
            ),
            set(),
            {'good'},
            -3,
            marks=pytest.mark.client_experiments3(**get_exp_template()),
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': Const.TARIFF_CLASS_MINIVAN,
                },
            },
            Events.EventTypeDescriptor(
                Events.OrderEventType.OFFER_TIMEOUT.value,
                tags=['chained_order'],
            ),
            {'good'},
            set(),
            -1,
            marks=pytest.mark.client_experiments3(
                **get_exp_template(['good']),
            ),
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': Const.TARIFF_CLASS_MINIVAN,
                },
            },
            Events.EventTypeDescriptor(Events.OrderEventType.COMPLETE.value),
            {'zero'},
            set(),
            0,
            marks=pytest.mark.client_experiments3(
                **get_exp_template(['zero']),
            ),
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 0}},
            'letter_events': {'c': {'activity': 0}},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 20,
        'predict_complete_scores': True,
        'tags': {
            'order': {
                'auto_reorder': ['long_waiting'],
                'offer_timeout': ['chained_order'],
                'park_cancel': ['long_waiting'],
                'park_fail': ['long_waiting'],
            },
        },
    },
    DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
    DRIVER_METRICS_COMPLETE_SCORES_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [{'type': 'complete_scores', 'value': 1}],
                        'tags': '\'tags::good\'',
                    },
                    {
                        'action': [{'type': 'complete_scores', 'value': 0}],
                        'tags': '\'tags::zero\'',
                    },
                    {
                        'action': [{'type': 'complete_scores', 'value': 2}],
                        'tags': '\'tags::bad\'',
                    },
                    {'action': [{'type': 'complete_scores', 'value': 3}]},
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'CompleteScores',
            },
            {
                'actions': [
                    {
                        'action': [{'type': 'complete_scores', 'level': -1}],
                        'tags': '\'event::chained_order\'',
                    },
                    {'action': [{'type': 'complete_scores', 'level': -2}]},
                ],
                'events': [{'name': 'offer_timeout', 'topic': 'order'}],
                'name': 'CompleteScoresReject',
            },
        ],
    },
    DRIVER_METRICS_ENABLE_COMPLETE_SCORES=True,
    DRIVER_METRICS_CONFIG_SERVICE_USAGE_SETTINGS={
        '__default__': ['blocking', 'loyalty', 'tagging'],
    },
    ADVERSE_ZONES={
        TST_ZONE: {
            TST_DESTINATION: {'show_destination': True, 'skip_fields': ''},
        },
    },
)
async def test_complete_scores_prediction(
        stq3_context,
        web_app_client,
        cached_drivers,
        patch,
        entity_processor,
        mongo,
        dms_mockserver,
        tst_request,
        tst_event,
        driver_tags,
        driver_tags_after,
        tst_cs_result,
):
    # pylint: disable=protected-access
    @patch(
        'taxi_driver_metrics.common.utils._tags_manager'
        '.TagsManager.fetch_service_tags',
    )
    async def _fetch_tags(*_args, **_kwargs):
        return driver_tags_after

    await mongo.unique_drivers.insert_one(
        {
            '_id': ObjectId(DRIVER_UDID),
            'blocking_by_activity': {
                'blocked_until': datetime.datetime(2016, 5, 3, 0, 0),
                'counter': 3,
                'is_blocked': True,
                'timestamp': None,
                'reason': 'bad_blocking_reason',
                'type': 'activity',
            },
            'created': datetime.datetime(2016, 5, 6, 0, 0),
            'dp': 50,
            'exam_created': datetime.datetime(2016, 5, 2, 0, 0),
            'exam_score': 5,
            'fraud': False,
            'gl': {'business': 'ekb', 'econom': 'moscow'},
            'is_blacklisted': False,
            'licenses': [{'license': 'LFROM1'}, {'license': 'LFROM2'}],
            'mqc_passed': datetime.datetime(2016, 5, 3, 0, 0),
            'new_score': {'unified': {'total': 0.6}},
            'pe': {'business': -4, 'econom': 3},
            'pl': {'business': 2, 'econom': 1},
            'profiles': [{'driver_id': 'DFROM1'}, {'driver_id': 'DFROM2'}],
            'updated': datetime.datetime(2016, 5, 7, 0, 0),
        },
    )

    tst_request['candidate']['tags'] = list(driver_tags)

    response = await web_app_client.post(HANDLER_PATH, json=tst_request)
    assert response.status == 200
    response = await response.json()

    await entity_processor._event_provider.save_event(
        Events.OrderEvent(
            event_id='88005',
            entity_id=DRIVER_UDID,
            zone=None,
            timestamp=TIMESTAMP,
            descriptor=tst_event,
            order_id=TST_ORDER_ID,
            dispatch_id=response.get('ident'),
            calculate_priority=True,
        ),
    )
    res = []

    async for row in mongo.driver_metrics_predictions.find(
            {'udid': DRIVER_UDID},
    ):
        res.append(row)

    assert len(res) == 1

    await run_dms_processing(stq3_context, 1)
    assert len(cached_drivers) == 1
    assert cached_drivers[-1].complete_scores == tst_cs_result


@pytest.mark.parametrize(
    'start_score, complete_scores, scores_result, priority_result',
    [
        (
            1,
            1,
            {'increment': 1, 'value_to_set': 2},
            {'absolute_value': 1, 'increment': 0},
        ),
        (
            0,
            2,
            {'increment': 2, 'value_to_set': 2},
            {'absolute_value': 1, 'increment': 1},
        ),
        (
            10,
            -5,
            {'increment': -5, 'value_to_set': 5},
            {'absolute_value': 5, 'increment': -94},
        ),
        (
            11,
            -1,
            {'increment': -1, 'value_to_set': 7},
            {'absolute_value': 99, 'increment': 0},
        ),
        (
            13,
            5,
            {'increment': 5, 'value_to_set': 7},
            {'absolute_value': 99, 'increment': 0},
        ),
        (
            13,
            -1,
            {'increment': -1, 'value_to_set': 7},
            {'absolute_value': 99, 'increment': 0},
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 0}},
            'letter_events': {'c': {'activity': 0}},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 20,
        'predict_complete_scores': True,
        'tags': {
            'order': {
                'auto_reorder': ['long_waiting'],
                'offer_timeout': ['chained_order'],
                'park_cancel': ['long_waiting'],
                'park_fail': ['long_waiting'],
            },
        },
    },
    DRIVER_METRICS_COMPLETE_SCORES_SETTINGS={
        '__default__': {'initial_value': 0},
    },
    DRIVER_METRICS_ENABLE_COMPLETE_SCORES=True,
    DRIVER_METRICS_TAG_FOR_EXPERIMENT={
        'use_complete_scores_in_lookup': {
            'from': 0,
            'to': 100,
            'salt': '&%^^#@%',
        },
    },
)
@pytest.mark.filldb(unique_drivers='common')
async def test_processing_complete_scores(
        stq3_context,
        taxi_config,
        mockserver,
        patch,
        entity_processor,
        predict_activity,
        dms_mockserver,
        start_score,
        complete_scores,
        scores_result,
        priority_result,
):

    dispatch_id = await predict_activity(
        DRIVER_UDID, {'order_complete': complete_scores}, value='cs',
    )

    @patch(
        'taxi_driver_metrics.common.models.'
        '_processor.Processor.make_entity_processor',
    )
    def _(*args, **kwargs):
        return entity_processor

    @mockserver.json_handler('/driver-metrics-storage/v3/event/complete')
    def patch_complete(*args, **kwargs):
        return {}

    @mockserver.json_handler(
        '/driver-metrics-storage/v3/events/unprocessed/list',
    )
    async def _(*args, **kwargs):
        return {
            'items': [
                {
                    'ticket_id': 1,
                    'unique_driver_id': DRIVER_UDID,
                    'current_activity': 98,
                    'current_complete_score': {'value': start_score},
                    'events': [
                        {
                            'event_id': 4,
                            'created': api_utils.time_to_iso_string_or_none(
                                TIMESTAMP,
                            ),
                            'type': 'order',
                            'name': 'complete',
                            'descriptor': {'type': 'complete'},
                            'extra_data': {
                                'dispatch_id': dispatch_id,
                                'calculate_priority': True,
                                'replace_activity_with_priority': True,
                            },
                        },
                    ],
                },
            ],
        }

    await run_dms_processing(stq3_context, 100)
    res = patch_complete.next_call()['args'][0].json
    assert res['complete_score'] == scores_result
    assert res['priority'] == priority_result


@pytest.mark.parametrize(
    'replace_activity, calculate_priority',
    [(True, True), (False, True), (False, False)],
)
@pytest.mark.parametrize(
    'value, expected_blocked', [(-10, True), (-3, True), (-1, False)],
)
@pytest.mark.config(
    DRIVER_METRICS_COMPLETE_SCORES_SETTINGS={
        '__default__': {
            'initial_value': 0,
            'blocking_threshold': -3,
            'amnesty_value': 5,
            'blocking_durations': [10_000],
        },
    },
    DRIVER_METRICS_STOP_COMPLETE_SCORES_BLOCKING=False,
    DRIVER_METRICS_ENABLE_COMPLETE_SCORES=True,
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 0}},
            'letter_events': {'c': {'activity': 0}},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 20,
        'predict_complete_scores': True,
        'tags': {
            'order': {
                'auto_reorder': ['long_waiting'],
                'offer_timeout': ['chained_order'],
                'park_cancel': ['long_waiting'],
                'park_fail': ['long_waiting'],
            },
        },
    },
)
@pytest.mark.filldb(unique_drivers='common')
async def test_block_for_low_scores_and_unblocking(
        stq3_context,
        patch,
        cached_drivers,
        entity_processor,
        event_provider,
        predict_activity,
        dms_mockserver,
        value,
        expected_blocked,
        replace_activity,
        calculate_priority,
):
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
    async def _(app, blocking, *args, **kwargs):
        return True

    @patch('taxi_driver_metrics.common.models.blocking_journal.reset_blocking')
    async def reset_blocking(db, blocking, **kwargs):
        return

    dispatch_id = await predict_activity(
        udid=DRIVER_UDID, event_map={'order_complete': value}, value='cs',
    )

    await event_provider.save_event(
        Events.OrderEvent(
            descriptor=Events.EventTypeDescriptor(
                Events.OrderEventType.COMPLETE.value,
            ),
            dispatch_id=dispatch_id,
            timestamp=TIMESTAMP,
            zone=TST_ZONE,
            event_id='2',
            driver_id=DRIVER_UDID,
            entity_id=DRIVER_UDID,
            order_id='393j3393j939j393',
            use_priority=replace_activity,
            calculate_priority=calculate_priority,
        ),
    )

    await run_dms_processing(stq3_context, 1)

    driver = cached_drivers[-1]
    active_blocking = driver.get_active_blocking(
        BlockingType.BY_COMPLETE_SCORES,
    )
    #  block is expected only if exp enabled
    expected_blocked = expected_blocked and replace_activity

    assert active_blocking if expected_blocked else not active_blocking

    if not expected_blocked:
        return

    entity_processor._event_timestamp = (
        datetime.datetime.utcnow() + datetime.timedelta(days=300)
    )
    entity_processor._now = datetime.datetime.utcnow() + datetime.timedelta(
        days=300,
    )
    entity_processor._context = driver

    await entity_processor._process_unblocking()
    calls = reset_blocking.calls
    assert len(calls) == 1


@pytest.mark.config(
    DRIVER_METRICS_COMPLETE_SCORES_SETTINGS={
        '__default__': {
            'initial_value': -5,
            'blocking_threshold': -3,
            'amnesty_value': 5,
            'blocking_durations': [10_000],
            'use_complete_scores_in_lookup': True,
        },
    },
    DRIVER_METRICS_STOP_COMPLETE_SCORES_BLOCKING=False,
    DRIVER_METRICS_ENABLE_COMPLETE_SCORES=True,
    DRIVER_METRICS_TAG_FOR_EXPERIMENT={
        'use_complete_scores_in_lookup': {
            'from': 0,
            'to': 100,
            'salt': '&%^^#@%',
        },
    },
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 0}},
            'letter_events': {'c': {'activity': 0}},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 20,
        'predict_complete_scores': True,
        'tags': {
            'order': {
                'auto_reorder': ['long_waiting'],
                'offer_timeout': ['chained_order'],
                'park_cancel': ['long_waiting'],
                'park_fail': ['long_waiting'],
            },
        },
    },
)
@pytest.mark.parametrize(
    'event_type, event, amnesty, expected_to_unblock',
    [
        pytest.param(
            Events.OrderEvent,
            dict(
                descriptor=Events.EventTypeDescriptor(
                    Events.OrderEventType.COMPLETE.value,
                ),
                timestamp=TIMESTAMP,
                zone=TST_ZONE,
                event_id='2',
                driver_id=DRIVER_UDID,
                entity_id=DRIVER_UDID,
                order_id='393j3393j939j393',
                use_priority=True,
                calculate_priority=True,
            ),
            True,
            True,
            id='experiment_enabled_should_amnesty_and_unblock',
        ),
        pytest.param(
            Events.OrderEvent,
            dict(
                descriptor=Events.EventTypeDescriptor(
                    Events.OrderEventType.COMPLETE.value,
                ),
                timestamp=TIMESTAMP,
                zone=TST_ZONE,
                event_id='2',
                driver_id=DRIVER_UDID,
                entity_id=DRIVER_UDID,
                order_id='393j3393j939j393',
            ),
            False,
            True,
            id='experiment_disabled_shouldnt_amnesty_but_unblock',
        ),
        pytest.param(
            Events.ServiceManualEvent,
            dict(
                entity_id=DRIVER_UDID,
                operation=(
                    Events.ServiceManualEventType.SET_COMPLETE_SCORES_VALUE
                ),
                mode=Events.ManualValueMode.ADDITIVE,
                value=1,
                event_id='2',
                timestamp=TIMESTAMP,
            ),
            True,
            True,
            id='manual_event_should_always_amnesty_and_unblock',
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
async def test_amnesty_complete_scores(
        stq3_context,
        patch,
        cached_drivers,
        event_provider,
        predict_activity,
        dms_mockserver,
        event_type,
        event,
        amnesty,
        expected_to_unblock,
):
    @patch(
        'taxi_driver_metrics.common.models.ItemBasedEntityProcessor'
        '._fetch_full_driver_data',
    )
    async def _full_data(*args, **kwargs):
        return

    @patch('taxi_driver_metrics.common.models.blocking_journal.reset_blocking')
    async def _reset_blocking(db, blocking, **kwargs):
        assert blocking.type == BlockingType.BY_COMPLETE_SCORES

    @patch(
        'taxi_driver_metrics.common.models.DriverInfo.'
        '_commit_unique_driver_changes',
    )
    async def _fake_commit_changes(*args, **kwargs):
        return

    now_ = datetime.datetime.utcnow()

    blocking = Blocking(
        until=now_ - datetime.timedelta(days=100),
        type=BlockingType(BlockingType.BY_COMPLETE_SCORES),
        reason='initial',
        record_id=None,
        zone='bangladesh',
        rule_name='rule_name',
    )

    driver = await DriverInfo.make(
        stq3_context,
        unique_driver_id=DRIVER_UDID,
        event_fetcher=event_provider,
        driver_history_from_timestamp=TIMESTAMP,
        fetch_events_history=False,
        fetch_tags=True,
        fetch_blocking_history=True,
    )

    await rule_utils.process_single_blocking(
        stq3_context,
        blocking,
        driver,
        event=Events.OrderEvent(
            event_id='bad_event',
            timestamp=now_,
            entity_id=DRIVER_UDID,
            zone='bangladesh',
        ),
    )
    await driver._apply_blocking_state(stq3_context.mongo, blocking)
    if event_type == Events.OrderEvent:
        dispatch_id = await predict_activity(
            udid=DRIVER_UDID, event_map={'order_complete': 1}, value='cs',
        )
        event['dispatch_id'] = dispatch_id

    await event_provider.save_event(event_type(**event))
    await run_dms_processing(stq3_context, 1)
    assert len(cached_drivers) == 1
    expected_res = {
        'activity': {'increment': 100, 'value_to_set': 100},
        'event_id': 1,
        'ticket_id': 1,
        'unique_driver_id': '5b05621ee6c22ea2654849c9',
    }
    if amnesty:
        expected_res['complete_score'] = {'increment': 1, 'value_to_set': 1}
        expected_res['priority'] = {'absolute_value': 1, 'increment': 1}

    assert (
        dms_mockserver.event_complete.next_call()['request'].json
        == expected_res
    )

    assert (
        _reset_blocking.calls
        if expected_to_unblock
        else not _reset_blocking.calls
    )


@pytest.mark.parametrize(
    'start_score, complete_scores, scores_result, priority_result',
    [
        (
            1,
            1,
            {'increment': 1, 'value_to_set': 2},
            {'absolute_value': 1, 'increment': 0},
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 0}},
            'letter_events': {'c': {'activity': 0}},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 20,
        'predict_complete_scores': True,
        'tags': {
            'order': {
                'auto_reorder': ['long_waiting'],
                'offer_timeout': ['chained_order'],
                'park_cancel': ['long_waiting'],
                'park_fail': ['long_waiting'],
            },
        },
    },
    DRIVER_METRICS_COMPLETE_SCORES_SETTINGS={
        '__default__': {'initial_value': 0},
    },
    DRIVER_METRICS_ENABLE_COMPLETE_SCORES=True,
    DRIVER_METRICS_TAG_FOR_EXPERIMENT={
        'use_complete_scores_in_lookup': {
            'from': 0,
            'to': 100,
            'salt': '&%^^#@%',
        },
    },
    DRIVER_METRICS_CLIENT_EVENTS_PAYLOADS={
        'change_payloads': {
            'positive': {
                'text': {
                    'operation_type': 'tanker_key',
                    'key': 'TankerKey',
                    'args': [
                        {
                            'key': 'num',
                            'is_num': True,
                            'expr': {
                                'operation_type': 'expr',
                                'expr': 'event.modified["complete_scores"]',
                            },
                        },
                    ],
                },
                'text_color': '#FFFFFF',
                'text_style': 'style',
            },
        },
        'item_payloads': {
            'opportunity_to_skip_order': {
                'type': 'tip_detail',
                'horizontal_divider_type': 'top_gap',
                'left_tip': {
                    'icon': {'icon_type': 'gift', 'tint_color': '#FFFFFF'},
                    'background_color': '#FCB000',
                },
                'title': {'operation_type': 'tanker_key', 'key': 'TankerKey2'},
            },
        },
    },
    DRIVER_METRICS_CLIENT_EVENTS_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'client_events_callback',
                                'service': 'some_service',
                                'channel': {
                                    'operation_type': 'formatted_string',
                                    'value': 'contractor/{dbid_uuid}',
                                    'args': [
                                        {
                                            'key': 'dbid_uuid',
                                            'expr': {
                                                'operation_type': 'expr',
                                                'expr': 'event.dbid_uuid',
                                            },
                                        },
                                    ],
                                },
                                'event_name': 'order',
                                'event_id': {
                                    'operation_type': 'expr',
                                    'expr': 'event.order_alias_id',
                                },
                                'ttl': 600,
                                'payload': {
                                    'priority_value': (
                                        'change_payloads.positive'
                                    ),
                                    'items': [
                                        'item_payloads.'
                                        'opportunity_to_skip_order',
                                    ],
                                },
                            },
                        ],
                    },
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'CompleteScoresChange',
            },
        ],
    },
)
@pytest.mark.translations(
    taximeter_messages={
        'TankerKey': {'ru': 'Начислено {num}', 'en': 'Accrued {num}'},
        'TankerKey2': {'ru': 'Молодец', 'en': 'Well done'},
    },
)
@pytest.mark.filldb(unique_drivers='common')
async def test_notify_complete_scores(
        stq3_context,
        taxi_config,
        mockserver,
        patch,
        entity_processor,
        predict_activity,
        dms_mockserver,
        start_score,
        complete_scores,
        scores_result,
        priority_result,
):

    dispatch_id = await predict_activity(
        DRIVER_UDID, {'order_complete': complete_scores}, value='cs',
    )

    @patch(
        'taxi_driver_metrics.common.models.'
        '_processor.Processor.make_entity_processor',
    )
    def _(*args, **kwargs):
        return entity_processor

    @mockserver.json_handler('/driver-metrics-storage/v3/event/complete')
    def patch_complete(*args, **kwargs):
        return {}

    @mockserver.json_handler(
        '/driver-metrics-storage/v3/events/unprocessed/list',
    )
    async def _(*args, **kwargs):
        return {
            'items': [
                {
                    'ticket_id': 1,
                    'unique_driver_id': DRIVER_UDID,
                    'current_activity': 98,
                    'current_complete_score': {'value': start_score},
                    'events': [
                        {
                            'event_id': 4,
                            'park_driver_profile_id': 'dbid_uuid',
                            'created': api_utils.time_to_iso_string_or_none(
                                TIMESTAMP,
                            ),
                            'type': 'order',
                            'name': 'complete',
                            'order_alias': 'alias',
                            'descriptor': {'type': 'complete'},
                            'extra_data': {
                                'dispatch_id': dispatch_id,
                                'replace_activity_with_priority': True,
                                'calculate_priority': True,
                            },
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    async def _(*args, **kwargs):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid',
                    'data': {'locale': 'en'},
                },
            ],
        }

    @mockserver.json_handler('/client-events/push')
    async def patch_push(*args, **kwargs):
        return {'version': '1'}

    await run_dms_processing(stq3_context, 100)
    res = patch_complete.next_call()['args'][0].json
    assert res['complete_score'] == scores_result
    assert res['priority'] == priority_result
    res = patch_push.next_call()['args'][0].json

    assert res == {
        'service': 'some_service',
        'channel': 'contractor/dbid_uuid',
        'event': 'order',
        'event_id': 'alias',
        'ttl': 600,
        'payload': {
            'items': [
                {
                    'horizontal_divider_type': 'top_gap',
                    'left_tip': {
                        'background_color': '#FCB000',
                        'icon': {'icon_type': 'gift', 'tint_color': '#FFFFFF'},
                    },
                    'title': 'Well done',
                    'type': 'tip_detail',
                },
            ],
            'priority_value': {
                'text': 'Accrued 1',
                'text_color': '#FFFFFF',
                'text_style': 'style',
            },
        },
    }
