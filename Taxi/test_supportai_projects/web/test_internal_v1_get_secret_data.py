import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_data(web_app_client):
    expected_response = {
        'project_integrations': [
            {
                'id': 1,
                'project_id': 1,
                'integration_id': 1,
                'secret_data': '{}',
            },
            {
                'id': 2,
                'project_id': 1,
                'integration_id': 2,
                'base_url': 'https://baseurl.com',
                'secret_data': '{"SIGNATURE_TOKEN": "token-token"}',
            },
            {
                'id': 3,
                'project_id': 1,
                'integration_id': 3,
                'base_url': 'https://anotherawesomeurl.com',
                'secret_data': '{"API_KEY": "keeeeeeeey"}',
            },
            {
                'id': 4,
                'project_id': 2,
                'integration_id': 4,
                'base_url': 'https://urlurlurl.com',
                'secret_data': '{"API_KEY": "keykeykey"}',
            },
            {
                'id': 5,
                'project_id': 3,
                'integration_id': 5,
                'base_url': 'https://urlurl.com',
                'secret_data': (
                    '{"API_KEY": "kkkey", "SIGNATURE_TOKEN": "tik-tak-token"}'
                ),
            },
        ],
        'api_keys': [
            {'project_id': 1, 'api_key': 'AsdadasdaQ23r'},
            {'project_id': 2, 'api_key': '321232131231'},
            {'project_id': 3, 'api_key': '12345678'},
        ],
        'allowed_ips': [
            {'project_id': 1, 'ip_address': '127.0.0.1'},
            {'project_id': 1, 'ip_address': '0.0.0.0'},
            {'project_id': 1, 'ip_address': '167.2.3.5'},
            {'project_id': 2, 'ip_address': '172.2.8.6'},
            {'project_id': 2, 'ip_address': '172.2.8.8'},
            {'project_id': 3, 'ip_address': '8.8.8.8'},
            {'project_id': 3, 'ip_address': '9.9.9.9'},
        ],
    }

    response = await web_app_client.get('/supportai-projects/v1/secret-data')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response
