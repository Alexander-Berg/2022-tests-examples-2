# pylint: disable=protected-access
import multidict
import pytest

from taxi_tests import http
from taxi_tests.plugins import mockserver as mockserver_mod


class DummyRequest:
    def __init__(self, headers):
        self.headers = multidict.CIMultiDict(headers)


async def test_example(mockserver, mockserver_client):
    @mockserver.handler('/foo')
    def handler(request):
        raise mockserver.TimeoutError()

    response = await mockserver_client.get(
        'foo', headers={'X-Testsuite-Supported-Errors': 'network,timeout'},
    )
    assert response.status == 599
    assert response.headers['X-Testsuite-Error'] == 'timeout'


@pytest.mark.parametrize(
    'exc_class,error_code',
    [(http.TimeoutError, 'timeout'), (http.NetworkError, 'network')],
)
async def test_mockserver_error(
        mockserver, mockserver_client, exc_class, error_code,
):
    @mockserver.handler('/foo')
    def handler(request):
        raise exc_class

    response = await mockserver_client.get(
        'foo', headers={'X-Testsuite-Supported-Errors': 'network,timeout'},
    )
    assert response.status == 599
    assert response.headers['X-Testsuite-Error'] == error_code


@pytest.mark.parametrize(
    'http_request,error_code,message',
    [
        (
            DummyRequest({}),
            'foo',
            'Service does not support mockserver errors protocol',
        ),
        (
            DummyRequest({'X-Testsuite-Supported-Errors': 'foo,bar'}),
            'maurice',
            'Service does not support mockserver error of type maurice',
        ),
    ],
)
def test_mocked_error_fail(http_request, error_code, message):
    with pytest.raises(mockserver_mod.MockServerError) as exc:
        mockserver_mod._mocked_error_response(http_request, error_code)
    assert str(exc.value) == message
