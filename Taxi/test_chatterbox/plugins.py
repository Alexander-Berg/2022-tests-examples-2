# pylint: disable=redefined-outer-name, unused-variable, too-many-lines
# pylint: disable=invalid-name
import concurrent
import datetime
import json
import typing
import uuid

from aiohttp import web
import asynctest
import bson
import magic
import pytest

from taxi import discovery
from taxi import settings
from taxi.clients import admin
from taxi.clients import dealapp
from taxi.clients import eats_support_misc
from taxi.clients import messenger_chat_mirror as messenger
from taxi.clients import salesforce
from taxi.clients import startrack
from taxi.clients import support_chat
from taxi.clients.helpers import errors
from taxi.maintenance import run

from chatterbox import app_stq
from chatterbox import constants
from chatterbox import cron_run
from chatterbox.generated.service.config import plugin as config
from chatterbox.internal import logbroker
from chatterbox.internal import tasks_manager
from chatterbox.internal.task_source import manager
from test_chatterbox import helpers


pytest_plugins = [
    'taxi.pytest_plugins.stq_agent',
    'taxi.pytest_plugins.order_archive',
]


CHATTERBOX_CSRF_SECRET = 'WqkQ?x]~mY;^w0o7s6{mJtQiQ(rV57=;Q<dTaRmb9)6[Kz=q-Q'

SUPPORT_MODERATION_API_KEY = 'test_token'

STARTRACK_CLIENT_ID = str(config.Config.STARTRACK_EMAIL_USER_ID)
STARTRACK_SUPPORT_ID = str(config.Config.STARTRACK_SUPPORT_USER_ID)

CHATTERBOX_API_KEY_TAXI = 'support-taxi_api_key'
CHATTERBOX_API_KEY_ZEN = 'support-zen_api_key'
CHATTERBOX_API_KEY_STARTREK = 'startrek_api_key'

ALLOW_KEYS_ANTIFRAUD_REFAUND = [
    'user_device_id',
    'user_id',
    'order_id',
    'timestamp',
    'user_personal_phone_id',
    'dialogue',
    'type_ticket',
    'params',
    'driver_license_personal_id',
]

STARTRACK_EXTRA_TICKET_PROFILES = {
    'support-taxi': {
        'allowed_queues': [],
        'gui_url': 'https://tracker.yandex.ru',
    },
    'support-zen': {
        'allowed_queues': [],
        'gui_url': 'https://tracker.yandex.ru',
    },
    'yandex-team': {
        'allowed_queues': [],
        'gui_url': 'https://st.yandex-team.ru',
    },
}


@pytest.fixture
def tracker_url():
    return 'https://tracker.yandex.ru/'


@pytest.fixture
def simple_secdist(simple_secdist, tracker_url: str):
    simple_secdist['settings_override'].update(
        {
            'CHATTERBOX_CSRF_SECRET': CHATTERBOX_CSRF_SECRET,
            'CHATTERBOX_API_KEYS': {
                CHATTERBOX_API_KEY_TAXI: 'support-taxi',
                CHATTERBOX_API_KEY_ZEN: 'support-zen',
                CHATTERBOX_API_KEY_STARTREK: 'yandex-team',
            },
            'SUPPORT_MODERATION_API_KEY': SUPPORT_MODERATION_API_KEY,
            'ARCHIVE_API_TOKEN': 'archive_api_token',
            'STARTRACK_API_PROFILES': {
                'support-taxi': {
                    'url': tracker_url,
                    'org_id': 1,
                    'oauth_token': 'test_token',
                },
                'support-zen': {
                    'url': tracker_url,
                    'org_id': 2,
                    'oauth_token': 'test_token2',
                },
            },
            'TELEGRAM_SUPPORT_BOT_API_KEY': '1234:test_api_key',
            'CHATTERBOX_SIP_API_KEY': 'API_KEY',
            'COMPENDIUM_API_KEY': 'COMPENDIUM_KEY',
            'SUPPORT_OAUTH_TOKEN_FOR_API_ADMIN_PY3': (
                'api_admin_py3_oauth_token'
            ),
            'CHATTERBOX_API_ROLES_BY_KEY': {
                'some_telphin_token': 'telphin',
                'some_oktell_token': 'oktell',
            },
            'SALESFORCE_API_PROFILES': {
                'salesforceg': {
                    'url': 'salesforce',
                    'client_id': 'client_id',
                    'client_secret': 'client_secret',
                    'grant_type': 'grant_type',
                    'password': 'password',
                    'username': 'username',
                },
            },
        },
    )
    return simple_secdist


class CboxWrap:
    # pylint: disable=too-many-instance-attributes

    def __init__(self, app, client):
        self.app = app
        self.db = app.db
        self.client = client
        self.settings = app.settings
        self.body = None
        self.headers = None
        self.status = None
        self.cookies = None

    async def query(self, path, params=None, headers=None):
        resp = await self.client.get(path, params=params, headers=headers)
        self.status = resp.status
        self.body = await resp.text()
        self.headers = resp.headers
        return resp

    async def post(
            self, path, params=None, data=None, raw_data=None, headers=None,
    ):
        resp = await self.client.post(
            path, params=params, json=data, data=raw_data, headers=headers,
        )
        self.status = resp.status
        self.body = await resp.text()
        self.cookies = resp.cookies
        return resp

    @property
    def body_data(self):
        return json.loads(self.body)

    def set_user(self, user):
        self.client.session.cookie_jar.update_cookies(
            {
                'Session_id': '{0}_sid'.format(user),
                'yandexuid': '{}_uid'.format(user),
                'sessionid2': '{}_sid2'.format(user),
            },
        )

    async def get_csrf_token(self):
        """Get CSRF token for tests"""
        await self.post('/me', data={})
        assert self.status == 200
        return self.body_data['csrf_token']


@pytest.fixture
async def cbox(cbox_app, cbox_client):
    return CboxWrap(app=cbox_app, client=cbox_client)


@pytest.fixture
async def cbox_app(web_app, territories_mock):
    await web_app.startup()
    yield web_app
    await web_app.shutdown()


@pytest.fixture
async def cbox_client(aiohttp_client, cbox_app, loop):
    return await aiohttp_client(cbox_app)


@pytest.fixture
async def cbox_stq(simple_secdist):
    stq_app = app_stq.create_app()
    await stq_app.startup()
    yield stq_app
    await stq_app.shutdown()


