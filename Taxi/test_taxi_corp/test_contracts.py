# pylint: disable=redefined-outer-name

import pytest

CONTRACTS_RESPONSE = {
    'contracts': [
        {
            'contract_id': 101,
            'billing_contract_id': '123',
            'services': ['taxi', 'eats2', 'drive', 'tanker'],
        },
    ],
}


@pytest.mark.parametrize(
    ['passport_mock', 'contracts_response', 'expected'],
    [
        pytest.param(
            'client1',
            {
                'contracts': [
                    {
                        'contract_id': 101,
                        'billing_contract_id': '123',
                        'services': ['taxi', 'eats2', 'drive', 'tanker'],
                    },
                    {
                        'contract_id': 102,
                        'billing_contract_id': '123',
                        'services': ['tanker'],
                    },
                ],
            },
            {
                'contracts': [
                    {
                        'contract_id': 101,
                        'billing_contract_id': '123',
                        'services': ['taxi', 'eats2', 'drive'],
                    },
                    {
                        'contract_id': 102,
                        'billing_contract_id': '123',
                        'services': ['tanker'],
                    },
                ],
            },
        ),
        pytest.param(
            'client1',
            {
                'contracts': [
                    {
                        'contract_id': 101,
                        'billing_contract_id': '123',
                        'services': ['tanker'],
                    },
                ],
            },
            {
                'contracts': [
                    {
                        'contract_id': 101,
                        'billing_contract_id': '123',
                        'services': ['tanker'],
                    },
                ],
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_get_contracts(
        taxi_corp_real_auth_client,
        passport_mock,
        contracts_response,
        expected,
        mock_corp_clients,
):
    mock_corp_clients.data.get_contracts_response = contracts_response

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/contracts',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.get_contracts.has_calls
    assert response_json == expected


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_contracts_is_active(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    mock_corp_clients.data.get_contracts_response = CONTRACTS_RESPONSE
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/contracts', params={'is_active': 'true'},
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.get_contracts.times_called == 1

    call = mock_corp_clients.get_contracts.next_call()
    assert call['request'].query['is_active'] == 'true'


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_contract_settings(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    mock_corp_clients.data.get_contracts_response = CONTRACTS_RESPONSE

    query = {'contract_id': '101'}
    data = {'low_balance_threshold': '100'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/contracts/settings/update',
        params=query,
        json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.update_contract_settings.has_calls
    mock_call = mock_corp_clients.update_contract_settings.next_call()
    assert mock_call['request'].query == query
    assert mock_call['request'].json == data
    assert not mock_corp_clients.update_contract_settings.has_calls


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_contract_settings_403(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    mock_corp_clients.data.get_contracts_response = CONTRACTS_RESPONSE

    query = {'contract_id': 'unknown'}
    data = {'low_balance_threshold': '100'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/contracts/settings/update',
        params=query,
        json=data,
    )
    response_json = await response.json()
    assert response.status == 403, response_json
    assert not mock_corp_clients.update_contract_settings.has_calls
