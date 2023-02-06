import pytest

from supportai_actions.action_types.sunlight import order_by_number
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize(
    '_call_param', [[], [param_module.ActionParam({'response_mapping': []})]],
)
async def test_sunlight_order_by_number_validation(_call_param):
    _ = order_by_number.OrderByNumberAction(
        'sunlight', 'order_by_number', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_number', 'value': '9999'}],
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
async def test_sunlight_order_by_number_state_validation(state, _call_param):
    action = order_by_number.OrderByNumberAction(
        'sunlight', 'order_by_number', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_number', 'value': '9999'}],
                ),
            ),
            [],
        ),
    ],
)
async def test_sunlight_orders_by_phone_call(
        web_context, state, _call_param, mock_sunlight_api,
):
    action = order_by_number.OrderByNumberAction(
        'sunlight', 'order_by_number', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'order_type' in _state.features
    assert 'order_est_store' in _state.features
