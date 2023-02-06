# pylint: disable=redefined-outer-name
from typing import Any
from typing import NamedTuple
from typing import Optional

import pytest

GET = 'GET'
HEAD = 'HEAD'


class Parameters(NamedTuple):
    tvm_header: Optional[str]
    resp_body: Any = 'protected'
    expected_status: int = 200


@pytest.fixture
def call_handler(web_app_client):
    async def request(method_name=GET, tvm_header=None, url='/tvm/protected'):
        headers = None
        if tvm_header is not None:
            headers = {'X-Ya-Service-Ticket': tvm_header}
        return await web_app_client.request(method_name, url, headers=headers)

    return request


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'url', ['/tvm/protected', '/tvm/protected-by-default'],
)
@pytest.mark.parametrize('method_name', [GET, HEAD])
@pytest.mark.parametrize(
    'parameters',
    [
        Parameters(tvm_header='good', resp_body='protected'),
        Parameters(
            tvm_header=None,
            resp_body={
                'message': 'TVM header missing',
                'code': 'tvm-auth-error',
            },
            expected_status=401,
        ),
        Parameters(
            tvm_header='bad',
            resp_body={
                'message': 'TVM authentication error',
                'code': 'tvm-auth-error',
            },
            expected_status=401,
        ),
    ],
)
async def test_enabled(
        call_handler, patched_tvm_ticket_check, method_name, parameters, url,
):
    response = await call_handler(method_name, parameters.tvm_header, url)
    assert response.status == parameters.expected_status

    if method_name == HEAD:
        content = await response.text()
        assert not content
    else:
        if parameters.expected_status != 200:
            content = await response.json()
        else:
            content = await response.text()
        assert content == parameters.resp_body

    if parameters.tvm_header is None:
        assert not patched_tvm_ticket_check.calls
    else:
        assert patched_tvm_ticket_check.calls[0]['ticket_body'] == (
            parameters.tvm_header.encode('utf-8')
        )


@pytest.mark.config(TVM_ENABLED=False)
async def test_disabled_check(call_handler):
    response = await call_handler()
    assert response.status == 200
    content = await response.text()
    assert content == 'protected'


@pytest.mark.config(TVM_ENABLED=True, TVM_DISABLE_CHECK=['example_service'])
async def test_disabled_service_check(call_handler):
    response = await call_handler()
    assert response.status == 200
    content = await response.text()
    assert content == 'protected'


@pytest.mark.config(TVM_ENABLED=False)
async def test_head_disabled_check(call_handler):
    response = await call_handler(method_name=HEAD)
    assert response.status == 200


@pytest.mark.config(TVM_ENABLED=True, TVM_DISABLE_CHECK=['example_service'])
async def test_head_disabled_service_check(call_handler):
    response = await call_handler(method_name=HEAD)
    assert response.status == 200
