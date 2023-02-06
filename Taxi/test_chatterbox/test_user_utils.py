from typing import Dict
from typing import List

import pytest

from testsuite.databases.pgsql import control

from chatterbox.api import user_utils
from test_chatterbox import plugins as conftest


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first_online': {'mode': 'online'},
        'second_online': {'mode': 'online'},
    },
)
@pytest.mark.parametrize(
    ('login', 'expected_result'),
    (
        ('user_without_tasks', ['offline', 'online']),
        ('user_with_only_online_in_progress_task', ['online']),
        ('user_with_only_online_offered_task', ['online']),
        ('user_with_only_online_accepted_task', ['online']),
        ('user_with_different_online_tasks', ['online']),
        ('user_with_only_offline_in_progress_task', ['offline']),
        ('user_with_online_and_offline_in_progress_task', ['online']),
    ),
)
async def test_get_user_available_modes(
        cbox: conftest.CboxWrap, login: str, expected_result: List[str],
):

    user_work_lines = await cbox.app.tasks_manager.get_user_lines_in_work(
        login=login,
    )

    result = await user_utils.get_user_available_modes(
        cbox.app, user_work_lines,
    )
    assert result == expected_result


async def test_get_in_additional_by_login(
        cbox: conftest.CboxWrap, pgsql: Dict[str, control.PgDatabaseWrapper],
):

    in_addition = await user_utils.get_in_additional_by_login(
        cbox.app, 'user_1',
    )
    assert not in_addition

    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'UPDATE chatterbox.online_supporters os '
        'SET in_additional = true '
        'WHERE os.supporter_login = %s',
        ('user_1',),
    )

    in_addition = await user_utils.get_in_additional_by_login(
        cbox.app, 'user_1',
    )
    assert in_addition


@pytest.mark.parametrize(
    (
        'user_lines',
        'assigned_lines',
        'can_choose_from_assigned_lines',
        'can_choose_except_assigned_lines',
        'output_lines',
    ),
    (
        (['line_1', 'line_2', 'line_3'], ['line_2'], False, False, ['line_2']),
        (['line_1', 'line_2', 'line_3'], ['line_2'], True, False, ['line_2']),
        (
            ['line_1', 'line_2', 'line_3'],
            ['line_2'],
            False,
            True,
            ['line_1', 'line_2', 'line_3'],
        ),
        (
            ['line_1', 'line_2', 'line_3'],
            ['line_2'],
            True,
            True,
            ['line_1', 'line_2', 'line_3'],
        ),
        ([], ['line_2'], False, False, ['line_2']),
        ([], ['line_2'], True, False, []),
        ([], ['line_2'], False, True, ['line_2']),
        ([], ['line_2'], True, True, []),
    ),
)
async def test_change_user_lines(
        user_lines,
        assigned_lines,
        can_choose_from_assigned_lines,
        can_choose_except_assigned_lines,
        output_lines,
):
    assert output_lines == user_utils.change_user_lines(
        user_lines,
        assigned_lines,
        can_choose_from_assigned_lines,
        can_choose_except_assigned_lines,
    )
