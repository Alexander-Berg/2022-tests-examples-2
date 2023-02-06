import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.parametrize(
    'payment_id, expected_response',
    [
        pytest.param(
            'payment_id-target_success',
            {
                'refunds': [
                    {
                        'amount': '10',
                        'created_at': '2021-07-01T14:00:00+00:00',
                        'currency': 'RUB',
                        'id': 'refund-id',
                        'metadata': {'mobi_id': '123'},
                    },
                ],
            },
            id='has refunds',
        ),
        pytest.param('payment_id-success', {'refunds': []}, id='no refunds'),
        pytest.param(
            'payment_id-merchant_accepted',
            {'refunds': []},
            id='not payment passed',
        ),
    ],
)
async def test_ok(
        taxi_contractor_merch_payments, payment_id, expected_response,
):
    response = await taxi_contractor_merch_payments.get(
        '/internal/contractor-merch-payments/v1/payment/refunds',
        params={'payment_id': payment_id, 'merchant_id': 'merchant-id-2'},
    )

    assert response.status == 200
    assert utils.date_parsed(response.json()) == utils.date_parsed(
        expected_response,
    )


@pytest.mark.parametrize(
    'payment_id, merchant_id',
    [
        pytest.param(
            'payment_id-invalid', 'merchant-id-2', id='invalid payment_id',
        ),
        pytest.param(
            'payment_id-success',
            'merchant-id-invalid',
            id='invalid merchant_id(success status)',
        ),
        pytest.param(
            'payment_id-merchant_accepted',
            'merchant-id-invalid',
            id='invalid merchant_id(merchant_accepted status)',
        ),
    ],
)
async def test_404(taxi_contractor_merch_payments, payment_id, merchant_id):
    response = await taxi_contractor_merch_payments.get(
        '/internal/contractor-merch-payments/v1/payment/refunds',
        params={'payment_id': payment_id, 'merchant_id': merchant_id},
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'payment_not_found',
        'message': 'payment_not_found',
    }
