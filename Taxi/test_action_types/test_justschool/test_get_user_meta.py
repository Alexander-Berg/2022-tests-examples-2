# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from generated.models import omnidesk_justschool as justschool_api_model

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.justschool_dialog import get_user_meta


@pytest.mark.parametrize('_call_param', [[]])
async def test_justschool_dialog_get_user_meta_validation(_call_param):
    _ = get_user_meta.GetUserMetaAction(
        'justschool_dialog', 'get_user_meta', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'user_id', 'value': 1}],
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
async def test_justschool_dialog_get_user_meta_state_validation(
        state, _call_param,
):
    action = get_user_meta.GetUserMetaAction(
        'justschool_dialog', 'get_user_meta', '0', _call_param,
    )

    action.validate_state(state)


@pytest.fixture(name='mock_justschool')
def _mock_justschool(mockserver):
    @mockserver.json_handler(
        '/omnidesk-justschool/api/users/.*.json', regex=True,
    )
    def _(_):
        return mockserver.make_response(
            json=justschool_api_model.UserMeta(
                user=justschool_api_model._UserMetaUser(  # pylint: disable=W0212
                    user_full_name='full_name',
                    telegram_id='XXX',
                    viber_id='XXX',
                ),
            ).serialize(),
        )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'user_id', 'value': 1}],
                ),
            ),
            [],
        ),
    ],
)
async def test_justschool_dialog_get_user_meta_call(
        web_context, state, _call_param, mock_justschool,
):
    action = get_user_meta.GetUserMetaAction(
        'justschool_dialog', 'get_user_meta', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'justschool_chat_id' in _state.features
