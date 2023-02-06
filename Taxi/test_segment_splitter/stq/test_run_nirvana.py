import pytest

from taxi.stq import async_worker_ng

from segment_splitter import entity
from segment_splitter import storage
from segment_splitter.stq import run_nirvana

TASK_ID = 'b12d3940-1bcd-424b-9a57-b3b02762c493'

SEGMENT_SPLITTER_SETTINGS = {
    'instance_id': 'a12d3940-1bcd-424b-9a57-b3b02762c493',
    'workflow_id': '1363da95-a6cc-45bb-ae7b-643ed902812f',
    'workflow_timeout_in_seconds': 86400,
    'workflow_retry_period_in_seconds': 60,
}


async def run_stq(stq3_context, nirvana_task, mockserver, patch):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'segment_splitter_run_nirvana'
        assert request.json['task_id'] == 'campaign_1_task_1'
        return {}

    @mockserver.json_handler('/nirvana-api/getExecutionState')
    async def _get_state_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        assert request.json['params'] == {'workflowInstanceId': TASK_ID}
        return {'result': {'status': 'running', 'result': 'undefined'}}

    task_info = async_worker_ng.TaskInfo(
        id='campaign_1_task_1',
        exec_tries=1,
        reschedule_counter=1,
        queue='segment_splitter_run_nirvana',
    )
    await run_nirvana.task(
        stq3_context,
        task_info,
        nirvana_task.id_,
        'source_instance_id1',
        'target_workflow_id1',
        [
            {'parameter': 'output_path', 'value': 'string param'},
            {'parameter': 'param2', 'value': 123456},
        ],
    )
    assert _stq_reschedule.times_called == 1


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_clone(stq, stq3_context, stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json == {
            'queue_name': 'segment_splitter_run_nirvana',
            'eta': '1970-01-01T00:00:00.000000Z',
            'task_id': 'campaign_1_task_1',
        }
        return {}

    @mockserver.json_handler('/nirvana-api/cloneWorkflowInstance')
    async def _clone_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        return {'result': TASK_ID}

    task_storage = storage.DbTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)

    await stq_runner.segment_splitter_run_nirvana.call(
        task_id='campaign_1_task_1',
        args=(
            nirvana_task.id_,
            'source_instance_id1',
            'target_workflow_id1',
            [
                {'parameter': 'param1', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
            ],
        ),
    )

    assert _stq_reschedule.times_called == 1

    # task is updated
    nirvana_task = await task_storage.fetch(nirvana_task.id_)
    assert nirvana_task.instance_id == TASK_ID
    assert nirvana_task.state == entity.TaskState.CLONED


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_start(stq, stq3_context, stq_runner, mockserver, patch):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json == {
            'queue_name': 'segment_splitter_run_nirvana',
            'eta': '1970-01-01T00:00:00.000000Z',
            'task_id': 'campaign_1_task_1',
        }
        return {}

    @mockserver.json_handler('/nirvana-api/setGlobalParameters')
    async def _set_params_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        expected_params = {
            'workflowInstanceId': TASK_ID,
            'params': [
                {'parameter': 'param1', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
                {
                    'parameter': 'path_to_spark_file',
                    'value': (
                        '//tmp/crm-efficiency/testing/'
                        'task_id/run_splitter_checker.py'
                    ),
                },
            ],
        }
        request.json['params']['params'].pop()  # pop path_to_spark_file
        for key, val in expected_params.items():
            assert request.json['params'][key] == val
        return {'result': 'ok'}

    @mockserver.json_handler('/nirvana-api/startWorkflow')
    async def _start_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        return {'result': 'ok'}

    task_storage = storage.DbTask(stq3_context)
    nirvana_task = await task_storage.create('task_id')
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.CLONED,
    )

    await stq_runner.segment_splitter_run_nirvana.call(
        task_id='campaign_1_task_1',
        args=(
            nirvana_task.id_,
            'source_instance_id1',
            'target_workflow_id1',
            [
                {'parameter': 'param1', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
            ],
        ),
    )

    assert _set_params_handler.times_called == 1
    assert _start_handler.times_called == 1
    assert _stq_reschedule.times_called == 1

    # task is updated
    nirvana_task = await task_storage.fetch(nirvana_task.id_)
    assert nirvana_task.state == entity.TaskState.STARTED


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_poll(stq, stq3_context, stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'segment_splitter_run_nirvana'
        assert request.json['task_id'] == 'campaign_1_task_1'
        return {}

    @mockserver.json_handler('/nirvana-api/getExecutionState')
    async def _get_state_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        assert request.json['params'] == {'workflowInstanceId': TASK_ID}
        return {'result': {'status': 'running', 'result': 'undefined'}}

    task_storage = storage.DbTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.STARTED,
    )

    await stq_runner.segment_splitter_run_nirvana.call(
        task_id='campaign_1_task_1',
        args=(
            nirvana_task.id_,
            'source_instance_id1',
            'target_workflow_id1',
            [
                {'parameter': 'param1', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
            ],
        ),
    )

    assert _get_state_handler.times_called == 1
    assert _stq_reschedule.times_called == 1

    # task is updated
    nirvana_task = await task_storage.fetch(nirvana_task.id_)
    assert nirvana_task.state == entity.TaskState.STARTED
    assert nirvana_task.instance_status == 'running'
    assert nirvana_task.instance_result == 'undefined'


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_finish(stq, stq3_context, stq_runner, mockserver, patch):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'segment_splitter_run_nirvana'
        assert request.json['task_id'] == 'campaign_1_task_1'
        return {}

    @mockserver.json_handler('/nirvana-api/getExecutionState')
    async def _get_state_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        assert request.json['params'] == {'workflowInstanceId': TASK_ID}
        return {'result': {'status': 'completed', 'result': 'success'}}

    task_storage = storage.DbTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.STARTED,
    )

    await stq_runner.segment_splitter_run_nirvana.call(
        task_id='campaign_1_task_1',
        args=(
            nirvana_task.id_,
            'source_instance_id1',
            'target_workflow_id1',
            [
                {'parameter': 'output_path', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
            ],
        ),
    )

    assert _get_state_handler.times_called == 1
    assert _stq_reschedule.times_called == 1

    # task is updated
    nirvana_task = await task_storage.fetch(nirvana_task.id_)
    assert nirvana_task.state == entity.TaskState.FINISHED
