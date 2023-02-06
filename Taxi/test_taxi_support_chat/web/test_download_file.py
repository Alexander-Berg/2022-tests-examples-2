import http

import pytest


async def test_invalid_id(web_app_client, mock_tvm_keys):
    params = {'sender_id': 'owner_id', 'sender_role': 'client'}
    response = await web_app_client.get(
        '/v1/chat/not_found_id/attachment/attachment_id', params=params,
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST

    response = await web_app_client.get(
        '/v1/chat/not_found_id/attachment/attachment_id',
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    'chat_id,attachment_id,sender_id,sender_role',
    [
        ('5b436ca8779fb3302cc784bc', 'attachment_id', 'sender_id', 'client'),
        ('5b436ca8779fb3302cc784ba', 'attachment_id', 'sender_id', 'client'),
        ('5b436ca8779fb3302cc784bc', 'attachment_id1', 'sender_id', 'client'),
        ('5b436ca8779fb3302cc784ba', 'attachment_id1', 'sender_id', 'client'),
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id1',
            '5b4f5059779fb332fcc26152',
            'driver',
        ),
    ],
)
async def test_not_found(
        web_app_client,
        mock_tvm_keys,
        chat_id,
        attachment_id,
        sender_id,
        sender_role,
):
    params = {'sender_id': sender_id, 'sender_role': sender_role}
    response = await web_app_client.get(
        '/v1/chat/%s/attachment/%s' % (chat_id, attachment_id), params=params,
    )
    assert response.status == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'service_ticket,chat_id,expected_status',
    [
        (
            'backend_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.OK,
        ),
        (
            'backend_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.NOT_FOUND,
        ),
        (
            'disp_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.FORBIDDEN,
        ),
        (
            'disp_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.NOT_FOUND,
        ),
        (
            'corp_service_ticket',
            '5b436ca8779fb3302cc784bf',
            http.HTTPStatus.NOT_FOUND,
        ),
        (
            'corp_service_ticket',
            '5b436ca8779fb3302cc784ba',
            http.HTTPStatus.FORBIDDEN,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_chat_type_access(
        web_app_client,
        mock_tvm_keys,
        service_ticket,
        chat_id,
        expected_status,
):
    params = {'sender_id': '5b4f5059779fb332fcc26152', 'sender_role': 'client'}
    response = await web_app_client.get(
        '/v1/chat/{}/attachment/attachment_id1'.format(chat_id),
        params=params,
        headers={'X-Ya-Service-Ticket': service_ticket},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'chat_id,attachment_id,sender_id,sender_role,preview,expected_redirect',
    [
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id1',
            '5b4f5059779fb332fcc26152',
            'client',
            False,
            '/attachments/some_user_id_attachment_id1',
        ),
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id1',
            '5b4f5059779fb332fcc26152',
            'client',
            True,
            '/attachments/some_user_id_attachment_id1_preview',
        ),
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id1',
            'test_user',
            'support',
            False,
            '/attachments/some_user_id_attachment_id1',
        ),
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id1',
            'test_user',
            'support',
            True,
            '/attachments/some_user_id_attachment_id1_preview',
        ),
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id2',
            '5b4f5059779fb332fcc26152',
            'client',
            False,
            '/attachments/chatterbox_attachments/attachment_id2',
        ),
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id2',
            '5b4f5059779fb332fcc26152',
            'client',
            True,
            '/attachments/chatterbox_attachments/attachment_id2_preview',
        ),
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id2',
            'test_user',
            'support',
            False,
            '/attachments/chatterbox_attachments/attachment_id2',
        ),
        (
            '5b436ca8779fb3302cc784ba',
            'attachment_id2',
            'test_user',
            'support',
            True,
            '/attachments/chatterbox_attachments/attachment_id2_preview',
        ),
    ],
)
async def test_download(
        web_app_client,
        mock_tvm_keys,
        chat_id,
        attachment_id,
        sender_id,
        sender_role,
        preview,
        expected_redirect,
):
    params = {'sender_id': sender_id, 'sender_role': sender_role}
    if preview:
        params['size'] = 'preview'
    response = await web_app_client.get(
        '/v1/chat/%s/attachment/%s' % (chat_id, attachment_id), params=params,
    )
    assert response.status == http.HTTPStatus.OK
    assert response.headers['X-Accel-Redirect'] == expected_redirect
