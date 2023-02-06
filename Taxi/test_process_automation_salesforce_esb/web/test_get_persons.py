import pytest


@pytest.fixture
def get_last_partner_mock(request, patch):
    @patch('taxi.clients.billing_v2.BalanceClient.get_client_persons')
    async def _get_partner_balances(*args, **kwargs):
        return [
            {'ID': '123', 'DT': '2020-12-18 12:58:42'},
            {'ID': '120', 'DT': '2020-12-18 11:57:42'},
            {'ID': '321', 'DT': '2020-12-18 11:58:42'},
        ]


@pytest.mark.servicetest
@pytest.mark.usefixtures('get_last_partner_mock')
async def test_get_persons(web_app_client):
    response = await web_app_client.get('/v1/billing/persons?client_id=1')

    assert response.status == 200
    content = await response.json()
    assert content == [
        {'person_id': 120},
        {'person_id': 123},
        {'person_id': 321},
    ]
