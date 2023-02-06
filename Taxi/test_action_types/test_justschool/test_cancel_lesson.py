# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.justschool_dialog import cancel_lesson


@pytest.mark.parametrize('_call_param', [[]])
async def test_justschool_cancel_lesson_validation(_call_param):
    _ = cancel_lesson.CancelLessonAction(
        'justschool_dialog', 'cancel_lesson', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-01-01T4:19',
                        },
                        {'key': 'lesson_to_cancel_id', 'value': 1},
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
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-01-01T4:19',
                        },
                    ],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_justschool_cancel_lesson_state_validation(state, _call_param):
    action = cancel_lesson.CancelLessonAction(
        'justschool_dialog', 'cancel_lesson', '0', _call_param,
    )

    action.validate_state(state)


@pytest.fixture(name='mock_justschool', params=[True, False])
def _mock_justschool(request, mockserver):
    @mockserver.json_handler(
        '/justschool-api/public/lesson-events/.*/cancel/single', regex=True,
    )
    def _(_):
        if not request.param:
            return mockserver.make_response(status=500)

        return mockserver.make_response(status=204)

    return request.param


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-01-01T4:19',
                        },
                        {'key': 'lesson_to_cancel_id', 'value': 1},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_justschool_cancel_lesson_call(
        web_context, state, _call_param, mock_justschool,
):
    action = cancel_lesson.CancelLessonAction(
        'justschool_dialog', 'cancel_lesson', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'cancelled_succesfully' in _state.features
    assert _state.features['cancelled_succesfully'] == mock_justschool
