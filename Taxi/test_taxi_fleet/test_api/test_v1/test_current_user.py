async def test_success(web_app_client, mock_dac_users, headers):

    response = await web_app_client.post(
        '/api/v1/users/current', headers=headers,
    )

    assert response.status == 200

    data = await response.json()

    assert data == {'user': {'position': 0}}