@pytest.fixture
async def cbox_context(loop, db, simple_secdist):
    async for context_data in cron_run.create_app():
        yield run.StuffContext(
            None, 'test_task_id', datetime.datetime.utcnow(), context_data,
        )


@pytest.fixture
def set_user(cbox_client, user):
    cbox_client.session.cookie_jar.update_cookies(
        {
            'Session_id': '{0}_sid'.format(user),
            'yandexuid': '{}_uid'.format(user),
            'sessionid2': '{}_sid2'.format(user),
        },
    )


@pytest.fixture
async def get_csrf_token(cbox_client):
    """Get CSRF token for tests"""
    response = await cbox_client.post('/me', data={})
    assert response.status == 200
    body_data = await response.json()
    return body_data['csrf_token']


@pytest.fixture
def mock_chat_add_update_raise(monkeypatch, mock):
    def _wrap(exc):
        @mock
        async def _dummy_add_update(*args, **kwargs):
            raise exc

        monkeypatch.setattr(
            support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
        )
        monkeypatch.setattr(
            messenger.MessengerChatMirrorApiClient,
            'add_update',
            _dummy_add_update,
        )
        return _dummy_add_update

    return _wrap


@pytest.fixture
def mock_uuid_uuid4(monkeypatch, mock):
    @mock
    def _dummy_uuid4():
        return uuid.UUID(int=0, version=4)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)


@pytest.fixture
def mock_chat_add_update(monkeypatch, mock):
    @mock
    async def _dummy_add_update(*args, **kwargs):
        return {'message_id': str(uuid.uuid4())}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )
    monkeypatch.setattr(
        messenger.MessengerChatMirrorApiClient,
        'add_update',
        _dummy_add_update,
    )
    return _dummy_add_update


@pytest.fixture
def mock_chat_create(monkeypatch, mock):
    @mock
    async def _dummy_create(*args, **kwargs):
        if kwargs.get('owner_id') == 'task_closed':
            return {'id': 'task_closed_chat_id'}
        if kwargs.get('owner_id') == 'task_broken':
            return {'id': 'task_broken_chat_id'}
        if kwargs.get('owner_id') == 'race_task':
            return {'id': 'race_task_chat_id'}
        return {'id': 'created_chat_id'}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'create_chat', _dummy_create,
    )
    return _dummy_create


@pytest.fixture
def mock_chat_create_new(monkeypatch, mock):
    @mock
    async def _dummy_create_new(*args, **kwargs):
        if kwargs.get('owner_id') == 'task_closed':
            return {'id': 'task_closed_chat_id'}
        if kwargs.get('owner_id') == 'task_broken':
            return {'id': 'task_broken_chat_id'}
        if kwargs.get('owner_id') == 'race_task':
            return {'id': 'race_task_chat_id'}
        return {'id': 'created_chat_id'}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient,
        'create_new_chat',
        _dummy_create_new,
    )
    return _dummy_create_new


@pytest.fixture
def mock_chat_search(monkeypatch, mock):
    @mock
    async def _dummy_search(*args, **kwargs):
        assert 'exclude_request_id' in kwargs

        if kwargs.get('owner_id') == 'task_exists':
            return {
                'chats': [
                    {
                        'id': 'task_exists_chat_id',
                        'metadata': {'chatterbox_id': 'existing_task_id'},
                    },
                ],
            }
        if kwargs.get('owner_id') == 'task_broken':
            return {'chats': [{'id': 'task_broken_chat_id', 'metadata': {}}]}
        return {'chats': []}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'search', _dummy_search,
    )
    return _dummy_search


@pytest.fixture
def mock_get_race_chat(monkeypatch, mock):
    def _wrap(uuid1='uuid1', uuid2='uuid2'):
        mock_uuid = asynctest.Mock()
        mock_uuid.side_effect = [uuid1, *[uuid2 for _ in range(10)]]

        @mock
        async def _dummy_get_chat(*args, **kwargs):
            return {'newest_message_id': mock_uuid()}

        monkeypatch.setattr(
            support_chat.SupportChatApiClient, 'get_chat', _dummy_get_chat,
        )
        monkeypatch.setattr(
            messenger.MessengerChatMirrorApiClient,
            'get_chat',
            _dummy_get_chat,
        )
        return _dummy_get_chat

    return _wrap


@pytest.fixture
def mock_get_chat(monkeypatch, mock):
    @mock
    async def _dummy_get_chat(*args, **kwargs):
        return {
            'id': 'some_chat_id',
            'participants': [
                {'id': 'owner_id', 'role': 'client', 'is_owner': True},
            ],
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', _dummy_get_chat,
    )
    monkeypatch.setattr(
        messenger.MessengerChatMirrorApiClient, 'get_chat', _dummy_get_chat,
    )
    return _dummy_get_chat


@pytest.fixture
def mock_chat_get_history(monkeypatch, mock):
    def _wrap(chat_messages):
        @mock
        async def _dummy_get_history(*args, **kwargs):
            return chat_messages

        monkeypatch.setattr(
            support_chat.SupportChatApiClient,
            'get_history',
            _dummy_get_history,
        )
        monkeypatch.setattr(
            messenger.MessengerChatMirrorApiClient,
            'get_history',
            _dummy_get_history,
        )
        return _dummy_get_history

    return _wrap


@pytest.fixture
def mock_chat_mark_processed(monkeypatch, mock):
    @mock
    async def _dummy_mark_processed(*args, **kwargs):
        pass

    monkeypatch.setattr(
        support_chat.SupportChatApiClient,
        'mark_processed',
        _dummy_mark_processed,
    )
    monkeypatch.setattr(
        messenger.MessengerChatMirrorApiClient,
        'mark_processed',
        _dummy_mark_processed,
    )
    return _dummy_mark_processed


@pytest.fixture
def mock_source_download_file(monkeypatch, mock):
    @mock
    async def _dummy_download_file(*args, **kwargs):
        return bytes('some binary data', encoding='utf-8')

    monkeypatch.setattr(
        manager.TaskSourceManager, 'download_file', _dummy_download_file,
    )
    return _dummy_download_file


@pytest.fixture
def mock_task_manager_update_task(monkeypatch, mock):
    method_patcher = helpers.BaseAsyncPatcher(
        target=tasks_manager.TasksManager,
        method='_update_assigned_task',
        response_body=None,
    )
    method_patcher.patch(monkeypatch)
    return method_patcher


