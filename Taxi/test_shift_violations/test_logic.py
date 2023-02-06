# pylint: disable=too-many-lines
import pytest

from workforce_management.common import utils as c_utils
from workforce_management.common.constants import (
    shift_violations as sv_constants,
)
from workforce_management.common.models import (
    shift_violations as violations_module,
)
from . import data


@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'current_state': {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': data.MARKERS_SHIFT_START,
            },
            [
                {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(0),
                    'duration_minutes': 0,
                    'shift_id': 1,
                },
                {
                    'state_type': 'late_and_break',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='late',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': data.MARKERS_CONSECUTIVE_SHIFTS,
            },
            [
                {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(0),
                    'duration_minutes': 0,
                    'shift_id': 1,
                },
                {
                    'state_type': 'absent',
                    'start': data.add_minutes(0),
                    'duration_minutes': 60,
                    'shift_id': 1,
                },
                {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(60),
                    'duration_minutes': 0,
                    'shift_id': 1,
                },
                {
                    'state_type': 'absent',
                    'start': data.add_minutes(60),
                    'duration_minutes': 60,
                    'shift_id': 3,
                },
                {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(120),
                    'duration_minutes': 0,
                    'shift_id': 3,
                },
                {
                    'state_type': 'late',
                    'start': data.add_minutes(120),
                    'duration_minutes': None,
                    'shift_id': 2,
                },
            ],
            id='triple_late',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': c_utils.sorted_by_field(
                    data.MARKERS_CONSECUTIVE_SHIFTS + data.MARKERS_CONNECT,
                ),
            },
            [
                {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(0),
                    'duration_minutes': 0,
                    'shift_id': 1,
                },
                {
                    'state_type': 'late_and_break',
                    'start': data.add_minutes(0),
                    'duration_minutes': 5,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working_on_break',
                    'start': data.add_minutes(5),
                    'duration_minutes': 25,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working',
                    'start': data.add_minutes(30),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'overtime',
                    'start': data.add_minutes(60),
                    'duration_minutes': 0,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working',
                    'start': data.add_minutes(60),
                    'duration_minutes': 60,
                    'shift_id': 3,
                },
                {
                    'state_type': 'overtime',
                    'start': data.add_minutes(120),
                    'duration_minutes': 0,
                    'shift_id': 3,
                },
                {
                    'state_type': 'working',
                    'start': data.add_minutes(120),
                    'duration_minutes': None,
                    'shift_id': 2,
                },
            ],
            id='slightly_late',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'late',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': [],
            },
            [
                {
                    'state_type': 'late',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='no_excessive_states',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'on_break',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': [
                    {
                        'marker_type': 'break_end',
                        'start': data.add_minutes(30),
                        'shift_id': 1,
                    },
                    {
                        'marker_type': 'shift_end',
                        'start': data.add_minutes(60),
                        'shift_id': 1,
                    },
                ],
            },
            [
                {
                    'state_type': 'on_break',
                    'start': data.add_minutes(0),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'late_from_break',
                    'start': data.add_minutes(30),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'paused',
                    'start': data.add_minutes(60),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='late_from_break',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'working',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': [
                    {
                        'marker_type': 'break_start',
                        'start': data.add_minutes(30),
                        'shift_id': 1,
                    },
                    {
                        'marker_type': 'break_end',
                        'start': data.add_minutes(60),
                        'shift_id': 1,
                    },
                ],
            },
            [
                {
                    'state_type': 'working',
                    'start': data.add_minutes(0),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working_on_break',
                    'start': data.add_minutes(30),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working',
                    'start': data.add_minutes(60),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='working_on_break',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'not_working',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': [
                    {
                        'marker_type': 'break_start',
                        'start': data.add_minutes(30),
                        'shift_id': 1,
                    },
                    {
                        'marker_type': 'break_end',
                        'start': data.add_minutes(60),
                        'shift_id': 1,
                    },
                ],
            },
            [
                {
                    'state_type': 'not_working',
                    'start': data.add_minutes(0),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'not_working_break',
                    'start': data.add_minutes(30),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'late_from_break',
                    'start': data.add_minutes(60),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='not_working_break',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'working',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': [
                    {
                        'marker_type': 'pause',
                        'start': data.add_minutes(30),
                        'shift_id': 1,
                    },
                    {
                        'marker_type': 'connect',
                        'start': data.add_minutes(60),
                        'shift_id': 1,
                    },
                ],
            },
            [
                {
                    'state_type': 'working',
                    'start': data.add_minutes(0),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'shift_paused',
                    'start': data.add_minutes(30),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working',
                    'start': data.add_minutes(60),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='shift_paused',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': None,
                },
                'markers': [
                    {
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(0),
                        'shift_id': 1,
                    },
                    {
                        'marker_type': 'event_start',
                        'start': data.add_minutes(0),
                        'shift_id': 1,
                    },
                    {
                        'marker_type': 'disconnect',
                        'start': data.add_minutes(15),
                        'shift_id': 1,
                    },
                    {
                        'marker_type': 'event_end',
                        'start': data.add_minutes(30),
                        'shift_id': 1,
                    },
                    {
                        'marker_type': 'connect',
                        'start': data.add_minutes(60),
                        'shift_id': None,
                    },
                ],
            },
            [
                {
                    'state_type': 'disconnected',
                    'start': data.add_minutes(0),
                    'duration_minutes': 0,
                    'shift_id': 1,
                },
                {
                    'state_type': 'late',
                    'start': data.add_minutes(0),
                    'duration_minutes': 0,
                    'shift_id': 1,
                },
                {
                    'state_type': 'late_and_event',
                    'start': data.add_minutes(0),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'late',
                    'start': data.add_minutes(30),
                    'duration_minutes': 30,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working',
                    'start': data.add_minutes(60),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='late_and_event',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'absent',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': [
                    {'marker_type': 'connect', 'start': data.add_minutes(1)},
                ],
            },
            [
                {
                    'state_type': 'late',
                    'start': data.add_minutes(0),
                    'duration_minutes': 1,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working',
                    'start': data.add_minutes(1),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='absent_to_late',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'connected',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 0,
                },
                'markers': [
                    {
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(10),
                        'shift_id': 1,
                    },
                ],
            },
            [
                {
                    'state_type': 'overtime',
                    'start': data.add_minutes(0),
                    'duration_minutes': 10,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working',
                    'start': data.add_minutes(10),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='inplace_overtime',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'working',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': [
                    {
                        'marker_type': 'shift_end',
                        'start': data.add_minutes(10),
                        'shift_id': 1,
                    },
                ],
            },
            [
                {
                    'state_type': 'working',
                    'start': data.add_minutes(0),
                    'duration_minutes': 10,
                    'shift_id': 1,
                },
                {
                    'state_type': 'overtime',
                    'start': data.add_minutes(10),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='overtime',
        ),
        pytest.param(
            {
                'current_state': {
                    'state_type': 'working',
                    'start': data.add_minutes(0),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
                'markers': [
                    {
                        'marker_type': 'pause',
                        'start': data.add_minutes(1),
                        'subtype': 'toilet',
                    },
                    {
                        'marker_type': 'connect',
                        'start': data.add_minutes(2),
                        'subtype': 'postcall',
                    },
                    {
                        'marker_type': 'disconnect',
                        'start': data.add_minutes(3),
                    },
                ],
            },
            [
                {
                    'state_type': 'working',
                    'subtype': None,
                    'start': data.add_minutes(0),
                    'duration_minutes': 1,
                    'shift_id': 1,
                },
                {
                    'state_type': 'shift_paused',
                    'subtype': 'toilet',
                    'start': data.add_minutes(1),
                    'duration_minutes': 1,
                    'shift_id': 1,
                },
                {
                    'state_type': 'working',
                    'subtype': 'postcall',
                    'start': data.add_minutes(2),
                    'duration_minutes': 1,
                    'shift_id': 1,
                },
                {
                    'state_type': 'not_working',
                    'subtype': None,
                    'start': data.add_minutes(3),
                    'duration_minutes': None,
                    'shift_id': 1,
                },
            ],
            id='subtype',
        ),
    ],
)
async def test_apply_markers(stq3_context, kwargs, expected_res):
    sv_obj = violations_module.ShiftViolations(stq3_context)
    current_state = violations_module.utils.make_state(
        kwargs.pop('current_state'),
    )
    markers = [
        violations_module.utils.make_marker(marker)
        for marker in kwargs.pop('markers')
    ]
    res = await sv_obj.apply_markers(
        current_state, markers, end=data.add_minutes(5),
    )
    res = data.expected_fields(res, expected_res)

    assert res == expected_res


