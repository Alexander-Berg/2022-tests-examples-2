# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.detmir_dialog import get_promo_features


@pytest.mark.parametrize('_call_params', [[]])
async def test_detmir_promocode_action_validate(_call_params):
    get_promo_features.GetPromoFeaturesAction(
        'detmir_dialog', 'detmir_promocode', '0', _call_params,
    )


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'some'}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'no_order_id', 'value': 'some'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_detmir_promocode_action_validate_state(state, _call_params):
    get_promo_features.GetPromoFeaturesAction(
        'detmir_dialog', 'detmir_promocode', '0', _call_params,
    ).validate_state(state)


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'gained'}],
                ),
            ),
            [],
        ),
    ],
)
async def test_detmir_promocode_action_call(web_context, _call_params, state):
    action = get_promo_features.GetPromoFeaturesAction(
        'detmir_dialog', 'detmir_promocode', '1', _call_params,
    )

    _state = await action(web_context, state)

    assert _state.features == state.features