@pytest.fixture
def mock_admin_generate_promocode(monkeypatch) -> helpers.BaseAsyncPatcher:
    client_patcher = helpers.BaseAsyncPatcher(
        target=admin.AdminApiClient,
        method='generate_promocode',
        response_body={'code': '_promo_code_'},
    )
    client_patcher.patch(monkeypatch)
    return client_patcher


@pytest.fixture
def mock_admin_rebill_order(monkeypatch) -> helpers.BaseAsyncPatcher:
    client_patcher = helpers.BaseAsyncPatcher(
        target=admin.AdminApiClient, method='rebill_order', response_body={},
    )
    client_patcher.patch(monkeypatch)
    return client_patcher


@pytest.fixture
def mock_st_get_ticket_with_status(monkeypatch, mock):
    def _wrap(
            status,
            tags=None,
            custom_fields=None,
            data_constructor=None,
            profile=None,
    ):
        if data_constructor is None:
            data_constructor = _ticket_data

        @mock
        async def _dummy_get_ticket(ticket, profile=None):
            return data_constructor(ticket, status, tags, custom_fields)

        monkeypatch.setattr(
            startrack.StartrackAPIClient, 'get_ticket', _dummy_get_ticket,
        )
        return _dummy_get_ticket

    return _wrap


@pytest.fixture
def mock_st_get_ticket(mock_st_get_ticket_with_status):
    return mock_st_get_ticket_with_status(constants.TICKET_STATUS_OPEN)


@pytest.fixture
def mock_st_search(monkeypatch, mock):
    @mock
    async def _dummy_search(**kwargs):
        unique = kwargs.get('json_filter', {}).get('unique')
        if unique == 'other_task_duplicated_request_id':
            return []
        return [_ticket_data('YANDEXTAXI-0', constants.TICKET_STATUS_OPEN)]

    monkeypatch.setattr(startrack.StartrackAPIClient, 'search', _dummy_search)
    return _dummy_search


@pytest.fixture
def mock_st_get_comments(monkeypatch, mock):
    def _wrap(comments):
        @mock
        async def _dummy_get_comments(ticket, **kwargs):
            return comments

        monkeypatch.setattr(
            startrack.StartrackAPIClient, 'get_comments', _dummy_get_comments,
        )
        return _dummy_get_comments

    return _wrap


@pytest.fixture
def mock_st_get_messages(monkeypatch, patch):
    def _wrap(messages):
        @patch(
            'chatterbox.internal.task_source._startrack.'
            'Startrack.get_messages',
        )
        async def _dummy_get_messages(*args, **kwargs):
            return messages

        return _dummy_get_messages

    return _wrap


@pytest.fixture
def mock_st_update_ticket(monkeypatch, mock):
    def _wrap(status):
        @mock
        async def _dummy_update_ticket(ticket, *args, **kwargs):
            return _ticket_data(ticket, status)

        monkeypatch.setattr(
            startrack.StartrackAPIClient,
            'update_ticket',
            _dummy_update_ticket,
        )
        return _dummy_update_ticket

    return _wrap


@pytest.fixture
def mock_st_get_all_attachments(monkeypatch, mock):
    def _wrap(empty=True, response=None):
        @mock
        async def _dummy_get_all_attachments(ticket, log_extra=None, **kwargs):
            if response:
                return response
            if empty:
                return []
            return [
                {
                    'id': '12',
                    'size': 35188,
                    'mimetype': 'image/png',
                    'createdAt': '2018-12-12T14:11:15.643+0000',
                    'name': 'Screen Shot 2018-10-26 at 12.54.39.png',
                    'link': 'https://trCHBOX-10/attachments/28?orgid=650580',
                    'link_preview': 'https://tr/CHBOX-10/thumbnail/28?orgid=6',
                },
            ]

        monkeypatch.setattr(
            startrack.StartrackAPIClient,
            'get_all_attachments',
            _dummy_get_all_attachments,
        )
        return _dummy_get_all_attachments

    return _wrap


@pytest.fixture
def mock_st_upload_attachment(monkeypatch, mock):
    def _wrap(attachment_id: str):
        @mock
        async def _dummy_upload_attachment(*args, **kwargs):
            return {'id': attachment_id}

        monkeypatch.setattr(
            startrack.StartrackAPIClient,
            'upload_attachment',
            _dummy_upload_attachment,
        )

        return _dummy_upload_attachment

    return _wrap


@pytest.fixture
def mock_chat_attachment(monkeypatch, mock):
    def _wrap(attachment_id: str):
        @mock
        async def _dummy_upload_attachment(*args, **kwargs):
            return {'attachment_id': attachment_id}

        monkeypatch.setattr(
            support_chat.SupportChatApiClient,
            'attach_file',
            _dummy_upload_attachment,
        )
        monkeypatch.setattr(
            messenger.MessengerChatMirrorApiClient,
            'attach_file',
            _dummy_upload_attachment,
        )
        return _dummy_upload_attachment

    return _wrap


@pytest.fixture
def mock_st_get_attachment(monkeypatch, mock):
    @mock
    async def _dummy_get_attachment(*args, **kwargs):
        return bytes('some binary startrack data', encoding='utf-8')

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'get_attachment', _dummy_get_attachment,
    )

    return _dummy_get_attachment


@pytest.fixture
def mock_st_create_comment(monkeypatch, mock):
    client_patcher = helpers.BaseAsyncPatcher(
        target=startrack.StartrackAPIClient,
        method='create_comment',
        response_body={
            'id': 1005005505045045040,
            'text': 'Test comment was created',
        },
    )
    client_patcher.patch(monkeypatch)
    return client_patcher


@pytest.fixture
def mock_st_create_ticket(monkeypatch, mock):
    @mock
    async def _dummy_create_ticket(**kwargs):
        if 'unique' in kwargs and 'duplicate' in kwargs['unique']:
            raise startrack.ConflictError
        return {'key': kwargs['queue'] + '-1'}

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'create_ticket', _dummy_create_ticket,
    )
    return _dummy_create_ticket


@pytest.fixture
def mock_st_transition(monkeypatch, mock):
    @mock
    async def _dummy_execute_transition(ticket, *args, **kwargs):
        transition = kwargs.get('transition') or ''
        if ticket.startswith('closed'):
            raise startrack.NotFoundError('Transition _close not found')
        if 'need' in transition:
            assert transition == 'need_info'
        return []

    monkeypatch.setattr(
        startrack.StartrackAPIClient,
        'execute_transition',
        _dummy_execute_transition,
    )
    return _dummy_execute_transition


