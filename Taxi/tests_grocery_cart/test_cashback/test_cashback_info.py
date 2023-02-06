import os

from grocery_mocks import grocery_p13n as modifiers  # pylint: disable=E0401
import pytest


YT_SKIP = pytest.mark.skipif(
    not os.getenv('IS_TEAMCITY')
    and not os.getenv('GROCERY_CART_LOCAL_YT_TESTING'),
    reason='yt does not work locally',
)
USE_COLD_STORAGE = pytest.mark.config(
    GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True,
)
STORAGE_KIND = pytest.mark.parametrize(
    'storage_kind', [pytest.param('cs', marks=USE_COLD_STORAGE), 'pg'],
)


@pytest.mark.parametrize('cashback_flow', [None, 'disabled', 'gain', 'charge'])
async def test_cashback_info_200(
        taxi_grocery_cart, overlord_catalog, cart, cashback_flow, grocery_p13n,
):
    item_id = 'item-id'
    price = 165
    cashback = 10
    quantity = 2
    vat = '12.3'
    payment_available = cashback_flow == 'charge'
    cashback_to_pay = '1' if cashback_flow == 'charge' else None
    order_id = '123456'
    balance = 123

    overlord_catalog.add_product(product_id=item_id, price=str(price), vat=vat)
    grocery_p13n.set_cashback_info_response(
        payment_available=payment_available, balance=balance,
    )

    grocery_p13n.add_modifier(
        product_id=item_id,
        value=str(cashback),
        payment_type=modifiers.PaymentType.CASHBACK_DISCOUNT,
    )
    await cart.modify(
        products={item_id: {'q': quantity, 'p': price, 'c': cashback}},
    )
    await cart.set_payment('card')
    if cashback_flow is not None:
        await cart.set_cashback_flow(cashback_flow)
    await cart.checkout(cashback_to_pay=cashback_to_pay)
    await cart.set_order_id(order_id)

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/cashback-info', json={'order_id': order_id},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['depot'] == {'franchise': False}
    assert response_json['order_id'] == order_id
    if cashback_flow == 'gain':
        assert response_json['items'] == [
            {
                'cashback_per_unit': str(cashback),
                'item_id': item_id,
                'shelf_type': 'store',
                'title': 'title for ' + item_id,
                'price': str(price),
                'total_price': str(price * quantity),
                'vat': vat,
            },
        ]
    else:
        assert not response_json['items']


@YT_SKIP
@STORAGE_KIND
@pytest.mark.pgsql('grocery_cart', files=['cart.sql'])
@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@pytest.mark.parametrize(
    'order_id,cart_id,cart_in_pg,checkout_data_in_pg',
    [
        ('order-id-1', 'e6a59113-503c-4d3e-8c59-000000000001', True, False),
        ('order-id-2', 'e6a59113-503c-4d3e-8c59-000000000002', False, False),
        ('order-id-3', 'e6a59113-503c-4d3e-8c59-000000000003', False, True),
        ('order-id-4', 'e6a59113-503c-4d3e-8c59-000000000004', True, True),
    ],
)
async def test_cashback_info_cold_storage(
        overlord_catalog,
        grocery_cold_storage,
        order_id,
        cart_id,
        cart_in_pg,
        checkout_data_in_pg,
        storage_kind,
        grocery_depots,
        _cashback_info_cold_storage_helper,
):
    legacy_depot_id = '71249'
    overlord_catalog.add_depot(legacy_depot_id=legacy_depot_id)
    grocery_depots.add_depot(int(legacy_depot_id), auto_add_zone=False)
    depot_id = 'depot-id'
    item_id = 'd3fb22b6f07341358bff6fc69db13dfa000200010001'
    cashback = '10'
    vat = '20.00'
    price = '20'
    title = 'title-1'

    if storage_kind == 'cs':
        if not checkout_data_in_pg:
            checkout_data = {
                'item_id': cart_id,
                'cart_id': cart_id,
                'depot_id': depot_id,
                'payment_method_discount': True,
            }
            grocery_cold_storage.set_checkout_data_response(
                items=[checkout_data],
            )
            grocery_cold_storage.check_carts_request(
                item_ids=[cart_id], fields=None,
            )
        if not cart_in_pg:
            grocery_cold_storage.set_carts_by_order_id_response(
                items=[
                    {
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
                    },
                ],
            )
            grocery_cold_storage.check_carts_by_order_id_request(
                item_ids=[order_id], fields=None,
            )

    _cashback_info_cold_storage_helper.init(
        storage_kind=storage_kind,
        cart_in_pg=cart_in_pg,
        checkout_data_in_pg=checkout_data_in_pg,
    )

    response = await _cashback_info_cold_storage_helper.make_request(
        order_id=order_id,
    )
    if response.status_code == 404:
        return

    assert response.json() == {
        'depot': {'franchise': False},
        'items': [
            {
                'cashback_per_unit': cashback,
                'item_id': item_id,
                'price': price,
                'shelf_type': 'store',
                'title': title,
                'total_price': '40',
                'vat': vat,
            },
        ],
        'order_id': order_id,
    }

    _cashback_info_cold_storage_helper.check(
        grocery_cold_storage=grocery_cold_storage,
    )


