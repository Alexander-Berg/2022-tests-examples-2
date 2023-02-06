async def test_success(
        web_app_client, mock_parks, mock_dac_users, headers, load_json, patch,
):
    stub = load_json('success.json')

    response = await web_app_client.get(
        '/support-chat-api/v1/references-quick', headers=headers,
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']
