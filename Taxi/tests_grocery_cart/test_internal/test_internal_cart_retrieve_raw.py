# pylint: disable=too-many-lines
import copy

from grocery_mocks import grocery_p13n as p13n  # pylint: disable=E0401
import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys

HANDLERS = pytest.mark.parametrize(
    'test_handler',
    ['/internal/v1/cart/retrieve/raw', '/admin/v1/cart/retrieve/raw'],
)

CART_ID = 'e6a59113-503c-4d3e-8c59-000000000020'
CART_VERSION = 1
DEPOT_ID = '91456'
USER_TYPE = 'taxi'
USER_ID = 'user_1'
ORDER_ID = 'order-id-1'
DELIVERY_TYPE = 'eats_dispatch'
PAYMENT_METHOD_TYPE = 'card'
PAYMENT_METHOD_ID = 'card-x1d968ab8793bf3a1178369ff'
PAYMENT_METHOD_META: dict = {
    'sbp': {},
    'card': {'verified': True, 'is_yandex_card': True},
}
PROMOCODE_DISCOUNT = '200.1'
PROMOCODE_PROPERTIES = {
    'source': 'taxi',
    'discount_type': 'fixed',
    'discount_value': '23.4',
    'series_purpose': 'support',
}
DELIVERY_COST = '0'
MIN_ETA = 10
MAX_ETA = 15
ORDER_CONDITIONS_WITH_ETA = {
    'delivery_cost': DELIVERY_COST,
    'min_eta': MIN_ETA,
    'max_eta': MAX_ETA,
}
PAYMENT_METHOD_DISCOUNT = False
CASHBACK_ON_CART_PERCENT = '10.0000'
TIPS_AMOUNT = '5'
TIPS_AMOUNT_TYPE = 'absolute'
TIPS_PAYMENT_FLOW = 'separate'
TIPS = {'amount': TIPS_AMOUNT, 'amount_type': TIPS_AMOUNT_TYPE}

COLD_CART_RESPONSE = {
    'item_id': CART_ID,
    'cart_id': CART_ID,
    'order_id': ORDER_ID,
    'cart_version': CART_VERSION,
    'user_type': USER_TYPE,
    'user_id': USER_ID,
    'delivery_type': DELIVERY_TYPE,
    'payment_method_type': PAYMENT_METHOD_TYPE,
    'payment_method_id': PAYMENT_METHOD_ID,
    'payment_method_meta': PAYMENT_METHOD_META,
    'tips_amount': TIPS_AMOUNT,
    'tips_amount_type': TIPS_AMOUNT_TYPE,
    'items': [],
}

COLD_CHECKOUT_DATA = {
    'item_id': CART_ID,
    'cart_id': CART_ID,
    'depot_id': DEPOT_ID,
    'cashback_on_cart_percent': CASHBACK_ON_CART_PERCENT,
    'payment_method_discount': PAYMENT_METHOD_DISCOUNT,
    'order_conditions_with_eta': ORDER_CONDITIONS_WITH_ETA,
    'items_pricing': {'items': []},
    'has_surge': False,
    'tips_payment_flow': TIPS_PAYMENT_FLOW,
}


def _round_price(value, currency='RUB'):
    if currency == 'RUB':
        value = int(round(float(value), 0))
    if currency == 'ILS':
        value = round(float(value), 1)
        # 12.0 -> 12
        if value % 1 < 0.1:
            value = int(value)
    return value


def _to_template(value, currency='RUB'):
    return f'{_round_price(value, currency)} $SIGN$$CURRENCY$'.replace(
        '.', ',',
    )


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

        def mock_cold_storage(
                self,
                promocode,
                idempotency_token,
                checked_out,
                carts_response=None,
                calculation_log=None,
        ):
            if carts_response is not None:
                self.carts_response = carts_response

            cart_id = self.carts_response.get('cart_id', CART_ID)
            self.carts_response['promocode'] = promocode
            self.carts_response['idempotency_token'] = idempotency_token
            self.carts_response['checked_out'] = checked_out

            if promocode is not None:
                self.checkout_data['promocode_discount'] = PROMOCODE_DISCOUNT
                self.checkout_data[
                    'promocode_properties'
                ] = PROMOCODE_PROPERTIES

            if calculation_log:
                self.checkout_data['calculation_log'] = calculation_log

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


