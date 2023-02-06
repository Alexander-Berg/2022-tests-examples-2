import json

import pytest

from . import consts
from . import headers
from . import models


@pytest.mark.parametrize('limited_discount_ids', [['test1', 'test2'], None])
async def test_processing_discount_use(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        mocked_time,
        stq,
        limited_discount_ids,
):
    order = models.Order(pgsql=pgsql)
    order.upsert(status='checked_out')

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('pickup')
    grocery_cart.set_limited_discount_ids(
        limited_discount_ids=limited_discount_ids,
    )

    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    request = {
        'order_id': order.order_id,
        'order_version': order.order_version,
        'flow_version': 'grocery_flow_v1',
        'payload': {},
    }
    mocked_time.set(consts.NOW_DT)
    response = await taxi_grocery_orders.post(
        '/processing/v1/reserve', json=request,
    )
    assert response.status_code == 200

    if limited_discount_ids is not None:
        assert stq.grocery_discounts_discount_usage_add.times_called == 1
        args = stq.grocery_discounts_discount_usage_add.next_call()
        assert args['id'] == order.order_id
        args['kwargs'].pop('log_extra')
        args['kwargs']['discount_ids'] = args['kwargs']['discount_ids'].sort()
        assert args['kwargs'] == {
            'order_id': order.order_id,
            'yandex_uid': int(headers.YANDEX_UID),
            'personal_phone_id': headers.PERSONAL_PHONE_ID,
            'discount_ids': limited_discount_ids.sort(),
            'add_time': consts.NOW_DT.isoformat(),
        }
    else:
        assert stq.grocery_discounts_discount_usage_add.times_called == 0


@pytest.mark.parametrize('limited_discount_ids', [['test1', 'test2'], None])
async def test_processing_discount_cancel(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        mocked_time,
        stq,
        limited_discount_ids,
):
    order = models.Order(
        pgsql=pgsql,
        status='canceled',
        state=models.OrderState(close_money_status='success'),
    )

    grocery_cart.set_cart_data(cart_id=order.cart_id)
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_delivery_type('pickup')
    grocery_cart.set_limited_discount_ids(
        limited_discount_ids=limited_discount_ids,
    )
    grocery_depots.add_depot(legacy_depot_id=order.depot_id)

    models.OrderAuthContext(
        pgsql=pgsql,
        order_id=order.order_id,
        raw_auth_context=json.dumps({'headers': headers.DEFAULT_HEADERS}),
    )

    mocked_time.set(consts.NOW_DT)
    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={'order_id': order.order_id, 'payload': {}},
    )
    assert response.status_code == 200
    if limited_discount_ids is not None:
        assert stq.grocery_discounts_discount_usage_cancel.times_called == 1
        args = stq.grocery_discounts_discount_usage_cancel.next_call()
        assert args['id'] == order.order_id
        args['kwargs'].pop('log_extra')
        assert args['kwargs'] == {
            'order_id': order.order_id,
            'yandex_uid': int(headers.YANDEX_UID),
            'personal_phone_id': headers.PERSONAL_PHONE_ID,
            'cancel_time': consts.NOW_DT.isoformat(),
        }
    else:
        assert stq.grocery_discounts_discount_usage_add.times_called == 0
