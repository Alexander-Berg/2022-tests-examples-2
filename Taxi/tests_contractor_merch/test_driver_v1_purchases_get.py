import pytest

from tests_contractor_merch import util


TRANSLATIONS = util.STQ_TRANSLATIONS


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.parametrize(
    ['purchase_id', 'response_json'],
    [
        pytest.param(
            'voucher_idempotency_token-2',
            'primitive_promocode_response.json',
            marks=(
                pytest.mark.pgsql(
                    'contractor_merch',
                    files=['primitive_promocode_purchase.sql'],
                )
            ),
            id='primitive_promocode',
        ),
        pytest.param(
            'voucher_idempotency_token-1',
            'promocode_with_barcode_response.json',
            marks=(
                pytest.mark.pgsql(
                    'contractor_merch',
                    files=['primitive_promocode_purchase.sql'],
                )
            ),
            id='promocode_with_barcode',
        ),
        pytest.param(
            'voucher_idempotency_token-1',
            'few_promocodes_response.json',
            marks=(
                pytest.mark.pgsql(
                    'contractor_merch', files=['few_promocodes_purchase.sql'],
                )
            ),
            id='few_promocodes',
        ),
        pytest.param(
            'voucher_idempotency_token-1',
            'hyperlinked_promocode_response.json',
            marks=(
                pytest.mark.pgsql(
                    'contractor_merch',
                    files=['hyperlinked_promocode_purchase.sql'],
                )
            ),
            id='hyperlinked_promocode',
        ),
    ],
)
async def test_contractor_merch_transactions(
        taxi_contractor_merch,
        mock_contractor_merch_payments,
        load_json,
        purchase_id,
        response_json,
):
    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/purchases',
        params={'purchase_id': purchase_id},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )

    assert response.status == 200
    assert response.json() == load_json(response_json)


@pytest.mark.parametrize(
    ['payment_id'],
    [
        pytest.param('payment_id-failed'),
        pytest.param('payment_id-success-0'),
        pytest.param('payment_id-merchant_canceled'),
    ],
)
async def test_contractor_merch_payments_transactions(
        taxi_contractor_merch,
        mock_contractor_merch_payments,
        load_json,
        payment_id,
):
    expected_responses = load_json('contractor_merch_payments_responses.json')

    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/purchases',
        params={'purchase_id': f'raw_payment_{payment_id}'},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )

    assert response.status == 200
    assert response.json() == expected_responses[payment_id]


@pytest.mark.pgsql(
    'contractor_merch', files=['primitive_promocode_purchase.sql'],
)
@pytest.mark.parametrize(
    ['purchase_id'],
    [
        pytest.param('voucher_idempotency_token-10', id='contractor-merch'),
        pytest.param(
            'raw_payment_unknown_payment_id', id='contractor-merch-payments',
        ),
        pytest.param('unknown_purchase_id', id='unknown'),
    ],
)
async def test_payment_not_found(
        taxi_contractor_merch, mock_contractor_merch_payments, purchase_id,
):
    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/purchases',
        params={'purchase_id': purchase_id},
        headers=util.get_headers('park_id-1', 'driver_id-1'),
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'payment_not_found',
        'message': 'payment_not_found',
    }
