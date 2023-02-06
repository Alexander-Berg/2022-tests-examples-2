import datetime

import pytest

from tests_grocery_marketing import models

SOME_CART_ID = '00000000-0000-0000-0000-d98013100500'


# получить цену в копейках
def get_price_with_precision(price_str):
    return str(int(price_str) * 100)


def get_price_obj(price_str, currency):
    return {
        'amount': get_price_with_precision(price_str),
        'currency': currency,
    }


async def test_send_to_lb(
        taxi_grocery_marketing,
        stq_runner,
        grocery_cart,
        grocery_order_log,
        overlord_catalog,
        grocery_depots,
        testpoint,
        mockserver,
):
    yandex_uid = '123456'
    depot_id = '991234'
    order_id = 'something-grocery'
    product_ids = ['123']
    categories = ['category-1', 'category-2']
    currency = 'CURRENCY_RUB'
    personal_phone_id = '+375001231234'
    order_created = '2019-07-12T15:19:21+03:00'
    order_created_ts = str(
        int(datetime.datetime.fromisoformat(order_created).timestamp()),
    )

    @mockserver.json_handler('/grocery-cashback/cashback/v1/order-calculator')
    def _mock_cashback_calculator(request):
        assert request.query['order_id'] == order_id
        return {'cashback': '120.00', 'currency': 'RUB'}

    grocery_order_log.set_order_id(order_id=order_id)
    grocery_order_log.set_yandex_uid(yandex_uid=yandex_uid)
    grocery_order_log.set_order_meta(
        personal_phone_id=personal_phone_id,
        cart_id=SOME_CART_ID,
        order_type='grocery',
        order_state='closed',
    )
    grocery_order_log.set_order_raw(
        depot_id=depot_id,
        status='closed',
        created_at=order_created,
        cashback_gain='120',
    )

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    for product_id in product_ids:
        overlord_catalog.add_product(
            product_id=product_id, category_ids=categories,
        )

    cart_version = 10

    grocery_cart_products = [
        models.GroceryCartItemV2(
            item_id=product_id,
            sub_items=[
                models.GroceryCartSubItem(
                    item_id=product_id,
                    full_price='100',
                    price='100',
                    paid_with_cashback='30',
                    quantity='2',
                ),
            ],
        )
        for product_id in product_ids
    ]

    grocery_cart.set_cart_data(cart_id=SOME_CART_ID, cart_version=cart_version)
    grocery_cart.set_items_v2(items=grocery_cart_products)

    @testpoint('grocery_marketing_plus_game_send_event')
    def send_event(data):
        assert data == {
            'createdTimestamp': order_created_ts,
            'id': order_id,
            'type': 'EVENT_TYPE_LAVKA_ORDER',
            'puid': yandex_uid,
            'platform': 'PLATFORM_ANDROID',
            'lavkaOrder': {
                'orderId': order_id,
                'categories': categories,
                'transaction': {
                    'cashbackGain': get_price_obj('120', currency),
                    'cashbackSpend': get_price_obj('30', currency),
                    'price': get_price_obj('200', currency),
                },
            },
        }

    @testpoint('logbroker_publish')
    def publish(data):
        assert data['name'] == 'lavka-plus-game-producer'

    await stq_runner.grocery_marketing_plus_game.call(
        task_id=order_id,
        kwargs={
            'order_id': order_id,
            'application': 'lavka_android',
            'yandex_uid': yandex_uid,
        },
    )

    # assert stq.grocery_marketing_plus_game.times_called == 1

    await send_event.wait_call()
    await publish.wait_call()


@pytest.mark.config(
    GROCERY_MARKETING_EATS_PLUS_GAME_STQ_SETTINGS={
        'attempts': 2,
        'retry_after': 300,
    },
)
async def test_reschedule(
        taxi_grocery_marketing, stq_runner, stq, grocery_order_log,
):
    yandex_uid = '123456'
    order_id = 'something-grocery'

    grocery_order_log.set_retrieve_raw_error(code=404)

    await stq_runner.grocery_marketing_plus_game.call(
        task_id=order_id,
        kwargs={
            'order_id': order_id,
            'application': 'lavka_android',
            'yandex_uid': yandex_uid,
        },
    )

    assert stq.grocery_marketing_plus_game.times_called == 1
