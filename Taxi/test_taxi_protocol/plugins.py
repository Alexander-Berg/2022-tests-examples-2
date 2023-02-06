# pylint: disable=redefined-outer-name,duplicate-code,unused-variable
import copy
import uuid

import pytest

from taxi.clients import experiments3
from taxi.clients import passport
from taxi.clients import support_chat
from taxi.clients import territories

from taxi_protocol import csat

pytest_plugins = ['taxi.pytest_plugins.stq_agent']


CHAT_RESPONSE = {
    'id': '5ff4901c583745e089e55be4',
    'status': {'is_open': True, 'is_visible': True},
    'participants': [
        {'id': 'client_id', 'role': 'client'},
        {
            'id': 'support_id',
            'role': 'support',
            'nickname': 'support_name',
            'avatar_url': 'support_avatar',
        },
    ],
    'messages': [
        {
            'id': 'message_id',
            'text': 'Привет!',
            'metadata': {'created': '2018-10-20T12:34:56'},
            'sender': {'id': 'client_id', 'role': 'client'},
        },
    ],
    'metadata': {'ask_csat': False, 'new_messages': 0},
    'actions': [],
    'view': {'show_message_input': True},
}

EXPERIMENT_CSAT_RESPONSE = {
    'csat_options': {
        'questions': [
            {
                'id': 'quality_score',
                'text': 'user_chat_csat.quality_score',
                'with_input': False,
                'values': [
                    {
                        'id': 'horrible',
                        'text': 'user_chat_csat.horrible',
                        'with_input': False,
                        'shuffle': True,
                        'reasons': [
                            {
                                'id': 'long_answer',
                                'text': 'user_chat_csat_reasons.long_answer',
                                'with_input': False,
                                'shuffle': True,
                                'reasons': [
                                    {
                                        'id': 'long_initial_answer',
                                        'text': (
                                            'user_chat_csat_reasons'
                                            '.long_initial_answer'
                                        ),
                                        'with_input': False,
                                    },
                                    {
                                        'id': 'long_interval_answer',
                                        'text': (
                                            'user_chat_csat_reasons'
                                            '.long_interval_answer'
                                        ),
                                        'with_input': False,
                                    },
                                ],
                            },
                            {
                                'id': 'template_answer',
                                'text': (
                                    'user_chat_csat_reasons.template_answer'
                                ),
                                'with_input': False,
                            },
                            {
                                'id': 'disagree_solution',
                                'text': (
                                    'user_chat_csat_reasons.disagree_solution'
                                ),
                                'with_input': False,
                            },
                            {
                                'id': 'problem_not_solved',
                                'text': (
                                    'user_chat_csat_reasons.problem_not_solved'
                                ),
                                'with_input': False,
                            },
                        ],
                    },
                    {
                        'id': 'good',
                        'text': 'user_chat_csat.good',
                        'with_input': False,
                    },
                    {
                        'id': 'amazing',
                        'text': 'user_chat_csat.amazing',
                        'with_input': False,
                    },
                ],
            },
            {
                'id': 'response_speed_score',
                'text': 'user_chat_csat.response_speed_score',
                'with_input': False,
                'values': [
                    {
                        'id': 'horrible',
                        'text': 'user_chat_csat.horrible',
                        'with_input': False,
                    },
                    {
                        'id': 'good',
                        'text': 'user_chat_csat.good',
                        'with_input': False,
                    },
                    {
                        'id': 'amazing',
                        'text': 'user_chat_csat.amazing',
                        'with_input': False,
                    },
                ],
            },
        ],
    },
}


def add_actions(chat):
    chat['actions'] = [
        {
            'action_id': 'anime',
            'type': 'questionary',
            'content': {
                'question': 'anime_text',
                'items': [
                    {
                        'action_id': 'anime1',
                        'type': 'text',
                        'title': 'Yes',
                        'params': {'text': 'Yes'},
                    },
                    {
                        'action_id': 'anime2',
                        'type': 'text',
                        'title': 'No',
                        'params': {'text': 'No'},
                    },
                ],
            },
        },
    ]
    return chat


@pytest.fixture
async def protocol_app(web_app):
    await web_app.startup()
    yield web_app
    await web_app.shutdown()