@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'new_states': [
                    {
                        'yandex_uid': 'uid1',
                        'state_type': 'late',
                        'start': data.add_minutes(0),
                        'duration_minutes': None,
                        'skill': 'pokemon',
                    },
                ],
                'end': data.add_minutes(4),
            },
            [],
            id='late_unfinished',
        ),
        pytest.param(
            {
                'new_states': [
                    {
                        'yandex_uid': 'uid1',
                        'state_type': 'late',
                        'start': data.add_minutes(0),
                        'duration_minutes': 4,
                        'skill': 'pokemon',
                    },
                ],
                'end': data.add_minutes(4),
            },
            [],
            id='late_short',
        ),
        pytest.param(
            {
                'new_states': [
                    {
                        'yandex_uid': 'uid1',
                        'state_type': 'late',
                        'start': data.add_minutes(0),
                        'duration_minutes': 10,
                        'skill': 'pokemon',
                    },
                    {
                        'yandex_uid': 'uid1',
                        'state_type': 'late_and_break',
                        'start': data.add_minutes(10),
                        'duration_minutes': 10,
                        'skill': 'pokemon',
                    },
                    {
                        'yandex_uid': 'uid1',
                        'state_type': 'late_and_break',
                        'start': data.add_minutes(20),
                        'duration_minutes': 3,
                        'skill': 'pokemon',
                    },
                ],
                'end': data.add_minutes(10),
            },
            [
                {
                    'yandex_uid': 'uid1',
                    'state_type': 'late',
                    'start': data.add_minutes(0),
                    'duration_minutes': 10,
                    'skill': 'pokemon',
                },
                {
                    'yandex_uid': 'uid1',
                    'state_type': 'late_and_break',
                    'start': data.add_minutes(10),
                    'duration_minutes': 10,
                    'skill': 'pokemon',
                },
            ],
            id='late_and_break',
        ),
    ],
)
def test_check_violations(stq3_context, kwargs, expected_res):
    sv_obj = violations_module.ShiftViolations(stq3_context)
    states = [
        violations_module.utils.make_state(state)
        for state in kwargs['new_states']
    ]
    res, _ = sv_obj.check_violations(new_states=states, end=kwargs['end'])

    res = data.expected_fields(res, expected_res)
    assert res == expected_res


