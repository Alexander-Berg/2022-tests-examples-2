import pytest

from . import common


@pytest.mark.dontfreeze
async def test_example_success(web_app_client, caplog):
    response = await web_app_client.get('/example', params={'name': 'me'})
    assert response.status == 200
    data = await response.json()
    assert data == {'name': 'me', 'greetings': 'Hello, me'}
    request_log, response_log = common.get_request_response(caplog)
    assert request_log.extdict['method'] == 'GET'
    assert request_log.extdict['uri'] == '/example?name=me'
    assert response_log.extdict['method'] == 'GET'
    assert response_log.extdict['delay'] > 0
    assert response_log.extdict['uri'] == '/example?name=me'


@pytest.mark.dontfreeze
async def test_example_exception(web_app_client, caplog):
    response = await web_app_client.get('/example', params={'name': 'evil'})
    assert response.status == 500
    data = await response.json()
    assert data == {
        'message': 'Internal server error',
        'code': 'INTERNAL_SERVER_ERROR',
        'details': {'reason': ''},
    }
    request_log, response_log = common.get_request_response(caplog)
    assert request_log.extdict['method'] == 'GET'
    assert request_log.extdict['uri'] == '/example?name=evil'
    assert response_log.extdict['method'] == 'GET'
    assert response_log.extdict['delay'] > 0
    assert response_log.extdict['uri'] == '/example?name=evil'
