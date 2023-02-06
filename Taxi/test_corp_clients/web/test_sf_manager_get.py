async def test_sf_manager_get(
        web_app_client, mock_salesforce_auth, mock_salesforce_query,
):
    expected_response = {
        'managers': [
            {
                'contracts': [
                    {
                        'contract_id': '101/12',
                        'services': ['taxi', 'cargo', 'eats2'],
                    },
                ],
                'manager': {
                    'name': 'Мария Козлова',
                    'phone': '',
                    'mobile_phone': '',
                    'extension': '',
                    'email': '',
                    'tier': 'SMB',
                },
            },
            {
                'contracts': [
                    {'contract_id': '103/12', 'services': ['cargo']},
                    {'contract_id': '105/12', 'services': ['tanker']},
                    {'contract_id': '109/12', 'services': ['eats2']},
                ],
            },
        ],
    }

    response = await web_app_client.get(
        '/v1/sf/managers', params={'client_id': 'client_id_1'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == expected_response
