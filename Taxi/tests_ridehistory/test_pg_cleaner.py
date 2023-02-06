import datetime as dt

import pytest
import pytz


@pytest.mark.pgsql('ridehistory')
@pytest.mark.config(
    RIDEHISTORY_PG_CLEANER_SETTINGS={
        'tables': [
            {
                'name': 'hidden_orders',
                'ttl': 86400 * 4 + 3600,
                'chunk_size': 123,
            },
            {'name': 'user_index', 'ttl': 86400 * 3 + 3600, 'chunk_size': 123},
        ],
        'period': 12345,
    },
)
@pytest.mark.suspend_periodic_tasks('ridehistory-pg-cleaner')
async def test_simple(
        taxi_ridehistory,
        get_table_ids,
        mock_order_core_heartbeat,
        pgsql,
        load,
):
    pgsql['ridehistory'].cursor().execute(load('ridehistory_simple.sql'))

    order_core_mock = mock_order_core_heartbeat(
        {
            '77777777777777777777777777777777': 200,
            '77777777777777777777777777777776': 404,
            '77777777777777777777777777777773': 500,
        },
    )

    await taxi_ridehistory.run_periodic_task('ridehistory-pg-cleaner')

    assert get_table_ids('hidden_orders') == {'4', '5'}
    assert get_table_ids('user_index') == {
        '77777777777777777777777777777777',
        '77777777777777777777777777777773',
        '77777777777777777777777777777775',
        '77777777777777777777777777777774',
    }
    assert order_core_mock.times_called >= 3

    db = pgsql['ridehistory']
    cursor = db.cursor()
    cursor.execute(
        'SELECT seen_unarchived_at FROM ridehistory.user_index '
        'WHERE order_id IN (\'77777777777777777777777777777773\', '
        '\'77777777777777777777777777777777\')',
    )
    seens = list({row[0] for row in cursor})
    assert len(seens) == 1

    seen_utc = seens[0].astimezone(pytz.UTC)
    hour_ago_utc = dt.datetime.now(tz=pytz.UTC) - dt.timedelta(hours=1)
    assert seen_utc >= hour_ago_utc
