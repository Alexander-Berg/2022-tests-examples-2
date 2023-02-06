# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.justschool_dialog import get_lesson_to_move


@pytest.mark.parametrize('_call_param', [[]])
async def test_justshool_dialog_get_lesson_to_move_validation(_call_param):
    _ = get_lesson_to_move.GetLessonToMoveAction(
        'justshool_dialog', 'get_lesson_to_move', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'user_lessons_lesson_id', 'value': []},
                        {'key': 'user_lessons_teacher_id', 'value': []},
                        {'key': 'user_lessons_type', 'value': []},
                        {'key': 'user_lessons_weekday', 'value': []},
                        {'key': 'user_lessons_hour', 'value': []},
                        {'key': 'user_lessons_minute', 'value': []},
                        {'key': 'user_lessons_year', 'value': []},
                        {'key': 'user_lessons_month', 'value': []},
                        {'key': 'user_lessons_day', 'value': []},
                        {
                            'key': 'source_date',
                            'value': '2021-01-01T12:04:35.112450',
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
                    features=[{'key': 'user_lessons', 'value': []}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_justshool_dialog_get_lesson_to_move_state_validation(
        state, _call_param,
):
    action = get_lesson_to_move.GetLessonToMoveAction(
        'justshool_dialog', 'get_lesson_to_move', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'user_lessons_lesson_id', 'value': []},
                        {'key': 'user_lessons_teacher_id', 'value': []},
                        {'key': 'user_lessons_type', 'value': []},
                        {'key': 'user_lessons_weekday', 'value': []},
                        {'key': 'user_lessons_hour', 'value': []},
                        {'key': 'user_lessons_minute', 'value': []},
                        {'key': 'user_lessons_year', 'value': []},
                        {'key': 'user_lessons_month', 'value': []},
                        {'key': 'user_lessons_day', 'value': []},
                        {
                            'key': 'source_date',
                            'value': '2021-01-01T12:04:35.112450',
                        },
                    ],
                ),
            ),
            [],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'user_lessons_lesson_id', 'value': [1]},
                        {'key': 'user_lessons_teacher_id', 'value': [1]},
                        {'key': 'user_lessons_type', 'value': ['type']},
                        {'key': 'user_lessons_weekday', 'value': [5]},
                        {'key': 'user_lessons_hour', 'value': [4]},
                        {'key': 'user_lessons_minute', 'value': [19]},
                        {'key': 'user_lessons_year', 'value': [0]},
                        {'key': 'user_lessons_month', 'value': [10]},
                        {'key': 'user_lessons_day', 'value': [13]},
                        {
                            'key': 'source_date',
                            'value': '2021-01-01T12:04:35.112450',
                        },
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_justshool_dialog_get_lesson_to_move_call(
        web_context, state, _call_param,
):
    action = get_lesson_to_move.GetLessonToMoveAction(
        'justshool_dialog', 'get_lesson_to_move', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'lesson_to_move_id' in _state.features
