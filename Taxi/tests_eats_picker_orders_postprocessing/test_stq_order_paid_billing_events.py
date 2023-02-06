import math
import operator

import pytest

from tests_eats_picker_orders_postprocessing import billing_event_utils

IDEMPOTENCY_TOKEN_PREFIX = 'retail_picker_'


@pytest.mark.parametrize(
    'billing_storage_response, eats_checkout_calls',
    [
        [
            {
                'json': {'message': 'Bad request', 'status': 'fail'},
                'status': 400,
            },
            0,
        ],
        [
            {'json': {'message': 'Conflict', 'status': 'fail'}, 'status': 409},
            1,
        ],
    ],
)
@pytest.mark.experiments3(filename='exp3_stq_settings.json')
@pytest.mark.experiments3(filename='exp3_cost_for_place.json')
async def test_stq_order_paid_billing_event_errors(
        stq_runner,
        mockserver,
        generate_picker_item,
        generate_picker_order,
        load_json,
        billing_storage_response,
        eats_checkout_calls,
):
    item = generate_picker_item(
        item_id='eats-item-1',
        count=2,
        measure={'quantum': 1000, 'value': 2000, 'unit': 'GRM'},
        is_catch_weight=True,
        measure_v2={
            'value': 2000,
            'quantum': 1000,
            'quantum_price': '1.0',
            'quantum_quantity': 2,
            'absolute_quantity': 2000,
            'unit': 'GRM',
        },
    )

    eats_id = '999'
    order = generate_picker_order(
        eats_id=eats_id,
        version=1,
        picker_id='123-456',
        status='complete',
        picker_items=[item],
    )
    order_id = order['id']

    @mockserver.json_handler('eats-picker-orders/api/v1/order')
    def _mock_order_get(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'payload': order, 'meta': {}}, status=200,
        )

    @mockserver.json_handler('eats-picker-orders/api/v1/order/cart')
    def _mock_order_cart(request):
        return mockserver.make_response(
            json={
                'picker_items': [{'id': item['id'], 'count': 3}],
                'cart_version': 1,
            },
        )

    @mockserver.json_handler('/eats-checkout/order/cost-for-place/')
    def _mock_eats_checkout(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json['cost_for_place'] == '1502.58'
        assert request.json['order_nr'] == eats_id
        assert request.json['currency'] == 'RUB'
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json['status'] == 'new'
        assert request.json['kind'] == 'PickerOrderPaidEvent'
        assert (
            request.json['external_event_ref']
            == f'PickerOrderPaidEvent/{order_id}'
        )
        assert request.json['service'] == 'eats-picker-orders-postprocessing'
        assert request.json['external_obj_id'] == eats_id
        assert request.json['service_user_id'] == '123-456'
        assert request.json['event_at'] == '2020-06-01T00:00:00'
        assert request.json['tags'] == []
        assert request.json['journal_entries'] == []

        assert request.json['data'] == {
            'amount': 1502.58,
            'paid_at': '2020-06-01T00:00:00',
            'currency': 'RUB',
        }
        return mockserver.make_response(**billing_storage_response)

    @mockserver.json_handler('/eats-checkout/order-changes/create')
    def _mock_order_changes_create(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json == {'order_id': eats_id}
        return mockserver.make_response(
            json={'change_id': 5, 'is_cost_increase_allowed': True},
            status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/add-offer')
    def _mock_order_changes_add_offer(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(json={'offer_id': 5}, status=200)

    await stq_runner.order_paid_billing_events.call(
        task_id='sample_task',
        kwargs={
            'order_id': order_id,
            'eats_id': eats_id,
            'picker_id': '123-456',
            'paid_at': '2020-06-01T00:00:00',
            'amount': 1502.58,
            'currency': 'RUB',
        },
    )
    assert _mock_eats_billing_storage.times_called == 1
    assert _mock_order_changes_create.times_called == eats_checkout_calls
    assert _mock_order_changes_add_offer.times_called == eats_checkout_calls
    assert _mock_eats_checkout.times_called == eats_checkout_calls


@pytest.mark.parametrize('response_code', [409, 425])
@pytest.mark.experiments3(filename='exp3_stq_settings.json')
@pytest.mark.experiments3(filename='exp3_cost_for_place.json')
async def test_stq_order_paid_billing_event_eats_checkout_cost_for_place_retry(
        stq_runner,
        mockserver,
        generate_picker_item,
        generate_picker_order,
        response_code,
):
    cost_for_place_attempts = 3
    eats_id = '999'
    picker_id = '123-456'

    item = generate_picker_item(
        item_id='eats-item-1',
        count=2,
        measure={'quantum': 1000, 'value': 2000, 'unit': 'GRM'},
        is_catch_weight=True,
        measure_v2={
            'value': 2000,
            'quantum': 1000,
            'quantum_price': '1.0',
            'quantum_quantity': 2,
            'absolute_quantity': 2000,
            'unit': 'GRM',
        },
    )

    order = generate_picker_order(
        eats_id=eats_id,
        version=1,
        picker_id=picker_id,
        status='complete',
        picker_items=[item],
    )
    order_id = order['id']

    @mockserver.json_handler('eats-picker-orders/api/v1/order')
    def _mock_order_get(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'payload': order, 'meta': {}}, status=200,
        )

    @mockserver.json_handler('eats-picker-orders/api/v1/order/cart')
    def _mock_order_cart(request):
        return mockserver.make_response(
            json={
                'picker_items': [{'id': item['id'], 'count': 3}],
                'cart_version': 1,
            },
        )

    @mockserver.json_handler('/eats-checkout/order/cost-for-place/')
    def _mock_eats_checkout(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json['cost_for_place'] == '1502.58'
        assert request.json['order_nr'] == eats_id
        assert request.json['currency'] == 'RUB'
        return mockserver.make_response(status=response_code)

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(
            json={'message': 'OK', 'status': 'success'}, status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/create')
    def _mock_order_changes_create(request):
        assert request.json == {'order_id': eats_id}
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(
            json={'change_id': 5, 'is_cost_increase_allowed': True},
            status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/add-offer')
    def _mock_order_changes_add_offer(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(json={'offer_id': 5}, status=200)

    await stq_runner.order_paid_billing_events.call(
        task_id='sample_task',
        kwargs={
            'order_id': order_id,
            'eats_id': eats_id,
            'picker_id': picker_id,
            'paid_at': '2020-06-01T00:00:00',
            'amount': 1502.58,
            'currency': 'RUB',
        },
    )
    assert _mock_eats_billing_storage.times_called == 1
    assert _mock_order_changes_create.times_called == 1
    assert _mock_order_changes_add_offer.times_called == 1
    assert _mock_eats_checkout.times_called == cost_for_place_attempts


@pytest.mark.experiments3(filename='exp3_stq_settings.json')
@pytest.mark.experiments3(filename='exp3_cost_for_place.json')
async def test_stq_order_paid_billing_event_eats_checkout_add_offer_404(
        stq_runner,
        mockserver,
        generate_picker_item,
        generate_picker_order,
        taxi_config,
):
    eats_id = '999'
    picker_id = '123-456'
    item = generate_picker_item(
        item_id='eats-item-1',
        count=2,
        measure={'quantum': 1000, 'value': 2000, 'unit': 'GRM'},
        is_catch_weight=True,
        measure_v2={
            'value': 2000,
            'quantum': 1000,
            'quantum_price': '1.0',
            'quantum_quantity': 2,
            'absolute_quantity': 2000,
            'unit': 'GRM',
        },
    )

    order = generate_picker_order(
        eats_id=eats_id,
        version=1,
        picker_id=picker_id,
        status='complete',
        picker_items=[item],
    )
    order_id = order['id']

    @mockserver.json_handler('eats-picker-orders/api/v1/order')
    def _mock_order_get(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'payload': order, 'meta': {}}, status=200,
        )

    @mockserver.json_handler('eats-picker-orders/api/v1/order/cart')
    def _mock_order_cart(request):
        return mockserver.make_response(
            json={
                'picker_items': [{'id': item['id'], 'count': 3}],
                'cart_version': 1,
            },
        )

    @mockserver.json_handler('/eats-checkout/order/cost-for-place/')
    def _mock_eats_checkout(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(
            json={'message': 'OK', 'status': 'success'}, status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/create')
    def _mock_order_changes_create(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json == {'order_id': eats_id}
        return mockserver.make_response(
            json={'change_id': 5, 'is_cost_increase_allowed': True},
            status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/add-offer')
    def _mock_order_changes_add_offer(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    await stq_runner.order_paid_billing_events.call(
        task_id='sample_task',
        kwargs={
            'order_id': order_id,
            'eats_id': eats_id,
            'picker_id': picker_id,
            'paid_at': '2020-06-01T00:00:00',
            'amount': 1502.58,
            'currency': 'RUB',
        },
    )
    assert _mock_eats_billing_storage.times_called == 1
    assert _mock_order_changes_create.times_called == 1
    assert _mock_order_changes_add_offer.times_called == 1
    assert _mock_eats_checkout.times_called == 1
    assert _mock_stq_reschedule.times_called == 0


@pytest.mark.experiments3(filename='exp3_stq_settings.json')
@pytest.mark.experiments3(filename='exp3_cost_for_place.json')
async def test_stq_order_paid_billing_event_retries_exceeded(
        stq_runner, mockserver,
):
    await stq_runner.order_paid_billing_events.call(
        task_id='sample_task',
        kwargs={
            'order_id': 12345,
            'eats_id': '999',
            'picker_id': '123-456',
            'paid_at': '2020-06-01T00:00:00',
            'amount': 1502.58,
            'currency': 'RUB',
        },
        exec_tries=0,
        reschedule_counter=3,
    )

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        assert request.headers['X-Idempotency-Token'] == '999'

    assert _mock_eats_billing_storage.times_called == 0


@pytest.mark.parametrize(
    'order, expected', billing_event_utils.get_test_cases_without_aligner(),
)
@pytest.mark.experiments3(filename='exp3_stq_settings.json')
@pytest.mark.experiments3(filename='exp3_cost_for_place.json')
async def test_stq_order_paid_billing_event_without_price_aligner(
        stq_runner,
        mockserver,
        load_json,
        order,
        expected,
        generate_picker_item,
        generate_picker_order,
):
    eats_id = 'eats_id_0'
    picker_id = 'picker_7'
    amount = order['amount']

    order_items_by_version = {}
    items = []
    for order_item in order['order_items']:
        version = int(order_item['version']) if 'version' in order_item else 0
        if 'measure_value' not in order_item:
            order_item['measure_value'] = 1
        if 'price' not in order_item:
            order_item['price'] = 10.0
        order_item['relative_quantum'] = 1.0

        is_catch_weight = (
            order_item['sold_by_weight']
            if 'sold_by_weight' in order_item
            else 'measure_value' in order_item
        )

        measure_v2 = None
        if 'measure_quantum' in order_item:
            measure_v2 = {
                'value': order_item['measure_value'],
                'quantum': order_item['measure_quantum'],
                'quantum_price': '{:.2f}'.format(order_item['quantum_price']),
                'quantum_quantity': order_item['quantum_quantity'],
                'absolute_quantity': order_item['absolute_quantity'],
                'relative_quantum': order_item['relative_quantum'],
                'unit': 'GRM',
            }

        quantity = order_item['quantity'] if 'quantity' in order_item else 1

        item = generate_picker_item(
            item_id=order_item['eats_item_id'],
            measure={
                'quantum': order_item['measure_value'],
                'value': quantity * order_item['measure_value'],
                'unit': 'GRM',
            },
            measure_v2=measure_v2,
            is_catch_weight=is_catch_weight,
            count=(quantity if not is_catch_weight else None),
            price='{:.2f}'.format(order_item['price']),
            name='Foo bar',
        )
        items.append(item)
        if version not in order_items_by_version:
            order_items_by_version[version] = []
        order_items_by_version[version].append(item)

    orders = {}
    orders[0] = generate_picker_order(
        eats_id=eats_id,
        brand_id=str(111),
        place_id=222,
        picker_id=picker_id,
        status='complete',
        version=0,
    )

    max_order_version = 0
    for version, order_items in order_items_by_version.items():
        orders[version] = generate_picker_order(
            eats_id=eats_id,
            brand_id=str(111),
            place_id=222,
            picker_id=picker_id,
            status='complete',
            version=version,
            picker_items=order_items,
        )
        max_order_version = max(max_order_version, version)

    cart_items_by_version = {}
    max_cart_version = 0
    for picked_item in order['picked_items']:
        version = picked_item['cart_version']
        if version not in cart_items_by_version:
            cart_items_by_version[version] = []
        cart_items_by_version[version].append(
            {
                'id': items[picked_item['order_item']]['id'],
                'count': (
                    picked_item['count'] if 'count' in picked_item else None
                ),
                'weight': (
                    picked_item['weight'] if 'weight' in picked_item else None
                ),
            },
        )
        max_cart_version = max(max_cart_version, version)

    order_id = 0

    @mockserver.json_handler('eats-picker-orders/api/v1/order')
    def _mock_order_get(request):
        assert request.method == 'GET'
        version = (
            int(request.query['version'])
            if 'version' in request.query
            else max_order_version
        )
        nonlocal order_id
        order_id = orders[version]['id']
        return mockserver.make_response(
            json={'payload': orders[version], 'meta': {}}, status=200,
        )

    @mockserver.json_handler('eats-picker-orders/api/v1/order/cart')
    def _mock_order_cart(request):
        items = (
            cart_items_by_version[max_cart_version]
            if max_cart_version in cart_items_by_version
            else []
        )
        return mockserver.make_response(
            json={'picker_items': items, 'cart_version': max_cart_version},
        )

    @mockserver.json_handler('/eats-checkout/order/cost-for-place/')
    def _mock_eats_checkout(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json['cost_for_place'] == f'{amount:.2f}'
        assert request.json['order_nr'] == eats_id
        assert request.json['currency'] == 'RUB'
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json['status'] == 'new'
        assert request.json['kind'] == 'PickerOrderPaidEvent'
        assert (
            request.json['external_event_ref']
            == f'PickerOrderPaidEvent/{order_id}'
        )
        assert request.json['service'] == 'eats-picker-orders-postprocessing'
        assert request.json['external_obj_id'] == eats_id
        assert request.json['service_user_id'] == picker_id
        assert request.json['event_at'] == '2020-06-01T00:00:00'
        assert request.json['tags'] == []
        assert request.json['journal_entries'] == []
        assert request.json['data'] == {
            'amount': amount,
            'paid_at': '2020-06-01T00:00:00',
            'currency': 'RUB',
        }
        return mockserver.make_response(
            json={'message': 'OK', 'status': 'success'}, status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/create')
    def _mock_order_changes_create(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json == {'order_id': eats_id}
        return mockserver.make_response(
            json={'change_id': 5, 'is_cost_increase_allowed': True},
            status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/add-offer')
    def _mock_order_changes_add_offer(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        request.json['offer']['operations'].sort(
            key=operator.itemgetter('identity'),
        )
        expected_request = billing_event_utils.make_expected_cart_diff_request(
            order, expected,
        )
        assert request.json == expected_request
        return mockserver.make_response(json={'offer_id': 5}, status=200)

    await stq_runner.order_paid_billing_events.call(
        task_id='sample_task',
        kwargs={
            'order_id': order_id,
            'eats_id': eats_id,
            'picker_id': picker_id,
            'paid_at': '2020-06-01T00:00:00',
            'amount': amount,
            'currency': 'RUB',
        },
    )

    order_changes_calls = 1 if expected else 0
    assert _mock_eats_billing_storage.times_called == 1
    assert _mock_order_changes_create.times_called == order_changes_calls
    assert _mock_order_changes_add_offer.times_called == order_changes_calls
    assert _mock_eats_checkout.times_called == 1


@pytest.mark.experiments3(filename='exp3_price_aligner.json')
@pytest.mark.parametrize(
    'order, expected', billing_event_utils.get_test_cases_with_aligner(),
)
@pytest.mark.experiments3(filename='exp3_stq_settings.json')
@pytest.mark.experiments3(filename='exp3_cost_for_place.json')
async def test_stq_order_paid_billing_event_with_price_aligner(
        stq_runner,
        mockserver,
        load_json,
        order,
        expected,
        generate_picker_item,
        generate_picker_order,
):
    eats_id = 'eats_id_0'
    picker_id = 'picker_7'
    amount = order['amount']

    order_items_by_version = {}
    items = []
    for order_item in order['order_items']:
        version = int(order_item['version']) if 'version' in order_item else 0
        if 'measure_value' not in order_item:
            order_item['measure_value'] = 1
        if 'price' not in order_item:
            order_item['price'] = 10.0
        order_item['relative_quantum'] = 1.0

        is_catch_weight = (
            order_item['sold_by_weight']
            if 'sold_by_weight' in order_item
            else 'measure_value' in order_item
        )

        measure_v2 = None
        if 'measure_quantum' in order_item:
            measure_v2 = {
                'value': order_item['measure_value'],
                'quantum': order_item['measure_quantum'],
                'quantum_price': '{:.2f}'.format(order_item['quantum_price']),
                'quantum_quantity': order_item['quantum_quantity'],
                'absolute_quantity': order_item['absolute_quantity'],
                'relative_quantum': order_item['relative_quantum'],
                'unit': 'GRM',
            }

        quantity = order_item['quantity'] if 'quantity' in order_item else 1

        item = generate_picker_item(
            item_id=order_item['eats_item_id'],
            measure={
                'quantum': order_item['measure_value'],
                'value': quantity * order_item['measure_value'],
                'unit': 'GRM',
            },
            measure_v2=measure_v2,
            is_catch_weight=is_catch_weight,
            count=(quantity if not is_catch_weight else None),
            price='{:.2f}'.format(order_item['price']),
            name='Foo bar',
        )
        items.append(item)
        if version not in order_items_by_version:
            order_items_by_version[version] = []
        order_items_by_version[version].append(item)

    orders = {}
    orders[0] = generate_picker_order(
        eats_id=eats_id,
        brand_id=str(111),
        place_id=222,
        picker_id=picker_id,
        status='complete',
        version=0,
    )

    max_order_version = 0
    for version, order_items in order_items_by_version.items():
        orders[version] = generate_picker_order(
            eats_id=eats_id,
            brand_id=str(111),
            place_id=222,
            picker_id=picker_id,
            status='complete',
            version=version,
            picker_items=order_items,
        )
        max_order_version = max(max_order_version, version)

    cart_items_by_version = {}
    max_cart_version = 0
    for picked_item in order['picked_items']:
        version = picked_item['cart_version']
        if version not in cart_items_by_version:
            cart_items_by_version[version] = []
        cart_items_by_version[version].append(
            {
                'id': items[picked_item['order_item']]['id'],
                'count': (
                    picked_item['count'] if 'count' in picked_item else None
                ),
                'weight': (
                    picked_item['weight'] if 'weight' in picked_item else None
                ),
            },
        )
        max_cart_version = max(max_cart_version, version)

    order_id = 0

    @mockserver.json_handler('eats-picker-orders/api/v1/order')
    def _mock_order_get(request):
        assert request.method == 'GET'
        version = (
            int(request.query['version'])
            if 'version' in request.query
            else max_order_version
        )
        nonlocal order_id
        order_id = orders[version]['id']
        return mockserver.make_response(
            json={'payload': orders[version], 'meta': {}}, status=200,
        )

    @mockserver.json_handler('eats-picker-orders/api/v1/order/cart')
    def _mock_order_cart(request):
        items = (
            cart_items_by_version[max_cart_version]
            if max_cart_version in cart_items_by_version
            else []
        )
        return mockserver.make_response(
            json={'picker_items': items, 'cart_version': max_cart_version},
        )

    @mockserver.json_handler('/eats-checkout/order/cost-for-place/')
    def _mock_eats_checkout(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json['cost_for_place'] == f'{amount:.2f}'
        assert request.json['order_nr'] == eats_id
        assert request.json['currency'] == 'RUB'
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json['status'] == 'new'
        assert request.json['kind'] == 'PickerOrderPaidEvent'
        assert (
            request.json['external_event_ref']
            == f'PickerOrderPaidEvent/{order_id}'
        )
        assert request.json['service'] == 'eats-picker-orders-postprocessing'
        assert request.json['external_obj_id'] == eats_id
        assert request.json['service_user_id'] == picker_id
        assert request.json['event_at'] == '2020-06-01T00:00:00'
        assert request.json['tags'] == []
        assert request.json['journal_entries'] == []

        assert request.json['data'] == {
            'amount': amount,
            'paid_at': '2020-06-01T00:00:00',
            'currency': 'RUB',
        }
        return mockserver.make_response(
            json={'message': 'OK', 'status': 'success'}, status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/create')
    def _mock_order_changes_create(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json == {'order_id': eats_id}
        return mockserver.make_response(
            json={'change_id': 5, 'is_cost_increase_allowed': True},
            status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/add-offer')
    def _mock_order_changes_add_offer(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        request.json['offer']['operations'].sort(
            key=operator.itemgetter('identity'),
        )
        expected_request = billing_event_utils.make_expected_cart_diff_request(
            order, expected,
        )
        assert request.json == expected_request
        return mockserver.make_response(json={'offer_id': 5}, status=200)

    await stq_runner.order_paid_billing_events.call(
        task_id='sample_task',
        kwargs={
            'order_id': order_id,
            'eats_id': eats_id,
            'picker_id': picker_id,
            'paid_at': '2020-06-01T00:00:00',
            'amount': amount,
            'currency': 'RUB',
        },
    )

    order_changes_calls = 1 if expected else 0
    assert _mock_eats_billing_storage.times_called == 1
    assert _mock_order_changes_create.times_called == order_changes_calls
    assert _mock_order_changes_add_offer.times_called == order_changes_calls
    assert _mock_eats_checkout.times_called == 1


@pytest.mark.experiments3(filename='exp3_stq_settings.json')
@pytest.mark.experiments3(filename='exp3_cost_for_place.json')
async def test_stq_order_paid_billing_event_rounding(
        stq_runner,
        mockserver,
        generate_picker_item,
        generate_picker_order,
        taxi_config,
):
    eats_id = '999'
    picker_id = '123-456'
    quantity = 1.1
    item = generate_picker_item(
        item_id='eats-item-1',
        measure={
            'quantum': 999,
            'value': 1098,
            'unit': 'GRM',
            'quantity': quantity,
        },
        is_catch_weight=True,
        measure_v2={
            'value': 2000,
            'quantum': 1000,
            'quantum_price': '1.0',
            'quantum_quantity': 2,
            'absolute_quantity': 2000,
            'unit': 'GRM',
        },
    )

    order = generate_picker_order(
        eats_id=eats_id,
        version=0,
        picker_id=picker_id,
        status='complete',
        picker_items=[item],
    )
    order_id = order['id']

    @mockserver.json_handler('eats-picker-orders/api/v1/order')
    def _mock_order_get(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'payload': order, 'meta': {}}, status=200,
        )

    @mockserver.json_handler('eats-picker-orders/api/v1/order/cart')
    def _mock_order_cart(request):
        return mockserver.make_response(
            json={
                'picker_items': [{'id': item['id'], 'weight': 1080}],
                'cart_version': 1,
            },
        )

    @mockserver.json_handler('/eats-checkout/order/cost-for-place/')
    def _mock_eats_checkout(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        return mockserver.make_response(
            json={'message': 'OK', 'status': 'success'}, status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/create')
    def _mock_order_changes_create(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json == {'order_id': eats_id}
        return mockserver.make_response(
            json={'change_id': 5, 'is_cost_increase_allowed': True},
            status=200,
        )

    @mockserver.json_handler('/eats-checkout/order-changes/add-offer')
    def _mock_order_changes_add_offer(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{IDEMPOTENCY_TOKEN_PREFIX}{eats_id}'
        )
        assert request.json['order_id'] == eats_id
        operations = request.json['offer']['operations']
        assert len(operations) == 1
        operation = operations[0]
        assert operation['operation_type'] == 'update'
        assert operation['identity'] == item['id']
        assert math.isclose(operation['quantity'], quantity, abs_tol=0.00001)
        return mockserver.make_response(status=200, json={'offer_id': 5})

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    await stq_runner.order_paid_billing_events.call(
        task_id='sample_task',
        kwargs={
            'order_id': order_id,
            'eats_id': eats_id,
            'picker_id': picker_id,
            'paid_at': '2020-06-01T00:00:00',
            'amount': 1502.58,
            'currency': 'RUB',
        },
    )
    assert _mock_eats_billing_storage.times_called == 1
    assert _mock_order_changes_create.times_called == 1
    assert _mock_order_changes_add_offer.times_called == 1
    assert _mock_eats_checkout.times_called == 1
    assert _mock_stq_reschedule.times_called == 0
