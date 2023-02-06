# pylint:disable=too-many-arguments, redefined-outer-name
# pylint: disable=too-many-lines, unused-variable
import datetime
import hashlib

import pytest

from taxi import discovery
from taxi.clients import tvm

from test_taxi_driver_support import conftest

UNIQUE_DRIVER_ID = '5bc702f995572fa0df26e0e2'
NOW = datetime.datetime(2018, 10, 1, 0, 0)
THREE_MONTHS_AGO = '2018-07-03T03:00:00+0300'


DAP_APP_HEADERS = {
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.61 (1234)',
}


@pytest.fixture
def mock_selfreg_validate(mockserver):
    @mockserver.json_handler('/selfreg-api/internal/selfreg/v1/validate')
    def _dummy_validate(request):
        if 'bad' in request.query['token']:
            return mockserver.make_response(json={}, status=404)
        return {
            'selfreg_id': 'some_selfreg_id',
            'city_id': 'Moscow',
            'mock_tags': ['some', 'tags'],
        }

    return _dummy_validate


@pytest.fixture
def mock_get_chat(taxi_driver_support_app, monkeypatch, mock):
    @mock
    async def _dummy_get_chat(*args, **kwargs):
        return {
            'id': '5bcdb13084b5976d23aa01bb',
            'participants': [],
            'status': {'is_open': True, 'is_visible': True},
        }

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'get_chat',
        _dummy_get_chat,
    )
    return _dummy_get_chat


@pytest.fixture
def mock_search(taxi_driver_support_app, monkeypatch, mock):
    @mock
    async def _dummy_search(*args, **kwargs):
        return {
            'chats': [
                {
                    'id': '5bcdb13084b5976d23aa01bb',
                    'participants': [],
                    'status': {'is_open': True, 'is_visible': True},
                },
            ],
        }

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client, 'search', _dummy_search,
    )
    return _dummy_search


@pytest.fixture
def mock_get_history(taxi_driver_support_app, monkeypatch, mock):
    def _wrap(owner_id, owner_role, meta: dict = None):
        @mock
        async def _dummy_get_history(*args, **kwargs):
            response = {
                'new_message_count': 0,
                'messages': [
                    {
                        'text': 'test_text',
                        'sender': {'role': 'support', 'id': 'support'},
                    },
                    {
                        'sender': {'role': owner_role, 'id': owner_id},
                        'text': 'tt',
                        'metadata': {
                            'created': THREE_MONTHS_AGO,
                            'attachments': [{'id': 'test_id'}],
                        },
                    },
                ],
                'total': 0,
                'participants': [{'id': owner_id, 'role': owner_role}],
                'metadata': {'ask_csat': True, 'user_locale': 'ru'},
            }
            if meta:
                response['metadata'].update(meta)
            return response

        monkeypatch.setattr(
            taxi_driver_support_app.support_chat_client,
            'get_history',
            _dummy_get_history,
        )
        return _dummy_get_history

    return _wrap


@pytest.fixture
def mock_read(taxi_driver_support_app, monkeypatch, mock):
    @mock
    async def _dummy_read(*args, **kwargs):
        return {}

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client, 'read', _dummy_read,
    )
    return _dummy_read


@pytest.fixture
def mock_add_update(taxi_driver_support_app, monkeypatch, mock):
    @mock
    async def _dummy_add_update(*args, **kwargs):
        return {}

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'add_update',
        _dummy_add_update,
    )
    return _dummy_add_update


@pytest.fixture
def mock_get_order_by_id(patch):
    @patch('taxi.clients.order_archive.OrderArchiveClient.get_order_by_id')
    async def _dummy_get_order_by_id(*args, **kwargs):
        return {'_id': 'some_order_id'}

    return _dummy_get_order_by_id


@pytest.fixture
def mock_get_order_by_id_old(taxi_driver_support_app, monkeypatch, mock):
    @mock
    async def _dummy_get_order_by_id(*args, **kwargs):
        return {'_id': 'some_order_id'}

    monkeypatch.setattr(
        taxi_driver_support_app.archive_api_client,
        'get_order_by_id',
        _dummy_get_order_by_id,
    )
    return _dummy_get_order_by_id


