import datetime

import pytest


PERIODIC_NAME = 'send-finished-trial-period-notifications-periodic'

EXPECTED_JOURNALPLACES = [
    (201, datetime.datetime.now().date()),
    (202, datetime.datetime.now().date()),
    (203, datetime.datetime.now().date()),
    (204, datetime.datetime.now().date()),
    (205, datetime.datetime.now().date()),
    (210, datetime.datetime.now().date()),
    (211, datetime.date(2020, 2, 2)),
    (212, datetime.date(2020, 2, 1)),
    (213, datetime.date(2020, 1, 31)),
    (214, datetime.date(2020, 1, 29)),
    (215, datetime.date(2020, 1, 29)),
    (215, datetime.datetime.now().date()),
    (216, datetime.date(2020, 2, 2)),
    (217, datetime.datetime.now().date()),
    (218, datetime.datetime.now().date()),
    (219, datetime.datetime.now().date()),
]


@pytest.mark.config(
    EATS_PLACE_SUBSCRIPTIONS_PERIODICS={
        PERIODIC_NAME: {
            'is_enabled': True,
            'period_in_sec': 3600,
            'db_chunk_size': 2,
        },
    },
)
@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.now('2020-02-02T15:00:00+0300')
async def test_send_notifications_about_finishig_trial_subscriptions(
        mockserver, taxi_eats_place_subscriptions, testpoint, pgsql,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications(request):
        request.json['recipients']['place_ids'].sort()
        place_ids = request.json['recipients']['place_ids']
        assert place_ids in (
            [210],
            [201, 202, 203, 204, 205],
            [215],
            [218, 219],
            [217],
        )
        return mockserver.make_response(status=204)

    await taxi_eats_place_subscriptions.run_distlock_task(PERIODIC_NAME)
    assert _mock_communications.times_called == 5
    cursor = pgsql['eats_place_subscriptions'].cursor()
    cursor.execute(
        f"""
        SELECT place_id, created_at
        FROM eats_place_subscriptions.notifications_journal
        ORDER BY place_id, created_at;
    """,
    )
    result = [(place[0], place[1].date()) for place in cursor.fetchall()]
    assert result == EXPECTED_JOURNALPLACES
