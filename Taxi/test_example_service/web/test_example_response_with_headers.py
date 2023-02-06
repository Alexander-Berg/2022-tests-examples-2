async def test_example_different_headers_in_response(web_app_client):
    response = await web_app_client.get(
        '/example_response_headers', params={'name': 'Naimo'},
    )
    assert response.status == 200
    data = await response.json()

    assert data == {'name': 'Naimo', 'greetings': 'Headered hello, Naimo'}
    assert (
        response.headers['Some-Header']
        == 'string header with request name: Naimo'
    )
    assert response.headers['Some-Shining-Header'] == '5'