@pytest.mark.config(USE_ORDER_ARCHIVE_FOR_GETTING_ORDER_ID=False)
@pytest.mark.parametrize(
    'park_id,session,headers,message,metadata,expected_create_data,'
    'expected_stq_data,is_exported',
    [
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_session',
            {},
            {'text': 'test message'},
            None,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'user_application': 'taximeter',
                'user_country': 'rus',
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {'text': 'test message'},
                'platform': 'taximeter',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'tags': [],
            },
            False,
        ),
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_session',
            {'user-agent': 'taximeter-uber'},
            {
                'text': 'test message',
                'metadata': {
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1'},
                        {'id': 'attachment_id_2'},
                    ],
                    'work_mode': 'online',
                },
            },
            None,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'order_id': 'some_order_id',
                    'work_mode': 'online',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': {
                    'order_id': 'some_order_id',
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1', 'source': 'mds'},
                        {'id': 'attachment_id_2', 'source': 'mds'},
                    ],
                    'work_mode': 'online',
                },
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'uberdriver',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'user_application': 'taximeter',
                'user_country': 'rus',
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {
                    'text': 'test message',
                    'metadata': {
                        'order_id': 'some_order_id',
                        'order_alias_id': 'some_alias_id',
                        'ticket_subject': 'ticket subject',
                        'attachments': [
                            {'id': 'attachment_id_1', 'source': 'mds'},
                            {'id': 'attachment_id_2', 'source': 'mds'},
                        ],
                        'work_mode': 'online',
                    },
                },
                'platform': 'uberdriver',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'order_id': 'some_order_id',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'work_mode': 'online',
                    'owner_type': 'unique_driver',
                },
                'tags': [],
            },
            False,
        ),
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_session',
            {'user-agent': 'taximeter-uber'},
            {
                'text': 'test message',
                'metadata': {
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1'},
                        {'id': 'attachment_id_2'},
                    ],
                    'driver_on_order': True,
                },
            },
            None,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'order_id': 'some_order_id',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': {
                    'order_id': 'some_order_id',
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1', 'source': 'mds'},
                        {'id': 'attachment_id_2', 'source': 'mds'},
                    ],
                    'driver_on_order': True,
                },
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'uberdriver',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'user_application': 'taximeter',
                'user_country': 'rus',
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {
                    'text': 'test message',
                    'metadata': {
                        'order_id': 'some_order_id',
                        'order_alias_id': 'some_alias_id',
                        'ticket_subject': 'ticket subject',
                        'attachments': [
                            {'id': 'attachment_id_1', 'source': 'mds'},
                            {'id': 'attachment_id_2', 'source': 'mds'},
                        ],
                        'driver_on_order': True,
                    },
                },
                'platform': 'uberdriver',
                'metadata': {
                    'owner_type': 'unique_driver',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'order_id': 'some_order_id',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                },
                'tags': ['driver_on_order'],
            },
            False,
        ),
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_session',
            {'user-agent': 'taximeter-uber'},
            {
                'text': 'test message',
                'metadata': {
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1'},
                        {'id': 'attachment_id_2'},
                    ],
                    'source': 'history',
                    'driver_on_order': False,
                },
            },
            None,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'appeal_source': 'history',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'order_id': 'some_order_id',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': {
                    'appeal_source': 'history',
                    'order_id': 'some_order_id',
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1', 'source': 'mds'},
                        {'id': 'attachment_id_2', 'source': 'mds'},
                    ],
                    'driver_on_order': False,
                },
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'uberdriver',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'user_application': 'taximeter',
                'user_country': 'rus',
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {
                    'text': 'test message',
                    'metadata': {
                        'order_id': 'some_order_id',
                        'order_alias_id': 'some_alias_id',
                        'ticket_subject': 'ticket subject',
                        'attachments': [
                            {'id': 'attachment_id_1', 'source': 'mds'},
                            {'id': 'attachment_id_2', 'source': 'mds'},
                        ],
                        'driver_on_order': False,
                        'appeal_source': 'history',
                    },
                },
                'platform': 'uberdriver',
                'metadata': {
                    'appeal_source': 'history',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'order_id': 'some_order_id',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'tags': [],
            },
            False,
        ),
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_session',
            {},
            {'text': 'test message'},
            {'csat_reasons': ['metadata']},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'csat_reasons': ['metadata'],
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {'text': 'test message'},
                'platform': 'taximeter',
                'metadata': {
                    'csat_reasons': ['metadata'],
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_application': 'taximeter',
                    'owner_type': 'unique_driver',
                    'user_country': 'rus',
                    'user_locale': 'en',
                },
                'tags': [],
            },
            False,
        ),
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_session',
            {'user-agent': 'taximeter-vezet'},
            None,
            {'csat_reasons': ['fast answer'], 'csat_value': 'amazing'},
            None,
            {
                'args': (
                    '5bcdb13084b5976d23aa01bb',
                    '5bc702f995572fa0df26e0e2',
                ),
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {},
                'platform': 'vezet',
                'metadata': {
                    'csat_reasons': ['fast answer'],
                    'csat_value': 'amazing',
                    'owner_type': 'unique_driver',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                },
                'tags': [],
            },
            False,
        ),
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_session',
            {'user-agent': 'taximeter-vezet'},
            None,
            {
                'csat_values': {
                    'questions': [
                        {
                            'id': 'question_id_1',
                            'value': {
                                'id': 'answer_id',
                                'comment': 'user comment text',
                                'reasons': [
                                    {'id': 'reason_id_1'},
                                    {'id': 'reason_id_2'},
                                ],
                            },
                        },
                        {
                            'id': 'question_id_2',
                            'value': {
                                'id': 'answer_id',
                                'reasons': [
                                    {'id': 'reason_id_1'},
                                    {
                                        'id': 'reason_id_2',
                                        'reasons': [{'id': 'sub_reason_id'}],
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            None,
            {
                'args': (
                    '5bcdb13084b5976d23aa01bb',
                    '5bc702f995572fa0df26e0e2',
                ),
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {},
                'platform': 'vezet',
                'metadata': {
                    'owner_type': 'unique_driver',
                    'csat_values': {
                        'questions': [
                            {
                                'id': 'question_id_1',
                                'value': {
                                    'id': 'answer_id',
                                    'comment': 'user comment text',
                                    'reasons': [
                                        {'id': 'reason_id_1'},
                                        {'id': 'reason_id_2'},
                                    ],
                                },
                            },
                            {
                                'id': 'question_id_2',
                                'value': {
                                    'id': 'answer_id',
                                    'reasons': [
                                        {'id': 'reason_id_1'},
                                        {
                                            'id': 'reason_id_2',
                                            'reasons': [
                                                {'id': 'sub_reason_id'},
                                            ],
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                },
                'tags': [],
            },
            False,
        ),
    ],
)
async def test_add_message(
        monkeypatch,
        mock,
        mock_stq_put,
        mock_driver_session,
        mock_add_update,
        mock_search,
        mock_get_order_by_id_old,
        mock_driver_profiles,
        mock_personal,
        taxi_driver_support_client,
        taxi_driver_support_app,
        park_id,
        session,
        headers,
        message,
        metadata,
        expected_create_data,
        expected_stq_data,
        is_exported,
        patch_additional_meta,
):
    # pylint: disable=too-many-locals
    additional_meta_calls = patch_additional_meta(
        metadata={'park_country': 'rus'},
    )

    @mock
    async def _dummy_create_chat(*args, **kwargs):
        data = {'id': 'dummy_chat_id', 'newest_message_id': 'new_message_id'}
        if is_exported:
            data['metadata'] = {'ticket_id': '1', 'author_id': '1'}
        return data

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'create_chat',
        _dummy_create_chat,
    )

    request_data = {'request_id': 'dummy_request_id', 'db': park_id}
    if message:
        request_data['message'] = message
    headers.update({'Authorization': session, 'Accept-Language': 'en'})
    if metadata is not None:
        request_data['metadata'] = metadata

    response = await taxi_driver_support_client.post(
        '/v1/support_chat/add_message', json=request_data, headers=headers,
    )
    assert response.status == 200
    assert additional_meta_calls

    create_chat_calls = _dummy_create_chat.calls
    if create_chat_calls:
        support_chat_call = create_chat_calls[0]
        for key, value in expected_create_data.items():
            assert support_chat_call['kwargs'][key] == value
    else:
        support_chat_call = mock_search.calls[0]
        assert support_chat_call
        assert support_chat_call['kwargs']['platform']
        assert mock_add_update.calls[0]

    stq_put_call = mock_stq_put.calls[0]
    if is_exported:
        assert stq_put_call['args'] == expected_stq_data
    else:
        assert stq_put_call['args'] == expected_stq_data['args']
        for key in (
                'db_id',
                'driver_uuid',
                'message',
                'platform',
                'metadata',
                'tags',
        ):
            assert stq_put_call['kwargs'][key] == expected_stq_data.get(key)


@pytest.mark.config(USE_ORDER_ARCHIVE_FOR_GETTING_ORDER_ID=True)
@pytest.mark.parametrize(
    'request_data,expected_get_history_kwargs',
    [
        (
            {},
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
        ),
        (
            {'include_metadata': True},
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
        ),
        (
            {'include_participants': True},
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
        ),
        (
            {
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'limit': 10,
                    },
                },
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': None,
                'message_ids_limit': 10,
            },
        ),
        (
            {'range': {'message_ids': {'older_than': 'some_message_id'}}},
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': 'some_message_id',
                'message_ids_limit': None,
            },
        ),
        (
            {
                'include_metadata': True,
                'include_participants': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'older_than': 'another_message_id',
                        'limit': 10,
                    },
                },
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': 'another_message_id',
                'message_ids_limit': 10,
            },
        ),
    ],
)
async def test_history(
        mock_get_history,
        taxi_driver_support_client,
        mock_driver_session,
        mock_get_chat,
        mock_driver_profiles,
        mock_personal,
        request_data,
        expected_get_history_kwargs,
):
    mocked_get_history = mock_get_history(UNIQUE_DRIVER_ID, 'driver')
    request_data['db'] = '59de5222293145d09d31cd1604f8f656'
    headers = {'Authorization': 'some_driver_session', 'Accept-Language': 'ru'}
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/5bcdb13084b5976d23aa01bb/history',
        json=request_data,
        headers=headers,
    )
    assert response.status == 200

    get_history_call = mocked_get_history.calls[0]

    for key, value in expected_get_history_kwargs.items():
        assert get_history_call['kwargs'][key] == value

    assert 'headers' in get_history_call['kwargs']
    assert 'Accept-Language' in get_history_call['kwargs']['headers']
    assert get_history_call['kwargs']['headers']['Accept-Language'] == 'ru'

    response_data = await response.json()
    assert 'messages' in response_data
    assert response_data['messages'] == [
        {'text': 'test_text', 'sender': {'role': 'support', 'id': 'support'}},
        {
            'text': 'tt',
            'sender': {'role': 'driver', 'id': UNIQUE_DRIVER_ID},
            'metadata': {
                'created': THREE_MONTHS_AGO,
                'attachments': [
                    {
                        'id': 'test_id',
                        'link': (
                            '/support_chat/5bcdb13084b5976d23aa01bb/'
                            'attachment/'
                            'test_id?db=%s' % request_data['db']
                        ),
                        'link_preview': (
                            '/support_chat/'
                            '5bcdb13084b5976d23aa01bb/'
                            'attachment/'
                            'test_id?db=%s'
                            '&size=preview' % request_data['db']
                        ),
                    },
                ],
            },
        },
    ]
    assert 'total' in response_data
    assert response_data['status'] == {'is_open': True, 'is_visible': True}


@pytest.mark.translations(
    client_messages={
        'user_chat_csat.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'user_chat_csat.bad': {'ru': 'Плохо', 'en': 'Bad'},
        'user_chat_csat.normal': {'ru': 'Нормально', 'en': 'Normal'},
        'user_chat_csat.good': {'ru': 'Хорошо', 'en': 'Good'},
        'user_chat_csat.amazing': {'ru': 'Отлично', 'en': 'Amazing'},
        'user_chat_csat_reasons.template_answer': {
            'ru': 'Ответ шаблоном',
            'en': 'Template answer',
        },
        'user_chat_csat_reasons.problem_not_solved': {
            'ru': 'Проблема не решена',
            'en': 'Problem not solved',
        },
        'user_chat_csat_reasons.disagree_solution': {
            'ru': 'Не согласен с решением',
            'en': 'Disagree solution',
        },
        'user_chat_csat_reasons.long_answer': {
            'ru': 'Долгий ответ',
            'en': 'Long answer',
        },
        'user_chat_csat_reasons.long_initial_answer': {
            'ru': 'Долгий первичный ответ',
            'en': 'Long initial response',
        },
        'user_chat_csat_reasons.long_interval_answer': {
            'ru': 'Задержка между сообщениями',
            'en': 'Long interval between messages',
        },
        'user_chat_csat.quality_score': {
            'ru': 'Оцените качество службы поддержки сервиса',
            'en': 'Score the quality of the service support',
        },
        'user_chat_csat.response_speed_score': {
            'ru': 'Оцените скорость ответа специалиста поддержки',
            'en': 'Score the response speed of the support specialist',
        },
    },
)
@pytest.mark.config(DRIVER_CHAT_USE_EXPERIMENTS_CSAT=True)
@pytest.mark.parametrize(
    'request_data,headers,additional_meta,expected_search_kwargs,'
    'expected_get_history_kwargs,expected_csat',
    [
        (
            {},
            {},
            {},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'open',
                'platform': 'taximeter',
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': False,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
            [
                {
                    'option_key': 'horrible',
                    'option_name': 'Horrible',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'template_answer',
                            'reason_name': 'Template answer',
                        },
                        {
                            'reason_key': 'problem_not_solved',
                            'reason_name': 'Problem not solved',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
                {
                    'option_key': 'bad',
                    'option_name': 'Bad',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'template_answer',
                            'reason_name': 'Template answer',
                        },
                        {
                            'reason_key': 'problem_not_solved',
                            'reason_name': 'Problem not solved',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
                {
                    'option_key': 'normal',
                    'option_name': 'Normal',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'template_answer',
                            'reason_name': 'Template answer',
                        },
                        {
                            'reason_key': 'problem_not_solved',
                            'reason_name': 'Problem not solved',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
                {
                    'option_key': 'good',
                    'option_name': 'Good',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'template_answer',
                            'reason_name': 'Template answer',
                        },
                        {
                            'reason_key': 'problem_not_solved',
                            'reason_name': 'Problem not solved',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
                {
                    'option_key': 'amazing',
                    'option_name': 'Amazing',
                    'reasons': [],
                },
            ],
        ),
        (
            {
                'include_metadata': True,
                'include_participants': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'older_than': 'another_message_id',
                        'limit': 10,
                    },
                },
            },
            {'user-agent': 'taximeter-uber'},
            {},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'open',
                'platform': 'uberdriver',
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': 'another_message_id',
                'message_ids_limit': 10,
            },
            [
                {
                    'option_key': 'horrible',
                    'option_name': 'Horrible',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'template_answer',
                            'reason_name': 'Template answer',
                        },
                        {
                            'reason_key': 'problem_not_solved',
                            'reason_name': 'Problem not solved',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
                {
                    'option_key': 'bad',
                    'option_name': 'Bad',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'template_answer',
                            'reason_name': 'Template answer',
                        },
                        {
                            'reason_key': 'problem_not_solved',
                            'reason_name': 'Problem not solved',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
                {
                    'option_key': 'normal',
                    'option_name': 'Normal',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'template_answer',
                            'reason_name': 'Template answer',
                        },
                        {
                            'reason_key': 'problem_not_solved',
                            'reason_name': 'Problem not solved',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
                {
                    'option_key': 'good',
                    'option_name': 'Good',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'template_answer',
                            'reason_name': 'Template answer',
                        },
                        {
                            'reason_key': 'problem_not_solved',
                            'reason_name': 'Problem not solved',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
                {
                    'option_key': 'amazing',
                    'option_name': 'Amazing',
                    'reasons': [],
                },
            ],
        ),
        (
            {
                'include_metadata': True,
                'include_participants': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'older_than': 'another_message_id',
                        'limit': 10,
                    },
                },
            },
            {'user-agent': 'taximeter-uber'},
            {'platform': 'dummy-platform'},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'open',
                'platform': 'uberdriver',
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': 'another_message_id',
                'message_ids_limit': 10,
            },
            {
                'questions': [
                    {
                        'id': 'quality_score',
                        'text': 'Score the quality of the service support',
                        'with_input': False,
                        'values': [
                            {
                                'id': 'horrible',
                                'text': 'Horrible',
                                'reasons': [
                                    {
                                        'id': 'disagree_solution',
                                        'text': 'Disagree solution',
                                        'with_input': False,
                                    },
                                    {
                                        'id': 'problem_not_solved',
                                        'text': 'Problem not solved',
                                        'with_input': False,
                                    },
                                    {
                                        'id': 'long_answer',
                                        'text': 'Long answer',
                                        'reasons': [
                                            {
                                                'id': 'long_initial_answer',
                                                'text': (
                                                    'Long initial response'
                                                ),
                                                'with_input': False,
                                            },
                                            {
                                                'id': 'long_interval_answer',
                                                'text': (
                                                    'Long interval between '
                                                    'messages'
                                                ),
                                                'with_input': False,
                                            },
                                        ],
                                        'with_input': False,
                                    },
                                    {
                                        'id': 'template_answer',
                                        'text': 'Template answer',
                                        'with_input': False,
                                    },
                                ],
                                'with_input': False,
                            },
                            {
                                'id': 'good',
                                'text': 'Good',
                                'with_input': False,
                            },
                            {
                                'id': 'amazing',
                                'text': 'Amazing',
                                'with_input': False,
                            },
                        ],
                    },
                    {
                        'id': 'response_speed_score',
                        'text': (
                            'Score the response speed of the '
                            'support specialist'
                        ),
                        'with_input': False,
                        'values': [
                            {
                                'id': 'horrible',
                                'text': 'Horrible',
                                'with_input': False,
                            },
                            {
                                'id': 'good',
                                'text': 'Good',
                                'with_input': False,
                            },
                            {
                                'id': 'amazing',
                                'text': 'Amazing',
                                'with_input': False,
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'include_metadata': True,
                'include_participants': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'older_than': 'another_message_id',
                        'limit': 10,
                    },
                },
            },
            {'user-agent': 'taximeter-uber'},
            {
                'platform': 'dummy-platform',
                'csat_options': {'questions': []},
                'csat_new_version': True,
            },
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'open',
                'platform': 'uberdriver',
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': 'another_message_id',
                'message_ids_limit': 10,
            },
            {'questions': []},
        ),
    ],
)
async def test_history_active(
        taxi_driver_support_client,
        mock_search,
        mock_exp3_get_values,
        taxi_driver_support_app,
        monkeypatch,
        mock,
        patch,
        mock_driver_session,
        mock_get_history,
        mock_driver_profiles,
        mock_personal,
        request_data,
        headers,
        additional_meta,
        expected_search_kwargs,
        expected_get_history_kwargs,
        expected_csat,
):
    mocked_get_history = mock_get_history(
        UNIQUE_DRIVER_ID, 'driver', additional_meta,
    )
    request_data['db'] = '59de5222293145d09d31cd1604f8f656'
    headers.update(
        {'Authorization': 'some_driver_session', 'Accept-Language': 'en'},
    )
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/history/active', json=request_data, headers=headers,
    )
    assert response.status == 200

    search_call = mock_search.calls[0]
    for key, value in expected_search_kwargs.items():
        assert search_call['kwargs'][key] == value

    assert 'headers' in search_call['kwargs']
    assert 'Accept-Language' in search_call['kwargs']['headers']
    assert search_call['kwargs']['headers']['Accept-Language'] == 'en'

    get_history_call = mocked_get_history.calls[0]
    for key, value in expected_get_history_kwargs.items():
        assert get_history_call['kwargs'][key] == value

    assert 'headers' in get_history_call['kwargs']
    assert 'Accept-Language' in get_history_call['kwargs']['headers']
    assert get_history_call['kwargs']['headers']['Accept-Language'] == 'en'

    response_data = await response.json()
    assert 'messages' in response_data
    assert response_data['messages'] == [
        {'text': 'test_text', 'sender': {'role': 'support', 'id': 'support'}},
        {
            'text': 'tt',
            'sender': {'role': 'driver', 'id': UNIQUE_DRIVER_ID},
            'metadata': {
                'created': THREE_MONTHS_AGO,
                'attachments': [
                    {
                        'id': 'test_id',
                        'link': (
                            '/support_chat/5bcdb13084b5976d23aa01bb/'
                            'attachment/'
                            'test_id?db=%s' % request_data['db']
                        ),
                        'link_preview': (
                            '/support_chat/'
                            '5bcdb13084b5976d23aa01bb/'
                            'attachment/'
                            'test_id?db=%s'
                            '&size=preview' % request_data['db']
                        ),
                    },
                ],
            },
        },
    ]
    assert 'total' in response_data
    assert response_data['status']['ask_csat']
    if response_data.get('metadata', {}).get('csat_new_version'):
        assert response_data['metadata']['csat_options'] == expected_csat
    else:
        assert response_data['csat_options'] == expected_csat


@pytest.mark.config(
    DRIVER_CHAT_CSAT_OPTIONS=[
        {'value': 'horrible', 'reasons': ['long_answer', 'disagree_solution']},
    ],
)
@pytest.mark.translations(
    client_messages={
        'user_chat_csat.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'user_chat_csat_reasons.disagree_solution': {
            'ru': 'Не согласен с решением',
            'en': 'Disagree solution',
        },
        'user_chat_csat_reasons.long_answer': {
            'ru': 'Долгий ответ',
            'en': 'Long answer',
        },
    },
)
@pytest.mark.parametrize(
    'user_lang, expected_csat_options',
    [
        (
            'en',
            [
                {
                    'option_key': 'horrible',
                    'option_name': 'Horrible',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
            ],
        ),
        (
            'ru',
            [
                {
                    'option_key': 'horrible',
                    'option_name': 'Ужасно',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Долгий ответ',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Не согласен с решением',
                        },
                    ],
                },
            ],
        ),
        (
            'fr',
            [
                {
                    'option_key': 'horrible',
                    'option_name': 'Ужасно',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Долгий ответ',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Не согласен с решением',
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_history_csat_translation(
        taxi_driver_support_client,
        taxi_driver_support_app,
        mock_search,
        mock_driver_session,
        mock_get_history,
        mock_driver_profiles,
        mock_personal,
        mock_exp3_get_values,
        user_lang,
        expected_csat_options,
):
    mock_get_history(UNIQUE_DRIVER_ID, 'driver')
    headers = {
        'Authorization': 'some_driver_session',
        'Accept-Language': user_lang,
    }
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/history/active',
        json={
            'db': '59de5222293145d09d31cd1604f8f656',
            'include_metadata': False,
            'include_participants': False,
        },
        headers=headers,
    )
    assert response.status == 200
    response_data = await response.json()
    assert 'messages' in response_data
    assert response_data['csat_options'] == expected_csat_options


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'request_data,headers,expected_search_kwargs',
    [
        (
            {},
            {'user-agent': 'taximeter-vezet'},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'archive',
                'date_newer_than': THREE_MONTHS_AGO,
                'date_older_than': None,
                'date_limit': 25,
                'platform': 'vezet',
            },
        ),
        (
            {
                'date': {
                    'newer_than': 'some_date',
                    'older_than': 'another_date',
                    'limit': 10,
                },
            },
            {'user-agent': 'yandex-taximeter'},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'archive',
                'date_newer_than': 'some_date',
                'date_older_than': 'another_date',
                'date_limit': 10,
                'platform': 'taximeter',
            },
        ),
    ],
)
async def test_list_archived(
        taxi_driver_support_client,
        mock_driver_session,
        mock_search,
        mock_driver_profiles,
        mock_personal,
        request_data,
        headers,
        expected_search_kwargs,
):
    request_data['db'] = '59de5222293145d09d31cd1604f8f656'
    headers.update(
        {'Authorization': 'some_driver_session', 'Accept-Language': 'en'},
    )
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/list_archived', json=request_data, headers=headers,
    )
    assert response.status == 200

    search_call = mock_search.calls[0]
    for key, value in expected_search_kwargs.items():
        assert search_call['kwargs'][key] == value

    assert 'headers' in search_call['kwargs']
    assert 'Accept-Language' in search_call['kwargs']['headers']
    assert search_call['kwargs']['headers']['Accept-Language'] == 'en'


@pytest.mark.parametrize(
    (
        'request_data',
        'headers',
        'expected_read_kwargs',
        'expected_support_chat',
    ),
    [
        (
            {},
            {},
            {
                'chat_id': '5bcdb13084b5976d23aa01bb',
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'platform': 'taximeter',
            },
            {
                'id': '5bcdb13084b5976d23aa01bb',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                    'platform': 'taximeter',
                },
            },
        ),
        (
            {},
            {'User-agent': 'taximeter-vezet'},
            {
                'chat_id': '5bcdb13084b5976d23aa01bb',
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'platform': 'vezet',
            },
            {
                'id': '5bcdb13084b5976d23aa01bb',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                    'platform': 'vezet',
                },
            },
        ),
    ],
)
@pytest.mark.translations(**conftest.TRANSLATIONS)
async def test_read(
        mock_read,
        mock_driver_profiles,
        mock_personal,
        patch,
        patch_aiohttp_session,
        response_mock,
        taxi_driver_support_client,
        mock_driver_session,
        request_data,
        headers,
        expected_read_kwargs,
        expected_support_chat,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'GET')
    def patch_support_chat_request(method, url, **kwargs):
        assert method == 'get'
        return response_mock(json=expected_support_chat)

    @patch('taxi_driver_support.internal.notification.send_driver_push')
    async def send_driver_push(app, chat_id, task_id, **kwargs):
        chat_response = await app.support_chat_client.get_chat(chat_id)
        meta_data = chat_response.get('metadata', {})
        assert kwargs.get('zero_messages') and meta_data['new_messages'] == 0

    request_data['db'] = '59de5222293145d09d31cd1604f8f656'
    headers['Authorization'] = 'some_driver_session'
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/5bcdb13084b5976d23aa01bb/read/',
        json=request_data,
        headers=headers,
    )
    assert response.status == 200

    read = mock_read.calls[0]
    read['kwargs'].pop('log_extra')
    assert read['kwargs'] == expected_read_kwargs


