import pytest


@pytest.mark.parametrize(
    ['passport_mock'],
    [
        pytest.param('client_1', id='client'),
        pytest.param('client_trial_1', id='rejected'),
        pytest.param('client_trial_2', id='pending'),
        pytest.param('client_trial_3', id='just_trial'),
    ],
    indirect=['passport_mock'],
)
async def test_alerts(
        taxi_corp_auth_client,
        load_json,
        passport_mock,
        mock_corp_clients,
        mock_corp_requests,
):
    mock_contracts_response = load_json('get_contracts_response.json')
    mock_corp_clients.data.get_contracts_response = mock_contracts_response

    response = await taxi_corp_auth_client.get('/1.0/alerts')
    response_json = await response.json()
    expected = load_json('expected_alerts.json')[passport_mock]
    assert response_json['alerts'] == expected
