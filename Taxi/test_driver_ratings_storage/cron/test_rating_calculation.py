# pylint: disable=protected-access

import datetime
import json
import operator
import typing

import pytest

from testsuite.utils import http

from driver_ratings_storage.crontasks import rating_calculation
from driver_ratings_storage.generated.cron import run_cron
from driver_ratings_storage.storage.postgresql import db


_NOW_STR = '2019-05-16T00:00:00'
_NOW_WITH_TZ = _NOW_STR + '+00:00'
_LOCAL_TZ_OFFSET = 60 * 60 * 3
PROFILES_MAPPING = {
    'profiles': [
        {
            'unique_driver_id': 'driver_1',
            'data': [
                {
                    'park_id': 'park_1',
                    'driver_profile_id': 'driver_1',
                    'park_driver_profile_id': 'park_1_driver_1',
                },
                {
                    'park_id': 'park_1',
                    'driver_profile_id': 'driver_2',
                    'park_driver_profile_id': 'park_1_driver_2',
                },
            ],
        },
        {
            'unique_driver_id': 'driver_2',
            'data': [
                {
                    'park_id': 'park_1',
                    'driver_profile_id': 'driver_3',
                    'park_driver_profile_id': 'park_1_driver_3',
                },
            ],
        },
    ],
}


def _prepare_event_logs(cron_event_logs):
    serialized_events = [json.loads(event) for event in cron_event_logs]
    serialized_events.sort(key=operator.itemgetter('unique_driver_id'))
    return serialized_events


def select_scores(pgsql, driver_id) -> typing.List[db.ScoreData]:
    cursor = pgsql['driver_ratings_storage'].cursor()

    cursor.execute(
        'SELECT order_id, score, scored_at, ignore_started_at '
        'FROM driver_ratings_storage.scores '
        f'WHERE driver_id=\'{driver_id}\'',
    )

    result = [
        db.ScoreData(
            order_id=row[0],
            score=row[1],
            scored_at=row[2],
            ignore_started_at=row[3],
        )
        for row in cursor
    ]

    cursor.close()
    return result


def test_no_scores(pgsql):
    scores = select_scores(pgsql, 'driver_1')
    calculator = rating_calculation._RatingCalculator(200, 15, 4, 1)
    rating, used_scores, _ = calculator.get_rating(scores, [])
    assert int(rating) == 1
    assert used_scores == 0


def test_enough_scores_no_padding(pgsql):
    scores = select_scores(pgsql, 'driver_1')

    # orders 1-5 => '5'
    calculator = rating_calculation._RatingCalculator(5, 10, 4, 3)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert int(rating) == 5
    assert used_scores_num == 5

    # orders 6-10 => '4'
    calculator = rating_calculation._RatingCalculator(5, 5, 4, 3)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert int(rating) == 4
    assert used_scores_num == 5

    # orders 11-15 => '3'
    calculator = rating_calculation._RatingCalculator(5, 5, 4, 3)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert int(rating) == 4
    assert used_scores_num == 5


def test_scores_weights():
    now = datetime.datetime.now()
    scores = [
        db.ScoreData(
            order_id=f'id{i}',
            score=v,
            scored_at=now - datetime.timedelta(days=i),
            ignore_started_at=None,
        )
        for i, v in enumerate((2, 2, 3, 4))
    ]
    calculator = rating_calculation._RatingCalculator(100, 1, 1, 5)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert rating == pytest.approx(
        (2 * 100 + 3 * 99 + 4 * 98) / (100 + 99 + 98), 0.0001,
    )
    assert used_scores_num == 3

    calculator = rating_calculation._RatingCalculator(20, 1, 5, 5)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert rating == pytest.approx(
        (2 * 20 + 3 * 19 + 4 * 18 + 5 * (17 + 16)) / (20 + 19 + 18 + 17 + 16),
        0.0001,
    )
    assert used_scores_num == 3


