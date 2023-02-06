import pytest

NOW = '2020-11-01T00:00:00+03:00'
SHORT_AGO = '2020-10-31T23:30:00+03:00'
LONG_AGO = '2020-10-31T21:30:00+03:00'
VERY_LONG_AGO = '2020-10-31T17:30:00+03:00'
PARK_ID = 'some_park_id'
DRIVER_ID = 'some_driver_id'


def _make_query(timestring: str) -> str:
    return f"""
        INSERT INTO random_bonus.progress
          (park_id, driver_id, progress, is_first,
           last_status,
           status_updated_at, last_online_at,
           last_bonus_at)
        VALUES
          ('{PARK_ID}', '{DRIVER_ID}', 10, FALSE,
           'online'::random_bonus.STATUS,
           '{timestring}'::TIMESTAMPTZ, '{timestring}'::TIMESTAMPTZ,
           '{timestring}'::TIMESTAMPTZ);"""


@pytest.mark.now(NOW)
@pytest.mark.config(
    RANDOM_BONUS_PROGRESS_CALCULATOR_SETTINGS={
        'enabled': True,
        'active_period_m': 120,
        'break_period_m': 360,
        'chunk_size': 10,
        'rules': {
            'first': {'online': 2, 'onorder': 5},
            'other': {'online': 0.4, 'onorder': 1},
        },
    },
)
@pytest.mark.parametrize(
    'expected',
    [
        pytest.param((0, True, 'offline'), id='no_initial_record'),
        pytest.param(
            (10.0, False, 'offline'),
            id='short_break',
            marks=pytest.mark.pgsql(
                'random-bonus-db', queries=[_make_query(SHORT_AGO)],
            ),
        ),
        pytest.param(
            (0.0, False, 'offline'),
            id='long_break',
            marks=pytest.mark.pgsql(
                'random-bonus-db', queries=[_make_query(LONG_AGO)],
            ),
        ),
        pytest.param(
            (0.0, True, 'offline'),
            id='very_long_break',
            marks=pytest.mark.pgsql(
                'random-bonus-db', queries=[_make_query(VERY_LONG_AGO)],
            ),
        ),
    ],
)
async def test_random_bonus_on_login(
        taxi_contractor_random_bonus, mockserver, pgsql, expected,
):
    response = await taxi_contractor_random_bonus.post(
        '/internal/random-bonus/v1/on-login',
        json={'park_id': PARK_ID, 'driver_profile_id': DRIVER_ID},
    )

    assert response.status_code == 200

    with pgsql['random-bonus-db'].cursor() as cursor:
        cursor.execute(
            """
            SELECT progress, is_first, last_status::TEXT
            FROM random_bonus.progress;
            """,
        )
        response = cursor.fetchall()
        assert len(response) == 1
        assert response[0] == expected