@HANDLERS
async def test_not_found(
        taxi_grocery_cart, cart, overlord_catalog, test_handler,
):
    item_id = 'item_id_1'
    price = '123'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': '1', 'p': price}})

    response = await taxi_grocery_cart.post(
        test_handler,
        json={
            'cart_id': 'ffffffff-ffff-40ff-ffff-ffffffffffff',
            'source': 'SQL',
        },
    )
    assert response.status_code == 404


@HANDLERS
async def test_ok(taxi_grocery_cart, cart, overlord_catalog, test_handler):
    item_id = 'item_id_1'
    price = '123'
    quantity = '1'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.set_payment(
        payment_type=PAYMENT_METHOD_TYPE,
        payment_id=PAYMENT_METHOD_ID,
        payment_meta=PAYMENT_METHOD_META,
    )
    cart.update_db(
        timeslot_start='2020-03-13T09:50:00+00:00',
        timeslot_end='2020-03-13T17:50:00+00:00',
        timeslot_request_kind='wide_slot',
    )

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200

    expected_json = {
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'idempotency_token': common.UPDATE_IDEMPOTENCY_TOKEN,
        'checked_out': False,
        'delivery_type': 'eats_dispatch',
        'payment_method_type': PAYMENT_METHOD_TYPE,
        'payment_method_id': PAYMENT_METHOD_ID,
        'payment_method_meta': PAYMENT_METHOD_META,
        'exists_order_id': False,
        'user_id': '1234',
        'user_type': 'yandex_taxi',
        'items': [
            {
                'currency': 'RUB',
                'id': item_id,
                'product_key': {
                    'id': item_id.split(':')[0],
                    'shelf_type': 'store',
                },
                'price': price,
                'price_template': _to_template(price),
                'quantity': quantity,
                'title': item_id,
                'refunded_quantity': '0',
            },
        ],
        'total_discount_template': _to_template(0),
        'full_total_template': _to_template(price),
        'client_price_template': _to_template(price),
        'items_full_price_template': _to_template(price),
        'items_price_template': _to_template(price),
        'total_promocode_discount_template': _to_template(0),
        'total_item_discounts_template': _to_template(0),
        'service_fee_template': _to_template(0),
        'client_price': price,
        'total_discount': '0',
        'source': 'SQL',
    }
    if test_handler == '/internal/v1/cart/retrieve/raw':
        expected_json['depot_id'] = keys.DEFAULT_LEGACY_DEPOT_ID
        expected_json['timeslot'] = {
            'end': '2020-03-13T17:50:00+00:00',
            'start': '2020-03-13T09:50:00+00:00',
        }
        expected_json['request_kind'] = 'wide_slot'

    resp = response.json()
    resp.pop('updated', None)
    assert resp == expected_json


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@HANDLERS
@pytest.mark.parametrize(
    'promocode,idempotency_token,checked_out',
    [
        (None, None, False),
        ('SOME_CODE', '123', False),
        ('SOME_CODE', '123', True),
    ],
)
async def test_basic_cold_storage(
        taxi_grocery_cart,
        test_handler,
        cold_storage,
        promocode,
        idempotency_token,
        checked_out,
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
        is_expiring=False,
        supplier_tin='supplier-tin',
    )

    cold_storage.mock_cold_storage(
        promocode=promocode,
        idempotency_token=idempotency_token,
        checked_out=checked_out,
    )

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': CART_ID, 'source': 'YT'},
    )
    assert response.status_code == 200

    expected_json = {
        'cart_id': CART_ID,
        'cart_version': CART_VERSION,
        'checked_out': checked_out,
        'delivery_type': DELIVERY_TYPE,
        'payment_method_type': PAYMENT_METHOD_TYPE,
        'payment_method_id': PAYMENT_METHOD_ID,
        'payment_method_meta': PAYMENT_METHOD_META,
        'exists_order_id': False,
        'user_id': USER_ID,
        'user_type': USER_TYPE,
        'items': [
            {
                'currency': 'RUB',
                'id': '3564d458-9a8a-11ea-7681-314846475f02',
                'product_key': {
                    'shelf_type': 'store',
                    'id': '3564d458-9a8a-11ea-7681-314846475f02',
                },
                'price': '299',
                'full_price': '299',
                'refunded_quantity': '0',
                'price_template': _to_template(299),
                'quantity': '1',
                'title': 'Куриные кебабы «Спидини»',
                'vat': '20.00',
                'cashback_per_unit': '10',
                'is_expiring': False,
                'supplier_tin': 'supplier-tin',
            },
        ],
        'total_discount_template': _to_template(0),
        'full_total_template': _to_template(299),
        'client_price_template': _to_template(299),
        'items_full_price_template': _to_template(299),
        'items_price_template': _to_template(299),
        'total_promocode_discount_template': _to_template(0),
        'total_item_discounts_template': _to_template(0),
        'service_fee_template': _to_template(0),
        'tips': TIPS,
        'client_price': '299',
        'total_discount': '0',
        'source': 'YT',
    }

    if promocode is not None and test_handler == '/admin/v1/cart/retrieve/raw':
        expected_json['promocode'] = 'SOME_CODE'
    if checked_out:
        expected_json['items_v2'] = [
            {
                'info': {
                    'item_id': '3564d458-9a8a-11ea-7681-314846475f02',
                    'title': 'Куриные кебабы «Спидини»',
                    'refunded_quantity': '0',
                    'shelf_type': 'store',
                    'vat': '20',
                    'supplier_tin': 'supplier-tin',
                },
                'sub_items': [
                    {
                        'item_id': '3564d458-9a8a-11ea-7681-314846475f02_0',
                        'full_price': '299',
                        'price': '299',
                        'quantity': '1',
                    },
                ],
            },
        ]
        if test_handler == '/internal/v1/cart/retrieve/raw':
            expected_json['items_v2_source'] = 'stored'
        expected_json['delivery'] = {
            'cost': DELIVERY_COST,
            'min_eta': MIN_ETA,
            'max_eta': MAX_ETA,
        }
        expected_json['has_surge'] = False
        expected_json['payment_method_discount'] = PAYMENT_METHOD_DISCOUNT
        if promocode is not None:
            expected_json['promocode_discount'] = PROMOCODE_DISCOUNT
            expected_json['promocode_properties'] = PROMOCODE_PROPERTIES
        expected_json['tips']['payment_flow'] = TIPS_PAYMENT_FLOW

    if promocode is not None and not test_handler.startswith('/admin'):
        expected_json['promocode'] = promocode
    if idempotency_token is not None:
        expected_json['idempotency_token'] = idempotency_token

    assert response.json() == expected_json


