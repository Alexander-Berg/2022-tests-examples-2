# pylint: disable=too-many-lines
import copy

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys


FULL_SQL_CART_ID = (
    'e6a59113-503c-4d3e-8c59-000000000011'  # - полностью в SQL, promocode
)
FULL_YT_CART_ID = 'e6a59113-503c-4d3e-8c59-000000000022'  # - полностью в YT
# - cart в SQL, checkout в YT, promocode
CART_SQL_CHECKOUT_YT_CART_ID = 'e6a59113-503c-4d3e-8c59-000000000012'
# - cart в YT, checkout в SQL, promocode
CART_YT_CHECKOUT_SQL_CART_ID = 'e6a59113-503c-4d3e-8c59-000000000021'
CART_SQL_CART_ID = (
    'e6a59113-503c-4d3e-8c59-000000000010'  # - cart в SQL, checkout нет
)
CART_YT_CART_ID = (
    'e6a59113-503c-4d3e-8c59-000000000020'  # - cart в YT, checkout нет
)
CHECKOUT_SQL_CART_ID = (
    'e6a59113-503c-4d3e-8c59-000000000001'  # - checkout в SQL
)
CHECKOUT_YT_CART_ID = 'e6a59113-503c-4d3e-8c59-000000000002'  # - checkout в YT
NO_DATA_CART_ID = (
    'e6a59113-503c-4d3e-8c59-000000000099'  # - несуществующий заказ
)

ALL_CART_IDS = [
    FULL_SQL_CART_ID,
    FULL_YT_CART_ID,
    CART_SQL_CHECKOUT_YT_CART_ID,
    CART_YT_CHECKOUT_SQL_CART_ID,
    CART_SQL_CART_ID,
    CART_YT_CART_ID,
    CHECKOUT_SQL_CART_ID,
    CHECKOUT_YT_CART_ID,
    NO_DATA_CART_ID,
]

CARTS_TO_SEARCH_FOR_IN_YT = [
    FULL_YT_CART_ID,
    CART_YT_CHECKOUT_SQL_CART_ID,
    CART_YT_CART_ID,
    CHECKOUT_SQL_CART_ID,
    CHECKOUT_YT_CART_ID,
    NO_DATA_CART_ID,
]

CHECKOUTS_TO_SEARCH_FOR_IN_YT = [
    FULL_YT_CART_ID,
    CART_SQL_CHECKOUT_YT_CART_ID,
    CART_SQL_CART_ID,
    CART_YT_CART_ID,
]

CART_DATA_IDS = [
    FULL_SQL_CART_ID,
    FULL_YT_CART_ID,
    CART_SQL_CHECKOUT_YT_CART_ID,
    CART_YT_CHECKOUT_SQL_CART_ID,
    CART_SQL_CART_ID,
    CART_YT_CART_ID,
]

CART_ID = 'e6a59113-503c-4d3e-8c59-000000000020'
DELIVERY_COST = '0'
MIN_ETA = 10
MAX_ETA = 15
ORDER_CONDITIONS_WITH_ETA = {
    'delivery_cost': DELIVERY_COST,
    'min_eta': MIN_ETA,
    'max_eta': MAX_ETA,
}
TIPS_AMOUNT = '5'
TIPS_AMOUNT_TYPE = 'absolute'
TIPS = {'amount': TIPS_AMOUNT, 'amount_type': TIPS_AMOUNT_TYPE}

COLD_CART_RESPONSE = {
    'item_id': CART_ID,
    'cart_id': CART_ID,
    'order_id': 'order-id-1',
    'cart_version': 1,
    'user_type': 'taxi',
    'user_id': 'user_1',
    'delivery_type': 'eats_dispatch',
    'payment_method_type': 'card',
    'payment_method_id': 'card-x1d968ab8793bf3a1178369ff',
    'payment_method_meta': {'sbp': {}},
    'tips_amount': TIPS_AMOUNT,
    'tips_amount_type': TIPS_AMOUNT_TYPE,
    'items': [],
}

COLD_CHECKOUT_DATA = {
    'item_id': CART_ID,
    'cart_id': CART_ID,
    'depot_id': '91456',
    'cashback_on_cart_percent': '10.0000',
    'payment_method_discount': False,
    'order_conditions_with_eta': ORDER_CONDITIONS_WITH_ETA,
    'items_pricing': {'items': []},
    'has_surge': False,
}


