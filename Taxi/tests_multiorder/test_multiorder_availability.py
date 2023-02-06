async def test_unauthorized(taxi_multiorder):
    response = await taxi_multiorder.post(
        '/v1/multiorder/availability', {}, headers={'X-Yandex-UID': 'uid'},
    )
    assert response.status_code == 200
