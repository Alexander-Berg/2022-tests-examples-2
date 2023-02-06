# pylint: disable=redefined-outer-name
# pylint: disable=wildcard-import
# pylint: disable=too-many-lines
import datetime
import http

import pytest

from taxi.clients import messenger_chat_mirror as messenger
from taxi.clients import startrack
from taxi.clients import support_chat
from taxi.util import dates

from chatterbox.api import tasks
from chatterbox.generated.service.config import plugin as chatterbox_config
from chatterbox.internal import tasks_manager
from chatterbox.internal.tasks_manager import _private
from test_chatterbox import plugins as conftest


class StartrackClientHolderMock:
    def __init__(self, startrack_client):
        self.startrack_client = startrack_client

    def get(self, profile: str):
        return self.startrack_client

    def get_default(self):
        return self.startrack_client


@pytest.mark.parametrize(
    (
        'data',
        'expected_query',
        'check_mongo_query',
        'expected_page',
        'expected_page_size',
        'expected_ids',
        'expected_chat_ids',
    ),
    [
        (
            {},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty()',
            None,
            1,
            96,
            [
                'user1_task_id_100500',
                'user1_task_id',
                'user4_task_id',
                'user3_task_id',
                'user1_another_task_id',
                'user2_task_id',
            ],
            [
                'chat_id100500',
                'chat_id1',
                'chat_id5',
                'chat_id4',
                'chat_id2',
                'chat_id3',
            ],
        ),
        (
            {'limit': 10000},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty()',
            None,
            1,
            996,
            [
                'user1_task_id_100500',
                'user1_task_id',
                'user4_task_id',
                'user3_task_id',
                'user1_another_task_id',
                'user2_task_id',
            ],
            [
                'chat_id100500',
                'chat_id1',
                'chat_id5',
                'chat_id4',
                'chat_id2',
                'chat_id3',
            ],
        ),
        (
            {'created': dates.timestring(datetime.datetime(2018, 5, 7))},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: "2018-05-07".."2018-05-07"',
            None,
            1,
            99,
            ['user1_task_id', 'user1_another_task_id'],
            ['chat_id1', 'chat_id2'],
        ),
        (
            {'tags': ['tag1']},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'tags: "tag1"',
            None,
            1,
            99,
            ['user1_task_id', 'user2_task_id'],
            ['chat_id1', 'chat_id3'],
        ),
        (
            {'tags': ['tag2'], 'lines': ['second', 'vip']},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"line": "second" AND '
            'tags: "tag2"',
            None,
            1,
            100,
            ['user2_task_id'],
            ['chat_id3'],
        ),
        (
            {'tags': ['tag1', 'tag2']},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'tags: "tag1" AND '
            'tags: "tag2"',
            None,
            1,
            100,
            ['user2_task_id'],
            ['chat_id3'],
        ),
        (
            {'tags': ['tag1'], 'offset': 0, 'limit': 2},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'tags: "tag1"',
            None,
            1,
            1,
            ['user1_task_id', 'user2_task_id'],
            ['chat_id1', 'chat_id3'],
        ),
        (
            {'limit': 1, 'offset': 1},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty()',
            None,
            1,
            1,
            ['user1_task_id'],
            ['chat_id1'],
        ),
        (
            {'user_phone': '+7999'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"user phone": "+7999"',
            None,
            1,
            99,
            ['user2_task_id'],
            ['chat_id3'],
        ),
        (
            {
                'user_phone': '+79999999999',
                'driver_license': 'some_driver_license',
                'user_email': 'user@yandex.ru',
            },
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"user phone": "+79999999999" AND '
            '"user e-mail": "user@yandex.ru" AND '
            '"driver license": "some_driver_license"',
            {
                'meta_info.driver_license_pd_id': 'driver_license_pd_id_1',
                'meta_info.user_email_pd_id': 'email_pd_id_2',
                'meta_info.user_phone_pd_id': 'phone_pd_id_1',
                'status': {'$ne': 'dummy_status'},
            },
            1,
            99,
            ['user3_task_id'],
            ['chat_id4'],
        ),
        (
            {
                'user_phone': '+79999999999',
                'driver_license': 'some_driver_license',
            },
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"user phone": "+79999999999" AND '
            '"driver license": "some_driver_license"',
            {
                'meta_info.driver_license_pd_id': 'driver_license_pd_id_1',
                'meta_info.user_phone_pd_id': 'phone_pd_id_1',
                'status': {'$ne': 'dummy_status'},
            },
            1,
            99,
            ['user3_task_id'],
            ['chat_id4'],
        ),
        (
            {'status': 'archived', 'login': 'admin2'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"support": "admin2"',
            None,
            1,
            100,
            ['user2_task_id'],
            ['chat_id3'],
        ),
        (
            {'text': 'some text', 'tags': ['tag2']},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'tags: "tag2" AND '
            '(Description: "some text" OR Comment: "some text")',
            None,
            1,
            99,
            ['user4_task_id', 'user1_another_task_id', 'user2_task_id'],
            ['chat_id5', 'chat_id2', 'chat_id3'],
        ),
        (
            {
                'text': 'some text with date',
                'tags': ['tag2'],
                'created': dates.timestring(datetime.datetime(2018, 5, 7)),
            },
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: "2018-05-07".."2018-05-07" AND '
            'tags: "tag2" AND (Description: "some text with date" OR '
            'Comment: "some text with date")',
            None,
            1,
            100,
            ['user1_another_task_id'],
            ['chat_id2'],
        ),
        (
            {'city': 'Москва'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"city": "москва"',
            None,
            1,
            99,
            ['user1_task_id'],
            ['chat_id1'],
        ),
        (
            {'city': 'qwe"or"queue":"BADQUEUE'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"city": "qwe or queue : badqueue"',
            None,
            1,
            100,
            [],
            [],
        ),
        (
            {'city': 'qwe\\"or(queue:badqueue)or"city":qwe\\'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"city": "qwe or queue:badqueue or city :qwe "',
            None,
            1,
            100,
            [],
            [],
        ),
        (
            {'tags': ['tag1', 'tag2'], 'tags_search_method': 'and'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'tags: "tag1" AND '
            'tags: "tag2"',
            None,
            1,
            100,
            ['user2_task_id'],
            ['chat_id3'],
        ),
        (
            {'tags': ['tag1', 'tag2'], 'tags_search_method': 'or'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'tags: "tag1","tag2"',
            None,
            1,
            98,
            [
                'user1_task_id',
                'user4_task_id',
                'user1_another_task_id',
                'user2_task_id',
            ],
            ['chat_id1', 'chat_id5', 'chat_id2', 'chat_id3'],
        ),
        (
            {'tags': ['tag1'], 'tags_search_method': 'or'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'tags: "tag1"',
            None,
            1,
            99,
            ['user1_task_id', 'user2_task_id'],
            ['chat_id1', 'chat_id3'],
        ),
        (
            {'tags_search_method': 'or'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty()',
            None,
            1,
            96,
            [
                'user1_task_id_100500',
                'user1_task_id',
                'user4_task_id',
                'user3_task_id',
                'user1_another_task_id',
                'user2_task_id',
            ],
            [
                'chat_id100500',
                'chat_id1',
                'chat_id5',
                'chat_id4',
                'chat_id2',
                'chat_id3',
            ],
        ),
        (
            {'logins': ['admin2']},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"support": "admin2"',
            None,
            1,
            98,
            ['user4_task_id', 'user3_task_id', 'user2_task_id'],
            ['chat_id5', 'chat_id4', 'chat_id3'],
        ),
        (
            {'logins': ['admin1', 'admin2']},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            '"support": "admin1", "admin2"',
            None,
            1,
            96,
            [
                'user1_task_id_100500',
                'user1_task_id',
                'user4_task_id',
                'user3_task_id',
                'user1_another_task_id',
                'user2_task_id',
            ],
            [
                'chat_id100500',
                'chat_id1',
                'chat_id5',
                'chat_id4',
                'chat_id2',
                'chat_id3',
            ],
        ),
        (
            {'status': 'new'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty()',
            None,
            1,
            98,
            ['user4_task_id', 'user3_task_id'],
            ['chat_id5', 'chat_id4'],
        ),
        (
            {'statuses': ['new']},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty()',
            None,
            1,
            98,
            ['user4_task_id', 'user3_task_id'],
            ['chat_id5', 'chat_id4'],
        ),
        (
            {'statuses': ['new', 'in_progress']},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty()',
            None,
            1,
            96,
            [
                'user1_task_id_100500',
                'user1_task_id',
                'user4_task_id',
                'user3_task_id',
            ],
            ['chat_id100500', 'chat_id1', 'chat_id5', 'chat_id4'],
        ),
    ],
)
@pytest.mark.translations(
    chatterbox={'text_search.truncated': {'en': 'text search truncated'}},
)
@pytest.mark.config(
    CHATTERBOX_STARTRACK_PROFILES=['support-taxi'],
    TVM_ENABLED=True,
    USER_CHAT_MESSAGES_DEFAULT_SEARCH_LIMIT=3,
    CHATTERBOX_SEARCH_QUEUES_BY_PROFILE={
        'support-taxi': ['TESTQUEUE', 'CHATTERBOX'],
    },
    STARTRACK_CUSTOM_FIELDS_MAP_FOR_SEARCH={
        'support-taxi': {
            'chatterbox_id': 'Chatterbox ID',
            'user_phone': 'user phone',
            'user_email': 'user e-mail',
            'login': 'support',
            'logins': 'support',
            'lines': 'line',
            'driver_license': 'driver license',
            'order_id': 'order id',
            'car_number': 'car number',
            'driver_uuid': 'driver uuid',
            'park_name': 'park name',
            'clid': 'clid',
            'park_db_id': 'park db id',
            'city': 'city',
            'driver_name': 'driver name',
            'taximeter_version': 'taximeter version',
            'device_model': 'device model',
        },
    },
    CHATTERBOX_LINES={
        'first': {
            'name': 'Первая линия',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'autoreply': True,
        },
        'second': {
            'name': 'Вторая линия',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'autoreply': True,
        },
    },
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'search_enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
        },
    },
    CHATTERBOX_META_INFO_FIELDS_FOR_EXACT_MATCH_SEARCH=[
        'driver_license',
        'driver_license_pd_id',
        'order_id',
        'city',
        'user_email',
        'user_email_pd_id',
        'user_phone',
        'user_phone_pd_id',
    ],
    CHATTERBOX_META_INFO_HIGH_SELECTIVE_FIELDS=[
        'driver_license',
        'driver_license_pd_id',
        'order_id',
        'user_email',
        'user_email_pd_id',
        'user_phone',
        'user_phone_pd_id',
    ],
    CHATTERBOX_USE_MESSENGER_TEXT_SEARCH=True,
)
async def test_search_ids(
        cbox,
        patch_auth,
        data,
        expected_query,
        check_mongo_query,
        expected_page,
        expected_page_size,
        expected_ids,
        expected_chat_ids,
        monkeypatch,
        mock,
        mock_personal,
):
    patch_auth(is_superuser=True)

    class DummyStartrackClient:
        def __init__(self):
            pass

        async def search(self, query, page, page_size, **kwargs):
            assert query == expected_query
            assert page == expected_page
            assert page_size == expected_page_size
            if 'created' in data:
                data['created'] = dates.parse_timestring(data['created'])
            personal_data = (
                await cbox.app.personal_manager.find_personal_metadata(
                    metadata=data,
                )
            )
            mongo_query = _private.get_query_for_search(
                cbox.app.config, **personal_data,
            )
            if mongo_query['status'].get('$nin'):
                del mongo_query['status']['$nin']
            if check_mongo_query:
                assert mongo_query == check_mongo_query
            mongo_query['status']['$in'] = [
                tasks_manager.STATUS_ARCHIVED,
                tasks_manager.STATUS_EXPORTED,
            ]
            result = []
            cursor = cbox.app.db.support_chatterbox.find(mongo_query)
            tasks = (
                await cursor.sort('created', -1)
                .skip((page - 1) * page_size)
                .to_list(page_size)
            )
            for task in tasks:
                result.append({'chatterboxId': task['_id']})
            return result

    async def _dummy_get_task(self, task_id, log_extra=None):
        return await cbox.app.db.support_chatterbox.find_one({'_id': task_id})

    @mock
    async def _dummy_search_by_text(*args, **kwargs):
        return {
            'chats': [
                {'id': 'chat_id1'},
                {'id': 'chat_id3'},
                {'id': 'unknown_chat_id'},
            ],
        }

    @mock
    async def _dummy_search_by_text_messenger(*args, **kwargs):
        return {'chats': [{'id': 'chat_id5'}, {'id': 'unknown_chat_id_msngr'}]}

    monkeypatch.setattr(
        tasks_manager.TasksManager, 'get_from_archive', _dummy_get_task,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient,
        'search_by_text',
        _dummy_search_by_text,
    )

    monkeypatch.setattr(
        messenger.MessengerChatMirrorApiClient,
        'search_by_text',
        _dummy_search_by_text_messenger,
    )

    cbox.app.startrack_manager.startrack_client_holder = (
        StartrackClientHolderMock(DummyStartrackClient())
    )

    await cbox.post(
        '/v1/tasks/search/', data=data, headers={'Accept-Language': 'en'},
    )
    assert cbox.status == http.HTTPStatus.OK
    tasks = cbox.body_data['tasks']
    assert [task['id'] for task in tasks] == expected_ids
    assert [task['external_id'] for task in tasks] == expected_chat_ids
    if 'text' in data:
        assert cbox.body_data['message'] == 'text search truncated'
        assert cbox.body_data['status'] == 'truncated'

        calls = _dummy_search_by_text.calls
        if data.get('created'):
            newer = calls[0]['kwargs']['date_newer_than']
            older = calls[0]['kwargs']['date_older_than']
            assert newer == '2018-05-07T03:00:00+0300'
            assert older == '2018-05-08T03:00:00+0300'


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    ['data', 'expected_status', 'expected_result'],
    [
        (
            {'status': 'in_progress', 'login': 'admin1'},
            200,
            {
                'tasks': [
                    {
                        'id': 'user1_task_id_100500',
                        'created': '2018-06-07T12:34:55+0000',
                        'updated': '2018-06-07T12:34:56+0000',
                        'login': 'admin1',
                        'line': 'first',
                        'chat_type': 'facebook_support',
                        'status': 'in_progress',
                        'tags': ['tag200500'],
                        'theme_name': 'theme',
                        'external_id': 'chat_id100500',
                        'requester': 'Petkya',
                        'actions': [],
                    },
                    {
                        'id': 'user1_task_id',
                        'created': '2018-05-07T12:34:56+0000',
                        'updated': '2018-05-07T12:34:56+0000',
                        'login': 'admin1',
                        'line': 'first',
                        'chat_type': 'client',
                        'status': 'in_progress',
                        'tags': ['tag1'],
                        'external_id': 'chat_id1',
                        'requester': '+79991',
                        'order_id': 'some_order_id',
                        'ticket_subject': 'some_subject',
                        'actions': [],
                    },
                ],
                'status': 'ok',
            },
        ),
        (
            {
                'status': 'in_progress',
                'login': 'admin1',
                'created': '2018-05-07',
            },
            200,
            {
                'tasks': [
                    {
                        'id': 'user1_task_id',
                        'external_id': 'chat_id1',
                        'line': 'first',
                        'status': 'in_progress',
                        'created': '2018-05-07T12:34:56+0000',
                        'updated': '2018-05-07T12:34:56+0000',
                        'tags': ['tag1'],
                        'chat_type': 'client',
                        'requester': '+79991',
                        'ticket_subject': 'some_subject',
                        'order_id': 'some_order_id',
                        'login': 'admin1',
                        'actions': [],
                    },
                ],
                'status': 'ok',
            },
        ),
        (
            {
                'status': 'in_progress',
                'login': 'admin1',
                'created_from': '2018-02-07',
            },
            200,
            {
                'tasks': [
                    {
                        'id': 'user1_task_id_100500',
                        'external_id': 'chat_id100500',
                        'line': 'first',
                        'status': 'in_progress',
                        'created': '2018-06-07T12:34:55+0000',
                        'updated': '2018-06-07T12:34:56+0000',
                        'tags': ['tag200500'],
                        'chat_type': 'facebook_support',
                        'requester': 'Petkya',
                        'theme_name': 'theme',
                        'login': 'admin1',
                        'actions': [],
                    },
                    {
                        'id': 'user1_task_id',
                        'external_id': 'chat_id1',
                        'line': 'first',
                        'status': 'in_progress',
                        'created': '2018-05-07T12:34:56+0000',
                        'updated': '2018-05-07T12:34:56+0000',
                        'tags': ['tag1'],
                        'chat_type': 'client',
                        'requester': '+79991',
                        'ticket_subject': 'some_subject',
                        'order_id': 'some_order_id',
                        'login': 'admin1',
                        'actions': [],
                    },
                ],
                'status': 'ok',
            },
        ),
        (
            {'status': 'in_progress', 'login': 'admin1', 'some': 'field'},
            400,
            {
                'message': 'fields {\'some\'} are unavailable for search',
                'status': 'error',
            },
        ),
        (
            {'created': '2018-05-07', 'created_from': '2018-05-07'},
            400,
            {
                'message': (
                    'You must not set fields [\'created\', \'created_from\'] '
                    'together'
                ),
                'status': 'request_error',
            },
        ),
        (
            {'status': 'status_1', 'statuses': ['status_1', 'status_2']},
            400,
            {
                'message': (
                    'You must not set fields [\'status\', \'statuses\'] '
                    'together'
                ),
                'status': 'request_error',
            },
        ),
        (
            {'login': 'login_1', 'logins': ['login_1', 'login_2']},
            400,
            {
                'message': (
                    'You must not set fields [\'login\', \'logins\'] '
                    'together'
                ),
                'status': 'request_error',
            },
        ),
    ],
)
async def test_search_body(
        cbox: conftest.CboxWrap,
        patch_auth,
        data: dict,
        expected_status: int,
        expected_result: dict,
        mock_personal,
):
    patch_auth(superuser=True, groups=[])

    await cbox.post('/v1/tasks/search/', data=data)

    assert cbox.status == expected_status
    assert cbox.body_data == expected_result


@pytest.mark.parametrize(
    ['data', 'expected_status', 'expected_result'],
    [
        (
            {'status': 'in_progress', 'login': 'admin1'},
            200,
            {
                'tasks': [
                    {
                        'id': 'user1_task_id',
                        'created': '2018-05-07T12:34:56+0000',
                        'updated': '2018-05-07T12:34:56+0000',
                        'login': 'admin1',
                        'line': 'first',
                        'chat_type': 'client',
                        'status': 'in_progress',
                        'tags': ['tag1'],
                        'external_id': 'chat_id1',
                        'requester': '+79991',
                        'order_id': 'some_order_id',
                        'ticket_subject': 'some_subject',
                        'actions': [],
                    },
                    {
                        'id': 'user1_task_id_100500',
                        'created': '2018-06-07T12:34:55+0000',
                        'updated': '2018-06-07T12:34:56+0000',
                        'login': 'admin1',
                        'line': 'first',
                        'chat_type': 'facebook_support',
                        'status': 'in_progress',
                        'tags': ['tag200500'],
                        'theme_name': 'theme',
                        'external_id': 'chat_id100500',
                        'requester': 'Petkya',
                        'actions': [],
                    },
                ],
                'status': 'ok',
            },
        ),
    ],
)
async def test_tvm_search(
        cbox: conftest.CboxWrap,
        patch_auth,
        data: dict,
        expected_status: int,
        expected_result: dict,
        mock_personal,
):

    await cbox.post('/v1/tasks/search/', data=data)

    assert cbox.status == expected_status
    cbox.body_data['tasks'] = sorted(
        cbox.body_data['tasks'], key=lambda item: item['created'],
    )
    assert cbox.body_data == expected_result


@pytest.mark.translations(chatterbox={'tanker.close': {'ru': 'Закрыть'}})
@pytest.mark.config(
    CHATTERBOX_SEARCH_ACTIONS=[
        {
            'action_id': 'close',
            'query_params': {},
            'permissions': [{'permissions': ['close_permissions']}],
            'title_tanker': 'tanker.close',
        },
    ],
)
async def test_search_actions_for_tvm(cbox: conftest.CboxWrap):
    await cbox.post('/v1/tasks/search/', data={})

    assert cbox.status == 200
    assert cbox.body_data['tasks'][0]['actions'] == []


@pytest.mark.translations(
    chatterbox={
        'tanker.export': {'ru': 'Ручное'},
        'tanker.close': {'ru': 'Закрыть'},
    },
)
@pytest.mark.config(
    TVM_ENABLED=True,
    CHATTERBOX_SEARCH_ACTIONS=[
        {
            'action_id': 'export',
            'query_params': {},
            'title_tanker': 'tanker.export',
        },
        {
            'action_id': 'close',
            'query_params': {},
            'permissions': [{'permissions': ['close_permissions']}],
            'title_tanker': 'tanker.close',
            'view': {
                'type': 'dropdown',
                'group_tanker': 'tanker.close',
                'default': True,
            },
        },
    ],
    CHATTERBOX_LINES_PERMISSIONS={
        'first': {'search': [{'permissions': ['search_permission']}]},
    },
)
@pytest.mark.parametrize('is_superuser', (True, False))
async def test_search_actions_for_passport(
        cbox: conftest.CboxWrap, patch_auth, is_superuser: bool,
):
    patch_auth(
        superuser=is_superuser,
        groups=['readonly', 'client_first_search', 'search_unlimited_time'],
    )

    await cbox.post('/v1/tasks/search/', data={})

    assert cbox.status == 200
    actions = cbox.body_data['tasks'][0]['actions']
    if is_superuser:
        assert actions == [
            {
                'action_id': 'export',
                'query_params': {},
                'title': 'Ручное',
                'view': {'type': 'button'},
            },
            {
                'action_id': 'close',
                'query_params': {},
                'title': 'Закрыть',
                'view': {
                    'type': 'dropdown',
                    'default': True,
                    'group': 'Закрыть',
                },
            },
        ]
    else:
        assert actions == [
            {
                'action_id': 'export',
                'query_params': {},
                'title': 'Ручное',
                'view': {'type': 'button'},
            },
        ]


@pytest.mark.translations(
    chatterbox={
        'tanker.export': {'ru': 'Ручное'},
        'tanker.close': {'ru': 'Закрыть'},
    },
)
@pytest.mark.config(
    TVM_ENABLED=True,
    CHATTERBOX_SEARCH_ACTIONS=[
        {
            'action_id': 'export',
            'query_params': {},
            'title_tanker': 'tanker.export',
            'view': {'type': 'dropdown'},
        },
        {
            'action_id': 'close',
            'query_params': {},
            'title_tanker': 'tanker.close',
            'conditions': {'chat_type': 'facebook_support'},
            'view': {'type': 'dropdown'},
        },
    ],
)
async def test_search_actions_conditions(cbox: conftest.CboxWrap):
    await cbox.post('/v1/tasks/search/', data={})

    assert cbox.status == 200

    actions_by_task_id = {
        task['id']: task['actions'] for task in cbox.body_data['tasks']
    }
    assert actions_by_task_id == {
        'user1_task_id_100500': [
            {
                'action_id': 'export',
                'query_params': {},
                'title': 'Ручное',
                'view': {'type': 'dropdown'},
            },
            {
                'action_id': 'close',
                'query_params': {},
                'title': 'Закрыть',
                'view': {'type': 'dropdown'},
            },
        ],
        'user1_task_id': [
            {
                'action_id': 'export',
                'query_params': {},
                'title': 'Ручное',
                'view': {'type': 'dropdown'},
            },
        ],
        'user3_task_id': [
            {
                'action_id': 'export',
                'query_params': {},
                'title': 'Ручное',
                'view': {'type': 'dropdown'},
            },
        ],
        'user4_task_id': [
            {
                'action_id': 'export',
                'query_params': {},
                'title': 'Ручное',
                'view': {'type': 'dropdown'},
            },
        ],
    }


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
        },
    },
)
@pytest.mark.parametrize(
    ('meta_info', 'chat_type', 'requester_info'),
    [
        ({'user_phone': '+100500'}, 'client', '+100500'),
        ({'user_phone': '+100500'}, 'sms', '+100500'),
        ({'driver_license': 'license'}, 'driver', 'license'),
        ({'user_name': 'Nikitka'}, 'facebook_support', 'Nikitka'),
        ({'user_email': 'niki@tka.ru'}, 'startrack', 'niki@tka.ru'),
        # leviy_chat_type is not defined in config
        ({'user_phone': '+100500'}, 'leviy_chat_type', None),
        # if doesn't have chat_type => then get chat_type as client by default
        ({'user_phone': '+100500'}, None, '+100500'),
        (
            {'user_phone': '+100500', 'ticket_subject': 'subject'},
            'client',
            '+100500',
        ),
        (
            {'user_phone': '+100500', 'some_field': 'field name'},
            'sms',
            '+100500',
        ),
        ({'user_phone_pd_id': 'personal_phone_id'}, 'sms', '+79001231234'),
        (
            {'driver_license_pd_id': 'driver_license_pd_id_1'},
            'driver',
            'some_driver_license',
        ),
        (
            {'user_email_pd_id': 'email_pd_id_1'},
            'startrack',
            'some_client@email',
        ),
    ],
)
async def test_create_tasks_info_response(
        meta_info, chat_type, requester_info, cbox, mock_personal,
):
    base_task_body = {
        '_id': 'user1_task_id',
        'external_id': 'external_id',
        'line': 'line',
        'status': 'status',
        'created': datetime.datetime.now(),
        'updated': datetime.datetime.now(),
        'tags': [],
        'meta_info': meta_info,
    }
    if chat_type:
        base_task_body['chat_type'] = chat_type
    response_task_body = (
        await tasks.create_tasks_info_response(
            [base_task_body], cbox.app, log_extra={},
        )
    )[0]
    assert response_task_body.get('requester') == requester_info
    assert response_task_body['chat_type'] == chat_type or 'client'
    if 'ticket_subject' in meta_info:
        assert 'ticket_subject' in response_task_body
    assert 'some_field' not in response_task_body


@pytest.mark.config(
    CHATTERBOX_LINES={'first': {'name': '1 · DM РФ', 'priority': 3}},
    CHATTERBOX_LINES_PERMISSIONS={
        'first': {
            'take': [{'permissions': ['take_permission']}],
            'search': [
                {'permissions': ['search_permission']},
                {
                    'permissions': ['search_permission_by_country'],
                    'countries': ['eng'],
                },
            ],
        },
    },
)
@pytest.mark.filldb(support_chatterbox='lines_permission')
@pytest.mark.parametrize(
    ('tvm_enabled', 'groups', 'is_superuser', 'expected_status'),
    (
        (False, [], False, 200),
        (True, [], True, 200),
        (
            True,
            ['readonly', 'client_first', 'search_unlimited_time'],
            False,
            200,
        ),
        (
            True,
            ['readonly', 'client_first_search', 'search_unlimited_time'],
            False,
            200,
        ),
        (
            True,
            [
                'readonly',
                'client_first_search_english',
                'search_unlimited_time',
            ],
            False,
            200,
        ),
        (
            True,
            ['readonly', 'chatterbox_take_full', 'search_unlimited_time'],
            False,
            200,
        ),
        (
            True,
            [
                'readonly',
                'chatterbox_search_and_view_full',
                'search_unlimited_time',
            ],
            False,
            200,
        ),
        (True, [], False, 403),
        (True, ['readonly', 'client_first_search_russia'], False, 403),
    ),
)
async def test_search_lines_permissions(
        cbox: conftest.CboxWrap,
        patch_auth,
        tvm_enabled: bool,
        groups: list,
        is_superuser: bool,
        expected_status: dict,
):
    cbox.app.config.TVM_ENABLED = tvm_enabled
    if tvm_enabled:
        patch_auth(superuser=is_superuser, groups=groups)

    await cbox.post('/v1/tasks/search/', data={})

    assert cbox.status == expected_status
    if cbox.status == 200:
        assert len(cbox.body_data['tasks']) == 1


@pytest.mark.translations(
    chatterbox={
        'text_search.search_limited': {
            'ru': 'Результат ограничен из-за отсутствия прав на линии: {}.',
            'en': 'Results limited for lines: {}. Permissions required',
        },
        'text_search.search_limit_time': {
            'ru': 'Отображаются тикеты за последние {days} дней',
            'en': 'Tickets for the last {days} days are displayed',
        },
    },
)
@pytest.mark.config(
    TVM_ENABLED=True,
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3},
        'corp': {'name': 'Corp', 'priority': 2},
    },
    CHATTERBOX_LINES_PERMISSIONS={
        'first': {
            'take': [{'permissions': ['take_permission']}],
            'search': [
                {'permissions': ['search_permission']},
                {
                    'permissions': ['search_permission_by_country'],
                    'countries': ['eng'],
                },
            ],
        },
        'corp': {
            'take': [{'permissions': ['take_corp_permission']}],
            'search': [{'permissions': ['search_corp_permission']}],
        },
    },
)
@pytest.mark.parametrize(
    ('locale', 'message'),
    (
        (
            'ru',
            'Результат ограничен из-за отсутствия прав на линии: corp.\n'
            'Отображаются тикеты за последние 45 дней',
        ),
        (
            'en',
            'Results limited for lines: corp. Permissions required\n'
            'Tickets for the last 45 days are displayed',
        ),
        (
            'az',
            'Results limited for lines: corp. Permissions required\n'
            'Tickets for the last 45 days are displayed',
        ),
    ),
)
@pytest.mark.parametrize(
    'groups',
    (['readonly', 'client_first'], ['readonly', 'client_first_search']),
)
async def test_search_lines_limited(
        cbox: conftest.CboxWrap,
        patch_auth,
        patch_support_chat_get_history,
        groups: list,
        locale: str,
        message: str,
):
    patch_auth(superuser=False, groups=groups)
    patch_support_chat_get_history()

    await cbox.post(
        '/v1/tasks/search/',
        data={'lines': ['first', 'corp']},
        headers={'Accept-Language': locale},
    )
    assert cbox.status == 200
    assert cbox.body_data['message'] == message


DEFAULT_LIMIT_DAYS = chatterbox_config.Config.CHATTERBOX_DAYS_LIMIT_FOR_SEARCH


@pytest.mark.config(
    TVM_ENABLED=True,
    CHATTERBOX_LINES_PERMISSIONS={
        'first': {
            'take': [{'permissions': ['take_permission']}],
            'search': [
                {'permissions': ['search_permission']},
                {'permissions': ['search_permission_by_country']},
            ],
        },
    },
)
@pytest.mark.parametrize(
    ('groups', 'is_superuser', 'expected_status', 'expected_limit_time'),
    (
        ([], False, 403, None),
        ([], True, 200, None),
        (['readonly', 'client_first'], False, 200, DEFAULT_LIMIT_DAYS),
        (['readonly', 'client_first_search'], False, 200, DEFAULT_LIMIT_DAYS),
        (
            ['readonly', 'client_first', 'search_unlimited_time'],
            False,
            200,
            None,
        ),
    ),
)
async def test_search_limit_time_flag(
        cbox: conftest.CboxWrap,
        patch_auth,
        groups,
        is_superuser,
        expected_status,
        expected_limit_time,
        patch,
):
    patch_auth(superuser=is_superuser, groups=groups)

    @patch('chatterbox.internal.tasks_manager._private.get_query_for_search')
    def _get_query_for_search(config, limit_time, **kwargs):
        assert limit_time == expected_limit_time

    @patch(
        'chatterbox.internal.startrack_manager.'
        'StartrackManager.get_startrack_query',
    )
    def _get_startrack_query(profile, limit_time, **kwargs):
        assert limit_time == expected_limit_time

    await cbox.post('/v1/tasks/search/', data={})
    assert cbox.status == expected_status


@pytest.mark.now('2019-10-02T12:00:00+0')
@pytest.mark.config(
    CHATTERBOX_SEARCH_QUEUES_BY_PROFILE={
        'support-taxi': ['TESTQUEUE', 'CHATTERBOX'],
    },
    STARTRACK_CUSTOM_FIELDS_MAP_FOR_SEARCH={
        'support-taxi': {
            'chatterbox_id': 'Chatterbox ID',
            'user_phone': 'user phone',
            'user_email': 'user e-mail',
            'login': 'support',
            'lines': 'line',
            'driver_license': 'driver license',
            'order_id': 'order id',
            'car_number': 'car number',
            'driver_uuid': 'driver uuid',
            'park_name': 'park name',
            'clid': 'clid',
            'park_db_id': 'park db id',
            'city': 'city',
            'driver_name': 'driver name',
            'taximeter_version': 'taximeter version',
            'device_model': 'device model',
        },
    },
)
@pytest.mark.parametrize(
    'data, expected_query, limit_days',
    [
        (
            {'status': 'archived'},
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: >= "2019-08-18"',
            DEFAULT_LIMIT_DAYS,
        ),
        (
            {
                'status': 'archived',
                'created': datetime.datetime(2018, 5, 7, 12),
            },
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: "2019-08-18".."2018-05-07"',
            DEFAULT_LIMIT_DAYS,
        ),
        (
            {
                'status': 'archived',
                'created': datetime.datetime(2019, 10, 1, 12),
            },
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: "2019-10-01".."2019-10-01"',
            DEFAULT_LIMIT_DAYS,
        ),
        (
            {
                'status': 'archived',
                'created_from': datetime.datetime(2019, 10, 1, 12),
            },
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: >= "2019-10-01 15:00"',
            DEFAULT_LIMIT_DAYS,
        ),
        (
            {
                'status': 'archived',
                'created_from': datetime.datetime(2018, 10, 1, 12),
            },
            'Queue: "TESTQUEUE", "CHATTERBOX" AND '
            '"Chatterbox ID": notEmpty() AND '
            'created: >= "2019-08-18 03:00"',
            DEFAULT_LIMIT_DAYS,
        ),
    ],
)
async def test_search_startrack_query_limit_time(
        cbox, data, expected_query, limit_days,
):

    query = cbox.app.startrack_manager.get_startrack_query(
        'support-taxi', limit_days, **data,
    )
    assert query == expected_query


@pytest.mark.now('2019-10-02T12:00:00+0')
@pytest.mark.parametrize(
    'data, limit_days, expected_gte',
    [
        ({}, DEFAULT_LIMIT_DAYS, datetime.datetime(2019, 8, 18, 0)),
        (
            {'created_from': datetime.datetime(2018, 5, 7, 12)},
            None,
            datetime.datetime(2018, 5, 7, 12),
        ),
        (
            {'created_from': datetime.datetime(2018, 5, 7, 12)},
            DEFAULT_LIMIT_DAYS,
            datetime.datetime(2019, 8, 18, 0),
        ),
        (
            {'created_from': datetime.datetime(2019, 8, 20, 12)},
            DEFAULT_LIMIT_DAYS,
            datetime.datetime(2019, 8, 20, 12),
        ),
        (
            {'created': datetime.datetime(2019, 8, 15, 12)},
            DEFAULT_LIMIT_DAYS,
            datetime.datetime(2019, 8, 18, 0),
        ),
    ],
)
async def test_search_mongo_query_limit_time(
        cbox, data, limit_days, expected_gte,
):
    query = _private.get_query_for_search(cbox.app.config, limit_days, **data)
    assert query['created']['$gte'] == expected_gte


@pytest.mark.translations(
    chatterbox={
        'text_search.startrack_error': {'en': 'Startrack tickets are rip'},
    },
)
@pytest.mark.config(
    STARTRACK_CUSTOM_FIELDS_MAP_FOR_SEARCH={
        'support-taxi': {
            'chatterbox_id': 'Chatterbox ID',
            'user_phone': 'user phone',
            'user_email': 'user e-mail',
            'login': 'support',
            'lines': 'line',
            'driver_license': 'driver license',
            'order_id': 'order id',
            'car_number': 'car number',
            'driver_uuid': 'driver uuid',
            'park_name': 'park name',
            'clid': 'clid',
            'park_db_id': 'park db id',
            'city': 'city',
            'driver_name': 'driver name',
            'taximeter_version': 'taximeter version',
            'device_model': 'device model',
        },
    },
)
@pytest.mark.parametrize(
    ['exc', 'expected_code'],
    [
        (
            pytest.param(
                startrack.NetworkError,
                200,
                marks=[
                    pytest.mark.config(
                        CHATTERBOX_HANDLE_SEARCH_TRACKER_ERRORS=False,
                    ),
                ],
            )
        ),
        (
            pytest.param(
                startrack.QueryError,
                200,
                marks=[
                    pytest.mark.config(
                        CHATTERBOX_HANDLE_SEARCH_TRACKER_ERRORS=True,
                    ),
                ],
            )
        ),
        (
            pytest.param(
                startrack.QueryError,
                500,
                marks=[
                    pytest.mark.config(
                        CHATTERBOX_HANDLE_SEARCH_TRACKER_ERRORS=False,
                    ),
                ],
            )
        ),
    ],
)
async def test_startrack_error(cbox, monkeypatch, mock, exc, expected_code):
    class DummyStartrackClient:
        def __init__(self):
            pass

        async def search(self, query, page, page_size, **kwargs):
            raise exc

    cbox.app.startrack_manager.startrack_client_holder = (
        StartrackClientHolderMock(DummyStartrackClient())
    )

    await cbox.post(
        '/v1/tasks/search/', data={}, headers={'Accept-Language': 'en'},
    )
    assert cbox.status == expected_code
    if expected_code == http.HTTPStatus.OK:
        assert cbox.body_data['message'] == 'Startrack tickets are rip'
