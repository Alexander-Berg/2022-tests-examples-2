import pytest

from supportai_actions.action_types.sunlight import orders_by_phone
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize(
    '_call_param', [[], [param_module.ActionParam({'response_mapping': []})]],
)
async def test_sunlight_orders_by_phone_validation(_call_param):
    _ = orders_by_phone.OrdersByPhoneAction(
        'sunlight', 'orders_by_phone', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'client_phone_number', 'value': '79999999999'},
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
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'visitor_id', 'value': '79999999999'},
                        {'key': 'channelType', 'value': 'whats up'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_sunlight_orders_by_phone_state_validation(state, _call_param):
    action = orders_by_phone.OrdersByPhoneAction(
        'sunlight', 'orders_by_phone', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'client_phone_number', 'value': '79999999999'},
                    ],
                ),
            ),
            [],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'visitor_id', 'value': '79999999999'},
                        {'key': 'channelType', 'value': 'WhatsAppMfms'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_sunlight_orders_by_phone_call(
        web_context, state, _call_param, mock_sunlight_api,
):
    action = orders_by_phone.OrdersByPhoneAction(
        'sunlight', 'orders_by_phone', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'active_orders_numbers' in _state.features
    assert 'num_of_active_orders' in _state.features
    assert _state.features['num_of_active_orders'] == 1
