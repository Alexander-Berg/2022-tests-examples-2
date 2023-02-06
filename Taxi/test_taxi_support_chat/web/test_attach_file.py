# pylint: disable=redefined-outer-name,no-member,protected-access
import datetime
import http

import pytest

from taxi.clients import mds_s3

from taxi_support_chat.api import attach_file


@pytest.mark.parametrize(
    (
        'chat_id',
        'sender_id',
        'sender_role',
        'file',
        'filename',
        'tmp_filename',
        'idempotency_token',
        'icap_response',
        'expected_key',
        'expected_status',
        'expected_result',
        'expected_icap_request',
    ),
    [
        (
            '5b436ca8779fb3302cc784bf',
            '5bbf8048779fb35d847fdb1e',
            'driver',
            b'test',
            'filename',
            'dummy',
            'test_token',
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0, res-body=44\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'\r\n'
                b'5\r\n'
                b'clean\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            '5bbf8048779fb35d847fdb1e_'
            'ce094fa09693604fb88de28e4876f8c38a5548d3',
            http.HTTPStatus.OK,
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            (
                b'REQMOD icap://av-tools-test/yavs ICAP/1.0\r\n'
                b'Host: av-tools-test\r\n'
                b'Encapsulated: req-body=0\r\n'
                b'\r\n'
                b'4\r\n'
                b'test\r\n'
                b'0\r\n'
                b'\r\n'
            ),
        ),
        (
            '5b436ca8779fb3302cc784bf',
            '5bbf8048779fb35d847fdb1e',
            'driver',
            b'test',
            'filename',
            'infected',
            'test_token',
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0, res-body=74\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            None,
            http.HTTPStatus.BAD_REQUEST,
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            (
                b'REQMOD icap://av-tools-test/yavs ICAP/1.0\r\n'
                b'Host: av-tools-test\r\n'
                b'Encapsulated: req-body=0\r\n'
                b'\r\n'
                b'4\r\n'
                b'test\r\n'
                b'0\r\n'
                b'\r\n'
            ),
        ),
        (
            '5b436ca8779fb3302cc784bf',
            '5bbf8048779fb35d847fdb1e',
            'driver',
            b'\x89PNG\r\n\x1a',
            'filename',
            'dummy',
            'test_token2',
            None,
            '5bbf8048779fb35d847fdb1e_'
            '3a27a28378ca2719087ec055dc1b1dd3279d36b3',
            http.HTTPStatus.OK,
            {'attachment_id': '3a27a28378ca2719087ec055dc1b1dd3279d36b3'},
            None,
        ),
        (
            '5b436ca8779fb3302cc784bf',
            '5bbf8048779fb35d847fdb1e',
            'support',
            b'\x89PNG\r\n\x1a',
            'filename',
            'dummy',
            'test_token2',
            None,
            'chatterbox_attachments/3a27a28378ca2719087ec055dc1b1dd3279d36b3',
            http.HTTPStatus.OK,
            {'attachment_id': '3a27a28378ca2719087ec055dc1b1dd3279d36b3'},
            None,
        ),
    ],
)
@pytest.mark.config(SUPPORT_CHAT_AV_CHECKED_MIMETYPES=['text/plain'])
async def test_attach_file(
        mock_asyncio_connection,
        mds_s3_client,
        web_app_client,
        chat_id,
        sender_id,
        sender_role,
        file,
        filename,
        tmp_filename,
        idempotency_token,
        icap_response,
        expected_key,
        expected_status,
        expected_result,
        expected_icap_request,
        mockserver,
):
    mocked_connection, _, mocked_writer = mock_asyncio_connection(
        mocked_host='av-tools-test', data_to_read=icap_response,
    )
    params = {
        'sender_id': sender_id,
        'sender_role': sender_role,
        'filename': filename,
        'idempotency_token': idempotency_token,
    }
    response = await web_app_client.post(
        '/v1/chat/attach_file', params=params, data=file,
    )
    assert response.status == expected_status

    if expected_status == http.HTTPStatus.OK:
        assert await response.json() == expected_result

    if expected_key:
        assert expected_key in mds_s3_client._storage

    if expected_icap_request is None:
        return

    (connect_call,) = mocked_connection.calls
    assert connect_call['host'] == 'av-tools-test'
    assert mocked_writer.data_written == expected_icap_request


async def test_image(stq, mds_s3_client, patch, web_app_client):
    async def _upload_content(
            key, body, content_type, metadata, additional_params,
    ):
        assert content_type == 'image/png'
        assert metadata == {
            'filename': 'filename',
            'width': '1',
            'height': '1',
            'preview_width': '1',
            'preview_height': '1',
        }
        return mds_s3.S3Object(Key=key, ETag='etag')

    mds_s3_client.upload_content = _upload_content

    sender_id = '5bbf8048779fb35d847fdb1e'
    sender_role = 'driver'
    expected_result = {
        'attachment_id': '3a27a28378ca2719087ec055dc1b1dd3279d36b3',
    }
    file = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'
        b'\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x04'
        b'gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00'
        b'\x16%\x00\x00\x16%\x01IR$\xf0\x00\x00\x00\rIDAT\x18Wc```\xf8'
        b'\x0f\x00\x01\x04\x01\x00p e\x0b\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    params = {
        'sender_id': sender_id,
        'sender_role': 'driver',
        'filename': 'filename',
        'idempotency_token': 'test_token2',
    }
    response = await web_app_client.post(
        '/v1/chat/attach_file', params=params, data=file,
    )
    assert response.status == http.HTTPStatus.OK
    assert await response.json() == expected_result

    call = stq.support_chat_generate_preview.next_call()
    assert call['kwargs']['sender_role'] == sender_role
    call.pop('kwargs')
    call.pop('id')
    assert call == {
        'queue': 'support_chat_generate_preview',
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'args': [sender_id, expected_result['attachment_id']],
    }


