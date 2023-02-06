import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.parametrize(
    ['payment_id'],
    [
        pytest.param('payment_id-success-0'),
        pytest.param('payment_id-success-1'),
        pytest.param('payment_id-success-2'),
        pytest.param('payment_id-merchant_canceled'),
        pytest.param('payment_id-failed'),
    ],
)
async def test_completed_payments(
        taxi_contractor_merch_payments,
        mock_merchant_profiles,
        load_json,
        payment_id,
):
    responses = load_json('responses.json')

    response = await taxi_contractor_merch_payments.get(
        '/internal/contractor-merch-payments/v1/completed_payments',
        params={'id': payment_id},
        headers={
            'Driver-Application': 'Taximeter 9.90',
            'Accept-Language': 'en_GB',
        },
    )

    assert response.status == 200
    assert response.json() == responses[payment_id]


async def test_payment_not_found(taxi_contractor_merch_payments):
    response = await taxi_contractor_merch_payments.get(
        '/internal/contractor-merch-payments/v1/completed_payments',
        params={'id': 'payment_id-unknown'},
        headers={
            'Driver-Application': 'Taximeter 9.90',
            'Accept-Language': 'en_GB',
        },
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'payment_not_found',
        'message': 'payment_not_found',
    }
