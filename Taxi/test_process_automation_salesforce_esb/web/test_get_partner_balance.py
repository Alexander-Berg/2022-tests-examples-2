import pytest


@pytest.fixture
def get_partner_balance_mock(request, patch):
    @patch('taxi.clients.billing_v2.BalanceClient.get_partner_balances')
    async def _get_partner_balances(*args, **kwargs):
        return [{'PersonalAccountExternalID': 11048320, 'ContractID': 123}]


@pytest.mark.servicetest
@pytest.mark.usefixtures('get_partner_balance_mock')
async def test_get_partner_balance(web_app_client):
    response = await web_app_client.get(
        '/v1/billing/partner/balance?contract_id=123&service_id=321',
    )

    assert response.status == 200
    content = await response.text()
    assert content == '{"personal_account_id": "11048320"}'