@pytest.mark.config(
    DRIVER_SUPPORT_ALLOWED_FILE_TYPES=[
        'image/png',
        'image/jpg',
        'application/octet-stream',
        'text/plain',
    ],
)
@pytest.mark.parametrize(
    'chat_id,file,filename,content_type,idempotency_token,expected_result',
    [
        (
            '5bcdb13084b5976d23aa01bb',
            b'test',
            'test_filename',
            'text/plain',
            'test_token',
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
        ),
        (
            '5bcdb13084b5976d23aa01bb',
            b'\x90\x01',
            'test_filename',
            'application/octet-stream',
            'test_token',
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
        ),
    ],
)
async def test_attach_file(
        mock_driver_profiles,
        mock_personal,
        taxi_driver_support_client,
        response_mock,
        patch_aiohttp_session,
        mock_driver_session,
        chat_id,
        file,
        filename,
        content_type,
        idempotency_token,
        expected_result,
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
            'sender_role': 'driver',
            'sender_id': '5bc702f995572fa0df26e0e2',
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
    headers = {'Authorization': 'some_driver_session'}
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/attach_file/',
        data=file,
        params=params,
        headers=headers,
    )
    assert response.status == 200
    assert await response.json() == expected_result


@pytest.mark.parametrize('file', [b'test', b'\x90\x01'])
async def test_attach_file_bad_mime_type(
        taxi_driver_support_client,
        mock_driver_session,
        file,
        mock_driver_profiles,
        mock_personal,
):
    params = {
        'filename': 'filename',
        'idempotency_token': 'test_token',
        'db': '59de5222293145d09d31cd1604f8f656',
    }
    headers = {'Authorization': 'some_driver_session'}
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/attach_file/',
        data=file,
        params=params,
        headers=headers,
    )
    assert response.status == 400


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'driver-support', 'dst': 'support_chat'},
        {'src': 'driver-support', 'dst': 'personal'},
    ],
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    'chat_id, attachment_id, preview, expected_redirect',
    [
        (
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            False,
            '/v1/chat/5c504337779fb336b89182a2/attachment/'
            'b444ac06613fc8d63795be9ad0beaf55011936ac'
            '?sender_id=5bc702f995572fa0df26e0e2&sender_role=driver',
        ),
        (
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            True,
            '/v1/chat/5c504337779fb336b89182a2/attachment/'
            'b444ac06613fc8d63795be9ad0beaf55011936ac'
            '?sender_id=5bc702f995572fa0df26e0e2&sender_role=driver'
            '&size=preview',
        ),
        (
            '5c504337779fb336b89182a3',
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f',
            False,
            '/v1/chat/5c504337779fb336b89182a3/attachment/'
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f'
            '?sender_id=5bc702f995572fa0df26e0e2&sender_role=driver',
        ),
        (
            '5c504337779fb336b89182a3',
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f',
            True,
            '/v1/chat/5c504337779fb336b89182a3/attachment/'
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f'
            '?sender_id=5bc702f995572fa0df26e0e2&sender_role=driver'
            '&size=preview',
        ),
    ],
)
async def test_download_file(
        taxi_driver_support_client,
        mock_driver_session,
        mock_driver_profiles,
        mock_personal,
        patch,
        chat_id,
        attachment_id,
        preview,
        expected_redirect,
):
    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return 'Ticket 123'

    params = {'db': '59de5222293145d09d31cd1604f8f656'}
    if preview:
        params['size'] = 'preview'
    headers = {'Authorization': 'some_driver_session'}
    response = await taxi_driver_support_client.get(
        '/v1/support_chat/%s/attachment/%s' % (chat_id, attachment_id),
        params=params,
        headers=headers,
    )
    assert response.status == 200
    assert response.headers['X-Accel-Redirect'] == expected_redirect
    assert response.headers['X-Ya-Service-Ticket'] == 'Ticket 123'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'headers, expected_platform, support_info_response, result',
    [
        (
            {'user-agent': 'taximeter-uber'},
            'uberdriver',
            {
                'archive': False,
                'open': False,
                'visible': True,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 0,
            },
            {'archive': False, 'open': False, 'new_messages_count': 0},
        ),
        (
            {'user-agent': 'taximeter'},
            'taximeter',
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 2,
                'visible_chat_new_messages_count': 3,
            },
            {'archive': False, 'open': True, 'new_messages_count': 2},
        ),
    ],
)
async def test_summary(
        taxi_driver_support_client,
        patch_aiohttp_session,
        mock_driver_session,
        mock_driver_profiles,
        mock_personal,
        response_mock,
        headers,
        expected_platform,
        support_info_response,
        result,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def _dummy_request(method, url, **kwargs):
        assert method == 'post'
        assert url == 'http://support-chat.taxi.dev.yandex.net/v1/chat/summary'
        assert kwargs['json'] == {
            'owner': {
                'id': '5bc702f995572fa0df26e0e2',
                'role': 'driver',
                'platform': expected_platform,
            },
        }
        return response_mock(json=support_info_response)

    headers.update(
        {'Authorization': 'some_driver_session', 'Accept-Language': 'en'},
    )
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/summary',
        json={'db': '59de5222293145d09d31cd1604f8f656'},
        headers=headers,
    )
    assert response.status == 200
    assert await response.json() == result


