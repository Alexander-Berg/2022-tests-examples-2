import datetime

from bson import ObjectId
import pytest

from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import run_dms_processing


TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)

HANDLER_PATH = 'v2/lookup_info/'
DRIVER_UDID = '5b05621ee6c22ea2654849c9'
TST_ZONE = 'burgund'
TST_DESTINATION = 'moon'
TST_ORDER_ID = 'dlsjfslkfj'
TST_ALIAS_ID = 'tstalias'


def make_priority_answer(event_tags=None, prediction=None):
    return {
        'distance_type': 'long',
        'event_tags': event_tags or [
            'replace_activity_with_priority',
            'dispatch_long',
        ],
        'prediction': {
            'blocking': {'duration_sec': 60, 'threshold': -3},
            'scores_to_next_level': 1,
            'type': 'priority',
            'value': 0,
            'value_changes': prediction or {'c': 5, 's': -2, 't': -3},
        },
    }


class Const:
    TARIFF_CLASS_EXPRESS = 'express'
    TARIFF_CLASS_ECONOM = 'econom'
    TARIFF_CLASS_BUSINESS = 'business'
    TARIFF_CLASS_COMFORTPLUS = 'comfortplus'
    TARIFF_CLASS_VIP = 'vip'
    TARIFF_CLASS_MINIVAN = 'minivan'
    TARIFF_CLASS_UNIVERSAL = 'universal'
    TARIFF_CLASS_POOL = 'pool'


def get_exp_template(tags=None, exp_name=None, value=None):
    return dict(
        consumer='driver-metrics',
        experiment_name=exp_name or 'replace_activity_with_priority',
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
            {
                'name': 'zones',
                'type': 'set_string',
                'value': ['root', 'russia', TST_ZONE],
            },
        ],
        value=value or {'enabled': True},
    )


