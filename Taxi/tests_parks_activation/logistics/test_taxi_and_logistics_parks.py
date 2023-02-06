import pytest


# TODO uncomment logistics after
#  https://st.yandex-team.ru/CARGODEV-8360#61bb2328ee8b8d148c4413ee
@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.mark.now('2021-09-30T07:30:00.000+00:00')
async def test_balances(taxi_parks_activation, park_sync_jobs):
    response = await taxi_parks_activation.post(
        '/v2/parks/activation/balances', params={'park_id': 'park_id_1'},
    )
    assert response.status == 200
    response_json = response.json()
    response_json['balances'] = sorted(
        response_json['balances'], key=lambda x: x['contract_id'],
    )
    assert response.json() == {
        'balances': [
            {
                'balance': '100.88',
                'contract_id': '0',
                'currency': 'RUB',
                'service_id': 1161,
                'threshold': '15.5',
                'threshold_dynamic': '-2000',
                'personal_account_external_id': 'lst_logistic',
            },
            {
                'balance': '55.55',
                'contract_id': '1',
                'currency': 'RUB',
                'threshold': '15.5',
                'threshold_dynamic': '-2111.11',
                'personal_account_external_id': 'lst_taxi',
            },
            {
                'contract_id': '2',
                'currency': 'RUB',
                'threshold': '15.5',
                'threshold_dynamic': '-2111.11',
            },
            {
                'contract_id': '3',
                'currency': 'RUB',
                'threshold': '15.5',
                'threshold_dynamic': '-2111.11',
            },
        ],
    }


@pytest.mark.config(
    ENABLE_DYNAMIC_PARK_THRESHOLD=True,
    PARKS_ACTIVATION_CORP_WITHOUT_VAT_CONTRACT_REQUIRED=True,
)
@pytest.mark.now('2021-09-30T00:00:00.000+00:00')
async def test_active_taxi_and_logistic_parks(
        taxi_parks_activation, park_sync_jobs,
):
    response = await taxi_parks_activation.post(
        'v1/parks/activation/updates', json={'last_known_revision': 0},
    )
    assert response.status_code == 200
    response_json = response.json()['parks_activation']
    for park in response_json:
        if park['park_id'] == 'park_id_1':
            assert park['data'] == {
                'can_card': True,
                'can_cash': True,
                'can_corp': True,
                'has_corp_without_vat_contract': False,
                'can_corp_without_vat': False,
                'can_coupon': True,
                'can_logistic': True,
                'can_subsidy': False,
                'deactivated': False,
                # 'logistic_can_card': True,
                # 'logistic_can_cash': True,
                # 'logistic_deactivated': False,
            }
        else:
            assert park['data'] == {
                'can_card': False,
                'can_cash': False,
                'can_corp': False,
                'has_corp_without_vat_contract': False,
                'can_corp_without_vat': False,
                'can_coupon': False,
                'can_logistic': False,
                'can_subsidy': False,
                'deactivated': True,
                'deactivated_reason': 'park not registered in billing',
                # 'logistic_can_card': False,
                # 'logistic_can_cash': False,
                # 'logistic_deactivated': True,
                # 'logistic_deactivated_reason': (
                #     'park not registered in billing'
                # ),
            }
