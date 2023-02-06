import copy
import datetime
import json

import pytest

from tests_grocery_uber_gw import models

REQUEST_DATA = {
    'event_type': 'orders.notification',
    'event_id': 'c4d2261e-2779-4eb6-beb0-cb41235c751e',
    'event_time': 1427343990,
    'meta': {
        'resource_id': '153dd7f1-339d-4619-940c-418943c14636',
        'status': 'pos',
        'user_id': '89dd9741-66b5-4bb4-b216-a813f3b21b4f',
    },
    'resource_href': (
        'https://api.uber.com/v2/eats/order/'
        '153dd7f1-339d-4619-940c-418943c14636'
    ),
}


def _merge_items(items):
    unique_items = dict()
    for item in copy.deepcopy(items):
        if item['id'] in unique_items:
            unique_items[item['id']]['quantity'] += item['quantity']
        else:
            unique_items[item['id']] = item
    return list(unique_items.values())


def _deny_reason_constructor(
        message, code, out_of_stock=None, invalid_items=None,
):
    reason = {'message': message, 'code': code}
    if out_of_stock:
        reason['out_of_stock'] = [out_of_stock]
    if invalid_items:
        reason['invalid_items'] = [invalid_items]

    return reason


@pytest.mark.config(
    GROCERY_UBER_GW_DEPOTS_MAPPING_SETTINGS={'enabled': True, 'limit': 50},
)
@pytest.mark.parametrize(
    'status', ['ok', 'uber_error', 'cart_create_error', 'orders_submit_error'],
)
async def test_order_create_flow(
        taxi_grocery_uber_gw,
        grocery_uber_gw_db,
        mock_uber_api,
        mockserver,
        grocery_depots,
        status,
):
    """ Checking the order create flow """

    # TODO: Add test for location deduction when tests for gmaps are settled
    #  with yamaps maintainers
    order_id = '73ef6892-11c0-4bb4-b216-f827a3c21f8b'
    cart_id = '24ad1e47-0cec-42b7-a2f0-df8d763f4e89'
    offer_id = '01234567-741d-410e-9f04-476f46ad43c7'
    eater_phone = '+44 1388 436844'
    eater_phone_code = '555 55 555'
    personal_phone_id = 'some_personal_phone_id'
    request_application = 'app_name=uber_eats_backend'
    grocery_depots.add_depot(
        depot_test_id=1,
        depot_id='grocery_depot_id',
        legacy_depot_id='grocery_depot_id',
    )
    items = [
        {
            'id': 'item_1',
            'quantity': 1,
            'price': {'unit_price': {'amount': 80, 'currency_code': 'GBP'}},
        },
        {
            'id': 'item_2',
            'quantity': 3,
            'price': {'unit_price': {'amount': 150, 'currency_code': 'GBP'}},
        },
        {
            'id': 'item_1',  # the same item id as the first item
            'quantity': 4,
            'price': {'unit_price': {'amount': 80, 'currency_code': 'GBP'}},
        },
        {
            'id': 'item_2',  # the same item id as the second item
            'quantity': 4,
            'price': {'unit_price': {'amount': 80, 'currency_code': 'GBP'}},
        },
    ]
    request_data = copy.deepcopy(REQUEST_DATA)

    store = models.Store(
        store_id='uber_store_id', merchant_store_id='grocery_depot_id',
    )
    mock_uber_api_payload = {'stores': {store.store_id: store}, 'orders': {}}

    if status != 'uber_error':
        order = models.Order(
            order_id=order_id,
            store_id='uber_store_id',
            items=items,
            eater_phone=eater_phone,
            eater_phone_code=eater_phone_code,
        )
        mock_uber_api_payload['orders'] = {order.order_id: order}
        request_data['meta']['resource_id'] = order.order_id

    mock_uber_api.set_payload(mock_uber_api_payload)

    @mockserver.json_handler('personal/v1/phones/store')
    def _phones_store(request):
        assert request.json['value'] == eater_phone.replace(' ', '')
        return {'value': request.json['value'], 'id': personal_phone_id}

    @mockserver.json_handler('grocery-cart/internal/v1/cart/create')
    def _cart_create(request):
        if status == 'cart_create_error':
            return mockserver.make_response(status=500)

        unique_items = _merge_items(items)
        for i, _ in enumerate(unique_items):
            assert (
                unique_items[i]['id'] == request.json['items'][i]['product_id']
                and str(unique_items[i]['quantity'])
                == request.json['items'][i]['quantity']
            )
        assert request.json['personal_phone_id'] == personal_phone_id
        assert request.json['locale'] == 'en'
        assert request.headers['X-Request-Application'] == request_application
        return {'cart_id': cart_id, 'cart_version': 1, 'offer_id': offer_id}

    @mockserver.json_handler(
        'grocery-orders/orders/v1/integration-api/v1/submit',
    )
    def _orders_submit(request):
        if status == 'orders_submit_error':
            return mockserver.make_response(status=500)

        assert request.headers['X-YaTaxi-Session'] == 'uber_eats:some_eater_id'
        assert request.headers[
            'X-YaTaxi-User'
        ] == 'personal_phone_id={}'.format(personal_phone_id)
        assert request.headers['X-Request-Application'] == request_application
        assert request.json['cart_id'] == cart_id
        assert request.json['cart_version'] == 1
        assert request.json['offer_id'] == offer_id
        assert 'location' in request.json['position']
        assert (
            request.json['position']['place_id']
            == 'gmaps://place_id=some_place_id'
        )
        assert request.json['additional_phone_code'] == eater_phone_code

        return {'order_id': order_id}

    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/create',
        data=json.dumps(request_data),
        headers={'content-type': 'application/json'},
    )

    query = 'SELECT * FROM grocery_uber_gw.orders_correspondence'
    if status == 'ok':
        assert response.status_code == 200
        assert mock_uber_api.order_accept_times_called == 1
        records = grocery_uber_gw_db.fetch_from_sql(query)
        assert records[0][0] == order_id and records[0][0] == records[0][1]
        assert records[0][2] > datetime.datetime.now(
            records[0][2].tzinfo,
        ) - datetime.timedelta(milliseconds=100)
    else:
        assert response.status_code == 500
        assert mock_uber_api.order_accept_times_called == 0
        assert not grocery_uber_gw_db.fetch_from_sql(query)