@HANDLERS
@pytest.mark.parametrize(
    'delivery_zone_type, pipeline_name, is_expiring',
    [
        ('pedestrian', 'calc_surge_grocery_v1', True),
        ('yandex_taxi', 'calc_surge_grocery_taxi_v0', True),
        ('yandex_taxi_remote', 'calc_surge_grocery_taxi_v0_remote', False),
        ('yandex_taxi_night', 'calc_surge_grocery_taxi_v0_night', False),
    ],
)
@pytest.mark.now(keys.TS_NOW)
async def test_retrieve_raw_after_checkout(
        taxi_grocery_cart,
        cart,
        grocery_p13n,
        overlord_catalog,
        test_handler,
        delivery_zone_type,
        pipeline_name,
        offers,
        experiments3,
        grocery_surge,
        grocery_depots,
        is_expiring,
):
    item_id = 'item_id_1'
    full_price = '124'
    price = '123'
    discount = str(int(full_price) - int(price))
    quantity = '1'
    delivery_cost = '100'
    min_eta = 20
    max_eta = 10
    supplier_tin = 'supplier-tin'

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
        name=pipeline_name,
        delivery_type=delivery_zone_type,
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
        delivery_type=delivery_zone_type,
    )
    await taxi_grocery_cart.invalidate_caches()

    overlord_catalog.add_product(
        product_id=item_id,
        price=full_price,
        logistic_tags=['cold'],
        supplier_tin=supplier_tin,
    )

    grocery_p13n.add_modifier(
        product_id=item_id, value=discount, meta={'is_expiring': is_expiring},
    )

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    grocery_p13n.set_cashback_info_response(
        payment_available=True, balance=1000,
    )

    await cart.checkout()

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200
    json = response.json()
    assert len(json['items']) == 1
    assert json['items'][0]['vat'] == '20.00'
    assert json['items'][0]['is_expiring'] == is_expiring
    assert json['items'][0]['supplier_tin'] == supplier_tin
    assert json['delivery']['cost'] == delivery_cost
    assert json['delivery']['max_eta'] == max_eta
    assert json['delivery']['min_eta'] == min_eta
    assert json['total_discount_template'] == '{} $SIGN$$CURRENCY$'.format(
        discount,
    )
    assert json['total_discount'] == discount
    assert json['delivery_zone_type'] == delivery_zone_type
    assert json['personal_wallet_id'] == p13n.WALLET_ID
    assert json['logistic_tags'] == ['cold']
    assert json['has_surge']


