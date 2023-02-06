import io

import aiohttp
import pytest

from taxi.clients import http_client
from taxi.clients import tvm
from taxi.clients import vh
from taxi.clients.helpers import errors


VH_HOST = '$mockserver/vh-api'


@pytest.fixture(name='tvm_client')
def tvm_client_fixture(patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='vh', secdist=None, config=None, session=None,
    )


@pytest.fixture(name='vh_client')
def vh_client_fixture(tvm_client):
    return vh.VhClient(
        tvm_client=tvm_client,
        session=http_client.HTTPClient(),
        vh_host=VH_HOST,
    )


@pytest.fixture(name='mock_handles_for_ok')
def mock_handles(mockserver):
    @mockserver.json_handler('vh-api/v1/upload')
    async def _upload(request):
        return {
            'metadata': {'metadata_key': 'metadata_value'},
            'endpoint': f'{VH_HOST}/some_endpoint',
        }

    @mockserver.json_handler('vh-api/some_endpoint')
    async def _some_endpoint(request):
        return {'location': f'{VH_HOST}/tus_endpoint'}

    @mockserver.json_handler('vh-api/tus_endpoint')
    async def _tus_endpoint(request):
        return aiohttp.web.Response(
            headers={'Location': f'{VH_HOST}/file_endpoint'}, status=201,
        )

    @mockserver.json_handler('vh-api/file_endpoint')
    async def _file_endpoint(request):
        if request.method == 'HEAD':
            return aiohttp.web.Response(
                headers={'Upload-Offset': '0'}, status=201,
            )
        if request.method == 'PATCH':
            return aiohttp.web.Response(status=204)


@pytest.mark.parametrize(
    ['endpoint', 'method', 'err_str'],
    [
        ('v1/upload', 'POST', None),
        ('some_endpoint', 'GET', None),
        ('tus_endpoint', 'POST', 'TusError(Create failed)'),
        ('file_endpoint', 'HEAD', 'TusError(Get offset failed)'),
        ('file_endpoint', 'PATCH', 'TusError(Upload chunk failed)'),
    ],
)
async def test_endpoint_fail(
        vh_client, mock_handles_for_ok, mockserver, endpoint, method, err_str,
):
    reason = (
        err_str or f'Error in request to "{endpoint}" with method {method}'
    )

    @mockserver.handler(f'/vh-api/{endpoint}')
    async def _handler(request):
        if request.method == method:
            return aiohttp.web.Response(status=500, reason=reason)
        # для мока file_endpoint и метода PATCH
        # чтобы не упало слишком рано
        if request.method == 'HEAD':
            return aiohttp.web.Response(
                headers={'Upload-Offset': '0'}, status=201,
            )

    try:
        await vh_client.upload(content=io.BytesIO(b'123'), key='key')
    except aiohttp.ClientResponseError as err:
        assert err.message == reason
    except vh.TusError as err:
        assert str(err) == reason
    except errors.BaseError as err:
        assert str(err.__cause__) == reason
    else:
        assert False


async def test_retries_negative(vh_client):
    try:
        await vh_client.upload(
            content=io.BytesIO(b'123'), key='key', retries_count=-1,
        )
    except AttributeError as err:
        assert str(err) == 'retry_number cannot be negative'
    else:
        assert False


async def test_all_ok(vh_client, mock_handles_for_ok, mockserver):
    sent_bytes = io.BytesIO()

    @mockserver.json_handler('vh-api/file_endpoint')
    async def _file_endpoint(request):
        if request.method == 'HEAD':
            return aiohttp.web.Response(
                headers={'Upload-Offset': '0'}, status=201,
            )
        if request.method == 'PATCH':
            sent_bytes.write(request.get_data())
            return aiohttp.web.Response(status=204)

    data_to_send = io.BytesIO(b'123')
    key = await vh_client.upload(
        content=data_to_send,
        file_name='some_file_name.mp4',
        key='key',
        chunk_size=1,
        retries_count=0,
    )
    assert key == 'key'
    assert data_to_send.getvalue() == sent_bytes.getvalue()


async def test_upload_chunk_continue(
        vh_client, mock_handles_for_ok, mockserver,
):
    upload_callc_count = 0
    errors_count = 0
    sent_bytes = io.BytesIO()

    @mockserver.json_handler('vh-api/file_endpoint')
    async def _file_endpoint(request):
        nonlocal upload_callc_count, errors_count
        if request.method == 'HEAD':
            return aiohttp.web.Response(
                headers={'Upload-Offset': f'{errors_count}'}, status=201,
            )
        if request.method == 'PATCH':
            upload_callc_count += 1
            if upload_callc_count % 2 == 0:
                errors_count += 1
                return aiohttp.web.Response(status=500)
            sent_bytes.write(request.get_data())
            return aiohttp.web.Response(status=204)

    data_to_send = io.BytesIO(b'123')
    key = await vh_client.upload(
        content=data_to_send,
        file_name='some_file_name.mp4',
        key='key',
        chunk_size=1,
        retries_count=3,
    )
    assert key == 'key'
    assert data_to_send.getvalue() == sent_bytes.getvalue()
