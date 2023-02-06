# pylint: disable=redefined-outer-name

import pytest

SF_MANAGERS_RESPONSE: dict = {
    'managers': [
        {
            'contracts': [
                {'contract_id': '1424719/20', 'services': ['eats2']},
            ],
            'manager': {'name': 'Мария Козлова', 'tier': 'Free'},
        },
        {
            'contracts': [
                {'contract_id': '1425792/20', 'services': ['drive']},
            ],
            'manager': {'name': 'Чикалова', 'tier': 'Free'},
        },
        {
            'contracts': [
                {'contract_id': '1425777/20', 'services': ['taxi', 'cargo']},
                {'contract_id': '1914267/21', 'services': ['cargo']},
            ],
            'manager': {'name': '', 'tier': 'Free'},
        },
    ],
}


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_sf_managers(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    mock_corp_clients.data.sf_managers_response = SF_MANAGERS_RESPONSE

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/sf/managers',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.get_sf_managers.has_calls
    assert response_json == SF_MANAGERS_RESPONSE
