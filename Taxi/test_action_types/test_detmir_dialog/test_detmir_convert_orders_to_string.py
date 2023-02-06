# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import state as state_module
from supportai_actions.actions import features as feature_module
from supportai_actions.action_types.detmir_dialog import (
    convert_orders_to_string,
)


@pytest.mark.parametrize('_call_param', [([])])
async def test_detmir_dialog_convert_orders_to_string_action_validate(
        _call_param,
):
    convert_orders_to_string.ConvertOrdersToStringAction(
        'detmir_dialog', 'convert_orders_to_string', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'orders', 'value': []}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'orders', 'value': ''}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationStateError, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'some', 'value': ''}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationStateError, strict=True,
            ),
        ),
    ],
)
async def test_detmir_dialog_convert_orders_to_string_action_validate_state(
        state, _call_param,
):
    convert_orders_to_string.ConvertOrdersToStringAction(
        'detmir_dialog', 'convert_orders_to_string', '0', _call_param,
    ).validate_state(state)


@pytest.mark.parametrize('_call_param', [[]])
@pytest.mark.parametrize(
    'state',
    [
        state_module.State(
            features=feature_module.Features(
                features=[
                    {
                        'key': 'orders',
                        'value': [
                            {'order_id': 4, 'creation_dttm': '5.09.21'},
                            {'order_id': 1, 'creation_dttm': '5.09.21'},
                        ],
                    },
                ],
            ),
        ),
        state_module.State(
            features=feature_module.Features(
                features=[{'key': 'orders', 'value': []}],
            ),
        ),
    ],
)
async def test_detmir_dialog_convert_orders_to_string_action_call(
        web_context, _call_param, state,
):
    action = convert_orders_to_string.ConvertOrdersToStringAction(
        'detmir_dialog', 'convert_orders_to_string', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'orders_as_str' in _state.features