@pytest.mark.geo_nodes(
    [
        {
            'name': 'root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': [TST_ZONE],
        },
        {
            'name': 'russia',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'parent_name': 'root',
            'node_type': 'node',
            'tariff_zones': [TST_ZONE],
        },
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'actions': [{'action': [{'type': 'activity', 'value': -1}]}],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'ActivityTrip',
            },
        ],
    },
    ADVERSE_ZONES={
        TST_ZONE: {
            TST_DESTINATION: {'show_destination': True, 'skip_fields': ''},
        },
    },
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {
                'order_complete': {'activity': 0, 'complete_scores': 2},
            },
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
        '__default__': {
            'amnesty_value': 0,
            'blocking_durations': [60, 180, 600],
            'blocking_threshold': -5,
            'initial_value': 0,
        },
    },
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
)
@pytest.mark.client_experiments3(**get_exp_template())
@pytest.mark.parametrize(
    'tst_request, tst_event, driver_tags, driver_tags_after, '
    'tst_cs_result, expected_res, exp_matched, double_prediction',
    [
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7707)',
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': Const.TARIFF_CLASS_MINIVAN,
                    'source_object_type': 'аэропорт',
                    'last_dest_object_type': 'организация',
                },
            },
            Events.EventTypeDescriptor(Events.OrderEventType.COMPLETE.value),
            set(),
            set(),
            3,
            make_priority_answer(
                event_tags=[
                    'source_airport',
                    'replace_activity_with_priority',
                    'dispatch_long',
                ],
            ),
            True,
            False,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7707)',
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
            make_priority_answer(),
            True,
            False,
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7707)',
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
            make_priority_answer(prediction={'c': 1, 's': -2, 't': -3}),
            True,
            False,
            marks=pytest.mark.client_experiments3(
                **get_exp_template(['good']),
            ),
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7707)',
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
            make_priority_answer(prediction={'s': -2, 't': -3}),
            True,
            False,
            marks=pytest.mark.client_experiments3(
                **get_exp_template(['zero']),
            ),
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7707)',
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
            None,
            {
                'distance_type': 'long',
                'event_tags': ['dispatch_long'],
                'prediction': {
                    'blocking': {'duration_sec': 3600, 'threshold': 30},
                    'type': 'activity',
                    'value': 100,
                    'value_changes': {'c': -1},
                },
            },
            False,
            True,
            marks=[
                pytest.mark.client_experiments3(
                    **get_exp_template(['wrong_tag']),
                ),
                pytest.mark.client_experiments3(
                    **get_exp_template(
                        ['zero'],
                        exp_name='complete_scores_usage_settings',
                        value={'calculate_priority': True},
                    ),
                ),
            ],
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7701)',
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
            None,
            {
                'distance_type': 'long',
                'event_tags': ['dispatch_long'],
                'prediction': {
                    'blocking': {'duration_sec': 3600, 'threshold': 30},
                    'type': 'activity',
                    'value': 100,
                    'value_changes': {'c': -1},
                },
            },
            False,
            False,
            # wrong_app_version
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7707)',
                },
                'order': {
                    'zone': 'wrong_zone',
                    'order_id': TST_ORDER_ID,
                    'tariff_class': Const.TARIFF_CLASS_MINIVAN,
                    'properties': ['explicit_antisurge'],
                },
            },
            Events.EventTypeDescriptor(Events.OrderEventType.COMPLETE.value),
            {'zero'},
            set(),
            None,
            {
                'distance_type': 'long',
                'event_tags': ['explicit_antisurge', 'dispatch_long'],
                'prediction': {
                    'blocking': {'duration_sec': 3600, 'threshold': 30},
                    'type': 'activity',
                    'value': 100,
                    'value_changes': {'c': -1},
                },
            },
            False,
            False,
            # wrong_zone
        ),
    ],
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
        expected_res,
        exp_matched,
        double_prediction,
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
    ident = response.pop('ident')
    assert response == expected_res

    await entity_processor._event_provider.save_event(
        Events.OrderEvent(
            event_id='88005',
            entity_id=DRIVER_UDID,
            zone=None,
            timestamp=TIMESTAMP,
            descriptor=tst_event,
            order_id=TST_ORDER_ID,
            dispatch_id=ident,
            use_priority=exp_matched,
            calculate_priority=exp_matched,
        ),
    )
    res = []

    async for row in mongo.driver_metrics_predictions.find(
            {'udid': DRIVER_UDID},
    ):
        res.append(row)

    assert len(res) == 2 if double_prediction else 1

    await run_dms_processing(stq3_context, 1)
    assert len(cached_drivers) == 1
    assert cached_drivers[-1].complete_scores == tst_cs_result
    assert cached_drivers[-1].activity == 100 if exp_matched else 99


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.rules_config(
    ACTIVITY={
        'default': [
            {
                'name': 'some_rule',
                'actions': [{'action': [{'type': 'activity', 'value': -1}]}],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'tariff': '__default__',
            },
            {
                'name': 'some_rule',
                'actions': [{'action': [{'type': 'activity', 'value': -2}]}],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'tariff': 'cargo_group',
            },
        ],
    },
)
@pytest.mark.config(
    DRIVER_METRICS_TARIFF_TOPOLOGIES={
        '__default__': {'__default__': {'__default__': ['__default__']}},
        'driver-metrics': {
            '__default__': {'cargo_tariff': ['cargo_group', '__default__']},
        },
    },
    DRIVER_METRICS_CONFIG_SERVICE_USAGE_SETTINGS={
        '__default__': ['activity', 'loyalty', 'tagging'],
    },
)
@pytest.mark.client_experiments3(**get_exp_template())
@pytest.mark.parametrize(
    'tst_request, tst_event, expected_res, expected_activity',
    [
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7707)',
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'cargo_tariff',
                    'source_object_type': 'аэропорт',
                    'last_dest_object_type': 'организация',
                },
            },
            Events.EventTypeDescriptor(Events.OrderEventType.COMPLETE.value),
            {
                'distance_type': 'long',
                'event_tags': ['source_airport', 'dispatch_long'],
                'prediction': {
                    'blocking': {'duration_sec': 3600, 'threshold': 30},
                    'type': 'activity',
                    'value': 100,
                    'value_changes': {'c': -2},
                },
            },
            98,
            id='cargo',
        ),
        pytest.param(
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': '9.92 (7707)',
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                    'source_object_type': 'аэропорт',
                    'last_dest_object_type': 'организация',
                },
            },
            Events.EventTypeDescriptor(Events.OrderEventType.COMPLETE.value),
            {
                'distance_type': 'long',
                'event_tags': ['source_airport', 'dispatch_long'],
                'prediction': {
                    'blocking': {'duration_sec': 3600, 'threshold': 30},
                    'type': 'activity',
                    'value': 100,
                    'value_changes': {'c': -1},
                },
            },
            99,
            id='default',
        ),
    ],
)
async def test_activity_tariff(
        stq3_context,
        taxi_driver_metrics,
        cached_drivers,
        patch,
        entity_processor,
        mongo,
        dms_mockserver,
        tst_request,
        tst_event,
        expected_res,
        expected_activity,
):
    # pylint: disable=protected-access
    @patch(
        'taxi_driver_metrics.common.utils._tags_manager'
        '.TagsManager.fetch_service_tags',
    )
    async def _fetch_tags(*_args, **_kwargs):
        return set()

    response = await taxi_driver_metrics.post(HANDLER_PATH, json=tst_request)
    assert response.status == 200
    response = await response.json()
    ident = response.pop('ident')
    assert response == expected_res

    await entity_processor._event_provider.save_event(
        Events.OrderEvent(
            event_id='88005',
            entity_id=DRIVER_UDID,
            zone=None,
            timestamp=TIMESTAMP,
            descriptor=tst_event,
            order_id=TST_ORDER_ID,
            dispatch_id=ident,
            tariff_class=tst_request['order']['tariff_class'],
        ),
    )
    res = []

    async for row in mongo.driver_metrics_predictions.find(
            {'udid': DRIVER_UDID},
    ):
        res.append(row)

    await run_dms_processing(stq3_context, 1)
    assert len(cached_drivers) == 1
    assert cached_drivers[-1].activity == expected_activity