@pytest.mark.parametrize(
    'state', ['ACCEPTED', 'DENIED', 'FINISHED', 'CANCELED'],
)
async def test_terminate_pipeline_by_order_state(
        taxi_grocery_uber_gw, mock_uber_api, grocery_depots, state,
):
    order_id = '73ef6892-11c0-4bb4-b216-f827a3c21f8b'
    eater_phone = '+44 1388 436844'
    eater_phone_code = '555 55 555'

    grocery_depots.add_depot(
        depot_test_id=1,
        depot_id='grocery_depot_id',
        legacy_depot_id='grocery_depot_id',
    )

    store = models.Store(
        store_id='uber_store_id', merchant_store_id='grocery_depot_id',
    )
    order = models.Order(
        order_id=order_id,
        store_id='uber_store_id',
        eater_phone=eater_phone,
        eater_phone_code=eater_phone_code,
        current_state=state,
    )
    mock_uber_api_payload = {
        'stores': {store.store_id: store},
        'orders': {order.order_id: order},
    }
    mock_uber_api.set_payload(mock_uber_api_payload)

    request = copy.deepcopy(REQUEST_DATA)
    request['meta']['resource_id'] = order_id

    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/create',
        data=json.dumps(request),
        headers={'content-type': 'application/json'},
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'cart_error_code, uber_code',
    [
        ['MISSING_PHONE_ID', 'MISSING_INFO'],
        ['INVALID_ITEMS', 'MISSING_INFO'],
        ['UNKNOWN_PRODUCT', 'OTHER'],
        ['PRODUCT_NOT_AVAILABLE_FOR_DELIVERY', 'ITEM_AVAILABILITY'],
    ],
)
async def test_creation_error_create_cart(
        taxi_grocery_uber_gw,
        mock_uber_api,
        grocery_depots,
        mockserver,
        cart_error_code,
        uber_code,
):
    order_id = '73ef6892-11c0-4bb4-b216-f827a3c21f8b'
    eater_phone = '+44 1388 436844'
    eater_phone_code = '555 55 555'
    personal_phone_id = 'some_personal_phone_id'
    grocery_depots.add_depot(
        depot_test_id=1,
        depot_id='grocery_depot_id',
        legacy_depot_id='grocery_depot_id',
    )
    items = [
        {
            'id': 'item_1',
            'quantity': 1,
            'price': {'unit_price': {'amount': 80, 'currency_code': 'GBP'}},
        },
    ]
    request_data = copy.deepcopy(REQUEST_DATA)

    store = models.Store(
        store_id='uber_store_id', merchant_store_id='grocery_depot_id',
    )
    mock_uber_api_payload = {'stores': {store.store_id: store}, 'orders': {}}

    order = models.Order(
        order_id=order_id,
        store_id='uber_store_id',
        items=items,
        eater_phone=eater_phone,
        eater_phone_code=eater_phone_code,
    )
    mock_uber_api_payload['orders'] = {order.order_id: order}
    request_data['meta']['resource_id'] = order.order_id

    mock_uber_api.set_payload(mock_uber_api_payload)

    @mockserver.json_handler('personal/v1/phones/store')
    def _phones_store(request):
        return {'value': request.json['value'], 'id': personal_phone_id}

    has_invalid_items = cart_error_code in [
        'UNKNOWN_PRODUCT',
        'PRODUCT_NOT_AVAILABLE_FOR_DELIVERY',
    ]

    message = 'some message' + (':item_1' if has_invalid_items else '')

    @mockserver.json_handler('grocery-cart/internal/v1/cart/create')
    def _cart_create(request):
        return mockserver.make_response(
            status=400, json={'code': cart_error_code, 'message': message},
        )

    expected_reason = _deny_reason_constructor(
        '', uber_code, invalid_items=('item_1' if has_invalid_items else None),
    )

    mock_uber_api.set_deny_reason(expected_reason)

    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/create',
        data=json.dumps(request_data),
        headers={'content-type': 'application/json'},
    )
    assert mock_uber_api.deny_order_times_called == 1
    assert response.status_code == 200


