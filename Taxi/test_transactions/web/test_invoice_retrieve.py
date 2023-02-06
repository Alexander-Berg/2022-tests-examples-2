from typing import Iterable

import pytest

from test_transactions import helpers
# pylint: disable=redefined-outer-name,invalid-name


@pytest.mark.parametrize(
    'request_path', ['/invoice/retrieve', '/v2/invoice/retrieve'],
)
async def test_invoice_get_not_found(web_app_client, db, request_path):
    body = {'id': 'not-found'}
    response = await web_app_client.post(request_path, json=body)
    assert response.status == 404
    content = await response.json()
    assert content == {'code': 'not-found', 'message': 'Invoice not found'}


@pytest.mark.parametrize(
    'data_path',
    [
        'test_invoice_basic_init/v1_single_payment_invoice_data.json',
        'test_invoice_basic_init/v2_single_payment_invoice_data.json',
        'test_invoice_basic_init/v2_merchant_id.json',
        (
            'test_invoice_basic_init/'
            'v2_single_payment_price_and_quantity_invoice_data.json'
        ),
        'test_invoice_basic_init/v1_multi_payment_invoice_data.json',
        'test_invoice_basic_init/v2_multi_payment_invoice_data.json',
        (
            'test_invoice_basic_init/'
            'v2_multi_payment_price_and_quantity_invoice_data.json'
        ),
        'test_invoice_basic_hold_done/v1_single_payment_invoice_data.json',
        'test_invoice_basic_hold_done/v2_single_payment_invoice_data.json',
        'test_invoice_basic_hold_done/v1_multi_payment_invoice_data.json',
        'test_invoice_basic_hold_done/v2_multi_payment_invoice_data.json',
        pytest.param(
            (
                'test_invoice_basic_hold_done/'
                'v2_multi_payment_held_cleared_invoice_data.json'
            ),
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_CLEARED_IS_HELD_IN_STATUS=True,
                ),
            ],
        ),
        (
            'test_invoice_basic_hold_done/'
            'v2_multi_payment_held_cleared_disabled_config_invoice_data.json'
        ),
        'test_invoice_basic_clear_done/v1_single_payment_invoice_data.json',
        'test_invoice_basic_clear_done/v2_single_payment_invoice_data.json',
        'test_invoice_basic_clear_done/v1_multi_payment_invoice_data.json',
        'test_invoice_basic_clear_done/v2_multi_payment_invoice_data.json',
        'test_invoice_basic_clear_failed/v1_single_payment_invoice_data.json',
        'test_invoice_basic_clear_failed/v2_single_payment_invoice_data.json',
        'test_invoice_basic_clear_failed/v1_multi_payment_invoice_data.json',
        'test_invoice_basic_clear_failed/v2_multi_payment_invoice_data.json',
        'test_invoice_unhold_statuses/v1_data.json',
        'test_invoice_unhold_statuses/v2_data.json',
    ],
)
async def test_invoice_basic_cases(
        load_py_json, web_app_client, db, data_path,
):
    data = load_py_json(data_path)
    body = {'id': data['invoice_id']}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content == data['expected_response']


@pytest.mark.config(TRANSACTIONS_ARCHIVE_ENABLED={'taxi': 1, '__default__': 0})
@pytest.mark.parametrize(
    'data_path',
    [
        pytest.param(
            'test_invoice_archive/v2_archive_invoice_data.json',
            id='it should return invoice from archive',
        ),
    ],
)
async def test_invoice_archive(
        patch, load_py_json, web_app_client, db, data_path,
):
    data = load_py_json(data_path)
    fetch_invoice = helpers.patch_fetch_invoice(
        patch, data['fetch_invoice_result'],
    )
    body = {'id': data['invoice_id']}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content == data['expected_response']
    assert len(fetch_invoice.calls) == 1


@pytest.mark.parametrize(
    'data_path',
    [
        'v1_no_invoice_rub.json',
        'v1_no_invoice_usd.json',
        'v2_no_invoice_rub.json',
        'v2_no_invoice_usd.json',
    ],
)
async def test_invoice_no_invoice_request(
        load_py_json, web_app_client, db, data_path,
):
    data = load_py_json(data_path)
    body = {'id': data['invoice_id']}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content['debt'] == data['expected']['debt']
    assert content['currency'] == data['expected']['currency']


