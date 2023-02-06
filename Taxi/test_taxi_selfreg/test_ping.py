async def test_ping(taxi_selfreg):
    response = await taxi_selfreg.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
