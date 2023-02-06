async def test_ping(taximeter_reports_client):
    response = await taximeter_reports_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