def test_constants():
    # there are default values for each checked state
    for key in sv_constants.VIOLATIONS_STATES:
        assert key in sv_constants.SETTINGS_MAP
        assert key in sv_constants.DEFAULT_AFTER_MINUTES

    # there are suggestions for each violation in db
    suggestions = {
        item[0] for item in sv_constants.SHIFT_VIOLATION_TYPES_SUGGEST_ITEMS
    }
    assert sv_constants.VIOLATION_TYPES & suggestions == suggestions

    # there are exactly one entry for each transformation
    for state in sv_constants.StateType:
        for marker in sv_constants.MarkerType:
            is_transformation = marker in sv_constants.TRANSFORM_TABLE[state]
            is_fallback = marker in sv_constants.FALLBACK_TABLE[state]
            assert is_transformation != is_fallback, (state, marker)

    # there is a reset to event for any state
    for state in sv_constants.StateType:
        assert state in sv_constants.STATE_TO_EVENT_MAP

    # must not reset event states as they appear at shift's end
    assert not sv_constants.FLAP_STATES & set(
        sv_constants.EVENT_TO_STATE_MAP.keys(),
    )


@pytest.mark.parametrize(
    'state, marker, expected_state',
    [
        pytest.param(
            {
                'state_type': 'disconnected',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'marker_type': 'connect',
                'start': data.add_minutes(0),
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'state_type': 'connected',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            id='connect',
        ),
        pytest.param(
            {
                'state_type': 'connected',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'marker_type': 'disconnect',
                'start': data.add_minutes(0.75),
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'state_type': 'disconnected',
                'start': data.add_minutes(0.75),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            id='disconnect_after_45',
        ),
        pytest.param(
            {
                'state_type': 'connected',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'marker_type': 'shift_start',
                'start': data.add_minutes(0.75),
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'state_type': 'working',
                'start': data.add_minutes(0.75),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            id='shift_start',
        ),
        pytest.param(
            {
                'state_type': 'working',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'marker_type': 'shift_end',
                'start': data.add_minutes(0.75),
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'state_type': 'overtime',
                'start': data.add_minutes(0.75),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            id='shift_end',
        ),
        pytest.param(
            {
                'state_type': 'disconnected',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'marker_type': 'shift_start',
                'start': data.add_minutes(0.75),
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'state_type': 'late',
                'start': data.add_minutes(0.75),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            id='shift_start_on_disconnected',
        ),
        pytest.param(
            {
                'state_type': 'late',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'marker_type': 'break_start',
                'start': data.add_minutes(0.75),
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'state_type': 'late_and_break',
                'start': data.add_minutes(0.75),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            id='late_and_break',
        ),
        pytest.param(
            {
                'state_type': 'on_break',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'marker_type': 'break_end',
                'start': data.add_minutes(0.75),
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'state_type': 'late_from_break',
                'start': data.add_minutes(0.75),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            id='late_from_break',
        ),
        pytest.param(
            {
                'state_type': 'working',
                'start': data.add_minutes(0),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'marker_type': 'break_start',
                'start': data.add_minutes(0.75),
                'skill': 'droid',
                'shift_id': 1,
            },
            {
                'state_type': 'working_on_break',
                'start': data.add_minutes(0.75),
                'duration_minutes': None,
                'skill': 'droid',
                'shift_id': 1,
            },
            id='working_on_break',
        ),
    ],
)
async def test_transform(state, marker, expected_state):
    res, _ = violations_module.utils.transform(
        violations_module.utils.make_state(state),
        violations_module.utils.make_marker(marker),
    )

    res = data.expected_fields([res], [expected_state])
    assert res == [expected_state]


@pytest.mark.parametrize(
    'kwargs, expected_res',
    [
        pytest.param(
            {
                'markers': [],
                'states': [
                    {
                        'yandex_uid': 'uid1',
                        'state_type': 'disconnected',
                        'start': data.add_minutes(0),
                    },
                ],
                'end': data.add_minutes(0),
            },
            [],
            id='default',
        ),
        pytest.param(
            {
                'markers': [
                    {
                        'yandex_uid': 'uid1',
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(0),
                    },
                    {
                        'yandex_uid': 'uid1',
                        'marker_type': 'event_start',
                        'start': data.add_minutes(0),
                    },
                    {
                        'yandex_uid': 'uid1',
                        'marker_type': 'break_start',
                        'start': data.add_minutes(0),
                    },
                    {
                        'yandex_uid': 'uid1',
                        'marker_type': 'event_end',
                        'start': data.add_minutes(15),
                    },
                    {
                        'yandex_uid': 'uid1',
                        'marker_type': 'break_end',
                        'start': data.add_minutes(20),
                    },
                ],
                'states': [
                    {
                        'yandex_uid': 'uid1',
                        'state_type': 'disconnected',
                        'start': data.add_minutes(-0.25),
                    },
                ],
                'end': data.add_minutes(30),
            },
            [
                {
                    'duration_minutes': 15.0,
                    'start': data.add_minutes(0),
                    'state_type': 'late_and_event_break',
                },
                {
                    'duration_minutes': None,
                    'start': data.add_minutes(15),
                    'state_type': 'late',
                },
            ],
            id='break_intersects_event',
        ),
        pytest.param(
            {
                'markers': [
                    {
                        'yandex_uid': 'uid1',
                        'marker_type': 'shift_start',
                        'start': data.add_minutes(0),
                    },
                ],
                'states': [
                    {
                        'yandex_uid': 'uid1',
                        'state_type': 'connected',
                        'start': data.add_minutes(-10),
                    },
                ],
                'end': data.add_minutes(1),
            },
            [
                {
                    'duration_minutes': 10,
                    'start': data.add_minutes(-10),
                    'state_type': 'overtime',
                },
                {
                    'duration_minutes': None,
                    'start': data.add_minutes(0),
                    'state_type': 'working',
                },
            ],
            id='overtime',
        ),
    ],
)
async def test_run_automaton(stq3_context, kwargs, expected_res):
    kwargs['states'] = [
        violations_module.utils.make_state(state) for state in kwargs['states']
    ]
    kwargs['markers'] = [
        violations_module.utils.make_marker(marker)
        for marker in kwargs['markers']
    ]

    sv_obj = violations_module.ShiftViolations(stq3_context)
    res, _, _ = await sv_obj.run_automaton(**kwargs)
    res = violations_module.utils.filter_modified_states(
        new_states=res, old_states=kwargs['states'], rest_states=[],
    )
    res = data.expected_fields(res, expected_res)

    assert res == expected_res