# This test for new endpoints behind dap
@pytest.mark.config(
    DRIVER_SUPPORT_ADD_MESSAGE_PARAMS_TO_META={
        'some_query_param': 'some_meta_field',
        'other_query_param': 'other_meta_field',
    },
    USE_ORDER_ARCHIVE_FOR_GETTING_ORDER_ID=True,
)
@pytest.mark.parametrize(
    'params,park_id,driver_profile_id,selfreg_token,headers,message,'
    'metadata,expected_status,expected_create_data,expected_stq_data,'
    'is_exported',
    [
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {},
            {'text': 'test message'},
            None,
            200,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'user_application': 'taximeter',
                'user_country': 'rus',
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {'text': 'test message'},
                'platform': 'taximeter',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'tags': [],
            },
            False,
        ),
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'user-agent': 'taximeter-uber'},
            {
                'text': 'test message',
                'metadata': {
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1'},
                        {'id': 'attachment_id_2'},
                    ],
                    'source': 'history',
                },
            },
            None,
            200,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'appeal_source': 'history',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                    'order_id': 'some_order_id',
                },
                'message_metadata': {
                    'appeal_source': 'history',
                    'order_id': 'some_order_id',
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1', 'source': 'mds'},
                        {'id': 'attachment_id_2', 'source': 'mds'},
                    ],
                },
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'uberdriver',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'user_application': 'taximeter',
                'user_country': 'rus',
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {
                    'text': 'test message',
                    'metadata': {
                        'order_id': 'some_order_id',
                        'order_alias_id': 'some_alias_id',
                        'ticket_subject': 'ticket subject',
                        'attachments': [
                            {'id': 'attachment_id_1', 'source': 'mds'},
                            {'id': 'attachment_id_2', 'source': 'mds'},
                        ],
                        'appeal_source': 'history',
                    },
                },
                'platform': 'uberdriver',
                'metadata': {
                    'appeal_source': 'history',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'order_id': 'some_order_id',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'tags': [],
            },
            False,
        ),
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'user-agent': 'taximeter-uber'},
            {
                'text': 'test message',
                'metadata': {
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1'},
                        {'id': 'attachment_id_2'},
                    ],
                    'driver_on_order': True,
                },
            },
            None,
            200,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'order_id': 'some_order_id',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': {
                    'order_id': 'some_order_id',
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1', 'source': 'mds'},
                        {'id': 'attachment_id_2', 'source': 'mds'},
                    ],
                    'driver_on_order': True,
                },
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'uberdriver',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'user_application': 'taximeter',
                'user_country': 'rus',
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {
                    'text': 'test message',
                    'metadata': {
                        'order_id': 'some_order_id',
                        'order_alias_id': 'some_alias_id',
                        'ticket_subject': 'ticket subject',
                        'attachments': [
                            {'id': 'attachment_id_1', 'source': 'mds'},
                            {'id': 'attachment_id_2', 'source': 'mds'},
                        ],
                        'driver_on_order': True,
                    },
                },
                'platform': 'uberdriver',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'order_id': 'some_order_id',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'tags': ['driver_on_order'],
            },
            False,
        ),
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'user-agent': 'taximeter-uber'},
            {
                'text': 'test message',
                'metadata': {
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1'},
                        {'id': 'attachment_id_2'},
                    ],
                    'driver_on_order': False,
                },
            },
            None,
            200,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'order_id': 'some_order_id',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': {
                    'order_id': 'some_order_id',
                    'order_alias_id': 'some_alias_id',
                    'ticket_subject': 'ticket subject',
                    'attachments': [
                        {'id': 'attachment_id_1', 'source': 'mds'},
                        {'id': 'attachment_id_2', 'source': 'mds'},
                    ],
                    'driver_on_order': False,
                },
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'uberdriver',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'user_application': 'taximeter',
                'user_country': 'rus',
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {
                    'text': 'test message',
                    'metadata': {
                        'order_id': 'some_order_id',
                        'order_alias_id': 'some_alias_id',
                        'ticket_subject': 'ticket subject',
                        'attachments': [
                            {'id': 'attachment_id_1', 'source': 'mds'},
                            {'id': 'attachment_id_2', 'source': 'mds'},
                        ],
                        'driver_on_order': False,
                    },
                },
                'platform': 'uberdriver',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'order_id': 'some_order_id',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'tags': [],
            },
            False,
        ),
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {},
            {'text': 'test message'},
            {'csat_reasons': ['metadata']},
            200,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'csat_reasons': ['metadata'],
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
            {
                'args': ('dummy_chat_id', '5bc702f995572fa0df26e0e2'),
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {'text': 'test message'},
                'platform': 'taximeter',
                'metadata': {
                    'csat_reasons': ['metadata'],
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'tags': [],
            },
            False,
        ),
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'user-agent': 'taximeter-vezet'},
            None,
            {'csat_reasons': ['fast answer'], 'csat_value': 'amazing'},
            200,
            None,
            {
                'args': (
                    '5bcdb13084b5976d23aa01bb',
                    '5bc702f995572fa0df26e0e2',
                ),
                'db_id': '59de5222293145d09d31cd1604f8f656',
                'driver_uuid': 'some_driver_uuid',
                'message': {},
                'platform': 'vezet',
                'metadata': {
                    'csat_reasons': ['fast answer'],
                    'csat_value': 'amazing',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'tags': [],
            },
            False,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'some_selfreg_token',
            {},
            None,
            {'csat_reasons': ['fast answer'], 'csat_value': 'amazing'},
            200,
            None,
            {
                'args': ('5bcdb13084b5976d23aa01bb', None),
                'platform': 'taximeter',
                'message': {},
                'metadata': {
                    'csat_reasons': ['fast answer'],
                    'csat_value': 'amazing',
                    'user_locale': 'en',
                },
                'tags': [],
                'hidden_comment': '[\'some\', \'tags\']',
            },
            False,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'bad_selfreg_token',
            {},
            {'text': 'test message'},
            None,
            401,
            None,
            None,
            False,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'some_selfreg_token',
            {},
            {'text': 'test message'},
            None,
            200,
            {
                'owner_id': 'some_selfreg_id',
                'owner_role': 'selfreg_driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_locale': 'en',
                    'selfreg_id': 'some_selfreg_id',
                    'city': 'Moscow',
                    'mock_tags': ['some', 'tags'],
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': 'some_selfreg_id',
                'message_sender_role': 'selfreg_driver',
                'platform': 'taximeter',
            },
            {
                'args': ('dummy_chat_id', None),
                'user_application': 'taximeter',
                'message': {'text': 'test message'},
                'platform': 'taximeter',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_locale': 'en',
                    'selfreg_id': 'some_selfreg_id',
                    'city': 'Moscow',
                    'mock_tags': ['some', 'tags'],
                },
                'tags': [],
                'hidden_comment': '[\'some\', \'tags\']',
            },
            False,
        ),
        (
            {
                'chat_type': 'selfreg_driver_support',
                'some_query_param': 'some_value',
                'other_query_param': 'other_value',
                'redundant_query_param': 'redundant_value',
            },
            None,
            None,
            'some_selfreg_token',
            {},
            {'text': 'test message'},
            {'csat_reasons': ['metadata']},
            200,
            {
                'owner_id': 'some_selfreg_id',
                'owner_role': 'selfreg_driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'csat_reasons': ['metadata'],
                    'user_locale': 'en',
                    'selfreg_id': 'some_selfreg_id',
                    'city': 'Moscow',
                    'mock_tags': ['some', 'tags'],
                    'some_meta_field': 'some_value',
                    'other_meta_field': 'other_value',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': 'some_selfreg_id',
                'message_sender_role': 'selfreg_driver',
                'platform': 'taximeter',
            },
            {
                'args': ('dummy_chat_id', None),
                'message': {'text': 'test message'},
                'platform': 'taximeter',
                'metadata': {
                    'csat_reasons': ['metadata'],
                    'user_application': 'taximeter',
                    'user_locale': 'en',
                    'selfreg_id': 'some_selfreg_id',
                    'city': 'Moscow',
                    'mock_tags': ['some', 'tags'],
                    'some_meta_field': 'some_value',
                    'other_meta_field': 'other_value',
                },
                'tags': [],
                'hidden_comment': '[\'some\', \'tags\']',
            },
            False,
        ),
    ],
)
async def test_add_message_new(
        monkeypatch,
        mock,
        mock_stq_put,
        mock_add_update,
        mock_search,
        mock_get_order_by_id,
        mock_selfreg_validate,
        mock_driver_profiles,
        mock_personal,
        taxi_driver_support_client,
        taxi_driver_support_app,
        params,
        park_id,
        driver_profile_id,
        selfreg_token,
        headers,
        message,
        metadata,
        expected_status,
        expected_create_data,
        expected_stq_data,
        is_exported,
        patch_additional_meta,
):
    # pylint: disable=too-many-locals
    additional_meta_calls = patch_additional_meta(
        metadata={'park_country': 'rus'},
    )

    @mock
    async def _dummy_create_chat(*args, **kwargs):
        data = {'id': 'dummy_chat_id', 'newest_message_id': 'new_message_id'}
        if is_exported:
            data['metadata'] = {'ticket_id': '1', 'author_id': '1'}
        return data

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'create_chat',
        _dummy_create_chat,
    )

    request_data = {'request_id': 'dummy_request_id'}
    headers['Accept-Language'] = 'en'
    headers.update(DAP_APP_HEADERS)
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    if message:
        request_data['message'] = message
    if metadata is not None:
        request_data['metadata'] = metadata

    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/support_chat/add_message',
        headers=headers,
        cookies=cookies,
        params=params,
        json=request_data,
    )
    assert response.status == expected_status
    if selfreg_token:
        assert mock_selfreg_validate.next_call()['request'].query == {
            'token': selfreg_token,
        }
    if expected_status != 200:
        return

    assert additional_meta_calls

    create_chat_calls = _dummy_create_chat.calls
    if create_chat_calls:
        support_chat_call = create_chat_calls[0]
        for key, value in expected_create_data.items():
            assert support_chat_call['kwargs'][key] == value
    else:
        support_chat_call = mock_search.calls[0]
        assert support_chat_call
        assert support_chat_call['kwargs']['platform']
        assert mock_add_update.calls[0]

    stq_kwargs = ['message', 'platform', 'metadata', 'tags']
    if park_id:
        stq_kwargs.append('db_id')
    if driver_profile_id:
        stq_kwargs.append('driver_uuid')
    if selfreg_token:
        stq_kwargs.append('hidden_comment')
    stq_put_call = mock_stq_put.calls[0]
    if is_exported:
        assert stq_put_call['args'] == expected_stq_data
    else:
        assert stq_put_call['args'] == expected_stq_data['args']
        for key in stq_kwargs:
            assert stq_put_call['kwargs'][key] == expected_stq_data.get(key)


