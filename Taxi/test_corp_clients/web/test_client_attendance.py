async def test_client_attendance(web_app_client):
    response = await web_app_client.get(
        '/v1/clients/attendance', params={'client_id': 'client_id_1'},
    )
    assert response.status == 200
    response_json = await response.json()

    assert len(response_json['attendances']) == 1
