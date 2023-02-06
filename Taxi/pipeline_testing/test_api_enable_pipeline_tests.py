async def test_enumerate(web_app_client):
    # no tests enabled before
    response = await web_app_client.post(
        '/v2/pipeline/tests/enumerate/',
        params={'consumer': 'taxi-surge', 'pipeline_name': 'the_pipeline'},
    )
    assert response.status == 200
    assert await response.json() == {'tests': []}

    response = await web_app_client.post(
        '/v2/pipeline/tests/enable/',
        params={'consumer': 'taxi-surge', 'pipeline_name': 'the_pipeline'},
        json={'enabled_tests': ['smoke_test']},
    )
    assert response.status == 200

    # some tests enabled noe
    response = await web_app_client.post(
        '/v2/pipeline/tests/enumerate/',
        params={'consumer': 'taxi-surge', 'pipeline_name': 'the_pipeline'},
    )
    assert response.status == 200
    assert await response.json() == {
        'tests': [
            {'id': 'test_id_1', 'name': 'smoke_test', 'scope': 'pipeline'},
        ],
    }
