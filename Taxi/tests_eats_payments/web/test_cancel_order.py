import typing

import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers

URL = 'v1/orders/cancel'

NOW = '2020-08-12T07:20:00+00:00'

BASE_PAYLOAD = {'id': 'test_order', 'version': 2, 'revision': 'abcd'}


@pytest.fixture(name='mock_transactions_invoice_clear')
def _mock_transactions_invoice_clear(mockserver):
    def _inner(invoice_clear_response=None):
        @mockserver.json_handler('/transactions-eda/invoice/clear')
        def _transactions_clear_invoice_handler(request):
            if invoice_clear_response is not None:
                return mockserver.make_response(**invoice_clear_response)

            assert request.json == {'id': 'test_order', 'clear_eta': NOW}
            return {}

        return _transactions_clear_invoice_handler

    return _inner


@pytest.fixture(name='check_cancel_order')
def _check_cancel_order(upsert_order, taxi_eats_payments):
    async def _inner(
            response_status: int = 200,
            response_body: typing.Optional[dict] = None,
            order_id: str = 'test_order',
    ):
        upsert_order(order_id)
        response = await taxi_eats_payments.post(URL, json=BASE_PAYLOAD)
        assert response.status == response_status
        response_body = response_body or {}
        assert response.json() == response_body

    return _inner


@pytest.mark.now(NOW)
async def test_ok(
        check_cancel_order,
        mock_transactions_invoice_update,
        mock_transactions_invoice_clear,
        mock_transactions_invoice_retrieve,
):
    mock_transactions_invoice_retrieve()
    invoice_update_mock = mock_transactions_invoice_update(
        items=[], operation_id='cancel:abcd',
    )
    invoice_clear_mock = mock_transactions_invoice_clear()
    await check_cancel_order()
    assert invoice_update_mock.times_called == 1
    assert invoice_clear_mock.times_called == 1


async def test_cancel_cash(
        upsert_order,
        upsert_order_payment,
        insert_operation,
        taxi_eats_payments,
        experiments3,
        fetch_operation,
        stq,
):
    order_id = 'test_order'
    payment_type = consts.CASH_PAYMENT_TYPE
    payment_method_id = 'cash_test_id'
    previous_revision = 'ab'
    revision = 'cd'

    experiments3.add_config(**helpers.make_operations_config())

    upsert_order(order_id=order_id, api_version=2)
    upsert_order_payment(
        order_id=order_id,
        payment_id=payment_method_id,
        payment_type=payment_type,
    )
    insert_operation(
        order_id=order_id,
        revision=previous_revision,
        prev_revision=previous_revision,
        op_type='create',
        status='done',
        fails_count=0,
    )

    response = await taxi_eats_payments.post(
        URL, json={'id': order_id, 'version': 2, 'revision': revision},
    )
    assert response.status == 200
    assert response.json() == {}

    fetch_operation(order_id, revision, prev_revision=revision)

    helpers.check_callback_mock(
        callback_mock=stq.eda_order_processing_payment_events_callback,
        times_called=1,
        task_id='test_order:cancel:cd:done:operation_finish',
        queue='eda_order_processing_payment_events_callback',
        **{
            'order_id': order_id,
            'action': 'cancel',
            'status': 'confirmed',
            'revision': revision,
        },
    )


