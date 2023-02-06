async def test_service_list_get(web_app_client):
    response = await web_app_client.get('/v1/services/list/')
    assert response.status == 200
    data = (await response.json())['services']
    assert data == [
        {'name': 'logs_errors_filters'},
        {'name': 'logs_warnings_filters'},
        {'name': 'replication'},
        {'name': 'taxi_corp'},
    ]
