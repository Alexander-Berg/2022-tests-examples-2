import json

import pytest


@pytest.mark.parametrize('code', ['200', '400', '404', '500', '401'])
async def test_source_response_code(
        taxi_api_proxy, endpoints, resources, mockserver, load_yaml, code,
):
    @mockserver.json_handler('/mock-me')
    def _mock_cardstorage_card(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        return mockserver.make_response(status=code, json={'code': code})

    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    # create endpoint
    handler_def = load_yaml('response_code_handler.yaml')
    path = '/test/foo/bar'
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    # call the endpoint
    response = await taxi_api_proxy.post('test/foo/bar', json={})
    assert response.status_code == 200

    responses = {
        '200': {'result': 'Ok', 'source-body': {'code': '200'}},
        '400': {'result': 'Bad request', 'source-body': {'code': '400'}},
        '404': {'result': 'Not found', 'source-body': {'code': '404'}},
        '500': {'result': 'Server error', 'source-body': {'code': '500'}},
        # Special fallback case
        '401': {'result': 'Ok', 'source-body': {'property': 'test'}},
    }
    assert json.loads(response.content) == responses[code]
