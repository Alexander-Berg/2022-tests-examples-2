async def test_ping(web_app_client):
    response = await web_app_client.get('/legacy/ping')
    response_json = await response.json()
    assert response.status == 200
    assert response_json == {'status': 'OK'}


async def test_post_json(web_app_client):
    response = await web_app_client.post('/legacy/post_json', json={'id': 37})
    response_json = await response.json()
    assert response.status == 200
    assert response_json == {'status': 'Done', 'title': 'Title 37'}


async def test_post_json_validate_request_error(web_app_client):
    response = await web_app_client.post('/legacy/post_json', json={'id': '1'})
    response_json = await response.json()
    assert response.status == 400
    assert response_json == {
        'status': 'error',
        'message': 'Invalid input',
        'code': 'invalid-input',
        'details': {'id': ['\'1\' is not of type \'integer\'']},
    }


async def test_post_json_validate_response_error(web_app_client):
    response = await web_app_client.post('/legacy/post_json', json={'id': 3})
    response_json = await response.json()
    assert response.status == 500
    assert response_json == {
        'code': 'INTERNAL_SERVER_ERROR',
        'details': {
            'reason': (
                '\'title\' is a required property\n\n'
                'Failed validating \'required\' in schema:\n'
                '    {\'properties\': {\'status\': {\'type\': \'string\'},\n'
                '                    \'title\': {\'type\': \'string\'}},\n'
                '     \'required\': [\'status\', \'title\'],\n'
                '     \'type\': \'object\'}\n\n'
                'On instance:\n'
                '    {\'status\': \'Done\'}'
            ),
        },
        'message': 'Internal server error',
    }