def _map(cart_infos_unmapped):
    cart_infos = dict()
    for cart_info in cart_infos_unmapped:
        cart_infos[cart_info['cart_id']] = cart_info
    return cart_infos


@pytest.fixture(name='cold_storage')
def _mock_cold_storage(grocery_cold_storage):
    class Context:
        def __init__(self):
            self.carts_response = copy.deepcopy(COLD_CART_RESPONSE)
            self.checkout_data = copy.deepcopy(COLD_CHECKOUT_DATA)

        def add_item(self, **kwargs):
            item = kwargs
            self.carts_response['items'].append(item)

            if (
                    'status' not in item.keys()
                    or item['status'] != 'deleted_before_checkout'
            ):
                self.checkout_data['items_pricing']['items'].append(
                    {
                        'item_id': item['item_id'],
                        'sub_items': [
                            {
                                'item_id': (item['item_id'] + '_0'),
                                'full_price': item['full_price'],
                                'price': item['price'],
                                'quantity': item['quantity'],
                            },
                        ],
                    },
                )

        def mock_cold_storage(self, checked_out, carts_response=None):
            if carts_response is not None:
                self.carts_response = carts_response

            cart_id = self.carts_response.get('cart_id', CART_ID)
            self.carts_response['checked_out'] = checked_out

            grocery_cold_storage.set_carts_response(
                items=[self.carts_response],
            )

            if checked_out:
                grocery_cold_storage.set_checkout_data_response(
                    items=[self.checkout_data],
                )

            grocery_cold_storage.check_carts_request(
                item_ids=[cart_id], fields=None,
            )

            grocery_cold_storage.check_checkout_data_request(
                item_ids=[cart_id], fields=None,
            )

    context = Context()
    return context


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@pytest.mark.pgsql('grocery_cart', files=['sql_carts_checkout_data.sql'])
async def test_basic(taxi_grocery_cart, grocery_cold_storage, load_json):
    cold_storage_carts_items = load_json(
        'cold_storage_carts_response_items.json',
    )
    grocery_cold_storage.check_carts_request(
        item_ids=CARTS_TO_SEARCH_FOR_IN_YT,
    )
    grocery_cold_storage.set_carts_response(items=cold_storage_carts_items)

    _cold_storage_checkout_data_items = load_json(
        'cold_storage_checkout_data_response_items.json',
    )
    grocery_cold_storage.check_checkout_data_request(
        item_ids=CHECKOUTS_TO_SEARCH_FOR_IN_YT,
    )
    grocery_cold_storage.set_checkout_data_response(
        items=_cold_storage_checkout_data_items,
    )

    response = await taxi_grocery_cart.post(
        '/admin/v1/cart/retrieve/raw/bulk', json={'cart_ids': ALL_CART_IDS},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert 'cart_infos' in response_json
    assert len(response_json['cart_infos']) == len(CART_DATA_IDS)

    cart_infos = _map(response_json['cart_infos'])

    expected_cart_infos = _map(load_json('expected_responses.json'))
    for cart_id in ALL_CART_IDS:
        if cart_id in CART_DATA_IDS:
            assert cart_id in cart_infos
            assert cart_infos[cart_id] == expected_cart_infos[cart_id]
        else:
            assert cart_id not in cart_infos


async def test_bad_request(taxi_grocery_cart):
    response = await taxi_grocery_cart.post(
        '/admin/v1/cart/retrieve/raw/bulk', json={'cart_ids': []},
    )
    assert response.status_code == 400


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@pytest.mark.parametrize('checked_out', [False, False, True])
async def test_basic_cold_storage(
        taxi_grocery_cart, cold_storage, checked_out,
):
    cold_storage.add_item(
        currency='RUB',
        item_id='3564d458-9a8a-11ea-7681-314846475f02',
        price='299',
        full_price='299',
        refunded_quantity='0',
        quantity='1',
        title='Куриные кебабы «Спидини»',
        vat='20.00',
        cashback='10.0000',
    )

    cold_storage.mock_cold_storage(checked_out=checked_out)

    response = await taxi_grocery_cart.post(
        '/admin/v1/cart/retrieve/raw/bulk', json={'cart_ids': [CART_ID]},
    )
    assert response.status_code == 200

    expected_info = {
        'cart_id': CART_ID,
        'client_price': '299',
        'total_discount': '0',
    }
    if checked_out:
        expected_info['delivery'] = {
            'cost': DELIVERY_COST,
            'min_eta': MIN_ETA,
            'max_eta': MAX_ETA,
        }
        expected_info['has_surge'] = False

    response_json = response.json()
    assert 'cart_infos' in response_json
    assert len(response_json['cart_infos']) == 1
    assert response_json['cart_infos'][0] == expected_info


@pytest.mark.now(keys.TS_NOW)
async def test_retrieve_raw_after_checkout(
        taxi_grocery_cart,
        cart,
        grocery_p13n,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
        grocery_depots,
):
    item_ids = ['item_id_1', 'item_id_2']
    price = '123'
    quantity = '1'
    delivery_cost = '100'
    min_eta = 20
    max_eta = 10
    client_price = str(
        len(item_ids) * int(price) * int(quantity) + int(delivery_cost),
    )

    delivery = {
        'cost': delivery_cost,
        'next_threshold': '500',
        'next_cost': '0',
    }

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        offer_time=keys.TS_NOW,
        depot_id='0',
    )
    experiments.set_delivery_conditions(
        experiments3, min_eta, max_eta, delivery, surge=True,
    )

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        0,
        legacy_depot_id=keys.DEFAULT_LEGACY_DEPOT_ID,
        depot_id=keys.DEFAULT_WMS_DEPOT_ID,
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
    )
    await taxi_grocery_cart.invalidate_caches()

    overlord_catalog.add_product(
        product_id=item_ids[0], price=price, logistic_tags=['cold'],
    )
    overlord_catalog.add_product(
        product_id=item_ids[1], price=price, logistic_tags=['cold'],
    )

    await cart.modify(
        {
            item_ids[0]: {'q': quantity, 'p': price},
            item_ids[1]: {'q': quantity, 'p': price},
        },
    )

    grocery_p13n.set_cashback_info_response(
        payment_available=True, balance=1000,
    )
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/admin/v1/cart/retrieve/raw/bulk', json={'cart_ids': [cart.cart_id]},
    )

    assert response.status_code == 200

    response_json = response.json()
    assert 'cart_infos' in response_json
    assert len(response_json['cart_infos']) == 1

    cart_info = response_json['cart_infos'][0]
    assert cart_info['delivery']['cost'] == delivery_cost
    assert cart_info['delivery']['max_eta'] == max_eta
    assert cart_info['delivery']['min_eta'] == min_eta
    assert cart_info['total_discount'] == '0'
    assert cart_info['client_price'] == client_price
    assert cart_info['has_surge']


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
async def test_cold_storage_deleted_items(taxi_grocery_cart, cold_storage):
    cold_storage.add_item(
        currency='RUB',
        item_id='3564d458-9a8a-11ea-7681-314846475f02',
        price='299',
        full_price='299',
        refunded_quantity='0',
        quantity='1',
        title='Куриные кебабы «Спидини»',
        vat='20.00',
        cashback='10.0000',
    )
    cold_storage.add_item(
        currency='RUB',
        item_id='42d3bca8-7f0a-11ea-639c-75b2947ca357',
        price='299',
        full_price='299',
        refunded_quantity='0',
        quantity='1',
        title='Куриные кебабы «Спидини»',
        vat='20.00',
        cashback='10.0000',
        status='in_cart',
    )
    cold_storage.add_item(
        currency='RUB',
        item_id='714f1f23-200a-11ea-b802-ac1f6b8569b3',
        price='299',
        full_price='299',
        refunded_quantity='0',
        quantity='1',
        cashback='10.0000',
        status='deleted_before_checkout',
    )

    cold_storage.mock_cold_storage(checked_out=True)

    response = await taxi_grocery_cart.post(
        '/admin/v1/cart/retrieve/raw/bulk', json={'cart_ids': [CART_ID]},
    )
    assert response.status_code == 200

    response_json = response.json()
    assert 'cart_infos' in response_json
    assert len(response_json['cart_infos']) == 1

    cart_info = response_json['cart_infos'][0]

    assert cart_info['client_price'] == str(299 * 2)
    assert cart_info['total_discount'] == '0'