def _check_templates(response):
    full_total = 0
    client_price = 0
    total_discount = 0
    items_full_price = 0
    items_price = 0

    for item in response['items']:
        items_price += float(item['price'])
        if 'full_price' in item:
            items_full_price += float(item['full_price']) * float(
                item['quantity'],
            )
        else:
            items_full_price += float(item['price']) * float(item['quantity'])

    full_total = items_full_price
    client_price = items_price
    if 'delivery' in response and 'cost' in response['delivery']:
        full_total += float(response['delivery']['cost'])
        client_price += float(response['delivery']['cost'])
    if 'total_promocode_discount_template' in response:
        promocode_discount = float(
            response['total_promocode_discount_template'].split(' ')[0],
        )
        client_price -= promocode_discount

    total_discount = full_total - client_price

    assert response['full_total_template'] == _to_template(full_total)
    assert response['client_price_template'] == _to_template(client_price)
    assert response['total_discount_template'] == _to_template(total_discount)
    assert response['items_price_template'] == _to_template(items_price)
    assert response['items_full_price_template'] == _to_template(
        items_full_price,
    )


@HANDLERS
async def test_retrieve_raw_after_refund(
        taxi_grocery_cart, cart, overlord_catalog, test_handler,
):
    item_id = 'item_id_1'
    price = '123'
    quantity = '1'

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify({item_id: {'q': quantity, 'p': price}})

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/refund',
        json={
            'cart_id': cart.cart_id,
            'item_refunds': [{'item_id': item_id, 'refunded_quantity': '1'}],
        },
    )

    assert response.status_code == 200

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200

    assert response.json()['items'][0]['refunded_quantity'] == '1'


