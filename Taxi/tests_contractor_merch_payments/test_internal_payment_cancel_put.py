import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.parametrize(
    ['payment_id', 'status_before'],
    [
        pytest.param(
            'payment_id-merchant_accepted',
            'merchant_approved',
            id='can_cancel (merchant_accepted)',
        ),
        pytest.param(
            'payment_id-merchant_canceled',
            'merchant_canceled',
            id='can_cancel (merchant_canceled)',
        ),
    ],
)
async def test_merchant_can_cancel_statuses(
        taxi_contractor_merch_payments, pgsql, payment_id, status_before,
):
    (merchant_id,) = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['merchant_id'],
    )

    response = await taxi_contractor_merch_payments.put(
        '/internal/contractor-merch-payments/v1/payment/cancel',
        params={'payment_id': payment_id, 'merchant_id': merchant_id},
        json={},
    )

    assert response.status == 200
    assert response.json() == {'status_before': status_before}

    (status,) = utils.get_fields_by_payment_id(pgsql, payment_id, ['status'])
    assert status == 'merchant_canceled'


async def test_cancel_draft(taxi_contractor_merch_payments, pgsql):
    payment_id = 'payment_id-draft'
    merchant_id = 'merchant_id-draft'

    response = await taxi_contractor_merch_payments.put(
        '/internal/contractor-merch-payments/v1/payment/cancel',
        params={'payment_id': payment_id, 'merchant_id': merchant_id},
        json={},
    )

    assert response.status == 200
    assert response.json() == {'status_before': 'pending_merchant_approve'}

    db_merchant_id, status = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['merchant_id', 'status'],
    )
    assert db_merchant_id == merchant_id
    assert status == 'merchant_canceled'


@pytest.mark.parametrize(
    ['payment_id', 'status_before'],
    [
        pytest.param(
            'payment_id-target_success',
            'payment_passed',
            id='cannot_cancel (target_success)',
        ),
        pytest.param(
            'payment_id-target_failed',
            'payment_failed',
            id='cannot_cancel (target_failed)',
        ),
        pytest.param(
            'payment_id-target_contractor_declined',
            'contractor_declined',
            id='cannot_cancel (target_contractor_declined)',
        ),
        pytest.param(
            'payment_id-success',
            'payment_passed',
            id='cannot_cancel (success)',
        ),
        pytest.param(
            'payment_id-failed', 'payment_failed', id='cannot_cancel (failed)',
        ),
        pytest.param(
            'payment_id-contractor_declined',
            'contractor_declined',
            id='cannot_cancel (contractor_declined)',
        ),
    ],
)
async def test_merchant_cannot_cancel_statuses(
        taxi_contractor_merch_payments, pgsql, payment_id, status_before,
):
    (merchant_id,) = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['merchant_id'],
    )

    response = await taxi_contractor_merch_payments.put(
        '/internal/contractor-merch-payments/v1/payment/cancel',
        params={'payment_id': payment_id, 'merchant_id': merchant_id},
        json={},
    )

    assert response.status == 409
    assert response.json() == {
        'code': 'merchant_cannot_cancel',
        'message': 'Payment is in a state when merchant cannot cancel',
        'status_before': status_before,
    }


@pytest.mark.parametrize(
    ['payment_id', 'merchant_id', 'status', 'response_body'],
    [
        pytest.param(
            'payment_id-100',
            'merchant_id-100',
            404,
            {'code': 'payment_not_found', 'message': 'Payment not found'},
            id='payment not found',
        ),
        pytest.param(
            'payment_id-merchant_accepted',
            'merchant-id-10',
            404,
            {'code': 'invalid_merchant_id', 'message': 'Invalid merchant id'},
            id='invalid merchant id',
        ),
    ],
)
async def test_incorrect_cancel_put(
        taxi_contractor_merch_payments,
        payment_id,
        merchant_id,
        status,
        response_body,
):
    response = await taxi_contractor_merch_payments.put(
        '/internal/contractor-merch-payments/v1/payment/cancel',
        params={'payment_id': payment_id, 'merchant_id': merchant_id},
        json={},
    )

    assert response.status == status
    assert response.json() == response_body
