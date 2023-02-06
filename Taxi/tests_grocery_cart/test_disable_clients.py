import pytest

from tests_grocery_cart import common
from tests_grocery_cart.plugins import keys

VALID_GROCERY_COUPONS_PROMOCODE = {
    'valid': True,
    'promocode_info': {
        'currency_code': 'RUB',
        'format_currency': True,
        'value': '100',
        'type': 'fixed',
    },
}


def _grocery_cart_disabled_clients(disabled_client):
    def _configure(disabled_clients):
        return pytest.param(
            disabled_clients,
            marks=pytest.mark.config(
                GROCERY_CART_DISABLED_CLIENTS={
                    'disabled_clients': disabled_clients,
                },
            ),
        )

    return pytest.mark.parametrize(
        'grocery_cart_disabled_clients',
        list(map(_configure, [[], [disabled_client]])),
    )


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@_grocery_cart_disabled_clients('grocery_coupons')
async def test_disable_grocery_coupons_client(
        cart,
        overlord_catalog,
        eats_promocodes,
        grocery_coupons,
        grocery_cart_disabled_clients,
):
    item_id = 'test-item'
    item = {item_id: {'q': 1, 'p': keys.DEFAULT_PRICE}}

    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id=item_id, price=str(keys.DEFAULT_PRICE),
    )

    grocery_coupons.set_check_response(
        response_body=VALID_GROCERY_COUPONS_PROMOCODE,
    )

    await cart.modify(item, headers=common.TAXI_HEADERS)
    await cart.apply_promocode(promocode, headers=common.TAXI_HEADERS)

    if grocery_cart_disabled_clients:
        assert grocery_coupons.check_times_called() == 0
    else:
        assert grocery_coupons.check_times_called() == 1


