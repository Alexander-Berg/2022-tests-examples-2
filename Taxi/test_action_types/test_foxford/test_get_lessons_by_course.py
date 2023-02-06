# pylint: disable=broad-except
import contextlib

import pytest

from supportai_actions.action_types.foxford_dialog import get_lessons_by_course
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module
from test_supportai_actions.test_action_types.test_foxford import (
    utils as test_utils,
)


ACTION_NAME = 'get_lessons_by_course'
PROJECT_NAME = 'foxford_dialog'


async def test_get_lessons_by_course_validation_call_params():
    _ = get_lessons_by_course.GetLessonsByCourseAction(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )


@pytest.mark.parametrize(
    'state, raises',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    [
                        {'key': 'user_id', 'value': 3},
                        {'key': 'user_course_id', 'value': 4},
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
                    [
                        {'key': 'user_id', 'value': '123'},
                        {'key': 'user_course_id', 'value': '123'},
                    ],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
    ],
)
async def test_get_lessons_by_course_state_validation(state, raises):
    action = get_lessons_by_course.GetLessonsByCourseAction(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )
    with raises:
        action.validate_state(state)


@pytest.fixture(name='mock_foxford')
def _mock_foxford(mockserver):
    @mockserver.json_handler(
        path='/foxford-api/api/yandex_support_ai/'
        'users/3/coach/user_courses/4/lessons',
    )
    def _(_):
        return mockserver.make_response(
            json=[
                {
                    'id': 312,
                    'starts_at': '2018-03-05 11:00:00 +0300',
                    'state': 'canceled',
                    'intro': False,
                },
                {
                    'id': 313,
                    'starts_at': '2018-03-05 11:00:00 +0300',
                    'state': 'not_canceled',
                    'intro': True,
                },
            ],
        )


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'user_id', 'value': 3},
                        {'key': 'user_course_id', 'value': 4},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_get_lessons_by_course(
        web_context, state, _call_params, mock_foxford,
):
    action = get_lessons_by_course.GetLessonsByCourseAction(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )

    _state = await action(web_context, state)
    assert 'lessons_ids' in _state.features
    assert 'lessons_starts_ats' in _state.features
    assert 'lessons_states' in _state.features
    assert 'lessons_intros' in _state.features

    assert _state.features['lessons_ids'] == [312, 313]
    assert (
        _state.features['lessons_starts_ats']
        == ['2018-03-05 11:00:00 +0300'] * 2
    )
    assert _state.features['lessons_states'] == ['canceled', 'not_canceled']
    assert _state.features['lessons_intros'] == [False, True]
    new_call_params, new_state = test_utils.make_new_call_params_and_state(
        state,
    )
    action = get_lessons_by_course.GetLessonsByCourseAction(
        PROJECT_NAME, ACTION_NAME, '0', new_call_params,
    )

    _state = await action(web_context, new_state)
    assert 'lessons_ids' in _state.features
    assert 'lessons_starts_ats' in _state.features
    assert 'lessons_states' in _state.features
    assert 'lessons_intros' in _state.features

    assert _state.features['lessons_ids'] == [312, 313]
    assert (
        _state.features['lessons_starts_ats']
        == ['2018-03-05 11:00:00 +0300'] * 2
    )
    assert _state.features['lessons_states'] == ['canceled', 'not_canceled']
    assert _state.features['lessons_intros'] == [False, True]
