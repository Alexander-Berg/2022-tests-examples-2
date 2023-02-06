import datetime as dt
import math

import pytest

# pylint: disable=redefined-outer-name
from random_bonus.generated.cron import run_cron


NOW_ISO = '2020-11-01T00:00:00+03:00'
NOW_UTC_ISO = '2020-10-31T21:00:00+00:00'
WAS_ISO = '2020-10-15T00:00:00+03:00'
CFG: dict = {
    'enabled': True,
    'active_period_m': 120,
    'break_period_m': 360,
    'chunk_size': 10,
    'rules': {
        'first': {'online': 2, 'onorder': 5},
        'other': {'online': 0.4, 'onorder': 1},
    },
}

EXPECTED = [
    (
        'park1',
        'driver1',
        float(0 + 2),
        True,
        'online',
        # dt.datetime.fromisoformat(NOW_ISO),
        # dt.datetime.fromisoformat(NOW_ISO),
    ),
    (
        'park2',
        'driver2',
        float(15 + 0),
        True,
        'online',
        # dt.datetime.fromisoformat(NOW_ISO),
        # dt.datetime.fromisoformat(NOW_ISO),
    ),
    (
        'park3',
        'driver3',
        float(50 + 1),
        False,
        'onorder',
        # dt.datetime.fromisoformat(NOW_ISO),
        # dt.datetime.fromisoformat(NOW_ISO),
    ),
    (
        'park4',
        'driver4',
        float(85 + 0),
        False,
        'online',
        # dt.datetime.fromisoformat(NOW_ISO),
        # dt.datetime.fromisoformat(NOW_ISO),
    ),
    (
        'park5',
        'driver5',
        float(80 - 80),
        False,
        'online',
        # dt.datetime.fromisoformat(NOW_ISO),
        # dt.datetime.fromisoformat(NOW_ISO),
    ),
    (
        'park6',
        'driver6',
        float(99.95 + 5 - 100),
        False,  # was True but got his bonus
        'onorder',
        # dt.datetime.fromisoformat(NOW_ISO),
        # dt.datetime.fromisoformat(NOW_ISO),
    ),
    (
        'park8',
        'driver8',
        float(77),
        False,
        'offline',
        # dt.datetime.fromisoformat('2020-10-31T19:00:00+03:00'),
        # dt.datetime.fromisoformat('2020-10-31T17:00:00+03:00'),
    ),
]


def _make_status(num: int, order_status: str):
    def to_milliseconds(timestring: str) -> int:
        return (
            int(
                dt.datetime.fromisoformat(timestring)
                .astimezone(tz=dt.timezone.utc)
                .timestamp(),
            )
            * 1000
        )

    return {
        'park_id': f'park{num}',
        'driver_id': f'driver{num}',
        'status': 'online',  # doesnt affect progress
        'updated_ts': to_milliseconds(NOW_ISO),
        **(
            {'orders': [{'id': 'id', 'status': order_status}]}
            if order_status
            else {}
        ),
    }


STATUSES_RESPONSES = {
    '1': _make_status(1, 'complete'),
    '2': _make_status(2, ''),
    '3': _make_status(3, 'transporting'),
    '4': _make_status(4, ''),
    '5': _make_status(5, ''),
    '6': _make_status(6, 'driving'),
}


def _compare(lhs, rhs):
    for i in [0, 1, 3, 4]:
        if lhs[i] != rhs[i]:
            return False
    return math.isclose(lhs[2], rhs[2])


@pytest.mark.config(RANDOM_BONUS_PROGRESS_CALCULATOR_SETTINGS=CFG)
@pytest.mark.now(NOW_ISO)
@pytest.mark.pgsql(
    'random_bonus_db',
    queries=[
        f"""
        INSERT INTO random_bonus.key_value (key, value)
        VALUES ('progress_last_run_at', '{WAS_ISO}'::TIMESTAMPTZ);
        """,
    ],
)
async def test_progress_calculator_empty(pgsql):
    await run_cron.main(
        ['random_bonus.crontasks.progress_calculator', '-t', '0'],
    )

    with pgsql['random_bonus_db'].cursor() as cursor:
        cursor.execute(
            """
            SELECT value
            FROM random_bonus.key_value
            WHERE key = 'progress_last_run_at';
            """,
        )
        row = cursor.fetchone()

        assert dt.datetime.fromisoformat(row[0]).astimezone(
            tz=dt.timezone.utc,
        ) == dt.datetime.fromisoformat(NOW_ISO).astimezone(tz=dt.timezone.utc)