@pytest.fixture
async def protocol_client(aiohttp_client, protocol_app, territories_mock):
    return await aiohttp_client(protocol_app)


class MockPassportClient:
    async def get_token_info(
            self, bearer, real_ip, required_scopes, log_extra,
    ):
        return passport.Token(
            yandex_uid=bearer,
            login='Test',
            is_staff=False,
            scopes=(),
            token_expires='2020-01-14 16:37:13',
            uber_id=bearer,
        )


class MockTerritoriesCllient:
    def __init__(self, db):
        self.db = db

    async def get_country(self, country):
        return await self.db.countries.find_one({'_id': country})


@pytest.fixture
def mock_get_all_countries(monkeypatch):
    async def _dummy_get_all_countries(self, log_extra=None):
        return [
            {
                'phone_code': '7',
                'phone_min_length': 10,
                'phone_max_length': 12,
            },
        ]

    monkeypatch.setattr(
        territories.TerritoriesApiClient,
        'get_all_countries',
        _dummy_get_all_countries,
    )


@pytest.fixture
def mock_passport(monkeypatch, protocol_app):
    monkeypatch.setattr(protocol_app, 'passport', MockPassportClient())


@pytest.fixture
def mock_chat_create(monkeypatch, mock):
    def _mock_chat_create(actions=False):
        @mock
        async def _dummy_create(*args, **kwargs):
            chat = copy.deepcopy(CHAT_RESPONSE)
            if actions:
                chat = add_actions(chat)
            return chat

        monkeypatch.setattr(
            support_chat.SupportChatApiClient, 'create_chat', _dummy_create,
        )
        return _dummy_create

    return _mock_chat_create


@pytest.fixture
def mock_chat_defaults(monkeypatch, mock):
    @mock
    async def defaults(*args, **kwargs):
        return {'actions': [], 'view': {'show_message_input': True}}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'defaults', defaults,
    )
    return defaults


@pytest.fixture
def mock_chat_search(monkeypatch, mock):
    @mock
    async def search(owner_id, *args, **kwargs):
        chats = {'chats': [copy.deepcopy(CHAT_RESPONSE)]}
        if owner_id in ['539eb65be7e5b1f53980dfa8', '12']:
            return chats
        if owner_id == '13c726a0440481a6d4208f6d834961400f7c8906':
            chats['chats'][0]['id'] = '5ff4901c583745e089e55be7'
            return chats
        if owner_id == '539eb65be7e5b1f53980dfa9':
            chats['chats'][0]['status']['is_visible'] = False
            return chats
        return {'chats': []}

    monkeypatch.setattr(support_chat.SupportChatApiClient, 'search', search)
    return search


@pytest.fixture
def mock_zendesk_ticket_create(patch):
    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_create')
    async def _ticket_create(*args, **kwargs):
        return {}

    return _ticket_create


@pytest.fixture
def mock_zendesk_get_by_external_id(patch):
    @patch('taxi.clients.zendesk.ZendeskApiClient.get_tickets_by_external_id')
    async def _get_tickets_by_external_id(*args, **kwargs):
        return {'tickets': []}

    return _get_tickets_by_external_id


@pytest.fixture
def mock_chat_add_update(monkeypatch, mock):
    @mock
    async def _dummy_add_update(*args, **kwargs):
        if not hasattr(_dummy_add_update, 'prev'):
            setattr(_dummy_add_update, 'prev', [])
        if kwargs['message_id'] in _dummy_add_update.prev:
            raise support_chat.ConflictError
        _dummy_add_update.prev.append(kwargs['message_id'])
        chat = copy.deepcopy(CHAT_RESPONSE)
        return {'chat': chat}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )
    return _dummy_add_update


@pytest.fixture
def mock_get_users(mockserver, load_json):
    users = load_json('user_api_users.json')

    @mockserver.json_handler('/user-api/users/get')
    def _get_user(request):
        for user in users:
            if request.json['id'] == user['id']:
                return user
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/user-api/users/search')
    def _search_users(request):
        yandex_uid = request.json['yandex_uid']
        response = []
        for user in users:
            if 'yandex_uid' in user and yandex_uid == user['yandex_uid']:
                response.append(user)
        return {'items': response}


