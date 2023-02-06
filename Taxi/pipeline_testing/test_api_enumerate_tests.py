async def test_enumerate(web_app_client):
    response = await web_app_client.post(
        '/v2/tests/enumerate/', params={'consumer': 'taxi-surge'},
    )
    assert response.status == 200
    assert await response.json() == {
        'tests': [
            {'id': 'test_id_0', 'name': 'test_test_0', 'scope': 'global'},
            {'id': 'test_id_1', 'name': 'test_test_1', 'scope': 'pipeline'},
        ],
    }