@pytest.mark.config(RANDOM_BONUS_PROGRESS_CALCULATOR_SETTINGS=CFG)
@pytest.mark.now(NOW_ISO)
@pytest.mark.pgsql('random_bonus_db', files=['initial_progresses.sql'])
async def test_progress_calculator_action(mockserver, pgsql):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status_mock(request):
        assert request.json == {
            'driver_ids': [
                {'park_id': f'park{num}', 'driver_id': f'driver{num}'}
                for num in [5, 4, 6, 3, 2, 1]  # last_online_at ASC
            ],
        }

        return {'statuses': list(STATUSES_RESPONSES.values())}

    @mockserver.json_handler('/stq-agent/queues/api/add', prefix=True)
    def _stq_agent(request):
        assert request.json['args'] == ['park6', 'driver6', True, NOW_UTC_ISO]
        return {}

    await run_cron.main(
        ['random_bonus.crontasks.progress_calculator', '-t', '0'],
    )

    with pgsql['random_bonus_db'].cursor() as cursor:
        cursor.execute(
            """
            SELECT park_id, driver_id, progress, is_first, last_status
                   -- , status_updated_at::TIMESTAMPTZ
                   -- , last_online_at::TIMESTAMPTZ
            FROM random_bonus.progress
            ORDER BY driver_id ASC;
            """,
        )
        for item, expected in zip(cursor.fetchall(), EXPECTED):
            assert _compare(item, expected)

        cursor.execute(
            """
            SELECT last_bonus_at::TIMESTAMPTZ
            FROM random_bonus.progress
            WHERE park_id = 'park6' AND driver_id = 'driver6';
            """,
        )
        last_bonus_at = cursor.fetchone()[0]
        assert last_bonus_at == dt.datetime.fromisoformat(NOW_ISO)


@pytest.mark.config(
    RANDOM_BONUS_PROGRESS_CALCULATOR_SETTINGS={
        'enabled': True,
        'active_period_m': 120,
        'break_period_m': 360,
        'chunk_size': 2,  # !
        'rules': {
            'first': {'online': 2, 'onorder': 5},
            'other': {'online': 0.4, 'onorder': 1},
        },
    },
)
@pytest.mark.now(NOW_ISO)
@pytest.mark.pgsql('random_bonus_db', files=['initial_progresses.sql'])
async def test_progress_calculator_chunks(mockserver, pgsql):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status_mock(request):
        assert request.json in [
            {
                'driver_ids': [
                    {'park_id': f'park{num}', 'driver_id': f'driver{num}'}
                    for num in nums  # last_online_at ASC
                ],
            }
            for nums in [[5, 4], [6, 3], [2, 1]]
        ]

        nums = [
            item['driver_id'][len('driver') :]
            for item in request.json['driver_ids']
        ]
        return {'statuses': [STATUSES_RESPONSES[num] for num in nums]}

    await run_cron.main(
        ['random_bonus.crontasks.progress_calculator', '-t', '0'],
    )

    with pgsql['random_bonus_db'].cursor() as cursor:
        cursor.execute(
            """
            SELECT park_id, driver_id, progress, is_first, last_status
                   -- , status_updated_at::TIMESTAMPTZ
                   -- , last_online_at::TIMESTAMPTZ
            FROM random_bonus.progress
            ORDER BY driver_id ASC;
            """,
        )
        for item, expected in zip(cursor.fetchall(), EXPECTED):
            assert _compare(item, expected)


@pytest.mark.config(RANDOM_BONUS_PROGRESS_CALCULATOR_SETTINGS=CFG)
@pytest.mark.now(NOW_ISO)
@pytest.mark.pgsql('random_bonus_db', files=['initial_progresses.sql'])
async def test_progress_calculator_stq_fail(mockserver, pgsql):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status_mock(request):
        assert request.json == {
            'driver_ids': [
                {'park_id': f'park{num}', 'driver_id': f'driver{num}'}
                for num in [5, 4, 6, 3, 2, 1]  # last_online_at ASC
            ],
        }

        return {'statuses': list(STATUSES_RESPONSES.values())}

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _stq_mock(request, queue_name):
        return mockserver.make_response(status=500)  # any error is ok here

    with pgsql['random_bonus_db'].cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM random_bonus.progress
            WHERE park_id = 'park6' AND driver_id = 'driver6';
            """,
        )
        driver_6 = cursor.fetchone()

        await run_cron.main(
            ['random_bonus.crontasks.progress_calculator', '-t', '0'],
        )

        cursor.execute(
            """
            SELECT *
            FROM random_bonus.progress
            WHERE park_id = 'park6' AND driver_id = 'driver6';
            """,
        )
        assert cursor.fetchone() == driver_6

        cursor.execute(
            """
            SELECT park_id, driver_id, progress, is_first, last_status
                   -- , status_updated_at::TIMESTAMPTZ
                   -- , last_online_at::TIMESTAMPTZ
            FROM random_bonus.progress
            ORDER BY driver_id ASC;
            """,
        )
        for item, expected in zip(cursor.fetchall(), EXPECTED):
            if item[1] == 'driver6':
                # without 100% progress all is ok
                continue

            assert _compare(item, expected)
