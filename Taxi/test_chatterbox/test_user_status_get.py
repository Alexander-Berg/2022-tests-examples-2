from typing import Any
from typing import Dict
from typing import List

import pytest

from testsuite.databases.pgsql import control

from chatterbox import constants
from test_chatterbox import plugins as conftest


@pytest.mark.config(
    CHATTERBOX_DASHBOARD_TIMEOUT_BY_LINE={
        '__default__': 5,
        'first': 10,
        'second': 3,
    },
)
@pytest.mark.parametrize(
    (
        'status',
        'expected_status',
        'in_additional',
        'lines',
        'expected_result_extra',
    ),
    (
        (
            'offline',
            'offline',
            False,
            [],
            {'dashboard_next_request_timeout': 5},
        ),
        (
            'online',
            'online',
            False,
            ['first'],
            {'dashboard_next_request_timeout': 10},
        ),
        (
            'online',
            'online-in-additional',
            True,
            ['second'],
            {'dashboard_next_request_timeout': 3},
        ),
        (
            'online',
            'online',
            False,
            ['first', 'second'],
            {'dashboard_next_request_timeout': 3},
        ),
    ),
)
async def test_get_status(
        cbox: conftest.CboxWrap,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        status: str,
        expected_status: str,
        in_additional: bool,
        lines: List[str],
        expected_result_extra: Dict[str, Any],
):
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', status, lines, in_additional),
    )

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    body = cbox.body_data

    skip_check_fields = (
        'status_list',
        'incoming_calls_allowed',
        'default_work_status',
        'assigned_lines',
        'can_choose_from_assigned_lines',
        'can_choose_except_assigned_lines',
    )
    for field in skip_check_fields:
        body.pop(field)

    assert body == {
        'available_modes': ['offline', 'online'],
        'current_status': expected_status,
        'lines': lines,
        'next_request_timeout': 60000,
        **expected_result_extra,
    }


@pytest.mark.parametrize(
    ('current_status', 'in_additional', 'expected_status'),
    (
        (constants.STATUS_OFFLINE, False, constants.STATUS_OFFLINE),
        (constants.STATUS_ONLINE, False, constants.STATUS_ONLINE),
        (constants.STATUS_ONLINE, True, constants.STATUS_ONLINE_IN_ADDITIONAL),
        (constants.STATUS_BEFORE_BREAK, False, constants.STATUS_BEFORE_BREAK),
        (
            constants.STATUS_BEFORE_BREAK,
            True,
            constants.STATUS_BEFORE_BREAK_IN_ADDITIONAL,
        ),
    ),
)
async def test_get_user_status_available_change(
        cbox: conftest.CboxWrap,
        pgsql: Dict[str, control.PgDatabaseWrapper],
        current_status: str,
        in_additional: bool,
        expected_status: str,
):
    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'INSERT INTO chatterbox.online_supporters ' 'VALUES (%s, %s, %s, %s)',
        ('superuser', current_status, ['first'], in_additional),
    )

    await cbox.query('/v1/user/status')
    assert cbox.status == 200
    available_status = {
        status['id'] for status in cbox.body_data['status_list']
    }
    expected_status_list = {
        expected_status,
        *constants.STATUSES_AVAILABLE_FOR_CHANGE[expected_status],
    }
    assert available_status == expected_status_list


@pytest.mark.parametrize(
    (
        'login',
        'assigned_lines',
        'can_choose_from_assigned_lines',
        'can_choose_except_assigned_lines',
    ),
    (
        ('user_not_found', [], False, True),
        ('user_with_default_values', [], False, True),
        ('user_with_custom_values', ['line_1', 'line_2'], True, False),
    ),
)
async def test_get_user_assigned_lines(
        cbox: conftest.CboxWrap,
        patch_auth,
        login,
        assigned_lines,
        can_choose_from_assigned_lines,
        can_choose_except_assigned_lines,
):
    patch_auth(login=login)
    await cbox.query('/v1/user/status')

    assert cbox.status == 200
    assert cbox.body_data['assigned_lines'] == assigned_lines
    assert (
        cbox.body_data['can_choose_from_assigned_lines']
        == can_choose_from_assigned_lines
    )
    assert (
        cbox.body_data['can_choose_except_assigned_lines']
        == can_choose_except_assigned_lines
    )
