import decimal

import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.parametrize(
    'payment_id', ['payment_id-target_success', 'payment_id-success'],
)
async def test_ok(taxi_contractor_merch_payments, stq, pgsql, payment_id):
    idempotency_token = 'idemp1000000000000000000000000000'

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/refund',
        params={'payment_id': payment_id, 'merchant_id': 'merchant-id-2'},
        headers={'X-Idempotency-Token': idempotency_token},
        json={
            'currency': 'RUB',
            'amount': '40',
            'metadata': {'mobi_id': '123'},
        },
    )

    assert response.status == 200

    id_created_at = utils.get_transaction_by_idempotency(
        pgsql, idempotency_token, 'id, created_at',
    )

    assert utils.date_parsed(response.json()) == utils.date_parsed(
        {
            'id': id_created_at['id'],
            'currency': 'RUB',
            'amount': '40',
            'metadata': {'mobi_id': '123'},
            'created_at': id_created_at['created_at'],
        },
    )

    assert stq.contractor_merch_payments_refund.has_calls
    task = stq.contractor_merch_payments_refund.next_call()
    assert task['args'] == []
    kwargs = task['kwargs']
    kwargs.pop('log_extra')
    assert kwargs == {
        'transaction_id': id_created_at['id'],
        'payment_id': payment_id,
    }

    refund = utils.get_transaction_by_idempotency(
        pgsql,
        idempotency_token,
        'idempotency_token, payment_id, metadata, amount, type',
    )
    assert refund == {
        'amount': decimal.Decimal('-40.0000'),
        'idempotency_token': 'idemp1000000000000000000000000000',
        'metadata': {'mobi_id': '123'},
        'payment_id': payment_id,
        'type': 'yandex_subsidy_refund',
    }


async def test_full_refund(taxi_contractor_merch_payments, stq, pgsql):
    idempotency_token = 'idemp1000000000000000000000000000'

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/refund',
        params={
            'payment_id': 'payment_id-success',
            'merchant_id': 'merchant-id-2',
        },
        headers={'X-Idempotency-Token': idempotency_token},
        json={'metadata': {'mobi_id': '123'}},
    )

    assert response.status == 200

    id_created_at = utils.get_transaction_by_idempotency(
        pgsql, idempotency_token, 'id, created_at',
    )

    assert utils.date_parsed(response.json()) == utils.date_parsed(
        {
            'id': id_created_at['id'],
            'currency': 'RUB',
            'amount': '40',
            'metadata': {'mobi_id': '123'},
            'created_at': id_created_at['created_at'],
        },
    )


async def test_retry(taxi_contractor_merch_payments, stq):
    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/refund',
        params={
            'payment_id': 'payment_id-target_success',
            'merchant_id': 'merchant-id-2',
        },
        headers={'X-Idempotency-Token': 'idempotency_token-0123456789'},
        json={
            'currency': 'RUB',
            'amount': '30',
            'metadata': {'mobi_id': '123'},
        },
    )

    assert response.status == 200
    assert utils.date_parsed(response.json()) == utils.date_parsed(
        {
            'id': 'refund-id',
            'currency': 'RUB',
            'amount': '10',
            'metadata': {'mobi_id': '123'},
            'created_at': '2021-07-01T14:00:00+00:00',
        },
    )
    assert not stq.contractor_merch_payments_refund.has_calls


