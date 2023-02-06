import datetime
import uuid

import pytest

from taxi_driver_metrics.common.models import DmsEventsProvider
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import run_dms_processing


TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)
UDID = '5b05621ee6c22ea2654849c9'


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
@pytest.mark.parametrize('absolute', (True, False))
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(
    DRIVER_METRICS_CONFIG_SERVICE_USAGE_SETTINGS={
        '__default__': ['loyalty', 'tagging'],
    },
    DRIVER_METRICS_ENABLE_TAGGING_RULES=True,
)
@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'name': '1 event = f',
                'events_period_sec': 4000,
                'events_to_trigger_cnt': 1,
                'events': [{'topic': 'dm_service_manual'}],
                'delayed': True,
                'actions': [
                    {
                        'action': [
                            {'type': 'tagging', 'tags': [{'name': 'f'}]},
                        ],
                        'expr': 'event.activity_change == 6',
                    },
                ],
            },
        ],
    },
)
async def test_delayed_rules(
        stq3_context,
        dms_mockserver,
        fake_event_provider,
        entity_processor,
        tags_service_mock,
        absolute,
):
    dms_mockserver.init_activity({UDID: 80})
    event_provider = DmsEventsProvider(stq3_context)
    tags_patch = tags_service_mock()

    event = Events.ServiceManualEvent(
        timestamp=TIMESTAMP,
        entity_id=UDID,
        zone='Albuquerque',
        event_id=uuid.uuid4().hex,
        value=86 if absolute else 6,
        mode=Events.ManualValueMode.ABSOLUTE
        if absolute
        else Events.ManualValueMode.ADDITIVE,
        reason='Tst reason',
    )

    driver = await DriverInfo.make(
        stq3_context, UDID, fake_event_provider([]), TIMESTAMP,
    )

    assert driver.activity == 80
    assert not driver.current_blocking

    await event_provider.save_event(event)

    await run_dms_processing(stq3_context, 1)

    assert dms_mockserver.event_complete.times_called

    driver = await DriverInfo.make(
        stq3_context, UDID, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.activity == 86
    assert not driver.current_blocking
    assert tags_patch.tags_upload.times_called == 1
