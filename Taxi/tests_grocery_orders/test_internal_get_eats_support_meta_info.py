import datetime
import uuid

import pytest

from . import consts
from . import headers
from . import models


HEADERS = {
    'X-YaTaxi-Pass-Flags': '',
    'X-YaTaxi-User': 'eats_user_id=test_eats_user_id',
    'X-YaTaxi-Session': 'test_domain:test_session',
    'X-YaTaxi-Bound-Sessions': 'old_test_domain:old_test_session',
}

DEFAULT_ETA = 55
NOW_TIME = consts.NOW


@pytest.mark.parametrize(
    'status, dispatch_status, cargo_status, cancel_reason, finished_at, '
    'eta, courier_contact_error_code',
    [
        ('delivering', 'delivering', 'performer_found', None, None, 25, None),
        ('delivering', 'accepted', 'pickuped', None, None, 15, None),
        ('closed', 'closed', 'delivered_finish', None, NOW_TIME, 35, 404),
        ('delivering', 'created', 'new', None, None, None, 500),
        (
            'canceled',
            'revoked',
            'cancelled',
            'admin_request',
            NOW_TIME,
            None,
            404,
        ),
        (
            'canceled',
            'revoked',
            'cancelled',
            'payment_failed',
            NOW_TIME,
            None,
            404,
        ),
        ('canceled', 'failed', 'failed', 'dispatch_failure', None, None, 404),
    ],
)
@pytest.mark.now(NOW_TIME)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_depots,
        grocery_cart,
        grocery_dispatch,
        personal,
        testpoint,
        status,
        dispatch_status,
        cargo_status,
        courier_contact_error_code,
        cancel_reason,
        finished_at,
        eta,
):
    dispatch_id = str(uuid.uuid4())
    user_number = '+79137777777'
    courier_number = '+79139999999'

    @testpoint('fix-log-no-phone')
    def testpoint_logs(data):
        assert user_number not in data['log']
        assert courier_number not in data['log']

    order = models.Order(
        pgsql=pgsql,
        dispatch_status_info=models.DispatchStatusInfo(
            dispatch_id=dispatch_id,
            dispatch_status=dispatch_status,
            dispatch_cargo_status=cargo_status,
        ),
        finished=finished_at,
        cancel_reason_type=cancel_reason,
        dispatch_flow='grocery_dispatch',
        status=status,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    grocery_cart.set_depot_id(depot_id=order.depot_id)
    grocery_cart.set_cart_data(
        cart_id=order.cart_id, cart_version=order.cart_version,
    )
    grocery_cart.set_order_conditions(delivery_cost=137, max_eta=eta)

    if courier_contact_error_code:
        grocery_dispatch.set_data(
            performer_contact_error_code=courier_contact_error_code,
        )
    else:
        grocery_dispatch.set_data(
            order_id=order.order_id,
            items=grocery_cart.get_items(),
            dispatch_id=dispatch_id,
            performer_contact_phone=courier_number,
            performer_contact_ext='632',
            performer_id='123',
            eats_profile_id='1010',
        )

    personal.phone = user_number
    personal.personal_phone_id = headers.PERSONAL_PHONE_ID

    response = await taxi_grocery_orders.post(
        '/internal/v1/get-eats-support-meta-info',
        headers=HEADERS,
        json={'order_id': order.order_id},
    )

    assert response.status_code == 200

    assert response.json()['order_id'] == order.order_id
    assert response.json()['order_status'] == order.status
    assert response.json()['cargo_status'] == cargo_status
    assert response.json()['user_phone_number'] == user_number
    assert response.json()['depot_id'] == order.depot_id

    if finished_at:
        assert response.json()['finished_at'] == finished_at
    if cancel_reason:
        assert response.json()['cancel_reason'] == cancel_reason

    if courier_contact_error_code or dispatch_status not in (
            'delivering',
            'accepted',
    ):
        assert 'courier_phone_number' not in response.json()
    else:
        assert response.json()['courier_phone_number'] == courier_number

    assert (
        response.json()['promised_delivery_ts']
        == (
            order.created
            + datetime.timedelta(minutes=(eta if eta else DEFAULT_ETA))
        ).isoformat()
    )

    assert testpoint_logs.times_called == 1
