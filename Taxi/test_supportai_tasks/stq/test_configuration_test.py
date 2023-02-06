import json

from aiohttp import web
import pytest

from supportai_lib.tasks import base_task

from supportai_tasks import models as db_models


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql']),
    pytest.mark.config(
        TVM_RULES=[
            {'src': 'supportai-tasks', 'dst': 'supportai'},
            {'src': 'supportai-tasks', 'dst': 'supportai-context'},
            {'src': 'supportai-tasks', 'dst': 'stq-agent'},
        ],
    ),
    pytest.mark.config(
        SUPPORTAI_TASKS_CONFIGURATION_TESTING={
            'default_settings': {
                'delay_between_batches_in_seconds': 1,
                'delay_between_requests_in_milliseconds': 200,
                'batch_size': 8,
            },
            'projects': [],
        },
    ),
]


def _get_context(chat_id, response_text, mark=None):
    context = {
        'created_at': '2021-04-01 10:00:00+03',
        'chat_id': chat_id,
        'records': [
            {
                'id': '1',
                'created_at': '2021-04-01 10:00:00+03',
                'request': {
                    'chat_id': chat_id,
                    'dialog': {'messages': [{'text': 'lol', 'author': 'ai'}]},
                    'features': [{'key': 'event_type', 'value': 'dial'}],
                },
                'response': {'reply': {'text': '1'}},
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
                'response': {'reply': {'text': response_text}},
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
                'response': {'reply': {'text': '1'}},
            },
        ],
    }

    if mark is not None:
        context['chat_mark'] = mark

    return context


@pytest.mark.config(
    SUPPORTAI_TASKS_CONFIGURATION_TESTING={
        'default_settings': {
            'delay_between_batches_in_seconds': 2,
            'delay_between_requests_in_milliseconds': 500,
            'batch_size': 8,
        },
        'projects': [
            {
                'project_id': 'sample_project',
                'settings': {
                    'delay_between_batches_in_seconds': 1,
                    'delay_between_requests_in_milliseconds': 200,
                    'batch_size': 8,
                },
            },
        ],
    },
)
async def test_configuration_test_task(
        stq3_context, mockserver, web_app_client, stq_runner, create_task,
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
                        _get_context('1', '1'),
                        _get_context('2', '1'),
                        _get_context('3', '1'),
                    ],
                    'total': 3,
                },
            )
        return web.json_response(data={'contexts': [], 'total': 3})

    @mockserver.json_handler('supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler_supportai(request):
        return web.json_response(data={'reply': {'text': '1'}})

    task = create_task(
        type_='test_configuration',
        params={'sample_slug': 'test_sample', 'use_history': True},
    )

    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': task.id},
    )
    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': task.id},
    )

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), f'Incorrect status, error_message: {task.error_message}'

    assert task.params.extra['processed_dialogs_count'] == 3
    assert task.progress == 100

    model = db_models.ConfigurationTest

    async with stq3_context.pg.slave_pool.acquire() as conn:
        tests = await model.select_by_task_id(
            stq3_context, conn, task_id=task.id, offset=0, limit=10,
        )

    assert len(tests) == 9
    assert all(map(lambda test: test.is_equal, tests))


async def test_configuration_test_task_not_empty_diff(
        stq3_context, mockserver, web_app_client, stq_runner, create_task,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        return {}

    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def handler_context(request):
        if request.args.get('offset') == '0':
            return web.json_response(
                data={'contexts': [_get_context('1', '1')], 'total': 1},
            )
        return web.json_response(data={'contexts': [], 'total': 1})

    @mockserver.json_handler('supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler_supportai(request):
        if request.args.get('version'):
            return web.json_response(data={'reply': {'text': 'Здравствуйте!'}})
        return web.json_response(data={'reply': {'text': 'До свидания!'}})

    task = create_task(
        type_='test_configuration', params={'sample_slug': 'test_sample'},
    )

    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': task.id},
    )
    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': task.id},
    )

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), f'Incorrect status, error_message: {task.error_message}'

    assert task.params.extra['processed_dialogs_count'] == 1
    assert task.progress == 100

    model = db_models.ConfigurationTest

    async with stq3_context.pg.slave_pool.acquire() as conn:
        tests = await model.select_by_task_id(
            stq3_context, conn, task_id=task.id, offset=0, limit=10,
        )

    assert len(tests) == 1
    assert not tests[0].is_equal
    assert tests[0].diff
    assert tests[0].chat_id == '1'


async def test_aggregation(
        stq3_context, mockserver, web_app_client, stq_runner, create_task,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        return {}

    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def handler_context(request):
        if request.args.get('offset') == '0':
            sure_context = _get_context('3', '4', 'ok')
            sure_context['records'][0]['response']['features'] = {
                'sure_topic': 'topic_1',
                'probabilities': [],
            }
            return web.json_response(
                data={
                    'contexts': [_get_context('1', '2'), sure_context],
                    'total': 2,
                },
            )
        return web.json_response(data={'contexts': [], 'total': 2})

    @mockserver.json_handler('supportai/supportai/v1/support')
    # pylint: disable=unused-variable
    async def handler_supportai(request):
        return web.json_response(
            data={
                'reply': {'text': '1'},
                'features': {'sure_topic': 'topic_1', 'probabilities': []},
            },
        )

    task = create_task(
        type_='test_configuration', params={'sample_slug': 'test_sample'},
    )

    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': task.id},
    )
    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': task.id},
    )

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), f'Incorrect status, error_message: {task.error_message}'

    assert task.params.extra['processed_dialogs_count'] == 2
    assert task.progress == 100

    model = db_models.TestingAggregation

    async with stq3_context.pg.slave_pool.acquire() as conn:
        aggregation = await model.select_by_task_id(
            stq3_context, conn, task_id=task.id,
        )

    assert aggregation is not None
    assert aggregation.task_id == task.id
    assert aggregation.ok_chat_count == 3
    assert aggregation.chat_count == 6
    assert aggregation.equal_count == 6
    assert aggregation.topic_ok_count_v1 == 1
    assert aggregation.topic_ok_count_v2 == 1
    assert aggregation.reply_count_v1 == 6
    assert aggregation.reply_count_v2 == 6
    assert aggregation.close_count_v1 == 0
    assert aggregation.close_count_v2 == 0
    assert aggregation.reply_or_close_count_v1 == 6
    assert aggregation.reply_or_close_count_v2 == 6
    assert json.loads(aggregation.topic_details) == {
        'topic_1': {'v1': 6, 'v2': 6, 'int_count': 6},
    }