@pytest.mark.parametrize(
    'submit_error_code, uber_code',
    [
        ['outdated_cart', 'OTHER'],
        ['bad_address', 'ADDRESS'],
        ['empty_cart', 'MISSING_INFO'],
        ['drop_and_try_again', 'OTHER'],
        ['grocery_order_id_exists', 'OTHER'],
        ['orders_limit_exceeded', 'OTHER'],
        ['try_again_later', 'OTHER'],
        ['need_local_phone_number', 'MISSING_INFO'],
        ['no_personal_phone_id', None],
        ['bad_payment_method', None],
        ['grocery_invalid_promocode', None],
        # ['grocery_unavailable_for_checkout', None],   needs a separate test
        ['no_such_eater', None],
        ['no_personal_email_id', None],
        ['invalid_payment_method', None],
    ],
)
async def test_creation_error_submit(
        taxi_grocery_uber_gw,
        mock_uber_api,
        grocery_depots,
        mockserver,
        submit_error_code,
        uber_code,
):
    order_id = '73ef6892-11c0-4bb4-b216-f827a3c21f8b'
    cart_id = '24ad1e47-0cec-42b7-a2f0-df8d763f4e89'
    offer_id = '01234567-741d-410e-9f04-476f46ad43c7'
    eater_phone = '+44 1388 436844'
    eater_phone_code = '555 55 555'
    personal_phone_id = 'some_personal_phone_id'
    grocery_depots.add_depot(
        depot_test_id=1,
        depot_id='grocery_depot_id',
        legacy_depot_id='grocery_depot_id',
    )
    items = [
        {
            'id': 'item_1',
            'quantity': 1,
            'price': {'unit_price': {'amount': 80, 'currency_code': 'GBP'}},
        },
    ]
    request_data = copy.deepcopy(REQUEST_DATA)

    store = models.Store(
        store_id='uber_store_id', merchant_store_id='grocery_depot_id',
    )
    mock_uber_api_payload = {'stores': {store.store_id: store}, 'orders': {}}

    order = models.Order(
        order_id=order_id,
        store_id='uber_store_id',
        items=items,
        eater_phone=eater_phone,
        eater_phone_code=eater_phone_code,
    )
    mock_uber_api_payload['orders'] = {order.order_id: order}
    request_data['meta']['resource_id'] = order.order_id

    mock_uber_api.set_payload(mock_uber_api_payload)

    @mockserver.json_handler('personal/v1/phones/store')
    def _phones_store(request):
        return {'value': request.json['value'], 'id': personal_phone_id}

    @mockserver.json_handler('grocery-cart/internal/v1/cart/create')
    def _cart_create(request):
        return {'cart_id': cart_id, 'cart_version': 1, 'offer_id': offer_id}

    @mockserver.json_handler(
        'grocery-orders/orders/v1/integration-api/v1/submit',
    )
    def _orders_submit(request):
        return mockserver.make_response(
            status=400,
            json={'code': submit_error_code, 'message': 'some message'},
        )

    if uber_code:
        expected_reason = _deny_reason_constructor('', uber_code)
        mock_uber_api.set_deny_reason(expected_reason)

    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/create',
        data=json.dumps(request_data),
        headers={'content-type': 'application/json'},
    )
    assert mock_uber_api.deny_order_times_called == (1 if uber_code else 0)
    assert response.status_code == (200 if uber_code else 500)


