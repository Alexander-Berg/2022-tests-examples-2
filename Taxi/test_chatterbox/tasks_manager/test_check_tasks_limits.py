# pylint: disable=protected-access
import dataclasses
import datetime

import pytest

from chatterbox.internal import tasks_manager as tasks_manager_module


@pytest.mark.parametrize(
    'status, stats_response, expected_count',
    [
        (
            200,
            [
                {
                    'key': 'tester',
                    'actions': [
                        {'name': 'close', 'count': 2},
                        {'name': 'create', 'count': 1},
                    ],
                },
            ],
            2,
        ),
        (
            200,
            [
                {
                    'key': 'tester',
                    'actions': [
                        {'name': 'close', 'count': 2},
                        {'name': 'create', 'count': 3},
                        {'name': 'defer', 'count': 2},
                        {'name': 'dismiss', 'count': 2},
                    ],
                },
            ],
            6,
        ),
        (400, [], None),
        (200, [], None),
    ],
)
async def test_completed_count_by_login(
        cbox, patch_get_action_stat, stats_response, status, expected_count,
):
    login = 'tester'
    patch_get_action_stat(result=stats_response, status=status, login=login)

    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login=login,
    )
    supporter_state = dataclasses.replace(
        supporter_state,
        shift_start=datetime.datetime(2018, 5, 5, 12),
        shift_finish=datetime.datetime(2018, 5, 5, 18),
    )

    count = await cbox.app.tasks_manager._get_completed_count_by_login(
        supporter_state,
    )
    assert count == expected_count


@pytest.mark.parametrize(
    'login, stat_completed_count',
    [
        ('user_without_limit', 10),
        ('user_without_limit', None),
        ('user_with_limit', None),
        ('user_with_limit', 10),
        ('user_with_limit', 20),
        ('user_with_limit', 15),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_check_limits(
        cbox,
        patch_get_action_stat,
        mock_get_completed_tasks_count,
        login,
        stat_completed_count,
):

    stat_count_mock = mock_get_completed_tasks_count(stat_completed_count)

    tasks_manager = cbox.app.tasks_manager
    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login=login,
    )
    max_tickets_per_shift = supporter_state.max_tickets_per_shift
    raise_exception = False
    if max_tickets_per_shift is not None and stat_completed_count is not None:
        raise_exception = True

    if raise_exception and max_tickets_per_shift <= stat_completed_count:
        with pytest.raises(
                tasks_manager_module.MaxShiftTicketsExceedException,
        ):
            await tasks_manager.check_tasks_per_shift_limits(supporter_state)
    else:
        await tasks_manager.check_tasks_per_shift_limits(supporter_state)

    if max_tickets_per_shift is not None:
        assert stat_count_mock.calls
