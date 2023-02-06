import pytest

URL = '/internal/pro-platform/income/balances/v1'
CATEGORY_ID = 'tips'
FINANCE_GROUP_ID = 'market'


@pytest.mark.parametrize(
    'mode', ['by_category', 'total_by_group', 'categories_by_group', 'total'],
)
async def test_income_balances(
        taxi_fleet_transactions_api, fleet_parks, mockserver, load_json, mode,
):
    def mode_data(mode):
        if mode == 'by_category':
            return {
                'finance_group_id': FINANCE_GROUP_ID,
                'category_id': CATEGORY_ID,
            }
        if mode == 'total_by_group':
            return {'finance_group_id': FINANCE_GROUP_ID}
        if mode == 'categories_by_group':
            return {'finance_group_id': FINANCE_GROUP_ID}
        if mode == 'total':
            return {}
        return {}

    # mock billing_reports
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_billing_reports(request):
        expected_json = load_json(f'{mode}/expected_billing_request.json')
        request.json['accounts'].sort(key=lambda el: el['agreement_id'])
        expected_json['accounts'].sort(key=lambda el: el['agreement_id'])
        assert request.json == expected_json
        return load_json(f'{mode}/billing_response.json')

    response_data = {
        'park_id': 'park0',
        'contractor_profile_id': 'courier0',
        'accrued_ats': ['2022-01-01T00:00:00Z', '2022-01-02T00:00:00Z'],
        'mode': {'type': mode, **mode_data(mode)},
    }

    response = await taxi_fleet_transactions_api.post(URL, json=response_data)

    assert response.status_code == 200
    response_json = response.json()
    expected_json = load_json(f'{mode}/expected_response.json')
    response_json['category_balances'].sort(
        key=lambda el: el['finance_group_id'],
    )
    expected_json['category_balances'].sort(
        key=lambda el: el['finance_group_id'],
    )
    assert response_json == expected_json
