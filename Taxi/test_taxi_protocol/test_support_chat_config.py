import pytest

from taxi_protocol import constants


@pytest.mark.config(
    PROTOCOL_HIDE_NOT_SOLVED={
        'realtime': ['good', 'amazing'],
        '__default__': [],
    },
    PROTOCOL_ALLOW_UPLOAD_FILES={
        'realtime': False,
        'regular': True,
        '__default__': False,
    },
)
@pytest.mark.parametrize(
    ['url', 'expected_result', 'auth_header'],
    [
        (
            '/4.0/support_chat/v1/regular/config',
            {
                'allow_upload_files': True,
                'allowed_file_mime_types': ['image/png', 'image/jpeg'],
                'options_when_hide_not_solved': [],
                'picture_preview': {'height': 200, 'width': 150},
                'update_timeout': 60000,
            },
            '5ff4901c583745e089e55be4',
        ),
        (
            '/4.0/support_chat/v1/regular/config',
            {
                'allow_upload_files': False,
                'allowed_file_mime_types': ['image/png', 'image/jpeg'],
                'options_when_hide_not_solved': [],
                'picture_preview': {'height': 200, 'width': 150},
                'update_timeout': 60000,
            },
            '5ff4901c583745e089e55be5',
        ),
        (
            '/4.0/support_chat/v1/regular/config',
            {
                'allow_upload_files': False,
                'allowed_file_mime_types': ['image/png', 'image/jpeg'],
                'options_when_hide_not_solved': [],
                'picture_preview': {'height': 200, 'width': 150},
                'update_timeout': 60000,
            },
            '5ff4901c583745e089e55be6',
        ),
        (
            '/4.0/support_chat/v1/realtime/config',
            {
                'allow_upload_files': False,
                'allowed_file_mime_types': ['image/png', 'image/jpeg'],
                'options_when_hide_not_solved': ['good', 'amazing'],
                'picture_preview': {'height': 200, 'width': 150},
                'update_timeout': 60000,
            },
            '5ff4901c583745e089e55be7',
        ),
        (
            '/4.0/support_chat/v1/regular/config',
            {
                'allow_upload_files': False,
                'allowed_file_mime_types': ['image/png', 'image/jpeg'],
                'options_when_hide_not_solved': [],
                'picture_preview': {'height': 200, 'width': 150},
                'update_timeout': 60000,
            },
            '5ff4901c583745e089e55bb3',
        ),
        pytest.param(
            '/4.0/support_chat/v1/realtime/config',
            {
                'allow_upload_files': False,
                'allowed_file_mime_types': ['text/plain'],
                'options_when_hide_not_solved': ['good', 'amazing'],
                'picture_preview': {'height': 200, 'width': 150},
                'update_timeout': 60000,
            },
            '5ff4901c583745e089e55be7',
            marks=[
                pytest.mark.config(
                    CHAT_ATTACHMENT_ALLOWED_MIMETYPES={
                        '__default__': ['image/png', 'image/jpeg'],
                        'eats': ['text/plain'],
                    },
                ),
            ],
        ),
    ],
)
async def test_get_config(
        protocol_client, mock_get_users, url, expected_result, auth_header,
):
    response = await protocol_client.get(
        url,
        headers={
            'X-Real-IP': '1.1.1.1',
            constants.YANDEX_UID_HEADER: auth_header,
            'X-YaTaxi-UserId': auth_header,
        },
    )
    assert response.status == 200
    assert await response.json() == expected_result
