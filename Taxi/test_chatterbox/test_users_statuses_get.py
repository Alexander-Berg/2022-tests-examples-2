import datetime
from typing import Dict

import pytest

from testsuite.databases.pgsql import control

from test_chatterbox import plugins as conftest

NOW = datetime.datetime(2019, 8, 13, 11, 51, 25)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ('lines', 'logins', 'expected_result'),
    (
        (
            ['first'],
            [],
            {
                'users': [
                    {
                        'login': 'user_1',
                        'current_status': 'online',
                        'lines': ['first'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_2',
                        'current_status': 'online',
                        'lines': ['first', 'new'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_4',
                        'current_status': 'online',
                        'lines': ['first'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_5',
                        'current_status': 'offline',
                        'lines': ['first', 'second'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_7',
                        'current_status': 'offline',
                        'lines': ['first'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_8',
                        'current_status': 'before-break',
                        'lines': ['first'],
                        'time_spent_in_status': 120,
                    },
                ],
            },
        ),
        (
            ['new', 'second'],
            [],
            {
                'users': [
                    {
                        'login': 'user_2',
                        'current_status': 'online',
                        'lines': ['first', 'new'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_3',
                        'current_status': 'online',
                        'lines': ['second'],
                        'time_spent_in_status': 60,
                    },
                    {
                        'login': 'user_5',
                        'current_status': 'offline',
                        'lines': ['first', 'second'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_6',
                        'current_status': 'offline',
                        'lines': ['second'],
                        'time_spent_in_status': 30,
                    },
                ],
            },
        ),
        (
            [],
            ['user_1', 'user_8'],
            {
                'users': [
                    {
                        'login': 'user_1',
                        'current_status': 'online',
                        'lines': ['first'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_8',
                        'current_status': 'before-break',
                        'lines': ['first'],
                        'time_spent_in_status': 120,
                    },
                ],
            },
        ),
        (
            ['new', 'second'],
            ['user_1', 'user_2', 'user_3'],
            {
                'users': [
                    {
                        'login': 'user_2',
                        'current_status': 'online',
                        'lines': ['first', 'new'],
                        'time_spent_in_status': 120,
                    },
                    {
                        'login': 'user_3',
                        'current_status': 'online',
                        'lines': ['second'],
                        'time_spent_in_status': 60,
                    },
                ],
            },
        ),
    ),
)
async def test_get_status(
        cbox: conftest.CboxWrap,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        lines: str,
        logins: str,
        expected_result,
):
    params = []
    if lines:
        for line in lines:
            params.append(('lines', line))
    if logins:
        for login in logins:
            params.append(('logins', login))
    await cbox.query('/v1/users/statuses', params=params)
    assert cbox.status == 200
    assert cbox.body_data == expected_result
