# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import state as state_module
from supportai_actions.actions import features as feature_module
from supportai_actions.action_types.detmir_dialog import get_order_ids_count


@pytest.mark.parametrize('_call_param', [([])])
async def test_detmir_dialog_get_order_ids_count_action_validate(_call_param):
    get_order_ids_count.GetOrderIdsCountAction(
        'detmir_dialog', 'get_order_ids_count', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [(state_module.State(features=feature_module.Features(features=[])), [])],
)
async def test_detmir_dialog_get_order_ids_count_action_validate_state(
        state, _call_param,
):
    get_order_ids_count.GetOrderIdsCountAction(
        'detmir_dialog', 'get_order_ids_count', '0', _call_param,
    ).validate_state(state)


@pytest.mark.parametrize('_call_param', [[]])
@pytest.mark.parametrize(
    'state',
    [
        state_module.State(
            features=feature_module.Features(
                features=[{'key': 'order_ids', 'value': [4, 1]}],
            ),
        ),
        state_module.State(
            features=feature_module.Features(
                features=[{'key': 'order_ids', 'value': []}],
            ),
        ),
    ],
)
async def test_detmir_dialog_get_order_ids_count_action_call(
        web_context, _call_param, state,
):
    action = get_order_ids_count.GetOrderIdsCountAction(
        'detmir_dialog', 'get_order_ids_count', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'order_ids_count' in _state.features
    assert _state.features['order_ids_count'] == len(
        state.features['order_ids'],
    )
