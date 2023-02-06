# pylint: disable=broad-except
import contextlib

import pytest

from supportai_actions.action_types.foxford_dialog import (
    get_agent_available_slots,
)
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module
from test_supportai_actions.test_action_types.test_foxford import (
    utils as test_utils,
)


ACTION_NAME = 'get_agent_available_slots'
PROJECT_NAME = 'foxford_dialog'


async def test_get_agent_available_slots_validation():
    _ = get_agent_available_slots.GetAgentAvailableSlots(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )


@pytest.mark.parametrize(
    'state, raises',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    [
                        {'key': 'agent_id', 'value': 123},
                        {'key': 'course_id', 'value': 123},
                    ],
                ),
            ),
            contextlib.nullcontext(),
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    [
                        {
                            'key': 'some_weird_feature',
                            'value': 'some_weird_feature_value',
                        },
                    ],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    [{'key': 'agent_id', 'value': '123'}],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
    ],
)
async def test_get_agent_available_slots_state_validation(state, raises):
    action = get_agent_available_slots.GetAgentAvailableSlots(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )
    with raises:
        action.validate_state(state)


@pytest.fixture(name='mock_foxford')
def _mock_foxford(mockserver):
    @mockserver.json_handler(
        path='foxford-api/api/yandex_support_ai/users/'
        '4/coach/courses/5/available_slots',
    )
    def _(_):
        return mockserver.make_response(
            json={
                'agent_available_slots': [
                    {'week_day': 5, 'time': '17:00'},
                    {'week_day': 6, 'time': '18:00'},
                ],
            },
        )


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'agent_id', 'value': 4},
                        {'key': 'course_id', 'value': 5},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_get_agent_available_slots_call(
        web_context, state, _call_params, mock_foxford,
):
    action = get_agent_available_slots.GetAgentAvailableSlots(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )

    _state = await action(web_context, state)
    assert 'agent_available_weekdays' in _state.features
    assert 'agent_available_times' in _state.features
    assert _state.features['agent_available_weekdays'] == [5, 6]
    assert _state.features['agent_available_times'] == ['17:00', '18:00']

    new_call_params, new_state = test_utils.make_new_call_params_and_state(
        state,
    )
    action = get_agent_available_slots.GetAgentAvailableSlots(
        PROJECT_NAME, ACTION_NAME, '0', new_call_params,
    )

    _state = await action(web_context, new_state)
    assert 'agent_available_weekdays' in _state.features
    assert 'agent_available_times' in _state.features
    assert _state.features['agent_available_weekdays'] == [5, 6]
    assert _state.features['agent_available_times'] == ['17:00', '18:00']
