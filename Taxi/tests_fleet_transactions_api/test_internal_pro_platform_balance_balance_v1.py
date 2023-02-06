import pytest

ENDPOINT_URL = '/internal/pro-platform/balance/balance/v1'
PARK_ID = '7ad35b'
CONTRACTOR_PROFILE_ID = '9c5e35'
EXTERNAL_ID = f'taximeter_driver_id/{PARK_ID}/{CONTRACTOR_PROFILE_ID}'
NOW = '2022-07-01T12:00:00+00:00'


@pytest.mark.now(NOW)
async def test_ok(taxi_fleet_transactions_api, load_json, mockserver):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    async def _mock_billing_reports(request):
        assert request.json['accounts'][0]['entity_external_id'] == EXTERNAL_ID
        assert request.json['accrued_at'][0] == NOW
        assert (
            billing_response['entries'][0]['account']['entity_external_id']
            == EXTERNAL_ID
        )
        assert (
            billing_response['entries'][0]['balances'][0]['accrued_at'] == NOW
        )
        return billing_response

    billing_response = load_json('billing_response.json')
    response = await taxi_fleet_transactions_api.get(
        ENDPOINT_URL,
        params={
            'park_id': PARK_ID,
            'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'total_balance': billing_response['entries'][0]['balances'][0][
            'balance'
        ],
    }
