# pylint: disable=redefined-outer-name,too-many-arguments,too-many-locals
# pylint: disable=no-member,too-many-lines

import datetime
import json
import random
import uuid

import bson
import pytest

from taxi import discovery
from taxi.clients import support_info
from taxi.clients import supportai_api

from chatterbox import stq_task

PREDISPATCH_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a5')
NEW_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a6')
REOPENED_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a7')
REOPENED_TASK_ID_2 = bson.ObjectId('5b2cae5cb2682a976914c2b8')
AUTOREPLY_CANCELLED_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a9')
AUTOREPLY_EXPIRED_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2aa')
NTO_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2ab')
NTO_IN_PROGRESS_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2ac')
AUTOREPLY_IN_PROGRESS_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2ad')
AUTOREPLY_IN_PROGRESS_TASK_ID_2 = bson.ObjectId('5b2cae5cb2682a976914c3ad')
AUTOREPLY_MUST_FAIL_TASK_ID_OFFLINE = bson.ObjectId('5b2cae5cb2682a976914c2ae')
AUTOREPLY_MUST_FAIL_TASK_ID_ONLINE = bson.ObjectId('5b2cae5cb2682a976914c2af')
DRIVER_EXTRA_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2a8')
DRIVER_ROUTING_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2b0')
FORWARD_CLIENT_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2b1')
FORWARD_CLIENT_TASK_ID_2 = bson.ObjectId('5b2cae5cb2682a976914c2b2')
FORWARD_DRIVER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2b3')
EATS_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2b4')
DEFERRED_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2b5')
OPTEUM_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2b6')
OPTEUM_NEW_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2b7')
POST_UPDATE_CLIENT_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2b9')
POST_UPDATE_DRIVER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2ba')
POST_UPDATE_OPTEUM_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2bb')
POST_UPDATE_DRIVER_THIRD_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2bc')
FOODTECH_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2bf')
FOODTECH_CLIENT_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2c1')
FOODTECH_PREDISPATCH_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2c2')
CONDITIONAL_FORWARD_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2bd')
POST_UPDATE_ONLINE_CLIENT_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2be')
PERSONAL_CLIENT_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2c4')
PERSONAL_DRIVER_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2c3')
MESSENGER_PREDISPATCH_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2c5')
CLIENT_ONLINE_REOPEN_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2c6')
FOODTECH_TASK_ID_2 = bson.ObjectId('5b2cae5cb2682a976914c2c7')
DRIVER_ML_ROUTING_TASK_ID = bson.ObjectId('5b2cae5cb2682a976914c2c8')
FOODTECH_TASK_ID_3 = bson.ObjectId('c4062d06caf0ed917e90fe83')
FOODTECH_TASK_ID_4 = bson.ObjectId('b67775bbc9aec61adf0f41eb')

NOW = datetime.datetime(2018, 6, 15, 12, 34)
UUID = '00000000000040008000000000000000'


def _dummy_uuid4():
    return uuid.UUID(int=0, version=4)