@YT_SKIP
@STORAGE_KIND
@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@pytest.mark.pgsql('grocery_cart', files=['cart.sql'])
@pytest.mark.parametrize(
    'order_id,cart_id,checkout_data_in_pg,cashback_on_cart_percent',
    [
        (
            'order-id-cart-cashback-1',
            'e6a59113-503c-4d3e-8c59-000000000005',
            True,
            '5',
        ),
        (
            'order-id-cart-cashback-2',
            'e6a59113-503c-4d3e-8c59-000000000006',
            False,
            '7',
        ),
    ],
)
async def test_cashback_on_cart_percent_cs(
        grocery_cold_storage,
        order_id,
        cart_id,
        checkout_data_in_pg,
        cashback_on_cart_percent,
        storage_kind,
        _cashback_info_cold_storage_helper,
):
    if storage_kind == 'cs':
        if not checkout_data_in_pg:
            checkout_data = {
                'item_id': cart_id,
                'cart_id': cart_id,
                'depot_id': 'depot-id',
                'payment_method_discount': True,
                'cashback_on_cart_percent': cashback_on_cart_percent,
            }
            grocery_cold_storage.set_checkout_data_response(
                items=[checkout_data],
            )
            grocery_cold_storage.check_carts_request(
                item_ids=[cart_id], fields=None,
            )

    _cashback_info_cold_storage_helper.init(
        storage_kind=storage_kind,
        cart_in_pg=True,
        checkout_data_in_pg=checkout_data_in_pg,
    )

    response = await _cashback_info_cold_storage_helper.make_request(
        order_id=order_id,
    )
    if response.status_code == 404:
        return

    assert (
        response.json()['cashback_on_cart_percent'] == cashback_on_cart_percent
    )

    _cashback_info_cold_storage_helper.check(
        grocery_cold_storage=grocery_cold_storage,
    )


