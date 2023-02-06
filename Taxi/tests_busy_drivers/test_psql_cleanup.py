import datetime

import pytest


NOW = datetime.datetime(1969, 7, 20, 20, 17, 39)


@pytest.mark.parametrize(
    'timestamp, expected_row_count, expected_logistic_count',
    [
        (NOW, 3, 2),
        (NOW + datetime.timedelta(minutes=5), 3, 2),
        (NOW + datetime.timedelta(minutes=15), 1, 1),
        (NOW + datetime.timedelta(minutes=65), 0, 0),
    ],
)
@pytest.mark.config(
    BUSY_DRIVERS_PSQL_CLEANUP_SETTINGS=dict(
        finished_order_ttl=10,
        expired_order_ttl=60,
        cleanup_chunk_size=1,
        logistic_event_ttl=60,
    ),
)
@pytest.mark.pgsql('busy_drivers', files=['orders.sql'])
async def test_psql_cleanup(
        taxi_busy_drivers,
        pgsql,
        mocked_time,
        timestamp,
        expected_row_count,
        expected_logistic_count,
):
    mocked_time.set(timestamp)
    await taxi_busy_drivers.run_task('distlock/psql-cleaner')
    cursor = pgsql['busy_drivers'].cursor()
    cursor.execute('SELECT 1 FROM busy_drivers.order_meta;')
    assert len(cursor.fetchall()) == expected_row_count
    cursor = pgsql['busy_drivers'].cursor()
    cursor.execute('SELECT 1 FROM busy_drivers.logistics_events;')
    assert len(cursor.fetchall()) == expected_logistic_count
