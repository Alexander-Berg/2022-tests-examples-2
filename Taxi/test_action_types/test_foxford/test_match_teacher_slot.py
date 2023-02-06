# pylint: disable=broad-except
import pytest

from supportai_actions.action_types.foxford_dialog import match_teacher_slot
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

ACTION_NAME = 'match_teacher_slot'
PROJECT_NAME = 'foxford_dialog'


@pytest.mark.parametrize('_call_param', [[]])
async def test_foxford_dialog_match_user_lesson_validation(_call_param):
    _ = match_teacher_slot.MatchTeacherSlot(
        PROJECT_NAME, ACTION_NAME, '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'agent_available_weekdays',
                            'value': [0, 2, 4],
                        },
                        {
                            'key': 'agent_available_times',
                            'value': ['17:00', '12:00', '11:00'],
                        },
                        {
                            'key': 'request_time',
                            'value': '2021-12-03T17:00:.576560',
                        },
                    ],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'some', 'value': 'some'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'lesson_ids', 'value': []}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_foxford_match_user_lesson_state_validation(state, _call_param):
    action = match_teacher_slot.MatchTeacherSlot(
        PROJECT_NAME, ACTION_NAME, '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.now('2021-12-02T10:00')
@pytest.mark.parametrize(
    'state,'
    '_call_param,'
    'requested_slot_available,'
    'matched_slot,'
    'matched_slot_formatted,'
    'available_slots_formatted',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'agent_available_weekdays',
                            'value': [5, 0, 3],
                        },  # 0  1  2  3  4  5  6
                        # -> вс пн вт ср чт пт сб
                        {
                            'key': 'agent_available_times',
                            'value': ['17:00', '12:00', '11:00'],
                        },
                        {
                            'key': 'request_time',
                            'value': '2021-12-03T17:00:00.576560',
                        },
                    ],
                ),
            ),
            [],
            True,
            '2021-12-03T17:00:00+0300',
            '03.12 в 17:00',
            ['03.12 в 17:00', '05.12 в 12:00', '08.12 в 11:00'],
        ),
    ],
)
async def test_justschool_dialog_get_lesson_to_cancel_call_lesson_choose(
        web_context,
        state,
        _call_param,
        requested_slot_available,
        matched_slot,
        matched_slot_formatted,
        available_slots_formatted,
):
    action = match_teacher_slot.MatchTeacherSlot(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )

    _state = await action(web_context, state)
    assert (
        _state.features.get('requested_slot_available')
        == requested_slot_available
    )
    assert _state.features.get('matched_slot') == matched_slot
    assert (
        _state.features.get('matched_slot_formatted') == matched_slot_formatted
    )
    assert (
        _state.features.get('available_slots_formatted')
        == available_slots_formatted
    )
