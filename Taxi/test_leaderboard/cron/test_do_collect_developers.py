import datetime

import pytest


def _get_top(pgsql):
    cursor = pgsql['leaderboard_pg'].conn.cursor()
    query = """select rank_place, login, index, date_of_top
               from leaderboard.developers
               order by rank_place limit 10;"""
    cursor.execute(query)
    return list(cursor)


@pytest.mark.now('2019-01-01T00:00:00')
@pytest.mark.config(
    LEADERBOARD_REPOSITORIES=['taxi/backend'], LEADERBOARD_COLLECT_PERIOD=14,
)
@pytest.mark.pgsql('leaderboard_pg', files=['developers.sql'])
@pytest.mark.skip
async def test_do_collect(run_cron_do_collect_developers, pgsql, load_json):
    assert _get_top(pgsql) == [(3, 'noname', 0.0, datetime.date(2018, 1, 1))]
    await run_cron_do_collect_developers()
    assert _get_top(pgsql) == [
        (1, 'ydemidenko', 2.0, datetime.date(2019, 1, 1)),
        (2, 'karachevda', 0.0, datetime.date(2019, 1, 1)),
    ]
