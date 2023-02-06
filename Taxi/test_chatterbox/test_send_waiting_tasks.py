import datetime

import pytest

from taxi import discovery

from chatterbox.crontasks import send_waiting_tasks


@pytest.mark.config(
    CHATTERBOX_SEND_TASKS_PARAMS={
        'waiting_tasks': {'enabled': True, 'chunk_size': 100},
        '__default__': {'enabled': True, 'chunk_size': 1000},
    },
    CHATTERBOX_WAITING_TASKS_SEARCH_PARAMS_BY_PROJECT={
        '__default__': {'task_creation_time_limit': 3 * 24 * 60 * 60},
        'eats': {},
    },
    CHATTERBOX_LINES={
        'first': {'projects': ['eats']},
        'second': {'projects': ['eats', 'market']},
    },
)
@pytest.mark.now(datetime.datetime(2021, 9, 16, 14, 30, 0).isoformat())
@pytest.mark.parametrize(
    ('messages', 'expected_request_data'),
    [
        pytest.param(
            [
                {
                    'sender': {'id': 'user', 'role': 'client'},
                    'text': 'Здравствуйте. Что-то заказа долго нет.',
                    'metadata': {'created': '2021-09-16T17:29:00+03:00'},
                },
                {
                    'sender': {'id': 'user', 'role': 'client'},
                    'text': 'Не подскажете, в чем дело?',
                    'metadata': {'created': '2021-09-16T17:29:16+03:00'},
                },
            ],
            {
                'tasks': [
                    {
                        'id': 'task_2',
                        'status': 'offered',
                        'login': '',
                        'line': 'first',
                        'waiting_time': 60,
                        'updated_ts': '2021-09-16T17:30:00+0300',
                    },
                    {
                        'id': 'task_3',
                        'status': 'accepted',
                        'login': 'support_1',
                        'line': 'first',
                        'waiting_time': 60,
                        'updated_ts': '2021-09-16T17:30:00+0300',
                    },
                    {
                        'id': 'task_4',
                        'status': 'in_progress',
                        'login': 'support_2',
                        'line': 'first',
                        'waiting_time': 60,
                        'updated_ts': '2021-09-16T17:30:00+0300',
                    },
                    {
                        'id': 'task_5',
                        'status': 'reopened',
                        'login': '',
                        'line': 'second',
                        'waiting_time': 60,
                        'updated_ts': '2021-09-16T17:30:00+0300',
                    },
                    {
                        'id': 'task_6',
                        'status': 'forwarded',
                        'login': '',
                        'line': 'second',
                        'waiting_time': 60,
                        'updated_ts': '2021-09-16T17:30:00+0300',
                    },
                ],
                'created_ts': '2021-09-16T17:30:00+0300',
            },
            marks=[pytest.mark.filldb(support_chatterbox='1')],
        ),
        pytest.param(
            [
                {
                    'sender': {'id': 'user', 'role': 'client'},
                    'text': 'Здравствуйте',
                    'metadata': {'created': '2021-09-16T17:28:00+03:00'},
                },
                {
                    'sender': {'id': 'support_1', 'role': 'support'},
                    'text': 'Добрый день!',
                    'metadata': {'created': '2021-09-16T17:28:56+03:00'},
                },
                {
                    'sender': {'id': 'user', 'role': 'client'},
                    'text': (
                        'Что-то заказа долго нет. Не подскажете, в чем дело?'
                    ),
                    'metadata': {'created': '2021-09-16T17:29:16+03:00'},
                },
            ],
            {
                'tasks': [
                    {
                        'id': 'task_1',
                        'status': 'accepted',
                        'login': 'support_1',
                        'line': 'first',
                        'waiting_time': 44,
                        'updated_ts': '2021-09-16T17:30:00+0300',
                    },
                    {
                        'id': 'task_2',
                        'status': 'in_progress',
                        'login': 'support_2',
                        'line': 'first',
                        'waiting_time': 44,
                        'updated_ts': '2021-09-16T17:30:00+0300',
                    },
                ],
                'created_ts': '2021-09-16T17:30:00+0300',
            },
            marks=[pytest.mark.filldb(support_chatterbox='2')],
        ),
        pytest.param(
            [
                {
                    'sender': {'id': 'user', 'role': 'client'},
                    'text': 'Здравствуйте. Что-то заказа долго нет.',
                    'metadata': {'created': '2021-09-16T17:27:56+03:00'},
                },
                {
                    'sender': {'id': 'support_1', 'role': 'support'},
                    'text': 'Добрый день. Сейчас уточню, где он',
                    'metadata': {'created': '2021-09-16T17:28:16+03:00'},
                },
            ],
            {'tasks': [], 'created_ts': '2021-09-16T17:30:00+0300'},
            marks=[pytest.mark.filldb(support_chatterbox='1')],
        ),
        pytest.param(
            [
                {
                    'sender': {'id': 'user', 'role': 'client'},
                    'text': 'Здравствуйте. Что-то заказа долго нет.',
                    'metadata': {'created': '2021-09-16T17:29:00+03:00'},
                },
                {
                    'sender': {'id': 'user', 'role': 'client'},
                    'text': 'Не подскажете, в чем дело?',
                    'metadata': {'created': '2021-09-16T17:29:16+03:00'},
                },
            ],
            {
                'tasks': [
                    {
                        'id': 'task_5',
                        'status': 'reopened',
                        'login': '',
                        'line': 'second',
                        'waiting_time': 60,
                        'updated_ts': '2021-09-16T17:30:00+0300',
                    },
                ],
                'created_ts': '2021-09-16T17:30:00+0300',
            },
            marks=[
                pytest.mark.filldb(support_chatterbox='1'),
                pytest.mark.config(
                    CHATTERBOX_LINES={
                        'first': {'projects': ['taxi']},
                        'second': {'projects': ['eats', 'market']},
                    },
                    CHATTERBOX_WAITING_TASKS_SEARCH_PARAMS_BY_PROJECT={
                        '__default__': {
                            'task_creation_time_limit': 3 * 24 * 60 * 60,
                        },
                        'eats': {'task_creation_time_limit': 7 * 60 * 60},
                    },
                ),
            ],
        ),
    ],
)
async def test_send_tasks_waiting_for_response(
        cbox_context,
        loop,
        response_mock,
        mock_chat_get_history,
        mock_st_get_messages,
        patch_aiohttp_session,
        messages,
        expected_request_data,
):
    mock_chat_get_history({'messages': messages})
    mock_st_get_messages({'messages': messages})
    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def _patch_request(method, url, **kwargs):
        assert method == 'post'
        assert (
            url
            == '%s/v1/bulk_process_waiting_tasks' % support_metrics_service.url
        )
        kwargs['json']['tasks'] = sorted(
            kwargs['json']['tasks'], key=lambda d: d['id'],
        )
        assert kwargs['json'] == expected_request_data
        return response_mock(json={})

    await send_waiting_tasks.do_stuff(cbox_context, loop)