@pytest.mark.parametrize(
    'checkout_error_code, uber_code',
    [
        ['checkedout', None],  # nothing to be done
        ['checkedout-other-token', 'OTHER'],
        ['offer-invalid', 'OTHER'],
        ['cashback-flow-not-allowed', 'OTHER'],
        ['cashback-low-balance', 'OTHER'],
        ['cashback-mismatch', 'OTHER'],
        ['delivery-cost', 'OTHER'],
        ['delivery-type-not-allowed', 'OTHER'],
        ['price-mismatch', 'PRICING'],
        ['minimum-price', 'PRICING'],
        ['quantity-over-limit', 'ITEM_AVAILABILITY'],
        ['depot-is-closed-now', 'STORE_CLOSED'],
        ['cannot_find_depot', 'OTHER'],
        ['cart_empty', 'MISSING_INFO'],
        ['parcel-wrong-depot', None],
        ['promocode-not-applied', None],
        ['no-payment-method', None],
        ['parcel-already-ordered', None],
        ['tips-not-allowed', None],
    ],
)
async def test_creation_error_checkout(
        taxi_grocery_uber_gw,
        mock_uber_api,
        grocery_depots,
        mockserver,
        checkout_error_code,
        uber_code,
):
    order_id = '73ef6892-11c0-4bb4-b216-f827a3c21f8b'
    cart_id = '24ad1e47-0cec-42b7-a2f0-df8d763f4e89'
    offer_id = '01234567-741d-410e-9f04-476f46ad43c7'
    eater_phone = '+44 1388 436844'
    eater_phone_code = '555 55 555'
    personal_phone_id = 'some_personal_phone_id'
    grocery_depots.add_depot(
        depot_test_id=1,
        depot_id='grocery_depot_id',
        legacy_depot_id='grocery_depot_id',
    )
    items = [
        {
            'id': 'item_1',
            'quantity': 1,
            'price': {'unit_price': {'amount': 80, 'currency_code': 'GBP'}},
        },
    ]
    request_data = copy.deepcopy(REQUEST_DATA)

    store = models.Store(
        store_id='uber_store_id', merchant_store_id='grocery_depot_id',
    )
    mock_uber_api_payload = {'stores': {store.store_id: store}, 'orders': {}}

    order = models.Order(
        order_id=order_id,
        store_id='uber_store_id',
        items=items,
        eater_phone=eater_phone,
        eater_phone_code=eater_phone_code,
    )
    mock_uber_api_payload['orders'] = {order.order_id: order}
    request_data['meta']['resource_id'] = order.order_id

    mock_uber_api.set_payload(mock_uber_api_payload)

    @mockserver.json_handler('personal/v1/phones/store')
    def _phones_store(request):
        return {'value': request.json['value'], 'id': personal_phone_id}

    @mockserver.json_handler('grocery-cart/internal/v1/cart/create')
    def _cart_create(request):
        return {'cart_id': cart_id, 'cart_version': 1, 'offer_id': offer_id}

    @mockserver.json_handler(
        'grocery-orders/orders/v1/integration-api/v1/submit',
    )
    def _orders_submit(request):
        return mockserver.make_response(
            status=400,
            json={
                'code': 'grocery_unavailable_for_checkout',
                'message': 'some message',
                'details': {
                    'cart': {
                        'checkout_unavailable_reason': checkout_error_code,
                    },
                },
            },
        )

    if uber_code:
        expected_reason = _deny_reason_constructor('', uber_code)
        mock_uber_api.set_deny_reason(expected_reason)

    response = await taxi_grocery_uber_gw.post(
        'processing/v1/uber-gw/v1/order/create',
        data=json.dumps(request_data),
        headers={'content-type': 'application/json'},
    )
    if checkout_error_code == 'checkedout':
        assert response.status_code == 200
        assert mock_uber_api.deny_order_times_called == 0
    else:
        assert mock_uber_api.deny_order_times_called == (1 if uber_code else 0)
        assert response.status_code == (200 if uber_code else 500)
