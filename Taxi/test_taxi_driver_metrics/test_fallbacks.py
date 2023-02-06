# pylint: disable=protected-access, C1801, C0103,
# pylint: disable=R0915, unused-variable
import datetime

import pytest

from metrics_processing.rules.common import RuleType

from taxi_driver_metrics.common.models import BlockingType
from taxi_driver_metrics.common.models import DmsEventsProvider
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import fallback
from taxi_driver_metrics.common.models import run_dms_processing


BAD_DRIVER_ID = '5b05621ee6c22ea2654849c0'
NEW_TST_RULE_NAME = 'new_blocking_rule'
TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)
TST_ZONE = 'bangladesh'
TST_ZONE2 = 'urupinsk'
TANKER_KEY = 'key'
TST_EVENT_REF_ID4 = 'sodfjasiaioid3i3i8s'


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
    DRIVER_METRICS_USE_EVENT_FALLBACKS=True,
)
@pytest.mark.rules_config(
    BLOCKING={
        'default': [],
        TST_ZONE2: [
            {
                'name': NEW_TST_RULE_NAME,
                'events_period_sec': 4000,
                'events_to_trigger_cnt': 1,
                'events': [{'topic': 'order', 'name': 'offer_timeout'}],
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
@pytest.mark.parametrize('fallback_fired', (True, False))
async def test_block_fallbacks(
        stq3_context,
        dms_mockserver,
        patch,
        response_mock,
        entity_processor,
        fake_event_provider,
        cached_drivers,
        fallback_fired,
):
    @patch('taxi.clients_wrappers.statistics.StatisticsClient.fallback_fired')
    def _(flck):
        if flck == fallback.FALLBACK_OFFER_TIMEOUT_EVENT_METRIC:
            return fallback_fired
        return False

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
        Events.OrderEvent(
            descriptor=Events.EventTypeDescriptor(
                Events.OrderEventType.OFFER_TIMEOUT.value, tags=['test'],
            ),
            timestamp=TIMESTAMP,
            entity_id=BAD_DRIVER_ID,
            event_id='__',
            zone=TST_ZONE2,
        ),
    )

    await run_dms_processing(stq3_context, 1)

    calls2 = apply_blocking_state.calls
    assert calls2
    driver = cached_drivers[-1]
    if fallback_fired:
        assert not driver.get_active_blocking(BlockingType.BY_ACTIONS)
    else:
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
@pytest.mark.config(
    DRIVER_METRICS_USE_EVENT_FALLBACKS=True,
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'seen_timeout': {'activity': -1}},
            'letter_events': {'c': {'activity': -1}},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 300,
        'tags': {'order': {'reject_manual': ['chained_order']}},
    },
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.parametrize('fallback_fired', (True, False))
async def test_activity_with_fallback(
        stq3_context,
        dms_mockserver,
        patch,
        cached_journals,
        event_provider,
        predict_activity,
        fallback_fired,
):
    @patch('taxi.clients_wrappers.statistics.StatisticsClient.fallback_fired')
    def _(fbck):
        if fbck == fallback.FALLBACK_SEEN_TIMEOUT_EVENT_METRIC:
            return fallback_fired
        return False

    dms_mockserver.init_activity({BAD_DRIVER_ID: 10})
    dispatch_id = await predict_activity(
        BAD_DRIVER_ID, {'order_seen_timeout': -5},
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
                Events.OrderEventType.SEEN_TIMEOUT.value,
            ),
        ),
    )
    await run_dms_processing(stq3_context, 1)
    actions = cached_journals[-1].actions
    assert len(actions[RuleType.ACTIVITY]) == 2
    # because we recalculate activity every time now
    assert actions[RuleType.ACTIVITY][0].action.result == 50
    assert (
        actions[RuleType.ACTIVITY][1].action.result == 0
        if fallback_fired
        else -5
    )

    driver = await DriverInfo.make(
        stq3_context,
        BAD_DRIVER_ID,
        event_provider,
        TIMESTAMP,
        False,
        False,
        False,
    )
    assert driver.activity == 60 if fallback_fired else 55
