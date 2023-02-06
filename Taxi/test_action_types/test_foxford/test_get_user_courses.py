# pylint: disable=broad-except
import contextlib

import pytest

from supportai_actions.action_types.foxford_dialog import get_user_courses
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module
from test_supportai_actions.test_action_types.test_foxford import (
    utils as test_utils,
)

ACTION_NAME = 'get_user_courses'
PROJECT_NAME = 'foxford_dialog'


async def test_get_user_courses_validation():
    _ = get_user_courses.GetUserCoursesAction(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )


@pytest.mark.parametrize(
    'state, raises',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    [{'key': 'user_id', 'value': 123}],
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
async def test_get_user_courses_state_validation(state, raises):
    action = get_user_courses.GetUserCoursesAction(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )
    with raises:
        action.validate_state(state)


@pytest.fixture(name='mock_foxford')
def _mock_foxford(mockserver):
    @mockserver.json_handler(
        path='/foxford-api/api/yandex_support_ai/'
        'users/3/coach/user_courses',
    )
    def _(_):
        return mockserver.make_response(
            json=[
                {
                    'id': 312,
                    'user_id': 3,
                    'agent_id': 4,
                    'course': {
                        'id': 902620,
                        'title': 'Русский язык. 5–9 классы',
                    },
                },
                {
                    'id': 313,
                    'user_id': 3,
                    'agent_id': 5,
                    'course': {
                        'id': 902621,
                        'title': 'Английский язык. 5–9 классы',
                    },
                },
            ],
        )


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'user_id', 'value': 3}],
                ),
            ),
            [],
        ),
    ],
)
async def test_get_user_courses_state_call(
        web_context, state, _call_params, mock_foxford,
):
    action = get_user_courses.GetUserCoursesAction(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )

    _state = await action(web_context, state)
    assert 'course_ids' in _state.features
    assert 'user_course_ids' in _state.features
    assert 'agent_ids' in _state.features
    assert _state.features['user_course_ids'] == [312, 313]
    assert _state.features['course_ids'] == [902620, 902621]
    assert _state.features['agent_ids'] == [4, 5]
    assert _state.features['course_names'] == [
        'Русский язык. 5–9 классы',
        'Английский язык. 5–9 классы',
    ]
    new_call_params, new_state = test_utils.make_new_call_params_and_state(
        state,
    )
    action = get_user_courses.GetUserCoursesAction(
        PROJECT_NAME, ACTION_NAME, '0', new_call_params,
    )

    _state = await action(web_context, new_state)
    assert 'course_ids' in _state.features
    assert 'user_course_ids' in _state.features
    assert 'agent_ids' in _state.features
    assert _state.features['user_course_ids'] == [312, 313]
    assert _state.features['course_ids'] == [902620, 902621]
    assert _state.features['agent_ids'] == [4, 5]
    assert _state.features['course_names'] == [
        'Русский язык. 5–9 классы',
        'Английский язык. 5–9 классы',
    ]
