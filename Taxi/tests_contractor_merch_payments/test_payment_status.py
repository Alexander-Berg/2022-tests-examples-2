import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.parametrize('request_type', ['driver', 'internal'])
@pytest.mark.parametrize(
    'payment_id, payment_json',
    [
        pytest.param('payment_id-draft', 'payments-draft.json'),
        pytest.param(
            'payment_id-merchant_accepted', 'payments-merchant_accepted.json',
        ),
        pytest.param(
            'payment_id-target_success', 'payments-target_success.json',
        ),
        pytest.param(
            'payment_id-target_failed', 'payments-target_failed.json',
        ),
        pytest.param(
            'payment_id-target_contractor_declined',
            'payments-target_contractor_declined.json',
        ),
        pytest.param('payment_id-success', 'payments-success.json'),
        pytest.param('payment_id-failed', 'payments-failed.json'),
        pytest.param(
            'payment_id-contractor_declined',
            'payments-contractor_declined.json',
        ),
        pytest.param(
            'payment_id-merchant_canceled', 'payments-merchant_canceled.json',
        ),
    ],
)
async def test_correct_payment_status(
        taxi_contractor_merch_payments,
        pgsql,
        load_json,
        mock_merchant_profiles,
        request_type,
        payment_id,
        payment_json,
):
    park_id, contractor_id, merchant_id, seller = (
        utils.get_fields_by_payment_id(
            pgsql,
            payment_id,
            ['park_id', 'contractor_id', 'merchant_id', 'seller'],
        )
    )

    response = await taxi_contractor_merch_payments.get(
        f'/{request_type}/v1/contractor-merch-payments/payment/status',
        params={'payment_id': payment_id},
        headers=utils.get_headers(
            park_id=park_id, driver_profile_id=contractor_id,
        ),
    )

    assert response.status == 200

    payment = load_json(f'payments/{payment_json}')
    assert response.json() == payment

    if merchant_id is not None and seller is None:
        assert mock_merchant_profiles.merchant.times_called == 1
        assert mock_merchant_profiles.merchant.next_call()[
            'request'
        ].query == {'merchant_id': merchant_id}


@pytest.mark.parametrize(
    'park_id, contractor_id, payment_id',
    [
        pytest.param('park-id-100', 'contractor-id-100', 'payment_id-100'),
        pytest.param('park-id-1', 'contractor-id-2', 'payment_id-draft'),
        pytest.param(
            'park-id-4', 'contractor-id-1', 'payment_id-contractor_declined',
        ),
    ],
)
async def test_incorrect_driver_request(
        taxi_contractor_merch_payments,
        load_json,
        mock_merchant_profiles,
        park_id,
        contractor_id,
        payment_id,
):
    query = {'payment_id': payment_id}

    response = await taxi_contractor_merch_payments.get(
        '/driver/v1/contractor-merch-payments/payment/status',
        params=query,
        headers=utils.get_headers(
            park_id=park_id, driver_profile_id=contractor_id,
        ),
    )

    assert response.status == 404

    expected_response = load_json('error_response.json')
    assert response.json() == expected_response

    assert mock_merchant_profiles.merchant.times_called == 0


async def test_incorrect_internal_request(
        taxi_contractor_merch_payments, load_json, mock_merchant_profiles,
):
    query = {'payment_id': 'payment_id-100'}

    response = await taxi_contractor_merch_payments.get(
        '/internal/v1/contractor-merch-payments/payment/status', params=query,
    )

    assert response.status == 404

    expected_response = load_json('error_response.json')
    assert response.json() == expected_response

    assert mock_merchant_profiles.merchant.times_called == 0


@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
@pytest.mark.parametrize('request_type', ['driver', 'internal'])
@pytest.mark.parametrize(
    ['cannot_buy_reason_code', 'localized_message'],
    [
        pytest.param(
            'some_error_occurred',
            'some_error_occurred-tr',
            id='some_error_occurred',
        ),
        pytest.param(
            'unknown_reason_code',
            'some_error_occurred-tr',
            id='unknown_reason_code',
        ),
        pytest.param(
            'not_enough_money_on_drivers_balance',
            'not_enough_money_on_drivers_balance-tr',
            id='not_enough_money_on_drivers_balance',
        ),
        pytest.param(
            'driver_has_pending_purchases',
            'driver_has_pending_purchases-tr',
            id='driver_has_pending_purchases',
        ),
        pytest.param(
            'park_has_not_enough_money',
            'park_has_not_enough_money-tr',
            id='park_has_not_enough_money',
        ),
        pytest.param(
            'balance_payments_is_disabled_for_park',
            'balance_payments_is_disabled_for_park-tr',
            id='balance_payments_is_disabled_for_park',
        ),
        pytest.param(
            'billing_is_disabled_for_park',
            'billing_is_disabled_for_park-tr',
            id='billing_is_disabled_for_park',
        ),
        pytest.param(
            'unsupported_country',
            'unsupported_country-tr',
            id='unsupported_country',
        ),
        pytest.param(
            'contractor_has_pending_payments',
            'contractor_has_pending_payments-tr',
            id='contractor_has_pending_payments',
        ),
    ],
)
async def test_cannot_buy_reason(
        taxi_contractor_merch_payments,
        pgsql,
        load_json,
        mock_merchant_profiles,
        request_type,
        cannot_buy_reason_code,
        localized_message,
):
    payment_id = 'payment_id-cannot_buy'

    utils.update_fields_by_payment_id(
        pgsql, payment_id, ['status_reason'], [cannot_buy_reason_code],
    )

    if cannot_buy_reason_code == 'unknown_reason_code':
        cannot_buy_reason_code = 'some_error_occurred'

    park_id, contractor_id = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['park_id', 'contractor_id'],
    )

    response = await taxi_contractor_merch_payments.get(
        f'/{request_type}/v1/contractor-merch-payments/payment/status',
        params={'payment_id': payment_id},
        headers=utils.get_headers(
            park_id=park_id, driver_profile_id=contractor_id,
        ),
    )

    payment = load_json(f'payments/payments-cannot_buy.json')

    cannot_buy_reason = {'code': cannot_buy_reason_code}
    if request_type == 'driver':
        cannot_buy_reason['localized_message'] = localized_message

    payment['payment']['cannot_buy_reason'] = cannot_buy_reason

    assert response.status == 200
    assert response.json() == payment