@pytest.fixture
def mock_st_create_link(monkeypatch, mock):
    @mock
    async def _dummy_create_link(
            ticket_id, related_ticket_id, relationship=None,
    ):
        return {}

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'create_link', _dummy_create_link,
    )
    return _dummy_create_link


@pytest.fixture
def mock_st_import_ticket(
        patch_aiohttp_session, response_mock, tracker_url: str,
):
    def wrapper(response=None, status=200):
        @patch_aiohttp_session(tracker_url + 'issues/_import', 'POST')
        def import_ticket(method, url, **kwargs):
            result = {} if response is None else response
            return response_mock(json=result, status=status)

        return import_ticket

    return wrapper


@pytest.fixture
def mock_st_get_ticket_by_unique_id(
        patch_aiohttp_session, response_mock, tracker_url: str,
):
    def wrapper(response=None, status=200):
        @patch_aiohttp_session(tracker_url + 'issues/_findByUnique', 'POST')
        def get_ticket_by_unique_id(method, url, **kwargs):
            result = {} if response is None else response
            return response_mock(json=result, status=status)

        return get_ticket_by_unique_id

    return wrapper


@pytest.fixture
def mock_st_import_comment(monkeypatch, mock):
    def _wrap(comment_data):
        @mock
        async def _dummy_import_comment(ticket_id, data):
            return comment_data

        monkeypatch.setattr(
            startrack.StartrackAPIClient,
            'import_comment',
            _dummy_import_comment,
        )
        return _dummy_import_comment

    return _wrap


@pytest.fixture
def mock_st_create_comment_old(monkeypatch, mock):
    def _wrap(comment_data):
        @mock
        async def _dummy_create_comment(ticket_id, text):
            return comment_data

        monkeypatch.setattr(
            startrack.StartrackAPIClient,
            'create_comment',
            _dummy_create_comment,
        )
        return _dummy_create_comment

    return _wrap


@pytest.fixture
def mock_st_import_file(monkeypatch, mock):
    @mock
    async def _dummy_import_file(*args, **kwargs):
        pass

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'import_file', _dummy_import_file,
    )
    return _dummy_import_file


def _ticket_data(ticket, status, tags=None, custom_fields=None):
    queue, _ = ticket.split('-')
    ticket = {
        'key': ticket,
        'queue': {'key': queue},
        'status': {'key': status},
        'createdAt': '2018-01-02T03:45:00.000Z',
        'createdBy': {'id': STARTRACK_CLIENT_ID},
        'updatedAt': '2018-01-02T03:45:00.000Z',
        'updatedBy': {'id': STARTRACK_CLIENT_ID},
        'summary': 'some summary',
        'description': 'some description',
        'emailFrom': 'some_client@email',
        'emailTo': ['test@support'],
        'emailCreatedBy': 'test@support',
    }
    if custom_fields is not None:
        ticket.update(custom_fields)
    if tags is not None:
        ticket['tags'] = tags
    return ticket


def construct_ticket_with_cc(*args, **kwargs):
    ticket = _ticket_data(*args, **kwargs)
    ticket['emailCc'] = ['toert@yandex-team', 'clinically@insane.me']
    return ticket


def construct_ticket_without_emails(*args, **kwargs):
    ticket = _ticket_data(*args, **kwargs)
    del ticket['emailFrom']
    del ticket['emailCreatedBy']
    return ticket


@pytest.fixture
def mock_uuid_fixture(patch):
    @patch('uuid.uuid4')
    def uuid4():
        return uuid.UUID('2104653b-dac3-43e3-9ac5-7869d0bd738d')


@pytest.fixture
def patch_auth(patch):
    def wrapper(**kwargs):
        @patch('taxi.clients.passport._superuser_auth')
        def superuser_auth(request):
            auth_default = {
                'login': 'superuser',
                'display_name': 'superuser',
                'default_avatar_id': '0/0-0',
                'uid': '0',
                'superuser': True,
                'groups': ['support'],
                'need_reset_cookie': False,
            }
            for field, default in auth_default.items():
                setattr(request, field, kwargs.get(field, default))

        return superuser_auth

    return wrapper


@pytest.fixture
def patch_tvm_auth(patch):
    def wrapper(src_service_name, good_ticket_body):
        @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
        async def tvm_auth(ticket_body, **kwargs):
            if ticket_body == str.encode(good_ticket_body):
                return src_service_name
            return None

        return tvm_auth

    return wrapper


@pytest.fixture
def patch_support_chat_get_history(patch_aiohttp_session, response_mock):
    def wrapper(response=None, status=200):
        support_chat_url = discovery.find_service('support_chat').url

        @patch_aiohttp_session(support_chat_url, 'POST')
        def get_history_request(method, url, **kwargs):
            result = (
                {'messages': [{'text': 'some message'}], 'total': 1}
                if response is None
                else response
            )
            return response_mock(json=result, status=status)

        return get_history_request

    return wrapper


@pytest.fixture
def patch_archive_yt_lookup_rows(patch_aiohttp_session, response_mock):
    def wrapper(headers=None, read=None, status=200):
        archive_api_url = settings.Settings.ARCHIVE_API_URL
        archive_api_url += '/v1/yt/lookup_rows'

        @patch_aiohttp_session(archive_api_url, 'POST')
        def archive_api_request(method, url, **kwargs):
            result_read = {'items': []} if read is None else read
            result_headers = (
                {'Content-Type': 'application/bson'}
                if headers is None
                else headers
            )

            return response_mock(
                read=bson.BSON.encode(result_read),
                status=status,
                headers=result_headers,
            )

        return archive_api_request

    return wrapper


@pytest.fixture
def support_metrics_mock(patch_aiohttp_session, response_mock):
    support_metrics_service = discovery.find_service('support_metrics')

    # pylint: disable=unused-variable
    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def patch_request(method, url, **kwargs):
        assert method == 'post'
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: d['created'],
        )
        return response_mock(json={})