def test_enough_scores_padding(pgsql):
    scores = select_scores(pgsql, 'driver_1')

    # orders 6-10 => '4' + padding 95 x 4
    calculator = rating_calculation._RatingCalculator(5, 5, 100, 4)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert int(rating) == 4
    assert used_scores_num == 5

    # order 3 => '5' + padding 52 x 5
    calculator = rating_calculation._RatingCalculator(1, 12, 53, 5)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert int(rating) == 5
    assert used_scores_num == 1

    # order 3-15 + padding 2 x 3 => round (!!!) -> 3
    calculator = rating_calculation._RatingCalculator(13, 0, 15, 3)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert int(rating) == 3
    assert used_scores_num == 13

    # order 1, 2 => '5' + padding 13 x 3 -> 5
    calculator = rating_calculation._RatingCalculator(15, 13, 15, 5)
    rating, used_scores_num, _ = calculator.get_rating(scores, [])
    assert int(rating) == 5
    assert used_scores_num == 2


@pytest.mark.config(
    RATING_CALCULATION_ENABLED=True, DRIVER_SCORES_HISTORY_LENGTH=5,
)
@pytest.mark.now(_NOW_STR)
@pytest.mark.parametrize(
    'newway',
    (
        pytest.param(False, id='oldway'),
        pytest.param(
            True,
            marks=[pytest.mark.config(RATING_CALCULATION_MODE='newway')],
            id='newway',
        ),
    ),
)
async def test_delete_overflow_tail(
        pgsql, newway, mock_unique_drivers, cron_event_logs, mocked_time,
):

    if newway:

        @mock_unique_drivers('/v1/driver/profiles/retrieve_by_uniques')
        async def _v1_driver_new(request: http.Request):
            return PROFILES_MAPPING

    await run_cron.main(
        ['driver_ratings_storage.crontasks.rating_calculation', '-t', '0'],
    )

    events = _prepare_event_logs(cron_event_logs)
    utc_timestamp = int(mocked_time.now().timestamp())
    local_timestamp = utc_timestamp + _LOCAL_TZ_OFFSET

    assert events == [
        {
            'unique_driver_id': profile['unique_driver_id'],
            'rating': 5,
            'updated_at': _NOW_WITH_TZ,
            'timestamp': local_timestamp,
        }
        for profile in PROFILES_MAPPING['profiles']
    ]

    cursor = pgsql['driver_ratings_storage'].cursor()
    cursor.execute('SELECT * FROM driver_ratings_storage.scores ')
    # the newest 5 scores are equal to '3'
    for row in cursor:
        assert row[2] == 3
    cursor.close()


@pytest.mark.config(RATING_CALCULATION_ENABLED=True, DRIVER_SCORE_TTL=1)
@pytest.mark.now(_NOW_STR)
@pytest.mark.skip('fix or remove this test after remove old ratings')
@pytest.mark.parametrize(
    'newway',
    (
        pytest.param(False, id='oldway'),
        pytest.param(
            True,
            marks=[pytest.mark.config(RATING_CALCULATION_MODE='newway')],
            id='newway',
        ),
    ),
)
async def test_delete_expired_tail(
        pgsql, newway, mock_unique_drivers, cron_event_logs,
):
    if newway:

        @mock_unique_drivers('/v1/driver/profiles/retrieve_by_uniques')
        async def _v1_driver_new(request: http.Request):
            return PROFILES_MAPPING

    await run_cron.main(
        ['driver_ratings_storage.crontasks.rating_calculation', '-t', '0'],
    )

    assert not cron_event_logs

    cursor = pgsql['driver_ratings_storage'].cursor()
    cursor.execute('SELECT * FROM driver_ratings_storage.scores')

    for _ in cursor:
        assert False

    cursor.execute('SELECT * FROM driver_ratings_storage.drivers')

    for _ in cursor:
        assert False
    cursor.close()


@pytest.mark.now(_NOW_STR)
@pytest.mark.pgsql(
    'driver_ratings_storage', files=['pg_driver_scores_ignored.sql'],
)
async def test_rating_calculation_ignore_in_details(pgsql, cron_event_logs):
    scores = select_scores(pgsql, 'driver_2')

    calculator = rating_calculation._RatingCalculator(20, 1, 1, 5)
    active = [x for x in scores if x.ignore_started_at is None]
    ignored = [x for x in scores if x.ignore_started_at is not None]
    rating, used_scores_num, details = calculator.get_rating(active, ignored)
    assert int(rating) == 5
    assert used_scores_num == 3
    assert len(details) == 3
    assert not cron_event_logs