# pylint: disable=too-many-statements
@pytest.fixture
def patch_support_chat_multi_msg(
        patch_aiohttp_session,
        response_mock,
        messages,
        sender_role,
        only_sender_user,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def _dummy_support_chat_request(method, url, **kwargs):
        if url.endswith('/history'):
            if only_sender_user:
                message_list = []
            else:
                message_list = [
                    {
                        'id': 'message_id',
                        'sender': {'id': 'some_login', 'role': 'support'},
                        'text': 'some support text',
                        'metadata': {'created': '2018-05-05T15:34:57'},
                    },
                ]
            for message_text, created_at in messages:
                data = {
                    'sender': {'id': 'some_login', 'role': sender_role},
                    'text': message_text,
                    'metadata': {'created': created_at},
                    'id': 'message_id',
                }
                message_list.append(data)
            return response_mock(json={'messages': message_list})

        return response_mock(json={})

    return _dummy_support_chat_request


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {
            'conditions': {},
            'name': '1 · DM РФ',
            'priority': 3,
            'autoreply': True,
            'mode': 'online',
        },
        'second': {
            'conditions': {'fields.ml_predicted_line': 'second'},
            'name': '2',
            'priority': 1,
            'autoreply': True,
            'mode': 'online',
        },
        'third': {
            'conditions': {'fields.ml_predicted_line': 'third'},
            'name': '3',
            'priority': 1,
        },
        'online': {
            'conditions': {},
            'name': '4',
            'priority': 4,
            'mode': 'online',
            'autoreply': True,
        },
    },
    CHATTERBOX_ENABLE_ONLINE_AUTOREPLY=True,
    CHATTERBOX_CHANGE_LINE_STATUSES={
        'forwarded': 'forwarded',
        'new': 'new',
        'routing': 'forwarded',
    },
    CHATTERBOX_AUTOREPLY={
        'client': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['client']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'client',
            'event_type': 'client',
        },
        'messenger': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['messenger']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'messenger',
            'event_type': 'messenger',
        },
        'driver': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['driver']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'driver',
            'event_type': 'driver',
            'predispatch_routing': True,
        },
        'opteum': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {
                'chat_type': {'#in': ['opteum']},
                'status': {'#in': ['new', 'routing']},
            },
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'opteum',
            'event_type': 'opteum',
            'predispatch_routing': True,
        },
        'eda': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {
                'chat_type': {
                    '#in': ['client', 'client_eats', 'client_eats_app'],
                },
            },
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'eats_client',
            'event_type': 'eats',
            'need_driver_meta': True,
            'predispatch_routing': True,
        },
    },
    CHATTERBOX_REOPEN_AUTOREPLY={
        'percentage': 100,
        'statuses': ['reopened', 'new', 'forwarded', 'routing', 'deferred'],
    },
    CHATTERBOX_FORWARD_AUTOREPLY=True,
    CHATTERBOX_AUTOREPLY_USE_EVENT_TYPE=True,
    PASS_STATUS_IF_FAIL_TO_STQ_CHATTERBOX_AUTOREPLY=True,
)
@pytest.mark.parametrize(
    (
        'task_id',
        'messages',
        'lang',
        'expected_tags',
        'autoreply_line',
        'autoreply_status',
        'autoreply_macro_id',
        'expected_status',
        'expected_autoreply_url',
        'event_type',
        'sender_role',
        'only_sender_user',
        'expected_autoreply',
        'expected_line',
        'expected_chatterbox_autoreply_queue_kwargs',
    ),
    [
        (
            DRIVER_EXTRA_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему меня заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            [
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            ],
            None,
            ['reply'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'driver',
            'driver',
            True,
            True,
            'first',
            {'log_extra': None, 'status_if_fail': 'new'},
        ),
        (
            FORWARD_CLIENT_TASK_ID,
            [('Сообщение1', '2018-05-05T15:34:57')],
            'ru',
            [
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_forward_autoreply',
                'use_ml_autoreply',
            ],
            None,
            ['reply'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'client',
            'client',
            True,
            True,
            'first',
            {'log_extra': None, 'status_if_fail': 'forwarded'},
        ),
        (
            FORWARD_CLIENT_TASK_ID_2,
            [('Сообщение1', '2018-05-05T15:34:57')],
            'ru',
            ['manual_solve'],
            None,
            ['reply'],
            1,
            'forwarded',
            None,
            'client',
            'client',
            False,
            False,
            'second',
            None,
        ),
        (
            FORWARD_DRIVER_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему меня заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            [
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'use_autoreply_project_driver',
                'use_forward_autoreply',
                'use_ml_autoreply',
            ],
            None,
            ['reply'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'driver',
            'driver',
            True,
            True,
            'first',
            {'log_extra': None, 'status_if_fail': 'forwarded'},
        ),
        (
            OPTEUM_NEW_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему парк заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            [
                'check_autoreply_project_opteum',
                'check_ml_autoreply',
                'use_autoreply_project_opteum',
                'use_ml_autoreply',
            ],
            None,
            ['reply'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'opteum',
            'opteum_client',
            True,
            True,
            'first',
            {'log_extra': None, 'status_if_fail': 'new'},
        ),
        (
            POST_UPDATE_DRIVER_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему меня заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            [
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            ],
            None,
            ['reply'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'driver',
            'driver',
            True,
            True,
            'first',
            {'log_extra': None, 'status_if_fail': 'reopened'},
        ),
        (
            POST_UPDATE_DRIVER_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему меня заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            [
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            ],
            'second',
            ['reply', 'forward'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'driver',
            'driver',
            True,
            True,
            'second',
            {'log_extra': None, 'status_if_fail': 'reopened'},
        ),
        (
            POST_UPDATE_DRIVER_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему меня заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            ['check_ml_autoreply', 'check_autoreply_project_driver'],
            'third',
            ['reply', 'forward'],
            1,
            'forwarded',
            '/supportai-api/v1/support_internal',
            'driver',
            'driver',
            True,
            False,
            'third',
            None,
        ),
        (
            POST_UPDATE_DRIVER_THIRD_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему меня заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            ['check_ml_autoreply', 'check_autoreply_project_driver'],
            None,
            ['reply'],
            1,
            'reopened',
            '/supportai-api/v1/support_internal',
            'driver',
            'driver',
            True,
            False,
            'third',
            None,
        ),
        (
            POST_UPDATE_CLIENT_TASK_ID,
            [('Сообщение1', '2018-05-05T15:34:57')],
            'ru',
            [
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            ],
            None,
            ['reply'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'client',
            'client',
            True,
            True,
            'first',
            {'log_extra': None, 'status_if_fail': 'reopened'},
        ),
        (
            POST_UPDATE_CLIENT_TASK_ID,
            [('Сообщение1', '2018-05-05T15:34:57')],
            'ru',
            [
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            ],
            'second',
            ['reply', 'forward'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'client',
            'client',
            True,
            True,
            'second',
            {'log_extra': None, 'status_if_fail': 'reopened'},
        ),
        pytest.param(
            POST_UPDATE_CLIENT_TASK_ID,
            [('Сообщение1', '2018-05-05T15:34:57')],
            'ru',
            [],
            None,
            None,
            None,
            'reopened',
            None,
            None,
            'client',
            True,
            False,
            'first',
            None,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
                        'client': {'__default__': True},
                    },
                ),
            ],
        ),
        (
            CONDITIONAL_FORWARD_TASK_ID,
            [('Сообщение1', '2018-05-05T15:34:57')],
            'ru',
            [
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'conditional_action_forward',
            ],
            'second',
            ['reply', 'forward'],
            1,
            'forwarded',
            '/supportai-api/v1/support_internal',
            'client',
            'client',
            True,
            False,
            'second',
            None,
        ),
        (
            POST_UPDATE_OPTEUM_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему парк заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            [
                'check_autoreply_project_opteum',
                'check_ml_autoreply',
                'use_autoreply_project_opteum',
                'use_ml_autoreply',
            ],
            None,
            ['reply'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'opteum',
            'opteum_client',
            True,
            True,
            'first',
            {'log_extra': None, 'status_if_fail': 'reopened'},
        ),
        (
            POST_UPDATE_OPTEUM_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему парк заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            [
                'check_autoreply_project_opteum',
                'check_ml_autoreply',
                'use_autoreply_project_opteum',
                'use_ml_autoreply',
            ],
            'second',
            ['reply', 'forward'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'opteum',
            'opteum_client',
            True,
            True,
            'second',
            {'log_extra': None, 'status_if_fail': 'reopened'},
        ),
        (
            POST_UPDATE_OPTEUM_TASK_ID,
            [
                ('Привет', '2018-05-05T15:34:57'),
                ('Почему парк заблокировали?', '2018-05-05T15:34:59'),
            ],
            'ru',
            ['check_ml_autoreply', 'check_autoreply_project_opteum'],
            'third',
            ['forward'],
            None,
            'forwarded',
            '/supportai-api/v1/support_internal',
            'opteum',
            'opteum_client',
            True,
            False,
            'third',
            None,
        ),
        (
            POST_UPDATE_ONLINE_CLIENT_TASK_ID,
            [('Сообщение1', '2018-05-05T15:34:57')],
            'ru',
            [
                'ar_fail',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
                'autoreply_macro_missing',
            ],
            None,
            ['reply'],
            0,
            'forwarded',
            '/supportai-api/v1/support_internal',
            'client',
            'client',
            True,
            False,
            'first',
            None,
        ),
    ],
)
async def test_post_update_autoreply(
        cbox,
        stq,
        patch_aiohttp_session,
        response_mock,
        patch_support_chat_multi_msg,
        monkeypatch,
        mock_get_chat_order_meta,
        task_id,
        messages,
        lang,
        expected_tags,
        autoreply_line,
        autoreply_status,
        autoreply_macro_id,
        expected_status,
        expected_autoreply_url,
        event_type,
        sender_role,
        only_sender_user,
        expected_autoreply,
        expected_line,
        expected_chatterbox_autoreply_queue_kwargs,
):
    def _dummy_randint(min_value, max_value):
        return max_value

    monkeypatch.setattr(random, 'randint', _dummy_randint)

    @patch_aiohttp_session('http://test-translate-url/', 'GET')
    def _dummy_translate_request(*args, **kwargs):
        return response_mock(json={'code': '200', 'lang': lang})

    support_info_service = discovery.find_service('support_info')

    @patch_aiohttp_session(
        support_info_service.url + '/v1/autoreply/driver', 'POST',
    )
    def _dummy_driver_autoreply(*args, **kwargs):
        response = {
            'autoreply': {
                'status': autoreply_status,
                'macro_id': autoreply_macro_id,
            },
        }
        if autoreply_line:
            response['autoreply']['line'] = autoreply_line
        return response_mock(json=response)

    @patch_aiohttp_session(
        support_info_service.url + '/v1/autoreply/driver_meta', 'POST',
    )
    def _dummy_autoreply_driver_meta(method, url, **kwargs):
        assert method == 'post'
        assert 'calls' not in kwargs['json']['metadata']
        response = {'metadata': {'some': 'metadata'}, 'status': 'ok'}
        return response_mock(json=response)

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert url == supportai_api_service.url + expected_autoreply_url

        response = {}
        if 'reply' in autoreply_status and autoreply_macro_id is not None:
            response.setdefault('reply', {})
            response['reply']['text'] = autoreply_macro_id
        if 'forward' in autoreply_status and autoreply_line:
            response.setdefault('forward', {})
            response['forward']['line'] = autoreply_line
        return response_mock(json=response)

    await stq_task.post_update(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    support_chat_request_calls = patch_support_chat_multi_msg.calls

    assert task['status'] == expected_status
    assert 'tags' in task
    assert set(task['tags']) == set(expected_tags)
    assert task['line'] == expected_line
    if autoreply_line:
        assert task['meta_info']['ml_predicted_line'] == autoreply_line
        update_meta_events = [
            event
            for event in task['history']
            if event['action'] == 'update_meta'
        ]
        assert any(
            {
                'change_type': 'set',
                'field_name': 'ml_predicted_line',
                'value': autoreply_line,
            }
            in event.get('meta_changes', [])
            for event in update_meta_events
        )

    if expected_autoreply:
        assert support_chat_request_calls
        assert stq.chatterbox_common_autoreply_queue.times_called == 1
        call = stq.chatterbox_common_autoreply_queue.next_call()
        assert call['args'] == [
            {'$oid': str(task['_id'])},
            {'comment': {'macro_id': autoreply_macro_id}},
            event_type,
        ]
        assert call['kwargs']['request_id']
        del call['kwargs']['request_id']
        assert call['kwargs'] == expected_chatterbox_autoreply_queue_kwargs
    else:
        assert not stq.chatterbox_common_autoreply_queue.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'second': {'name': '2', 'mode': 'online', 'autoreply': True},
    },
    CHATTERBOX_AUTOREPLY={
        'client': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['client']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'client',
            'event_type': 'client',
        },
        'messenger': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['messenger']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'messenger',
            'event_type': 'messenger',
        },
        'driver': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['driver']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'driver',
            'event_type': 'driver',
            'predispatch_routing': True,
        },
        'opteum': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {
                'chat_type': {'#in': ['opteum']},
                'status': {'#in': ['new', 'routing']},
            },
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'opteum',
            'event_type': 'opteum',
            'predispatch_routing': True,
        },
        'eda': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {
                'chat_type': {
                    '#in': ['client', 'client_eats', 'client_eats_app'],
                },
                '#or': [
                    {'meta_info.order_type': 'eats'},
                    {'meta_info.service': 'native'},
                ],
            },
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'eda_client_dialog',
            'event_type': 'eats',
            'need_driver_meta': True,
            'predispatch_routing': True,
        },
        'lavka': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {
                'chat_type': {
                    '#in': ['client', 'client_eats', 'client_eats_app'],
                },
                '#or': [
                    {'meta_info.order_type': 'lavka'},
                    {'meta_info.service': 'grocery'},
                ],
            },
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'lavka_client_dialog',
            'event_type': 'lavka',
            'need_driver_meta': True,
            'predispatch_routing': True,
        },
    },
    CHATTERBOX_REOPEN_AUTOREPLY={
        'percentage': 100,
        'statuses': ['reopened', 'new', 'forwarded', 'routing', 'deferred'],
    },
    CHATTERBOX_FORWARD_AUTOREPLY=True,
    CHATTERBOX_AUTOREPLY_USE_EVENT_TYPE=True,
    CHATTERBOX_USE_CHAT_MESSAGE_ID=True,
)
@pytest.mark.parametrize(
    (
        'task_id',
        'lang',
        'expected_tags',
        'autoreply_status',
        'autoreply_macro_id',
        'expected_status',
        'expected_autoreply_url',
        'event_type',
        'expected_autoreply',
        'custom_chat_get_history',
        'expected_dialogue',
    ),
    [
        (
            REOPENED_TASK_ID,
            'ru',
            [
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            ],
            ['reply', 'close'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'client',
            True,
            {
                'new_message_count': 1,
                'messages': [
                    {
                        'id': 1,
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'сообщение1',
                        'metadata': {
                            'created': '2018-05-05T12:34:56+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                    {
                        'id': 2,
                        'sender': {'id': 'support_login', 'role': 'support'},
                        'text': 'сообщение',
                        'metadata': {
                            'created': '2018-05-05T12:34:59+00:00',
                            'reply_to': ['123'],
                        },
                    },
                    {
                        'id': 3,
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'сообщение2',
                        'metadata': {'created': '2018-05-05T12:35:01+00:00'},
                    },
                ],
            },
            {
                'chat_id': '5b2cae5cb2682a976914c2a7',
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:34:56Z',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': (
                                        '398b9611471548029cd3338c44cdd6bf'
                                    ),
                                },
                                {'key': 'line', 'value': 'first_center'},
                            ],
                            'id': 1,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение1',
                        },
                        {
                            'author': 'support',
                            'created': '2018-05-05T12:34:59Z',
                            'features': [
                                {'key': 'login', 'value': 'support_login'},
                                {'key': 'action', 'value': 'communicate'},
                                {'key': 'line', 'value': 'first_center'},
                                {'key': 'macro_ids', 'value': [123, 456]},
                                {
                                    'key': 'tags',
                                    'value': ['add_tag', 'chat_tag'],
                                },
                            ],
                            'id': 2,
                            'language': 'ru',
                            'reply_to': ['123'],
                            'text': 'сообщение',
                        },
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:35:01Z',
                            'id': 3,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение2',
                        },
                    ],
                },
                'features': [
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'locale', 'value': 'ru'},
                    {
                        'key': 'ml_request_id',
                        'value': '045fb0acd2024594b52952fec3cd39f2',
                    },
                    {'key': 'user_id', 'value': 'user_id'},
                    {'key': 'user_phone', 'value': '+74950000001'},
                    {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'client'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {
                        'key': 'request_id',
                        'value': '045fb0acd2024594b52952fec3cd39f2',
                    },
                    {'key': 'is_reopen', 'value': True},
                    {'key': 'number_of_reopens', 'value': 1},
                    {'key': 'all_tags', 'value': ['add_tag', 'chat_tag']},
                    {
                        'key': 'last_message_tags',
                        'value': ['add_tag', 'chat_tag'],
                    },
                    {'key': 'comment_lowercased', 'value': 'сообщение2'},
                    {'key': 'number_of_orders', 'value': 1},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'communicate'},
                ],
            },
        ),
        (
            REOPENED_TASK_ID,
            'ru',
            [
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            ],
            ['close'],
            None,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'client',
            True,
            {
                'new_message_count': 1,
                'messages': [
                    {
                        'id': 1,
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'сообщение1',
                        'metadata': {
                            'created': '2018-05-05T12:34:56+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                    {
                        'id': 2,
                        'sender': {'id': 'support_login', 'role': 'support'},
                        'text': 'сообщение',
                        'metadata': {
                            'created': '2018-05-05T12:34:59+00:00',
                            'reply_to': ['123'],
                        },
                    },
                    {
                        'id': 3,
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'сообщение2',
                        'metadata': {'created': '2018-05-05T12:35:01+00:00'},
                    },
                ],
            },
            {
                'chat_id': '5b2cae5cb2682a976914c2a7',
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:34:56Z',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': (
                                        '398b9611471548029cd3338c44cdd6bf'
                                    ),
                                },
                                {'key': 'line', 'value': 'first_center'},
                            ],
                            'id': 1,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение1',
                        },
                        {
                            'author': 'support',
                            'created': '2018-05-05T12:34:59Z',
                            'features': [
                                {'key': 'login', 'value': 'support_login'},
                                {'key': 'action', 'value': 'communicate'},
                                {'key': 'line', 'value': 'first_center'},
                                {'key': 'macro_ids', 'value': [123, 456]},
                                {
                                    'key': 'tags',
                                    'value': ['add_tag', 'chat_tag'],
                                },
                            ],
                            'id': 2,
                            'language': 'ru',
                            'reply_to': ['123'],
                            'text': 'сообщение',
                        },
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:35:01Z',
                            'id': 3,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение2',
                        },
                    ],
                },
                'features': [
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'locale', 'value': 'ru'},
                    {
                        'key': 'ml_request_id',
                        'value': '045fb0acd2024594b52952fec3cd39f2',
                    },
                    {'key': 'user_id', 'value': 'user_id'},
                    {'key': 'user_phone', 'value': '+74950000001'},
                    {'key': 'antifraud_rules', 'value': ['taxi_free_trips']},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'client'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {
                        'key': 'request_id',
                        'value': '045fb0acd2024594b52952fec3cd39f2',
                    },
                    {'key': 'is_reopen', 'value': True},
                    {'key': 'number_of_reopens', 'value': 1},
                    {'key': 'all_tags', 'value': ['add_tag', 'chat_tag']},
                    {
                        'key': 'last_message_tags',
                        'value': ['add_tag', 'chat_tag'],
                    },
                    {'key': 'comment_lowercased', 'value': 'сообщение2'},
                    {'key': 'number_of_orders', 'value': 1},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'communicate'},
                ],
            },
        ),
        (
            REOPENED_TASK_ID_2,
            'ru',
            [
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'use_autoreply_project_driver',
                'use_ml_autoreply',
            ],
            ['reply', 'close'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'driver',
            True,
            {
                'new_message_count': 0,
                'messages': [
                    {
                        'id': 1,
                        'sender': {'id': 'some_login', 'role': 'sms_client'},
                        'text': 'сообщение1',
                        'metadata': {
                            'created': '2018-05-05T12:34:56Z',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                    {
                        'id': 2,
                        'sender': {'id': 'some_login', 'role': 'eats_client'},
                        'text': 'сообщение2',
                        'metadata': {'created': '2018-05-05T12:34:58Z'},
                    },
                    {
                        'id': 3,
                        'sender': {'id': 'support_login', 'role': 'support'},
                        'text': 'сообщениеA',
                        'metadata': {'created': '2018-05-05T12:34:59Z'},
                    },
                    {
                        'id': 4,
                        'sender': {'id': 'some_login', 'role': 'driver'},
                        'text': 'сообщение3',
                        'metadata': {
                            'created': '2018-05-05T12:35:00Z',
                            'attachments': [
                                {'id': '123', 'mimetype': 'text/plain'},
                            ],
                        },
                    },
                    {
                        'id': 5,
                        'sender': {'id': 'support_login', 'role': 'support'},
                        'text': 'сообщениеB',
                        'metadata': {'created': '2018-05-05T12:35:01Z'},
                    },
                ],
            },
            {
                'chat_id': '5b2cae5cb2682a976914c2b8',
                'dialog': {
                    'messages': [
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:34:56Z',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': (
                                        '398b9611471548029cd3338c44cdd6bf'
                                    ),
                                },
                                {'key': 'line', 'value': 'first_center'},
                            ],
                            'id': 1,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение1',
                        },
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:34:58Z',
                            'features': [
                                {'key': 'line', 'value': 'first_center'},
                            ],
                            'id': 2,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение2',
                        },
                        {
                            'author': 'support',
                            'created': '2018-05-05T12:34:59Z',
                            'features': [
                                {'key': 'login', 'value': 'support_login'},
                                {'key': 'action', 'value': 'communicate'},
                                {'key': 'line', 'value': 'first_center'},
                                {'key': 'macro_ids', 'value': [123, 456]},
                            ],
                            'id': 3,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщениеA',
                        },
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:35:00Z',
                            'features': [
                                {'key': 'line', 'value': 'first_center'},
                            ],
                            'id': 4,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение3',
                        },
                        {
                            'author': 'support',
                            'created': '2018-05-05T12:35:01Z',
                            'features': [
                                {'key': 'login', 'value': 'support_login'},
                                {'key': 'action', 'value': 'communicate'},
                                {'key': 'line', 'value': 'first_center'},
                            ],
                            'id': 5,
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщениеB',
                        },
                    ],
                },
                'features': [
                    {'key': 'autoreply_enqueue_count', 'value': 5},
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'locale', 'value': 'ru'},
                    {
                        'key': 'ml_request_id',
                        'value': '045fb0acd2024594b52952fec3cd39f2',
                    },
                    {'key': 'user_id', 'value': 'user_id'},
                    {'key': 'user_phone', 'value': '+74950000001'},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'driver'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {
                        'key': 'request_id',
                        'value': '045fb0acd2024594b52952fec3cd39f2',
                    },
                    {'key': 'is_reopen', 'value': True},
                    {'key': 'number_of_reopens', 'value': 1},
                    {'key': 'all_tags', 'value': []},
                    {'key': 'last_message_tags', 'value': []},
                    {'key': 'comment_lowercased', 'value': 'сообщение3'},
                    {'key': 'number_of_orders', 'value': 1},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'dismiss'},
                ],
            },
        ),
        (
            FOODTECH_TASK_ID,
            'ru',
            [
                'check_autoreply_project_lavka_client_dialog',
                'check_ml_autoreply',
                'use_autoreply_project_lavka_client_dialog',
                'use_ml_autoreply',
            ],
            ['reply', 'close'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'lavka',
            True,
            {
                'new_message_count': 1,
                'messages': [
                    {
                        'id': 1,
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'сообщение1',
                        'metadata': {
                            'created': '2018-05-05T12:34:56+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                ],
            },
            {
                'chat_id': '5b2cae5cb2682a976914c2bf',
                'dialog': {
                    'messages': [
                        {
                            'id': 1,
                            'author': 'user',
                            'created': '2018-05-05T12:34:56Z',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение1',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': (
                                        '398b9611471548029cd3338c44cdd6bf'
                                    ),
                                },
                                {'key': 'line', 'value': 'first_center'},
                            ],
                        },
                    ],
                },
                'features': [
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'locale', 'value': 'ru'},
                    {'key': 'order_type', 'value': 'lavka'},
                    {'key': 'service', 'value': 'grocery'},
                    {'key': 'user_id', 'value': 'user_id'},
                    {'key': 'user_phone', 'value': '+74950000001'},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'client_eats'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {'key': 'is_reopen', 'value': False},
                    {'key': 'number_of_reopens', 'value': 0},
                    {'key': 'all_tags', 'value': []},
                    {'key': 'last_message_tags', 'value': []},
                    {'key': 'comment_lowercased', 'value': 'сообщение1'},
                    {'key': 'number_of_orders', 'value': 1},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'communicate'},
                ],
            },
        ),
        (
            FOODTECH_TASK_ID_2,
            'ru',
            [
                'check_autoreply_project_lavka_client_dialog',
                'check_ml_autoreply',
                'use_autoreply_project_lavka_client_dialog',
                'use_ml_autoreply',
            ],
            ['reply', 'close'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'lavka',
            True,
            {
                'new_message_count': 1,
                'messages': [
                    {
                        'id': 1,
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'сообщение1',
                        'metadata': {
                            'created': '2018-05-05T12:34:56+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                ],
            },
            {
                'chat_id': '5b2cae5cb2682a976914c2c7',
                'dialog': {
                    'messages': [
                        {
                            'id': 1,
                            'author': 'user',
                            'created': '2018-05-05T12:34:56Z',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение1',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': (
                                        '398b9611471548029cd3338c44cdd6bf'
                                    ),
                                },
                            ],
                        },
                    ],
                },
                'features': [
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'extra_field_2', 'value': ['123', 456, 789.0]},
                    {'key': 'locale', 'value': 'ru'},
                    {'key': 'order_type', 'value': 'lavka'},
                    {'key': 'service', 'value': 'grocery'},
                    {'key': 'user_id', 'value': 'user_id'},
                    {'key': 'user_phone', 'value': '+74950000001'},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'client_eats'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {'key': 'is_reopen', 'value': False},
                    {'key': 'number_of_reopens', 'value': 0},
                    {'key': 'all_tags', 'value': []},
                    {'key': 'last_message_tags', 'value': []},
                    {'key': 'comment_lowercased', 'value': 'сообщение1'},
                    {'key': 'number_of_orders', 'value': 1},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'empty'},
                ],
            },
        ),
        (
            FOODTECH_TASK_ID_3,
            'ru',
            [
                'check_autoreply_project_lavka_client_dialog',
                'check_ml_autoreply',
                'use_autoreply_project_lavka_client_dialog',
                'use_ml_autoreply',
            ],
            ['reply', 'close'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'lavka',
            True,
            {
                'new_message_count': 1,
                'messages': [
                    {
                        'id': 'lavka_user_chat_message_id_3',
                        'sender': {'id': 'superuser', 'role': 'superuser'},
                        'text': 'сообщение12',
                        'metadata': {
                            'created': '2018-05-05T12:34:56+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                    {
                        'id': 'some_id',
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'сообщение1',
                        'metadata': {
                            'created': '2018-05-05T12:34:56+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                ],
            },
            {
                'chat_id': 'c4062d06caf0ed917e90fe83',
                'dialog': {
                    'messages': [
                        {
                            'id': 'lavka_user_chat_message_id_3',
                            'author': 'ai',
                            'created': '2018-05-05T12:34:56Z',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение12',
                            'features': [
                                {'key': 'login', 'value': 'superuser'},
                                {'key': 'action', 'value': 'communicate'},
                                {'key': 'line', 'value': 'first'},
                                {'key': 'macro_ids', 'value': [12, 13, 14]},
                                {'key': 'tags', 'value': ['tag1']},
                            ],
                        },
                        {
                            'id': 'some_id',
                            'author': 'user',
                            'created': '2018-05-05T12:34:56Z',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'сообщение1',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': (
                                        '398b9611471548029cd3338c44cdd6bf'
                                    ),
                                },
                                {'key': 'line', 'value': 'first'},
                            ],
                        },
                    ],
                },
                'features': [
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'extra_field_2', 'value': ['123', 456, 789.0]},
                    {'key': 'locale', 'value': 'ru'},
                    {'key': 'order_type', 'value': 'lavka'},
                    {'key': 'service', 'value': 'grocery'},
                    {'key': 'user_id', 'value': 'user_id'},
                    {'key': 'user_phone', 'value': '+74950000001'},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'client_eats'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {'key': 'is_reopen', 'value': True},
                    {'key': 'number_of_reopens', 'value': 1},
                    {'key': 'all_tags', 'value': ['tag1']},
                    {'key': 'last_message_tags', 'value': ['tag1']},
                    {'key': 'comment_lowercased', 'value': 'сообщение1'},
                    {'key': 'number_of_orders', 'value': 1},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'empty'},
                ],
            },
        ),
        (
            FOODTECH_TASK_ID_4,
            'ru',
            [
                'check_autoreply_project_lavka_client_dialog',
                'check_ml_autoreply',
                'use_autoreply_project_lavka_client_dialog',
                'use_ml_autoreply',
            ],
            ['reply', 'close'],
            1,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            'lavka',
            True,
            {
                'new_message_count': 1,
                'messages': [
                    {
                        'id': 'chat_message_1',
                        'sender': {'id': 'superuser', 'role': 'superuser'},
                        'text': 'superuser_message_1',
                        'metadata': {
                            'created': '2018-05-05T12:34:56+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                    {
                        'id': 'chat_message_2',
                        'sender': {'id': 'user', 'role': 'client'},
                        'text': 'client_message_1',
                        'metadata': {
                            'created': '2018-05-05T12:34:57+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                    {
                        'id': 'chat_message_3',
                        'sender': {'id': 'support_1', 'role': 'support'},
                        'text': 'support_message_1',
                        'metadata': {
                            'created': '2018-05-05T12:34:58+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                    {
                        'id': 'chat_message_4',
                        'sender': {'id': 'support_1', 'role': 'support'},
                        'text': 'support_message_2',
                        'metadata': {
                            'created': '2018-05-05T12:34:59+00:00',
                            'order_id': '398b9611471548029cd3338c44cdd6bf',
                        },
                    },
                    {
                        'id': 'chat_message_5',
                        'sender': {'id': 'user', 'role': 'client'},
                        'text': 'client_message_2',
                        'metadata': {
                            'created': '2018-05-05T12:35:00+00:00',
                            'order_id': '3333333333333333333333333333333',
                        },
                    },
                    {
                        'id': 'chat_message_6',
                        'sender': {'id': 'user', 'role': 'client'},
                        'text': 'client_message_3',
                        'metadata': {
                            'created': '2018-05-05T12:35:01+00:00',
                            'order_id': '3333333333333333333333333333333',
                        },
                    },
                ],
            },
            {
                'chat_id': 'b67775bbc9aec61adf0f41eb',
                'dialog': {
                    'messages': [
                        {
                            'id': 'chat_message_1',
                            'author': 'ai',
                            'created': '2018-05-05T12:34:56Z',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'superuser_message_1',
                            'features': [
                                {'key': 'login', 'value': 'superuser'},
                                {'key': 'action', 'value': 'communicate'},
                                {'key': 'line', 'value': 'first'},
                                {'key': 'macro_ids', 'value': [12, 13, 14]},
                                {'key': 'tags', 'value': ['tag1']},
                            ],
                        },
                        {
                            'id': 'chat_message_2',
                            'author': 'user',
                            'created': '2018-05-05T12:34:57Z',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'client_message_1',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': (
                                        '398b9611471548029cd3338c44cdd6bf'
                                    ),
                                },
                                {'key': 'line', 'value': 'first'},
                            ],
                        },
                        {
                            'author': 'support',
                            'created': '2018-05-05T12:34:58Z',
                            'features': [
                                {'key': 'login', 'value': 'support_1'},
                                {'key': 'action', 'value': 'communicate'},
                                {'key': 'line', 'value': 'first'},
                                {'key': 'macro_ids', 'value': [12, 13, 14]},
                                {'key': 'tags', 'value': ['tag2', 'tag3']},
                            ],
                            'id': 'chat_message_3',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'support_message_1',
                        },
                        {
                            'author': 'support',
                            'created': '2018-05-05T12:34:59Z',
                            'features': [
                                {'key': 'login', 'value': 'support_1'},
                                {
                                    'key': 'action',
                                    'value': 'support_message_2',
                                },
                                {'key': 'line', 'value': 'first'},
                                {'key': 'macro_ids', 'value': [12, 13, 14]},
                                {'key': 'tags', 'value': ['tag4', 'tag5']},
                            ],
                            'id': 'chat_message_4',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'support_message_2',
                        },
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:35:00Z',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': '3333333333333333333333333333333',
                                },
                                {'key': 'line', 'value': 'first'},
                            ],
                            'id': 'chat_message_5',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'client_message_2',
                        },
                        {
                            'author': 'user',
                            'created': '2018-05-05T12:35:01Z',
                            'features': [
                                {
                                    'key': 'order_id',
                                    'value': '3333333333333333333333333333333',
                                },
                                {'key': 'line', 'value': 'first'},
                            ],
                            'id': 'chat_message_6',
                            'language': 'ru',
                            'reply_to': [],
                            'text': 'client_message_3',
                        },
                    ],
                },
                'features': [
                    {'key': 'city', 'value': 'Moscow'},
                    {'key': 'country', 'value': 'rus'},
                    {'key': 'extra_field_2', 'value': ['123', 456, 789.0]},
                    {'key': 'locale', 'value': 'ru'},
                    {'key': 'order_type', 'value': 'lavka'},
                    {'key': 'service', 'value': 'grocery'},
                    {'key': 'user_id', 'value': 'user_id'},
                    {'key': 'user_phone', 'value': '+74950000001'},
                    {'key': 'request_repeated', 'value': True},
                    {'key': 'chat_type', 'value': 'client_eats'},
                    {'key': 'line', 'value': 'first'},
                    {'key': 'screen_attach', 'value': False},
                    {'key': 'is_reopen', 'value': True},
                    {'key': 'number_of_reopens', 'value': 2},
                    {
                        'key': 'all_tags',
                        'value': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
                    },
                    {
                        'key': 'last_message_tags',
                        'value': ['tag2', 'tag3', 'tag4', 'tag5'],
                    },
                    {
                        'key': 'comment_lowercased',
                        'value': 'client_message_2\nclient_message_3',
                    },
                    {'key': 'number_of_orders', 'value': 2},
                    {'key': 'minutes_from_order_creation', 'value': 59039},
                    {'key': 'last_support_action', 'value': 'communicate'},
                ],
            },
        ),
    ],
)
async def test_autoreply_dialogue(
        cbox,
        stq,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        task_id,
        lang,
        expected_tags,
        autoreply_status,
        autoreply_macro_id,
        expected_status,
        expected_autoreply_url,
        event_type,
        expected_autoreply,
        custom_chat_get_history,
        expected_dialogue,
):
    def _dummy_randint(min_value, max_value):
        return min_value - 1

    monkeypatch.setattr(random, 'randint', _dummy_randint)

    mock_chat_get_history(custom_chat_get_history)

    @patch_aiohttp_session('http://test-translate-url/', 'GET')
    def _dummy_translate_request(*args, **kwargs):
        return response_mock(json={'code': '200', 'lang': lang})

    support_info_service = discovery.find_service('support_info')

    @patch_aiohttp_session(support_info_service.url, 'POST')
    def _dummy_autoreply_meta(method, url, **kwargs):
        assert url == support_info_service.url + '/v1/autoreply/driver_meta'
        response = {'metadata': {}, 'status': 'ok'}
        return response_mock(json=response)

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert url == supportai_api_service.url + expected_autoreply_url
        assert kwargs['json'] == expected_dialogue
        assert json.dumps(expected_dialogue)

        response = {}
        if 'close' in autoreply_status:
            response.setdefault('close', {})
        if 'reply' in autoreply_status:
            response.setdefault('reply', {})
            response['reply']['text'] = autoreply_macro_id
        return response_mock(json=response)

    await stq_task.post_update(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})

    assert task['status'] == expected_status
    assert 'tags' in task
    assert set(task['tags']) == set(expected_tags)

    if expected_autoreply:
        assert stq.chatterbox_common_autoreply_queue.times_called == 1
        call = stq.chatterbox_common_autoreply_queue.next_call()
        action_arg = {}
        if 'reply' in autoreply_status and 'close' in autoreply_status:
            action_arg['close'] = {'macro_id': autoreply_macro_id}
        elif 'close' in autoreply_status:
            action_arg['dismiss'] = {}
        elif 'reply' in autoreply_status:
            action_arg['comment'] = {'macro_id': autoreply_macro_id}
        assert call['args'] == [
            {'$oid': str(task['_id'])},
            action_arg,
            event_type,
        ]
    else:
        assert not stq.chatterbox_common_autoreply_queue.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'second': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
    },
    CHATTERBOX_FORWARD_AUTOREPLY=True,
    CHATTERBOX_AUTOREPLY_USE_EVENT_TYPE=True,
    CHATTERBOX_DEFER_AUTOREPLY={
        'enabled': True,
        'max_count': 3,
        'max_time_sec': 600,
        'default_time_sec': 300,
    },
)
@pytest.mark.parametrize(
    (
        'task_id',
        'metadata',
        'call_predispatch',
        'messages',
        'lang',
        'expected_tags',
        'autoreply_status',
        'autoreply_time',
        'expected_time',
        'expected_status',
        'expected_autoreply_url',
        'expected_defer',
        'expected_get_meta',
    ),
    [
        (
            PREDISPATCH_TASK_ID,
            None,
            True,
            ['Привет, еду в такси', '2018-05-05T15:34:57'],
            'ru',
            [
                'lang_ru',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            ],
            'defer',
            240,
            240,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            True,
            False,
        ),
        (
            PREDISPATCH_TASK_ID,
            None,
            True,
            ['Привет, еду в такси', '2018-05-05T15:34:57'],
            'ru',
            [
                'lang_ru',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            ],
            'defer',
            1200,
            1200,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            True,
            False,
        ),
        pytest.param(
            DEFERRED_TASK_ID,
            {'meta_info.autoreply_defer_count': 0},
            False,
            ['Привет, еду в такси', '2018-05-05T15:34:57'],
            'ru',
            [],
            None,
            None,
            None,
            'deferred',
            None,
            False,
            False,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
                        'client': {'__default__': True},
                    },
                ),
            ],
        ),
        (
            DEFERRED_TASK_ID,
            {'meta_info.autoreply_defer_count': 3},
            False,
            ['Привет, еду в такси'],
            'ru',
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            'defer',
            300,
            300,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            True,
            True,
        ),
        (
            DEFERRED_TASK_ID,
            {'meta_info.autoreply_defer_count': 1},
            False,
            ['Привет, еду в такси'],
            'ru',
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            'defer',
            420,
            420,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            True,
            True,
        ),
        (
            DEFERRED_TASK_ID,
            {'meta_info.autoreply_defer_count': 1},
            False,
            ['Привет, еду в такси'],
            'ru',
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            'defer',
            None,
            None,
            'deferred',
            '/supportai-api/v1/support_internal',
            False,
            True,
        ),
        pytest.param(
            DEFERRED_TASK_ID,
            {'meta_info.autoreply_defer_count': 1},
            False,
            ['Привет, еду в такси'],
            'ru',
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            'defer',
            300,
            300,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            True,
            True,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_DEFER_AUTOREPLY={
                        'enabled': True,
                        'max_count': 3,
                        'max_time_sec': 600,
                        'default_time_sec': 300,
                        'deferred_status_delay_sec': 180,
                    },
                ),
            ],
        ),
        pytest.param(
            FOODTECH_TASK_ID,
            {'meta_info.autoreply_defer_count': 0},
            False,
            ['Привет, еду в такси'],
            'ru',
            [
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_autoreply_project_eats_client',
                'use_ml_autoreply',
            ],
            'defer',
            300,
            300,
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
            True,
            False,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_DEFER_AUTOREPLY={
                        'enabled': True,
                        'max_count': 3,
                        'max_time_sec': 600,
                        'default_time_sec': 300,
                        'deferred_status_delay_sec': 180,
                    },
                ),
            ],
        ),
    ],
)
async def test_defer_autoreply(
        cbox,
        stq,
        patch_aiohttp_session,
        response_mock,
        mock_chat_get_history,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        monkeypatch,
        task_id,
        metadata,
        call_predispatch,
        messages,
        lang,
        expected_tags,
        autoreply_status,
        autoreply_time,
        expected_time,
        expected_status,
        expected_autoreply_url,
        expected_defer,
        expected_get_meta,
):
    mock_chat_get_history(
        {
            'messages': [
                {
                    'id': str(index),
                    'sender': {'id': 'some_login', 'role': 'client'},
                    'text': message,
                    'metadata': {'created': '2018-05-05T15:34:56'},
                }
                for index, message in enumerate(messages)
            ],
        },
    )

    async def _dummy_get_additional_meta(*args, **kwargs):
        _metadata = {'test': 'test'}
        return {'metadata': _metadata, 'status': 'ok'}

    monkeypatch.setattr(
        support_info.SupportInfoApiClient,
        'get_additional_meta',
        _dummy_get_additional_meta,
    )

    def _dummy_randint(min_value, max_value):
        return max_value

    monkeypatch.setattr(random, 'randint', _dummy_randint)

    @patch_aiohttp_session('http://test-translate-url/', 'GET')
    def _dummy_translate_request(*args, **kwargs):
        return response_mock(json={'code': '200', 'lang': lang})

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert url == supportai_api_service.url + expected_autoreply_url

        response = {}
        if autoreply_time:
            response.setdefault('defer', {})
            response['defer']['time_sec'] = autoreply_time
        return response_mock(json=response)

    if call_predispatch:
        await stq_task.chatterbox_predispatch(cbox.app, task_id)
    else:
        await cbox.db.support_chatterbox.find_one_and_update(
            filter={'_id': task_id}, update={'$set': metadata},
        )
        await stq_task.post_update(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})

    assert task['status'] == expected_status
    assert 'tags' in task
    assert set(task['tags']) == set(expected_tags)

    if expected_defer:
        assert stq.chatterbox_common_autoreply_queue.times_called == 1
        call = stq.chatterbox_common_autoreply_queue.next_call()
        assert call['args'][:2] == [
            {'$oid': str(task['_id'])},
            {'defer': {'defer_time': expected_time}},
        ]
    else:
        assert not stq.chatterbox_common_autoreply_queue.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'second': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
    },
    CHATTERBOX_FORWARD_AUTOREPLY=True,
    CHATTERBOX_AUTOREPLY_USE_EVENT_TYPE=True,
    CHATTERBOX_DEFER_AUTOREPLY={
        'enabled': True,
        'max_count': 3,
        'max_time_sec': 600,
        'default_time_sec': 300,
    },
    CHATTERBOX_AUTOREPLY_ML_META={
        'top_most_probable_macros': 'ml_suggestions',
        'foodtech_ml': 'foodtech_meta',
    },
)
@pytest.mark.parametrize(
    (
        'task_id',
        'autoreply_status',
        'autoreply_meta',
        'expected_meta',
        'expected_status',
        'expected_autoreply_url',
    ),
    [
        (
            PREDISPATCH_TASK_ID,
            ['close'],
            {
                'features': {
                    'features': [
                        {
                            'key': 'top_most_probable_macros',
                            'value': [1, 2, 3, 4, 5],
                        },
                    ],
                },
            },
            {
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'user_phone': '+74950000001',
                'task_language': 'ru',
                'ml_request_id': UUID,
                'ml_suggestions': [1, 2, 3, 4, 5],
                'antifraud_rules': ['taxi_free_trips'],
                'check_autoreply_count': 1,
                'autoreply_count_dismiss': 1,
                'use_autoreply_count': 1,
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'predispatch',
            },
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
        ),
        (
            PREDISPATCH_TASK_ID,
            [],
            {
                'features': {
                    'features': [
                        {
                            'key': 'top_most_probable_macros',
                            'value': [1, 2, 3, 4, 5],
                        },
                    ],
                },
            },
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'user_phone': '+74950000001',
                'task_language': 'ru',
                'ml_request_id': UUID,
                'ml_suggestions': [1, 2, 3, 4, 5],
                'antifraud_rules': ['taxi_free_trips'],
            },
            'new',
            '/supportai-api/v1/support_internal',
        ),
        (
            PREDISPATCH_TASK_ID,
            ['reply', 'close'],
            {
                'features': {
                    'features': [
                        {
                            'key': 'top_most_probable_macros',
                            'value': [1, 2, 3, 4, 5],
                        },
                    ],
                },
            },
            {
                'check_autoreply_count': 1,
                'autoreply_count_close': 1,
                'use_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'user_phone': '+74950000001',
                'task_language': 'ru',
                'ml_request_id': UUID,
                'ml_suggestions': [1, 2, 3, 4, 5],
                'antifraud_rules': ['taxi_free_trips'],
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'predispatch',
            },
            'autoreply_in_progress',
            '/supportai-api/v1/support_internal',
        ),
        (
            FOODTECH_TASK_ID,
            ['reply', 'close'],
            {
                'features': {
                    'features': [
                        {'key': 'foodtech_ml', 'value': 'foodtech_value'},
                    ],
                },
            },
            {
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
            },
            'new',
            '/supportai-api/v1/support_internal',
        ),
    ],
)
async def test_autoreply_meta(
        cbox,
        patch_aiohttp_session,
        response_mock,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_get_user_phone,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        mock_translate,
        monkeypatch,
        task_id,
        autoreply_status,
        autoreply_meta,
        expected_meta,
        expected_status,
        expected_autoreply_url,
        mock_uuid_uuid4,
):
    mock_chat_get_history(
        {
            'messages': [
                {
                    'sender': {'id': 'some_login', 'role': 'client'},
                    'text': 'some message',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                    'id': 'message_id',
                },
            ],
        },
    )
    mock_translate('ru')

    def _dummy_randint(min_value, max_value):
        return max_value

    monkeypatch.setattr(random, 'randint', _dummy_randint)

    @patch_aiohttp_session('http://test-translate-url/', 'GET')
    def _dummy_translate_request(*args, **kwargs):
        return response_mock(json={'code': '200', 'lang': 'ru'})

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert url == supportai_api_service.url + expected_autoreply_url

        response = {}
        if 'reply' in autoreply_status:
            response.setdefault('reply', {})
            response['reply']['text'] = 1
        if 'close' in autoreply_status:
            response.setdefault('close', {})
        response.update(autoreply_meta)
        return response_mock(json=response)

    await stq_task.chatterbox_predispatch(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})

    assert task['status'] == expected_status
    assert task['meta_info'] == expected_meta


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_AUTOREPLY_USE_EVENT_TYPE=True,
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'second': {
            'name': '2 · DM РФ',
            'priority': 2,
            'autoreply': True,
            'conditions': {'line': 'second'},
        },
    },
    PASS_STATUS_IF_FAIL_TO_STQ_CHATTERBOX_AUTOREPLY=True,
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
    [
        'nto_delay',
        'percentage',
        'task_id',
        'messages',
        'autoreply_status',
        'autoreply_macro_id',
        'autoreply_tags',
        'call_predispatch',
        'expected_tags',
        'expected_task_meta',
        'expected_meta_request',
        'expected_driver_meta_request',
        'expected_autoreply_url',
        'expected_autoreply_calls',
        'expected_stq_put_calls',
        'custom_chat_get_history',
    ],
    [
        (
            False,
            0,
            PREDISPATCH_TASK_ID,
            ['мне оторвали ногу'],
            ['reply', 'close'],
            1,
            [],
            True,
            [
                'lang_ru',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            ],
            {
                'check_autoreply_count': 1,
                'autoreply_count_close': 1,
                'use_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'task_language': 'ru',
                'antifraud_rules': ['taxi_free_trips'],
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'predispatch',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a5',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'task_language', 'value': 'ru'},
                        {
                            'key': 'antifraud_rules',
                            'value': ['taxi_free_trips'],
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'second'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            None,
        ),
        pytest.param(
            False,
            0,
            PREDISPATCH_TASK_ID,
            ['мне оторвали ногу'],
            None,
            None,
            [],
            True,
            ['lang_none'],
            {
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'user_phone': '+74950000001',
            },
            None,
            None,
            None,
            [],
            [],
            None,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
                        'client': {'__default__': True},
                    },
                ),
            ],
        ),
        (
            False,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу'],
            ['reply', 'close'],
            1,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'check_autoreply_count': 1,
                'autoreply_count_close': 1,
                'use_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'calls': [],
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a6'},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу'],
            ['reply', 'close'],
            3,
            [],
            False,
            [
                'autoreply_macro_missing',
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'check_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'calls': [],
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
            None,
        ),
        (
            False,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу'],
            [],
            1,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'check_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'calls': [],
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
            None,
        ),
        (
            False,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу'],
            ['reply', 'close'],
            'abc',
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'check_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'calls': [],
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
            None,
        ),
        (
            False,
            0,
            NEW_TASK_ID,
            ['мне оторвали ногу'],
            ['reply', 'close'],
            1,
            [],
            False,
            [],
            {
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'calls': [],
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [],
            [],
            None,
        ),
        (
            False,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу', 'и ещё одну'],
            ['reply', 'close'],
            1,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'autoreply_count_close': 1,
                'use_autoreply_count': 1,
                'check_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'calls': [],
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'и ещё одну',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу\nи ещё одну',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a6'},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу', 'и ещё одну'],
            ['reply', 'close'],
            1,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'autoreply_count_close': 1,
                'calls': [],
                'check_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'use_autoreply_count': 1,
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'и ещё одну',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу\nи ещё одну',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a6'},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу', 'и ещё одну'],
            ['close'],
            None,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'autoreply_count_dismiss': 1,
                'use_autoreply_count': 1,
                'check_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'calls': [],
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'и ещё одну',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу\nи ещё одну',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a6'},
                        {'dismiss': {}},
                        'client',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            True,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу', 'и ещё одну'],
            ['close'],
            None,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'autoreply_count_dismiss': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'calls': [],
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'и ещё одну',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу\nи ещё одну',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a6'},
                        {'dismiss': {}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            True,
            100,
            AUTOREPLY_CANCELLED_TASK_ID,
            ['мне оторвали ногу', 'и ещё одну'],
            ['close'],
            None,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'autoreply_count_dismiss': 1,
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'use_autoreply_count': 1,
                'user_phone': '+74950000001',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a9',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'и ещё одну',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу\nи ещё одну',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a9'},
                        {'dismiss': {}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            True,
            100,
            NTO_TASK_ID,
            ['мне оторвали ногу', 'и ещё одну'],
            ['reply', 'close'],
            1,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'autoreply_count_close': 1,
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'use_autoreply_count': 1,
                'user_phone': '+74950000001',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2ab',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'и ещё одну',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу\nи ещё одну',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2ab'},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            DRIVER_EXTRA_TASK_ID,
            ['мне оторвали ногу'],
            ['reply', 'close'],
            1,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'use_autoreply_project_driver',
            ],
            {
                'autoreply_count_close': 1,
                'block_reasons': ['DriverPointsRateBlockTemp'],
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'driver_phone': '+74950000000',
                'locale': 'ru',
                'tariff': 'econom',
                'ticket_subject': 'Я не вижу новые заказы',
                'use_autoreply_count': 1,
                'zendesk_profile': 'yataxi',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a8',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {
                            'key': 'block_reasons',
                            'value': ['DriverPointsRateBlockTemp'],
                        },
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'driver_phone', 'value': '+74950000000'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'tariff', 'value': 'econom'},
                        {
                            'key': 'ticket_subject',
                            'value': 'Я не вижу новые заказы',
                        },
                        {'key': 'zendesk_profile', 'value': 'yataxi'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'driver'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 0},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a8'},
                        {'close': {'macro_id': 1}},
                        'driver',
                    ],
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            NEW_TASK_ID,
            ['мне оторвали ногу'],
            ['reply', 'close'],
            1,
            [],
            False,
            [
                'use_ml_autoreply',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
            ],
            {
                'autoreply_count_close': 1,
                'calls': [],
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'use_autoreply_count': 1,
                'user_phone': '+74950000001',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': 123,
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': True},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a6'},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            {
                'messages': [
                    {
                        'id': 123,
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'мне оторвали ногу',
                        'metadata': {
                            'created': '2018-05-05T15:34:56',
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'mimetype': 'image/png',
                                    'size': 35188,
                                    'source': 'mds',
                                    'name': 'screenshot.jpg',
                                },
                                {'id': '123', 'mimetype': 'text/plain'},
                            ],
                        },
                    },
                ],
            },
        ),
        (
            False,
            100,
            DRIVER_EXTRA_TASK_ID,
            [],
            ['reply', 'close'],
            1,
            [],
            False,
            ['check_ml_autoreply', 'check_autoreply_project_driver'],
            {
                'check_autoreply_count': 1,
                'driver_phone': '+74950000000',
                'zendesk_profile': 'yataxi',
                'city': 'Moscow',
                'country': 'rus',
                'tariff': 'econom',
                'ticket_subject': 'Я не вижу новые заказы',
                'block_reasons': ['DriverPointsRateBlockTemp'],
                'locale': 'ru',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a8',
                    'dialog': {'messages': []},
                    'features': [
                        {
                            'key': 'block_reasons',
                            'value': ['DriverPointsRateBlockTemp'],
                        },
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'driver_phone', 'value': '+74950000000'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'tariff', 'value': 'econom'},
                        {
                            'key': 'ticket_subject',
                            'value': 'Я не вижу новые заказы',
                        },
                        {'key': 'zendesk_profile', 'value': 'yataxi'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'driver'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': ''},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 0},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
            None,
        ),
        (
            False,
            100,
            OPTEUM_TASK_ID,
            ['сообщение'],
            ['reply', 'close'],
            1,
            ['ml_tag'],
            True,
            [
                'check_autoreply_project_opteum',
                'check_ml_autoreply',
                'ml_tag',
                'lang_ru',
                'use_autoreply_project_opteum',
                'use_ml_autoreply',
            ],
            {
                'autoreply_count_close': 1,
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'some': 'metadata',
                'task_language': 'ru',
                'use_autoreply_count': 1,
                'user_phone': '+74950000001',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'predispatch',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': '00000000000040008000000000000000',
                    'task_language': 'ru',
                    'user_phone': '+74950000001',
                },
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': '00000000000040008000000000000000',
                    'some': 'metadata',
                    'task_language': 'ru',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2b6',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': 123,
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'opteum'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': True},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2b6'},
                        {'close': {'macro_id': 1}},
                        'opteum',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            {
                'messages': [
                    {
                        'id': 123,
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': 'сообщение',
                        'metadata': {
                            'created': '2018-05-05T15:34:56',
                            'attachments': [
                                {
                                    'id': 'attachment_id',
                                    'mimetype': 'image/png',
                                    'size': 35188,
                                    'source': 'mds',
                                    'name': 'screenshot.jpg',
                                },
                                {'id': '123', 'mimetype': 'text/plain'},
                            ],
                        },
                    },
                ],
            },
        ),
        (
            False,
            100,
            OPTEUM_NEW_TASK_ID,
            ['сообщение'],
            ['reply', 'close'],
            1,
            ['ml_tag'],
            False,
            [
                'check_autoreply_project_opteum',
                'check_ml_autoreply',
                'ml_tag',
                'use_autoreply_project_opteum',
                'use_ml_autoreply',
            ],
            {
                'autoreply_count_close': 1,
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'some': 'metadata',
                'use_autoreply_count': 1,
                'user_phone': '+74950000001',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': '00000000000040008000000000000000',
                    'user_phone': '+74950000001',
                    'some': 'old_value',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2b7',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'opteum'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2b7'},
                        {'close': {'macro_id': 1}},
                        'opteum',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            FOODTECH_TASK_ID,
            ['сообщение'],
            ['reply'],
            1,
            ['ml_tag'],
            False,
            [
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'ml_tag',
                'use_autoreply_project_eats_client',
                'use_ml_autoreply',
            ],
            {
                'autoreply_count_comment': 1,
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'lavka',
                'service': 'grocery',
                'use_autoreply_count': 1,
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {'comment': {'macro_id': 1}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            FOODTECH_TASK_ID,
            ['сообщение'],
            ['reply', 'close'],
            1,
            ['ml_tag'],
            False,
            [
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'ml_tag',
                'use_autoreply_project_eats_client',
                'use_ml_autoreply',
            ],
            {
                'autoreply_count_close': 1,
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'lavka',
                'service': 'grocery',
                'use_autoreply_count': 1,
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'new',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {'close': {'macro_id': 1}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'new'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            FOODTECH_TASK_ID,
            ['сообщение'],
            [],
            1,
            ['ml_tag'],
            False,
            [
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'ml_tag',
                'use_autoreply_project_eats_client',
                'use_ml_autoreply',
            ],
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [],
            None,
        ),
        (
            False,
            100,
            FOODTECH_CLIENT_TASK_ID,
            ['сообщение'],
            [],
            1,
            ['ml_tag'],
            False,
            [
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'ml_tag',
                'use_autoreply_project_client',
                'use_ml_autoreply',
            ],
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'extra1': {'some': 'field'},
                'extra2': ['1', '2', '3'],
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c1',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'extra2', 'value': ['1', '2', '3']},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
            None,
        ),
        (
            False,
            100,
            PERSONAL_CLIENT_TASK_ID,
            ['сообщение'],
            ['reply', 'close'],
            1,
            ['ml_tag'],
            True,
            [
                'ml_tag',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_autoreply_project_client',
                'use_ml_autoreply',
                'lang_ru',
            ],
            {
                'antifraud_rules': ['taxi_free_trips'],
                'autoreply_count_close': 1,
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'locale': 'ru',
                'some': 'old_value',
                'task_language': 'ru',
                'use_autoreply_count': 1,
                'user_phone_pd_id': 'phone_pd_id_1',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'predispatch',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c4',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {
                            'key': 'driver_license_pd_id',
                            'value': 'driver_license_pd_id_1',
                        },
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'some', 'value': 'old_value'},
                        {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_1'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'task_language', 'value': 'ru'},
                        {
                            'key': 'antifraud_rules',
                            'value': ['taxi_free_trips'],
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {
                            'key': 'driver_license',
                            'value': 'some_driver_license',
                        },
                        {'key': 'user_phone', 'value': '+79999999999'},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c4'},
                        {'close': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            None,
        ),
        (
            False,
            100,
            PERSONAL_DRIVER_TASK_ID,
            ['сообщение'],
            ['reply', 'close'],
            1,
            ['ml_tag'],
            True,
            [
                'use_ml_autoreply',
                'check_autoreply_project_driver',
                'check_ml_autoreply',
                'ml_tag',
                'use_autoreply_project_driver',
                'lang_ru',
            ],
            {
                'autoreply_count_close': 1,
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'locale': 'ru',
                'some': 'old_value',
                'task_language': 'ru',
                'use_autoreply_count': 1,
                'user_phone_pd_id': 'phone_pd_id_1',
                'latest_stq_autoreply_task_id': UUID,
                'task_status_before_autoreply': 'predispatch',
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c3',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {
                            'key': 'driver_license_pd_id',
                            'value': 'driver_license_pd_id_1',
                        },
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'some', 'value': 'old_value'},
                        {'key': 'user_phone_pd_id', 'value': 'phone_pd_id_1'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'driver'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {
                            'key': 'driver_license',
                            'value': 'some_driver_license',
                        },
                        {'key': 'user_phone', 'value': '+79999999999'},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c3'},
                        {'close': {'macro_id': 1}},
                        'driver',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'reopened'},
                },
            ],
            None,
        ),
        pytest.param(
            False,
            0,
            PREDISPATCH_TASK_ID,
            ['мне оторвали ногу'],
            ['reply', 'close'],
            1,
            [],
            True,
            ['lang_ru'],
            {
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'task_language': 'ru',
                'antifraud_rules': ['taxi_free_trips'],
            },
            None,
            None,
            '/supportai-api/v1/support_internal',
            [],
            [],
            None,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_AUTOREPLY={
                        'client': {
                            'use_percentage': 100,
                            'check_percentage': 0,
                            'conditions': {'chat_type': {'#in': ['client']}},
                            'langs': ['ru'],
                            'delay_range': [300, 600],
                            'project_id': 'client',
                            'event_type': 'client',
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_autoreply(
        cbox,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_translate,
        mock_get_user_phone,
        mock_randint,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        stq,
        patch_aiohttp_session,
        response_mock,
        nto_delay,
        percentage,
        task_id,
        messages,
        autoreply_status,
        autoreply_macro_id,
        autoreply_tags,
        call_predispatch,
        expected_tags,
        expected_task_meta,
        expected_meta_request,
        expected_driver_meta_request,
        expected_autoreply_url,
        expected_autoreply_calls,
        expected_stq_put_calls,
        custom_chat_get_history,
        mock_uuid_uuid4,
        mock_personal,
):
    cbox.app.config.CHATTERBOX_AUTOREPLY_NTO_DELAY = nto_delay
    cbox.app.config.CHATTERBOX_REOPEN_AUTOREPLY = {
        'percentage': percentage,
        'statuses': ['reopened', 'new', 'forwarded', 'routing', 'deferred'],
    }
    if custom_chat_get_history:
        mock_chat_get_history(custom_chat_get_history)
    else:
        mock_chat_get_history(
            {
                'messages': [
                    {
                        'id': str(index),
                        'sender': {'id': 'some_login', 'role': 'client'},
                        'text': message,
                        'metadata': {'created': '2018-05-05T15:34:56'},
                    }
                    for index, message in enumerate(messages)
                ],
            },
        )
    mock_translate('ru')

    support_info_service = discovery.find_service('support_info')

    @patch_aiohttp_session(
        support_info_service.url + '/v1/get_additional_meta', 'POST',
    )
    def _dummy_autoreply_meta(method, url, **kwargs):
        assert method == 'post'
        response = {'metadata': {'some': 'metadata'}, 'status': 'ok'}
        return response_mock(json=response)

    @patch_aiohttp_session(
        support_info_service.url + '/v1/autoreply/driver_meta', 'POST',
    )
    def _dummy_autoreply_driver_meta(method, url, **kwargs):
        assert method == 'post'
        response = {'metadata': {'some': 'metadata'}, 'status': 'ok'}
        return response_mock(json=response)

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert url == supportai_api_service.url + expected_autoreply_url

        response = {'tag': {'add': autoreply_tags}}
        if 'reply' in autoreply_status:
            response.setdefault('reply', {})
            response['reply']['text'] = autoreply_macro_id
        if 'close' in autoreply_status:
            response.setdefault('close', {})
        return response_mock(json=response)

    if call_predispatch:
        await stq_task.chatterbox_predispatch(cbox.app, task_id)
    else:
        await cbox.db.support_chatterbox.find_one_and_update(
            filter={'_id': task_id},
            update={'$set': {'meta_info.ml_request_id': UUID}},
        )
        await stq_task.post_update(cbox.app, task_id)

    updated_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert set(updated_task['tags']) == set(expected_tags)
    assert updated_task['meta_info']['ml_request_id'] == UUID
    updated_task['meta_info'].pop('ml_request_id')
    assert updated_task['meta_info'] == expected_task_meta

    if expected_driver_meta_request:
        assert (
            _dummy_autoreply_driver_meta.calls[0]['kwargs']['json']
            == expected_driver_meta_request
        )
    elif expected_meta_request:
        assert (
            _dummy_autoreply_meta.calls[0]['kwargs']['json']
            == expected_meta_request
        )
    else:
        assert not _dummy_autoreply_meta.calls

    autoreply_calls_ai = [
        call['kwargs']['json'] for call in _dummy_autoreply_ai.calls
    ]
    autoreply_calls = autoreply_calls_ai
    assert autoreply_calls == expected_autoreply_calls

    stq_put_calls = [
        stq.chatterbox_common_autoreply_queue.next_call()
        for _ in range(stq.chatterbox_common_autoreply_queue.times_called)
    ]
    for call in stq_put_calls:
        del call['id']
        del call['queue']
        del call['kwargs']['log_extra']
        del call['kwargs']['request_id']
    assert stq_put_calls == expected_stq_put_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'second': {
            'conditions': {'fields.ml_predicted_line': 'second'},
            'name': '2',
            'priority': 1,
            'autoreply': True,
        },
        'third': {
            'conditions': {'fields.ml_predicted_line': 'third'},
            'name': '3',
            'priority': 1,
        },
        'first_without_autoreply': {
            'name': 'kek',
            'priority': 2,
            'autoreply': False,
        },
        'online': {
            'conditions': {},
            'name': '4',
            'priority': 4,
            'mode': 'online',
        },
    },
    CHATTERBOX_POST_UPDATE_ROUTING_PERCENTAGE=100,
    CHATTERBOX_CHANGE_LINE_STATUSES={
        'forwarded': 'forwarded',
        'new': 'new',
        'predispatch': 'new',
    },
    PASS_STATUS_IF_FAIL_TO_STQ_CHATTERBOX_AUTOREPLY=True,
    CHATTERBOX_AUTOREPLY={
        'client': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['client']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'client',
            'event_type': 'client',
        },
        'messenger': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['messenger']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'messenger',
            'event_type': 'messenger',
        },
        'driver': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['driver']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'driver',
            'event_type': 'driver',
            'predispatch_routing': True,
        },
        'eda': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {
                'chat_type': {
                    '#in': ['client', 'client_eats', 'client_eats_app'],
                },
            },
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'eats_client',
            'event_type': 'eats',
            'need_driver_meta': True,
            'predispatch_routing': True,
        },
    },
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
    CHATTERBOX_AUTOREPLY_ML_META={
        'top_most_probable_macros': 'ml_suggestions',
        'foodtech_ml': 'foodtech_meta',
    },
)
@pytest.mark.parametrize(
    [
        'task_id',
        'messages',
        'autoreply_answer',
        'call_predispatch',
        'expected_tags',
        'expected_task_line',
        'expected_task_meta',
        'expected_driver_meta_request',
        'expected_autoreply_url',
        'expected_autoreply_calls',
        'expected_stq_put_calls',
    ],
    [
        (
            PREDISPATCH_TASK_ID,
            ['мне оторвали ногу'],
            {'reply': {'text': 1}},
            True,
            [
                'use_autoreply_project_client',
                'check_autoreply_project_client',
                'lang_ru',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'use_autoreply_count': 1,
                'autoreply_count_comment': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'predispatch',
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'task_language': 'ru',
                'antifraud_rules': ['taxi_free_trips'],
                'latest_stq_autoreply_task_id': UUID,
            },
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2a5',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {
                            'key': 'antifraud_rules',
                            'value': ['taxi_free_trips'],
                        },
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'second'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2a5'},
                        {'comment': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            MESSENGER_PREDISPATCH_TASK_ID,
            ['мне оторвали ногу'],
            {'reply': {'text': 1}},
            True,
            [
                'use_autoreply_project_messenger',
                'check_autoreply_project_messenger',
                'lang_ru',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'use_autoreply_count': 1,
                'autoreply_count_comment': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'predispatch',
                'user_phone': '+74950000001',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'task_language': 'ru',
                'latest_stq_autoreply_task_id': UUID,
            },
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c5',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'messenger'},
                        {'key': 'line', 'value': 'second'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c5'},
                        {'comment': {'macro_id': 1}},
                        'messenger',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            DRIVER_ROUTING_TASK_ID,
            ['мне оторвали ногу'],
            {'reply': {'text': 1}},
            True,
            [
                'use_autoreply_project_driver',
                'check_autoreply_project_driver',
                'lang_ru',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_comment': 1,
                'task_status_before_autoreply': 'predispatch',
                'block_reasons': ['DriverPointsRateBlockTemp'],
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'driver_phone': '+74950000000',
                'locale': 'ru',
                'tariff': 'econom',
                'task_language': 'ru',
                'ticket_subject': 'Я не вижу новые заказы',
                'use_autoreply_count': 1,
                'zendesk_profile': 'yataxi',
                'latest_stq_autoreply_task_id': UUID,
            },
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2b0',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {
                            'key': 'block_reasons',
                            'value': ['DriverPointsRateBlockTemp'],
                        },
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'driver_phone', 'value': '+74950000000'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'tariff', 'value': 'econom'},
                        {
                            'key': 'ticket_subject',
                            'value': 'Я не вижу новые заказы',
                        },
                        {'key': 'zendesk_profile', 'value': 'yataxi'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'driver'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 0},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2b0'},
                        {'comment': {'macro_id': 1}},
                        'driver',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_PREDISPATCH_TASK_ID,
            ['мне оторвали ногу'],
            {'forward': {'line': 'second'}},
            True,
            [
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'lang_ru',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'ml_predicted_line': 'second',
                'order_type': 'native',
                'service': 'eats',
                'some': 'metadata',
                'task_language': 'ru',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
            },
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c2',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'мне оторвали ногу',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {
                            'key': 'comment_lowercased',
                            'value': 'мне оторвали ногу',
                        },
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
        ),
        (
            FOODTECH_CLIENT_TASK_ID,
            ['сообщение'],
            {'reply': {'text': 1}, 'tag': {'add': ['ml_tag_test']}},
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_client',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'use_autoreply_count': 1,
                'autoreply_count_comment': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'extra1': {'some': 'field'},
                'extra2': ['1', '2', '3'],
                'latest_stq_autoreply_task_id': UUID,
            },
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c1',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'extra2', 'value': ['1', '2', '3']},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c1'},
                        {'comment': {'macro_id': 1}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_CLIENT_TASK_ID,
            ['сообщение'],
            {'close': {}, 'tag': {'add': ['ml_tag_test']}},
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_client',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'use_autoreply_count': 1,
                'autoreply_count_dismiss': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'extra1': {'some': 'field'},
                'extra2': ['1', '2', '3'],
                'latest_stq_autoreply_task_id': UUID,
            },
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c1',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'extra2', 'value': ['1', '2', '3']},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c1'},
                        {'dismiss': {}},
                        'client',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_CLIENT_TASK_ID,
            ['сообщение'],
            {
                'close': {},
                'reply': {'text': 2},
                'tag': {'add': ['ml_tag_test']},
            },
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_client',
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_close': 1,
                'use_autoreply_count': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'extra1': {'some': 'field'},
                'extra2': ['1', '2', '3'],
                'latest_stq_autoreply_task_id': UUID,
            },
            None,
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c1',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'extra2', 'value': ['1', '2', '3']},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c1'},
                        {'close': {'macro_id': 2}},
                        'client',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'defer': {'time_sec': 5},
                'tag': {'add': ['ml_tag_test']},
            },
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'use_autoreply_count': 1,
                'autoreply_count_comment': 1,
                'autoreply_count_defer': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'locale': 'ru',
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
                'latest_stq_autoreply_task_id': UUID,
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {
                            'comment': {'macro_id': 2},
                            'defer': {'defer_time': 5},
                        },
                        'eats',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'close': {},
                'defer': {'time_sec': 5},
                'tag': {'add': ['ml_tag_test']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [],
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'close': {},
                'defer': {'time_sec': 5},
                'tag': {'add': ['ml_tag_test']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [],
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'defer': {'time_sec': 5},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'action_communicate',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_communicate': 1,
                'autoreply_count_defer': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
                'latest_stq_autoreply_task_id': UUID,
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {
                            'communicate': {'macro_id': 2},
                            'defer': {'defer_time': 5},
                        },
                        'eats',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'action_communicate',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_communicate': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
                'latest_stq_autoreply_task_id': UUID,
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {'communicate': {'macro_id': 2}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_PREDISPATCH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'defer': {'time_sec': 5},
                'forward': {'line': 'second'},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            True,
            [
                'ml_tag_test',
                'action_communicate',
                'lang_ru',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'autoreply_count_communicate': 1,
                'autoreply_count_defer': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'predispatch',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'task_language': 'ru',
                'ml_suggestions': [1, 2, 3],
                'ml_predicted_line': 'second',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
                'latest_stq_autoreply_task_id': UUID,
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'native',
                    'service': 'eats',
                    'task_language': 'ru',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c2',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c2'},
                        {
                            'communicate': {'macro_id': 2},
                            'defer': {'defer_time': 5},
                        },
                        'eats',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_PREDISPATCH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'forward': {'line': 'second'},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            True,
            [
                'ml_tag_test',
                'action_communicate',
                'lang_ru',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'autoreply_count_communicate': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'predispatch',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'task_language': 'ru',
                'ml_suggestions': [1, 2, 3],
                'ml_predicted_line': 'second',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
                'latest_stq_autoreply_task_id': UUID,
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'native',
                    'service': 'eats',
                    'task_language': 'ru',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c2',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c2'},
                        {'communicate': {'macro_id': 2}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'action_communicate',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [],
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'defer': {'time_sec': 5},
                'tag': {'add': ['ml_tag_test']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_comment': 1,
                'autoreply_count_defer': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
                'latest_stq_autoreply_task_id': UUID,
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {
                            'comment': {'macro_id': 2},
                            'defer': {'defer_time': 5},
                        },
                        'eats',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'close': {},
                'reply': {'text': 2},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'action_communicate',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_close': 1,
                'use_autoreply_count': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
                'latest_stq_autoreply_task_id': UUID,
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {'close': {'macro_id': 2}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
        ),
        (
            DRIVER_ML_ROUTING_TASK_ID,
            ['форфард', ''],
            {'forward': {'line': 'third'}},
            True,
            [
                'lang_ru',
                'check_ml_autoreply',
                'check_autoreply_project_driver',
            ],
            'third',
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'driver_phone': '+74950000000',
                'locale': 'ru',
                'tariff': 'econom',
                'ticket_subject': 'Я не вижу новые заказы',
                'zendesk_profile': 'yataxi',
                'ml_predicted_line': 'third',
                'task_language': 'ru',
            },
            {},
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c8',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'форфард',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': '',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'driver_phone', 'value': '+74950000000'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'tariff', 'value': 'econom'},
                        {
                            'key': 'ticket_subject',
                            'value': 'Я не вижу новые заказы',
                        },
                        {'key': 'zendesk_profile', 'value': 'yataxi'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'driver'},
                        {'key': 'line', 'value': 'first_without_autoreply'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'форфард\n'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 0},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
        ),
    ],
)
async def test_common_autoreply(
        cbox,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_get_race_chat,
        mock_translate,
        mock_get_user_phone,
        mock_randint,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        stq,
        patch_aiohttp_session,
        response_mock,
        task_id,
        messages,
        autoreply_answer,
        call_predispatch,
        expected_tags,
        expected_task_line,
        expected_task_meta,
        expected_driver_meta_request,
        expected_autoreply_url,
        expected_autoreply_calls,
        expected_stq_put_calls,
        mock_uuid_uuid4,
        mock_personal,
):
    mock_chat_get_history(
        {
            'messages': [
                {
                    'id': str(index),
                    'sender': {'id': 'some_login', 'role': 'client'},
                    'text': message,
                    'metadata': {'created': '2018-05-05T15:34:56'},
                }
                for index, message in enumerate(messages)
            ],
        },
    )
    mock_translate('ru')

    mock_get_race_chat()

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert url == supportai_api_service.url + expected_autoreply_url
        return response_mock(json=autoreply_answer)

    support_info_service = discovery.find_service('support_info')

    @patch_aiohttp_session(
        support_info_service.url + '/v1/autoreply/driver_meta', 'POST',
    )
    def _dummy_autoreply_driver_meta(method, url, **kwargs):
        assert method == 'post'
        response = {'metadata': {'some': 'metadata'}, 'status': 'ok'}
        return response_mock(json=response)

    if call_predispatch:
        await stq_task.chatterbox_predispatch(cbox.app, task_id)
    else:
        await cbox.db.support_chatterbox.find_one_and_update(
            filter={'_id': task_id},
            update={'$set': {'meta_info.ml_request_id': UUID}},
        )
        await stq_task.post_update(cbox.app, task_id)

    updated_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert set(updated_task['tags']) == set(expected_tags)
    assert updated_task['meta_info']['ml_request_id'] == UUID
    updated_task['meta_info'].pop('ml_request_id')
    assert updated_task['meta_info'] == expected_task_meta
    assert updated_task['line'] == expected_task_line

    if expected_driver_meta_request:
        assert (
            _dummy_autoreply_driver_meta.calls[0]['kwargs']['json']
            == expected_driver_meta_request
        )

    autoreply_calls_ai = [
        call['kwargs']['json'] for call in _dummy_autoreply_ai.calls
    ]
    assert autoreply_calls_ai == expected_autoreply_calls

    stq_put_calls = [
        stq.chatterbox_common_autoreply_queue.next_call()
        for _ in range(stq.chatterbox_common_autoreply_queue.times_called)
    ]
    for call in stq_put_calls:
        del call['id']
        del call['kwargs']['log_extra']
        del call['kwargs']['request_id']
    assert stq_put_calls == expected_stq_put_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1 · DM РФ', 'priority': 3, 'autoreply': True},
        'second': {
            'conditions': {'fields.ml_predicted_line': 'second'},
            'name': '2',
            'priority': 1,
            'autoreply': True,
        },
        'third': {
            'conditions': {'fields.ml_predicted_line': 'third'},
            'name': '3',
            'priority': 1,
        },
        'first_without_autoreply': {
            'name': 'kek',
            'priority': 2,
            'autoreply': False,
        },
        'online': {
            'conditions': {},
            'name': '4',
            'priority': 4,
            'mode': 'online',
        },
    },
    CHATTERBOX_POST_UPDATE_ROUTING_PERCENTAGE=100,
    CHATTERBOX_CHANGE_LINE_STATUSES={
        'forwarded': 'forwarded',
        'new': 'new',
        'predispatch': 'new',
    },
    PASS_STATUS_IF_FAIL_TO_STQ_CHATTERBOX_AUTOREPLY=True,
    CHATTERBOX_AUTOREPLY={
        'client': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['client']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'client',
            'event_type': 'client',
        },
        'messenger': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['messenger']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'messenger',
            'event_type': 'messenger',
        },
        'driver': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {'chat_type': {'#in': ['driver']}},
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'driver',
            'event_type': 'driver',
            'predispatch_routing': True,
        },
        'eda': {
            'use_percentage': 100,
            'check_percentage': 100,
            'conditions': {
                'chat_type': {
                    '#in': ['client', 'client_eats', 'client_eats_app'],
                },
            },
            'langs': ['ru'],
            'delay_range': [300, 600],
            'project_id': 'eats_client',
            'event_type': 'eats',
            'need_driver_meta': True,
            'predispatch_routing': True,
        },
    },
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
    CHATTERBOX_AUTOREPLY_ML_META={
        'top_most_probable_macros': 'ml_suggestions',
        'foodtech_ml': 'foodtech_meta',
    },
)
@pytest.mark.parametrize(
    [
        'task_id',
        'messages',
        'autoreply_answer',
        'call_predispatch',
        'expected_tags',
        'expected_task_line',
        'expected_task_meta',
        'expected_driver_meta_request',
        'expected_autoreply_url',
        'expected_autoreply_calls',
        'expected_stq_put_calls',
        'last_message_id',
        'race_message_id',
    ],
    [
        (
            FOODTECH_PREDISPATCH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'defer': {'time_sec': 5},
                'forward': {'line': 'second'},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            True,
            [
                'ml_tag_test',
                'action_communicate',
                'lang_ru',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'autoreply_count_communicate': 1,
                'autoreply_count_defer': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'predispatch',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'latest_stq_autoreply_task_id': UUID,
                'task_language': 'ru',
                'ml_suggestions': [1, 2, 3],
                'ml_predicted_line': 'second',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'native',
                    'service': 'eats',
                    'task_language': 'ru',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c2',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c2'},
                        {
                            'communicate': {'macro_id': 2},
                            'defer': {'defer_time': 5},
                        },
                        'eats',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            'uuid1',
            'uuid1',
        ),
        (
            FOODTECH_PREDISPATCH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'defer': {'time_sec': 5},
                'forward': {'line': 'second'},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            True,
            [
                'ml_tag_test',
                'action_communicate',
                'lang_ru',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'autoreply_count_communicate': 1,
                'autoreply_count_defer': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'predispatch',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'latest_stq_autoreply_task_id': UUID,
                'task_language': 'ru',
                'ml_suggestions': [1, 2, 3],
                'ml_predicted_line': 'second',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'native',
                    'service': 'eats',
                    'task_language': 'ru',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c2',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c2'},
                        {
                            'communicate': {'macro_id': 2},
                            'defer': {'defer_time': 5},
                        },
                        'eats',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            'uuid1',
            'uuid2',
        ),
        (
            FOODTECH_PREDISPATCH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'forward': {'line': 'second'},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            True,
            [
                'ml_tag_test',
                'action_communicate',
                'lang_ru',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'autoreply_count_communicate': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'predispatch',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'latest_stq_autoreply_task_id': UUID,
                'task_language': 'ru',
                'ml_suggestions': [1, 2, 3],
                'ml_predicted_line': 'second',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'native',
                    'service': 'eats',
                    'task_language': 'ru',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c2',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c2'},
                        {'communicate': {'macro_id': 2}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            'uuid1',
            'uuid1',
        ),
        (
            FOODTECH_PREDISPATCH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'forward': {'line': 'second'},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            True,
            [
                'ml_tag_test',
                'action_communicate',
                'lang_ru',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'second',
            {
                'autoreply_count_communicate': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'predispatch',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'latest_stq_autoreply_task_id': UUID,
                'task_language': 'ru',
                'ml_suggestions': [1, 2, 3],
                'ml_predicted_line': 'second',
                'order_type': 'native',
                'service': 'eats',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'native',
                    'service': 'eats',
                    'task_language': 'ru',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c2',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'native'},
                        {'key': 'service', 'value': 'eats'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2c2'},
                        {'communicate': {'macro_id': 2}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'reopened',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            'uuid1',
            'uuid2',
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'defer': {'time_sec': 5},
                'tag': {'add': ['ml_tag_test']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_comment': 1,
                'autoreply_count_defer': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'latest_stq_autoreply_task_id': UUID,
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {
                            'comment': {'macro_id': 2},
                            'defer': {'defer_time': 5},
                        },
                        'eats',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            'uuid1',
            'uuid1',
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'reply': {'text': 2},
                'defer': {'time_sec': 5},
                'tag': {'add': ['ml_tag_test']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_comment': 1,
                'autoreply_count_defer': 1,
                'check_autoreply_count': 1,
                'use_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'latest_stq_autoreply_task_id': UUID,
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {
                            'comment': {'macro_id': 2},
                            'defer': {'defer_time': 5},
                        },
                        'eats',
                    ],
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            'uuid1',
            'uuid2',
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'close': {},
                'reply': {'text': 2},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'action_communicate',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_close': 1,
                'use_autoreply_count': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'latest_stq_autoreply_task_id': UUID,
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {'close': {'macro_id': 2}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            'uuid1',
            'uuid1',
        ),
        (
            FOODTECH_TASK_ID,
            ['сообщение'],
            {
                'close': {},
                'reply': {'text': 2},
                'tag': {'add': ['ml_tag_test', 'action_communicate']},
                'features': {
                    'top_most_probable_macros': [1, 2, 3],
                    'features': [{'key': 'foodtech_ml', 'value': 'test'}],
                },
            },
            False,
            [
                'ml_tag_test',
                'action_communicate',
                'use_autoreply_project_eats_client',
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'use_ml_autoreply',
            ],
            'first',
            {
                'autoreply_count_close': 1,
                'use_autoreply_count': 1,
                'check_autoreply_count': 1,
                'task_status_before_autoreply': 'new',
                'city': 'Moscow',
                'country': 'rus',
                'foodtech_meta': 'test',
                'locale': 'ru',
                'latest_stq_autoreply_task_id': UUID,
                'ml_suggestions': [1, 2, 3],
                'order_type': 'lavka',
                'service': 'grocery',
                'user_id': 'user_id',
                'user_phone': '+74950000001',
                'some': 'metadata',
            },
            {
                'metadata': {
                    'city': 'Moscow',
                    'country': 'rus',
                    'locale': 'ru',
                    'ml_request_id': UUID,
                    'order_type': 'lavka',
                    'service': 'grocery',
                    'user_id': 'user_id',
                    'user_phone': '+74950000001',
                },
            },
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2bf',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'сообщение',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'order_type', 'value': 'lavka'},
                        {'key': 'service', 'value': 'grocery'},
                        {'key': 'user_id', 'value': 'user_id'},
                        {'key': 'user_phone', 'value': '+74950000001'},
                        {'key': 'ml_request_id', 'value': UUID},
                        {'key': 'some', 'value': 'metadata'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'client_eats'},
                        {'key': 'line', 'value': 'first'},
                        {'key': 'screen_attach', 'value': False},
                        {'key': 'request_id', 'value': UUID},
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'сообщение'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 59039},
                        {'key': 'last_support_action', 'value': 'communicate'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': '5b2cae5cb2682a976914c2bf'},
                        {'close': {'macro_id': 2}},
                        'eats',
                    ],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'status_if_fail': 'new',
                        'autoreply_message_id': 'uuid1',
                    },
                    'queue': 'chatterbox_common_autoreply_queue',
                },
            ],
            'uuid1',
            'uuid2',
        ),
        (
            DRIVER_ML_ROUTING_TASK_ID,
            ['форфард', ''],
            {'forward': {'line': 'third'}},
            True,
            [
                'lang_ru',
                'check_ml_autoreply',
                'check_autoreply_project_driver',
            ],
            'third',
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'driver_phone': '+74950000000',
                'locale': 'ru',
                'tariff': 'econom',
                'ticket_subject': 'Я не вижу новые заказы',
                'zendesk_profile': 'yataxi',
                'ml_predicted_line': 'third',
                'task_language': 'ru',
            },
            {},
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c8',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'форфард',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': '',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'driver_phone', 'value': '+74950000000'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'tariff', 'value': 'econom'},
                        {
                            'key': 'ticket_subject',
                            'value': 'Я не вижу новые заказы',
                        },
                        {'key': 'zendesk_profile', 'value': 'yataxi'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'driver'},
                        {'key': 'line', 'value': 'first_without_autoreply'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'форфард\n'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 0},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
            'uudi1',
            'uuid1',
        ),
        (
            DRIVER_ML_ROUTING_TASK_ID,
            ['форфард', ''],
            {'forward': {'line': 'third'}},
            True,
            [
                'lang_ru',
                'check_ml_autoreply',
                'check_autoreply_project_driver',
            ],
            'third',
            {
                'check_autoreply_count': 1,
                'city': 'Moscow',
                'country': 'rus',
                'driver_phone': '+74950000000',
                'locale': 'ru',
                'tariff': 'econom',
                'ticket_subject': 'Я не вижу новые заказы',
                'zendesk_profile': 'yataxi',
                'ml_predicted_line': 'third',
                'task_language': 'ru',
            },
            {},
            '/supportai-api/v1/support_internal',
            [
                {
                    'chat_id': '5b2cae5cb2682a976914c2c8',
                    'dialog': {
                        'messages': [
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '0',
                                'language': 'ru',
                                'reply_to': [],
                                'text': 'форфард',
                            },
                            {
                                'author': 'user',
                                'created': '2018-05-05T15:34:56Z',
                                'id': '1',
                                'language': 'ru',
                                'reply_to': [],
                                'text': '',
                            },
                        ],
                    },
                    'features': [
                        {'key': 'city', 'value': 'Moscow'},
                        {'key': 'country', 'value': 'rus'},
                        {'key': 'driver_phone', 'value': '+74950000000'},
                        {'key': 'locale', 'value': 'ru'},
                        {'key': 'tariff', 'value': 'econom'},
                        {
                            'key': 'ticket_subject',
                            'value': 'Я не вижу новые заказы',
                        },
                        {'key': 'zendesk_profile', 'value': 'yataxi'},
                        {
                            'key': 'ml_request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'task_language', 'value': 'ru'},
                        {'key': 'request_repeated', 'value': True},
                        {'key': 'chat_type', 'value': 'driver'},
                        {'key': 'line', 'value': 'first_without_autoreply'},
                        {'key': 'screen_attach', 'value': False},
                        {
                            'key': 'request_id',
                            'value': '00000000000040008000000000000000',
                        },
                        {'key': 'is_reopen', 'value': False},
                        {'key': 'number_of_reopens', 'value': 0},
                        {'key': 'all_tags', 'value': []},
                        {'key': 'last_message_tags', 'value': []},
                        {'key': 'comment_lowercased', 'value': 'форфард\n'},
                        {'key': 'number_of_orders', 'value': 0},
                        {'key': 'minutes_from_order_creation', 'value': 0},
                        {'key': 'last_support_action', 'value': 'empty'},
                    ],
                },
            ],
            [],
            'uuid1',
            'uuid2',
        ),
    ],
)
async def test_prevent_race_by_saving_autoreply_message(
        cbox,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_get_race_chat,
        mock_translate,
        mock_get_user_phone,
        mock_randint,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        stq,
        patch_aiohttp_session,
        response_mock,
        task_id,
        messages,
        autoreply_answer,
        call_predispatch,
        expected_tags,
        expected_task_line,
        expected_task_meta,
        expected_driver_meta_request,
        expected_autoreply_url,
        expected_autoreply_calls,
        expected_stq_put_calls,
        last_message_id,
        race_message_id,
        mock_uuid_uuid4,
        mock_personal,
):
    mock_chat_get_history(
        {
            'messages': [
                {
                    'id': str(index),
                    'sender': {'id': 'some_login', 'role': 'client'},
                    'text': message,
                    'metadata': {'created': '2018-05-05T15:34:56'},
                }
                for index, message in enumerate(messages)
            ],
        },
    )
    mock_translate('ru')

    mock_get_race_chat(last_message_id, race_message_id)

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert url == supportai_api_service.url + expected_autoreply_url
        return response_mock(json=autoreply_answer)

    support_info_service = discovery.find_service('support_info')

    @patch_aiohttp_session(
        support_info_service.url + '/v1/autoreply/driver_meta', 'POST',
    )
    def _dummy_autoreply_driver_meta(method, url, **kwargs):
        assert method == 'post'
        response = {'metadata': {'some': 'metadata'}, 'status': 'ok'}
        return response_mock(json=response)

    if call_predispatch:
        await stq_task.chatterbox_predispatch(cbox.app, task_id)
    else:
        await cbox.db.support_chatterbox.find_one_and_update(
            filter={'_id': task_id},
            update={'$set': {'meta_info.ml_request_id': UUID}},
        )
        await stq_task.post_update(cbox.app, task_id)

    updated_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert set(updated_task['tags']) == set(expected_tags)
    assert updated_task['meta_info']['ml_request_id'] == UUID
    updated_task['meta_info'].pop('ml_request_id')
    assert updated_task['meta_info'] == expected_task_meta
    assert updated_task['line'] == expected_task_line

    if expected_driver_meta_request:
        assert (
            _dummy_autoreply_driver_meta.calls[0]['kwargs']['json']
            == expected_driver_meta_request
        )

    autoreply_calls_ai = [
        call['kwargs']['json'] for call in _dummy_autoreply_ai.calls
    ]
    assert autoreply_calls_ai == expected_autoreply_calls

    stq_put_calls = [
        stq.chatterbox_common_autoreply_queue.next_call()
        for _ in range(stq.chatterbox_common_autoreply_queue.times_called)
    ]
    for call in stq_put_calls:
        del call['id']
        del call['kwargs']['log_extra']
        del call['kwargs']['request_id']
    assert stq_put_calls == expected_stq_put_calls

    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }
    for call in stq_put_calls:
        await stq_task.chatterbox_common_autoreply(
            cbox.app,
            task_id=task_id,
            actions=call['args'][1],
            event_type=call['args'][2],
            **call['kwargs'],
        )
    updated_twice_task = await cbox.db.support_chatterbox.find_one(
        {'_id': task_id},
    )
    if race_message_id != last_message_id or not stq_put_calls:
        assert updated_twice_task['history'] == updated_task['history']
    else:
        assert updated_twice_task['history'] != updated_task['history']


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_EATS_AUTOREPLY={
        'percentage': 100,
        'chat_types': ['startrack'],
        'langs': ['ru'],
        'delay_range': [300, 600],
        'tags': ['eda_mail_ticket'],
    },
    CHATTERBOX_LINES={
        'first': {'name': 'Еда', 'priority': 3, 'autoreply': True},
    },
    CHATTERBOX_AUTOREPLY_USE_EVENT_TYPE=True,
    PASS_STATUS_IF_FAIL_TO_STQ_CHATTERBOX_AUTOREPLY=True,
)
@pytest.mark.parametrize(
    (
        'task_id',
        'task_metadata',
        'task_tags',
        'expected_tags',
        'expected_stq_put_calls',
    ),
    [
        (
            EATS_TASK_ID,
            {
                'feedback_comment': 'Привезли холодный борщ',
                'macro_id_ml': '1',
                'ml_request_id': UUID,
                'model_ml': '/eats/support/v1',
                'model_status_ml': 'ok',
                'most_probable_topic_ml': 'temperature',
                'order_nr': '200421-1234567',
                'rating': '2',
                'status_ml': 'ok',
                'topic_ml': 'temperature',
                'topics_probabilities_ml': '0.9, 0.1',
                'queue': 'CHATTERBOX',
                'ticket_subject': 'Яндекс.Еда: ответ на ваше обращение',
                'user_email': 'user_email',
                'support_email': 'support_email',
                'task_language': 'ru',
                'webhook_calls': 1,
            },
            ['eda_mail_ticket'],
            ['eda_mail_ticket', 'lang_ru', 'use_eats_autoreply'],
            [
                {
                    'args': [{'$oid': str(EATS_TASK_ID)}, 1, 'eats'],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {'status_if_fail': 'reopened'},
                    'queue': 'chatterbox_autoreply_queue',
                },
            ],
        ),
        (
            EATS_TASK_ID,
            {
                'feedback_comment': 'Привезли холодный борщ',
                'macro_id_ml': '1',
                'ml_request_id': UUID,
                'model_ml': '/eats/support/v1',
                'model_status_ml': 'ok',
                'most_probable_topic_ml': 'temperature',
                'order_nr': '200421-1234567',
                'rating': '2',
                'status_ml': 'waiting',
                'topic_ml': 'temperature',
                'topics_probabilities_ml': '0.9, 0.1',
                'queue': 'CHATTERBOX',
                'ticket_subject': 'Яндекс.Еда: ответ на ваше обращение',
                'user_email': 'user_email',
                'support_email': 'support_email',
                'task_language': 'ru',
                'webhook_calls': 1,
            },
            ['eda_mail_ticket'],
            ['eda_mail_ticket', 'lang_ru', 'use_eats_autoreply'],
            [
                {
                    'args': [{'$oid': str(EATS_TASK_ID)}, 1, 'eats'],
                    'eta': datetime.datetime(2018, 6, 15, 12, 44),
                    'kwargs': {
                        'close_task': False,
                        'status_if_fail': 'reopened',
                    },
                    'queue': 'chatterbox_autoreply_queue',
                },
            ],
        ),
        (
            EATS_TASK_ID,
            {'status_ml': 'ok', 'webhook_calls': 1},
            ['eda_mail_ticket'],
            [
                'autoreply_macro_missing',
                'use_eats_autoreply',
                'eda_mail_ticket',
                'lang_ru',
            ],
            [],
        ),
        (
            EATS_TASK_ID,
            {'status_ml': 'nope', 'webhook_calls': 1},
            ['eda_mail_ticket'],
            ['use_eats_autoreply', 'eda_mail_ticket', 'lang_ru'],
            [],
        ),
        (
            EATS_TASK_ID,
            {'status_ml': 'not_reply', 'webhook_calls': 1},
            ['eda_mail_ticket'],
            ['ar_dismiss', 'use_eats_autoreply', 'eda_mail_ticket', 'lang_ru'],
            [],
        ),
        (
            EATS_TASK_ID,
            {'status_ml': 'ok', 'macro_id_ml': '1', 'webhook_calls': 1},
            [],
            ['lang_ru'],
            [],
        ),
        (
            EATS_TASK_ID,
            {'status_ml': 'ok', 'macro_id_ml': '1', 'webhook_calls': 2},
            ['eda_mail_ticket'],
            ['eda_mail_ticket', 'lang_ru'],
            [],
        ),
    ],
)
async def test_eats_autoreply(
        cbox,
        mock_st_get_messages,
        mock_st_transition,
        mock_translate,
        mock_chat_get_history,
        mock_randint,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        stq,
        task_id,
        task_metadata,
        task_tags,
        expected_tags,
        expected_stq_put_calls,
):
    messages = [
        {
            'id': 'message_id',
            'sender': {'id': 'client_login', 'role': 'client'},
            'text': 'Привезли холодный борщ',
            'metadata': {'created': '2018-05-05T15:34:56'},
        },
    ]
    mock_st_get_messages(
        {'messages': messages, 'total': 0, 'hidden_comments': []},
    )
    mock_chat_get_history({'messages': messages})
    mock_translate('ru')

    if task_metadata:
        await cbox.db.support_chatterbox.find_one_and_update(
            filter={'_id': task_id},
            update={'$set': {'meta_info': task_metadata, 'tags': task_tags}},
        )

    await stq_task.chatterbox_predispatch(cbox.app, task_id)

    updated_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert set(updated_task['tags']) == set(expected_tags)

    stq_put_calls = [
        stq.chatterbox_autoreply_queue.next_call()
        for _ in range(stq.chatterbox_autoreply_queue.times_called)
    ]
    for call in stq_put_calls:
        del call['id']
        del call['kwargs']['log_extra']
        del call['kwargs']['request_id']
    assert stq_put_calls == expected_stq_put_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    [
        'use_meta_close_task',
        'task_id',
        'close_task',
        'expected_task_status',
        'expected_tags',
        'expected_add_update_calls',
        'expected_history',
        'expected_stq_put_calls',
    ],
    [
        (
            False,
            NTO_IN_PROGRESS_TASK_ID,
            True,
            'closed',
            [],
            [
                {
                    'args': ('nto_in_progress_user_chat_message_id',),
                    'kwargs': {
                        'message_id': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': None,
                        'update_metadata': {
                            'ticket_status': 'solved',
                            'ask_csat': False,
                            'retry_csat_request': False,
                        },
                        'message_metadata': None,
                        'log_extra': None,
                    },
                },
            ],
            {
                'action_id': 'test_uid',
                'action': 'dismiss',
                'in_addition': False,
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
            [],
        ),
        (
            False,
            AUTOREPLY_IN_PROGRESS_TASK_ID,
            True,
            'closed',
            ['ar_reply'],
            [
                {
                    'args': ('autoreply_in_progress_user_chat_message_id',),
                    'kwargs': {
                        'message_id': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': 'Какой-то текст',
                        'update_metadata': {
                            'ticket_status': 'solved',
                            'ask_csat': True,
                            'retry_csat_request': False,
                        },
                        'message_metadata': None,
                        'log_extra': None,
                    },
                },
            ],
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Какой-то текст',
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'tags_changes': [{'change_type': 'add', 'tag': 'ar_reply'}],
                'tags_added': ['ar_reply'],
                'meta_changes': [
                    {
                        'change_type': 'set',
                        'field_name': 'macro_id',
                        'value': 1,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'currently_used_macro_ids',
                        'value': ['1'],
                    },
                ],
                'line': 'first',
            },
            [
                {
                    'args': [
                        {'$oid': str(AUTOREPLY_IN_PROGRESS_TASK_ID)},
                        ['1'],
                    ],
                    'queue': 'chatterbox_send_macros_to_support_tags',
                },
            ],
        ),
        (
            True,
            AUTOREPLY_MUST_FAIL_TASK_ID_OFFLINE,
            True,
            'new',
            [],
            [],
            {
                'action': 'fail_autoreply',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'login': 'superuser',
                'line': 'first',
            },
            [],
        ),
        (
            True,
            AUTOREPLY_MUST_FAIL_TASK_ID_ONLINE,
            True,
            'new',
            [],
            [],
            {
                'action': 'fail_autoreply',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'login': 'superuser',
                'line': 'second',
            },
            [],
        ),
        (
            False,
            AUTOREPLY_IN_PROGRESS_TASK_ID,
            False,
            'waiting',
            ['ar_reply'],
            [
                {
                    'args': ('autoreply_in_progress_user_chat_message_id',),
                    'kwargs': {
                        'message_id': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': 'Какой-то текст',
                        'update_metadata': {'ticket_status': 'pending'},
                        'message_metadata': None,
                        'log_extra': None,
                    },
                },
            ],
            {
                'action_id': 'test_uid',
                'comment': 'Какой-то текст',
                'in_addition': False,
                'action': 'comment',
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'tags_changes': [{'change_type': 'add', 'tag': 'ar_reply'}],
                'tags_added': ['ar_reply'],
                'meta_changes': [
                    {
                        'change_type': 'set',
                        'field_name': 'macro_id',
                        'value': 1,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'currently_used_macro_ids',
                        'value': ['1'],
                    },
                ],
                'line': 'first',
            },
            [
                {
                    'args': [{'$oid': '5b2cae5cb2682a976914c2ad'}, ['1']],
                    'queue': 'chatterbox_send_macros_to_support_tags',
                },
            ],
        ),
        (
            True,
            AUTOREPLY_IN_PROGRESS_TASK_ID_2,
            False,
            'closed',
            ['ar_reply', 'chat_model_ar_reply'],
            [
                {
                    'args': ('autoreply_in_progress_user_chat_message_id_2',),
                    'kwargs': {
                        'message_id': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': 'Какой-то текст',
                        'update_metadata': {
                            'ticket_status': 'solved',
                            'ask_csat': True,
                            'retry_csat_request': False,
                        },
                        'message_metadata': None,
                        'log_extra': None,
                    },
                },
            ],
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Какой-то текст',
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'tags_changes': [
                    {'change_type': 'add', 'tag': 'ar_reply'},
                    {'change_type': 'add', 'tag': 'chat_model_ar_reply'},
                ],
                'tags_added': ['ar_reply', 'chat_model_ar_reply'],
                'meta_changes': [
                    {
                        'change_type': 'set',
                        'field_name': 'macro_id',
                        'value': 1,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'currently_used_macro_ids',
                        'value': ['1'],
                    },
                ],
                'line': 'first',
            },
            [
                {
                    'args': [
                        {'$oid': str(AUTOREPLY_IN_PROGRESS_TASK_ID_2)},
                        ['1'],
                    ],
                    'queue': 'chatterbox_send_macros_to_support_tags',
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_LINES={'first': {}, 'second': {'mode': 'online'}},
    CHATTERBOX_HISTORY_TAGS_ADDED=True,
    PASS_STATUS_IF_FAIL_TO_STQ_CHATTERBOX_AUTOREPLY=True,
)
async def test_complete_autoreply(
        cbox,
        stq,
        task_id,
        use_meta_close_task,
        close_task,
        expected_task_status,
        expected_tags,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_random_str_uuid,
        expected_add_update_calls,
        expected_history,
        expected_stq_put_calls,
):
    mock_random_str_uuid()
    cbox.app.config.CHATTERBOX_AUTOREPLY_USE_META_CLOSE_TASK = (
        use_meta_close_task
    )
    mock_chat_get_history({'messages': []})
    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }
    await stq_task.chatterbox_autoreply(
        cbox.app, task_id, 'client', None, close_task=close_task,
    )
    updated_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert updated_task['status'] == expected_task_status
    assert set(updated_task['tags']) == set(expected_tags)
    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls == expected_add_update_calls
    assert updated_task['history'][-1] == expected_history
    stq_put_calls = [
        stq.chatterbox_send_macros_to_support_tags.next_call()
        for _ in range(stq.chatterbox_send_macros_to_support_tags.times_called)
    ]
    for call in stq_put_calls:
        del call['id']
        del call['eta']
        del call['kwargs']
    assert stq_put_calls == expected_stq_put_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    [
        'task_id',
        'actions',
        'event_type',
        'kwargs',
        'expected_task_status',
        'expected_tags',
        'expected_add_update_calls',
        'history_count',
        'expected_history',
        'expected_stq_put_calls',
    ],
    [
        (
            AUTOREPLY_IN_PROGRESS_TASK_ID,
            {'comment': {'macro_id': 1}, 'defer': {'defer_time': 300}},
            'client',
            {'status_if_fail': 'new', 'request_id': UUID},
            'deferred',
            ['ar_reply'],
            [
                {
                    'args': ('autoreply_in_progress_user_chat_message_id',),
                    'kwargs': {
                        'log_extra': None,
                        'message_id': None,
                        'message_metadata': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': 'Какой-то текст',
                        'update_metadata': {'ticket_status': 'pending'},
                    },
                },
            ],
            2,
            [
                {
                    'action_id': 'test_uid',
                    'action': 'comment',
                    'comment': 'Какой-то текст',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 1,
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['1'],
                        },
                    ],
                    'tags_added': ['ar_reply'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'ar_reply'},
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'reopen_at': datetime.datetime(2018, 6, 15, 12, 42),
                    'meta_changes': [],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': str(AUTOREPLY_IN_PROGRESS_TASK_ID)},
                        ['1'],
                    ],
                    'queue': 'chatterbox_send_macros_to_support_tags',
                },
                {
                    'args': [
                        {'$oid': str(AUTOREPLY_IN_PROGRESS_TASK_ID)},
                        ['1'],
                    ],
                    'queue': 'chatterbox_send_macros_to_support_tags',
                },
            ],
        ),
        (
            AUTOREPLY_IN_PROGRESS_TASK_ID,
            {'close': {'macro_id': 1}},
            'client',
            {'status_if_fail': 'new', 'request_id': UUID},
            'closed',
            ['ar_reply'],
            [
                {
                    'args': ('autoreply_in_progress_user_chat_message_id',),
                    'kwargs': {
                        'log_extra': None,
                        'message_id': None,
                        'message_metadata': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': 'Какой-то текст',
                        'update_metadata': {
                            'ask_csat': True,
                            'retry_csat_request': False,
                            'ticket_status': 'solved',
                        },
                    },
                },
            ],
            1,
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'comment': 'Какой-то текст',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 1,
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['1'],
                        },
                    ],
                    'tags_added': ['ar_reply'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'ar_reply'},
                    ],
                },
            ],
            [
                {
                    'args': [
                        {'$oid': str(AUTOREPLY_IN_PROGRESS_TASK_ID)},
                        ['1'],
                    ],
                    'queue': 'chatterbox_send_macros_to_support_tags',
                },
            ],
        ),
        (
            AUTOREPLY_IN_PROGRESS_TASK_ID,
            {'dismiss': {}},
            'client',
            {'status_if_fail': 'new', 'request_id': UUID},
            'closed',
            ['ar_dismiss'],
            [
                {
                    'args': ('autoreply_in_progress_user_chat_message_id',),
                    'kwargs': {
                        'log_extra': None,
                        'message_id': None,
                        'message_metadata': None,
                        'message_sender_id': 'superuser',
                        'message_sender_role': 'support',
                        'message_text': None,
                        'update_metadata': {
                            'ask_csat': False,
                            'retry_csat_request': False,
                            'ticket_status': 'solved',
                        },
                    },
                },
            ],
            1,
            [
                {
                    'action_id': 'test_uid',
                    'action': 'dismiss',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'tags_added': ['ar_dismiss'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'ar_dismiss'},
                    ],
                },
            ],
            [],
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_LINES={'first': {}, 'second': {'mode': 'online'}},
    CHATTERBOX_HISTORY_TAGS_ADDED=True,
    PASS_STATUS_IF_FAIL_TO_STQ_CHATTERBOX_AUTOREPLY=True,
    CHATTERBOX_DEFER_AUTOREPLY={
        'enabled': True,
        'max_count': 3,
        'max_time_sec': 600,
        'default_time_sec': 300,
        'deferred_status_delay_sec': 180,
    },
)
async def test_complete_common_autoreply(
        cbox,
        stq,
        task_id,
        actions,
        event_type,
        kwargs,
        expected_task_status,
        expected_tags,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_random_str_uuid,
        expected_add_update_calls,
        history_count,
        expected_history,
        expected_stq_put_calls,
):
    mock_random_str_uuid()
    mock_chat_get_history({'messages': []})
    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }
    await stq_task.chatterbox_common_autoreply(
        cbox.app, task_id, actions, event_type, **kwargs,
    )
    updated_task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert updated_task['status'] == expected_task_status
    assert set(updated_task['tags']) == set(expected_tags)
    add_update_calls = mock_chat_add_update.calls
    assert add_update_calls == expected_add_update_calls
    assert updated_task['history'][-history_count:] == expected_history
    stq_put_calls = [
        stq.chatterbox_send_macros_to_support_tags.next_call()
        for _ in range(stq.chatterbox_send_macros_to_support_tags.times_called)
    ]
    for call in stq_put_calls:
        del call['id']
        del call['kwargs']
        del call['eta']

    assert stq_put_calls == expected_stq_put_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {
            'conditions': {},
            'name': '1 · DM РФ',
            'priority': 3,
            'autoreply': True,
        },
        'second': {
            'conditions': {'fields.ml_predicted_line': 'second'},
            'name': '2',
            'priority': 1,
            'autoreply': True,
        },
    },
    CHATTERBOX_FORWARD_AUTOREPLY=True,
    CHATTERBOX_AUTOREPLY_USE_EVENT_TYPE=True,
    CHATTERBOX_USE_CHAT_MESSAGE_ID=True,
    CHATTERBOX_EDA_DIALOG_AUTOREPLY={
        'percentage': 100,
        'chat_types': ['client_eats', 'client_eats_app'],
        'langs': ['ru'],
        'delay_range': [300, 600],
        'update_autoreply': {
            'percentage': 100,
            'requeue_delay_range': [60, 120],
            'statuses': ['new'],
        },
    },
)
@pytest.mark.parametrize(
    ('task_id', 'expected_status', 'expected_tags', 'expected_autoreply_url'),
    [
        (
            PREDISPATCH_TASK_ID,
            'new',
            [
                'check_autoreply_project_client',
                'check_ml_autoreply',
                'lang_ru',
            ],
            '/supportai-api/v1/support_internal',
        ),
        (
            FOODTECH_PREDISPATCH_TASK_ID,
            'new',
            [
                'check_autoreply_project_eats_client',
                'check_ml_autoreply',
                'lang_ru',
            ],
            '/supportai-api/v1/support_internal',
        ),
    ],
)
async def test_autoreply_request_error(
        cbox,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_translate,
        mock_get_user_phone,
        mock_randint,
        mock_antifraud_refund,
        mock_get_chat_order_meta,
        stq,
        patch_aiohttp_session,
        response_mock,
        mock_uuid_uuid4,
        task_id,
        expected_status,
        expected_tags,
        expected_autoreply_url,
):
    mock_chat_get_history(
        {
            'messages': [
                {
                    'id': 0,
                    'sender': {'id': 'some_login', 'role': 'client'},
                    'text': 'some message',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
            ],
        },
    )
    mock_translate('ru')

    support_info_service = discovery.find_service('support_info')

    @patch_aiohttp_session(
        support_info_service.url + '/v1/get_additional_meta', 'POST',
    )
    @patch_aiohttp_session(
        support_info_service.url + '/v1/autoreply/driver_meta', 'POST',
    )
    def _dummy_autoreply_meta(method, url, **kwargs):
        assert method == 'post'
        response = {'metadata': {'some': 'metadata'}, 'status': 'ok'}
        return response_mock(json=response)

    supportai_api_service = discovery.find_service('supportai-api')

    @patch_aiohttp_session(supportai_api_service.url, 'POST')
    def _dummy_autoreply_ai(method, url, **kwargs):
        assert method == 'post'
        assert url == supportai_api_service.url + expected_autoreply_url

        raise supportai_api.BaseError

    await stq_task.chatterbox_predispatch(cbox.app, task_id)

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] == expected_status
    assert set(task['tags']) == set(expected_tags)

    assert not stq.chatterbox_common_autoreply_queue.has_calls
