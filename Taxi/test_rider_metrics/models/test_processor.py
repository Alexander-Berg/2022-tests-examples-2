import pytest

from rider_metrics.models import processor

TIMESTAMP = '2020-04-14T14:03:46.905244+03:00'
MINUS_TWO_HOURS = '2020-04-14T12:03:46.905244+03:00'
DEFAULT_HISTORY_FROM = '2020-04-14T01:03:46.905244+03:00'

ENTITY_ID = 'entity_id'


@pytest.mark.parametrize(
    'period_in_config',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    RIDER_METRICS_EVENTS_PROCESSING_PARAMS={
                        'master_worker_interval_msec': 800,
                        'workers_num': 10,
                        'max_delay_for_worker_spawn_msec': 50,
                        'events_butch_size': 10,
                        'event_period_seconds': 7200,
                    },
                ),
            ],
        ),
        False,
    ],
)
@pytest.mark.config(
    RIDER_METRICS_TAG_FOR_EXPERIMENT={
        'rare_tag': {'salt': 'pepper', 'from': 0, 'to': 1},
        'common_tag': {'salt': 'pepper', 'from': 0, 'to': 100},
    },
)
@pytest.mark.now(TIMESTAMP)
async def test_event_period(
        stq3_context, mock_processing_service, period_in_config,
):
    patch = mock_processing_service([], [])

    tst_processor = processor.Processor(stq3_context)
    entity_processor = tst_processor.make_entity_processor()

    # pylint: disable=protected-access
    rider = await entity_processor._acquire_context(ENTITY_ID)
    assert rider.prefix_tags == {'experiment::common_tag'}

    assert patch.event_history.times_called == 1
    assert patch.event_history.next_call()['_args'][0].json == {
        'user_id': ENTITY_ID,
        'created_after': (
            MINUS_TWO_HOURS if period_in_config else DEFAULT_HISTORY_FROM
        ),
    }
