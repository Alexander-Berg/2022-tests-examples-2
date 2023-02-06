import pytest

from taxi.stq import async_worker_ng

from crm_efficiency import entity
from crm_efficiency import storage
from crm_efficiency.stq import run_spark

TASK_ID = 'b12d3940-1bcd-424b-9a57-b3b02762c493'

NIRVANA_SETTINGS = {
    'instance_id': 'a12d3940-1bcd-424b-9a57-b3b02762c493',
    'workflow_id': '1363da95-a6cc-45bb-ae7b-643ed902812f',
    'workflow_timeout_in_seconds': 86400,
    'workflow_retry_period_in_seconds': 60,
}
CRM_HUB_SETTINGS = {
    'dry_run': False,
    'item_sending_timeout_in_seconds': 10,
    'enabled': True,
}
CRM_HUB_SETTINGS_DISABLED = {
    'dry_run': False,
    'item_sending_timeout_in_seconds': 10,
    'enabled': False,
}
CRM_HUB_SETTINGS_DRY_RUN = {
    'dry_run': True,
    'item_sending_timeout_in_seconds': 10,
    'enabled': True,
}
SPARK_SETTINGS = {
    'spark3_discovery_path': '//home/taxi-crm/production/spark',
    'output_path': '//tmp/crm-efficiency/testing',
    'temp_path': '//tmp/crm-efficiency',
}
CRM_EFFICIENCY_SETTINGS = {
    'NirvanaSettings': NIRVANA_SETTINGS,
    'CrmHubSettings': CRM_HUB_SETTINGS,
    'SparkSettings': SPARK_SETTINGS,
}
CRM_EFFICIENCY_SETTINGS_CRM_HUB_DISABLED = {
    'NirvanaSettings': NIRVANA_SETTINGS,
    'CrmHubSettings': CRM_HUB_SETTINGS_DISABLED,
    'SparkSettings': SPARK_SETTINGS,
}
CRM_EFFICIENCY_SETTINGS_DRY_RUN = {
    'NirvanaSettings': NIRVANA_SETTINGS,
    'CrmHubSettings': CRM_HUB_SETTINGS_DRY_RUN,
    'SparkSettings': SPARK_SETTINGS,
}


