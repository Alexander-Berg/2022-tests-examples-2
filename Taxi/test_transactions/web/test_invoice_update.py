# pylint: disable=redefined-outer-name,invalid-name
import copy

import pytest

from test_transactions import helpers


_ALLOW_PRODUCT_ID_CHANGE = pytest.mark.config(
    TRANSACTIONS_ALLOW_PRODUCT_ID_CHANGE={'__default__': True},
)


async def test_invoice_update_not_found(web_app_client):
    response = await web_app_client.post(
        '/invoice/update',
        json={
            'id': 'no-such-order',
            'operation_id': 'operation-1234',
            'originator': 'processing',
            'payment': {
                'type': 'card',
                'method': '1324',
                'billing_id': 'card-1324',
            },
            'yandex_uid': '123',
            'items': [
                {
                    'item_id': 'ride',
                    'product_id': 'taxi_park_ride',
                    'amount': '123',
                },
            ],
        },
    )
    assert response.status == 404
    content = await response.json()
    assert content == {}


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_ARCHIVE_ENABLED={'__default__': 1},
                ),
            ],
            id='it should return 404 when invoice was not found anywhere',
        ),
        pytest.param(id='it should return 404 when archive is disabled'),
    ],
)
async def test_v2_invoice_update_not_found(patch, web_app_client):
    helpers.patch_fetch_invoice(
        patch, result=None, expected_invoice_id='no-such-order',
    )
    response = await web_app_client.post(
        '/v2/invoice/update',
        json={
            'id': 'no-such-order',
            'operation_id': 'operation-1234',
            'originator': 'processing',
            'payments': [
                {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'},
            ],
            'yandex_uid': '123',
            'items_by_payment_type': [
                {
                    'payment_type': 'card',
                    'items': [
                        {
                            'item_id': 'ride',
                            'product_id': 'taxi_park_ride',
                            'amount': '123',
                        },
                    ],
                },
            ],
        },
    )
    assert response.status == 404
    content = await response.json()
    assert content == {}


@pytest.mark.parametrize(
    'originator,priority',
    [('antifraud', 0), ('debt_collector', 1), ('processing', 1), ('admin', 2)],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_invoice_update_order(
        web_app_client, db, stq, originator, priority, now,
):
    response = await web_app_client.post(
        '/invoice/update',
        json={
            'id': 'my-order',
            'operation_id': 'operation-1234',
            'originator': originator,
            'payment': {
                'type': 'card',
                'method': '1324',
                'billing_id': 'card-1324',
            },
            'yandex_uid': '123',
            'items': [
                {
                    'item_id': 'ride',
                    'product_id': '132',
                    'amount': '123',
                    'region_id': 123,
                },
            ],
            'payment_timeout': 180,
            'user_ip': '127.0.0.1',
            'version': 0,
            'pass_params': {'a': 'b'},
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    order = await db.orders.find_one('my-order')

    assert order['invoice_request'] == {
        'operations': [
            {
                'created': now,
                'id': 'operation-1234',
                'type': 'update',
                'originator': originator,
                'payment_timeout': 180,
                'payment': {
                    'billing_id': 'card-1324',
                    'method': '1324',
                    'type': 'card',
                },
                'status': 'init',
                'items': [
                    {
                        'item_id': 'ride',
                        'product_id': '132',
                        'amount': '123',
                        'region_id': 123,
                    },
                ],
                'user_ip': '127.0.0.1',
                'pass_params': {'a': 'b'},
                'yandex_uid': '123',
            },
        ],
        'originator': originator,
        'priority': priority,
        'products': {'ride': '132'},
        'version': 1,
    }

    assert stq.transactions_events.times_called == 1
    assert stq.transactions_events.next_call()['id'] == 'my-order'


@pytest.mark.parametrize(
    'data_path',
    [
        'update_with_card_payment.json',
        pytest.param(
            'update_with_card_payment_archive.json',
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_ARCHIVE_ENABLED={'__default__': 1},
                ),
            ],
            id='it should restore invoice from archive,',
        ),
        'update_with_merchant_id.json',
        pytest.param(
            'update_with_product_change.json',
            marks=[_ALLOW_PRODUCT_ID_CHANGE],
        ),
        'update_with_price_and_quantity_payment.json',
        'update_with_card_and_wallet_payment.json',
        'update_with_agent_payment.json',
        'update_with_yandex_card_payment.json',
        'update_with_transaction_payload.json',
        'update_with_sbp_payment.json',
        'update_with_trust_additional_properties.json',
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_v2_invoice_update_order(
        patch, load_py_json, web_app_client, db, stq, data_path, now,
):
    data = load_py_json(data_path)
    helpers.patch_fetch_invoice(
        patch,
        result=data.get('fetch_invoice_result'),
        expected_invoice_id=data['request']['id'],
    )
    response = await web_app_client.post(
        '/v2/invoice/update', json=data['request'],
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}
    invoice_id = data['request']['id']
    order = await db.orders.find_one(invoice_id)
    assert order['invoice_request'] == data['expected_invoice_request']
    assert stq.transactions_events.times_called == 1
    assert stq.transactions_events.next_call()['id'] == invoice_id


@pytest.mark.parametrize('api_version', [1, 2])
async def test_invoice_update_already_called(
        web_app_client, db, stq, api_version,
):
    data = {
        'id': 'my-order-processing-applied',
        'operation_id': 'operation-1234',
        'originator': 'processing',
        'payment': {
            'type': 'card',
            'method': '1324',
            'billing_id': 'card-1324',
        },
        'yandex_uid': '123',
        'items': [{'item_id': 'ride', 'product_id': '132', 'amount': '123'}],
    }
    assert api_version in (1, 2)
    if api_version == 1:
        request_path = '/invoice/update'
    else:
        request_path = '/v2/invoice/update'
        data = _convert_to_v2_update_request(data)
    response = await web_app_client.post(request_path, json=data)
    assert response.status == 200
    assert stq.transactions_events.times_called == 1
    assert (
        stq.transactions_events.next_call()['id']
        == 'my-order-processing-applied'
    )


@pytest.mark.parametrize('api_version', [1, 2])
async def test_invoice_update_lower_priority(web_app_client, db, api_version):
    data = {
        'id': 'my-order-processing-applied',
        'operation_id': 'operation-antifraud',
        'originator': 'antifraud',
        'payment': {
            'type': 'card',
            'method': '1324',
            'billing_id': 'card-1324',
        },
        'yandex_uid': '123',
        'items': [{'item_id': 'ride', 'product_id': '132', 'amount': '123'}],
    }
    assert api_version in (1, 2)
    if api_version == 1:
        request_path = '/invoice/update'
    else:
        request_path = '/v2/invoice/update'
        data = _convert_to_v2_update_request(data)
    response = await web_app_client.post(request_path, json=data)
    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'conflict',
        'message': 'Originator priority conflict',
    }


@pytest.mark.parametrize('api_version', [1, 2])
@pytest.mark.parametrize(
    'item,message',
    [
        (
            # item without product, config disabled
            {'item_id': 'tips', 'amount': '123'},
            'product_id is not known for item tips',
        ),
        pytest.param(
            # item without product, config enabled
            {'item_id': 'tips', 'amount': '123'},
            'product_id is not known for item tips',
            marks=[_ALLOW_PRODUCT_ID_CHANGE],
        ),
        (
            # product change, config disabled
            {'item_id': 'ride', 'product_id': 'product_2', 'amount': '123'},
            'Cannot change product_id for item ride',
        ),
    ],
)
async def test_invoice_update_product_change(
        web_app_client, db, item, message, api_version,
):
    data = {
        'id': 'my-order-processing-applied',
        'operation_id': 'operation-antifraud',
        'originator': 'processing',
        'payment': {
            'type': 'card',
            'method': '1324',
            'billing_id': 'card-1324',
        },
        'yandex_uid': '123',
        'items': [item],
    }
    assert api_version in (1, 2)
    if api_version == 1:
        request_path = '/invoice/update'
    else:
        request_path = '/v2/invoice/update'
        data = _convert_to_v2_update_request(data)
    response = await web_app_client.post(request_path, json=data)
    assert response.status == 400
    content = await response.json()
    assert content == {'code': 'bad-request', 'message': message}


@pytest.mark.parametrize('api_version', [1, 2])
@pytest.mark.now('2020-01-01T00:00:00')
async def test_invoice_update_higher_priority(
        web_app_client, db, stq, now, api_version,
):
    data = {
        'id': 'my-order-processing-applied',
        'operation_id': 'operation-admin',
        'originator': 'admin',
        'yandex_uid': '123',
        'items': [
            {'item_id': 'ride', 'product_id': 'product_1', 'amount': '1000'},
        ],
    }
    expected_invoice_request = {
        'operations': [
            {
                'id': 'operation-1234',
                'originator': 'processing',
                'payment': {
                    'billing_id': 'card-1324',
                    'method': '1324',
                    'type': 'card',
                },
                'type': 'update',
                'status': 'init',
                'items': [],
            },
            {
                'created': now,
                'id': 'operation-admin',
                'type': 'update',
                'originator': 'admin',
                'status': 'init',
                'items': [
                    {
                        'item_id': 'ride',
                        'product_id': 'product_1',
                        'amount': '1000',
                    },
                ],
                'yandex_uid': '123',
            },
        ],
        'originator': 'admin',
        'priority': 2,
        'products': {'ride': 'product_1'},
        'version': 2,
    }
    assert api_version in (1, 2)
    if api_version == 1:
        request_path = '/invoice/update'
    else:
        request_path = '/v2/invoice/update'
        data = _convert_to_v2_update_request(data)
        expected_invoice_request['operations'][-1] = (
            _convert_to_v2_update_request(
                expected_invoice_request['operations'][-1],
            )
        )
    response = await web_app_client.post(request_path, json=data)
    assert response.status == 200
    content = await response.json()
    assert content == {}

    order = await db.orders.find_one('my-order-processing-applied')

    assert order['invoice_request'] == expected_invoice_request
    assert stq.transactions_events.times_called == 1
    assert (
        stq.transactions_events.next_call()['id']
        == 'my-order-processing-applied'
    )


@pytest.mark.parametrize('api_version', [1, 2])
@pytest.mark.now('2020-01-01T00:00:00')
async def test_invoice_update_order_need_cvn(
        web_app_client, db, stq, now, api_version,
):
    data = {
        'id': 'my-order',
        'operation_id': 'operation-1234',
        'originator': 'processing',
        'yandex_uid': '123',
        'items': [{'item_id': 'ride', 'product_id': '132', 'amount': '123'}],
        'need_cvn': True,
        'user_ip': '127.0.0.1',
        'version': 0,
    }
    expected_invoice_request = {
        'operations': [
            {
                'created': now,
                'id': 'operation-1234',
                'type': 'update',
                'originator': 'processing',
                'status': 'init',
                'items': [
                    {'item_id': 'ride', 'product_id': '132', 'amount': '123'},
                ],
                'need_cvn': True,
                'user_ip': '127.0.0.1',
                'yandex_uid': '123',
            },
        ],
        'originator': 'processing',
        'priority': 1,
        'products': {'ride': '132'},
        'version': 1,
    }
    assert api_version in (1, 2)
    if api_version == 1:
        request_path = '/invoice/update'
    else:
        request_path = '/v2/invoice/update'
        data = _convert_to_v2_update_request(data)
        expected_invoice_request['operations'][-1] = (
            _convert_to_v2_update_request(
                expected_invoice_request['operations'][-1],
            )
        )
    response = await web_app_client.post(request_path, json=data)
    assert response.status == 200
    content = await response.json()
    assert content == {}

    order = await db.orders.find_one('my-order')

    assert order['invoice_request'] == expected_invoice_request

    assert stq.transactions_events.times_called == 1
    assert stq.transactions_events.next_call()['id'] == 'my-order'


@pytest.mark.parametrize(
    'data_path',
    [
        'empty_payments.json',
        'merchant_id_in_only_some_items.json',
        'different_merchants.json',
        'no_merchant_id_in_invoice_with_merchant.json',
        'no_merchant_id_in_invoice_with_merchant_and_empty_op.json',
        'merchant_id_in_invoice_without_merchant.json',
        'no_payments_after_update.json',
        'duplicate_payments.json',
        'yandex_card_without_login_id.json',
        'amount_and_price.json',
        'amount_and_quantity.json',
        'price_without_quantity.json',
        'quantity_without_price.json',
        'neither_amount_nor_price.json',
        'amount_and_price_plus_quantity_in_item_list.json',
        'bad_operation_id.json',
        'duplicate_items.json',
        'duplicate_payment_types.json',
        'coop_account_payment.json',
        'coop_account_payment_type.json',
        'long_fiscal_title.json',
        'without_trust_orders_different_product_ids.json',
        'without_trust_orders_no_product_ids.json',
    ],
)
async def test_invalid_v2_update(load_py_json, web_app_client, data_path):
    data = load_py_json(data_path)
    response = await web_app_client.post(
        '/v2/invoice/update', json=data['request'],
    )
    assert response.status == 400
    content = await response.json()
    assert data['expected_message'] in content['message']


@pytest.mark.parametrize(
    'data_path', ['update_with_card_payment.json', 'conflict.json'],
)
@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.config(
    TRANSACTIONS_PLAN_OPERATION_IN_ADVANCE={
        '__default__': False,
        'taxi': True,
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_preplan_operation(
        load_py_json, web_app_client, db, stq, data_path, now,
):
    data = load_py_json(data_path)
    response = await web_app_client.post(
        '/v2/invoice/update', json=data['request'],
    )
    assert response.status == data['expected_status']
    assert stq.transactions_events.times_called == 0
    calls = _get_plan_operation_calls(stq.transactions_plan_operation)
    assert calls == data['expected_calls']


@pytest.mark.config(
    TRANSACTIONS_PAYMENT_LIMITS={
        '__default__': {'enabled': False, 'limits': {'__default__': '9'}},
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_limits_disabled(load_py_json, web_app_client):
    await _assert_payment_limit_not_broken(
        load_py_json, web_app_client, 'test_payment_limits/success.json',
    )


@pytest.mark.config(
    TRANSACTIONS_PAYMENT_LIMITS={
        '__default__': {'enabled': True, 'limits': {'__default__': '9'}},
        'taxi': {'enabled': False, 'limits': {'__default__': '9'}},
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_taxi_limits_disabled(load_py_json, web_app_client):
    await _assert_payment_limit_not_broken(
        load_py_json, web_app_client, 'test_payment_limits/success.json',
    )


@pytest.mark.config(
    TRANSACTIONS_PAYMENT_LIMITS={
        '__default__': {'enabled': True, 'limits': {'__default__': '9'}},
        'taxi': {
            'enabled': True,
            'limits': {'__default__': '9', 'RUB': '999'},
        },
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_taxi_rub_limit_not_broken(load_py_json, web_app_client):
    await _assert_payment_limit_not_broken(
        load_py_json, web_app_client, 'test_payment_limits/success.json',
    )


@pytest.mark.config(
    TRANSACTIONS_PAYMENT_LIMITS={
        '__default__': {'enabled': True, 'limits': {'__default__': '9'}},
        'taxi': {
            'enabled': True,
            'limits': {'__default__': '999', 'RUB': '99'},
        },
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_taxi_rub_limit_broken_for_ride(load_py_json, web_app_client):
    await _assert_payment_limit_broken(
        load_py_json,
        web_app_client,
        'test_payment_limits/limit_broken_for_ride.json',
    )


@pytest.mark.config(
    TRANSACTIONS_PAYMENT_LIMITS={
        '__default__': {'enabled': True, 'limits': {'__default__': '9'}},
        'taxi': {
            'enabled': True,
            'limits': {'__default__': '999', 'RUB': '99'},
        },
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_taxi_rub_limit_broken_for_tips(load_py_json, web_app_client):
    await _assert_payment_limit_broken(
        load_py_json,
        web_app_client,
        'test_payment_limits/limit_broken_for_tips.json',
    )


@pytest.mark.config(
    TRANSACTIONS_PAYMENT_LIMITS={
        '__default__': {'enabled': True, 'limits': {'__default__': '99'}},
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_no_currency_update_fail(load_py_json, web_app_client):
    await _assert_payment_limit_broken(
        load_py_json, web_app_client, 'test_payment_limits/no_currency.json',
    )


def _convert_to_v2_update_request(update_request):
    data = copy.deepcopy(update_request)
    if 'payment' in data:
        data['payments'] = [data.pop('payment')]
    items = data.pop('items', [])
    if items:
        data['items_by_payment_type'] = [
            {'payment_type': 'card', 'items': items},
        ]
    return data


def _get_plan_operation_calls(queue):
    return [
        {
            'id': call['id'],
            'args': call['args'],
            'kwargs': _remove_fields(call['kwargs'], ['log_extra', 'created']),
            'eta': call['eta'],
        }
        for call in _get_calls(queue)
    ]


def _get_calls(queue):
    calls = []
    while queue.has_calls:
        calls.append(queue.next_call())
    return calls


def _remove_fields(kwargs, fields):
    return {k: v for k, v in kwargs.items() if k not in fields}


async def _assert_payment_limit_broken(
        load_py_json, web_app_client, data_path,
):
    data = load_py_json(data_path)
    response = await _request_for_payment_limits(web_app_client, data)
    assert response.status == 400
    response_data = await response.json()
    assert response_data['code'] == 'bad-request'
    assert response_data['message'] == data['expected_error']


async def _assert_payment_limit_not_broken(
        load_py_json, web_app_client, data_path,
):
    data = load_py_json(data_path)
    response = await _request_for_payment_limits(web_app_client, data)
    assert response.status == 200


async def _request_for_payment_limits(client, data):
    return await client.post(
        '/v2/invoice/update',
        json={
            'id': data['invoice_id'],
            'items_by_payment_type': data['items_by_payment_type'],
            'operation_id': 'operation-1234',
            'originator': 'processing',
            'user_ip': '127.0.0.1',
            'yandex_uid': '123',
        },
    )


@pytest.mark.parametrize('omit_billing_id', [False, True])
@pytest.mark.parametrize(
    'data_path', ['card.json', 'applepay.json', 'googlepay.json'],
)
async def test_omitted_billing_id(
        load_py_json, web_app_client, db, data_path, omit_billing_id,
):
    data = load_py_json(data_path)
    invoice_id = 'my-order'
    body = {
        'id': invoice_id,
        'items_by_payment_type': [],
        'operation_id': 'operation-1234',
        'originator': 'processing',
        'pass_params': {},
        'payments': data['payments'],
        'user_ip': '127.0.0.1',
        'version': 0,
        'yandex_uid': '123',
    }
    if omit_billing_id:
        body['payments'] = [
            _without_billing_id(payment) for payment in data['payments']
        ]
    response = await web_app_client.post('/v2/invoice/update', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}
    order = await db.orders.find_one(invoice_id)
    operations = order['invoice_request']['operations']
    assert len(operations) == 1
    assert operations[0]['payments'] == data['payments']


@pytest.mark.parametrize(
    'data_path',
    [
        # pnq = price & quantity
        # Check is enabled in Eda, pnq is required: expect 400
        'eda_pnq_required.json',
        # Check is enabled in Eda, pnq is not required: expect 200
        'eda_pnq_not_required.json',
        # Check is disabled in Taxi, pnq is required: expect 200
        'taxi_pnq_required.json',
        # Check is enabled in Eda, price changes: expect 400
        'eda_price_changes.json',
        # Check is enabled in Eda, price doesn't change: expect 200
        'eda_price_doesnt_change.json',
        # Check is disabled in Taxi, price changes: expect 200
        'taxi_price_changes.json',
        # Check old_composite_basket for sbp: expect 400
        'eda_price_sbp_changes.json',
        # Check old_composite_basket for sbp: expect 200
        'eda_price_sbp_changes_when_previous_failed.json',
    ],
)
@pytest.mark.config(
    TRANSACTIONS_SERVICES_WITH_MANDATORY_QUANTITIES=[
        'lavka_courier_payment',
        'card',
    ],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_price_and_quantity_checks(
        load_py_json, eda_web_app_client, web_app_client, data_path,
):
    clients_by_scope = {'taxi': web_app_client, 'eda': eda_web_app_client}
    data = load_py_json(data_path)
    client = clients_by_scope[data['scope']]
    response = await client.post('/v2/invoice/update', json=data['request'])
    assert response.status == data['expected_status']
    if response.status != 200:
        content = await response.json()
        assert content['message'] == data['expected_message']


def _without_billing_id(payment):
    if 'billing_id' not in payment:
        return payment
    if payment['type'] in ('applepay', 'googlepay', 'card'):
        stripped = copy.deepcopy(payment)
        del stripped['billing_id']
        return stripped
    return payment


@pytest.mark.now('2020-01-01T00:00:00')
async def test_v2_invoice_update_intent(
        load_py_json, web_app_client, db, stq, now,
):
    intent_str = 'Hehe classic'
    request = {
        'id': 'my-order',
        'items_by_payment_type': [
            {
                'items': [
                    {
                        'amount': '123',
                        'commission_category': 600,
                        'item_id': 'ride',
                    },
                ],
                'payment_type': 'agent',
            },
        ],
        'login_id': 'some_login_id',
        'mcc': 1234,
        'operation_id': 'operation-1234',
        'originator': 'processing',
        'payment_timeout': 180,
        'payments': [{'agent_id': '007', 'type': 'agent'}],
        'user_ip': '127.0.0.1',
        'version': 0,
        'yandex_uid': '123',
        'intent': intent_str,
    }
    response = await web_app_client.post('/v2/invoice/update', json=request)
    assert response.status == 200
    content = await response.json()
    assert content == {}
    invoice_id = request['id']
    order = await db.orders.find_one(invoice_id)
    assert order['invoice_request']['operations'][0]['intent'] == intent_str
    assert stq.transactions_events.times_called == 1
    assert stq.transactions_events.next_call()['id'] == invoice_id