@pytest.mark.parametrize(
    'data_path',
    [
        'test_invoice_cash/v1_data.json',
        'test_invoice_cash/v2_data.json',
        'test_invoice_coop/v1_data.json',
        'test_invoice_coop/v2_data.json',
        'test_invoice_corp/v1_data.json',
        'test_invoice_corp/v2_data.json',
        'test_invoice_prepaid/v1_data.json',
        'test_invoice_prepaid/v2_data.json',
    ],
)
async def test_old_order_cases(load_py_json, web_app_client, db, data_path):
    data = load_py_json(data_path)
    body = {'id': data['invoice_id']}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content == data['expected_response']


@pytest.mark.parametrize(
    'data_path',
    [
        # expect data from order
        'migrated_order_v1.json',
        # expect data from order and no transactions_ready
        'migrated_order_v2_no_flag.json',
        # expect data from transactions and transactions_ready=true
        'migrated_order_v2_with_flag.json',
        'no_payments_migrated_order_v2_with_flag.json',
        # expect data from order and no transactions_ready
        'order_not_migrated_v2_no_flag.json',
        # expect data from order and transactions_ready=false
        'order_not_migrated_v2_with_flag.json',
        # expect data from order and transactions_ready=false
        'agent_order_not_migrated_v1.json',
        # expect data from order and transactions_ready=false
        'agent_order_not_migrated_v2_with_flag.json',
        # expect data from order and no transactions_ready
        'agent_order_not_migrated_v2_no_flag.json',
        # expect data from order and transactions_ready=false
        'agent_order_not_migrated_v2_with_flag.json',
    ],
)
@pytest.mark.filldb(orders='for_test_transactions_data')
async def test_transactions_data(load_py_json, web_app_client, db, data_path):
    data = load_py_json(data_path)
    body = data['request']['body']
    response = await web_app_client.post(data['request']['path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content == data['expected_response']


@pytest.mark.parametrize('data_path', ['v1_data.json', 'v2_data.json'])
async def test_transactions_refunds(load_py_json, web_app_client, data_path):
    data = load_py_json(data_path)
    body = {'id': 'order-no-invoice-rub'}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content['transactions'] == data['expected']['transactions']


@pytest.mark.parametrize('data_path', ['v2_data.json'])
async def test_receipts(load_py_json, web_app_client, data_path):
    data = load_py_json(data_path)
    body = {'id': 'order-no-invoice-rub-receipts'}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content['transactions'] == data['expected']['transactions']


@pytest.mark.parametrize('data_path', ['v2_data.json'])
async def test_operations_items_fiscal_receipt_info(
        load_py_json, web_app_client, data_path,
):
    data = load_py_json(data_path)
    body = {'id': 'my-order-fiscal-receipt-info'}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content['operations'] == data['expected']['operations']


@pytest.mark.parametrize('data_path', ['v1_data.json', 'v2_data.json'])
async def test_old_transaction(load_py_json, web_app_client, data_path):
    data = load_py_json(data_path)
    body = {'id': 'order-old-transaction'}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()
    assert content == data['expected_response']


@pytest.mark.parametrize(
    'request_path', ['/invoice/retrieve', '/v2/invoice/retrieve'],
)
async def test_invoice_with_extra_request_fields(web_app_client, request_path):
    await _check_extra_request_fields(
        web_app_client,
        request_path,
        extra_fields={
            'service': 'eda',
            'external_user_info': {'user_id': 'abc', 'origin': 'taxi'},
        },
    )


async def test_invoice_with_mcc(web_app_client):
    await _check_extra_request_fields(
        web_app_client,
        request_path='/v2/invoice/retrieve',
        extra_fields={'mcc': 1234},
    )


async def test_invoice_with_login_id(web_app_client):
    await _check_extra_request_fields(
        web_app_client,
        request_path='/v2/invoice/retrieve',
        extra_fields={'login_id': 'some_login_id'},
    )


async def test_invoice_with_disable_automatic_composite_refund(web_app_client):
    await _check_extra_request_fields(
        web_app_client,
        request_path='/v2/invoice/retrieve',
        extra_fields={'disable_automatic_composite_refund': True},
    )


async def test_invoice_with_personal_fields(web_app_client):
    await _check_extra_request_fields(
        web_app_client,
        request_path='/v2/invoice/retrieve',
        extra_fields={
            'personal_phone_id': 'personal-phone-id',
            'personal_email_id': 'personal-email-id',
        },
    )


async def test_invoice_with_is_processing_halted(web_app_client):
    await _check_extra_request_fields(
        web_app_client,
        request_path='/v2/invoice/retrieve',
        extra_fields={'is_processing_halted': True},
    )


@pytest.mark.parametrize('data_path', ['v2_data.json'])
async def test_new_fields(load_py_json, web_app_client, data_path):
    data = load_py_json(data_path)
    body = {'id': 'with_new_fields'}
    response = await web_app_client.post(data['request_path'], json=body)
    assert response.status == 200
    content = await response.json()

    assert_issubset(data['expected'], content)


async def test_negative_transaction_amounts(eda_web_app_client, load_py_json):
    data = load_py_json('expected_data.json')
    response = await eda_web_app_client.post(
        '/v2/invoice/retrieve', json={'id': 'with-negative-transactions'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == data['expected_response']


@pytest.mark.parametrize(
    'data_path',
    ['init.json', 'success.json', 'failed.json', 'in-progress.json'],
)
async def test_cashback(web_app_client, load_py_json, data_path):
    data = load_py_json(data_path)
    response = await web_app_client.post(
        '/v2/invoice/retrieve', json={'id': data['id']},
    )
    assert response.status == 200
    content = await response.json()
    assert content == data['expected_response']


@pytest.mark.config(
    TRANSACTIONS_REFUND_ATTEMPTS_MINUTES_BY_SCOPE={
        '__default__': 1_000_000_000,
        'taxi': 120,
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-09-10T00:00:00')
@pytest.mark.parametrize(
    'data_path',
    [
        # expect true
        'no_invoice_request.json',
        # expect true
        'no_ops.json',
        # expect true
        'no_update_ops.json',
        # expect true
        'no_update_ops_with_created.json',
        # expect true
        'no_failed_refunds_after_last_op.json',
        # expect true
        'attempts_delay_not_exceeded.json',
        # expect false
        'attempts_delay_exceeded.json',
    ],
)
@pytest.mark.filldb(orders='for_test_is_refundable')
async def test_is_refundable(load_py_json, web_app_client, db, data_path):
    data = load_py_json(data_path)
    response = await web_app_client.post(
        '/v2/invoice/retrieve', json={'id': data['id']},
    )
    assert response.status == 200
    content = await response.json()
    assert content['is_refundable'] == data['expected_is_refundable']


async def test_operations_and_transactions_have_transaction_payload(
        load_py_json, web_app_client, db,
):
    data = load_py_json('order_with_transaction_payload.json')
    response = await web_app_client.post(
        data['request_path'], json={'id': data['invoice_id']},
    )
    assert response.status == 200
    content = await response.json()
    assert content == data['expected_response']


def assert_issubset(what, where):
    for key in what:
        assert key in where, f'{key} is missing'
        if isinstance(what[key], dict):
            assert isinstance(what[key], dict), f'{key} is not dict'
            assert_issubset(what[key], where[key])
        elif isiterable(what[key]):
            assert isiterable(where[key]), f'{key} is not iterable'
            for what_i, where_i in zip(what[key], where[key]):
                assert_issubset(what_i, where_i)
        else:
            assert what[key] == where[key]


def isiterable(what) -> bool:
    return isinstance(what, Iterable) and not isinstance(what, str)


async def _check_extra_request_fields(
        web_app_client, request_path, extra_fields,
):
    response = await web_app_client.post(
        request_path, json={'id': 'my-order-with-extra-request-fields'},
    )
    assert response.status == 200
    content = await response.json()
    for field, value in extra_fields.items():
        assert content[field] == value


async def test_v2_invoice_retrieve_intent(web_app_client, db):
    request = {'id': 'my-order-operation-with-intent'}
    response = await web_app_client.post('v2/invoice/retrieve', json=request)
    assert response.status == 200
    content = await response.json()
    assert content['operations'][0]['intent'] == 'geese'
