# pylint: disable=broad-except
import contextlib

import pytest

from supportai_actions.action_types.foxford_dialog import cancel_user_lesson
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module
from test_supportai_actions.test_action_types.test_foxford import (
    utils as test_utils,
)

ACTION_NAME = 'cancel_user_lesson'
PROJECT_NAME = 'foxford_dialog'


async def test_cancel_user_lesson_validate():
    _ = cancel_user_lesson.CancelUserLessonAction(
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
async def test_cancel_user_lesson_action_state_validation(state, raises):
    action = cancel_user_lesson.CancelUserLessonAction(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )
    with raises:
        action.validate_state(state)


@pytest.fixture(name='mock_foxford')
def _mock_foxford(mockserver):
    @mockserver.json_handler(
        path='/foxford-api/api/yandex_support_ai/users/4/coach/lessons/5',
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
                    ],
                ),
            ),
            [],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'user_id', 'value': 4},
                        {'key': 'lesson_id_to_modify', 'value': 5},
                    ],
                ),
            ),
            [],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'user_id', 'value': 4},
                        {'key': 'lesson_id_to_modify', 'value': 5},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_foxford_dialog_get_user_info_state_call(
        web_context, state, _call_params, mock_foxford,
):
    action = cancel_user_lesson.CancelUserLessonAction(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )
    _state = await action(web_context, state)
    assert _state.features.get(f'lesson_cancelled_successfully') is True
    new_call_params, new_state = test_utils.make_new_call_params_and_state(
        state,
    )
    action = cancel_user_lesson.CancelUserLessonAction(
        PROJECT_NAME, ACTION_NAME, '0', new_call_params,
    )
    _state = await action(web_context, new_state)
    assert _state.features.get(f'lesson_cancelled_successfully') is True
