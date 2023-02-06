# pylint: disable=redefined-outer-name,duplicate-code,unused-variable
import pytest

from driver_ratings_storage.generated.cron import run_cron


@pytest.mark.pgsql(
    'driver_ratings_storage', files=['pg_driver_ratings_history.sql'],
)
@pytest.mark.parametrize(
    'expected_data',
    [
        pytest.param(
            [('driver1', 4.0), ('driver2', 4.0), ('driver3', 4.0)],
            marks=[pytest.mark.config(DRIVER_HISTORY_RATING_LIMIT=1)],
            id='Limit 1',
        ),
        pytest.param(
            [
                ('driver1', 3.0),
                ('driver2', 3.0),
                ('driver1', 4.0),
                ('driver2', 4.0),
                ('driver3', 4.0),
            ],
            marks=[pytest.mark.config(DRIVER_HISTORY_RATING_LIMIT=2)],
            id='Limit 2',
        ),
    ],
)
async def test_cron(pgsql, expected_data):
    await run_cron.main(
        ['driver_ratings_storage.crontasks.clean_rating_history', '-t', '0'],
    )

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(
            """
            SELECT driver_id, rating
            FROM driver_ratings_storage.ratings_history
            ORDER BY calc_at;
            """,
        )
        rows = list(cursor)

    assert rows == expected_data
