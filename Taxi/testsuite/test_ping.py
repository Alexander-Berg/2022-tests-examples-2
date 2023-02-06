async def test_ping(logistic_dispatcher_client):
    response = await logistic_dispatcher_client.get('ping')
    assert response.status_code == 200
