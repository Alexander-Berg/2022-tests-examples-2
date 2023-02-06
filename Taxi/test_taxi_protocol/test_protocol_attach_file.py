# pylint: disable=too-many-arguments
import hashlib
import json

import pytest

from taxi import discovery
from taxi.clients import tvm

from taxi_protocol import constants


@pytest.mark.config(
    CHAT_ATTACHMENT_ALLOWED_MIMETYPES={
        '__default__': ['text/plain'],
        'eats': ['application/octet-stream'],
    },
    PROTOCOL_ENABLE_DEBUG_INFO_FOR_ATTACH_FILE=True,
)
@pytest.mark.parametrize(
    [
        'chat_type',
        'chat_id',
        'file',
        'filename',
        'content_type',
        'idempotency_token',
        'expected_status',
        'expected_result',
        'expected_params',
    ],
    [
        (
            'regular',
            '5bcdb13084b5976d23aa01bb',
            b'test',
            'test_filename',
            'text/plain',
            'test_token',
            200,
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            {'sender_role': 'client', 'sender_id': '539eb65be7e5b1f53980dfa8'},
        ),
        (
            'realtime',
            '5bcdb13084b5976d23aa01bb',
            b'\x90\x01' * 10000,
            'test_filename',
            'application/octet-stream',
            'test_token',
            200,
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            {'sender_role': 'eats_client', 'sender_id': '12'},
        ),
        pytest.param(
            'realtime',
            '5bcdb13084b5976d23aa01bb',
            b'test',
            'test_filename',
            'text/plain',
            'test_token',
            200,
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            {'sender_role': 'eats_client', 'sender_id': '12'},
            marks=[
                pytest.mark.config(
                    CHAT_ATTACHMENT_ALLOWED_MIMETYPES={
                        '__default__': ['image/png', 'image/jpeg'],
                        'eats': ['text/plain'],
                    },
                ),
            ],
        ),
        pytest.param(
            'realtime',
            '5bcdb13084b5976d23aa01bb',
            b'\x90\x01' * 10000,
            'test_filename',
            'application/octet-stream',
            'test_token',
            400,
            None,
            {'sender_role': 'eats_client', 'sender_id': '12'},
            marks=[
                pytest.mark.config(
                    CHAT_ATTACHMENT_ALLOWED_MIMETYPES={
                        '__default__': ['text/plain'],
                        'eats': ['image/png', 'image/jpeg'],
                    },
                ),
            ],
        ),
    ],
)
async def test_protocol_attach_file(
        protocol_client,
        response_mock,
        mock_get_users,
        patch_aiohttp_session,
        chat_type,
        chat_id,
        file,
        filename,
        content_type,
        idempotency_token,
        expected_status,
        expected_result,
        expected_params,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def _dummy_request(method, url, **kwargs):
        assert method == 'post'
        assert (
            url == 'http://support-chat.taxi.dev.yandex.net/v1/'
            'chat/attach_file'
        )
        assert kwargs['data'] == file
        assert kwargs['headers']['Content-Type'] == content_type

        assert kwargs['params'] == {
            **expected_params,
            'filename': filename,
            'idempotency_token': idempotency_token,
        }
        return response_mock(
            json={
                'attachment_id': (
                    hashlib.sha1(idempotency_token.encode('utf-8')).hexdigest()
                ),
            },
        )

    params = {
        'filename': filename,
        'idempotency_token': idempotency_token,
        'db': '59de5222293145d09d31cd1604f8f656',
    }
    headers = {
        'X-Real-IP': '1.1.1.1',
        constants.YANDEX_UID_HEADER: '12',
        'X-YaTaxi-UserId': '5ff4901c583745e089e55be4',
    }
    response = await protocol_client.post(
        '/4.0/support_chat/v1/{0}/attach_file'.format(chat_type),
        data=file,
        params=params,
        headers=headers,
    )
    assert response.status == expected_status
    if expected_result:
        assert await response.json() == expected_result


@pytest.mark.config(
    CHAT_ATTACHMENT_ALLOWED_MIMETYPES={
        '__default__': ['application/octet-stream', 'text/plain'],
    },
)
@pytest.mark.parametrize(
    ['chat_type', 'file', 'filename', 'idempotency_token', 'expected_result'],
    [
        (
            'regular',
            b'test',
            'test_filename',
            'test_token',
            {'error': 'File test_filename is infected'},
        ),
        (
            'realtime',
            b'\x90\x01' * 10000,
            'test_filename',
            'test_token',
            {'error': 'File test_filename is infected'},
        ),
    ],
)
async def test_protocol_attach_error(
        protocol_client,
        response_mock,
        mock_get_users,
        patch_aiohttp_session,
        chat_type,
        file,
        filename,
        idempotency_token,
        expected_result,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def _dummy_request(method, url, **kwargs):
        return response_mock(
            text=json.dumps({'error': {'reason_code': 'infected'}}),
            status=400,
        )

    params = {
        'filename': filename,
        'idempotency_token': idempotency_token,
        'db': '59de5222293145d09d31cd1604f8f656',
    }
    headers = {
        'X-Real-IP': '1.1.1.1',
        constants.YANDEX_UID_HEADER: '12',
        'X-YaTaxi-UserId': '5ff4901c583745e089e55be4',
    }
    response = await protocol_client.post(
        '/4.0/support_chat/v1/{0}/attach_file'.format(chat_type),
        data=file,
        params=params,
        headers=headers,
    )
    assert response.status == 400
    assert await response.json() == expected_result


@pytest.mark.config(
    TVM_RULES=[{'src': 'protocol-py3', 'dst': 'support_chat'}],
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    ['chat_type', 'chat_id', 'attachment_id', 'preview', 'expected_redirect'],
    [
        (
            'regular',
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            False,
            '/v1/chat/5c504337779fb336b89182a2/attachment/'
            'b444ac06613fc8d63795be9ad0beaf55011936ac'
            '?sender_id=539eb65be7e5b1f53980dfa8&sender_role=client',
        ),
        (
            'realtime',
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            False,
            '/v1/chat/5c504337779fb336b89182a2/attachment/'
            'b444ac06613fc8d63795be9ad0beaf55011936ac'
            '?sender_id=12&sender_role=eats_client',
        ),
        (
            'regular',
            '5c504337779fb336b89182a3',
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f',
            True,
            '/v1/chat/5c504337779fb336b89182a3/attachment/'
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f'
            '?sender_id=539eb65be7e5b1f53980dfa8&sender_role=client'
            '&size=preview',
        ),
        (
            'realtime',
            '5c504337779fb336b89182a3',
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f',
            True,
            '/v1/chat/5c504337779fb336b89182a3/attachment/'
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f'
            '?sender_id=12&sender_role=eats_client&size=preview',
        ),
    ],
)
async def test_download_file(
        protocol_client,
        mock_get_users,
        patch,
        chat_type,
        chat_id,
        attachment_id,
        preview,
        expected_redirect,
):
    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def _get_ticket(*args, **kwargs):
        return 'Ticket 123'

    @patch('taxi.clients.tvm.check_tvm')
    async def _check_tvm(*args, **kwargs):
        return tvm.CheckResult(src_service_name='api-python')

    params = {}
    if preview:
        params['size'] = 'preview'
    headers = {
        'X-Real-IP': '1.1.1.1',
        constants.YANDEX_UID_HEADER: '12',
        'X-YaTaxi-UserId': '5ff4901c583745e089e55be4',
        'X-Ya-Service-Ticket': 'Ticket 123',
    }
    url = '/4.0/support_chat/v1/{type}/{chat}/download_file/{attachment}'
    response = await protocol_client.get(
        url.format(type=chat_type, chat=chat_id, attachment=attachment_id),
        params=params,
        headers=headers,
    )
    assert response.status == 200
    assert response.headers['X-Accel-Redirect'] == expected_redirect
    assert response.headers['X-Ya-Service-Ticket'] == 'Ticket 123'
