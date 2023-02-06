import datetime

import pytest
import pytz


EXPECTED_YT_TABLE_NAME = '//home/ratings'
SYNC_START_TIME = datetime.datetime(2019, 12, 19, 0, 0, 0, tzinfo=pytz.utc)

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        PASSENGER_PROFILE_RATINGS_YT_TABLE=EXPECTED_YT_TABLE_NAME,
        PASSENGER_PROFILE_RATINGS_SYNC_ENABLED=True,
    ),
    pytest.mark.now(SYNC_START_TIME.isoformat()),
]


async def test_sync_start(cron_runner, run_sql, mocked_time):

    await cron_runner.ratings_sync_start()

    result = run_sql('select * from passenger_profile.ratings_sync')
    assert len(result) == 1
    created_sync = result[0]

    # TODO: fix mocked time
    # assert created_sync['started_at'] == SYNC_START_TIME
    assert created_sync['finished_at'] is None
    assert created_sync['sync_ratings_changed_since'] is None
    assert created_sync['yt_table_name'] == EXPECTED_YT_TABLE_NAME
    assert created_sync['last_row_processed'] == 0


@pytest.mark.pgsql(
    dbname='passenger_profile',
    files=['pg_passenger_profile_last_sync_finished.sql'],
)
async def test_sync_start_last_sync_finished(cron_runner, run_sql):
    await cron_runner.ratings_sync_start()

    created_sync = run_sql(
        """
        select * from passenger_profile.ratings_sync
        where yt_table_name = %s
        """,
        EXPECTED_YT_TABLE_NAME,
    )[0]

    previous_sync_started_at = datetime.datetime(
        2019, 12, 15, 0, 0, 0, tzinfo=pytz.utc,
    )
    # TODO: fix mocked time
    # assert created_sync['started_at'] == SYNC_START_TIME
    assert created_sync['finished_at'] is None
    assert (
        created_sync['sync_ratings_changed_since'] == previous_sync_started_at
    )
    assert created_sync['last_row_processed'] == 0


@pytest.mark.pgsql(
    dbname='passenger_profile',
    files=['pg_passenger_profile_last_sync_not_finished.sql'],
)
async def test_sync_start_last_sync_not_finished(cron_runner, run_sql):
    with pytest.raises(RuntimeError) as exc:
        await cron_runner.ratings_sync_start()

    assert str(exc.value) == 'Task \'ratings_sync_start\' failed'

    # Check that we didn't create a new sync instance
    latest_sync = run_sql(
        """
        select * from passenger_profile.ratings_sync
        order by started_at desc
        limit 1
        """,
    )[0]

    assert latest_sync['finished_at'] is None
    assert latest_sync['started_at'] == datetime.datetime(
        2019, 12, 15, 0, 0, 0, tzinfo=pytz.utc,
    )


async def test_sync_start_sync_disabled(cron_runner, run_sql, taxi_config):
    taxi_config.set(PASSENGER_PROFILE_RATINGS_SYNC_ENABLED=False)
    await cron_runner.ratings_sync_start()

    # check that we didn't create a new sync
    syncs = run_sql('select * from passenger_profile.ratings_sync')
    assert not syncs
