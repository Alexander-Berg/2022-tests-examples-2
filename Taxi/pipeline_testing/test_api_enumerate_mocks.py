async def test_enumerate(web_app_client, mockserver, load_json):
    response = await web_app_client.post(
        '/v2/test/mocks/enumerate/', params={'consumer': 'taxi-surge'},
    )
    assert response.status == 200
    assert await response.json() == {
        'input_mocks': [
            {'id': 'id_2', 'name': 'dummy_input'},
            {'id': 'id_3', 'name': 'other_input'},
        ],
        'prefetched_resources_mocks': [
            {
                'id': 'id_1',
                'name': 'the_mock',
                'resource': 'some_prefetched_resource',
            },
        ],
        'resources_mocks': [
            {
                'id': 'id_0',
                'name': 'dummy_candidates',
                'resource': 'candidates',
            },
        ],
    }