@pytest.fixture
def mock_stq_put(patch):
    @patch('taxi.stq.client.put')
    async def _put(
            queue, task_id=None, args=None, kwargs=None, eta=None, loop=None,
    ):
        pass

    return _put


@pytest.fixture
def mock_uuid_fixture(patch):
    @patch('uuid.uuid4')
    def uuid4():
        return uuid.UUID('2104653b-dac3-43e3-9ac5-7869d0bd738d')

    return uuid4


@pytest.fixture
def mock_get_user_phone_from_db(patch):
    @patch('taxi.clients.user_api._get_user_phone_from_db')
    async def _get_user_phone_from_db(*args, **kwargs):
        assert str(args[1]) == '1234567890abcdef7890abcd'
        return {'phone': 'test_phone', 'type': 'yandex'}


@pytest.fixture
def mock_chat_new(monkeypatch, mock):
    def _wrapper(setting):
        @mock
        async def create_new_chat(
                owner_id,
                owner_role,
                message_text,
                message_sender_id,
                message_sender_role,
                metadata=None,
                message_metadata=None,
                platform=None,
                include_history=False,
                **kwargs,
        ):
            if 'request' in setting:
                request_data = {
                    'owner': {'id': owner_id, 'role': owner_role},
                    'message': {
                        'text': message_text,
                        'sender': {
                            'id': message_sender_id,
                            'role': message_sender_role,
                        },
                    },
                }
                if include_history:
                    request_data['include_history'] = include_history
                if metadata is not None:
                    request_data['metadata'] = metadata
                if message_metadata is not None:
                    request_data['message']['metadata'] = message_metadata
                if platform is not None:
                    request_data['owner']['platform'] = platform
                    request_data['message']['sender']['platform'] = platform
                assert request_data == setting['request']
            return setting['response']

        monkeypatch.setattr(
            support_chat.SupportChatApiClient,
            'create_new_chat',
            create_new_chat,
        )

    return _wrapper


@pytest.fixture
def mock_get_chat(monkeypatch, mock, load_json):
    chats = load_json('chat_get_mock.json')

    @mock
    async def get_chat(chat_id, *args, **kwargs):
        for chat in chats:
            if chat['id'] == chat_id:
                return chat

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )
    return get_chat


@pytest.fixture
def mock_chat_history(monkeypatch, mock, load_json):
    chats = load_json('chat_history_mock.json')

    @mock
    async def get_history(user_chat_message_id, *args, **kwargs):
        return chats.get(user_chat_message_id)

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_history', get_history,
    )
    return get_history


@pytest.fixture
def mock_read_chat(monkeypatch, mock):
    @mock
    async def read(*args, **kwargs):
        pass

    monkeypatch.setattr(support_chat.SupportChatApiClient, 'read', read)


@pytest.fixture
def mock_chat_search_json(monkeypatch, mock, load_json):
    chats = load_json('chat_get_mock.json')

    @mock
    async def search(owner_id, chat_type, *args, **kwargs):
        is_open = chat_type == 'open'
        filtered_chats = [
            chat for chat in chats if chat['status']['is_open'] == is_open
        ]
        if kwargs.get('date_older_than'):
            filtered_chats = filtered_chats[1:]
        if kwargs.get('date_limit'):
            filtered_chats = filtered_chats[:1]
        return {'chats': filtered_chats}

    monkeypatch.setattr(support_chat.SupportChatApiClient, 'search', search)
    return search


@pytest.fixture
def mock_exp3_get_values(patch):
    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _get_values(
            consumer,
            experiments_args,
            client_application=None,
            user_agent=None,
            log_extra=None,
    ):
        if consumer != csat.EXPERIMENT_CONSUMER:
            return []

        exp_args = {}
        for arg in experiments_args:
            exp_args[arg.name] = arg.value

        if exp_args.get('service') == 'dummy_service':
            return [
                experiments3.ExperimentsValue(
                    name=csat.EXPERIMENT_NAME,
                    value=copy.deepcopy(EXPERIMENT_CSAT_RESPONSE),
                ),
            ]
        return []

    return _get_values
