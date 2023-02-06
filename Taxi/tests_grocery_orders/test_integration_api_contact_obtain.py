import pytest

from . import models


@pytest.mark.parametrize(
    'dispatch_courier_phone_error,status,delivery_type',
    [
        (None, 409, 'pickup'),
        (None, 200, 'courier'),
        ('404', 409, 'courier'),
        ('500', 500, 'courier'),
    ],
)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        grocery_dispatch,
        dispatch_courier_phone_error,
        status,
        delivery_type,
        testpoint,
):
    dispatch_id = '01234567-89ab-cdef-0123-456789abcdef'
    courier_contact_phone = '+79091237492'
    courier_contact_ext = '632'

    @testpoint('fix-log-no-phone')
    def testpoint_logs(data):
        assert courier_contact_phone not in data['log']
        assert courier_contact_ext not in data['log']

    order = models.Order(
        pgsql=pgsql,
        status='delivering',
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id, 'delivering', 'new',
        ),
        dispatch_flow='grocery_dispatch',
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type(delivery_type)

    if dispatch_courier_phone_error:
        grocery_dispatch.set_data(
            dispatch_id=dispatch_id,
            performer_contact_error_code=dispatch_courier_phone_error,
        )
    else:
        grocery_dispatch.set_data(
            order_id=order.order_id,
            items=grocery_cart.get_items(),
            dispatch_id=dispatch_id,
            performer_contact_phone=courier_contact_phone,
            performer_contact_ext=courier_contact_ext,
            performer_id='123',
            eats_profile_id='1010',
        )

    response = await taxi_grocery_orders.post(
        '/orders/v1/integration-api/v1/contact/obtain',
        json={'order_id': order.order_id},
    )

    assert response.status_code == status
    if status == 200:
        assert response.json() == {
            'phone': courier_contact_phone,
            'ext': courier_contact_ext,
        }
        assert testpoint_logs.times_called == 1

    if delivery_type != 'pickup':
        assert grocery_dispatch.times_performer_contact_called() == 1
