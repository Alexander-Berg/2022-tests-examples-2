import copy
import datetime as dt

import pytest

from transactions.clients.trust import event_stats

_UNCHANGED_EVENT_STATS = [
    {
        'created': dt.datetime(2020, 4, 3, 3, 2),
        'detailed': {'card': {'CheckBasket': {'success': 2, 'error': 1}}},
        'success': 2,
        'error': 1,
        'name': 'billing_call_simple',
    },
]


@pytest.mark.now('2020-04-03T03:02:08+00:00')
@pytest.mark.config(
    TRANSACTIONS_UPDATE_EVENT_STATS_FOR=['card'],
    TRANSACTIONS_UPDATE_SERVICE_STATS_FOR=['card'],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize(
    (
        'pass_collection, billing_service_id, method, status, '
        'expected_event_stats'
    ),
    [
        (
            True,
            'card',
            'CheckBasket',
            'success',
            [
                {
                    'created': dt.datetime(2020, 4, 3, 3, 2),
                    'detailed': {
                        'card': {'CheckBasket': {'success': 3, 'error': 1}},
                    },
                    'success': 3,
                    'error': 1,
                    'name': 'billing_call_simple',
                },
            ],
        ),
        (False, 'card', 'CheckBasket', 'success', _UNCHANGED_EVENT_STATS),
        (True, 'uber', 'CheckBasket', 'success', _UNCHANGED_EVENT_STATS),
    ],
)
@pytest.mark.parametrize(
    'events_to_statistics_enabled',
    [
        pytest.param(False, id='statistics_disabled'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                TRANSACTIONS_BILLING_EVENTS_TO_STATISTICS_ENABLED=True,
            ),
            id='statistics_enabled',
        ),
    ],
)
@pytest.mark.filldb(event_stats='for_test_save_for')
async def test_save_for(
        db,
        web_context,
        mock_statistics_agent,
        pass_collection,
        billing_service_id,
        method,
        status,
        expected_event_stats,
        events_to_statistics_enabled,
):
    @mock_statistics_agent('/v1/metrics/store')
    async def statistics_handler(request):
        assert request.json == {
            'metrics': [
                {
                    'name': (
                        'billing_call_simple.detailed.card.CheckBasket.success'
                    ),
                    'value': 1,
                },
                {'name': 'billing_call_simple.total.success', 'value': 1},
            ],
        }
        return {}

    config = web_context.config

    collection = db.event_stats if pass_collection else None
    stats = event_stats.EventStats(
        collection, config, web_context.clients.statistics_agent,
    )

    await stats.save_for(billing_service_id, method, status)

    docs = await db.event_stats.find().to_list(None)
    _assert_same_event_stats(docs, expected_event_stats)

    should_report_for_service = (
        billing_service_id in config.TRANSACTIONS_UPDATE_SERVICE_STATS_FOR
    )
    if events_to_statistics_enabled and should_report_for_service:
        assert statistics_handler.times_called == 1


def _assert_same_event_stats(actual, expected):
    assert _prepare(actual) == _prepare(expected)


def _prepare(event_stats_):
    result = copy.deepcopy(sorted(event_stats_, key=_by_created))
    for item in result:
        item.pop('_id', None)
    return result


def _by_created(stat):
    return stat['created']
