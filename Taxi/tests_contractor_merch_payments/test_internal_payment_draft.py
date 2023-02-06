import pytest

from tests_contractor_merch_payments import utils


async def payment_draft_request(
        client, park_id, contractor_id, merchant_id, idempotency_token,
):
    return await client.post(
        '/internal/v1/payment/draft',
        headers={
            'X-Idempotency-Token': idempotency_token,
            'Accept-Language': 'en_GB',
        },
        json={
            'park_id': park_id,
            'contractor_id': contractor_id,
            'merchant_id': merchant_id,
            'driver_application': 'Taximeter 9.90',
        },
    )


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
async def test_payment_draft_inserting(
        taxi_contractor_merch_payments,
        pgsql,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_merchant_profiles,
        mock_parks_activation,
):
    mock_merchant_profiles.payment_ttl_sec = 228

    park_id = 'park_id'
    contractor_id = 'contractor_id'
    merchant_id = 'merchant_id'
    idempotency_token = 'idempotency_token'

    response = await payment_draft_request(
        taxi_contractor_merch_payments,
        park_id,
        contractor_id,
        merchant_id,
        idempotency_token,
    )

    assert response.status == 200

    payments = utils.get_payments_by_token(pgsql, idempotency_token)
    assert len(payments) == 1

    payment_id = payments[0][0]

    assert response.json() == {
        'payment_id': payment_id,
        'qr_code': utils.DEEP_LINK_PROXY.format(payment_id),
        'ttl_sec': 228,
    }

    assert payments[0] == (
        payment_id,
        idempotency_token,
        park_id,
        contractor_id,
        merchant_id,
        None,
        'draft',
    )


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
async def test_merchant_id_mismatch_on_retry(
        taxi_contractor_merch_payments,
        pgsql,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_merchant_profiles,
        mock_parks_activation,
):
    park_id = 'park_id'
    contractor_id = 'contractor_id'
    merchant_id = 'merchant_id'
    idempotency_token = 'idempotency_token'

    response = await payment_draft_request(
        taxi_contractor_merch_payments,
        park_id,
        contractor_id,
        merchant_id,
        idempotency_token,
    )

    assert response.status == 200

    response = await payment_draft_request(
        taxi_contractor_merch_payments,
        park_id,
        contractor_id,
        'merchant_id-2',
        idempotency_token,
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'invalid_parameters',
        'message': (
            'Parameters have changed for idempotency_token = idempotency_token'
        ),
    }


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
async def test_merchant_not_found(
        taxi_contractor_merch_payments,
        mockserver,
        pgsql,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_merchant_profiles,
        mock_parks_activation,
):
    @mockserver.json_handler(
        'merchant-profiles/internal/merchant-profiles/v1/merchant',
    )
    async def _merchant(request):
        return mockserver.make_response(
            status=404,
            json={
                'code': 'merchant_not_found',
                'message': 'merchant_not_found',
            },
        )

    response = await payment_draft_request(
        taxi_contractor_merch_payments,
        'park_id',
        'contractor_id',
        'merchant_id',
        'idempotency_token',
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'merchant_not_found',
        'message': 'Merchant merchant_id not found',
    }


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
async def test_merchant_disabled_balance_check(
        taxi_contractor_merch_payments,
        mockserver,
        pgsql,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_merchant_profiles,
        mock_parks_activation,
):
    mock_merchant_profiles.enable_balance_check_on_pay = False
    mock_fleet_transactions_api.balance = '-100'

    park_id = 'park_id'
    contractor_id = 'contractor_id'
    merchant_id = 'merchant_id'
    idempotency_token = 'idempotency_token'

    response = await payment_draft_request(
        taxi_contractor_merch_payments,
        park_id,
        contractor_id,
        merchant_id,
        idempotency_token,
    )

    assert response.status == 400
    assert response.json()['problem_description'] == {
        'code': 'not_enough_money_on_drivers_balance',
        'localized_message': 'not_enough_money_on_drivers_balance-tr',
    }


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.parametrize('failed', [True, False])
@pytest.mark.translations(
    taximeter_backend_marketplace_payments=utils.TRANSLATIONS,
)
async def test_requisites_failed(
        taxi_contractor_merch_payments,
        mockserver,
        pgsql,
        load_json,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_merchant_profiles,
        mock_parks_activation,
        mock_parks_replica,
        mock_billing_replication,
        failed,
):
    mock_merchant_profiles.enable_requisites_check = True
    mock_merchant_profiles.park_id = 'park_id'

    if failed:
        mock_billing_replication.response = load_json(
            'failed_contracts_response.json',
        )

    response = await payment_draft_request(
        taxi_contractor_merch_payments,
        'park_id',
        'contractor_id',
        'merchant_id',
        'idempotency_token',
    )

    if failed:
        assert response.status == 400
        assert response.json() == {
            'code': 'cannot_buy',
            'message': 'some_error_occurred',
            'problem_description': {
                'code': 'some_error_occurred',
                'localized_message': 'some_error_occurred-tr',
            },
        }
    else:
        assert response.status == 200
