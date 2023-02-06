# pylint: disable=C5521
from datetime import datetime

import pytest


@pytest.fixture(name='driver_wall')
def _mock_driver_wall(mockserver):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def _driver_wall_add(request):
        return mockserver.make_response(status=200, json={'id': '1'})


@pytest.mark.experiments3(
    filename='eats_performer_statistics_time_to_send.json',
)
@pytest.mark.now('2022-02-22T12:00:00+00:00')
@pytest.mark.yt(static_table_data=['yt_leaderboards.yaml'])
async def test_leaderboard_send(
        taxi_eats_performer_statistics, yt_apply, driver_wall, pgsql,
):
    await taxi_eats_performer_statistics.run_periodic_task(
        'eats-performer-statistics-leaderboard-sender-periodic',
    )

    cursor = pgsql['eats_performer_statistics'].dict_cursor()
    cursor.execute(
        """select leaderboard
        from eats_performer_statistics.last_sent_to_chats""",
    )
    assert len(cursor.fetchall()) == 3


@pytest.mark.experiments3(
    filename='eats_performer_statistics_time_to_send.json',
)
@pytest.mark.now('2022-02-22T12:00:00+00:00')
@pytest.mark.pgsql('eats_performer_statistics', files=['fill_data_send.sql'])
@pytest.mark.yt(static_table_data=['yt_leaderboards.yaml'])
async def test_leaderboard_new_send(
        taxi_eats_performer_statistics, yt_apply, driver_wall, pgsql,
):
    await taxi_eats_performer_statistics.run_periodic_task(
        'eats-performer-statistics-leaderboard-sender-periodic',
    )

    cursor = pgsql['eats_performer_statistics'].dict_cursor()
    cursor.execute(
        """select last_leaderboard_sent_at
        from eats_performer_statistics.last_sent_to_chats""",
    )
    for row in cursor.fetchall():
        print(row[0])
        assert row[0] == datetime.fromisoformat(
            '2022-06-21 00:00:00.000+00:00',
        )


@pytest.mark.experiments3(
    filename='eats_performer_statistics_time_to_send.json',
)
@pytest.mark.now('2022-02-22T12:00:00+00:00')
@pytest.mark.pgsql(
    'eats_performer_statistics', files=['fill_data_not_send.sql'],
)
@pytest.mark.yt(static_table_data=['yt_leaderboards.yaml'])
async def test_leaderboard_not_send(
        taxi_eats_performer_statistics, yt_apply, driver_wall, pgsql,
):
    await taxi_eats_performer_statistics.run_periodic_task(
        'eats-performer-statistics-leaderboard-sender-periodic',
    )

    cursor = pgsql['eats_performer_statistics'].dict_cursor()
    cursor.execute(
        """select last_leaderboard_sent_at
        from eats_performer_statistics.last_sent_to_chats""",
    )
    for row in cursor.fetchall():
        assert row[0] == datetime.fromisoformat(
            '2022-06-22 12:00:00.000+00:00',
        )


@pytest.mark.experiments3(
    filename='eats_performer_statistics_time_to_send.json',
)
@pytest.mark.now('2022-02-22T14:00:00+00:00')
@pytest.mark.pgsql('eats_performer_statistics', files=['fill_data_send.sql'])
@pytest.mark.yt(static_table_data=['yt_leaderboards.yaml'])
async def test_leaderboard_not_send_not_in_exp_time(
        taxi_eats_performer_statistics, yt_apply, driver_wall, pgsql,
):
    await taxi_eats_performer_statistics.run_periodic_task(
        'eats-performer-statistics-leaderboard-sender-periodic',
    )

    cursor = pgsql['eats_performer_statistics'].dict_cursor()
    cursor.execute(
        """select last_leaderboard_sent_at
        from eats_performer_statistics.last_sent_to_chats""",
    )
    for row in cursor.fetchall():
        assert row[0] == datetime.fromisoformat(
            '2022-06-20 12:00:00.000+00:00',
        )
