import pytest

from workforce_management.common.constants import (
    shift_violations as sv_constants,
)
from workforce_management.common.models import (
    shift_violations as violations_module,
)
from workforce_management.storage.postgresql import (
    actual_shifts as actual_shifts_db,
)
from . import data


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SHIFT_VIOLATIONS_SETTINGS={
        'batched_markers_processing': True,
    },
)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'phone_queues': ['pokemon'],
        'shift_skills': ['pokemon'],
    },
)
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_actual_states.sql',
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'yandex_uids': ['uid1'],
                'events': [],
                'start': data.add_minutes(0),
                'end': data.add_minutes(0.5),
            },
            {
                'markers': [
                    {
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(0),
                    },
                    {
                        'marker_type': 'break_start',
                        'start': data.add_minutes(0),
                    },
                ],
                'violations': [],
                'actual_states': [
                    {
                        'start': data.add_minutes(-0.5),
                        'state_type': 'disconnected',
                    },
                    {
                        'start': data.add_minutes(0),
                        'state_type': 'late_and_break',
                    },
                ],
            },
            id='not_late_yet',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid1'],
                'events': [],
                'start': data.add_minutes(0),
                'end': data.add_minutes(5.5),
            },
            {
                'violations': [
                    {
                        'duration_minutes': None,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                    },
                ],
                'actual_states': [
                    {
                        'start': data.add_minutes(-0.5),
                        'state_type': 'disconnected',
                        'violation_id': None,
                    },
                    {
                        'start': data.add_minutes(0),
                        'state_type': 'late_and_break',
                        'violation_id': 2,
                    },
                ],
            },
            id='late',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid1'],
                'events': [],
                'start': data.add_minutes(0),
                'end': data.add_minutes(120.5),
            },
            {
                'violations': [
                    {
                        'duration_minutes': 60,
                        'start': data.add_minutes(0),
                        'state_type': 'absent',
                        'shift_id': 1,
                    },
                    {
                        'duration_minutes': 60,
                        'start': data.add_minutes(60),
                        'state_type': 'absent',
                        'shift_id': 3,
                    },
                ],
            },
            id='double_late',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid1'],
                'events': data.EVENTS_CONNECT,
                'start': data.add_minutes(0),
                'end': data.add_minutes(60.5),
            },
            {
                'markers': [
                    {
                        'marker_type': 'shift_start',
                        'shift_id': 1,
                        'start': data.add_minutes(0),
                    },
                    {
                        'marker_type': 'break_start',
                        'shift_id': 1,
                        'start': data.add_minutes(0),
                    },
                    {
                        'marker_type': 'connect',
                        'shift_id': None,
                        'start': data.add_minutes(5),
                    },
                    {
                        'marker_type': 'break_end',
                        'shift_id': 1,
                        'start': data.add_minutes(30),
                    },
                    {
                        'marker_type': 'shift_end',
                        'shift_id': 1,
                        'start': data.add_minutes(60),
                    },
                    {
                        'marker_type': 'shift_start',
                        'shift_id': 3,
                        'start': data.add_minutes(60),
                    },
                ],
                'violations': [
                    {
                        'duration_minutes': 5,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                    },
                    {
                        'duration_minutes': 25,
                        'start': data.add_minutes(5),
                        'state_type': 'working_on_break',
                    },
                ],
                'actual_states': [
                    {
                        'shift_id': 1,
                        'start': data.add_minutes(60),
                        'state_type': 'overtime',
                    },
                    {
                        'shift_id': 3,
                        'start': data.add_minutes(60),
                        'state_type': 'working',
                    },
                ],
            },
            id='late_connect',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid5'],
                'events': [],
                'start': data.add_minutes(5.3),
                'end': data.add_minutes(5.5),
            },
            {
                'markers': [],
                'violations': [
                    {
                        'duration_minutes': None,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                    },
                ],
            },
            id='late_saved',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid4'],
                'events': [],
                'start': data.add_minutes(241),
                'end': data.add_minutes(242),
            },
            {
                'markers': [],
                'violations': [
                    {
                        'duration_minutes': 60,
                        'start': data.add_minutes(0),
                        'state_type': 'absent',
                    },
                ],
            },
            id='late_into_absent',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid5'],
                'events': data.EVENTS_CONNECT_UID5,
                'start': data.add_minutes(12),
                'end': data.add_minutes(15),
            },
            {
                'markers': [
                    {'marker_type': 'connect', 'start': data.add_minutes(10)},
                ],
                'violations': [
                    {
                        'duration_minutes': 10,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                    },
                ],
            },
            id='delayed_event',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid1'],
                'events': [],
                'start': data.add_minutes(0),
                'end': data.add_minutes(60.25),
            },
            {
                'markers': [
                    {'marker_type': 'shift_start'},
                    {'marker_type': 'break_start'},
                    {'marker_type': 'break_end'},
                    {'marker_type': 'event_start'},
                    {'marker_type': 'event_end'},
                    {'marker_type': 'shift_end'},
                    {'marker_type': 'shift_start'},
                ],
                'violations': [
                    {
                        'duration_minutes': 30,
                        'finish': data.add_minutes(30),
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                    },
                ],
            },
            id='shift_events',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management', files=['simple_shift_events.sql'],
                ),
            ],
        ),
        pytest.param(
            {
                'yandex_uids': ['uid1'],
                'events': [],
                'start': data.add_minutes(0),
                'end': data.add_minutes(5),
            },
            {'markers': [], 'actual_states': []},
            id='state_and_invalid_skill',
            marks=[
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
                        'shift_skills': [],
                    },
                ),
            ],
        ),
    ],
)
async def test_process_markers(
        kwargs, expected_res, stq3_context, patch, monkeypatch,
):
    cs_events_db = actual_shifts_db.ActualShiftsRepo(stq3_context)
    sv_obj = violations_module.ShiftViolations(stq3_context)

    yandex_uids = set(kwargs['yandex_uids'])

    module_path = 'workforce_management.common.models.shift_violations'

    @patch(f'{module_path}.utils.get_window')
    def _(*_args, **_kwargs):
        return kwargs['start'], kwargs['end']

    flap_states = sv_constants.FLAP_STATES | {sv_constants.StateType.late}
    monkeypatch.setattr(sv_constants, 'FLAP_STATES', flap_states)

    await sv_obj.process_markers(kwargs['events'], 5)

    if 'markers' in expected_res:
        async with cs_events_db.master.acquire() as conn:
            records = await sv_obj.db.get_markers(
                conn, worker_num=0, worker_count=1,
            )
        markers = [
            violations_module.utils.extract_marker(record)
            for record in records
            if record['yandex_uid'] in yandex_uids
        ]
        assert (
            data.expected_fields(markers, expected_res['markers'])
            == expected_res['markers']
        )

    await sv_obj.batch_operators(worker_num=0, worker_count=1)

    async with cs_events_db.master.acquire() as conn:
        if 'violations' in expected_res:
            res = await cs_events_db.get_operators_shift_violations(
                conn,
                datetime_from=data.add_minutes(0),
                datetime_to=data.add_minutes(300),
            )
            violations = [
                violations_module.utils.make_violation(violation)
                for violation in res
                if violation['yandex_uid'] in yandex_uids
            ]
            assert (
                data.expected_fields(violations, expected_res['violations'])
                == expected_res['violations']
            )

        if 'actual_states' in expected_res:
            states_records = await sv_obj.db.get_actual_states(conn)
            states = [
                violations_module.utils.make_state(state)
                for state in states_records
                if state['yandex_uid'] in yandex_uids
            ]
            assert (
                data.expected_fields(states, expected_res['actual_states'])
                == expected_res['actual_states']
            )


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SHIFT_VIOLATIONS_SETTINGS={
        'batched_markers_processing': True,
    },
)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'phone_queues': ['pokemon'],
        'shift_skills': ['pokemon'],
    },
)
@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'yandex_uids': ['uid3'],
                'events': data.EVENTS_DISCONNECT_UID3,
                'start': data.add_minutes(-10),
                'end': data.add_minutes(0),
            },
            {
                'markers': [
                    {
                        'marker_type': 'disconnect',
                        'start': data.add_minutes(-5),
                    },
                ],
                'actual_states': [
                    {
                        'start': data.add_minutes(-5),
                        'state_type': 'disconnected',
                    },
                ],
            },
            id='from_event',
        ),
        pytest.param(
            {
                'yandex_uids': ['missing_uid'],
                'events': [
                    {
                        'yandex_uid': 'missing_uid',
                        'type': 'disconnected',
                        'start': data.add_minutes(5),
                        'meta_queues': ['pokemon'],
                    },
                ],
                'start': data.add_minutes(0),
                'end': data.add_minutes(5.5),
            },
            {
                'markers': [
                    {
                        'marker_type': 'disconnect',
                        'start': data.add_minutes(5),
                    },
                ],
                'actual_states': [
                    {
                        'start': data.add_minutes(5),
                        'state_type': 'disconnected',
                    },
                ],
            },
            id='from_event_missing_uid',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid3'],
                'events': [
                    {
                        'yandex_uid': 'uid3',
                        'type': 'disconnected',
                        'start': data.add_minutes(5),
                        'meta_queues': ['wrong_queue'],
                    },
                ],
                'start': data.add_minutes(0),
                'end': data.add_minutes(5.5),
            },
            {'markers': [], 'actual_states': []},
            id='from_event_wrong_queue',
        ),
    ],
)
async def test_accumulate(
        kwargs, expected_res, stq3_context, patch, monkeypatch,
):
    await test_process_markers(
        kwargs, expected_res, stq3_context, patch, monkeypatch,
    )


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SHIFT_VIOLATIONS_SETTINGS={
        'batched_markers_processing': True,
    },
)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'phone_queues': ['pokemon'],
        'shift_skills': ['pokemon'],
    },
)
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'extra_shift.sql'],
)
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'yandex_uids': ['uid3'],
                'events': [],
                'start': data.add_minutes(0),
                'end': data.add_minutes(5.5),
            },
            {
                'markers': [
                    {
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(0),
                    },
                ],
                'actual_states': [
                    {
                        'start': data.add_minutes(0),
                        'state_type': 'disconnected',
                    },
                    {'start': data.add_minutes(0), 'state_type': 'late'},
                ],
            },
            id='from_shift',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid3'],
                'events': data.EVENTS_DISCONNECT_UID3,
                'start': data.add_minutes(-10),
                'end': data.add_minutes(10),
            },
            {
                'markers': [
                    {
                        'marker_type': 'disconnect',
                        'start': data.add_minutes(-5),
                    },
                    {
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(0),
                    },
                ],
                'actual_states': [
                    {
                        'start': data.add_minutes(-5),
                        'state_type': 'disconnected',
                    },
                    {'start': data.add_minutes(0), 'state_type': 'late'},
                ],
            },
            id='from_event_and_shift',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid3'],
                'events': [
                    {
                        **data.EVENTS_DISCONNECT_UID3[0],
                        'start': data.add_minutes(5),
                    },
                ],
                'start': data.add_minutes(-10),
                'end': data.add_minutes(10),
            },
            {
                'markers': [
                    {
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(0),
                    },
                    {
                        'marker_type': 'disconnect',
                        'start': data.add_minutes(5),
                    },
                ],
                'actual_states': [
                    {
                        'start': data.add_minutes(0),
                        'state_type': 'disconnected',
                    },
                    {'start': data.add_minutes(0), 'state_type': 'late'},
                ],
            },
            id='from_event_and_shift_late',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid4'],
                'events': [
                    {
                        'yandex_uid': 'uid4',
                        'type': 'disconnected',
                        'start': data.add_minutes(-5),
                        'meta_queues': ['pokemon'],
                    },
                ],
                'start': data.add_minutes(0),
                'end': data.add_minutes(5),
            },
            {'markers': [], 'actual_states': []},
            id='valid_event_invalid_shift',
            marks=[
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
                        'phone_queues': ['pokemon'],
                        'shift_skills': [],
                    },
                ),
            ],
        ),
        pytest.param(
            {
                'yandex_uids': ['uid4'],
                'events': [
                    {
                        'yandex_uid': 'uid4',
                        'type': 'disconnected',
                        'start': data.add_minutes(1),
                        'meta_queues': ['pokemon'],
                    },
                ],
                'start': data.add_minutes(0),
                'end': data.add_minutes(5),
            },
            {'markers': [], 'actual_states': []},
            id='invalid_shift_valid_event',
            marks=[
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
                        'phone_queues': ['pokemon'],
                        'shift_skills': [],
                    },
                ),
            ],
        ),
    ],
)
async def test_accumulate_with_shift(
        kwargs, expected_res, stq3_context, patch, monkeypatch,
):
    await test_process_markers(
        kwargs, expected_res, stq3_context, patch, monkeypatch,
    )


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_SHIFT_VIOLATIONS_SETTINGS={
        'batched_markers_processing': True,
    },
)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'phone_queues': ['pokemon'],
        'shift_skills': ['pokemon'],
    },
)
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_actual_states.sql',
    ],
)
@pytest.mark.parametrize(
    'kwargs, expected_res, deleted',
    [
        pytest.param(
            {
                'yandex_uids': ['uid1'],
                'events': data.EVENTS_FLAP,
                'start': data.add_minutes(0),
                'end': data.add_minutes(20),
            },
            {
                'markers': [
                    {
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(0),
                    },
                    {
                        'marker_type': 'break_start',
                        'start': data.add_minutes(0),
                    },
                    {'marker_type': 'connect', 'start': data.add_minutes(5)},
                    {
                        'marker_type': 'connect',
                        'start': data.add_minutes(15.25),
                    },
                ],
                'violations': [
                    {
                        'duration_minutes': 5,
                        'start': data.add_minutes(0),
                        'state_type': 'late',
                    },
                    {
                        'duration_minutes': None,
                        'start': data.add_minutes(5),
                        'state_type': 'working_on_break',
                    },
                ],
            },
            [],
            id='flap',
            marks=[
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_ACTUAL_SHIFTS_SETTINGS={
                        'min_flap_interval_sec': 60,
                    },
                ),
            ],
        ),
        pytest.param(
            {
                'yandex_uids': ['uid4'],
                'events': data.EVENTS_FLAP_START,
                'start': data.add_minutes(0.1),
                'end': data.add_minutes(30.5),
            },
            {
                'markers': [
                    {
                        'marker_type': 'connect',
                        'start': data.add_minutes(0.25),
                    },
                    {
                        'marker_type': 'connect',
                        'start': data.add_minutes(15.25),
                    },
                ],
                'violations': [],
                'actual_states': [
                    {
                        'start': data.add_minutes(-1),
                        'state_type': 'disconnected',
                    },
                    {'start': data.add_minutes(0), 'state_type': 'working'},
                ],
            },
            [1],
            id='flap_on_start',
            marks=[
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_ACTUAL_SHIFTS_SETTINGS={
                        'min_flap_interval_sec': 60,
                    },
                ),
            ],
        ),
    ],
)
async def test_flaps(
        kwargs, expected_res, deleted, stq3_context, patch, monkeypatch,
):
    await test_process_markers(
        kwargs, expected_res, stq3_context, patch, monkeypatch,
    )
    db = actual_shifts_db.ActualShiftsRepo(stq3_context)
    async with db.master.acquire() as conn:
        res = await db.get_deleted_operators_shift_violations(
            conn, violation_ids=deleted,
        )
        assert len(res) == len(deleted)


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_actual_shifts.sql',
        'simple_actual_states.sql',
    ],
)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'phone_queues': ['pokemon'],
        'shift_skills': ['pokemon'],
    },
)
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            dict(shift_id=1),
            [
                {
                    'author_yandex_uid': 'uid1',
                    'duration_minutes': 30,
                    'shift_id': 1,
                    'start': data.add_minutes(0),
                    'state_type': 'working_on_break',
                    'yandex_uid': 'uid1',
                },
            ],
            id='no_events',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['extra_shift_violations.sql'],
                ),
            ],
        ),
        pytest.param(
            dict(shift_id=6),
            [
                {
                    'author_yandex_uid': 'uid1',
                    'duration_minutes': 40.5,
                    'shift_id': 6,
                    'start': data.add_minutes(180),
                    'state_type': 'late',
                    'yandex_uid': 'uid2',
                },
            ],
            id='with_events',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management', files=['simple_actual_events.sql'],
                ),
            ],
        ),
        pytest.param(
            dict(shift_id=5),
            [
                {
                    'duration_minutes': 60.0,
                    'shift_id': 5,
                    'start': data.add_minutes(240),
                    'state_type': 'absent',
                    'yandex_uid': 'uid2',
                    'author_yandex_uid': 'uid1',
                },
            ],
            id='no_actual_shift',
        ),
        pytest.param(
            dict(shift_id=1, is_current_shift=True),
            [
                {
                    'author_yandex_uid': 'uid1',
                    'duration_minutes': 30.0,
                    'shift_id': 1,
                    'start': data.add_minutes(0),
                    'state_type': 'working_on_break',
                    'yandex_uid': 'uid1',
                },
            ],
            id='is_current_shift',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['extra_shift_violations.sql'],
                ),
                pytest.mark.now(data.add_minutes(41).isoformat()),
            ],
        ),
        pytest.param(
            dict(shift_id=1),
            [
                {
                    'author_yandex_uid': 'uid1',
                    'duration_minutes': 30.0,
                    'shift_id': 1,
                    'start': data.add_minutes(0),
                    'state_type': 'working_on_break',
                    'yandex_uid': 'uid1',
                },
            ],
            id='shift_events',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management', files=['simple_shift_events.sql'],
                ),
            ],
        ),
    ],
)
async def test_single_shift(stq3_context, kwargs, expected_res):
    cs_events_db = actual_shifts_db.ActualShiftsRepo(stq3_context)
    sv_obj = violations_module.ShiftViolations(stq3_context)

    async with cs_events_db.master.acquire() as conn:
        await sv_obj.recalc_single_shift(
            conn, **kwargs, author_yandex_uid='uid1',
        )
        res = await cs_events_db.get_operators_shift_violations(
            conn,
            datetime_from=data.add_minutes(0),
            datetime_to=data.add_minutes(300),
        )

    violations = [
        violations_module.utils.make_violation(violation)
        for violation in res
        if violation['shift_id'] == kwargs['shift_id']
    ]
    assert data.expected_fields(violations, expected_res) == expected_res


@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'extra_shift.sql'],
)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'shift_skills': ['pokemon'],
    },
)
@pytest.mark.parametrize(
    'kwargs, expected_res',
    [pytest.param(dict(shift_id=12), [], id='foreign_operator')],
)
async def test_single_shift_custom(stq3_context, kwargs, expected_res):
    await test_single_shift(stq3_context, kwargs, expected_res)
