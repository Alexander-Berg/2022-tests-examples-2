from aiohttp import web
import pytest

from supportai_lib.tasks import base_task

from supportai_tasks import models as db_models


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql']),
    pytest.mark.config(
        TVM_RULES=[
            {'src': 'supportai-tasks', 'dst': 'supportai-context'},
            {'src': 'supportai-tasks', 'dst': 'stq-agent'},
        ],
    ),
    pytest.mark.config(
        SUPPORTAI_TASKS_CLUSTERING_SETTINGS={
            'default_settings': {
                'nirvana_instance_id': (
                    'bb951dc5-975b-4b3f-944c-9de56aae8beb/'
                    '828f5201-f124-4c36-8815-cc2b55fb673f'
                ),
                'yt_root_dir': '//home/taxi_ml/imports/support',
                'messages_count': 10,
                'context_batch_size': 3,
            },
            'projects': [{'project_slug': 'sample_project'}],
        },
    ),
]


def _get_context(chat_id, request_text):
    context = {
        'created_at': '2021-04-01 10:00:00+03',
        'chat_id': chat_id,
        'records': [
            {
                'created_at': '2021-04-01 10:00:00+03',
                'request': {
                    'chat_id': chat_id,
                    'dialog': {
                        'messages': [{'text': request_text, 'author': 'ai'}],
                    },
                    'features': [{'key': 'event_type', 'value': 'dial'}],
                },
                'response': {'reply': {'text': '1'}},
            },
        ],
    }

    return context


@pytest.mark.yt(static_table_data=['yt_clustering_result.yaml'])
async def test_clustering_test_task(
        stq3_context, mockserver, stq_runner, create_task, yt_client,
):
    @mockserver.json_handler('/nirvana-api/setGlobalParameters')
    async def _set_params_handler(request):
        return {'result': 'ok'}

    @mockserver.json_handler('/nirvana-api/approveWorkflow')
    async def _approve_handler(request):
        return {'result': 'ok'}

    @mockserver.json_handler('/nirvana-api/startWorkflow')
    async def _start_handler(request):
        return {'result': 'ok'}

    @mockserver.json_handler('/nirvana-api/cloneWorkflowInstance')
    async def _clone_handler(request):
        return {'result': 'new_instance_id'}

    @mockserver.json_handler('/nirvana-api/getExecutionState')
    async def _state_handler(request):
        return {'result': {'status': 'completed', 'result': 'success'}}

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        return {}

    context_request_count = 0

    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def handler_context(request):
        nonlocal context_request_count
        context_request_count += 1

        return web.json_response(
            data={
                'contexts': [
                    _get_context('1', 'text_1'),
                    _get_context('2', 'text_2'),
                    _get_context('3', 'text_3'),
                ],
                'total': 3,
            },
        )

    db_task = create_task(type_='clustering')

    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': db_task.id},
    )

    assert db_task.status == base_task.TaskStatus.PROCESSING.value
    assert context_request_count == 4

    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': db_task.id},
    )

    assert db_task.status == base_task.TaskStatus.COMPLETED.value

    async with stq3_context.pg.slave_pool.acquire() as conn:
        results = await db_models.ClusteringResult.select_overview(
            stq3_context, conn, 'test_slug', header_count=10,
        )

    assert len(results) == 3

    assert results[0].project_slug == 'test_slug'
    assert {1, 3} == {
        results[0].cluster_number,
        results[1].cluster_number,
        results[2].cluster_number,
    }
