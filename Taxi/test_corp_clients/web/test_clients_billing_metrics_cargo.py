async def test_empty_clients_list(web_app_client):
    response = await web_app_client.post(
        '/v1/clients/billing-metrics/cargo', json={'clients': []},
    )
    assert response.status == 400
    response_json = await response.json()
    assert response_json == {
        'code': 'REQUEST_ERROR',
        'details': {'reason': 'Empty input'},
        'message': 'Request error',
    }


async def test_basic(web_app_client, load_json):
    response = await web_app_client.post(
        '/v1/clients/billing-metrics/cargo',
        json={
            'clients': [
                'client_service_is_not_found',
                'client_service_is_disabled',
                'client_happy_path_prepaid',
                'taxi_client_happy_path_prepaid',
                'client_contract_deactivated',
            ],
        },
    )

    expected_clients = load_json('expected_clients.json')

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {'clients': expected_clients}
