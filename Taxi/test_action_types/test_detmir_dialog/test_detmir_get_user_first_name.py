# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import state as state_module
from supportai_actions.actions import features as feature_module
from supportai_actions.action_types.detmir_dialog import get_user_first_name


@pytest.mark.parametrize('_call_param', [([])])
async def test_detmir_dialog_get_user_first_name_action_validate(_call_param):
    get_user_first_name.GetUserFirstNameAction(
        'detmir_dialog', 'get_user_first_name', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'name', 'value': 'Name'}],
                ),
            ),
            [],
        ),
    ],
)
async def test_detmir_dialog_get_user_first_name_action_validate_state(
        state, _call_param,
):
    get_user_first_name.GetUserFirstNameAction(
        'detmir_dialog', 'get_user_first_name', '0', _call_param,
    ).validate_state(state)


@pytest.fixture(name='mock_wizard')
def _mock_wizard(mockserver):
    @mockserver.json_handler('/wizard/wizard')
    def _(_):
        return mockserver.make_response(
            json={'rules': {'Fio': {'Fio': 'Surname Name'}}},
        )


@pytest.mark.parametrize('_call_param', [[]])
@pytest.mark.parametrize(
    'state',
    [
        state_module.State(
            features=feature_module.Features(
                features=[{'key': 'name', 'value': 'Name'}],
            ),
        ),
        state_module.State(
            features=feature_module.Features(
                features=[{'key': 'not_name', 'value': 'Name'}],
            ),
        ),
    ],
)
async def test_detmir_dialog_get_user_first_name_action_call(
        web_context, _call_param, state, mock_wizard,
):
    action = get_user_first_name.GetUserFirstNameAction(
        'detmir_dialog', 'get_user_first_name', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'user_first_name' in _state.features