@pytest.mark.parametrize(
    'params,owner_id,owner_role,park_id,driver_profile_id,selfreg_token,'
    'request_data,expected_status,expected_get_history_kwargs,expected_link',
    [
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {},
            200,
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?db=59de5222293145d09d31cd1604f8f656'
            ),
        ),
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'include_metadata': True},
            200,
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?db=59de5222293145d09d31cd1604f8f656'
            ),
        ),
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'include_participants': True},
            200,
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?db=59de5222293145d09d31cd1604f8f656'
            ),
        ),
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'limit': 10,
                    },
                },
            },
            200,
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': None,
                'message_ids_limit': 10,
            },
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?db=59de5222293145d09d31cd1604f8f656'
            ),
        ),
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'range': {'message_ids': {'older_than': 'some_message_id'}}},
            200,
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': 'some_message_id',
                'message_ids_limit': None,
            },
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?db=59de5222293145d09d31cd1604f8f656'
            ),
        ),
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {
                'include_metadata': True,
                'include_participants': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'older_than': 'another_message_id',
                        'limit': 10,
                    },
                },
            },
            200,
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': 'another_message_id',
                'message_ids_limit': 10,
            },
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?db=59de5222293145d09d31cd1604f8f656'
            ),
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'bad_selfreg_token',
            {},
            401,
            None,
            None,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'some_selfreg_token',
            {},
            200,
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': False,
                'include_participants': True,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?chat_type=selfreg_driver_support'
            ),
        ),
    ],
)
async def test_history_new(
        mock_get_history,
        taxi_driver_support_client,
        mock_get_chat,
        mock_selfreg_validate,
        mock_driver_profiles,
        mock_personal,
        params,
        owner_id,
        owner_role,
        park_id,
        driver_profile_id,
        selfreg_token,
        request_data,
        expected_status,
        expected_get_history_kwargs,
        expected_link,
):
    mocked_get_history = mock_get_history(owner_id, owner_role)
    headers = {'Accept-Language': 'ru', **DAP_APP_HEADERS}
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.post(
        (
            '/driver/v1/driver-support/'
            'v1/support_chat/5bcdb13084b5976d23aa01bb/history'
        ),
        headers=headers,
        cookies=cookies,
        params=params,
        json=request_data,
    )
    assert response.status == expected_status
    if selfreg_token:
        assert mock_selfreg_validate.next_call()['request'].query == {
            'token': selfreg_token,
        }
    if expected_status != 200:
        return

    get_history_call = mocked_get_history.calls[0]

    for key, value in expected_get_history_kwargs.items():
        assert get_history_call['kwargs'][key] == value

    assert 'headers' in get_history_call['kwargs']
    assert 'Accept-Language' in get_history_call['kwargs']['headers']
    assert get_history_call['kwargs']['headers']['Accept-Language'] == 'ru'

    response_data = await response.json()
    assert 'messages' in response_data
    assert response_data['messages'] == [
        {'text': 'test_text', 'sender': {'role': 'support', 'id': 'support'}},
        {
            'text': 'tt',
            'sender': {'role': owner_role, 'id': owner_id},
            'metadata': {
                'created': THREE_MONTHS_AGO,
                'attachments': [
                    {
                        'id': 'test_id',
                        'link': expected_link,
                        'link_preview': expected_link + '&size=preview',
                    },
                ],
            },
        },
    ]
    assert 'total' in response_data
    assert response_data['status'] == {'is_open': True, 'is_visible': True}


