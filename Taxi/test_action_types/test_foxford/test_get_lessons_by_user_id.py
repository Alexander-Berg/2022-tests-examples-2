# pylint: disable=broad-except
# pylint: disable=unused-variable
import contextlib

import pytest

from supportai_actions.action_types.foxford_dialog import (
    get_lessons_by_user_id,
)
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module
from test_supportai_actions.test_action_types.test_foxford import (
    utils as test_utils,
)

ACTION_NAME = 'get_lessons_by_user_id'
PROJECT_NAME = 'foxford_dialog'


async def test_get_lessons_by_user_id_validation():
    _ = get_lessons_by_user_id.GetLessonsByUserId(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )


@pytest.mark.parametrize(
    'state, raises',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    [
                        {
                            'key': get_lessons_by_user_id.INPUT_USER_ID,
                            'value': 5,
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
                    [
                        {
                            'key': get_lessons_by_user_id.INPUT_USER_ID,
                            'value': '123',
                        },
                    ],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
    ],
)
async def test_get_lessons_by_user_id_state_validation(state, raises):
    action = get_lessons_by_user_id.GetLessonsByUserId(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )
    with raises:
        action.validate_state(state)


@pytest.fixture(name='mock_foxford')
def _mock_foxford(mockserver):
    @mockserver.json_handler(
        path='/foxford-api/api/yandex_support_ai/users/3/'
        'coach/user_courses/4/lessons',
    )
    def course_four_lessons(_):
        return mockserver.make_response(
            json=[
                {
                    'id': 312,
                    'starts_at': '2018-03-05 11:00:00 +0300',
                    'state': 'canceled',
                    'intro': False,
                },
            ],
        )

    @mockserver.json_handler(
        path='/foxford-api/api/yandex_support_ai/users/3/'
        'coach/user_courses/5/lessons',
    )
    def course_five_lessons(_):
        return mockserver.make_response(
            json=[
                {
                    'id': 313,
                    'starts_at': '2018-03-05 11:00:00 +0300',
                    'state': 'pending',
                    'intro': True,
                },
            ],
        )

    @mockserver.json_handler(
        path='/foxford-api/api/yandex_support_ai/'
        'users/3/coach/user_courses',
    )
    def get_user_courses(_):
        return mockserver.make_response(
            json=[
                {
                    'id': 4,
                    'user_id': 3,
                    'agent_id': 4,
                    'course': {'id': 4, 'title': 'Русский язык. 5–9 классы'},
                },
                {
                    'id': 5,
                    'user_id': 3,
                    'agent_id': 5,
                    'course': {
                        'id': 5,
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
async def test_get_lessons_by_user_id_call(
        web_context, state, _call_params, mock_foxford,
):
    action = get_lessons_by_user_id.GetLessonsByUserId(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )

    _state = await action(web_context, state)
    assert 'lessons_ids' in _state.features
    assert 'lessons_course_ids' in _state.features
    assert 'lessons_states' in _state.features
    assert 'lessons_starts_ats' in _state.features
    assert 'lessons_intros' in _state.features

    assert _state.features['lessons_ids'] == [312, 313]
    assert _state.features['lessons_course_ids'] == [4, 5]
    assert (
        _state.features['lessons_starts_ats']
        == ['2018-03-05 11:00:00 +0300'] * 2
    )
    assert _state.features['lessons_states'] == ['canceled', 'pending']
    assert _state.features['lessons_intros'] == [False, True]
    new_call_params, new_state = test_utils.make_new_call_params_and_state(
        state,
    )
    action = get_lessons_by_user_id.GetLessonsByUserId(
        PROJECT_NAME, ACTION_NAME, '0', new_call_params,
    )

    _state = await action(web_context, new_state)
    assert 'lessons_ids' in _state.features
    assert 'lessons_course_ids' in _state.features
    assert 'lessons_states' in _state.features
    assert 'lessons_starts_ats' in _state.features
    assert 'lessons_intros' in _state.features

    assert _state.features['lessons_ids'] == [312, 313]
    assert _state.features['lessons_course_ids'] == [4, 5]
    assert (
        _state.features['lessons_starts_ats']
        == ['2018-03-05 11:00:00 +0300'] * 2
    )
    assert _state.features['lessons_states'] == ['canceled', 'pending']
    assert _state.features['lessons_intros'] == [False, True]
