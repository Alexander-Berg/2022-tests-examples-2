import pytest


@pytest.mark.parametrize('has_data', [True, False])
@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 3650,
        },
    },
)
async def test_pricing_payment_methods(
        taxi_cargo_claims, state_controller, has_data, load_json,
):
    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    pricing_payment_methods = {
        'card': {
            'cardstorage_id': 'card-xxx',
            'owner_yandex_uid': 'yandex_uid-yyy',
        },
    }

    request = load_json('finish_estimate_request.json')
    if has_data:
        request['pricing_payment_methods'] = pricing_payment_methods

    response = await taxi_cargo_claims.post(
        'v1/claims/finish-estimate',
        params={'claim_id': claim_id},
        json=request,
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.get(
        '/v2/claims/finance/estimation-result/payment-methods',
        params={'claim_id': claim_id},
    )

    claim_full = await taxi_cargo_claims.get(
        '/v2/claims/full', params={'claim_id': claim_id},
    )

    if has_data:
        assert response.status_code == 200
        assert response.json() == pricing_payment_methods
        assert (
            claim_full.json()['pricing_payment_methods']
            == pricing_payment_methods
        )
    else:
        assert response.status_code == 404
