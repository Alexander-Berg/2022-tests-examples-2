# pylint: disable=broad-except
import contextlib

import pytest

from supportai_actions.action_types.foxford_dialog import (
    reschedule_user_lesson_action,
)
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module
from test_supportai_actions.test_action_types.test_foxford import (
    utils as test_utils,
)


ACTION_NAME = 'reschedule_user_lesson_action'
PROJECT_NAME = 'foxford_dialog'


async def test_reschedule_user_lesson_validate():
    _ = reschedule_user_lesson_action.RescheduleUserLessonAction(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )


@pytest.mark.parametrize(
    'state, raises',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    [
                        {'key': 'user_id', 'value': 123},
                        {'key': 'lesson_id_to_modify', 'value': 123},
                        {
                            'key': 'target_datetime',
                            'value': '2021-11-17 01:00:00',
                        },
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
                    [{'key': 'user_id', 'value': '123'}],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
    ],
)
async def test_reschedule_user_lesson_state_validation(state, raises):
    action = reschedule_user_lesson_action.RescheduleUserLessonAction(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )
    with raises:
        action.validate_state(state)


@pytest.fixture(name='mock_foxford')
def _mock_foxford(mockserver):
    @mockserver.json_handler(
        path='/foxford-api/api/yandex_support_ai/'
        'users/4/coach/lessons/5/reschedules',
    )
    def _(_):
        return mockserver.make_response(status=200)


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'user_id', 'value': 4},
                        {'key': 'lesson_id_to_modify', 'value': 5},
                        {
                            'key': 'target_datetime',
                            'value': '2021-11-17 01:00:00',
                        },
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_reschedule_user_lesson_call(
        web_context, state, _call_params, mock_foxford,
):
    action = reschedule_user_lesson_action.RescheduleUserLessonAction(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )

    _state = await action(web_context, state)
    assert _state.features.get('lesson_rescheduled_successfully') is True
    new_call_params, new_state = test_utils.make_new_call_params_and_state(
        state,
    )
    action = reschedule_user_lesson_action.RescheduleUserLessonAction(
        PROJECT_NAME, ACTION_NAME, '0', new_call_params,
    )

    _state = await action(web_context, new_state)
    assert _state.features.get('lesson_rescheduled_successfully') is True
