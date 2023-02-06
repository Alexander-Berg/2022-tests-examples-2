# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.justschool_dialog import (
    get_target_lesson_datetime,
)


@pytest.mark.parametrize('_call_param', [[]])
async def test_justschool_dialog_get_target_lesson_datetime_validation(
        _call_param,
):
    _ = get_target_lesson_datetime.GetTargetLessonDatetimeAction(
        'justschool_dialog', 'get_target_lesson_datetime', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'teacher_id', 'value': 1},
                        {'key': 'target_date', 'value': '2021-01-01'},
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
                    features=[{'key': 'teacher_id', 'value': 1}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_justschool_dialog_get_target_lesson_datetime_state_validation(
        state, _call_param,
):
    action = get_target_lesson_datetime.GetTargetLessonDatetimeAction(
        'justschool_dialog', 'get_target_lesson_datetime', '0', _call_param,
    )

    action.validate_state(state)


@pytest.fixture(name='mock_justschool')
def _mock_justschool(mockserver):
    @mockserver.json_handler('/justschool-api/public/reservations/slots')
    def _(_):
        return mockserver.make_response(json=[{'hour': 4, 'minute': 19}])


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'teacher_id', 'value': 1},
                        {'key': 'target_date', 'value': '2021-01-01'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_justschool_dialog_get_target_lesson_datetime_call(
        web_context, state, _call_param, mock_justschool,
):
    action = get_target_lesson_datetime.GetTargetLessonDatetimeAction(
        'justschool_dialog', 'get_target_lesson_datetime', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'teacher_available' in _state.features