@pytest.mark.config(
    RATING_CALCULATION_ENABLED=True, RATING_PSQL_CHUNK_GET_DRIVER_IDS=3,
)
@pytest.mark.now(_NOW_STR)
@pytest.mark.pgsql(
    'driver_ratings_storage',
    queries=[
        """
        INSERT INTO driver_ratings_storage.drivers (driver_id)
        VALUES ('1'), ('2'), ('3'), ('4')
        """,
    ],
    files=['pg_driver_ratings_storage.sql'],
)
async def test_driver_cursor(pgsql, cron_event_logs, mocked_time):
    await run_cron.main(
        ['driver_ratings_storage.crontasks.rating_calculation', '-t', '0'],
    )

    cursor = pgsql['driver_ratings_storage'].cursor()
    cursor.execute('SELECT * FROM driver_ratings_storage.drivers')

    rating_by_udid = {}
    for driver in cursor:
        assert driver[4]
        rating_by_udid[driver[0]] = driver[1]

    cursor.close()

    events = _prepare_event_logs(cron_event_logs)
    assert len(rating_by_udid) == len(events)
    for event in events:
        udid = event['unique_driver_id']
        assert rating_by_udid[udid] == 5


@pytest.mark.config(
    RATING_CALCULATION_ENABLED=True, RATING_PSQL_CHUNK_GET_DRIVER_IDS=3,
)
@pytest.mark.now(_NOW_STR)
@pytest.mark.pgsql(
    'driver_ratings_storage', files=['pg_driver_scores_ignored.sql'],
)
async def test_driver_cursor_ignored(pgsql, cron_event_logs, mocked_time):
    await run_cron.main(
        ['driver_ratings_storage.crontasks.rating_calculation', '-t', '0'],
    )

    cursor = pgsql['driver_ratings_storage'].cursor()
    cursor.execute(
        'SELECT driver_id, rating FROM driver_ratings_storage.drivers',
    )

    for driver in (x for x in cursor if x[0] == 'driver_2'):
        assert driver[1] == 5

    cursor.close()

    events = _prepare_event_logs(cron_event_logs)
    assert events == [
        {
            'unique_driver_id': 'driver_2',
            'rating': 5,
            'updated_at': _NOW_WITH_TZ,
            'timestamp': mocked_time.now().timestamp() + _LOCAL_TZ_OFFSET,
        },
    ]


@pytest.mark.config(
    RATING_CALCULATION_ENABLED=True, RATING_PSQL_CHUNK_GET_DRIVER_IDS=3,
)
@pytest.mark.now(_NOW_STR)
@pytest.mark.parametrize(
    'newway',
    (
        pytest.param(False, id='oldway'),
        pytest.param(
            True,
            marks=[pytest.mark.config(RATING_CALCULATION_MODE='newway')],
            id='newway',
        ),
    ),
)
async def test_driver_previous_rating(
        pgsql, newway, mock_unique_drivers, cron_event_logs, mocked_time,
):
    if newway:

        @mock_unique_drivers('/v1/driver/profiles/retrieve_by_uniques')
        async def _v1_driver_new(request: http.Request):
            return PROFILES_MAPPING

    await run_cron.main(
        ['driver_ratings_storage.crontasks.rating_calculation', '-t', '0'],
    )

    cursor = pgsql['driver_ratings_storage'].cursor()
    cursor.execute(
        'SELECT driver_id, rating '
        'FROM driver_ratings_storage.ratings_history',
    )
    assert list(cursor) == [('driver_2', 3.0)]

    cursor.close()

    events = _prepare_event_logs(cron_event_logs)
    local_timestamp = mocked_time.now().timestamp() + _LOCAL_TZ_OFFSET
    assert events == [
        {
            'unique_driver_id': 'driver_1',
            'rating': 5.0,
            'updated_at': _NOW_WITH_TZ,
            'timestamp': local_timestamp,
        },
        {
            'unique_driver_id': 'driver_2',
            'rating': 5,
            'updated_at': _NOW_WITH_TZ,
            'timestamp': local_timestamp,
        },
    ]