@common.GROCERY_ORDER_FLOW_VERSION_CONFIG
@common.GROCERY_ORDER_CYCLE_ENABLED
@_grocery_cart_disabled_clients('eats_promocodes')
async def test_disable_eats_promocodes_client(
        cart,
        overlord_catalog,
        grocery_coupons,
        eats_promocodes,
        grocery_cart_disabled_clients,
):
    item_id = 'test-item'
    item = {item_id: {'q': 1, 'p': keys.DEFAULT_PRICE}}

    promocode = 'test_promocode_01'
    overlord_catalog.add_product(
        product_id=item_id, price=str(keys.DEFAULT_PRICE),
    )

    grocery_coupons.set_check_response(
        response_body=VALID_GROCERY_COUPONS_PROMOCODE,
    )

    await cart.modify(item, headers=common.TAXI_HEADERS)
    await cart.apply_promocode(promocode, headers=common.TAXI_HEADERS)

    if grocery_cart_disabled_clients:
        assert eats_promocodes.times_called() == 0
    else:
        assert eats_promocodes.times_called() == 1


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@_grocery_cart_disabled_clients('grocery_cold_storage')
async def test_disable_grocery_cold_storage_client1(
        taxi_grocery_cart,
        overlord_catalog,
        grocery_cold_storage,
        grocery_coupons,
        grocery_cart_disabled_clients,
        grocery_depots,
):
    order_id = 'order-id-2'
    cart_id = 'e6a59113-503c-4d3e-8c59-000000000002'
    depot_id = 'depot-id'
    item_id = 'd3fb22b6f07341358bff6fc69db13dfa000200010001'
    cashback = '10'
    vat = '20.00'
    price = '20'
    title = 'title-1'

    cart = {
        'order_id': order_id,
        'cart_id': cart_id,
        'cart_version': 3,
        'item_id': order_id,
        'depot_id': depot_id,
        'cashback_flow': 'gain',
        'user_type': 'eats_user_id',
        'user_id': '145597824',
        'checked_out': True,
        'delivery_type': 'eats_dispatch',
        'items': [
            {
                'item_id': item_id,
                'price': price,
                'quantity': '2',
                'title': title,
                'vat': vat,
                'cashback': cashback,
                'currency': 'RUB',
            },
        ],
    }
    checkout_data = {
        'item_id': cart_id,
        'cart_id': cart_id,
        'depot_id': depot_id,
        'payment_method_discount': True,
    }

    grocery_cold_storage.set_carts_by_order_id_response(items=[cart])
    grocery_cold_storage.set_checkout_data_response(items=[checkout_data])
    overlord_catalog.add_depot(legacy_depot_id=depot_id)
    grocery_depots.add_depot(100, legacy_depot_id=depot_id)

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/cashback-info',
        json={'order_id': order_id, 'yt_lookup': True},
    )

    if grocery_cart_disabled_clients:
        assert response.status_code == 404
        assert grocery_cold_storage.carts_by_order_id_times_called() == 0
        assert grocery_cold_storage.checkout_data_times_called() == 0
    else:
        assert response.status_code == 200
        assert grocery_cold_storage.carts_by_order_id_times_called() == 1
        assert grocery_cold_storage.checkout_data_times_called() == 1
    assert grocery_cold_storage.carts_times_called() == 0


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@_grocery_cart_disabled_clients('grocery_cold_storage')
@pytest.mark.parametrize(
    'uri', ['/internal/v1/cart/retrieve/raw', '/admin/v1/cart/retrieve/raw'],
)
async def test_disable_grocery_cold_storage_client2(
        taxi_grocery_cart,
        grocery_cold_storage,
        grocery_cart_disabled_clients,
        uri,
):
    order_id = 'order-id-2'
    cart_id = 'e6a59113-503c-4d3e-8c59-000000000002'
    depot_id = 'depot-id'
    item_id = 'd3fb22b6f07341358bff6fc69db13dfa000200010001'
    cashback = '10'
    vat = '20.00'
    price = '20'
    title = 'title-1'

    cart = {
        'order_id': order_id,
        'cart_id': cart_id,
        'cart_version': 3,
        'item_id': order_id,
        'depot_id': depot_id,
        'cashback_flow': 'gain',
        'user_type': 'eats_user_id',
        'user_id': '145597824',
        'checked_out': True,
        'delivery_type': 'eats_dispatch',
        'items': [
            {
                'item_id': item_id,
                'price': price,
                'quantity': '2',
                'title': title,
                'vat': vat,
                'cashback': cashback,
                'currency': 'RUB',
            },
        ],
    }
    checkout_data = {
        'item_id': cart_id,
        'cart_id': cart_id,
        'depot_id': depot_id,
        'payment_method_discount': True,
    }

    grocery_cold_storage.set_carts_response(items=[cart])
    grocery_cold_storage.set_checkout_data_response(items=[checkout_data])

    response = await taxi_grocery_cart.post(
        uri,
        json={'cart_id': cart_id, 'source': 'YT'},
        headers=common.TAXI_HEADERS,
    )

    if grocery_cart_disabled_clients:
        assert response.status_code == 404
        assert grocery_cold_storage.carts_times_called() == 0
        assert grocery_cold_storage.checkout_data_times_called() == 0
    else:
        assert response.status_code == 200
        assert grocery_cold_storage.carts_times_called() == 1
        assert grocery_cold_storage.checkout_data_times_called() == 1
    assert grocery_cold_storage.carts_by_order_id_times_called() == 0


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@_grocery_cart_disabled_clients('grocery_cold_storage')
async def test_disable_grocery_cold_storage_client3(
        taxi_grocery_cart,
        grocery_cold_storage,
        overlord_catalog,
        grocery_coupons,
        eats_promocodes,
        grocery_cart_disabled_clients,
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
    item_id = '3564d458-9a8a-11ea-7681-314846475f02'
    price = '399'
    quantity = '1'

    overlord_catalog.add_product(
        product_id=item_id, price=price, in_stock=quantity,
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
                'items': [
                    {
                        'currency': 'RUB',
                        'item_id': item_id,
                        'price': '299',
                        'full_price': price,
                        'refunded_quantity': '0',
                        'quantity': quantity,
                        'title': 'Куриные кебабы «Спидини»',
                        'vat': '20.00',
                    },
                ],
            },
        ],
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/restore',
        headers=common.TAXI_HEADERS,
        json={
            'position': {
                'location': keys.DEFAULT_DEPOT_LOCATION,
                'uri': 'test_url',
            },
            'order_id': order_id,
            'offer_id': '555',
        },
    )

    if grocery_cart_disabled_clients:
        assert response.status_code == 404
        assert grocery_cold_storage.carts_by_order_id_times_called() == 0
    else:
        assert response.status_code == 200
        assert grocery_cold_storage.carts_by_order_id_times_called() == 1
    assert grocery_cold_storage.carts_times_called() == 0
    assert grocery_cold_storage.checkout_data_times_called() == 0


@common.GROCERY_ORDER_CYCLE_ENABLED
@_grocery_cart_disabled_clients('tristero_parcels')
async def test_disable_tristero_parcels_client(
        taxi_grocery_cart,
        offers,
        overlord_catalog,
        tristero_parcels,
        grocery_cart_disabled_clients,
        pgsql,
        grocery_depots,
):
    depot_id = '100'
    grocery_depots.add_depot(
        int(depot_id), location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_depot(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )
    overlord_catalog.add_location(
        legacy_depot_id=depot_id, location=keys.DEFAULT_DEPOT_LOCATION,
    )

    tristero_suffix = ':st-pa'
    item_id = 'item-id' + tristero_suffix
    item = {'id': item_id, 'price': '100', 'quantity': '1', 'currency': 'RUB'}

    json = {
        'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        'items': [item],
    }

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/update', json=json, headers=common.TAXI_HEADERS,
    )
    assert response.status_code == 200

    if grocery_cart_disabled_clients:
        assert tristero_parcels.times_called() == 0
    else:
        assert tristero_parcels.times_called() == 1
