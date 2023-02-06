import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.parametrize(
    'park_id, contractor_id, merchant_id, payment_id',
    [
        pytest.param(
            'park-id-1', 'contractor-id-1', 'merchant_id-2', 'payment_id-3',
        ),
    ],
)
async def test_payment_approval(
        taxi_contractor_merch_payments,
        stq,
        park_id,
        contractor_id,
        merchant_id,
        payment_id,
):
    query = {'payment_id': payment_id}

    response = await taxi_contractor_merch_payments.put(
        '/driver/v1/contractor-merch-payments/payment/approval',
        params=query,
        headers=utils.get_headers(
            park_id=park_id, driver_profile_id=contractor_id,
        ),
    )

    assert response.status == 200
    assert response.json() == {}

    assert stq.contractor_merch_payments_payment_process.has_calls

    task = stq.contractor_merch_payments_payment_process.next_call()
    assert task['id'] == f'{park_id}_{contractor_id}_{payment_id}'
    assert task['args'] == []

    kwargs_asserts = {
        'action_type': 'approve',
        'park_id': park_id,
        'contractor_id': contractor_id,
        'payment_id': payment_id,
        'payment_method': 'with_approval',
    }

    task['kwargs'].pop('log_extra')
    assert task['kwargs'] == kwargs_asserts
