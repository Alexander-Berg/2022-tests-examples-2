# pylint: disable=protected-access
import datetime

import pytest

from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import run_dms_processing


UDID = '5b05621ee6c22ea2654849c9'
TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)


async def _get_driver(app, event_fetcher) -> DriverInfo:
    return await DriverInfo.make(
        app,
        unique_driver_id=UDID,
        event_fetcher=event_fetcher,
        driver_history_from_timestamp=TIMESTAMP,
        fetch_events_history=False,
        fetch_tags=True,
        fetch_blocking_history=True,
    )


@pytest.mark.config(
    DRIVER_METRICS_ENABLE_TAG_FETCHER=True,
    DRIVER_METRICS_COMPLETE_SCORES_SETTINGS={
        '__default__': {
            'initial_value': 0,
            'blocking_threshold': -3,
            'amnesty_value': 5,
            'blocking_durations': [10_000],
            'use_complete_scores_in_lookup': True,
        },
    },
    DRIVER_METRICS_TAG_FOR_EXPERIMENT={
        'use_complete_scores_in_lookup': {
            'from': 0,
            'to': 100,
            'salt': '&%^^#@%',
        },
    },
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.parametrize(
    'starting_cs, mode, value, cs_result, priority_result',
    [
        (
            7,
            'additive',
            10,
            {'increment': 10, 'value_to_set': 7},
            {'absolute_value': 99, 'increment': 0},
        ),
        (
            1,
            'absolute',
            -5,
            {'increment': -6, 'value_to_set': -5},
            {'absolute_value': -3, 'increment': -4},
        ),
    ],
)
# type of event processing
async def test_cs_supertest(
        stq3_context,
        dms_mockserver,
        event_provider,
        fake_event_provider,
        tags_service_mock,
        starting_cs,
        mode,
        value,
        cs_result,
        priority_result,
):
    app = stq3_context
    tags_service_mock()
    dms_mockserver.init_complete_scores({UDID: starting_cs})
    driver = await _get_driver(app, fake_event_provider([]))

    # check starting parameters
    assert driver.current_blocking == []

    event = Events.ServiceManualEvent(
        timestamp=TIMESTAMP,
        event_id='1991',
        entity_id=UDID,
        order_id='393j3393j939j394',
        operation=Events.ServiceManualEventType.SET_COMPLETE_SCORES_VALUE,
        mode=Events.ManualValueMode(mode),
        value=value,
    )

    await event_provider.save_event(event)

    await run_dms_processing(app, 999)
    assert dms_mockserver.event_complete.times_called == 1

    complete_call = dms_mockserver.event_complete.next_call()['request'].json

    assert complete_call['complete_score'] == cs_result
    #  check when migrate to dms scale
    assert complete_call['priority'] == priority_result
