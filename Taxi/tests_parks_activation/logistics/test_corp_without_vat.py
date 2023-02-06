import pytest


@pytest.mark.config(PARKS_ACTIVATION_CORP_WITHOUT_VAT_CONTRACT_REQUIRED=False)
@pytest.mark.now('2021-09-30T00:00:00.000+00:00')
async def test_contract_not_required(
        taxi_config, taxi_parks_activation, park_sync_jobs,
):
    park_with_contract = 'park_id_1'
    park_without_contract = 'park_id_2'

    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={'last_known_revision': 0},
    )
    assert response.status_code == 200
    response_json = response.json()['parks_activation']
    for park in response_json:
        if park['park_id'] == park_with_contract:
            assert park['data'] == {
                'can_card': True,
                'can_cash': True,
                'can_corp': True,
                'has_corp_without_vat_contract': True,
                'can_corp_without_vat': True,
                'can_coupon': True,
                'can_logistic': False,
                'can_subsidy': False,
                'deactivated': False,
            }
        if park['park_id'] == park_without_contract:
            assert park['data'] == {
                'can_card': True,
                'can_cash': True,
                'can_corp': True,
                'has_corp_without_vat_contract': False,
                'can_corp_without_vat': True,
                'can_coupon': False,
                'can_logistic': False,
                'can_subsidy': False,
                'deactivated': False,
            }


@pytest.mark.config(PARKS_ACTIVATION_CORP_WITHOUT_VAT_CONTRACT_REQUIRED=True)
@pytest.mark.now('2021-09-30T00:00:00.000+00:00')
async def test_contract_required(
        taxi_config, taxi_parks_activation, park_sync_jobs,
):
    park_with_contract = 'park_id_1'
    park_without_contract = 'park_id_2'

    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={'last_known_revision': 0},
    )
    assert response.status_code == 200
    response_json = response.json()['parks_activation']
    for park in response_json:
        if park['park_id'] == park_with_contract:
            assert park['data'] == {
                'can_card': True,
                'can_cash': True,
                'can_corp': True,
                'has_corp_without_vat_contract': True,
                'can_corp_without_vat': True,
                'can_coupon': True,
                'can_logistic': False,
                'can_subsidy': False,
                'deactivated': False,
            }
        if park['park_id'] == park_without_contract:
            assert park['data'] == {
                'can_card': True,
                'can_cash': True,
                'can_corp': True,
                'has_corp_without_vat_contract': False,
                'can_corp_without_vat': False,
                'can_coupon': False,
                'can_logistic': False,
                'can_subsidy': False,
                'deactivated': False,
            }
