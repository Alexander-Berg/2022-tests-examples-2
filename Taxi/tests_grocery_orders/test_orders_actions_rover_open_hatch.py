import uuid

import pytest

from . import headers
from . import models

PROCESSING_FLOW_VERSION = 'grocery_flow_v3'


@pytest.mark.parametrize(
    'order_status,dispatch_status,dispatch_cargo_status,'
    'transport_type,response_code',
    [
        (
            'closed',
            'delivering',
            'ready_for_delivery_confirmation',
            'rover',
            409,
        ),
        (
            'canceled',
            'delivering',
            'ready_for_delivery_confirmation',
            'rover',
            409,
        ),
        ('assembled', None, None, None, 429),
        ('delivering', 'accepted', 'new', 'rover', 429),
        ('delivering', 'delivering', 'pickuped', 'rover', 429),
        (
            'delivering',
            'delivering',
            'ready_for_delivery_confirmation',
            'car',
            409,
        ),
        ('delivering', 'delivering', 'delivery_arrived', 'rover', 429),
        (
            'delivering',
            'delivering',
            'ready_for_delivery_confirmation',
            'rover',
            200,
        ),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        mockserver,
        load_json,
        grocery_cart,
        grocery_depots,
        pgsql,
        processing,
        grocery_dispatch,
        robot_sdc,
        grocery_supply,
        order_status,
        dispatch_status,
        dispatch_cargo_status,
        transport_type,
        response_code,
):
    courier_id = '12345'
    rover_vin = 'F4IFN32ICNSDJF22'
    taxi_alias_id = 'some_taxi_alias_id'

    dispatch_id = str(uuid.uuid4())

    order = models.Order(
        pgsql=pgsql,
        status=order_status,
        grocery_flow_version=PROCESSING_FLOW_VERSION,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status=dispatch_status,
            dispatch_cargo_status=dispatch_cargo_status,
            dispatch_transport_type=transport_type,
        )
        if dispatch_status is not None
        else models.DispatchStatusInfo(),
    )
    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_delivery_type('rover')
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_dispatch.set_data(
        dispatch_id=dispatch_id,
        performer_id=courier_id,
        eats_profile_id=courier_id,
        taxi_alias_id=taxi_alias_id,
        performer_name='Ivan',
    )
    grocery_supply.set_courier_response(
        {
            'courier_id': courier_id,
            'transport_type': transport_type,
            'full_name': rover_vin,
        },
    )
    robot_sdc.check_open_hatch(number=taxi_alias_id)

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/actions/rover/open_hatch',
        headers=headers.DEFAULT_HEADERS,
        json={'order_id': order.order_id},
    )
    assert response.status_code == response_code

    assert robot_sdc.times_open_hatch_called() == (
        1 if response_code == 200 else 0
    )
