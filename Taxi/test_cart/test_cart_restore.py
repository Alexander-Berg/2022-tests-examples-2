import copy

import pytest

from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys

HEADERS = {
    'X-YaTaxi-Session': 'eats:123',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=android',
    'X-YaTaxi-User': 'eats_user_id=123',
}


@experiments.TIPS_EXPERIMENT
@pytest.mark.experiments3(filename='exp_del_type.json')
@pytest.mark.parametrize('change_session', (False, True))
@pytest.mark.parametrize(
    'order_id,offer_id,expected_code,available_for_checkout,product_ids,'
    'promocode,delivery_type,cashback_flow,tips_amount,tips_amount_type',
    [
        (
            '111-exists',
            '777',
            200,
            True,
            '1',
            None,
            'eats_dispatch',
            None,
            None,
            None,
        ),
        (
            '111-exists',
            None,
            200,
            True,
            '1',
            None,
            'eats_dispatch',
            None,
            None,
            None,
        ),
        ('111-notexists', '777', 404, None, '1', None, None, None, None, None),
        ('111-wronguser', '777', 404, None, '1', None, None, None, None, None),
        (
            '111-notavail',
            '777',
            200,
            False,
            '1,2',
            None,
            'eats_dispatch',
            None,
            None,
            None,
        ),
        (
            '111-promo',
            '777',
            200,
            True,
            '1',
            'LAVKA',
            'eats_dispatch',
            None,
            None,
            None,
        ),
        (
            '111-delivery',
            '777',
            200,
            True,
            '1',
            None,
            'rover',
            None,
            None,
            None,
        ),
        (
            '111-cashback',
            '777',
            200,
            True,
            '1',
            None,
            'eats_dispatch',
            'gain',
            None,
            None,
        ),
        (
            '111-tips',
            '777',
            200,
            True,
            '1',
            None,
            'eats_dispatch',
            None,
            '49',
            'absolute',
        ),
    ],
)
async def test_cart_restore(
        taxi_grocery_cart,
        mockserver,
        overlord_catalog,
        grocery_coupons,
        grocery_p13n,
        change_session,
        order_id,
        offer_id,
        expected_code,
        available_for_checkout,
        product_ids,
        promocode,
        delivery_type,
        cashback_flow,
        tips_amount,
        tips_amount_type,
):
    balance = 200
    payment_available = True
    product_ids = product_ids.split(',')

    overlord_catalog.add_product(
        product_id='1', price='100', in_stock='1234.5678',
    )
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )
    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)

    @mockserver.json_handler('/eats-promocodes/promocodes/grocery/validate')
    def _mock_promocode_validate(request):
        return {
            'payload': {
                'validationResult': {
                    'valid': True,
                    'message': '1',
                    'promocode': {
                        'discount': '200',
                        'discountType': 'fixed',
                        'discountLimit': '500',
                        'discountResult': '100',
                    },
                },
            },
        }

    request = {
        'position': keys.DEFAULT_POSITION,
        'order_id': order_id,
        'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
    }
    if offer_id is not None:
        request['offer_id'] = offer_id
    headers = HEADERS.copy()
    headers['User-Agent'] = keys.DEFAULT_USER_AGENT
    if change_session:
        headers['X-YaTaxi-Session'] = 'brand_new_session'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/restore', json=request, headers=headers,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        products = {
            product['id']: (product['price'], product.get('catalog_price'))
            for product in response_json['items']
        }
        all_products = {'1': ('100', '100'), '2': ('55', None)}
        expected_products = {
            k: v for k, v in all_products.items() if k in product_ids
        }
        assert products == expected_products
        assert (
            response_json['available_for_checkout'] == available_for_checkout
        )
        if promocode is not None:
            assert response_json['promocode']['code'] == promocode
        else:
            assert 'promocode' not in response_json
        if delivery_type is not None:
            assert response_json['delivery_type'] == delivery_type
        else:
            assert 'delivery_type' not in response_json
        if cashback_flow is not None:
            assert response_json['cashback_flow'] == cashback_flow
        else:
            assert 'cashback_flow' not in response_json
        if tips_amount is not None and tips_amount_type is not None:
            assert response_json['tips'] == {
                'amount': tips_amount,
                'amount_type': tips_amount_type,
                'payment_flow': 'separate',
            }
        else:
            assert 'tips' not in response_json

        assert overlord_catalog.times_called() == 1


