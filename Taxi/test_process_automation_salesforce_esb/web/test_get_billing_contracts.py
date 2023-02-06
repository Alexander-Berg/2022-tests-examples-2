import datetime

import pytest


@pytest.fixture
def get_client_contracts_mock(request, patch):
    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _get_client_contracts(*args, **kwargs):
        return [
            {
                'CONTRACT_TYPE': 9,
                'COUNTRY': 225,
                'CURRENCY': 'RUR',
                'DT': datetime.datetime.now(),
                'EXTERNAL_ID': '942262/20',
                'FIRM_ID': 13,
                'ID': 1811525,
                'IS_ACTIVE': 1,
                'IS_CANCELLED': 0,
                'IS_DEACTIVATED': 0,
                'IS_FAXED': 0,
                'IS_SIGNED': 1,
                'IS_SUSPENDED': 0,
                'MANAGER_CODE': 27703,
                'NDS_FOR_RECEIPT': -1,
                'NETTING': 1,
                'NETTING_PCT': '100',
                'OFFER_ACCEPTED': 1,
                'PAYMENT_TYPE': 2,
                'PERSON_ID': 11002921,
                'SERVICES': [128, 605, 626, 111, 124, 125],
            },
        ]


@pytest.mark.servicetest
@pytest.mark.usefixtures('get_client_contracts_mock')
async def test_get_billing_contracts(web_app_client):
    response = await web_app_client.get(
        '/v1/billing/contract?client_id=467949&contract_kind=GENERAL',
    )

    assert response.status == 200
    content = await response.text()
    assert content != ''


@pytest.mark.servicetest
@pytest.mark.usefixtures('get_client_contracts_mock')
async def test_get_billing_contracts_with_external_id(web_app_client):
    response = await web_app_client.get(
        '/v1/billing/contract?client_id=111111&'
        'contract_kind=GENERAL&external_id=111122/20',
    )

    assert response.status == 200
    content = await response.text()
    assert content != ''
