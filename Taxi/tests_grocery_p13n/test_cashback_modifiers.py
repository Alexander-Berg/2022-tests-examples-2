import pytest

from tests_grocery_p13n import depot
from tests_grocery_p13n import experiments


# проверяем модификаторы иерархий menu_cashback и payment_method_cashback
@experiments.CASHBACK_EXPERIMENT_RUSSIA
@experiments.PAYMENT_METHOD_DISCOUNT_EXPERIMENT
async def test_cashback_menu_and_payment_method(
        taxi_grocery_p13n, grocery_discounts,
):
    product_id = 'product-1'
    menu_percent = '10'
    payment_method_percent = '20'

    grocery_discounts.add_cashback_discount(
        product_id=product_id,
        value_type='fraction',
        value=menu_percent,
        hierarchy_name='menu_cashback',
    )
    grocery_discounts.add_cashback_discount(
        product_id=product_id,
        value_type='fraction',
        value=payment_method_percent,
        hierarchy_name='payment_method_cashback',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': product_id, 'category_ids': []}],
            'payment_method': {'type': 'card', 'id': '1'},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'menu_cashback'},
                'product_id': product_id,
                'rule': {'gain_percent': menu_percent},
                'type': 'item_discount',
            },
            {
                'meta': {'hierarchy_name': 'payment_method_cashback'},
                'product_id': product_id,
                'rule': {'gain_percent': payment_method_percent},
                'type': 'payment_method_discount',
            },
        ],
    }


# 2 скидки кешбеком: одна из иерархии menu_discounts другая из иерархии
# menu_cashback. Скидка возвращается только из иерархии menu_cashback
@experiments.CASHBACK_EXPERIMENT_RUSSIA
async def test_cashback_discount_filtered(
        taxi_grocery_p13n, grocery_discounts,
):
    product_id = 'product-one'
    grocery_discounts.add_cashback_discount(
        product_id=product_id,
        value_type='fraction',
        value='10',
        hierarchy_name='menu_discounts',
    )
    grocery_discounts.add_cashback_discount(
        product_id=product_id, value_type='fraction', value='50',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'catalog',
            'depot': depot.DEPOT,
            'items': [{'product_id': product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    assert response.json() == {
        'modifiers': [
            {
                'meta': {'hierarchy_name': 'menu_cashback'},
                'product_id': product_id,
                'rule': {'gain_percent': '50'},
                'type': 'item_discount',
            },
        ],
    }


# проверяем модификаторы иерархии cart_cashback
# при отключенном эксперименте модификаторы данной
# иерархии не возвращаются
@pytest.mark.parametrize(
    'is_cashback_on',
    [
        pytest.param(
            True,
            id='cashback_on',
            marks=[experiments.CASHBACK_EXPERIMENT_RUSSIA],
        ),
        pytest.param(False, id='cashback_off', marks=[]),
    ],
)
async def test_cart_cashback_hierarchy(
        taxi_grocery_p13n, grocery_discounts, is_cashback_on,
):
    product_id = 'product-1'
    table_items = [
        {
            'discount': {'value': '10', 'value_type': 'absolute'},
            'from_cost': '75',
        },
        {
            'discount': {'value': '15', 'value_type': 'fraction'},
            'from_cost': '100',
        },
    ]

    grocery_discounts.add_cart_cashback_gain(
        product_id=product_id,
        table_items=table_items,
        hierarchy_name='cart_cashback',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [{'product_id': product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert response.json()['modifiers'] == (
        [
            {
                'meta': {'hierarchy_name': 'cart_cashback'},
                'min_cart_price': '0',
                'steps': [
                    {'rule': {'gain_value': '10'}, 'threshold': '75'},
                    {'rule': {'gain_percent': '15'}, 'threshold': '100'},
                ],
                'type': 'cart_discount',
            },
        ]
        if is_cashback_on
        else []
    )


# скидка на корзину из иерархии cart_discounts приоритетней
# скидки на корзину из иерархии cart_cashback
@experiments.CASHBACK_EXPERIMENT_RUSSIA
async def test_cart_hierarchy_priority(taxi_grocery_p13n, grocery_discounts):
    product_id = 'product-1'
    table_items_cart = [
        {
            'discount': {'value': '5', 'value_type': 'absolute'},
            'from_cost': '100',
        },
    ]
    table_items_cart_cashback = [
        {
            'discount': {'value': '5', 'value_type': 'absolute'},
            'from_cost': '200',
        },
    ]
    grocery_discounts.add_cart_cashback_gain(
        product_id=product_id, table_items=table_items_cart,
    )
    grocery_discounts.add_cart_cashback_gain(
        product_id=product_id,
        table_items=table_items_cart_cashback,
        hierarchy_name='cart_cashback',
    )

    response = await taxi_grocery_p13n.post(
        '/internal/v1/p13n/v1/discount-modifiers',
        headers={'X-Yandex-UID': '1'},
        json={
            'purpose': 'cart',
            'depot': depot.DEPOT,
            'items': [{'product_id': product_id, 'category_ids': []}],
        },
    )
    assert response.status_code == 200
    assert response.json()['modifiers'] == (
        [
            {
                'meta': {'hierarchy_name': 'cart_discounts'},
                'min_cart_price': '0',
                'steps': [{'rule': {'gain_value': '5'}, 'threshold': '100'}],
                'type': 'cart_discount',
            },
        ]
    )
