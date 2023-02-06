import pytest

from supportai_actions.action_types.sunlight import order_extend
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize(
    '_call_param', [[], [param_module.ActionParam({'response_mapping': []})]],
)
async def test_sunlight_order_extend_validation(_call_param):
    _ = order_extend.OrderExtensionAction(
        'sunlight', 'order_extend', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'order_number', 'value': '9999'},
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
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_number', 'value': '1234'}],
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
                    features=[{'key': 'client_phone_number', 'value': '1234'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_sunlight_order_extend_state_validation(state, _call_param):
    action = order_extend.OrderExtensionAction(
        'sunlight', 'order_extend', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'order_number', 'value': '9999'},
                        {'key': 'client_phone_number', 'value': '12345'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_sunlight_orders_extend_call_200(
        web_context, state, _call_param, mock_sunlight_api,
):
    action = order_extend.OrderExtensionAction(
        'sunlight', 'order_extend', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'order_extend_error_type' not in _state.features
    assert 'order_extend_error_message' not in _state.features


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'order_number', 'value': '4321'},
                        {'key': 'client_phone_number', 'value': '1234'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_sunlight_orders_extend_call_400(
        web_context, state, _call_param, mock_sunlight_api,
):
    action = order_extend.OrderExtensionAction(
        'sunlight', 'order_extend', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'order_extend_error_type' in _state.features
    assert 'order_extend_error_message' in _state.features
