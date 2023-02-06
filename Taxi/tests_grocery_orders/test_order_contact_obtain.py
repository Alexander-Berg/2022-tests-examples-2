import uuid

import pytest

from . import headers
from . import models


@pytest.mark.parametrize(
    'performer_contact_error_code,status,delivery_type,started',
    [
        (None, 409, 'pickup', True),
        (None, 200, 'courier', True),
        ('204', 409, 'courier', True),
        ('404', 409, 'courier', True),
        (500, 500, 'courier', True),
        (None, 500, 'courier', False),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_dispatch,
        performer_contact_error_code,
        status,
        delivery_type,
        testpoint,
        started,
):
    dispatch_id = str(uuid.uuid4())
    courier_contact_phone = '+79091237492'
    courier_contact_ext = '632'

    @testpoint('fix-log-no-phone')
    def testpoint_logs(data):
        assert courier_contact_phone not in data['log']
        assert courier_contact_ext not in data['log']

    order = models.Order(pgsql=pgsql, status='assembled')

    if started:
        order.upsert(
            dispatch_status_info=models.DispatchStatusInfo(
                dispatch_id, 'delivering', 'new',
            ),
            status='delivering',
        )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type(delivery_type)

    grocery_dispatch.set_data(
        dispatch_id=dispatch_id,
        performer_contact_phone=courier_contact_phone,
        performer_contact_ext=courier_contact_ext,
        performer_contact_error_code=performer_contact_error_code,
        performer_id='01234567-89ab-cdef-0123-456789abcdef',
    )

    response = await taxi_grocery_orders.post(
        '/lavka/v1/orders/v1/contact/obtain',
        json={'order_id': order.order_id},
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == status
    if status == 200:
        assert response.json() == {
            'phone': courier_contact_phone,
            'ext': courier_contact_ext,
        }

    if delivery_type != 'pickup' and started:
        assert grocery_dispatch.times_performer_contact_called() == 1

    if status == 200:
        assert testpoint_logs.times_called == 1
