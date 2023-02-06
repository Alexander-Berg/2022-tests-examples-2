import datetime

import pytest

from supportai_lib.tasks import base_task

from supportai_tasks import models as db_models


@pytest.fixture(name='mocked_supportai')
def mock_supportai(mockserver):
    feature = {
        'id': '1',
        'slug': 'feature1',
        'type': 'str',
        'description': 'Feature 1',
        'domain': [],
    }

    line = {'id': '1', 'slug': 'line1'}

    tag = {'id': '1', 'slug': 'tag1'}

    @mockserver.json_handler('/supportai/supportai/v1/features')
    async def _features_resp(request):
        return {'features': [feature]}

    @mockserver.json_handler('/supportai/supportai/v1/entities')
    async def _entities_resp(request):
        return {'entities': []}

    @mockserver.json_handler('/supportai/supportai/v1/tags')
    async def _tags_resp(request):
        return {'tags': [tag]}

    @mockserver.json_handler('/supportai/supportai/v1/lines')
    async def _lines_resp(request):
        return {'lines': [line]}

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _topics_resp(request):
        return {
            'topics': [
                {'id': '1', 'slug': 'topic1', 'title': 'Topic 1'},
                {'id': '2', 'slug': 'topic2', 'title': 'Topic 2'},
                {'id': '3', 'slug': 'topic3', 'title': 'Topic 3'},
            ],
        }

    @mockserver.json_handler('/supportai/supportai/v1/scenarios')
    async def _scenarios_resp(request):
        return {
            'scenarios': [
                {
                    'id': '1',
                    'topic_id': '1',
                    'title': 'Scenario 1',
                    'available': True,
                    'rule': {'parts': ['feature1']},
                    'clarify_order': [feature],
                    'tags': [tag],
                    'actions': [
                        {
                            'type': 'response',
                            'defer_time_sec': 10,
                            'texts': ['Text 1', 'Text2'],
                            'forward_line': 'line1',
                            'close': False,
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler('/supportai/supportai/v1/model_topics')
    async def _thresholds_resp(request):
        return {
            'model_topics': [
                {
                    'slug': 'topic1',
                    'key_metric': 'precision',
                    'threshold': 0.8,
                },
                {
                    'slug': 'topic2',
                    'key_metric': 'precision',
                    'threshold': 0.9,
                },
                {
                    'slug': 'topic3',
                    'key_metric': 'precision',
                    'threshold': 0.7,
                },
            ],
        }

    @mockserver.json_handler('/supportai/v1/versions/draft/release')
    async def _version_hidden_resp(request):
        return {
            'id': '2',
            'hidden': False,
            'draft': False,
            'created': datetime.datetime.now().isoformat(),
            'version': 1,
        }


@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
@pytest.mark.yt(static_table_data=['yt_validation_metrics.yaml'])
@pytest.mark.project(slug='sample_project')
async def test_validation_task(
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        yt_client,
        mocked_supportai,
        create_task,
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

    task = create_task(type_='validation')

    await stq_runner.supportai_admin_export.call(
        task_id='val_task', args=(), kwargs={'task_id': task.id},
    )

    assert (
        task.status == base_task.TaskStatus.PROCESSING.value
    ), f'Error message: {task.error_message}'

    await stq_runner.supportai_admin_export.call(
        task_id='val_task', args=(), kwargs={'task_id': task.id},
    )

    assert _stq_reschedule.times_called == 1

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), f'Error message: {task.error_message}'

    async with stq3_context.pg.slave_pool.acquire() as conn:
        results = await db_models.ValidationResult.select_by_project_and_task(
            stq3_context, conn, int(task.project_id), task.id,
        )

        assert len(results) == 3
