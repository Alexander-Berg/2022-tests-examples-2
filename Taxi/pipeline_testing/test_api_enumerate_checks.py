async def test_enumerate(web_app_client, mockserver, load_json):
    response = await web_app_client.post(
        '/v2/test/checks/enumerate/', params={'consumer': 'taxi-surge'},
    )
    assert response.status == 200
    assert await response.json() == {
        'output_checks': [
            {
                'id': 'test_check_decl',
                'name': 'declarative',
                'type': 'combined',
            },
            {
                'id': 'test_check_imp',
                'name': 'imperative',
                'type': 'imperative',
            },
        ],
    }
