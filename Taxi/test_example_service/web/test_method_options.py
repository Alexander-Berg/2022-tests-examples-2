from typing import NamedTuple
from typing import Optional

import pytest

ALLOW_AUTH_REQUEST = 'X-YaTaxi-Allow-Auth-Request'
ALLOW_AUTH_RESPONSE = 'X-YaTaxi-Allow-Auth-Response'


class Parameters(NamedTuple):
    request: str
    response: str
    ticket: Optional[str] = None


async def test_handler(web_app_client):
    response = await web_app_client.options('/ping')
    assert response.status == 200
    assert set(response.headers['Allow'].split(', ')) == {'OPTIONS', 'GET'}

    response = await web_app_client.options('/test_ap/parameters_schemed')
    assert response.status == 200
    assert set(response.headers['Allow'].split(', ')) == {'OPTIONS', 'POST'}

    response = await web_app_client.options('/not-existed/route')
    assert not response.headers.get('Allow')
    assert response.status == 404


async def test_auth(web_app_client):
    auth_check_headers = {ALLOW_AUTH_REQUEST: 'tvm2'}
    response = await web_app_client.options(
        '/ping', headers=auth_check_headers,
    )
    assert response.status == 200
    assert set(response.headers['Allow'].split(', ')) == {'OPTIONS', 'GET'}
    assert response.headers[ALLOW_AUTH_RESPONSE] == 'OK'


async def test_options_custom(web_app_client):
    response = await web_app_client.options(
        '/example', headers={ALLOW_AUTH_REQUEST: 'tvm2'},
    )
    assert response.status == 200
    assert set(response.headers['Custom-Allow'].split(', ')) == {
        'OPTIONS',
        'GET',
    }
    assert not response.headers.get(ALLOW_AUTH_RESPONSE)
    assert not response.headers.get('Allow')


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'params',
    [
        Parameters(request='tvm2', ticket=None, response='TVM header missing'),
        Parameters(request='tvm2', ticket='good', response='OK'),
        Parameters(
            request='tvm2', ticket='bad', response='TVM authentication error',
        ),
        Parameters(request='sth', ticket='good', response='unknown checker'),
    ],
)
async def test_auth_tvm_header(params, patch, web_app_client):
    # pylint: disable=unused-variable
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good':
            return 'service'
        return None

    auth_check_headers = {ALLOW_AUTH_REQUEST: params.request}
    if params.ticket:
        auth_check_headers['X-Ya-Service-Ticket'] = params.ticket
    response = await web_app_client.options(
        '/tvm/protected', headers=auth_check_headers,
    )
    assert response.status == 200
    assert set(response.headers['Allow'].split(', ')) == {'OPTIONS', 'GET'}
    assert response.headers[ALLOW_AUTH_RESPONSE] == params.response
