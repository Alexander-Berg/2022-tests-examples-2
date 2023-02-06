# pylint: disable=redefined-outer-name,invalid-name
import pytest


@pytest.mark.parametrize(
    'data_path',
    [
        'success.json',
        'uber_success.json',
        'uber_roaming_success.json',
        'service_order_fields_success.json',
        'version_success.json',
        'not_found.json',
        'negative_gross_amount.json',
        'zero_gross_amount.json',
        'negative_acquiring_rate.json',
        'acquiring_rate_above_1.json',
        'operation_id_conflict.json',
        'version_conflict.json',
        'effectively_zero_net_amount.json',
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_create_compensation(
        load_py_json, web_app_client, db, stq, data_path, now,
):
    data = load_py_json(data_path)
    await _check_request(
        stq=stq,
        db=db,
        client=web_app_client,
        path='/v2/invoice/compensation/create',
        request=data['request'],
        operations_field='operations',
        processing_queue=stq.transactions_events,
        expected=data['expected'],
    )


@pytest.mark.parametrize(
    'data_path',
    [
        'success.json',
        'uber_success.json',
        'uber_roaming_success.json',
        'service_order_fields_success.json',
        'version_success.json',
        'with_gateway_name_and_pass_params_success.json',
        'not_found.json',
        'negative_gross_amount.json',
        'zero_gross_amount.json',
        'negative_acquiring_rate.json',
        'acquiring_rate_above_1.json',
        'operation_id_conflict.json',
        'version_conflict.json',
        'effectively_zero_net_amount.json',
        'bad_gateway_name.json',
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_v3_create_compensation(
        load_py_json, web_app_client, db, stq, data_path, now,
):
    data = load_py_json(data_path)
    await _check_request(
        stq=stq,
        db=db,
        client=web_app_client,
        path='/v3/invoice/compensation/create',
        request=data['request'],
        operations_field='compensation_operations',
        processing_queue=stq.transactions_plan_operation,
        expected=data['expected'],
    )


@pytest.mark.parametrize(
    'data_path',
    [
        'success.json',
        'uber_success.json',
        'uber_roaming_success.json',
        'version_success.json',
        'not_found.json',
        'negative_net_amount.json',
        'zero_net_amount.json',
        'operation_id_conflict.json',
        'version_conflict.json',
        'effectively_zero_net_amount.json',
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_refund_compensation(
        load_py_json, web_app_client, db, stq, data_path, now,
):
    data = load_py_json(data_path)
    await _check_request(
        stq=stq,
        db=db,
        client=web_app_client,
        path='/v2/invoice/compensation/refund',
        request=data['request'],
        operations_field='operations',
        processing_queue=stq.transactions_events,
        expected=data['expected'],
    )


@pytest.mark.parametrize(
    'data_path',
    [
        'success.json',
        'uber_success.json',
        'uber_roaming_success.json',
        'version_success.json',
        'not_found.json',
        'negative_net_amount.json',
        'zero_net_amount.json',
        'operation_id_conflict.json',
        'version_conflict.json',
        'effectively_zero_net_amount.json',
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_v3_refund_compensation(
        load_py_json, web_app_client, db, stq, data_path, now,
):
    data = load_py_json(data_path)
    await _check_request(
        stq=stq,
        db=db,
        client=web_app_client,
        path='/v3/invoice/compensation/refund',
        request=data['request'],
        operations_field='compensation_operations',
        processing_queue=stq.transactions_plan_operation,
        expected=data['expected'],
    )


@pytest.mark.parametrize('api_version', ['v3'])
@pytest.mark.now('2020-01-01T00:00:00')
async def test_compensation_in_ng(
        load_py_json, ng_web_app_client, db, stq, now, api_version,
):
    invoice_id = 'ng-invoice'
    response = await ng_web_app_client.post(
        path=f'/{api_version}/invoice/compensation/create',
        json={
            'acquiring_rate': '0.02',
            'gross_amount': '100.00',
            'invoice_id': invoice_id,
            'operation_id': 'compensation',
            'originator': 'processing',
        },
    )
    assert response.status == 200
    response = await ng_web_app_client.post(
        path=f'/{api_version}/invoice/compensation/refund',
        json={
            'invoice_id': invoice_id,
            'net_amount': '100.00',
            'operation_id': 'compensation-refund',
            'originator': 'processing',
            'trust_payment_id': 'some-trust-payment-id',
        },
    )
    assert response.status == 200


@pytest.mark.parametrize('api_version', ['v2', 'v3'])
@pytest.mark.now('2020-01-01T00:00:00')
async def test_no_compensation_in_eda(
        load_py_json, eda_web_app_client, db, stq, now, api_version,
):
    invoice_id = 'eda-invoice'
    response = await eda_web_app_client.post(
        path=f'/{api_version}/invoice/compensation/create',
        json={
            'acquiring_rate': '0.02',
            'gross_amount': '100.00',
            'invoice_id': invoice_id,
            'operation_id': 'compensation',
            'originator': 'processing',
        },
    )
    assert response.status == 400
    response = await eda_web_app_client.post(
        path=f'/{api_version}/invoice/compensation/refund',
        json={
            'invoice_id': invoice_id,
            'net_amount': '100.00',
            'operation_id': 'compensation-refund',
            'originator': 'processing',
            'trust_payment_id': 'some-trust-payment-id',
        },
    )
    assert response.status == 400


async def _check_request(
        stq,
        db,
        client,
        path,
        request,
        operations_field,
        processing_queue,
        expected,
):
    # Second response must be the same
    NUM_ATTEMPTS = 2
    for _ in range(NUM_ATTEMPTS):
        with stq.flushing():
            response = await client.post(path, json=request)
            assert response.status == expected['response']['status']
            content = await response.json()
            assert content == expected['response']['content']
            if expected['response']['status'] == 200:
                invoice_id = request['invoice_id']
                order = await db.orders.find_one(invoice_id)
                assert (
                    order['invoice_request'][operations_field]
                    == expected['operations']
                )
                assert processing_queue.times_called == expected['num_calls']
                assert (
                    processing_queue.next_call()['id'] == expected['task_id']
                )
