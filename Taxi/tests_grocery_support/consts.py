# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks.models import cart


def _make_cart_item_v2(
        item_id, price, quantity, refunded=0, promocode=0, cashback=0,
):
    sub_items = [
        cart.GroceryCartSubItem(
            item_id=item_id + '_0',
            price=str(price),
            full_price=str(price),
            quantity=str(quantity),
            paid_with_promocode=str(promocode),
            paid_with_cashback=str(cashback),
        ),
    ]

    return cart.GroceryCartItemV2(
        item_id=item_id,
        sub_items=sub_items,
        title=item_id,
        refunded_quantity=str(refunded),
    )


CART_ITEMS = [
    _make_cart_item_v2('id1', price='8.35', quantity=2, refunded=1),
    _make_cart_item_v2(
        'id2', price='5.65', quantity=1, promocode=1, cashback=1,
    ),
]

PRICE_LIMIT = '2'
TICKET_QUEUE = 'test_queue'
TICKET_TAGS = ['test_tag', 'another_test_tag']
FIRST_ORDER_COUNT = 1
CREATION_DELAY = 1

LATE_ORDER_SUMMARY = 'Заказ опаздывает'
EXPENSIVE_ORDER_SUMMARY = 'Дорогой заказ'
VIP_ORDER_SUMMARY = 'Заказ важной персоны'
CANCELED_ORDER_SUMMARY = 'Отмененный заказ'
FIRST_ORDER_SUMMARY = 'Первый заказ'

LONG_SEARCH_INFORMER = 'long_courier_search'
LONG_SEARCH_PROMOCODE_INFORMER = 'long_courier_search_promocode'
LONG_DELIVERY_INFORMER = 'long_delivery'
LONG_DELIVERY_PROMOCODE_INFORMER = 'long_delivery_promocode'
