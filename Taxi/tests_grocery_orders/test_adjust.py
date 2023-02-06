import pytest

from . import headers
from . import models

CART_ID = '00000000-0000-0000-0000-d98013100500'
TAXI_USER_ID = 'taxi_user_id'
NOW = '2020-11-12T13:00:50.283761+00:00'
CURRENCY = 'ILS'
PRICE = 12.3
QUANTITY = 4
TOTAL_PRICE_ROUNDED = 49  # int(price * quantity)


@pytest.fixture(name='_setup_order')
def _setup_order(pgsql, grocery_cart, grocery_depots):
    def inner(app_name, currency=CURRENCY):
        order = models.Order(
            pgsql,
            taxi_user_id=TAXI_USER_ID,
            yandex_uid=headers.YANDEX_UID,
            cart_id=CART_ID,
            state=models.OrderState(close_money_status='success'),
            app_info='app_name={}'.format(app_name),
        )
        grocery_cart.set_cart_data(cart_id=CART_ID)
        grocery_cart.set_items(
            [
                models.GroceryCartItem(
                    item_id='item_id',
                    currency=currency,
                    price=str(PRICE),
                    quantity=str(QUANTITY),
                ),
            ],
        )
        grocery_depots.add_depot(order.depot_id)

        return order

    return inner


@pytest.mark.now('2020-11-12T13:00:50.283761+00:00')
@pytest.mark.parametrize(
    'app_name,is_first_order,event_type',
    [
        (
            'yangodeli_android',
            True,
            'first_successful_purchase_grocery_to_deliapp',
        ),
        (
            'yangodeli_android',
            False,
            'repeat_successful_purchase_grocery_to_deliapp',
        ),
        (
            'yangodeli_iphone',
            True,
            'first_successful_purchase_grocery_to_deliapp',
        ),
        (
            'yangodeli_iphone',
            False,
            'repeat_successful_purchase_grocery_to_deliapp',
        ),
        (
            'mobileweb_yango_android',
            True,
            'first_successful_purchase_grocery_to_yango',
        ),
        (
            'mobileweb_yango_android',
            False,
            'repeat_successful_purchase_grocery_to_yango',
        ),
        (
            'mobileweb_yango_iphone',
            True,
            'first_successful_purchase_grocery_to_yango',
        ),
        (
            'mobileweb_yango_iphone',
            False,
            'repeat_successful_purchase_grocery_to_yango',
        ),
    ],
)
async def test_adjust_basic(
        taxi_grocery_orders,
        pgsql,
        grocery_cart,
        _setup_order,
        adjust_provider,
        app_name,
        is_first_order,
        event_type,
):
    order = _setup_order(app_name)
    if not is_first_order:
        _add_previous_order(pgsql)

    adjust_provider.check_event_payload(
        {
            'createdAt': NOW,
            'deviceId': TAXI_USER_ID,
            'type': event_type,
            'data': {
                'currency': CURRENCY,
                'orderNr': order.order_id,
                'revenue': TOTAL_PRICE_ROUNDED,
                'userId': CART_ID,
            },
        },
    )

    response = await _close_and_finish_order(
        taxi_grocery_orders, adjust_provider, order,
    )
    assert response.status_code == 200

    assert adjust_provider.events_times_called() == 1


async def test_adjust_dont_send_in_russia(
        taxi_grocery_orders, grocery_cart, _setup_order, adjust_provider,
):
    order = _setup_order('random_app_name')

    response = await _close_and_finish_order(
        taxi_grocery_orders, adjust_provider, order,
    )
    assert response.status_code == 200

    assert adjust_provider.events_times_called() == 0


async def test_adjust_dont_send_rub_currency(
        taxi_grocery_orders, grocery_cart, _setup_order, adjust_provider,
):
    order = _setup_order('yangodeli_android', 'RUB')

    response = await _close_and_finish_order(
        taxi_grocery_orders, adjust_provider, order,
    )
    assert response.status_code == 200

    assert adjust_provider.events_times_called() == 0


async def _close_and_finish_order(taxi_grocery_orders, adjust_provider, order):
    await taxi_grocery_orders.post(
        '/processing/v1/close',
        json={
            'order_id': order.order_id,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': False,
            'payload': {},
        },
    )

    adjust_provider.flush()

    response = await taxi_grocery_orders.post(
        '/processing/v1/finish',
        json={
            'order_id': order.order_id,
            'flow_version': 'grocery_flow_v1',
            'is_canceled': False,
            'payload': {},
        },
    )

    return response


def _add_previous_order(pgsql):
    models.Order(pgsql, status='closed', yandex_uid=headers.YANDEX_UID)
