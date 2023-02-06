import pytest

from taxi_corp import settings


@pytest.mark.parametrize(
    ['passport_mock', 'request_data', 'expected_create_chat'],
    [
        pytest.param(
            'client1',
            {
                'message': 'test',
                'message_id': '123',
                'type': 'text',
                'message_metadata': {'attachments': []},
            },
            {
                'owner_id': 'client1_null_client1_uid',
                'owner_role': 'corp_cabinet_client',
                'message_text': 'test',
                'message_sender_id': 'client1_null_client1_uid',
                'request_id': '123',
                'message_sender_role': 'corp_cabinet_client',
                'metadata': {
                    'client_id': 'client1',
                    'corp_client_contract_type': 'taxi',
                    'department_id': 'null',
                    'user_locale': 'en',
                },
                'message_metadata': {'attachments': []},
            },
        ),
        pytest.param(
            'manager1',
            {
                'message': 'test',
                'message_id': '123',
                'type': 'text',
                'message_metadata': {'attachments': []},
            },
            {
                'owner_id': 'client1_d1_1_manager1_uid',
                'owner_role': 'corp_cabinet_client',
                'message_text': 'test',
                'request_id': '123',
                'message_sender_id': 'client1_d1_1_manager1_uid',
                'message_sender_role': 'corp_cabinet_client',
                'metadata': {
                    'client_id': 'client1',
                    'corp_client_contract_type': 'taxi',
                    'department_id': 'd1_1',
                    'user_locale': 'en',
                },
                'message_metadata': {'attachments': []},
            },
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(LOCALES_CORP_SUPPORTED=['ru', 'en'])
async def test_add_user_message_happy_path(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        request_data,
        expected_create_chat,
):
    chat_id = 'some_chat_id'

    @patch('taxi.stq.client.put')
    async def _stq_put(*args, **kwargs):
        pass

    @patch('taxi.clients.support_chat.SupportChatApiClient.create_chat')
    async def _create_chat(*args, **kwargs):
        return {'id': chat_id}

    @patch('taxi.clients.support_chat.SupportChatApiClient.search')
    async def _search(*args, **kwargs):
        return {'chats': [{'id': chat_id}]}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/deprecated/support_chat/v1/realtime/add_user_message',
        json=request_data,
        headers={'Accept-Language': 'en'},
    )
    assert response.status == 200

    create_chat_calls = list(_create_chat.calls)
    assert len(create_chat_calls) == 1
    create_chat_kwargs = create_chat_calls[0]['kwargs']
    create_chat_kwargs.pop('log_extra', None)
    assert create_chat_kwargs == expected_create_chat

    # check STQ
    stq_put_calls = list(_stq_put.calls)
    assert len(stq_put_calls) == 1
    assert (
        stq_put_calls[0]['args'][0]
        == settings.STQ_CREATE_CHATTERBOX_TASK_FOR_CHAT_QUEUE
    )
    assert stq_put_calls[0]['kwargs']['kwargs']['chat_id'] == chat_id
    assert (
        stq_put_calls[0]['kwargs']['kwargs']['metadata']
        == expected_create_chat['metadata']
    )


@pytest.mark.parametrize(
    [
        'passport_mock',
        'request_data',
        'chat_id',
        'expected_add_update',
        'expected_stq_kwargs',
    ],
    [
        pytest.param(
            'manager1',
            {
                'message_id': '123',
                'type': 'csat',
                'message_key': 'bad',
                'reason_codes': ['long_answer', 'template_answer'],
            },
            'some_chat_id',
            {
                'chat_id': 'some_chat_id',
                'message_id': '123',
                'message_sender_id': 'client1_d1_1_manager1_uid',
                'message_sender_role': 'corp_cabinet_client',
                'update_metadata': {
                    'csat_value': 'bad',
                    'csat_reasons': ['long_answer', 'template_answer'],
                },
            },
            {
                'chat_id': 'some_chat_id',
                'metadata': {
                    'client_id': 'client1',
                    'corp_client_contract_type': 'taxi',
                    'department_id': 'd1_1',
                    'user_locale': 'en',
                    'csat_value': 'bad',
                    'csat_reasons': ['long_answer', 'template_answer'],
                },
                'hidden_comment': None,
            },
            id='csat',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(LOCALES_CORP_SUPPORTED=['ru', 'en'])
async def test_add_user_message_csat(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        request_data,
        chat_id,
        expected_add_update,
        expected_stq_kwargs,
):
    @patch('taxi.stq.client.put')
    async def _stq_put(*args, **kwargs):
        pass

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _add_update(*args, **kwargs):
        pass

    @patch('taxi.clients.support_chat.SupportChatApiClient.search')
    async def _search(*args, **kwargs):
        return {'chats': [{'id': chat_id}]}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/deprecated/support_chat/v1/realtime/add_user_message',
        json=request_data,
        headers={'Accept-Language': 'en'},
    )
    assert response.status == 200

    add_update_calls = list(_add_update.calls)
    assert len(add_update_calls) == 1
    add_update_kwargs = add_update_calls[0]['kwargs']
    add_update_kwargs.pop('log_extra', None)
    assert add_update_kwargs == expected_add_update

    # check STQ
    stq_put_calls = list(_stq_put.calls)
    assert len(stq_put_calls) == 1
    assert (
        stq_put_calls[0]['args'][0]
        == settings.STQ_CREATE_CHATTERBOX_TASK_FOR_CHAT_QUEUE
    )

    stq_put_kwargs = stq_put_calls[0]['kwargs']['kwargs']
    stq_put_kwargs.pop('log_extra', None)
    assert stq_put_kwargs == expected_stq_kwargs


@pytest.mark.parametrize(
    [
        'passport_mock',
        'owner_id',
        'search_response',
        'get_history_response',
        'expected',
    ],
    [
        pytest.param(
            'client1',
            'client1_null_client1_uid',
            {
                'chats': [
                    {
                        'id': 'some_chat_id',
                        'newest_message_id': 'uuid',
                        'participants': [
                            {
                                'id': 'support',
                                'role': 'support',
                                'avatar_url': '5',
                                'nickname': 'Служба поддержки',
                            },
                            {
                                'id': 'client1_null_client1_uid',
                                'role': 'corp_cabinet_client',
                            },
                        ],
                        'metadata': {
                            'created': '2019-01-01T01:01:00+0000',
                            'updated': '2019-01-01T01:01:00+0000',
                            'last_message_from_user': True,
                            'new_messages': 0,
                            'user_locale': 'en',
                            'ask_csat': False,
                            'chatterbox_id': 'some_chatterbox_id',
                        },
                        'status': {'is_open': True, 'is_visible': True},
                        'type': 'corp_cabinet_support',
                    },
                ],
            },
            {
                'messages': [
                    {
                        'id': 'message_id',
                        'text': 'test message',
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'mimetype': 'text/plain',
                                    'size': 14,
                                    'source': 'mds',
                                    'name': 'screenshot.jpg',
                                },
                            ],
                            'created': '2019-01-01T01:01:00+0000',
                        },
                        'sender': {
                            'id': 'client1_null_client1_uid',
                            'role': 'corp_cabinet_client',
                        },
                    },
                ],
                'total': 1,
                'new_message_count': 0,
                'newest_message_id': 'message_id',
                'metadata': {
                    'created': '2019-01-01T01:01:00+0000',
                    'updated': '2019-01-01T01:01:00+0000',
                    'last_message_from_user': True,
                    'new_messages': 0,
                    'user_locale': 'en',
                    'ask_csat': False,
                    'chatterbox_id': 'some_chatterbox_id',
                },
                'participants': [
                    {
                        'id': 'support',
                        'role': 'support',
                        'avatar_url': '5',
                        'nickname': 'Служба поддержки',
                    },
                    {
                        'id': 'client1_null_client1_uid',
                        'role': 'corp_cabinet_client',
                    },
                ],
            },
            {
                'ask_csat': False,
                'avatar_url': '5',
                'chat_id': 'some_chat_id',
                'chat_open': True,
                'chat_visible': True,
                'messages': [
                    {
                        'author': 'user',
                        'body': 'test message',
                        'id': 'message_id',
                        'metadata': {
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'link': 'support_chat/v1/realtime/some_chat_id/download_file/attachment_id',  # noqa: W605, E501 # pylint: disable=line-too-long
                                    'link_preview': 'support_chat/v1/realtime/some_chat_id/download_file/attachment_id?size=preview',  # noqa: W605, E501 # pylint: disable=line-too-long
                                    'mimetype': 'text/plain',
                                    'name': 'screenshot.jpg',
                                    'size': 14,
                                    'source': 'mds',
                                },
                            ],
                            'created': '2019-01-01T01:01:00+0000',
                        },
                        'sender': {
                            'id': 'client1_null_client1_uid',
                            'role': 'corp_cabinet_client',
                        },
                        'text': 'test message',
                        'timestamp': '2019-01-01T01:01:00+0000',
                        'type': 'text',
                    },
                ],
                'new_messages': 0,
                'participants': [
                    {
                        'avatar_url': '5',
                        'id': 'support',
                        'nickname': 'Служба поддержки',
                        'role': 'support',
                    },
                    {
                        'id': 'client1_null_client1_uid',
                        'role': 'corp_cabinet_client',
                    },
                ],
                'support_name': 'Служба поддержки',
            },
        ),
        pytest.param(
            'client1',
            'client1_null_client1_uid',
            {'chats': []},
            {},
            {
                'chat_id': 'dummy_chat_id',
                'chat_open': True,
                'chat_visible': True,
                'ask_csat': False,
                'new_messages': 0,
                'avatar_url': '',
                'support_name': '',
                'messages': [],
                'participants': [],
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_get_user_messages(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        owner_id,
        search_response,
        get_history_response,
        expected,
):
    @patch('taxi.clients.support_chat.SupportChatApiClient.search')
    async def _search(*args, **kwargs):
        return search_response

    @patch('taxi.clients.support_chat.SupportChatApiClient.get_history')
    async def _get_history(*args, **kwargs):
        return get_history_response

    response = await taxi_corp_real_auth_client.post(
        '/1.0/deprecated/support_chat/v1/realtime/get_user_messages',
        headers={'Accept-Language': 'en'},
    )
    assert response.status == 200
    assert await response.json() == expected

    search_calls = list(_search.calls)
    assert len(search_calls) == 1
    search_calls_kwargs = search_calls[0]['kwargs']
    assert search_calls_kwargs['owner_id'] == owner_id
    assert search_calls_kwargs['owner_role'] == 'corp_cabinet_client'
    assert search_calls_kwargs['chat_type'] == 'open'


# test_attach_file
# test_download_file


@pytest.mark.parametrize(
    ['passport_mock', 'chat_id', 'owner_id'],
    [pytest.param('client1', 'chat_id', 'client1_null_client1_uid')],
    indirect=['passport_mock'],
)
async def test_read(
        taxi_corp_real_auth_client, patch, passport_mock, chat_id, owner_id,
):
    @patch('taxi.clients.support_chat.SupportChatApiClient.read')
    async def _read(*args, **kwargs):
        pass

    response = await taxi_corp_real_auth_client.post(
        '/1.0/deprecated/support_chat/v1/realtime/read/{}'.format(chat_id),
        headers={'Accept-Language': 'en'},
    )
    assert response.status == 200

    read_calls = list(_read.calls)
    assert len(read_calls) == 1
    read_calls_kwargs = read_calls[0]['kwargs']
    assert read_calls_kwargs['chat_id'] == chat_id
    assert read_calls_kwargs['owner_id'] == owner_id
    assert read_calls_kwargs['owner_role'] == 'corp_cabinet_client'


@pytest.mark.parametrize(
    ['passport_mock', 'chat_id', 'owner_id'],
    [pytest.param('client1', 'dummy_chat_id', 'client1_null_client1_uid')],
    indirect=['passport_mock'],
)
async def test_read_dummy(
        taxi_corp_real_auth_client, patch, passport_mock, chat_id, owner_id,
):
    @patch('taxi.clients.support_chat.SupportChatApiClient.read')
    async def _read(*args, **kwargs):
        pass

    response = await taxi_corp_real_auth_client.post(
        '/1.0/deprecated/support_chat/v1/realtime/read/{}'.format(chat_id),
        headers={'Accept-Language': 'en'},
    )
    assert response.status == 200

    assert not _read.calls


@pytest.mark.parametrize(
    ['passport_mock', 'owner_id'],
    [pytest.param('client1', 'client1_null_client1_uid')],
    indirect=['passport_mock'],
)
async def test_summary(
        taxi_corp_real_auth_client, patch, passport_mock, owner_id,
):
    @patch('taxi.clients.support_chat.SupportChatApiClient.summary')
    async def _summary(*args, **kwargs):
        return {
            'open': True,
            'archive': False,
            'visible': True,
            'visible_chat_new_messages_count': 10,
        }

    response = await taxi_corp_real_auth_client.post(
        '/1.0/deprecated/support_chat/v1/realtime/summary',
        headers={'Accept-Language': 'en'},
    )
    assert response.status == 200
    assert await response.json() == {
        'open': True,
        'archive': False,
        'visible': True,
        'new_messages_count': 10,
    }

    summary_calls = list(_summary.calls)
    assert len(summary_calls) == 1
    summary_calls_kwargs = summary_calls[0]['kwargs']
    assert summary_calls_kwargs['owner_id'] == owner_id
    assert summary_calls_kwargs['owner_role'] == 'corp_cabinet_client'


@pytest.mark.parametrize(
    ['passport_mock'], [pytest.param('client1')], indirect=['passport_mock'],
)
async def test_download_file(taxi_corp_real_auth_client, passport_mock):

    response = await taxi_corp_real_auth_client.get(
        '/1.0/deprecated/support_chat/v1/realtime/chat_id123/download_file/attach_id456',  # noqa: W605, E501 # pylint: disable=line-too-long
    )
    assert response.status == 200
    assert response.headers['X-Accel-Redirect'] == (
        '/proxy-support-chat/v1/chat/chat_id123/attachment/attach_id456?'
        'sender_id=client1_null_client1_uid&sender_role=corp_cabinet_client'
    )


@pytest.mark.config(
    CORP_CABINET_SUPPORT_CHAT_ALLOWED_MIMETYPES=[
        'application/octet-stream',
        'text/plain',
    ],
)
@pytest.mark.parametrize(
    [
        'passport_mock',
        'owner_id',
        'request_data',
        'request_params',
        'content_type',
    ],
    [
        pytest.param(
            'client1',
            'client1_null_client1_uid',
            b'some text file',
            {'idempotency_token': 'token123', 'filename': 'some.txt'},
            'text/plain',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_attach_file(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        owner_id,
        request_data,
        request_params,
        content_type,
):
    @patch('taxi.clients.support_chat.SupportChatApiClient.attach_file')
    async def _attach_file(*args, **kwargs):
        return {'attachment_id': 'attachment_id123456'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/deprecated/support_chat/v1/realtime/attach_file',
        data=request_data,
        params=request_params,
    )
    assert response.status == 200

    attach_file_calls = list(_attach_file.calls)
    assert len(attach_file_calls) == 1
    attach_file_calls_kwargs = attach_file_calls[0]['kwargs']
    assert attach_file_calls_kwargs['sender_id'] == owner_id
    assert attach_file_calls_kwargs['sender_role'] == 'corp_cabinet_client'
    assert (
        attach_file_calls_kwargs['idempotency_token']
        == request_params['idempotency_token']
    )
    assert attach_file_calls_kwargs['filename'] == request_params['filename']
    assert attach_file_calls_kwargs['file'] == request_data
    assert attach_file_calls_kwargs['content_type'] == content_type
