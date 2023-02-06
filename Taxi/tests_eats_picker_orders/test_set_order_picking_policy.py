import itertools

import pytest

from . import utils


@pytest.mark.parametrize('communication_policy', utils.COMMUNICATION_POLICIES)
@pytest.mark.parametrize(
    'not_found_item_policy', utils.NOT_FOUND_ITEM_POLICIES,
)
async def test_set_order_picking_policy_ok(
        taxi_eats_picker_orders,
        get_order_picking_policy,
        communication_policy,
        not_found_item_policy,
):
    eats_id = 'eats_id'

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/picking-policy',
        params={'eats_id': eats_id},
        json={
            'communication_policy': communication_policy,
            'not_found_item_policy': not_found_item_policy,
        },
    )

    assert response.status == 200
    order_picking_policy = get_order_picking_policy(eats_id)
    assert order_picking_policy['communication_policy'] == communication_policy
    assert (
        order_picking_policy['not_found_item_policy'] == not_found_item_policy
    )


@pytest.mark.parametrize(
    'old_communication_policy, new_communication_policy',
    itertools.permutations(utils.COMMUNICATION_POLICIES, 2),
)
@pytest.mark.parametrize(
    'old_not_found_item_policy, new_not_found_item_policy',
    itertools.permutations(utils.NOT_FOUND_ITEM_POLICIES, 2),
)
async def test_update_order_picking_policy_ok(
        taxi_eats_picker_orders,
        create_order_picking_policy,
        get_order_picking_policy,
        old_communication_policy,
        new_communication_policy,
        old_not_found_item_policy,
        new_not_found_item_policy,
):
    eats_id = 'eats_id'

    create_order_picking_policy(
        eats_id=eats_id,
        communication_policy=old_communication_policy,
        not_found_item_policy=old_not_found_item_policy,
    )

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/picking-policy',
        params={'eats_id': eats_id},
        json={
            'communication_policy': new_communication_policy,
            'not_found_item_policy': new_not_found_item_policy,
        },
    )

    assert response.status == 200
    order_picking_policy = get_order_picking_policy(eats_id)
    assert (
        order_picking_policy['communication_policy']
        == new_communication_policy
    )
    assert (
        order_picking_policy['not_found_item_policy']
        == new_not_found_item_policy
    )