@pytest.mark.translations(
    client_messages={
        'user_chat_csat.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'user_chat_csat.bad': {'ru': 'Плохо', 'en': 'Bad'},
        'user_chat_csat.normal': {'ru': 'Нормально', 'en': 'Normal'},
        'user_chat_csat.good': {'ru': 'Хорошо', 'en': 'Good'},
        'user_chat_csat.amazing': {'ru': 'Отлично', 'en': 'Amazing'},
        'user_chat_csat_reasons.template_answer': {
            'ru': 'Ответ шаблоном',
            'en': 'Template answer',
        },
        'user_chat_csat_reasons.problem_not_solved': {
            'ru': 'Проблема не решена',
            'en': 'Problem not solved',
        },
        'user_chat_csat_reasons.disagree_solution': {
            'ru': 'Не согласен с решением',
            'en': 'Disagree solution',
        },
        'user_chat_csat_reasons.long_answer': {
            'ru': 'Долгий ответ',
            'en': 'Long answer',
        },
    },
)
@pytest.mark.parametrize(
    'owner_id,owner_role,park_id,driver_profile_id,selfreg_token,params,'
    'request_data,headers,expected_search_kwargs,expected_get_history_kwargs,'
    'expected_status,expected_link',
    [
        (
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            None,
            {},
            {},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'open',
                'platform': 'taximeter',
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': False,
                'message_ids_newer_than': None,
                'message_ids_older_than': None,
                'message_ids_limit': None,
            },
            200,
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?db=59de5222293145d09d31cd1604f8f656'
            ),
        ),
        (
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            None,
            {
                'include_metadata': True,
                'include_participants': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'older_than': 'another_message_id',
                        'limit': 10,
                    },
                },
            },
            {'user-agent': 'taximeter-uber'},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'open',
                'platform': 'uberdriver',
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': 'another_message_id',
                'message_ids_limit': 10,
            },
            200,
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?db=59de5222293145d09d31cd1604f8f656'
            ),
        ),
        (
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'bad_selfreg_token',
            {'chat_type': 'selfreg_driver_support'},
            {
                'include_metadata': True,
                'include_participants': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'older_than': 'another_message_id',
                        'limit': 10,
                    },
                },
            },
            {'user-agent': 'taximeter-uber'},
            None,
            None,
            401,
            None,
        ),
        (
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'some_selfreg_token',
            {'chat_type': 'selfreg_driver_support'},
            {
                'include_metadata': True,
                'include_participants': True,
                'range': {
                    'message_ids': {
                        'newer_than': 'some_message_id',
                        'older_than': 'another_message_id',
                        'limit': 10,
                    },
                },
            },
            {},
            {
                'owner_id': 'some_selfreg_id',
                'owner_role': 'selfreg_driver',
                'chat_type': 'open',
                'platform': 'taximeter',
            },
            {
                'user_chat_message_id': '5bcdb13084b5976d23aa01bb',
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': 'some_message_id',
                'message_ids_older_than': 'another_message_id',
                'message_ids_limit': 10,
            },
            200,
            (
                '/support_chat/'
                '5bcdb13084b5976d23aa01bb/attachment/'
                'test_id?chat_type=selfreg_driver_support'
            ),
        ),
    ],
)
async def test_history_active_new(
        taxi_driver_support_client,
        mock_search,
        taxi_driver_support_app,
        monkeypatch,
        mock,
        mock_get_history,
        mock_selfreg_validate,
        mock_driver_profiles,
        mock_personal,
        mock_exp3_get_values,
        owner_id,
        owner_role,
        park_id,
        driver_profile_id,
        selfreg_token,
        params,
        request_data,
        headers,
        expected_search_kwargs,
        expected_get_history_kwargs,
        expected_status,
        expected_link,
):
    mocked_get_history = mock_get_history(owner_id, owner_role)
    headers['Accept-Language'] = 'en'
    headers.update(DAP_APP_HEADERS)
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/support_chat/history/active',
        headers=headers,
        cookies=cookies,
        params=params,
        json=request_data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    search_call = mock_search.calls[0]
    for key, value in expected_search_kwargs.items():
        assert search_call['kwargs'][key] == value

    assert 'headers' in search_call['kwargs']
    assert 'Accept-Language' in search_call['kwargs']['headers']
    assert search_call['kwargs']['headers']['Accept-Language'] == 'en'

    get_history_call = mocked_get_history.calls[0]
    for key, value in expected_get_history_kwargs.items():
        assert get_history_call['kwargs'][key] == value

    assert 'headers' in get_history_call['kwargs']
    assert 'Accept-Language' in get_history_call['kwargs']['headers']
    assert get_history_call['kwargs']['headers']['Accept-Language'] == 'en'

    response_data = await response.json()
    assert 'messages' in response_data
    assert response_data['messages'] == [
        {'text': 'test_text', 'sender': {'role': 'support', 'id': 'support'}},
        {
            'text': 'tt',
            'sender': {'role': owner_role, 'id': owner_id},
            'metadata': {
                'created': THREE_MONTHS_AGO,
                'attachments': [
                    {
                        'id': 'test_id',
                        'link': expected_link,
                        'link_preview': expected_link + '&size=preview',
                    },
                ],
            },
        },
    ]
    assert 'total' in response_data
    assert response_data['status']['ask_csat']
    assert response_data['csat_options'] == [
        {
            'option_key': 'horrible',
            'option_name': 'Horrible',
            'reasons': [
                {'reason_key': 'long_answer', 'reason_name': 'Long answer'},
                {
                    'reason_key': 'template_answer',
                    'reason_name': 'Template answer',
                },
                {
                    'reason_key': 'problem_not_solved',
                    'reason_name': 'Problem not solved',
                },
                {
                    'reason_key': 'disagree_solution',
                    'reason_name': 'Disagree solution',
                },
            ],
        },
        {
            'option_key': 'bad',
            'option_name': 'Bad',
            'reasons': [
                {'reason_key': 'long_answer', 'reason_name': 'Long answer'},
                {
                    'reason_key': 'template_answer',
                    'reason_name': 'Template answer',
                },
                {
                    'reason_key': 'problem_not_solved',
                    'reason_name': 'Problem not solved',
                },
                {
                    'reason_key': 'disagree_solution',
                    'reason_name': 'Disagree solution',
                },
            ],
        },
        {
            'option_key': 'normal',
            'option_name': 'Normal',
            'reasons': [
                {'reason_key': 'long_answer', 'reason_name': 'Long answer'},
                {
                    'reason_key': 'template_answer',
                    'reason_name': 'Template answer',
                },
                {
                    'reason_key': 'problem_not_solved',
                    'reason_name': 'Problem not solved',
                },
                {
                    'reason_key': 'disagree_solution',
                    'reason_name': 'Disagree solution',
                },
            ],
        },
        {
            'option_key': 'good',
            'option_name': 'Good',
            'reasons': [
                {'reason_key': 'long_answer', 'reason_name': 'Long answer'},
                {
                    'reason_key': 'template_answer',
                    'reason_name': 'Template answer',
                },
                {
                    'reason_key': 'problem_not_solved',
                    'reason_name': 'Problem not solved',
                },
                {
                    'reason_key': 'disagree_solution',
                    'reason_name': 'Disagree solution',
                },
            ],
        },
        {'option_key': 'amazing', 'option_name': 'Amazing', 'reasons': []},
    ]


