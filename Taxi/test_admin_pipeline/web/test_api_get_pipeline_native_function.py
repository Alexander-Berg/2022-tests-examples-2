async def test_get_native_function(web_app_client, mockserver):
    consumer = 'taxi-surge'
    service = 'surge-calculator'
    name = 'sample_function'
    body = {
        'signature': {
            'arguments': [
                {'name': 'sample_argument', 'schema': {'type': 'integer'}},
            ],
            'return_value': {'schema': {'type': 'boolean'}},
        },
        'js_source_code': 'some_code',
    }

    @mockserver.json_handler(f'/{service}/v1/js/pipeline/native-function')
    def _native_function(request):
        assert request.query['name'] == name
        return body

    response = await web_app_client.post(
        '/v2/pipeline/native-function',
        params={'consumer': consumer, 'name': name},
    )
    assert response.status == 200
    assert await response.json() == body