@pytest.mark.pgsql('grocery_cart', files=['localized_product.sql'])
@pytest.mark.parametrize('locale', ['en', 'ru', 'he'])
async def test_return_localized_product(
        taxi_grocery_cart, overlord_catalog, load_json, locale,
):
    localized = load_json('expected_product_localization.json')
    overlord_catalog.add_product(
        product_id='localized_product', price='100', in_stock='1234.5678',
    )

    request = {
        'position': keys.DEFAULT_POSITION,
        'order_id': '111-exists',
        'offer_id': '777',
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/restore',
        json=request,
        headers={**HEADERS, 'X-Request-Language': locale},
    )
    assert response.status_code == 200
    item = response.json()['items'][0]
    assert item['title'] == localized[locale]['title']
    assert item['subtitle'] == localized[locale]['subtitle']


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
async def test_restore_cold_storage(
        taxi_grocery_cart,
        grocery_cold_storage,
        grocery_coupons,
        cart,
        eats_promocodes,
        overlord_catalog,
        grocery_p13n,
):
    cart_id = 'e6a59113-503c-4d3e-8c59-000000000020'
    order_id = 'hdirxr78ien2d-grocery'
    cart_version = 1
    depot_id = 'some-depot-id'
    user_type = 'taxi'
    user_id = 'user_1'
    delivery_type = 'eats_dispatch'
    promocode = 'LAVKA100'
    cashback_flow = 'gain'
    payment_method_type = 'card'
    payment_method_id = 'card-132'
    payment_method_meta = {}
    tips_amount = '5'
    tips_amount_type = 'absolute'
    tips = {
        'amount': tips_amount,
        'amount_type': tips_amount_type,
        'payment_flow': 'separate',
    }

    overlord_catalog.add_product(
        product_id='3564d458-9a8a-11ea-7681-314846475f02',
        price='399',
        in_stock='1',
    )
    overlord_catalog.add_product(
        product_id='42d3bca8-7f0a-11ea-639c-75b2947ca357',
        price='239',
        in_stock='1',
    )
    overlord_catalog.add_product(
        product_id='714f1f23-200a-11ea-b802-ac1f6b8569b3',
        price='169',
        in_stock='1',
    )

    grocery_cold_storage.set_carts_by_order_id_response(
        items=[
            {
                'item_id': order_id,
                'cart_id': cart_id,
                'depot_id': depot_id,
                'order_id': order_id,
                'cart_version': cart_version,
                'user_type': user_type,
                'user_id': user_id,
                'checked_out': True,
                'promocode': promocode,
                'idempotency_token': '123',
                'delivery_type': delivery_type,
                'cashback_flow': cashback_flow,
                'payment_method_type': payment_method_type,
                'payment_method_id': payment_method_id,
                'payment_method_meta': payment_method_meta,
                'tips_amount': tips_amount,
                'tips_amount_type': tips_amount_type,
                'items': [
                    {
                        'currency': 'RUB',
                        'item_id': '3564d458-9a8a-11ea-7681-314846475f02',
                        'price': '299',
                        'full_price': '399',
                        'refunded_quantity': '0',
                        'quantity': '1',
                        'title': 'Куриные кебабы «Спидини»',
                        'vat': '20.00',
                    },
                    {
                        'currency': 'RUB',
                        'item_id': '42d3bca8-7f0a-11ea-639c-75b2947ca357',
                        'price': '239',
                        'full_price': '239',
                        'refunded_quantity': '0',
                        'quantity': '1',
                        'title': 'Борщ с подкопчённым говяжьим ребром Two One',
                    },
                    {
                        'currency': 'RUB',
                        'item_id': '714f1f23-200a-11ea-b802-ac1f6b8569b3',
                        'price': '169',
                        'full_price': '169',
                        'refunded_quantity': '0',
                        'quantity': '1',
                        'title': 'title_123',
                    },
                ],
            },
        ],
    )

    grocery_cold_storage.check_carts_by_order_id_request(
        item_ids=[order_id], fields=None,
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/restore',
        headers={
            **HEADERS,
            'X-Request-Language': 'ru',
            'User-Agent': keys.DEFAULT_USER_AGENT,
        },
        json={
            'position': keys.DEFAULT_POSITION,
            'order_id': order_id,
            'offer_id': '777',
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
    )
    assert response.status_code == 200

    response_json = response.json()

    products = {
        product['id']: (
            product['price'],
            product.get('catalog_price'),
            product['quantity'],
            product['title'],
        )
        for product in response_json['items']
    }

    assert products == {
        '3564d458-9a8a-11ea-7681-314846475f02': (
            '299',
            '399',
            '1',
            'title for 3564d458-9a8a-11ea-7681-314846475f02',
        ),
        '42d3bca8-7f0a-11ea-639c-75b2947ca357': (
            '239',
            '239',
            '1',
            'title for 42d3bca8-7f0a-11ea-639c-75b2947ca357',
        ),
        '714f1f23-200a-11ea-b802-ac1f6b8569b3': (
            '169',
            '169',
            '1',
            'title for 714f1f23-200a-11ea-b802-ac1f6b8569b3',
        ),
    }

    assert response_json['cart_version'] == 1

    assert response_json['promocode']['code'] == promocode

    assert response_json['delivery_type'] == delivery_type
    assert response_json['cashback_flow'] == cashback_flow
    assert response_json['tips'] == tips

    new_cart_id = response_json['cart_id']

    cart_data = cart.fetch_db(cart_id=new_cart_id)

    assert cart_data.cart_version == 1
    assert cart_data.delivery_type == delivery_type
    assert cart_data.payment_method_type == payment_method_type
    assert cart_data.payment_method_id == payment_method_id
    assert cart_data.payment_method_meta == payment_method_meta

    items = cart.fetch_items(cart_id=new_cart_id)
    assert len(items) == 3

    products = {
        product.item_id: (str(int(product.price)), str(int(product.quantity)))
        for product in items
    }

    assert products == {
        '3564d458-9a8a-11ea-7681-314846475f02': ('299', '1'),
        '42d3bca8-7f0a-11ea-639c-75b2947ca357': ('239', '1'),
        '714f1f23-200a-11ea-b802-ac1f6b8569b3': ('169', '1'),
    }

    assert grocery_p13n.discount_modifiers_times_called == 1


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(
        taxi_grocery_cart,
        user_api,
        grocery_coupons,
        cart,
        has_personal_phone_id,
):
    headers = copy.deepcopy(HEADERS)
    headers['X-Yandex-UID'] = 'some_uid'
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    request = {
        'position': keys.DEFAULT_POSITION,
        'order_id': '111-exists',
        'offer_id': '777',
    }
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/restore', json=request, headers=headers,
    )
    assert response.status_code == 200
    assert user_api.times_called == (1 if has_personal_phone_id else 0)
