import pytest


@pytest.mark.parametrize(
    ['query', 'expected_client_ids'],
    [
        pytest.param(
            {'city': 'Москва'},
            ['client_id_1', 'client_id_2', 'client_id_6', 'client_id_7'],
        ),
        pytest.param(
            {},
            [
                'client_id_1',
                'client_id_2',
                'client_id_3',
                'client_id_4',
                'client_id_5',
                'client_id_6',
                'client_id_7',
            ],
        ),
        pytest.param(
            {'client_ids': 'client_id_1,client_id_4'},
            ['client_id_1', 'client_id_4'],
        ),
        pytest.param({'city': 'Москва', 'phone': '+79260410252'}, []),
    ],
)
async def test_search(
        web_app_client, load_json, personal_mock, query, expected_client_ids,
):
    response = await web_app_client.get(
        '/v1/clients/list/accurate', params=query,
    )
    assert response.status == 200
    response_json = await response.json()

    expected_clients = load_json('expected_clients.json')

    expected_clients = [
        expected_clients[client] for client in expected_client_ids
    ]
    assert response_json == {
        'clients': expected_clients,
        'skip': 0,
        'limit': 50,
        'amount': len(expected_clients),
        'sort_field': 'name',
        'sort_direction': 1,
    }
