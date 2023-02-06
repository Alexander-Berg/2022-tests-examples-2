import pytest

from supportai_actions.action_types.sunlight import edit_subscription
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize(
    '_call_param', [[], [param_module.ActionParam({'response_mapping': []})]],
)
async def test_sunlight_edit_subscription_validation(_call_param):
    _ = edit_subscription.SubscriptionEditionAction(
        'sunlight', 'edit_subscription', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'client_phone_number', 'value': '12345'},
                    ],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'random_feature', 'value': 'random'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_sunlight_edit_subscription_state_validation(state, _call_param):
    action = edit_subscription.SubscriptionEditionAction(
        'sunlight', 'edit_subscription', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'client_phone_number', 'value': '12345'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_sunlight_edit_subscription_call(
        web_context, state, _call_param, mock_sunlight_api,
):
    action = edit_subscription.SubscriptionEditionAction(
        'sunlight', 'edit_subscription', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert len(_state.features) == 1
