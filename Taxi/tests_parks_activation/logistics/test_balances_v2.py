import pytest


@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.mark.now('2021-09-30T07:30:00.000+00:00')
async def test_logistic_balances(taxi_parks_activation, park_sync_jobs):
    response = await taxi_parks_activation.post(
        '/v2/parks/activation/balances', params={'park_id': 'park_id_1'},
    )
    assert response.status == 200
    assert response.json() == {
        'balances': [
            {
                'balance': '100.88',
                'contract_id': '0',
                'currency': 'RUB',
                'service_id': 1161,
                'threshold': '15.5',
                'threshold_dynamic': '-2000',
                'personal_account_external_id': 'string',
            },
        ],
    }


@pytest.mark.config(ENABLE_DYNAMIC_PARK_THRESHOLD=True)
@pytest.mark.now('2021-09-30T00:00:00.000+00:00')
async def test_logistic_balances_404(taxi_parks_activation, park_sync_jobs):
    response = await taxi_parks_activation.post(
        '/v2/parks/activation/balances', params={'park_id': 'park_id_2'},
    )
    assert response.status == 404
