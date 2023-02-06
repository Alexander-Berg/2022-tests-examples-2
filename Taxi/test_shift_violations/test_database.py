import typing as tp

import pytest

from workforce_management.common import exceptions
from workforce_management.common import utils
from workforce_management.common.models import (
    shift_violations as violations_module,
)
from workforce_management.storage.postgresql import (
    actual_shifts as actual_shifts_db,
)
from . import data


@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'violations': [
                    {
                        'duration_minutes': None,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                        'yandex_uid': 'uid1',
                        'finish': None,
                        'violation_id': 1,
                    },
                ],
                'states': [
                    {
                        'duration_minutes': None,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                        'yandex_uid': 'uid1',
                        'finish': None,
                        'violation_id': 1,
                    },
                ],
            },
            [],
            id='continue_violation',
        ),
        pytest.param(
            {
                'violations': [
                    {
                        'duration_minutes': None,
                        'start': data.add_minutes(0),
                        'state_type': 'absent',
                        'yandex_uid': 'uid1',
                        'finish': None,
                        'violation_id': 1,
                    },
                ],
                'states': [
                    {
                        'duration_minutes': None,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                        'yandex_uid': 'uid1',
                        'finish': None,
                        'violation_id': 1,
                    },
                ],
            },
            [
                {
                    'duration_minutes': None,
                    'start': data.add_minutes(0),
                    'state_type': 'absent',
                    'yandex_uid': 'uid1',
                    'finish': None,
                    'violation_id': 1,
                },
            ],
            id='modified_violation',
        ),
        pytest.param(
            {
                'violations': [
                    {
                        'duration_minutes': 25,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                        'yandex_uid': 'uid1',
                        'finish': data.add_minutes(25),
                        'violation_id': None,
                    },
                ],
                'states': [
                    {
                        'duration_minutes': 0,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                        'yandex_uid': 'uid1',
                        'finish': data.add_minutes(0),
                        'violation_id': 1,
                    },
                ],
            },
            [],
            id='new_violation',
        ),
    ],
)
async def test_modified_violations(kwargs, expected_res):
    res = violations_module.utils.filter_modified_violations(**kwargs)
    assert res == expected_res


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'shift_skills': ['pokemon'],
    },
)
@pytest.mark.now(data.add_minutes(45).isoformat())
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'extra_shift.sql'],
)
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'start': data.add_minutes(1),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'late',
                        'shift_id': None,
                        'start': data.add_minutes(0),
                        'updated_at': data.add_minutes(0),
                    },
                ],
            },
            ['disconnected', 'late'],
            id='recalc_on_new_current_shift',
        ),
        pytest.param(
            {
                'start': data.add_minutes(45),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'not_working',
                        'shift_id': 10,
                        # start < window.start < shift.finish
                        'start': data.add_minutes(30),
                        # > shift.range_updated_at
                        'updated_at': data.add_minutes(30),
                    },
                ],
            },
            ['not_working'],
            id='valid_violation',
        ),
        pytest.param(
            {
                'start': data.add_minutes(1),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'late',
                        'shift_id': 10,
                        # start < window.start < shift.finish
                        'start': data.add_minutes(0),
                        # < shift.range_updated_at
                        'updated_at': data.add_minutes(0),
                    },
                ],
            },
            ['disconnected', 'late'],
            id='recalc_on_related_shift_update',
        ),
        pytest.param(
            {
                'start': data.add_minutes(100),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'late',
                        'shift_id': 11,
                        # < shift.start
                        'start': data.add_minutes(60),
                        'updated_at': data.add_minutes(60),
                    },
                ],
            },
            ['disconnected'],
            id='shift_moved_to_future',
        ),
        pytest.param(
            {
                'start': data.add_minutes(61),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'overtime',
                        'shift_id': 11,
                        # < shift.start
                        'start': data.add_minutes(60),
                        'updated_at': data.add_minutes(60),
                    },
                ],
            },
            ['connected'],
            id='shift_moved_to_future_overtime',
        ),
        pytest.param(
            {
                'start': data.add_minutes(300),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'not_working',
                        'shift_id': 13,
                        # > shift.finish
                        'start': data.add_minutes(240 + 10),
                        # < shift.range_updated_at
                        'updated_at': data.add_minutes(240 + 10),
                    },
                ],
            },
            ['disconnected'],
            id='shift_moved_to_past_before_actual_state',
        ),
        pytest.param(
            {
                'start': data.add_minutes(300),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'not_working',
                        'shift_id': 13,
                        # <= shift.finish
                        'start': data.add_minutes(240 - 5),
                        # < shift.range_updated_at
                        'updated_at': data.add_minutes(240 - 5),
                    },
                ],
            },
            ['disconnected'],
            id='shift_moved_to_past_after_actual_state',
        ),
        pytest.param(
            {
                'start': data.add_minutes(300),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'not_working',
                        'shift_id': 13,
                        # > shift.finish
                        'start': data.add_minutes(240 + 15),
                        # > shift.range_updated_at
                        'updated_at': data.add_minutes(240 + 20),
                    },
                ],
            },
            ['disconnected'],
            id='state_updated_while_shift_in_transaction',
        ),
    ],
)
async def test_revision(stq3_context, kwargs, expected_res):
    cs_events_db = actual_shifts_db.ActualShiftsRepo(stq3_context)
    sv_obj = violations_module.ShiftViolations(stq3_context)

    async with cs_events_db.master.acquire() as conn:
        await sv_obj.db.commit_cursor(conn, kwargs['start'])
        await cs_events_db.save_operators_actual_states(conn, kwargs['states'])

    await sv_obj.process_markers(events=[], period_interval_sec=5)

    async with cs_events_db.master.acquire() as conn:
        states_records = await sv_obj.db.get_actual_states(
            conn, yandex_uids=['uid4'],
        )
        actual_states_map = utils.map_by_yandex_uid(
            violations_module.utils.make_state(state)
            for state in states_records
        )
        shifts = await sv_obj.db.get_shifts(
            conn,
            datetime_from=data.add_minutes(0),
            datetime_to=data.add_minutes(600),
        )

    state_types = [
        state['state_type']
        for states in actual_states_map.values()
        for state in states
    ]
    for shift in shifts:
        assert shift['author_yandex_uid'] == 'uid1'

    assert state_types == expected_res


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'shift_skills': ['not_shifts_skill'],
    },
)
@pytest.mark.now(data.add_minutes(45).isoformat())
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'extra_shift.sql'],
)
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'start': data.add_minutes(1),
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'late',
                        'shift_id': None,
                        'start': data.add_minutes(0),
                        'updated_at': data.add_minutes(0),
                    },
                ],
            },
            [],
            id='shift_skill_is_not_provided_in_config',
        ),
    ],
)
async def test_wrong_skill(stq3_context, kwargs, expected_res):
    cs_events_db = actual_shifts_db.ActualShiftsRepo(stq3_context)
    sv_obj = violations_module.ShiftViolations(stq3_context)

    async with cs_events_db.master.acquire() as conn:
        await sv_obj.db.commit_cursor(conn, kwargs['start'])
        await cs_events_db.save_operators_actual_states(conn, kwargs['states'])

        await sv_obj.process_markers(events=[], period_interval_sec=5)

        states_records = await sv_obj.db.get_actual_states(conn)

    state_types = [state['state_type'] for state in states_records]

    assert state_types == expected_res


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'disconnected',
                        'start': data.add_minutes(0),
                        'skill': 'pokemon',
                        'shift_id': None,
                        'violation_id': 1,
                    },
                ],
                'markers': [],
                'cursor': data.add_minutes(0),
            },
            [
                {
                    'state_type': 'disconnected',
                    'yandex_uid': 'uid4',
                    'violation_id': None,
                },
            ],
            id='delete_once',
        ),
        pytest.param(
            {
                'states': [
                    {
                        'yandex_uid': 'uid4',
                        'state_type': 'disconnected',
                        'start': data.add_minutes(0),
                        'skill': None,
                        'shift_id': None,
                        'violation_id': None,
                    },
                ],
                'markers': [
                    {
                        'id': 1,
                        'shift_id': 1,
                        'marker_type': 'shift_start',
                        'skill': 'pokemon',
                        'start': data.add_minutes(0),
                        'yandex_uid': 'uid4',
                    },
                ],
                'cursor': data.add_minutes(45),
            },
            [],
            id='deleted_shift_marker',
        ),
    ],
)
async def test_process_single_operator(stq3_context, kwargs, expected_res):
    cs_events_db = actual_shifts_db.ActualShiftsRepo(stq3_context)
    sv_obj = violations_module.ShiftViolations(stq3_context)

    await sv_obj.process_single_operator(**kwargs)

    async with cs_events_db.master.acquire() as conn:
        states_records = await sv_obj.db.get_actual_states(conn)
    actual_states = [
        violations_module.utils.make_state(state) for state in states_records
    ]

    assert data.expected_fields(actual_states, expected_res) == expected_res


