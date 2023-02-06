async def test_enumerate(web_app_client):
    response = await web_app_client.post(
        '/v2/pipeline/tests/enumerate/',
        params={'consumer': 'taxi-surge', 'pipeline_name': 'the_pipeline'},
    )
    assert response.status == 200
    assert await response.json() == {
        'tests': [
            {'id': 'test_id_0', 'name': 'test_test_0', 'scope': 'global'},
            {'id': 'test_id_1', 'name': 'test_test_1', 'scope': 'pipeline'},
        ],
    }
