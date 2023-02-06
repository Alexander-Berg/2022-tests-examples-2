import decimal

import pytest

CURSOR_DATA = pytest.mark.parametrize(
    ['cursor_data'],
    (
        pytest.param({'count': 10}, id='by cursor'),
        pytest.param(
            {'order_id': '5c44b80d-e583-4d0a-a74a-f53cf070b4f6'}, id='by id',
        ),
    ),
)

COLD_STORAGE_CURSOR_DATA = pytest.mark.parametrize(
    ['cursor_data'],
    (
        pytest.param({'count': 10}, id='by cursor'),
        pytest.param({'order_id': 'cold-grocery'}, id='by id'),
    ),
)

CONFIG_CURRENCY_FORMATTING_RULES = pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        'RUB': {
            '__default__': 1,
            'grocery': 2,  # проверяем что возьмется именно grocery
        },
    },
)


def from_template(price):
    if not price:
        return None
    return price.split(' ')[0]


def fetch_delivery_cost(addends):
    for addend in addends:
        if 'product_id' not in addend:
            return from_template(addend['cost'])
    return None


def create_cart_items(addends, map_price=lambda x: x):
    cart_items = []
    for addend in addends:
        if 'product_id' in addend:
            price = addend['cost']
            cart_item = {
                'item_name': addend['name'],
                'price': from_template(price),
            }
            if 'product_id' in addend:
                cart_item['id'] = addend['product_id']
            if 'count' in addend:
                cart_item['quantity'] = (
                    str(int(decimal.Decimal(addend['count']))) + '.490000'
                )
            if 'gross_weight' in addend:
                cart_item['gross_weight'] = str(
                    decimal.Decimal(addend['gross_weight']),
                )
            if 'cashback_gain' in addend:
                cart_item['cashback_gain'] = str(
                    decimal.Decimal(map_price(addend['cashback_gain'])),
                )
            if 'cashback_charge' in addend:
                cart_item['cashback_charge'] = str(
                    decimal.Decimal(map_price(addend['cashback_charge'])),
                )
            if 'parcel_vendor' in addend:
                cart_item['parcel_vendor'] = addend['parcel_vendor']
            if 'parcel_ref_order' in addend:
                cart_item['parcel_ref_order'] = addend['parcel_ref_order']
            if 'discounts' in addend:
                cart_item['discounts'] = addend['discounts']
            if 'image_url' in addend:
                cart_item['image_url'] = addend['image_url']
            if 'refunded_quantity' in addend:
                cart_item['refunded_quantity'] = addend['refunded_quantity']
            if 'status' in addend:
                cart_item['status'] = addend['status']
            cart_items.append(cart_item)
    return cart_items