@pytest.mark.config(
    DRIVER_CHAT_CSAT_OPTIONS=[
        {'value': 'horrible', 'reasons': ['long_answer', 'disagree_solution']},
    ],
)
@pytest.mark.translations(
    client_messages={
        'user_chat_csat.horrible': {'ru': 'Ужасно', 'en': 'Horrible'},
        'user_chat_csat_reasons.disagree_solution': {
            'ru': 'Не согласен с решением',
            'en': 'Disagree solution',
        },
        'user_chat_csat_reasons.long_answer': {
            'ru': 'Долгий ответ',
            'en': 'Long answer',
        },
    },
)
@pytest.mark.parametrize(
    'params, owner_id, owner_role, park_id, driver_profile_id, selfreg_token, '
    'expected_status',
    [
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'bad_selfreg_token',
            401,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'some_selfreg_token',
            200,
        ),
    ],
)
@pytest.mark.parametrize(
    'user_lang, expected_csat_options',
    [
        (
            'en',
            [
                {
                    'option_key': 'horrible',
                    'option_name': 'Horrible',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Long answer',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Disagree solution',
                        },
                    ],
                },
            ],
        ),
        (
            'ru',
            [
                {
                    'option_key': 'horrible',
                    'option_name': 'Ужасно',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Долгий ответ',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Не согласен с решением',
                        },
                    ],
                },
            ],
        ),
        (
            'fr',
            [
                {
                    'option_key': 'horrible',
                    'option_name': 'Ужасно',
                    'reasons': [
                        {
                            'reason_key': 'long_answer',
                            'reason_name': 'Долгий ответ',
                        },
                        {
                            'reason_key': 'disagree_solution',
                            'reason_name': 'Не согласен с решением',
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_history_csat_translation_new(
        taxi_driver_support_client,
        taxi_driver_support_app,
        mock_search,
        mock_get_history,
        mock_selfreg_validate,
        mock_driver_profiles,
        mock_personal,
        mock_exp3_get_values,
        params,
        owner_id,
        owner_role,
        park_id,
        driver_profile_id,
        selfreg_token,
        user_lang,
        expected_csat_options,
        expected_status,
):
    mock_get_history(owner_id, owner_role)
    headers = {'Accept-Language': user_lang, **DAP_APP_HEADERS}
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/support_chat/history/active',
        headers=headers,
        cookies=cookies,
        params=params,
        json={'include_metadata': False, 'include_participants': False},
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    response_data = await response.json()
    assert 'messages' in response_data
    assert response_data['csat_options'] == expected_csat_options


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'params,park_id,driver_profile_id,selfreg_token,request_data,headers,'
    'expected_search_kwargs,expected_status',
    [
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {},
            {'user-agent': 'taximeter-vezet'},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'archive',
                'date_newer_than': THREE_MONTHS_AGO,
                'date_older_than': None,
                'date_limit': 25,
                'platform': 'vezet',
            },
            200,
        ),
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {
                'date': {
                    'newer_than': 'some_date',
                    'older_than': 'another_date',
                    'limit': 10,
                },
            },
            {'user-agent': 'yandex-taximeter'},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'chat_type': 'archive',
                'date_newer_than': 'some_date',
                'date_older_than': 'another_date',
                'date_limit': 10,
                'platform': 'taximeter',
            },
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'bad_selfreg_token',
            {},
            {'user-agent': 'taximeter-vezet'},
            None,
            401,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'some_selfreg_token',
            {},
            {},
            {
                'owner_id': 'some_selfreg_id',
                'owner_role': 'selfreg_driver',
                'chat_type': 'archive',
                'date_newer_than': THREE_MONTHS_AGO,
                'date_older_than': None,
                'date_limit': 25,
                'platform': 'taximeter',
            },
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'some_selfreg_token',
            {
                'date': {
                    'newer_than': 'some_date',
                    'older_than': 'another_date',
                    'limit': 10,
                },
            },
            {'user-agent': 'yandex-taximeter'},
            {
                'owner_id': 'some_selfreg_id',
                'owner_role': 'selfreg_driver',
                'chat_type': 'archive',
                'date_newer_than': 'some_date',
                'date_older_than': 'another_date',
                'date_limit': 10,
                'platform': 'taximeter',
            },
            200,
        ),
    ],
)
async def test_list_archived_new(
        taxi_driver_support_client,
        mock_search,
        mock_selfreg_validate,
        mock_driver_profiles,
        mock_personal,
        params,
        park_id,
        driver_profile_id,
        selfreg_token,
        request_data,
        headers,
        expected_search_kwargs,
        expected_status,
):
    headers['Accept-Language'] = 'en'
    headers.update(DAP_APP_HEADERS)
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/support_chat/list_archived',
        headers=headers,
        cookies=cookies,
        params=params,
        json=request_data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    search_call = mock_search.calls[0]
    for key, value in expected_search_kwargs.items():
        assert search_call['kwargs'][key] == value

    assert 'headers' in search_call['kwargs']
    assert 'Accept-Language' in search_call['kwargs']['headers']
    assert search_call['kwargs']['headers']['Accept-Language'] == 'en'


