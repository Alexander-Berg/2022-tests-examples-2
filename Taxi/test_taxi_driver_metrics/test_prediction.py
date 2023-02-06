#  pylint: disable=protected-access
import asyncio
import datetime

import pytest

from taxi_driver_metrics.common import prediction
from taxi_driver_metrics.common.models import Events


DISPATCH_ID = '123321'
UDID = 'wow_udid'
ORDER_ID = 'another_one_order_id'
TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)


async def test_base(stq3_context, mongo):
    prediction_obj = prediction.PredictionManager(
        stq3_context, asyncio.get_event_loop(),
    )

    prediction_obj.prediction_to_insert[DISPATCH_ID] = {
        'dispatch_id': DISPATCH_ID,
        'udid': UDID,
        'order_id': ORDER_ID,
        'prediction': {},
        'additional_params': {},
        'updated': TIMESTAMP,
    }

    await prediction_obj._insert_records(
        prediction_obj.prediction_to_insert.values(),
    )
    mongo_prediction = await mongo.driver_metrics_predictions.find_one(
        {'dispatch_id': DISPATCH_ID},
    )
    assert mongo_prediction == prediction_obj.prediction_to_insert[DISPATCH_ID]


@pytest.mark.parametrize(
    'config_mark, expected_value',
    [
        ({'DRIVER_METRICS_STOP_ACTIVITY_PENALTY': {'order': {}}}, 0),
        (
            {
                'DRIVER_METRICS_STOP_ACTIVITY_PENALTY': {
                    'order': {'complete': {}},
                },
            },
            0,
        ),
        (
            {
                'DRIVER_METRICS_STOP_ACTIVITY_PENALTY': {
                    'order': {'complete': {'tags': ['aa']}},
                },
            },
            0,
        ),
        ({'DRIVER_METRICS_STOP_ACTIVITY_PENALTY': {'all': {}}}, 0),
        ({'DRIVER_METRICS_STOP_ACTIVITY_PENALTY': {'reposition': {}}}, -5),
        (
            {
                'DRIVER_METRICS_STOP_ACTIVITY_PENALTY': {
                    'order': {'reject': {}},
                },
            },
            -5,
        ),
        ({'DRIVER_METRICS_STOP_ACTIVITY_PENALTY': {'order': {'all': {}}}}, 0),
        (
            {
                'DRIVER_METRICS_STOP_ACTIVITY_PENALTY': {
                    'order': {'complete': {'tags': ['not_existing']}},
                },
            },
            -5,
        ),
    ],
)
async def test_stop_penalty(
        patch, stq3_context, config_mark, expected_value, taxi_config,
):
    @patch(
        'taxi_driver_metrics.common.prediction.get_activity_event_prediction',
    )
    async def _(app, event):
        return {'activity': -5}

    taxi_config.set(**config_mark)
    await stq3_context.refresh_caches()

    event = Events.OrderEvent(
        event_id='1',
        timestamp=datetime.datetime.now(),
        descriptor=Events.EventTypeDescriptor(
            event_name='complete', tags=['aa'],
        ),
    )

    value, _ = await prediction.get_predicted_activity_data(
        stq3_context, event,
    )

    assert value == expected_value