@pytest.mark.parametrize(
    'payment_id, merchant_id, request_body, expected_code, expected_response',
    [
        pytest.param(
            'some-payment',
            'merchant-id-2',
            None,
            404,
            {'code': 'payment_not_found', 'message': 'payment_not_found'},
            id='payment not found',
        ),
        pytest.param(
            'payment_id-success',
            'merchant-id-invalid',
            None,
            404,
            {'code': 'payment_not_found', 'message': 'payment_not_found'},
            id='invalid merchant',
        ),
        pytest.param(
            'payment_id-draft',
            'merchant-id-2',
            None,
            409,
            {
                'code': 'invalid_payment_status',
                'message': 'invalid_payment_status',
            },
            id='invalid payment status',
        ),
        pytest.param(
            'payment_id-success',
            'merchant-id-2',
            {'currency': 'USD', 'amount': '10'},
            400,
            {'code': 'invalid_currency', 'message': 'invalid_currency'},
            id='invalid_currency',
        ),
        pytest.param(
            'payment_id-success',
            'merchant-id-2',
            {'currency': 'rub', 'amount': '0'},
            400,
            {'code': 'invalid_amount', 'message': 'invalid_amount'},
            id='invalid_currency',
        ),
        pytest.param(
            'payment_id-success',
            'merchant-id-2',
            {'currency': 'rub', 'amount': '41'},
            400,
            {
                'code': 'cannot_refund_more_than_paid',
                'message': 'cannot_refund_more_than_paid',
            },
            id='cannot_refund_more_than_paid one refund',
        ),
        pytest.param(
            'payment_id-target_success',
            'merchant-id-2',
            {'currency': 'rub', 'amount': '41'},
            400,
            {
                'code': 'cannot_refund_more_than_paid',
                'message': 'cannot_refund_more_than_paid',
            },
            id='cannot_refund_more_than_paid two refunds',
        ),
        pytest.param(
            'payment_id-target_success',
            'merchant-id-2',
            {},
            400,
            {
                'code': 'cannot_refund_more_than_paid',
                'message': 'cannot_refund_more_than_paid',
            },
            id='cannot make full refund when has refunds',
        ),
        pytest.param(
            'payment_id-target_success',
            'merchant-id-2',
            {'currency': 'rub', 'amount': '1'},
            400,
            {'code': 'too_many_refunds', 'message': 'too_many_refunds'},
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_MAX_REASONABLE_REFUNDS=1,
            ),
            id='too many refunds',
        ),
        pytest.param(
            'payment_id-target_success',
            'merchant-id-2',
            {'amount': '1'},
            400,
            {
                'code': (
                    'amount_and_currency_should_be_provided_simultaneously'
                ),
                'message': (
                    'amount_and_currency_should_be_provided_simultaneously'
                ),
            },
            id='amount_and_currency_should_be_provided_simultaneously',
        ),
        pytest.param(
            'payment_id-target_success',
            'merchant-id-2',
            {'currency': 'rub'},
            400,
            {
                'code': (
                    'amount_and_currency_should_be_provided_simultaneously'
                ),
                'message': (
                    'amount_and_currency_should_be_provided_simultaneously'
                ),
            },
            id='amount_and_currency_should_be_provided_simultaneously',
        ),
    ],
)
async def test_not_found_and_invalid_status(
        taxi_contractor_merch_payments,
        payment_id,
        merchant_id,
        request_body,
        expected_code,
        expected_response,
):
    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/refund',
        params={'payment_id': payment_id, 'merchant_id': merchant_id},
        headers={'X-Idempotency-Token': 'idemp1000000000000000000000000000'},
        json=request_body
        if request_body is not None
        else {'currency': 'RUB', 'amount': '10'},
    )

    assert response.status == expected_code
    assert response.json() == expected_response


async def test_stq_call_failed(
        taxi_contractor_merch_payments, mockserver, pgsql,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_queue(request, queue_name):
        return mockserver.make_response(status=500)

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/refund',
        params={
            'payment_id': 'payment_id-success',
            'merchant_id': 'merchant-id-2',
        },
        headers={'X-Idempotency-Token': 'idemp1000000000000000000000000000'},
        json={'currency': 'RUB', 'amount': '10'},
    )

    assert _mock_stq_queue.times_called >= 1
    assert response.status == 500
    assert not utils.get_transactions_by_payment_id(
        pgsql, 'payment_id-success', 'id',
    )