@pytest.mark.parametrize(
    (
        'params',
        'park_id',
        'driver_profile_id',
        'selfreg_token',
        'request_data',
        'headers',
        'expected_read_kwargs',
        'expected_support_chat',
        'expected_status',
    ),
    [
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {},
            {},
            {
                'chat_id': '5bcdb13084b5976d23aa01bb',
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'platform': 'taximeter',
            },
            {
                'id': '5bcdb13084b5976d23aa01bb',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                    'platform': 'taximeter',
                },
            },
            200,
        ),
        (
            None,
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {},
            {'User-agent': 'taximeter-vezet'},
            {
                'chat_id': '5bcdb13084b5976d23aa01bb',
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'platform': 'vezet',
            },
            {
                'id': '5bcdb13084b5976d23aa01bb',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                    'platform': 'vezet',
                },
            },
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'bad_selfreg_token',
            {},
            {},
            None,
            None,
            401,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'some_selfreg_token',
            {},
            {},
            {
                'chat_id': '5bcdb13084b5976d23aa01bb',
                'owner_id': 'some_selfreg_id',
                'owner_role': 'selfreg_driver',
                'platform': 'taximeter',
            },
            {
                'id': '5bcdb13084b5976d23aa01bb',
                'metadata': {
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                    'platform': 'taximeter',
                },
            },
            200,
        ),
    ],
)
@pytest.mark.translations(**conftest.TRANSLATIONS)
async def test_read_new(
        mock_read,
        mock_driver_profiles,
        mock_personal,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_selfreg_validate,
        taxi_driver_support_client,
        params,
        park_id,
        driver_profile_id,
        selfreg_token,
        request_data,
        headers,
        expected_read_kwargs,
        expected_support_chat,
        expected_status,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'GET')
    def patch_support_chat_request(method, url, **kwargs):
        assert method == 'get'
        return response_mock(json=expected_support_chat)

    @patch('taxi_driver_support.internal.notification.send_driver_push')
    async def send_driver_push(app, chat_id, task_id, **kwargs):
        chat_response = await app.support_chat_client.get_chat(chat_id)
        meta_data = chat_response.get('metadata', {})
        assert kwargs.get('zero_messages') and meta_data['new_messages'] == 0

    cookies = {}
    headers.update(DAP_APP_HEADERS)
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.post(
        (
            '/driver/v1/driver-support/'
            'v1/support_chat/5bcdb13084b5976d23aa01bb/read/'
        ),
        headers=headers,
        cookies=cookies,
        params=params,
        json=request_data,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    read = mock_read.calls[0]
    read['kwargs'].pop('log_extra')
    assert read['kwargs'] == expected_read_kwargs


@pytest.mark.config(
    DRIVER_SUPPORT_ALLOWED_FILE_TYPES=[
        'image/png',
        'image/jpg',
        'application/octet-stream',
        'text/plain',
    ],
)
@pytest.mark.parametrize(
    'params,owner_id,owner_role,park_id,driver_profile_id,selfreg_token,'
    'chat_id,file,filename,content_type,idempotency_token,expected_result,'
    'expected_status',
    [
        (
            {},
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            '5bcdb13084b5976d23aa01bb',
            b'test',
            'test_filename',
            'text/plain',
            'test_token',
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            200,
        ),
        (
            {},
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            '5bcdb13084b5976d23aa01bb',
            b'\x90\x01',
            'test_filename',
            'application/octet-stream',
            'test_token',
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'bad_selfreg_token',
            '5bcdb13084b5976d23aa01bb',
            b'test',
            'test_filename',
            'text/plain',
            'test_token',
            None,
            401,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'some_selfreg_token',
            '5bcdb13084b5976d23aa01bb',
            b'test',
            'test_filename',
            'text/plain',
            'test_token',
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'some_selfreg_token',
            '5bcdb13084b5976d23aa01bb',
            b'\x90\x01',
            'test_filename',
            'application/octet-stream',
            'test_token',
            {'attachment_id': 'ce094fa09693604fb88de28e4876f8c38a5548d3'},
            200,
        ),
    ],
)
async def test_attach_file_new(
        taxi_driver_support_client,
        response_mock,
        mock_driver_profiles,
        mock_personal,
        patch_aiohttp_session,
        mock_selfreg_validate,
        params,
        owner_id,
        owner_role,
        park_id,
        driver_profile_id,
        selfreg_token,
        chat_id,
        file,
        filename,
        content_type,
        idempotency_token,
        expected_result,
        expected_status,
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
            'sender_role': owner_role,
            'sender_id': owner_id,
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

    params.update(
        {'filename': filename, 'idempotency_token': idempotency_token},
    )
    headers = DAP_APP_HEADERS
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/support_chat/attach_file/',
        data=file,
        params=params,
        headers=headers,
        cookies=cookies,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    assert await response.json() == expected_result


@pytest.mark.parametrize(
    'params, owner_id, owner_role, park_id, driver_profile_id, selfreg_token, '
    'expected_status',
    [
        (
            {},
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            400,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'bad_selfreg_token',
            401,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'some_selfreg_token',
            400,
        ),
    ],
)
@pytest.mark.parametrize('file', [b'test', b'\x90\x01'])
async def test_attach_file_bad_mime_type_new(
        taxi_driver_support_client,
        mock_selfreg_validate,
        mock_driver_profiles,
        mock_personal,
        params,
        owner_id,
        owner_role,
        park_id,
        driver_profile_id,
        selfreg_token,
        file,
        expected_status,
):
    params.update({'filename': 'filename', 'idempotency_token': 'test_token'})
    headers = DAP_APP_HEADERS
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/support_chat/attach_file/',
        data=file,
        params=params,
        headers=headers,
        cookies=cookies,
    )
    assert response.status == expected_status


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'driver-support', 'dst': 'support_chat'},
        {'src': 'driver-support', 'dst': 'personal'},
    ],
    TVM_ENABLED=True,
)
@pytest.mark.parametrize(
    'params, park_id, driver_profile_id, selfreg_token, chat_id, '
    'attachment_id, preview, expected_redirect, expected_status',
    [
        (
            {},
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            False,
            '/v1/chat/5c504337779fb336b89182a2/attachment/'
            'b444ac06613fc8d63795be9ad0beaf55011936ac'
            '?sender_id=5bc702f995572fa0df26e0e2&sender_role=driver',
            200,
        ),
        (
            {},
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            True,
            '/v1/chat/5c504337779fb336b89182a2/attachment/'
            'b444ac06613fc8d63795be9ad0beaf55011936ac'
            '?sender_id=5bc702f995572fa0df26e0e2&sender_role=driver'
            '&size=preview',
            200,
        ),
        (
            {},
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            '5c504337779fb336b89182a3',
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f',
            False,
            '/v1/chat/5c504337779fb336b89182a3/attachment/'
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f'
            '?sender_id=5bc702f995572fa0df26e0e2&sender_role=driver',
            200,
        ),
        (
            {},
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            '5c504337779fb336b89182a3',
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f',
            True,
            '/v1/chat/5c504337779fb336b89182a3/attachment/'
            '109f4b3c50d7b0df729d299bc6f8e9ef9066971f'
            '?sender_id=5bc702f995572fa0df26e0e2&sender_role=driver'
            '&size=preview',
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'bad_selfreg_token',
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            False,
            None,
            401,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'some_selfreg_token',
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            False,
            '/v1/chat/5c504337779fb336b89182a2/attachment/'
            'b444ac06613fc8d63795be9ad0beaf55011936ac'
            '?sender_id=some_selfreg_id&sender_role=selfreg_driver',
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            None,
            None,
            'some_selfreg_token',
            '5c504337779fb336b89182a2',
            'b444ac06613fc8d63795be9ad0beaf55011936ac',
            True,
            '/v1/chat/5c504337779fb336b89182a2/attachment/'
            'b444ac06613fc8d63795be9ad0beaf55011936ac'
            '?sender_id=some_selfreg_id&sender_role=selfreg_driver'
            '&size=preview',
            200,
        ),
    ],
)
async def test_download_file_new(
        taxi_driver_support_client,
        patch,
        mock_selfreg_validate,
        mock_driver_profiles,
        mock_personal,
        params,
        park_id,
        driver_profile_id,
        selfreg_token,
        chat_id,
        attachment_id,
        preview,
        expected_redirect,
        expected_status,
):
    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return 'Ticket 123'

    @patch('taxi.clients.tvm.check_tvm')
    async def get_check_tvm(*args, **kwargs):
        return tvm.CheckResult(src_service_name='DRIVER-SUPPORT')

    if preview:
        params['size'] = 'preview'
    headers = DAP_APP_HEADERS
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.get(
        '/driver/v1/driver-support/v1/support_chat/%s/attachment/%s'
        % (chat_id, attachment_id),
        params=params,
        headers=headers,
        cookies=cookies,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    assert response.headers['X-Accel-Redirect'] == expected_redirect
    assert response.headers['X-Ya-Service-Ticket'] == 'Ticket 123'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'params, owner_id, owner_role, park_id, driver_profile_id, selfreg_token, '
    'headers, expected_platform, support_info_response, result, '
    'expected_status',
    [
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'user-agent': 'taximeter-uber'},
            'uberdriver',
            {
                'archive': False,
                'open': False,
                'visible': True,
                'open_chat_new_messages_count': 0,
                'visible_chat_new_messages_count': 0,
            },
            {'archive': False, 'open': False, 'new_messages_count': 0},
            200,
        ),
        (
            None,
            UNIQUE_DRIVER_ID,
            'driver',
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            None,
            {'user-agent': 'taximeter'},
            'taximeter',
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 2,
                'visible_chat_new_messages_count': 3,
            },
            {'archive': False, 'open': True, 'new_messages_count': 2},
            200,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'bad_selfreg_token',
            {'user-agent': 'taximeter'},
            None,
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 2,
                'visible_chat_new_messages_count': 3,
            },
            None,
            401,
        ),
        (
            {'chat_type': 'selfreg_driver_support'},
            'some_selfreg_id',
            'selfreg_driver',
            None,
            None,
            'some_selfreg_token',
            {'user-agent': 'taximeter'},
            'taximeter',
            {
                'archive': False,
                'open': True,
                'visible': True,
                'open_chat_new_messages_count': 2,
                'visible_chat_new_messages_count': 3,
            },
            {'archive': False, 'open': True, 'new_messages_count': 2},
            200,
        ),
    ],
)
async def test_summary_new(
        taxi_driver_support_client,
        patch_aiohttp_session,
        mock_driver_session,
        response_mock,
        mock_selfreg_validate,
        mock_driver_profiles,
        mock_personal,
        params,
        owner_id,
        owner_role,
        park_id,
        driver_profile_id,
        selfreg_token,
        headers,
        expected_platform,
        support_info_response,
        result,
        expected_status,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def _dummy_request(method, url, **kwargs):
        assert method == 'post'
        assert url == 'http://support-chat.taxi.dev.yandex.net/v1/chat/summary'
        assert kwargs['json'] == {
            'owner': {
                'id': owner_id,
                'role': owner_role,
                'platform': expected_platform,
            },
        }
        return response_mock(json=support_info_response)

    headers['Accept-Language'] = 'en'
    headers.update(DAP_APP_HEADERS)
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if selfreg_token:
        cookies['webviewselfregtoken'] = selfreg_token
    response = await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/support_chat/summary',
        headers=headers,
        cookies=cookies,
        params=params,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return
    assert await response.json() == result
