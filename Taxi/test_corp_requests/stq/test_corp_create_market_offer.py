import pytest

from corp_requests.stq import corp_create_market_offer

CONTRACTS_RESPONSE = {
    'contracts': [
        {
            'contract_id': 15384971,
            'external_id': '3553886/21',
            'billing_client_id': '1354933928',
            'billing_person_id': '19104248',
            'payment_type': 'prepaid',
            'is_offer': True,
            'currency': 'RUB',
            'services': ['taxi', 'cargo'],
            'is_active': True,
        },
    ],
}


@pytest.mark.parametrize(
    ['create_3p_contract'],
    [
        pytest.param(
            True,
            marks=pytest.mark.config(CORP_MARKET_3P_CONTRACTS_ENABLED=True),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(CORP_MARKET_3P_CONTRACTS_ENABLED=False),
        ),
    ],
)
@pytest.mark.config(
    CORP_OFFER_BALANCE_MANAGER_UIDS={'rus': {'__default__': [123456789]}},
)
async def test_create_market_offer(
        patch, db, stq3_context, stq, mock_corp_clients, create_3p_contract,
):
    @patch('taxi.clients.billing_v2.BalanceClient.create_offer')
    async def _create_offer(*args, **kwargs):
        return {'EXTERNAL_ID': 'EXTERNAL_ID', 'ID': 'CONTRACT_ID'}

    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def _client_contracts(*args, **kwargs):
        return []

    mock_corp_clients.data.get_contracts_response = CONTRACTS_RESPONSE
    mock_corp_clients.data.get_client_response = {
        'id': 'client_id_1',
        'country': 'rus',
    }

    await corp_create_market_offer.task(stq3_context, client_id='client_id_1')

    balance_calls = _create_offer.calls
    assert len(balance_calls) == 2 if create_3p_contract else 1
    assert balance_calls[0]['kwargs'] == {
        'client_id': '1354933928',
        'country': 225,
        'currency': 'RUB',
        'firm_id': 111,
        'manager_uid': 123456789,
        'payment_type': 2,
        'person_id': '19104248',
        'region': 225,
        'services': [1173],
    }
    if create_3p_contract:
        assert balance_calls[1]['kwargs'] == {
            'client_id': '1354933928',
            'country': 225,
            'currency': 'RUB',
            'firm_id': 1932,
            'external_id': 'EXTERNAL_ID',
            'manager_uid': 123456789,
            'payment_type': 2,
            'person_id': '19104248',
            'region': 225,
            'services': [1173],
        }

    assert stq.corp_sync_market_contract.times_called == 1
    assert stq.corp_sync_market_contract.next_call()['kwargs'] == {
        'billing_client_id': '1354933928',
    }

    assert mock_corp_clients.service_market.times_called == 1
    assert mock_corp_clients.service_market.next_call()['request'].json == {
        'is_active': True,
        'is_visible': True,
    }


async def test_create_market_offer_fail(
        patch, db, stq3_context, stq, mock_corp_clients,
):
    mock_corp_clients.data.get_contracts_response = CONTRACTS_RESPONSE
    mock_corp_clients.data.get_client_response = {
        'id': 'client_id_1',
        'country': 'rus',
    }

    await corp_create_market_offer.task(stq3_context, client_id='client_id_1')

    additional_client_request = (
        await db.corp_additional_client_requests.find_one(
            {'client_id': 'client_id_1'},
        )
    )
    assert additional_client_request['last_error'] is not None
