from aiohttp import test_utils
import pytest


@pytest.mark.config(
    PERSONAL_WALLET_FIRM_BY_SERVICE={
        'eats': {'RUB': '32'},
        'grocery': {'RUB': '32'},
        'restaurants': {'RUB': '32'},
        'yataxi': {'RUB': '13'},
    },
)
@pytest.mark.parametrize(
    'scenario_file',
    [
        'cursor.json',
        'no-cursor.json',
        'wallet-not-found.json',
        'naive-datetime.json',
        'filter-by-service.json',
        'filter-by-service-unknown.json',
        'filter-by-cashback-type-marketing.json',
        'filter-by-cashback-type-unknown.json',
        'filter-by-cashback-type-transaction.json',
        'filter-by-transaction-type-expense.json',
        'filter-by-transaction-type-income.json',
    ],
)
async def test_get_transactions(
        web_app_client: test_utils.TestClient,
        mockserver,
        scenario_file,
        load_json,
):
    scenario = load_json(scenario_file)

    @mockserver.handler('/billing-wallet/statement')
    def _mock_statement(request):
        assert request.json == scenario['billing_wallet']['expected_request']
        return mockserver.make_response(
            json=scenario['billing_wallet']['response'],
            status=scenario['billing_wallet']['status'],
        )

    response = await web_app_client.post(
        '/v1/admin/transactions', json=scenario['request'],
    )

    assert response.status == scenario['expected_status']
    assert await response.json() == scenario['expected_response']
