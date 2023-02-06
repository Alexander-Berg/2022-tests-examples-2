import decimal

import pytest

from . import headers
from . import models
from . import order_log
from . import processing_noncrit


@pytest.mark.config(GROCERY_ORDERS_LOG_PARCEL_INFO={'enabled': True})
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.parametrize('is_parcel', [True, False])
@pytest.mark.parametrize(
    'cart_cashback_flow, cashback_charge, cashback_gain',
    [('charge', '10.1', None), ('gain', None, '9.08'), (None, None, None)],
)
async def test_check_new_fields_for_order_log(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        processing,
        tristero_parcels,
        is_parcel,
        cart_cashback_flow,
        cashback_charge,
        cashback_gain,
):
    order = models.Order(
        pgsql=pgsql,
        status='checked_out',
        meet_outside=True,
        no_door_call=False,
    )

    item_id = 'item_id0'
    if is_parcel:
        item_id += ':st-pa'
    gross_weight = 123

    cart_item = models.GroceryCartItem(
        item_id, gross_weight=gross_weight, cashback_per_unit=cashback_gain,
    )

    subitem = models.GroceryCartSubItem(
        item_id + '_0',
        price=cart_item.price,
        full_price=cart_item.price,
        quantity=cart_item.quantity,
        paid_with_cashback=cashback_charge,
    )
    item_v2 = models.GroceryCartItemV2(
        item_id,
        sub_items=[subitem],
        title=cart_item.title,
        shelf_type='parcel',
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_items([cart_item])
    grocery_cart.set_items_v2([item_v2])
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_order_conditions(delivery_cost='500', max_eta=15)
    grocery_cart.set_delivery_type('courier')
    grocery_cart.set_cashback_data(flow=cart_cashback_flow)

    depot = grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    vendor = None
    ref_order = None
    if is_parcel:
        vendor = 'beru'
        ref_order = 'external_order_id_0'

        parcels = [
            {
                'parcel_id': item_id,
                'depot_id': order.depot_id,
                'quantity_limit': cart_item.quantity,
                'title': f'title {item_id}',
                'state': 'delivering',
                'state_meta': {},
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'length': 1,
                    'weight': gross_weight,
                },
                'vendor': vendor,
                'ref_order': ref_order,
            },
        ]
        tristero_parcels.set_parcels(parcels)

    response = await taxi_grocery_orders.post(
        '/processing/v1/prepare',
        json={
            'order_id': order.order_id,
            'order_version': order.order_version,
            'flow_version': 'grocery_flow_v1',
            'payload': {},
        },
        headers=headers.HEADER_APP_INFO_YANGO,
    )

    assert response.status_code == 200
    assert tristero_parcels.get_parcels_info_times_called() == (
        1 if is_parcel else 0
    )

    order.update()

    state_change_event = processing_noncrit.check_noncrit_event(
        processing, order.order_id, 'status_change',
    )

    if cashback_gain is not None:
        cashback_gain = str(
            decimal.Decimal(cashback_gain)
            * decimal.Decimal(cart_item.quantity),
        )

    if cashback_charge is not None:
        cashback_charge = str(
            decimal.Decimal(cashback_charge)
            * decimal.Decimal(cart_item.quantity),
        )

    order_log_cart_items = [
        models.OrderLogGroceryCartItem(
            item_id,
            item_name=cart_item.title,
            price=cart_item.price,
            quantity=cart_item.quantity,
            gross_weight=gross_weight,
            parcel_vendor=vendor,
            parcel_ref_order=ref_order,
            cashback_charge=cashback_charge,
            cashback_gain=cashback_gain,
        ),
    ]

    order_log.check_order_log_payload(
        state_change_event,
        order,
        cart_items=[cart_item],
        order_log_cart_items=order_log_cart_items,
        depot=depot,
        is_checkout=True,
        delivery_cost='500',
        cashback_gain=cashback_gain,
        cashback_charge=cashback_charge,
    )
