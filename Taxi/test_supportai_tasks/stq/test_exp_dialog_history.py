#  pylint: disable=protected-access
#  type: ignore
import io

from aiohttp import web
import pandas as pd
import pytest

from supportai_lib.tasks import base_task
from taxi.stq import async_worker_ng

from supportai_tasks.generated.stq3 import stq_context
from supportai_tasks.stq import runner


def _get_context(chat_id, response_text, created_sec):
    context = {
        'created_at': f'2021-04-01 10:00:{created_sec}+03',
        'chat_id': chat_id,
        'records': [
            {
                'id': '1',
                'created_at': '2021-04-01 10:00:00+03',
                'mark_comment': 'Тематика',
                'request': {
                    'chat_id': chat_id,
                    'dialog': {'messages': [{'text': 'Some', 'author': 'ai'}]},
                    'features': [{'key': 'event_type', 'value': 'dial'}],
                },
                'response': {
                    'reply': {'text': '1', 'texts': ['1']},
                    'features': {
                        'sure_topic': 'topic_1',
                        'probabilities': [],
                        'most_probable_topic': '',
                        'features': [{'key': 'write', 'value': 'exel'}],
                    },
                },
            },
            {
                'id': '2',
                'created_at': '2021-04-01 10:02:00+03',
                'request': {
                    'chat_id': chat_id,
                    'dialog': {
                        'messages': [
                            {'text': 'help help help', 'author': 'user'},
                        ],
                    },
                    'features': [],
                },
                'response': {
                    'reply': {'text': response_text, 'texts': [response_text]},
                    'features': {
                        'probabilities': [],
                        'most_probable_topic': '',
                        'features': [{'key': 'read', 'value': 'exel'}],
                    },
                },
            },
            {
                'id': '3',
                'created_at': '2021-04-01 10:05:00+03',
                'request': {
                    'chat_id': chat_id,
                    'dialog': {
                        'messages': [
                            {'text': 'Some answer', 'author': 'user'},
                        ],
                    },
                    'features': [],
                },
                'response': {'reply': {'text': '300', 'texts': ['300']}},
            },
        ],
    }

    return context


@pytest.mark.config(
    SUPPORTAI_TASKS_EXPORT_DIALOGS_SETTINGS={
        'settings': {
            'batch_size': 30,
            'delay_in_seconds': 10,
            'max_rows_number': 2000,
        },
        'projects': [
            {'project_id': 'sample_project', 'default_features': ['read']},
        ],
    },
)
@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
@pytest.mark.parametrize('sampling_slug', [None, 'slug'])
async def test_export_dialog_history(
        stq3_context: stq_context.Context,
        response_mock,
        mockserver,
        create_task,
        sampling_slug,
        get_task_file,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        return {}

    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def handler_context(request):
        if request.args.get('offset') == '0':
            return web.json_response(
                data={
                    'contexts': [
                        _get_context('1', '1', 50),
                        _get_context('2', '2', 40),
                        _get_context('3', '3', 55),
                        _get_context('4', '4', 20),
                        _get_context('5', '5', 10),
                    ],
                    'total': 3,
                },
            )
        return web.json_response(data={'contexts': [], 'total': 0})

    task = create_task(
        type_='export_dialog_history',
        params={'sampling_slug': sampling_slug}
        if sampling_slug is not None
        else None,
    )

    for _ in range(2):
        await runner.task(
            stq3_context,
            async_worker_ng.TaskInfo(
                id=1,
                exec_tries=10,
                reschedule_counter=0,
                queue='supportai_admin_export',
            ),
            task_id=task.id,
        )

    assert task.status != base_task.TaskStatus.ERROR.value, task.error_message
    assert task.file_id is not None

    file_data = get_task_file(task.file_id)

    assert file_data is not None

    all_data = pd.read_excel(
        io.BytesIO(file_data[1]), sheet_name=None, na_filter=False,
    )

    history = all_data['history'].to_dict('records')
    assert len(history) == 12
    assert str(history[0]['chat_id']) == '1'
    assert 'Тематика' in [h['mark_comment'] for h in history]
    assert 'topic_1' in [h['sure_topic'] for h in history]


@pytest.mark.config(
    SUPPORTAI_TASKS_EXPORT_DIALOGS_SETTINGS={
        'settings': {
            'batch_size': 30,
            'delay_in_seconds': 10,
            'max_rows_number': 2000,
        },
        'projects': [
            {'project_id': 'sample_project', 'default_features': ['read']},
        ],
    },
)
@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
async def test_export_dialog_history_one_dialog(
        stq3_context: stq_context.Context,
        response_mock,
        mockserver,
        create_task,
        get_task_file,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        return {}

    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def handler_context(request):
        if request.args.get('offset') == '0':
            return web.json_response(
                data={
                    'contexts': [
                        {
                            'created_at': f'2021-04-01 10:00:00+03',
                            'chat_id': 'XXXX',
                            'records': [
                                {
                                    'id': '1',
                                    'created_at': '2021-04-01 10:00:00+03',
                                    'mark_comment': 'Тематика',
                                    'request': {
                                        'chat_id': 'XXXX',
                                        'dialog': {
                                            'messages': [
                                                {
                                                    'text': 'Some',
                                                    'author': 'ai',
                                                },
                                            ],
                                        },
                                        'features': [
                                            {
                                                'key': 'event_type',
                                                'value': 'dial',
                                            },
                                        ],
                                    },
                                    'response': {
                                        'reply': {'text': '1', 'texts': ['1']},
                                        'features': {
                                            'sure_topic': 'topic_1',
                                            'probabilities': [],
                                            'most_probable_topic': '',
                                            'features': [
                                                {
                                                    'key': 'write',
                                                    'value': 'exel',
                                                },
                                            ],
                                        },
                                    },
                                },
                            ],
                        },
                    ],
                    'total': 1,
                },
            )
        return web.json_response(data={'contexts': [], 'total': 0})

    task = create_task(type_='export_dialog_history', params=None)

    await runner.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1,
            exec_tries=10,
            reschedule_counter=0,
            queue='supportai_admin_export',
        ),
        task_id=task.id,
    )

    assert task.status != base_task.TaskStatus.ERROR.value, task.error_message
    assert task.file_id is not None

    file_data = get_task_file(task.file_id)

    assert file_data is not None

    all_data = pd.read_excel(
        io.BytesIO(file_data[1]), sheet_name=None, na_filter=False,
    )

    history = all_data['history'].to_dict('records')
    assert len(history) == 1
    assert str(history[0]['chat_id']) == 'XXXX'