@pytest.mark.pgsql('grocery_cart', files=['sql_carts_checkout_data.sql'])
@pytest.mark.parametrize(
    'source,response_size', [(None, 3), ('All', 9), ('SQL', 3)],
)
@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
async def test_carts_retrieve_raw_list(
        taxi_grocery_cart,
        overlord_catalog,
        source,
        response_size,
        cold_storage,
):
    """
    e6a59113-503c-4d3e-8c59-000000000011 - полностью в SQL, есть промокод
    e6a59113-503c-4d3e-8c59-000000000022 - полностью в YT
    e6a59113-503c-4d3e-8c59-000000000021 - cart в YT checkout в SQL, есть п-код
    e6a59113-503c-4d3e-8c59-000000000012 - cart в SQL checkout в YT, есть п-код
    e6a59113-503c-4d3e-8c59-000000000010 - cart в SQL checkout нет
    e6a59113-503c-4d3e-8c59-000000000020 - cart в YT checkout нет
    e6a59113-503c-4d3e-8c59-000000000001 - cart нет checkout в SQL
    e6a59113-503c-4d3e-8c59-000000000002 - cart нет checkout в YT
    e6a59113-503c-4d3e-8c59-000000000099 - не существующая корзина
    """

    depot_id = '71249'
    order_id = 'some_order'

    overlord_catalog.add_depot(legacy_depot_id=depot_id)

    response_cnt = 0
    for cart_id in ['01', '02', '10', '11', '12', '20', '21', '22', '99']:
        full_cart_id = 'e6a59113-503c-4d3e-8c59-0000000000' + cart_id
        request = {'cart_id': full_cart_id}

        cart = (
            {
                'order_id': order_id,
                'cart_id': full_cart_id,
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
                        'item_id': 'item_id',
                        'price': '10',
                        'quantity': '2',
                        'title': 'title',
                        'vat': '20.00',
                        'cashback': '1',
                        'currency': 'RUB',
                    },
                ],
            }
            if source == 'All'
            else None
        )

        cold_storage.mock_cold_storage(
            promocode=None,
            idempotency_token='123',
            checked_out=True,
            carts_response=cart,
        )
        if source is not None:
            request['source'] = source
        response = await taxi_grocery_cart.post(
            '/internal/v1/cart/retrieve/raw', json=request,
        )
        response_cnt += response.status_code == 200

    assert response_cnt == response_size


@common.GROCERY_ORDER_CYCLE_ENABLED
@HANDLERS
async def test_product_keys(
        taxi_grocery_cart, cart, test_handler, tristero_parcels,
):
    parcel_id = 'item_id_2:st-pa'
    items = ['item_id_1', parcel_id]
    tristero_parcels.add_parcel(parcel_id=parcel_id)
    for item_id in items:
        await cart.modify({item_id: {'q': '1', 'p': '1'}})

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200
    items_response = response.json()['items']
    for item in items_response:
        assert item['id'] in items
        if item['id'] == 'item_id_1':
            assert item['product_key']['shelf_type'] == 'store'
        if item['id'] == 'item_id_2:st-pa':
            assert item['product_key']['shelf_type'] == 'parcel'
            assert 'gross_weight' not in item


# Cover with experiment
@common.GROCERY_ORDER_CYCLE_ENABLED
@HANDLERS
@experiments.ENABLED_PARCEL_SIZES_EXP
async def test_tristero_weight_params(
        taxi_grocery_cart, cart, test_handler, tristero_parcels,
):
    parcel_id = 'item_id_2:st-pa'
    items = ['item_id_1', parcel_id]
    tristero_parcels.add_parcel(parcel_id=parcel_id)
    for item_id in items:
        await cart.modify({item_id: {'q': '1', 'p': '1'}})

    headers = {}
    if 'admin' not in test_handler:
        headers['X-YaTaxi-Session'] = 'taxi:some_sess'

    response = await taxi_grocery_cart.post(
        test_handler,
        json={'cart_id': cart.cart_id, 'source': 'SQL'},
        headers=headers,
    )

    assert response.status_code == 200

    items_response = response.json()['items']
    for item in items_response:
        assert item['id'] in items
        if item['id'] == 'item_id_1':
            assert item['product_key']['shelf_type'] == 'store'
        if item['id'] == 'item_id_2:st-pa':
            assert item['product_key']['shelf_type'] == 'parcel'
            assert item['gross_weight'] == 8


