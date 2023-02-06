async def test_get_tests_results(web_app_client):
    response = await web_app_client.get(
        '/v2/pipeline/tests/results/',
        params={
            'consumer': 'taxi-surge',
            'pipeline_id': '012345678901234567890123',
        },
    )
    assert response.status == 200
    assert await response.json() == {
        'tests_results': {
            'created': '2020-01-01T13:00:00+03:00',
            'tests': [
                {
                    'name': 'the_test',
                    'testcases': [
                        {'name': 'surge_is_present', 'passed': True},
                    ],
                },
            ],
        },
    }


async def test_no_results(web_app_client):
    response = await web_app_client.get(
        '/v2/pipeline/tests/results/',
        params={'consumer': 'taxi-surge', 'pipeline_id': 'another_pipeline'},
    )
    assert response.status == 200
    assert await response.json() == {}