@pytest.mark.parametrize(
    'new_violations, expected_res',
    [
        pytest.param(
            [
                {
                    'start': data.add_minutes(0),
                    'finish': data.add_minutes(30.0),
                    'state_type': 'late',
                    'yandex_uid': 'uid1',
                    'shift_id': 1,
                },
                {
                    'start': data.add_minutes(29.0),
                    'finish': data.add_minutes(60.0),
                    'state_type': 'late',
                    'yandex_uid': 'uid1',
                    'shift_id': 1,
                },
            ],
            False,
            id='intersects',
        ),
    ],
)
async def test_save(stq3_context, new_violations: tp.List, expected_res: bool):
    cs_events_db = actual_shifts_db.ActualShiftsRepo(stq3_context)
    sv_obj = violations_module.ShiftViolations(stq3_context)
    new_violations = [
        violations_module.utils.make_state(state) for state in new_violations
    ]
    async with cs_events_db.master.acquire() as conn:
        try:
            await sv_obj.db.save_violations(conn, new_violations)
            res = True
        except exceptions.WrongDataError:
            res = False
    assert res == expected_res


ACTUAL_STATES = [
    {
        'start': data.add_minutes(x),
        'state_type': 'disconnected',
        'yandex_uid': uid,
    }
    for uid in {'uid1', 'uid2', 'uid3'}
    for x in range(5)
]


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_actual_states.sql',
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_len',
    [
        pytest.param(
            {'states': ACTUAL_STATES, 'yandex_uids': ['uid1', 'uid2', 'uid3']},
            6,
            id='modify_multiple',
        ),
    ],
)
async def test_modify_actual_states(stq3_context, kwargs, expected_len):
    sv_obj = violations_module.ShiftViolations(stq3_context)
    pool = sv_obj.db.cs_events_db.master

    kwargs['states'] = [
        violations_module.utils.make_state(state) for state in kwargs['states']
    ]

    async with pool.acquire() as conn:
        await sv_obj.db.modify_actual_states(
            conn, new_actual_states=kwargs['states'],
        )
        states_records = await sv_obj.db.get_actual_states(
            conn, yandex_uids=kwargs['yandex_uids'],
        )

    assert len(states_records) == expected_len