@pytest.fixture
def patch_support_metrics_get_stat(patch_aiohttp_session, response_mock):
    support_metrics_service = discovery.find_service('support_metrics')
    route = '{}/v1/chatterbox/stats/list'.format(support_metrics_service.url)

    @patch_aiohttp_session(route, 'GET')
    def patch_request(method, url, **kwargs):
        zero = '2019-06-07T00:00:00.000000+03:00'
        one_hour = '2019-06-07T01:00:00.000000+03:00'
        two_hours = '2019-06-07T02:00:00.000000+03:00'
        nine_hours = '2019-06-07T09:00:00.000000+03:00'
        ten_hours = '2019-06-07T10:00:00.000000+03:00'
        one_day = '2019-06-08T00:00:00.000000+03:00'
        if kwargs['params']['instances'] == 'line':
            response = [
                {
                    'interval': '1hour',
                    'items': [
                        {
                            'key': 'telephony_line',
                            'stats': [
                                {
                                    'name': (
                                        'ivr_success_calls_by_line_calculator'
                                    ),
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_hour,
                                            'value': 12,
                                            'total': 40,
                                            'param_name': (
                                                'success_call_gt5_lt10'
                                            ),
                                        },
                                        {
                                            'interval_start': one_hour,
                                            'interval_finish': two_hours,
                                            'value': 23,
                                            'param_name': (
                                                'success_call_gt5_lt10'
                                            ),
                                        },
                                        {
                                            'interval_start': one_hour,
                                            'interval_finish': two_hours,
                                            'value': 5,
                                            'total': 40,
                                            'param_name': 'success_call_gt10',
                                        },
                                    ],
                                },
                                {
                                    'name': (
                                        'ivr_missed_calls_by_line_calculator'
                                    ),
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_hour,
                                            'value': 12,
                                            'total': 34,
                                            'param_name': (
                                                'missed_call_gt5_lt10'
                                            ),
                                        },
                                        {
                                            'interval_start': one_hour,
                                            'interval_finish': two_hours,
                                            'value': 23,
                                            'param_name': (
                                                'missed_call_gt5_lt10'
                                            ),
                                        },
                                        {
                                            'interval_start': one_hour,
                                            'interval_finish': two_hours,
                                            'value': 5,
                                            'total': 5,
                                            'param_name': 'missed_call_gt10',
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'key': 'first',
                            'stats': [
                                {
                                    'name': 'create_by_line_calculator',
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_hour,
                                            'value': 12,
                                        },
                                        {
                                            'interval_start': one_hour,
                                            'interval_finish': two_hours,
                                            'value': 23,
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'key': 'corp',
                            'stats': [
                                {
                                    'name': 'create_by_line_calculator',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 15,
                                        },
                                    ],
                                },
                                {
                                    'name': 'line_sla',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 1,
                                        },
                                    ],
                                },
                                {
                                    'name': 'aht_by_line',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 900,
                                        },
                                    ],
                                },
                                {
                                    'name': 'first_accept_by_line_calculator',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 10,
                                        },
                                    ],
                                },
                                {
                                    'name': 'online_time_by_line',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 300,
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'key': 'vip',
                            'stats': [
                                {
                                    'name': 'line_sla',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 0.44,
                                        },
                                    ],
                                },
                                {
                                    'name': 'first_accept_by_line_calculator',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 100,
                                        },
                                    ],
                                },
                                {
                                    'name': 'aht_by_line',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 900,
                                        },
                                    ],
                                },
                                {
                                    'name': 'online_time_by_line',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 600,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
                {
                    'interval': '1day',
                    'items': [
                        {
                            'key': 'first',
                            'stats': [
                                {
                                    'name': 'create_by_line_calculator',
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_day,
                                            'value': 12,
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            'key': 'corp',
                            'stats': [
                                {
                                    'name': 'line_sla',
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_day,
                                            'value': 0.55,
                                        },
                                    ],
                                },
                                {
                                    'name': 'max_first_answer_by_hour',
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_day,
                                            'value': 612999,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ]
        elif kwargs['params']['instances'] == 'project':
            response = [
                {
                    'interval': '1hour',
                    'items': [
                        {
                            'key': 'eats',
                            'stats': [
                                {
                                    'name': 'online_time_by_project',
                                    'values': [
                                        {
                                            'interval_start': nine_hours,
                                            'interval_finish': ten_hours,
                                            'value': 450,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ]
        else:
            response = [
                {
                    'interval': '1day',
                    'items': [
                        {
                            'key': 'user_2',
                            'stats': [
                                {
                                    'name': 'supporter_sla',
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_hour,
                                            'value': 0.99,
                                        },
                                    ],
                                },
                                {
                                    'name': 'aht_by_login',
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_hour,
                                            'value': 1200,
                                        },
                                    ],
                                },
                                {
                                    'name': 'online_time_by_login',
                                    'values': [
                                        {
                                            'interval_start': zero,
                                            'interval_finish': one_hour,
                                            'value': 500,
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ]
        return response_mock(json=response)


@pytest.fixture
def patch_support_metrics_stat_sip(load, patch_aiohttp_session, response_mock):
    support_metrics_service = discovery.find_service('support_metrics')
    route = '{}/v1/chatterbox/raw_stats/list'.format(
        support_metrics_service.url,
    )

    @patch_aiohttp_session(route, 'GET')
    def patch_request(method, url, **kwargs):
        params = kwargs['params']
        raw_stat = json.loads(load('support_metrics_raw_stat.json'))
        response = sum(
            [raw_stat.get(name, []) for name in params['names'].split('|')],
            [],
        )

        if 'line' in params:
            response = [i for i in response if i['line'] == params['line']]
        if 'logins' in params:
            response = [i for i in response if i['login'] in params['logins']]
        return response_mock(json=response)

    return patch_request


@pytest.fixture
def patch_support_info_refund(patch_aiohttp_session, response_mock):
    def wrapper(response=None, status=200):
        support_info_refund_url = (
            discovery.find_service('support_info').url
            + '/v1/payments/update_order_ride_sum',
        )

        @patch_aiohttp_session(support_info_refund_url, 'POST')
        def update_order_ride_sum(method, url, **kwargs):
            result = {} if response is None else response
            return response_mock(json=result, status=status)

        return update_order_ride_sum

    return wrapper


@pytest.fixture
def patch_support_info_compensation(patch_aiohttp_session, response_mock):
    def wrapper(response=None, status=200):
        support_info_compensation_url = (
            discovery.find_service('support_info').url
            + '/v1/payments/process_compensation',
        )

        @patch_aiohttp_session(support_info_compensation_url, 'POST')
        def process_compensation(method, url, **kwargs):
            result = {} if response is None else response
            return response_mock(json=result, status=status)

        return process_compensation

    return wrapper


@pytest.fixture
def auth_data() -> dict:
    return {
        'cookies': {
            'Session_id': 'some_user_sid',
            'yandexuid': 'some_user_uid',
            'sessionid2': 'some_user_sid2',
        },
        'token': 'some_token',
    }


@pytest.fixture
def patch_get_action_stat(patch_aiohttp_session, response_mock):
    def wrapper(result, status=200, login=None):
        support_metrics_service = discovery.find_service('support_metrics')
        route = '{}/v1/chatterbox/actions/count'.format(
            support_metrics_service.url,
        )

        @patch_aiohttp_session(route, 'GET')
        def _get_stat(method, url, **kwargs):
            if login:
                assert login == kwargs['params']['keys']
            return response_mock(json=result, status=status)

        return _get_stat

    return wrapper


@pytest.fixture
def mock_get_tags_v1(mockserver, load_json):
    def _wrap(tags_setting, tags_service='tags'):
        tags_v1_match = f'/{tags_service}/v1/match'
        tags_v1_match_profile = f'/{tags_service}/v1/drivers/match/profile'

        tags = load_json('tags.json')[tags_setting]

        @mockserver.json_handler(tags_v1_match_profile)
        @mockserver.json_handler(tags_v1_match)
        def _match(request):
            return {
                'entities': [
                    {
                        'id': entity['id'],
                        'type': entity['type'],
                        'tags': tags.get(entity['type'], {}).get(
                            entity['id'], [],
                        ),
                    }
                    for entity in request.json['entities']
                ],
            }

        return _match

    return _wrap


@pytest.fixture
def mock_get_tags_v2(mockserver, load_json):
    def _wrap(tags_setting, tags_service='tags'):
        tags_v2_match_single = f'/{tags_service}/v2/match_single'
        tags = load_json('tags.json')[tags_setting]

        @mockserver.json_handler(tags_v2_match_single)
        def _match(request):
            return {
                'tags': sum(
                    [
                        tags.get(entity['type'], {}).get(entity['value'], [])
                        for entity in request.json['match']
                    ],
                    [],
                ),
            }

        return _match

    return _wrap


@pytest.fixture
def mock_get_completed_tasks_count(monkeypatch, mock):
    def _wrap(count):
        @mock
        async def _get_completed_count_by_login(*args, **kwargs):
            return count

        monkeypatch.setattr(
            tasks_manager.TasksManager,
            '_get_completed_count_by_login',
            _get_completed_count_by_login,
        )
        return _get_completed_count_by_login

    return _wrap


@pytest.fixture
def mock_check_tasks_limits(monkeypatch, mock):
    def _wrap(max_count):
        @mock
        async def _check_tasks_per_shift_limits(*args, **kwargs):
            raise tasks_manager.MaxShiftTicketsExceedException(max_count)

        monkeypatch.setattr(
            tasks_manager.TasksManager,
            'check_tasks_per_shift_limits',
            _check_tasks_per_shift_limits,
        )
        return _check_tasks_per_shift_limits

    return _wrap


@pytest.fixture
def patch_raw_stat_lines_backlog(patch_aiohttp_session, response_mock):
    def wrapper(result, status=200, created_ts=None):
        support_metrics_service = discovery.find_service('support_metrics')

        @patch_aiohttp_session(support_metrics_service.url, 'GET')
        def _patch_request(method, url, **kwargs):
            assert method == 'get'
            assert '/v1/chatterbox/raw_stats/list' in url
            if created_ts:
                assert kwargs['params']['created_ts'] == created_ts
            return response_mock(json=result, status=status)

        return _patch_request

    return wrapper


@pytest.fixture
def mock_translate(patch_aiohttp_session, response_mock):
    def wrapper(lang):
        @patch_aiohttp_session('http://test-translate-url/', 'GET')
        def _dummy_translate_request(*args, **kwargs):
            return response_mock(json={'code': '200', 'lang': lang})

        return _dummy_translate_request

    return wrapper


@pytest.fixture
def mock_ml_suggest(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session('http://pyml.taxi.dev.yandex.net', 'POST')
    def _dummy_ml_suggest_request(*args, **kwargs):
        response = {
            'probs': {
                1: 0.025994541123509407,
                2: 3.5593038774095476e-06,
                3: 7.337190618272871e-05,
            },
        }
        return response_mock(json=response)

    return patch_aiohttp_session


@pytest.fixture
def mock_get_user_phone(mockserver, load_json):
    try:
        user_phones = load_json('user_api_user_phones.json')
    except FileNotFoundError:
        user_phones = []

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _get_user_phone(request):
        request_phone = request.json['phone']
        request_type = request.json['type']
        for user_phone in user_phones:
            if (
                    user_phone['phone'] == request_phone
                    and user_phone['type'] == request_type
            ):
                return user_phone
        return mockserver.make_response(status=404)

    return _get_user_phone


@pytest.fixture
def mock_external_salesforce_auth(monkeypatch, mock):
    @mock
    async def _dummy_auth(*args, **kwargs):
        return {'access_token': 'some_access_token'}

    monkeypatch.setattr(salesforce.SalesforceClient, 'auth_token', _dummy_auth)
    return _dummy_auth


@pytest.fixture
def mock_external_salesforce_create(monkeypatch, mock):
    def _wrap(response):
        @mock
        async def _dummy_create_case(*args, **kwargs):
            return response

        monkeypatch.setattr(
            salesforce.SalesforceClient, 'create_case', _dummy_create_case,
        )
        return _dummy_create_case

    return _wrap


@pytest.fixture
def mock_external_salesforce_update(monkeypatch, mock):
    @mock
    async def _dummy_update_case(*args, **kwargs):
        return {}

    monkeypatch.setattr(
        salesforce.SalesforceClient, 'update_case', _dummy_update_case,
    )
    return _dummy_update_case


@pytest.fixture
def mock_uapi_keys_auth(mockserver):
    @mockserver.json_handler('/uapi-keys/v2/authorization/')
    def mock_auth(request, *args, **kwargs):
        if (
                request.headers['X-API-Key'] == 'right_key'
                and request.json['client_id'] == 'right_client_id'
        ):
            return mockserver.make_response(
                json={'key_id': '12345'}, status=200,
            )
        return mockserver.make_response(json={}, status=403)


@pytest.fixture
def mock_personal(mockserver, load_json, patch):

    pd_data = load_json('personal_data.json')

    default_response = {'id': 'test_pd_id', 'value': 'test_value'}

    @patch('taxi.clients.personal.PersonalApiClient._get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {'auth': 'ticket'}

    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>\w+)/retrieve', regex=True,
    )
    def mock_retrieve_item(request, personal_type, *args, **kwargs):
        items = pd_data[personal_type]
        for item in items:
            if item['id'] == request.json['id']:
                return item
        return default_response

    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>\w+)/find', regex=True,
    )
    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>\w+)/store', regex=True,
    )
    def mock_store_item(request, personal_type, *args, **kwargs):
        items = pd_data[personal_type]
        for item in items:
            if item['value'] == request.json['value']:
                return item
        return default_response


@pytest.fixture
def mock_personal_phone_id(mockserver, load_json):
    phones = load_json('personal_phone_ids.json')

    @mockserver.json_handler('personal/v1/phones/store')
    def _store_phone(request):
        phone = request.json['value']
        return {'id': phones[phone], 'value': phone}

    return _store_phone


@pytest.fixture
def mock_randint(patch):
    @patch('random.randint')
    def _dummy_randint(min_value, max_value):
        return max_value

    return _dummy_randint


@pytest.fixture(autouse=True)
def mock_antifraud_refund(mockserver):
    @mockserver.json_handler(
        '/antifraud_refund-api/taxi/support', prefix=False,
    )
    def _rules(request):
        assert request.method == 'POST'
        for key in request.json:
            assert ALLOW_KEYS_ANTIFRAUD_REFAUND.count(key) == 1
        for message in request.json['dialogue']['dialog']['messages']:
            assert 'attachment_ids' in message
        return {
            'result': [
                {
                    'source': 'antifraud',
                    'subsource': 'rtxaron',
                    'entity': 'driver_uuid',
                    'key': '',
                    'name': 'taxi_free_trips',
                    'value': True,
                },
                {
                    'source': 'antifraud',
                    'subsource': 'rtxaron',
                    'entity': 'driver_uuid',
                    'key': '',
                    'name': 'taxi_something_else',
                    'value': False,
                },
            ],
        }

    return _rules


@pytest.fixture
def mock_get_chat_order_meta(patch):
    @patch(
        'taxi.clients.eats_support_misc'
        '.EatsSupportMiscClient.get_support_meta',
    )
    async def _dummy_get_chat_order_meta(
            order_nr: str, log_extra: typing.Optional[dict] = None,
    ):
        if order_nr == 'order_id':
            return {}
        if order_nr == '12345':
            return {
                'metadata': {
                    'is_blocked_user': False,
                    'eater_id': 'eater_id',
                    'eater_name': 'Иван Иванович',
                    'is_first_order': False,
                    'country_code': 'RU',
                    'is_promocode_used': False,
                    'order_total_amount': 777,
                    'order_delivered_at': '2020-01-20T18:02:42+0700',
                    'order_promised_at': '2020-01-20T18:00:00+0700',
                },
            }
        if order_nr == 'order_of_vip_eater':
            return {
                'metadata': {
                    'eater_id': 'eater_id',
                    'eater_name': 'Иван Иванович',
                    'eater_phone_id': 'vip_eater_phone_id',
                    'eater_decency': 'good',
                    'is_first_order': False,
                    'is_blocked_user': False,
                    'order_status': 'place_confirmed',
                    'order_type': 'native',
                    'delivery_type': 'our_delivery',
                    'is_fast_food': False,
                    'app_type': 'eats',
                    'country_code': 'RU',
                    'country_label': 'Russia',
                    'city_label': 'Moscow',
                    'order_total_amount': 777,
                    'order_delivered_at': '2020-01-20T18:02:42+0700',
                    'order_promised_at': '2020-01-20T18:00:00+0700',
                    'is_surge': False,
                    'is_promocode_used': False,
                    'persons_count': 2,
                    'payment_method': 'card',
                    'place_id': 'good_place',
                    'place_name': 'GoodPlace',
                    'courier_id': 'courier_1',
                    'is_sent_to_restapp': True,
                    'is_sent_to_integration': False,
                    'integration_type': 'native',
                    'brand_id': 'good_places',
                },
            }
        raise eats_support_misc.NotFoundError('Order not found')

    return _dummy_get_chat_order_meta


@pytest.fixture
def mock_checkouter_order(mock_market_checkouter, load_json):
    try:
        orders = load_json('checkouter_orders.json')
    except FileNotFoundError:
        orders = []

    @mock_market_checkouter(r'/orders/(?P<order_id>\d+)', regex=True)
    async def handler(request, order_id):
        for order in orders:
            if order['id'] == int(order_id):
                return web.json_response(order)

        return web.json_response({}, status=404)

    return handler


@pytest.fixture
def mock_checkouter_return(mock_market_checkouter, load_json):
    try:
        returns = load_json('checkouter_returns.json')
    except FileNotFoundError:
        returns = []

    @mock_market_checkouter(r'/returns/(?P<order_return_id>\d+)', regex=True)
    async def handler(request, order_return_id):
        for ret in returns:
            if ret['id'] == int(order_return_id):
                return web.json_response(ret)
        return web.json_response({}, status=404)

    return handler


@pytest.fixture
def mock_checkouter_return_appl(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session('https://example.com/return-application.pdf', 'GET')
    def get_application_pdf(method, url, **kwargs):
        return response_mock(
            status=200,
            read=b'%PDF-1.5\n%\xe2\xe3\xcf\xd3\n3 0 obj\n<</Filter'
            b'/FlateDecode/Length 975>>stream\nx\x9c\xadW]o\xdb6\x14',
        )


@pytest.fixture
def mock_market_crm_get_order_meta(patch):
    @patch('taxi.clients.market_crm' '.MarketCrmApiClient.get_order_meta')
    async def _dummy_get_order_meta(order_id: str):
        if order_id == '1234567':
            return {
                'buyerAddressCity': 'Москва',
                'creationDate': '2020-01-10T10:10:10+03:00',
                'deliveryFromDate': '2020-01-15',
                'deliveryToDate': '2020-01-20',
                'deliveryService': {
                    'code': '50',
                    'title': 'TestPost',
                    'url': 'http://www.test-post.ru',
                },
                'deliveryType': {
                    'code': 'DELIVERY',
                    'title': 'Доставка курьером',
                },
                'status': {'code': 'DELIVERY', 'title': 'передан в доставку'},
                'orderdeliverytype': 'PICKUP',
                'originalDeliveryFromDate': '2020-01-14',
                'originalDeliveryToDate': '2020-01-19',
                'order_status': 'DELIVERY',
                'title': 1234567,
            }
        raise errors.NotFoundError(
            'Order not found', 404, 'text/text', bytearray(),
        )

    return _dummy_get_order_meta


@pytest.fixture
def mock_dealapp_send_chat(monkeypatch, mock):
    def _wrap(response):
        @mock
        async def _dummy_send_chat(*args, **kwargs):
            return response

        monkeypatch.setattr(
            dealapp.DealAppClient, 'send_chat', _dummy_send_chat,
        )
        return _dummy_send_chat

    return _wrap


@pytest.fixture
def mock_autoreply(patch_aiohttp_session, load_json, response_mock):
    responses = load_json('autoreply_responses.json')
    plotva_ml_url = discovery.find_service('plotva-ml').url
    supportai_api_url = discovery.find_service('supportai-api').url

    def wrapper(response):
        @patch_aiohttp_session(plotva_ml_url, 'POST')
        @patch_aiohttp_session(supportai_api_url, 'POST')
        def handler(method, url, **kwargs):
            response_data = responses.get(response, {})
            return response_mock(json=response_data, status=200)

        return handler

    return wrapper


@pytest.fixture
def mock_collections(mockserver, load_json):
    @mockserver.json_handler('/chatterbox-admin/v1/internal/collections')
    def _get_collections(request):
        if request.query.getall('categories') == [
                'taxi',
                'category,with,commas',
        ]:
            return load_json('collections_1.json')
        if request.query.getall('categories') == ['single']:
            return load_json('collections_2.json')
        return {'collections': []}

    return _get_collections


@pytest.fixture()
def mock_blocklist(mockserver):
    @mockserver.json_handler('/internal/blocklist/v1/add')
    def _dummy_block_driver(request):
        return {'block_id': 'test_block_id'}

    return _dummy_block_driver


@pytest.fixture()
def mock_block_personal(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def _dummy_get_licenses_pd_id(request):
        return {'value': 'value', 'id': 'not_ticket_license_pd_id'}

    return _dummy_get_licenses_pd_id


@pytest.fixture
def mock_magic(monkeypatch, mock):
    def _wrap(content_type):
        @mock
        def _dummy_magic(*args, **kwargs):
            return content_type

        monkeypatch.setattr(magic, 'from_buffer', _dummy_magic)
        return _dummy_magic

    return _wrap


@pytest.fixture(autouse=True)
def mock_support_tags(mockserver):
    @mockserver.json_handler('/support-tags/v1/tags')
    def fetch_tags(request):
        return {'tags': ['macro_used_1', 'macro_used_2']}


@pytest.fixture
def mock_support_tags_save_tags(mockserver):
    def _wrap(expected_request):
        @mockserver.json_handler('/support-tags/v1/save_tags')
        def _match(request):
            assert 'entities' in request.json
            assert request.json['entities'] == expected_request
            return {}

        return _match

    return _wrap


@pytest.fixture()
def mock_callcenter_qa(mockserver):
    @mockserver.json_handler('/v1/rating/get')
    def _dummy_callcenter_qa(request):
        map_guid_ans = {
            '1': {'is_finished': True, 'rating': '5'},
            '2': {'is_finished': False},
            '3': {'is_finished': True},
            '4': {'is_finished': True, 'rating': '6'},
            '5': {'is_finished': True},
            '6': {'is_finished': True, 'rating': '10'},
        }
        return {guid: map_guid_ans[guid] for guid in request.json['guids']}

    return _dummy_callcenter_qa


@pytest.fixture
def mock_yandex_calendar(mockserver):
    @mockserver.json_handler('/yandex-calendar/internal/get-holidays')
    def _dummy_internal_get_holidays(request):
        return {
            'holidays': [
                {
                    'date': '2015-01-01',
                    'type': 'holiday',
                    'name': 'Новогодние каникулы',
                },
                {
                    'date': '2015-01-08',
                    'type': 'weekend',
                    'transferDate': '2015-01-31',
                    'name': 'Перенос выходного с 31 января',
                },
                {
                    'date': '2015-01-13',
                    'type': 'weekday',
                    'isTransfer': False,
                    'name': 'День российской печати',
                },
            ],
        }


@pytest.fixture
def mock_random_str_uuid(monkeypatch, mock):
    def _wrap():
        @mock
        def _random_str_uuid():
            return 'test_uid'

        monkeypatch.setattr(
            tasks_manager.TasksManager, 'random_str_uuid', _random_str_uuid,
        )
        return _random_str_uuid

    return _wrap


@pytest.fixture
def mock_passport_for_lb(patch_aiohttp_session, response_mock):
    def _wrap(users):
        @patch_aiohttp_session(
            'http://blackbox.yandex-team.ru/blackbox/', 'GET',
        )
        def _dummy_passport(method, url, *args, **kwargs):
            assert 'yandex-team.ru' in url
            return response_mock(text=json.dumps(users))

        return _dummy_passport

    return _wrap


@pytest.fixture
def mock_logbroker_producer(monkeypatch, mock):
    class _DummyApi:
        def __init__(self, expected_message):
            self.expected_message = expected_message

        def start(self):
            future = concurrent.futures.Future()
            future.set_result('start result')
            return future

        def create_retrying_producer(self, *args, **kwargs):
            return _DummyProducer(self.expected_message)

    class _DummyProducer:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            return future

        def __init__(self, expected_message, first_write_fail=False):
            self._to_send = []
            self._first_write_fail = first_write_fail
            self.expected_message = expected_message

        def stop(self):
            pass

        def write(self, seq_no, message):
            if self._first_write_fail:
                self._first_write_fail = False
                raise concurrent.futures.TimeoutError
            future = concurrent.futures.Future()
            self._to_send.append((future, message))
            _message = json.loads(message)
            _message.pop('id')
            assert _message == self.expected_message
            for fut, msg in self._to_send:
                fut.set_result(_DummyFutureResult)
            self._to_send = []

            return future

    class _DummyFutureResult:
        @staticmethod
        def HasField(field):
            return True

        class init:
            max_seq_no = 0

    def _wrap(expected_message):
        @mock
        async def _create_api(*args, **kwargs):
            return _DummyApi(expected_message)

        monkeypatch.setattr(
            logbroker.LogbrokerAsyncWrapper, '_create_api', _create_api,
        )

        return _create_api

    return _wrap


@pytest.fixture
def api_keys(simple_secdist):
    return {
        profile: api_key
        for api_key, profile in simple_secdist['settings_override'][
            'CHATTERBOX_API_KEYS'
        ].items()
    }
