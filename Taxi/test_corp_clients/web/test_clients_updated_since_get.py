import pytest


@pytest.mark.parametrize(
    ['query', 'expected_client_ids'],
    [
        pytest.param(
            {'updated_since': '1532470705.0'}, ['client_id_4', 'client_id_5'],
        ),
        pytest.param(
            {},
            [
                'client_id_1',
                'client_id_6',
                'client_id_7',
                'client_id_2',
                'client_id_3',
                'client_id_4',
                'client_id_5',
            ],
        ),
    ],
)
async def test_updated_since(
        web_app_client, load_json, personal_mock, query, expected_client_ids,
):
    response = await web_app_client.get(
        '/v1/clients/list/updated-since', params=query,
    )
    assert response.status == 200
    response_json = await response.json()

    expected_clients = load_json('expected_clients_updated_at.json')

    expected_clients = [
        expected_clients[client] for client in expected_client_ids
    ]
    assert response_json['clients'] == expected_clients