@HANDLERS
@pytest.mark.parametrize(
    'measurements',
    [
        None,
        {
            'width': 1,
            'height': 2,
            'depth': 3,
            'gross_weight': 4,
            'net_weight': 5,
        },
    ],
)
async def test_measurements(
        taxi_grocery_cart, cart, test_handler, overlord_catalog, measurements,
):
    """ Check retrieve/raw returns item measurements, if exists """

    item_id = 'item_id_1'
    overlord_catalog.add_product(
        product_id=item_id, price=1, measurements=measurements,
    )
    await cart.modify({item_id: {'q': '1', 'p': '1'}})

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200
    response_json = response.json()
    for item in response_json['items']:
        assert item['id'] == item_id
        if measurements is not None:
            for key in ['width', 'height', 'depth', 'gross_weight']:
                assert item[key] == measurements[key]


@HANDLERS
@pytest.mark.parametrize('cashback', ['10', None])
async def test_response_with_cashback(
        taxi_grocery_cart, cart, overlord_catalog, test_handler, cashback,
):
    item_id = 'item_id_1'
    price = '1000'
    quantity = '1'

    if cashback is not None:
        cashback_field = {'cashback_per_unit': cashback}
    else:
        cashback_field = {}

    overlord_catalog.add_product(product_id=item_id, price=price)

    await cart.modify(
        products={item_id: {'q': quantity, 'p': price, 'c': cashback}},
    )

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200

    expected_json = {
        'cart_id': cart.cart_id,
        'cart_version': cart.cart_version,
        'idempotency_token': common.UPDATE_IDEMPOTENCY_TOKEN,
        'checked_out': False,
        'delivery_type': 'eats_dispatch',
        'exists_order_id': False,
        'user_id': '1234',
        'user_type': 'yandex_taxi',
        'items': [
            {
                'currency': 'RUB',
                'id': item_id,
                'product_key': {
                    'id': item_id.split(':')[0],
                    'shelf_type': 'store',
                },
                'price': price,
                'price_template': _to_template(price),
                'quantity': quantity,
                'title': item_id,
                'refunded_quantity': '0',
                **cashback_field,
            },
        ],
        'total_discount_template': _to_template(0),
        'full_total_template': _to_template(price),
        'client_price_template': _to_template(price),
        'items_full_price_template': _to_template(price),
        'items_price_template': _to_template(price),
        'total_promocode_discount_template': _to_template(0),
        'total_item_discounts_template': _to_template(0),
        'service_fee_template': _to_template(0),
        'client_price': price,
        'total_discount': '0',
        'source': 'SQL',
    }
    if test_handler == '/internal/v1/cart/retrieve/raw':
        expected_json['depot_id'] = keys.DEFAULT_LEGACY_DEPOT_ID

    resp = response.json()
    resp.pop('updated', None)
    assert resp == expected_json


@pytest.mark.parametrize(
    'tips_param',
    [
        {'amount': '15', 'amount_type': 'absolute'},
        {'amount': '10', 'amount_type': 'percent'},
    ],
)
async def test_internal_response_with_tips(
        taxi_grocery_cart, tips_param, cart, overlord_catalog,
):
    item_id = 'item_id_1'

    overlord_catalog.add_product(product_id=item_id, price='1')
    await cart.modify(products={item_id: {'q': '1', 'p': '1'}})
    await cart.set_tips(tips_param)
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/internal/v1/cart/retrieve/raw',
        json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200
    assert response.json()['tips'] == {
        **tips_param,
        'payment_flow': 'separate',
    }


