#  pylint: disable=protected-access

import asyncio
import datetime
from unittest.mock import Mock

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
WRONG_APP_VERSION = '10.0.0'


class Const:
    TARIFF_CLASS_EXPRESS = 'express'
    TARIFF_CLASS_ECONOM = 'econom'
    TARIFF_CLASS_BUSINESS = 'business'
    TARIFF_CLASS_COMFORTPLUS = 'comfortplus'
    TARIFF_CLASS_VIP = 'vip'
    TARIFF_CLASS_MINIVAN = 'minivan'
    TARIFF_CLASS_UNIVERSAL = 'universal'
    TARIFF_CLASS_POOL = 'pool'


@pytest.mark.parametrize(
    'tst_request, tst_event, driver_tags,'
    ' driver_tags_after, tst_activity_result',
    [
        (
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
            53,
        ),
        (
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
            {'good'},
            53,
        ),
        (
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
            {'good'},
            set(),
            60,
        ),
        (
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
            50,
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
        'tags': {
            'order': {
                'auto_reorder': ['long_waiting'],
                'offer_timeout': ['chained_order'],
                'park_cancel': ['long_waiting'],
                'park_fail': ['long_waiting'],
            },
        },
    },
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 10}],
                        'tags': '\'tags::good\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 0}],
                        'tags': '\'tags::zero\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 4}],
                        'tags': '\'tags::bad\'',
                    },
                    {'action': [{'type': 'activity', 'value': 3}]},
                ],
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
)
async def test_activity_prediction(
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
        tst_activity_result,
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
    dms_mockserver.init_activity({DRIVER_UDID: 50})

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
        ),
    )

    prediction = await mongo.driver_metrics_predictions.find_one(
        {'udid': DRIVER_UDID},
    )

    assert prediction

    await run_dms_processing(stq3_context, 1)
    assert len(cached_drivers) == 1
    assert cached_drivers[-1].activity == tst_activity_result


@pytest.mark.parametrize(
    'tst_request, tst_event, tst_activity_result',
    [
        (
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
                    'properties': ['lookup_mode_multioffer'],
                },
            },
            Events.EventTypeDescriptor(
                Events.MultiofferEventType.OFFER_TIMEOUT.value,
            ),
            53,
        ),
        (
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
                    'properties': ['lookup_mode_multioffer'],
                },
            },
            Events.EventTypeDescriptor(
                Events.MultiofferEventType.REJECT_AUTO_CANCEL.value,
            ),
            50,
        ),
        (
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
                    'properties': ['lookup_mode_multioffer'],
                },
            },
            Events.EventTypeDescriptor(
                Events.MultiofferEventType.OFFER_TIMEOUT.value,
                ['chained_order'],
            ),
            55,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'insert_chunk_size': 1000,
        'insert_timeout': 20,
        'tags': {'multioffer_order': {'offer_timeout': ['chained_order']}},
        'fallback': {
            'events': {'order_complete': {'activity': 0}},
            'letter_events': {'c': {'activity': 0}},
        },
    },
    DRIVER_METRICS_ENABLE_MULTIOFFER=True,
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 5}],
                        'tags': '\'event::chained_order\'',
                    },
                    {'action': [{'type': 'activity', 'value': 3}]},
                ],
                'events': [
                    {'name': 'offer_timeout', 'topic': 'multioffer_order'},
                ],
                'name': 'ActivityTrip',
            },
        ],
    },
)
async def test_activity_prediction_multioffer(
        stq3_context,
        web_app_client,
        cached_drivers,
        patch,
        entity_processor,
        mongo,
        dms_mockserver,
        tst_request,
        tst_event,
        tst_activity_result,
):
    # pylint: disable=protected-access
    @patch(
        'taxi_driver_metrics.common.utils._tags_manager'
        '.TagsManager.fetch_service_tags',
    )
    async def _fetch_tags(*_args, **_kwargs):
        return []

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
    dms_mockserver.init_activity({DRIVER_UDID: 50})

    response = await web_app_client.post(HANDLER_PATH, json=tst_request)
    assert response.status == 200
    response = await response.json()

    await entity_processor._event_provider.save_event(
        Events.MultiofferEvent(
            event_id='88005',
            entity_id=DRIVER_UDID,
            zone=None,
            timestamp=TIMESTAMP,
            descriptor=tst_event,
            order_id=TST_ORDER_ID,
            dispatch_id=response.get('ident'),
        ),
    )

    prediction = await mongo.driver_metrics_predictions.find_one(
        {'udid': DRIVER_UDID},
    )

    assert prediction['prediction']
    await run_dms_processing(stq3_context, 1)
    assert len(cached_drivers) == 1
    assert cached_drivers[-1].activity == tst_activity_result


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 0}},
            'letter_events': {'c': {'activity': 0}},
        },
        'insert_chunk_size': 1000,
        'prediction_lifetime_sec': 3,
        'insert_timeout': 20,
        'tags': {},
    },
)
async def test_prediction_inserting(web_context):
    web_context.metrics_prediction.return_records_to_queue = Mock()

    web_context.metrics_prediction._prediction_to_insert = {
        'one': {
            'dispatch_id': 'one',
            'udid': 'udid',
            'order_id': 'order_id',
            'prediction': {},
            'additional_params': None,
            'updated': TIMESTAMP,
        },
        'two': {
            'dispatch_id': 'two',
            'udid': 'udid',
            'order_id': 'order_id',
            'prediction': {},
            'additional_params': None,
            'updated': TIMESTAMP - datetime.timedelta(seconds=5),
        },
        'three': {
            'dispatch_id': 'one',
            'udid': 'udid',
            'order_id': 'order_id',
            'prediction': {},
            'additional_params': None,
            'updated': TIMESTAMP,
        },
    }

    await web_context.metrics_prediction.start_prediction_inserting()
    await asyncio.gather(*web_context.metrics_prediction.tasks)

    prediction = await web_context.mongo.driver_metrics_predictions.find_one(
        {'udid': 'udid'},
    )
    assert prediction

    web_context.mongo.driver_metrics_predictions = None

    web_context.metrics_prediction._prediction_to_insert = {
        'four': {
            'dispatch_id': 'four',
            'udid': 'udid',
            'order_id': 'order_id',
            'prediction': {},
            'additional_params': None,
            'updated': TIMESTAMP,
        },
    }

    await web_context.metrics_prediction.start_prediction_inserting()
    await asyncio.gather(*web_context.metrics_prediction.tasks)

    # with broken inserts record trying to return in queue
    assert (
        web_context.metrics_prediction.return_records_to_queue.call_count == 1
    )