@pytest.mark.parametrize(
    ('invoice_update_response,' 'response_status,' 'response_body'),
    [
        (
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': 'something wrong was sent',
                },
            },
            400,
            {
                'code': 'bad-request',
                'message': (
                    'Transactions error while updating canceled invoice. '
                    'Error: `something wrong was sent`'
                ),
            },
        ),
        (
            {'status': 404, 'json': {}},
            404,
            {
                'code': 'invoice-not-found',
                'message': (
                    'Transactions error while updating canceled invoice. '
                    'Error: `invoice not found`'
                ),
            },
        ),
        (
            {
                'status': 409,
                'json': {'code': 'conflict', 'message': 'conflict happened'},
            },
            409,
            {
                'code': 'conflict',
                'message': (
                    'Transactions error while updating canceled invoice. '
                    'Error: `conflict happened`'
                ),
            },
        ),
        (
            {
                'status': 500,
                'json': {
                    'code': 'internal-server-error',
                    'message': 'exception',
                },
            },
            500,
            {
                'code': 'unknown-error',
                'message': (
                    'Transactions error while updating canceled invoice. '
                    'Error: `Unexpected HTTP response code '
                    '\'500\' for \'POST /v2/invoice/update\'`'
                ),
            },
        ),
    ],
)
async def test_update_errors(
        check_cancel_order,
        mock_transactions_invoice_update,
        mock_transactions_invoice_clear,
        mock_transactions_invoice_retrieve,
        invoice_update_response,
        response_status,
        response_body,
):
    mock_transactions_invoice_retrieve()
    invoice_update_mock = mock_transactions_invoice_update(
        invoice_update_response=invoice_update_response,
    )
    invoice_clear_mock = mock_transactions_invoice_clear()
    await check_cancel_order(
        response_status=response_status, response_body=response_body,
    )
    assert invoice_update_mock.times_called == 1
    assert invoice_clear_mock.times_called == 0


@pytest.mark.parametrize(
    ('invoice_clear_response,' 'response_status,' 'response_body'),
    [
        (
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': 'something wrong was sent',
                },
            },
            400,
            {
                'code': 'bad-request',
                'message': (
                    'Transactions error while clearing canceled invoice. '
                    'Error: `something wrong was sent`'
                ),
            },
        ),
        (
            {'status': 404, 'json': {}},
            404,
            {
                'code': 'invoice-not-found',
                'message': (
                    'Transactions error while clearing canceled invoice. '
                    'Error: `invoice not found`'
                ),
            },
        ),
        (
            {
                'status': 409,
                'json': {'code': 'conflict', 'message': 'conflict happened'},
            },
            409,
            {
                'code': 'conflict',
                'message': (
                    'Transactions error while clearing canceled invoice. '
                    'Error: `conflict happened`'
                ),
            },
        ),
        (
            {
                'status': 500,
                'json': {
                    'code': 'internal-server-error',
                    'message': 'exception',
                },
            },
            500,
            {
                'code': 'unknown-error',
                'message': (
                    'Transactions error while clearing canceled invoice. '
                    'Error: `Unexpected HTTP response code '
                    '\'500\' for \'POST /invoice/clear\'`'
                ),
            },
        ),
    ],
)
async def test_clear_errors(
        check_cancel_order,
        mock_transactions_invoice_update,
        mock_transactions_invoice_clear,
        mock_transactions_invoice_retrieve,
        invoice_clear_response,
        response_status,
        response_body,
):
    mock_transactions_invoice_retrieve()
    invoice_update_mock = mock_transactions_invoice_update(
        items=[], operation_id='cancel:abcd',
    )
    invoice_clear_mock = mock_transactions_invoice_clear(
        invoice_clear_response=invoice_clear_response,
    )
    await check_cancel_order(
        response_status=response_status, response_body=response_body,
    )
    assert invoice_update_mock.times_called == 1
    assert invoice_clear_mock.times_called == 1


@pytest.mark.now(NOW)
async def test_order_not_found(
        check_cancel_order,
        mock_transactions_invoice_update,
        mock_transactions_invoice_clear,
        mock_transactions_invoice_retrieve,
):
    mock_transactions_invoice_retrieve()
    mock_transactions_invoice_update(items=[], operation_id='cancel:abcd')
    mock_transactions_invoice_clear()
    await check_cancel_order(
        response_status=404,
        response_body={
            'code': 'unknown-error',
            'message': (
                'Error while cancelling order. ' 'Error: `order_id not found`'
            ),
        },
        order_id='non_existing_order_id',
    )


@pytest.mark.now(NOW)
async def test_mark_cancelled(
        check_cancel_order,
        mock_transactions_invoice_update,
        mock_transactions_invoice_clear,
        mock_transactions_invoice_retrieve,
        assert_db_order,
):
    mock_transactions_invoice_retrieve()
    mock_transactions_invoice_update(items=[], operation_id='cancel:abcd')
    mock_transactions_invoice_clear()
    await check_cancel_order()
    assert_db_order('test_order', expected_cancelled=True)