@HANDLERS
async def test_by_order_id_sql(
        taxi_grocery_cart, cart, overlord_catalog, test_handler,
):
    item_id = 'item_id_1'
    order_id = 'order_id:123'

    overlord_catalog.add_product(product_id=item_id, price='1')
    await cart.modify(products={item_id: {'q': '1', 'p': '1'}})
    await cart.checkout()
    await cart.set_order_id(order_id)

    response = await taxi_grocery_cart.post(
        test_handler, json={'order_id': order_id, 'source': 'SQL'},
    )

    assert response.status_code == 200
    assert response.json()['cart_id'] == cart.cart_id


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@HANDLERS
async def test_by_order_id_cold_storage(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        test_handler,
        grocery_cold_storage,
):
    order_id = 'order_id:123'
    item_id = 'item_id_1'

    overlord_catalog.add_product(product_id=item_id, price='1')
    await cart.modify(products={item_id: {'q': '1', 'p': '1'}})
    await cart.checkout()
    await cart.set_order_id(order_id)

    grocery_cold_storage.set_carts_by_order_id_response(
        items=[
            {
                'item_id': order_id,
                'cart_id': cart.cart_id,
                'cart_version': 3,
                'user_type': 'eats_user_id',
                'user_id': '145597824',
                'order_id': order_id,
                'checked_out': True,
                'delivery_type': 'eats_dispatch',
                'items': [],
            },
        ],
    )
    grocery_cold_storage.check_carts_by_order_id_request(
        item_ids=[order_id], fields=None,
    )

    response = await taxi_grocery_cart.post(
        test_handler, json={'order_id': order_id, 'source': 'YT'},
    )
    assert response.status_code == 200
    assert response.json()['cart_id'] == cart.cart_id


def _check_item_in_response(response, item_id, shold_exists):
    items_v2 = response['items_v2']

    for item_v2 in items_v2:
        if item_v2['info']['item_id'] == item_id:
            if shold_exists:
                return
            assert False

    assert not shold_exists


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
@HANDLERS
async def test_cold_storage_deleted_items(
        taxi_grocery_cart, test_handler, cold_storage,
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

    cold_storage.mock_cold_storage(
        promocode=None, idempotency_token='123', checked_out=True,
    )

    response = await taxi_grocery_cart.post(
        test_handler, json={'cart_id': CART_ID, 'source': 'YT'},
    )
    assert response.status_code == 200

    _check_item_in_response(
        response.json(), '3564d458-9a8a-11ea-7681-314846475f02', True,
    )
    _check_item_in_response(
        response.json(), '42d3bca8-7f0a-11ea-639c-75b2947ca357', True,
    )
    _check_item_in_response(
        response.json(), '714f1f23-200a-11ea-b802-ac1f6b8569b3', False,
    )


async def test_calculation_log_in_admin_handler(
        taxi_grocery_cart, cart, grocery_p13n, overlord_catalog,
):
    item_id = 'item_id_1'
    full_price = '124'
    price = '100'
    discount = str(int(full_price) - int(price))
    quantity = '1'
    overlord_catalog.add_product(product_id=item_id, price=full_price)
    grocery_p13n.add_modifier(product_id=item_id, value=discount)

    await cart.modify({item_id: {'q': quantity, 'p': price}})
    await cart.checkout()

    response = await taxi_grocery_cart.post(
        '/admin/v1/cart/retrieve/raw',
        json={'cart_id': cart.cart_id, 'source': 'SQL'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['calculation_log'] == {
        'total': '100',
        'coupon': {'value': '0'},
        'currency': 'RUB',
        'calculation': {
            'products_calculation': [
                {
                    'steps': [
                        {'bag': [{'price': '124', 'quantity': '1'}]},
                        {
                            'bag': [{'price': '100', 'quantity': '1'}],
                            'discount': {
                                'payment_type': 'money_payment',
                                'discount_type': 'menu_discount',
                            },
                            'total_discount': '24',
                        },
                    ],
                    'product_id': 'item_id_1',
                },
            ],
        },
        'service_fees': {'delivery_cost': '0'},
    }


@pytest.mark.config(GROCERY_CART_RESTORE_FROM_COLD_STORAGE=True)
async def test_calculation_log_cold_storage_in_admin_handler(
        taxi_grocery_cart, cold_storage,
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
        is_expiring=False,
    )
    calculation_log = {'test-key': 'test-value'}
    cold_storage.mock_cold_storage(
        promocode='None',
        idempotency_token='123',
        checked_out=True,
        calculation_log=calculation_log,
    )

    response = await taxi_grocery_cart.post(
        '/admin/v1/cart/retrieve/raw',
        json={'cart_id': CART_ID, 'source': 'YT'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['calculation_log'] == calculation_log