async def run_stq(stq3_context, nirvana_task, mockserver, mock_crm_hub, patch):
    @patch('crm_efficiency.stq.run_spark._copy_if_exists')
    async def _copy_if_exists(context, *args, **kwargs):
        pass

    @patch('crm_efficiency.stq.run_spark._check_if_exists')
    async def _check_if_exists(context, *args, **kwargs):
        return False

    @mock_crm_hub('/v1/communication/efficiency/new')
    async def _crm_hub(context, *args, **kwargs):
        return {'table_path': 'table_path', 'id': TASK_ID, 'state': 'new'}

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'crm_efficiency_run_spark'
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
        queue='crm_efficiency_run_spark',
    )
    await run_spark.task(
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


@pytest.mark.config(CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS)
async def test_clone(stq, stq3_context, stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json == {
            'queue_name': 'crm_efficiency_run_spark',
            'eta': '1970-01-01T00:00:00.000000Z',
            'task_id': 'campaign_1_task_1',
        }
        return {}

    @mockserver.json_handler('/nirvana-api/cloneWorkflowInstance')
    async def _clone_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        return {'result': TASK_ID}

    task_storage = storage.DbNirvanaTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)

    await stq_runner.crm_efficiency_run_spark.call(
        task_id='campaign_1_task_1',
        args=(
            nirvana_task.id_,
            'source_instance_id1',
            'target_workflow_id1',
            [
                {'parameter': 'param1', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
                {'parameter': 'output_path', 'value': 'string param'},
            ],
        ),
    )

    assert _stq_reschedule.times_called == 1

    # task is updated
    nirvana_task = await task_storage.fetch(nirvana_task.id_)
    assert nirvana_task.instance_id == TASK_ID
    assert nirvana_task.state == entity.TaskState.CLONED


@pytest.mark.config(CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS)
async def test_start(stq, stq3_context, stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json == {
            'queue_name': 'crm_efficiency_run_spark',
            'eta': '1970-01-01T00:00:00.000000Z',
            'task_id': 'campaign_1_task_1',
        }
        return {}

    @mockserver.json_handler('/nirvana-api/setGlobalParameters')
    async def _set_params_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        assert request.json['params'] == {
            'workflowInstanceId': TASK_ID,
            'params': [
                {'parameter': 'param1', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
                {
                    'parameter': 'output_path',
                    'value': '//tmp/crm-efficiency/table',
                },
            ],
        }
        return {'result': 'ok'}

    @mockserver.json_handler('/nirvana-api/startWorkflow')
    async def _start_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        return {'result': 'ok'}

    task_storage = storage.DbNirvanaTask(stq3_context)
    nirvana_task = await task_storage.create('task_id')
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.CLONED,
    )

    await stq_runner.crm_efficiency_run_spark.call(
        task_id='campaign_1_task_1',
        args=(
            nirvana_task.id_,
            'source_instance_id1',
            'target_workflow_id1',
            [
                {'parameter': 'param1', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
                {'parameter': 'output_path', 'value': '/table'},
            ],
        ),
    )

    assert _set_params_handler.times_called == 1
    assert _start_handler.times_called == 1
    assert _stq_reschedule.times_called == 1

    # task is updated
    nirvana_task = await task_storage.fetch(nirvana_task.id_)
    assert nirvana_task.state == entity.TaskState.STARTED


@pytest.mark.config(CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS)
async def test_poll(stq, stq3_context, stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'crm_efficiency_run_spark'
        assert request.json['task_id'] == 'campaign_1_task_1'
        return {}

    @mockserver.json_handler('/nirvana-api/getExecutionState')
    async def _get_state_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        assert request.json['params'] == {'workflowInstanceId': TASK_ID}
        return {'result': {'status': 'running', 'result': 'undefined'}}

    task_storage = storage.DbNirvanaTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.STARTED,
    )

    await stq_runner.crm_efficiency_run_spark.call(
        task_id='campaign_1_task_1',
        args=(
            nirvana_task.id_,
            'source_instance_id1',
            'target_workflow_id1',
            [
                {'parameter': 'param1', 'value': 'string param'},
                {'parameter': 'param2', 'value': 123456},
                {'parameter': 'output_path', 'value': 'string param'},
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


@pytest.mark.config(CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS)
async def test_finish(stq, stq3_context, stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'crm_efficiency_run_spark'
        assert request.json['task_id'] == 'campaign_1_task_1'
        return {}

    @mockserver.json_handler('/nirvana-api/getExecutionState')
    async def _get_state_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        assert request.json['params'] == {'workflowInstanceId': TASK_ID}
        return {'result': {'status': 'completed', 'result': 'success'}}

    task_storage = storage.DbNirvanaTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.STARTED,
    )

    await stq_runner.crm_efficiency_run_spark.call(
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
    assert nirvana_task.state == entity.TaskState.SENDING


@pytest.mark.config(CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS)
async def test_crm_hub_add_item(
        stq, stq3_context, stq_runner, mockserver, mock_crm_hub, patch,
):
    task_storage = storage.DbNirvanaTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.SENDING,
    )
    await run_stq(stq3_context, nirvana_task, mockserver, mock_crm_hub, patch)

    # task is updated
    nirvana_task = await task_storage.fetch(nirvana_task.id_)

    assert nirvana_task.state == entity.TaskState.FINISHED
    assert nirvana_task.instance_result == 'success'


@pytest.mark.config(
    CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS_CRM_HUB_DISABLED,
)
async def test_crm_hub_disabled(stq, stq3_context, stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'crm_efficiency_run_spark'
        assert request.json['task_id'] == 'campaign_1_task_1'
        return {}

    @mockserver.json_handler('/nirvana-api/getExecutionState')
    async def _get_state_handler(request):
        assert request.method == 'POST', 'only POST are allowed'
        assert request.json['params'] == {'workflowInstanceId': TASK_ID}
        return {'result': {'status': 'completed', 'result': 'success'}}

    task_storage = storage.DbNirvanaTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.STARTED,
    )

    await stq_runner.crm_efficiency_run_spark.call(
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
    assert nirvana_task.instance_result == 'success'
    assert nirvana_task.instance_status == 'completed'


@pytest.mark.config(CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS_DRY_RUN)
async def test_crm_hub_dry_run(
        stq, stq3_context, stq_runner, mockserver, mock_crm_hub, patch,
):
    task_storage = storage.DbNirvanaTask(stq3_context)
    nirvana_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        nirvana_task, instance_id=TASK_ID, state=entity.TaskState.SENDING,
    )

    await run_stq(stq3_context, nirvana_task, mockserver, mock_crm_hub, patch)

    # task is updated
    nirvana_task = await task_storage.fetch(nirvana_task.id_)

    assert nirvana_task.state == entity.TaskState.FINISHED
    assert nirvana_task.instance_result == 'success'
    assert nirvana_task.instance_status == 'completed'