@pytest.mark.parametrize(
    'sampler_name', ('io_error_image.png', 'syntax_error_image.png'),
)
async def test_validate_image(
        web_app_client, stq, mds_s3_client, image_sampler_getter, sampler_name,
):
    async def _upload_content(
            key, body, content_type, metadata, additional_params,
    ):
        assert content_type == 'image/png'
        expected_metadata = {'filename': 'filename'}
        if sampler_name == 'syntax_error_image.png':
            expected_metadata.update(
                {
                    'width': '720',
                    'height': '720',
                    'preview_width': '150',
                    'preview_height': '150',
                },
            )

        assert metadata == expected_metadata

        return mds_s3.S3Object(Key=key, ETag='etag')

    mds_s3_client.upload_content = _upload_content

    file = image_sampler_getter(sampler_name)
    params = {
        'sender_id': '5bbf8048779fb35d847fdb1e',
        'sender_role': 'driver',
        'filename': 'filename',
        'idempotency_token': 'test_token2',
    }
    response = await web_app_client.post(
        '/v1/chat/attach_file', params=params, data=file,
    )
    assert response.status == http.HTTPStatus.OK
    assert stq.is_empty


@pytest.mark.parametrize(
    'width, height, expected_width, expected_height, expected_preview_width,'
    'expected_preview_height',
    [
        (1, 1, 150, 200, 1, 1),
        (1911, 642, 150, 200, 150, 50),
        (150, 200, 150, 200, 150, 200),
        (149, 199, 150, 200, 149, 199),
        (148, 579, 150, 200, 51, 200),
    ],
)
async def test_calc_preview(
        width,
        height,
        expected_width,
        expected_height,
        expected_preview_width,
        expected_preview_height,
):
    preview_width, preview_height = attach_file._calc_preview_size(
        width, height, expected_width, expected_height,
    )
    assert preview_height == expected_preview_height
    assert preview_width == expected_preview_width


@pytest.mark.parametrize(
    'file, exif_tag_added',
    [
        (
            (
                b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H'
                b'\x00H\x00\x00\xff\xdb\x00C\x00\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x0b\x08'
                b'\x00\x01\x00\x02\x01\x01\x11\x00\xff\xc4\x00\x14\x00'
                b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x03\xff\xc4\x00\x14\x10\x01\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00G\xff\xd9',
            ),
            False,
        ),
        (
            (
                b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H'
                b'\x00H\x00\x00\xff\xe1\x00bExif\x00\x00MM\x00*\x00'
                b'\x00\x00\x08\x00\x05\x01\x12\x00\x03\x00\x00\x00\x01'
                b'\x00\x06\x00\x00\x01\x1a\x00\x05\x00\x00\x00\x01\x00'
                b'\x00\x00J\x01\x1b\x00\x05\x00\x00\x00\x01\x00\x00'
                b'\x00R\x01(\x00\x03\x00\x00\x00\x01\x00\x02\x00\x00'
                b'\x02\x13\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00H\x00\x00\x00\x01\x00\x00'
                b'\x00H\x00\x00\x00\x01\xff\xdb\x00C\x00\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x0b'
                b'\x08\x00\x01\x00\x02\x01\x01\x11\x00\xff\xc4\x00\x14'
                b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x03\xff\xc4\x00\x14\x10\x01\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00G\xff\xd9',
            ),
            True,
        ),
    ],
)
async def test_reorient_image(
        file,
        exif_tag_added,
        web_context,
        mds_s3_client,
        web_app_client,
        patch,
):

    file = file[0]

    expected_width, expected_height = 2, 1
    if exif_tag_added:
        expected_width, expected_height = expected_height, expected_width

    async def _upload_content(
            key,
            body,
            content_type,
            metadata,
            additional_params,
            web_app_client,
    ):
        assert content_type == 'image/jpeg'
        assert metadata == {
            'filename': 'filename',
            'width': str(expected_width),
            'height': str(expected_height),
            'preview_width': str(expected_width),
            'preview_height': str(expected_height),
        }
        return mds_s3.S3Object(Key=key, ETag='etag')

    web_app_client.upload_content = _upload_content

    sender_id = '5bbf8048779fb35d847fdb1e'
    expected_result = {
        'attachment_id': '3a27a28378ca2719087ec055dc1b1dd3279d36b3',
    }

    params = {
        'sender_id': sender_id,
        'sender_role': 'driver',
        'filename': 'filename',
        'idempotency_token': 'test_token2',
    }
    response = await web_app_client.post(
        '/v1/chat/attach_file', params=params, data=file,
    )
    assert response.status == http.HTTPStatus.OK
    assert await response.json() == expected_result