@pytest.mark.now(data.add_minutes(30).isoformat())
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'extra_shift.sql'],
)
@pytest.mark.parametrize(
    'kwargs, expected_count',
    [
        pytest.param(
            {
                'states': [
                    {
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                        'yandex_uid': 'uid4',
                        'shift_id': 10,
                        'updated_at': data.add_minutes(0),
                        'skill': None,
                        'violation_id': None,
                    },
                ],
                'yandex_uids': ['uid4'],
            },
            1,
            id='related_shift_modified',
        ),
    ],
)
async def test_recursion(stq3_context, kwargs, expected_count, patch):
    sv_obj = violations_module.ShiftViolations(stq3_context)
    pool = sv_obj.db.cs_events_db.master

    counter = 0

    @patch(
        'workforce_management.common.models.shift_violations.db'
        '.ShiftViolationsRepo.delete_markers_revision',
    )
    async def _delete_markers_revision(*_args, **_kwargs):
        nonlocal counter
        counter += 1
        if counter > expected_count:
            raise RuntimeError('Recursion detected')

    async with pool.acquire() as conn:
        await sv_obj.db.cs_events_db.save_operators_actual_states(
            conn, kwargs['states'],
        )
        await sv_obj.process_markers(events=list(), period_interval_sec=0)

    assert counter == expected_count
