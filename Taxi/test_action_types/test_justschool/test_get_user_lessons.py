# flake8: noqa: I100
# pylint: disable=broad-except
import datetime
import pytest

from generated.models import justschool_api as justschool_api_model

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.justschool_dialog import get_user_lessons


@pytest.mark.parametrize('_call_param', [[]])
async def test_justschool_dialog_get_user_lessons_validation(_call_param):
    _ = get_user_lessons.GetUserLessonsAction(
        'justschool_dialog', 'get_user_lessons', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'justschool_chat_id', 'value': 'XXX-XXXX'},
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
    ],
)
async def test_justschool_dialog_get_user_lessons_state_validation(
        state, _call_param,
):
    action = get_user_lessons.GetUserLessonsAction(
        'justschool_dialog', 'get_user_lessons', '0', _call_param,
    )

    action.validate_state(state)


@pytest.fixture(name='get_two_lessons_response')
def get_lessons_response(load_json):
    return load_json('find_lessons_response.json')


@pytest.fixture(name='mock_justschool')
def _mock_justschool(mockserver, get_two_lessons_response):
    @mockserver.json_handler('/justschool-api/public/lesson-events/find')
    def _(_):
        return mockserver.make_response(
            status=200, json=get_two_lessons_response,
        )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'justschool_chat_id', 'value': 'XXX-XXXX'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_justschool_dialog_get_user_lessons_call(
        web_context, state, _call_param, mock_justschool,
):
    action = get_user_lessons.GetUserLessonsAction(
        'justschool_dialog', 'get_user_lessons', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'user_lessons' in _state.features
    assert len(_state.features['user_lessons']) == 2