@YT_SKIP
@STORAGE_KIND
@pytest.mark.pgsql('grocery_cart', files=['cart.sql'])
@pytest.mark.parametrize(
    'order_id,cart_id,checkout_data_in_pg,cart_cashback_gain',
    [
        (
            'order-id-cart-cashback-1',
            'e6a59113-503c-4d3e-8c59-000000000005',
            True,
            '100',
        ),
        (
            'order-id-cart-cashback-2',
            'e6a59113-503c-4d3e-8c59-000000000006',
            False,
            '77',
        ),
    ],
)
async def test_cart_cashback_gain_cs(
        grocery_cold_storage,
        order_id,
        cart_id,
        checkout_data_in_pg,
        cart_cashback_gain,
        storage_kind,
        _cashback_info_cold_storage_helper,
):
    if storage_kind == 'cs':
        if not checkout_data_in_pg:
            checkout_data = {
                'item_id': cart_id,
                'cart_id': cart_id,
                'depot_id': 'depot-id',
                'payment_method_discount': True,
                'cart_cashback_gain': cart_cashback_gain,
            }
            grocery_cold_storage.set_checkout_data_response(
                items=[checkout_data],
            )
            grocery_cold_storage.check_carts_request(
                item_ids=[cart_id], fields=None,
            )

    _cashback_info_cold_storage_helper.init(
        storage_kind=storage_kind,
        cart_in_pg=True,
        checkout_data_in_pg=checkout_data_in_pg,
    )

    response = await _cashback_info_cold_storage_helper.make_request(
        order_id=order_id,
    )
    if response.status_code == 404:
        return

    assert response.json()['cart_cashback_gain'] == cart_cashback_gain

    _cashback_info_cold_storage_helper.check(
        grocery_cold_storage=grocery_cold_storage,
    )


@pytest.fixture
def _cashback_info_cold_storage_helper(
        testpoint, overlord_catalog, taxi_grocery_cart, grocery_depots,
):
    @testpoint('cart_in_pg_found')
    def cart_in_pg_found_tp(data):
        pass

    @testpoint('checkout_data_in_pg_found')
    def checkout_data_in_pg_found_tp(data):
        pass

    @testpoint('cart_in_cold_storage_found')
    def cart_in_cs_found_tp(data):
        pass

    @testpoint('checkout_data_in_cold_storage_found')
    def checkout_data_in_cs_found_tp(data):
        pass

    class Context:
        storage_kind = None
        cart_in_pg = None
        checkout_data_in_pg = None

        def init(self, *, storage_kind, cart_in_pg, checkout_data_in_pg):
            overlord_catalog.add_depot(legacy_depot_id='depot-id')
            grocery_depots.add_depot(100, legacy_depot_id='depot-id')
            self.storage_kind = storage_kind
            self.cart_in_pg = cart_in_pg
            self.checkout_data_in_pg = checkout_data_in_pg

        async def make_request(self, *, order_id):
            response = await taxi_grocery_cart.post(
                '/internal/v1/cart/cashback-info',
                json={
                    'order_id': order_id,
                    'yt_lookup': self.storage_kind != 'pg',
                },
            )

            if self.storage_kind != 'pg':
                assert response.status_code == 200
            else:
                if self.cart_in_pg and self.checkout_data_in_pg:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 404

            return response

        def check(self, *, grocery_cold_storage):
            if self.storage_kind == 'cs':
                assert grocery_cold_storage.carts_times_called() == 0
            if self.cart_in_pg:
                assert cart_in_pg_found_tp.times_called == 1
                assert cart_in_cs_found_tp.times_called == 0
                if self.storage_kind == 'cs':
                    assert (
                        grocery_cold_storage.carts_by_order_id_times_called()
                        == 0
                    )
            else:
                assert cart_in_pg_found_tp.times_called == 0
                assert cart_in_cs_found_tp.times_called == 1
                if self.storage_kind == 'cs':
                    assert (
                        grocery_cold_storage.carts_by_order_id_times_called()
                        == 1
                    )

            if self.checkout_data_in_pg:
                assert checkout_data_in_pg_found_tp.times_called == 1
                assert checkout_data_in_cs_found_tp.times_called == 0
                if self.storage_kind == 'cs':
                    assert (
                        grocery_cold_storage.checkout_data_times_called() == 0
                    )
            else:
                assert checkout_data_in_pg_found_tp.times_called == 0
                assert checkout_data_in_cs_found_tp.times_called == 1
                if self.storage_kind == 'cs':
                    assert (
                        grocery_cold_storage.checkout_data_times_called() == 1
                    )

    context = Context()
    return context
