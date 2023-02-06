import operator

import pytest

from . import billing_event_utils

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
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        billing_storage_response,
        eats_checkout_calls,
):
    eats_id = '999'
    order_id = create_order(
        eats_id=eats_id,
        last_version=1,
        picker_id='123-456',
        payment_value=1502.58,
        state='complete',
    )

    item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-1',
        quantity=2,
        measure_value=1000,
        sold_by_weight=True,
    )

    create_picked_item(
        order_item_id=item_id, picker_id='picker_7', count=3, cart_version=1,
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
        assert request.json['service'] == 'eats-picker-orders'
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

    await stq_runner.send_order_paid_billing_event.call(
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
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        response_code,
):
    cost_for_place_attempts = 3
    eats_id = '999'
    picker_id = '123-456'
    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        payment_value=1502.58,
        state='complete',
    )
    item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-1',
        quantity=2,
        measure_value=1000,
        sold_by_weight=True,
    )
    create_picked_item(
        order_item_id=item_id, picker_id=picker_id, count=3, cart_version=1,
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

    await stq_runner.send_order_paid_billing_event.call(
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
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
):
    eats_id = '999'
    picker_id = '123-456'
    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        payment_value=1502.58,
        state='complete',
    )
    item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-1',
        quantity=2,
        measure_value=1000,
        sold_by_weight=True,
    )
    create_picked_item(
        order_item_id=item_id, picker_id=picker_id, count=3, cart_version=1,
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

    await stq_runner.send_order_paid_billing_event.call(
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
    await stq_runner.send_order_paid_billing_event.call(
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
    '',
    [
        pytest.param(),
        pytest.param(
            marks=[
                pytest.mark.experiments3(filename='exp3_price_aligner.json'),
            ],
        ),
    ],
)
async def test_stq_order_paid_billing_event_order_item_not_found(
        stq_runner,
        mockserver,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
):
    eats_id = 'eats_id_0'
    picker_id = 'picker_id_0'
    amount = 123.456

    order_id = create_order(
        eats_id=eats_id,
        last_version=0,
        picker_id=picker_id,
        payment_value=1502.58,
        state='complete',
    )

    item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-1',
        quantity=2,
        measure_value=1000,
        sold_by_weight=True,
    )

    create_picked_item(
        eats_id=eats_id,
        eats_item_id='unknown-item',
        order_version=0,
        order_item_id=item_id + 1,
        picker_id=picker_id,
        count=3,
        cart_version=1,
    )

    @mockserver.json_handler('/eats-billing-storage/billing-storage/create')
    def _mock_eats_billing_storage(request):
        return {'message': 'OK', 'status': 'success'}

    await stq_runner.send_order_paid_billing_event.call(
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


@pytest.mark.parametrize(
    'order, expected', billing_event_utils.get_test_cases_without_aligner(),
)
@pytest.mark.experiments3(filename='exp3_stq_settings.json')
@pytest.mark.experiments3(filename='exp3_cost_for_place.json')
async def test_stq_order_paid_billing_event_without_price_aligner(
        stq_runner,
        mockserver,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        order,
        expected,
):
    eats_id = 'eats_id_0'
    picker_id = order['picker_id']
    amount = order['amount']

    order_id = create_order(
        eats_id=eats_id,
        brand_id=111,
        place_id=222,
        last_version=order['last_version'],
        picker_id=picker_id,
        payment_value=amount,
        state='complete',
    )

    order_items = []
    for order_item in order['order_items']:
        if 'measure_value' not in order_item:
            order_item['measure_value'] = 1
        if 'price' not in order_item:
            order_item['price'] = 10.0
        replacements = []
        if 'replacements' in order_item:
            for order_item_i in order_item['replacements']:
                replacements.append(
                    (
                        order['order_items'][order_item_i]['eats_item_id'],
                        order_items[order_item_i],
                    ),
                )
        order_item['order_id'] = order_id
        order_item.setdefault('sold_by_weight', 'measure_value' in order_item)
        order_item['replacements'] = tuple(replacements)
        order_item['relative_quantum'] = 1
        item_id = create_order_item(**order_item)
        order_items.append(item_id)

    for picked_item in order['picked_items']:
        create_picked_item_args = picked_item.copy()
        create_picked_item_args['order_item_id'] = order_items[
            picked_item['order_item']
        ]
        create_picked_item_args.setdefault('picker_id', picker_id)
        del create_picked_item_args['order_item']
        create_picked_item(**create_picked_item_args)

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
        assert request.json['service'] == 'eats-picker-orders'
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

    await stq_runner.send_order_paid_billing_event.call(
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
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        order,
        expected,
):
    eats_id = 'eats_id_0'
    picker_id = 'picker_7'
    amount = order['amount']

    order_id = create_order(
        eats_id=eats_id,
        brand_id=111,
        place_id=222,
        last_version=order['last_version'],
        picker_id=picker_id,
        payment_value=amount,
        state='complete',
    )

    order_items = []
    for order_item in order['order_items']:
        if 'measure_value' not in order_item:
            order_item['measure_value'] = 1
        if 'price' not in order_item:
            order_item['price'] = 10.0
        replacements = []
        if 'replacements' in order_item:
            for order_item_i in order_item['replacements']:
                replacements.append(
                    (
                        order['order_items'][order_item_i]['eats_item_id'],
                        order_items[order_item_i],
                    ),
                )
        order_item['order_id'] = order_id
        order_item.setdefault('sold_by_weight', 'measure_value' in order_item)
        order_item['replacements'] = tuple(replacements)
        order_item['relative_quantum'] = 1
        item_id = create_order_item(**order_item)
        order_items.append(item_id)

    for picked_item in order['picked_items']:
        create_picked_item_args = picked_item.copy()
        create_picked_item_args['order_item_id'] = order_items[
            picked_item['order_item']
        ]
        create_picked_item_args.setdefault('picker_id', picker_id)
        del create_picked_item_args['order_item']
        create_picked_item(**create_picked_item_args)

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
        assert request.json['service'] == 'eats-picker-orders'
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

    await stq_runner.send_order_paid_billing_event.call(
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
