import pytest

from taxi.stq import async_worker_ng

from segment_splitter import entity
from segment_splitter import storage
from segment_splitter.stq import run_spark

TASK_ID = 'b12d3940-1bcd-424b-9a57-b3b02762c493'

SEGMENT_SPLITTER_SETTINGS = {
    'instance_id': 'a12d3940-1bcd-424b-9a57-b3b02762c493',
    'workflow_id': '1363da95-a6cc-45bb-ae7b-643ed902812f',
    'workflow_timeout_in_seconds': 86400,
    'workflow_retry_period_in_seconds': 60,
}


async def run_stq(stq3_context, spark_task, mockserver):
    task_info = async_worker_ng.TaskInfo(
        id='campaign_1_task_1',
        exec_tries=1,
        reschedule_counter=1,
        queue='segment_splitter_run_nirvana',
    )
    await run_spark.task(
        stq3_context,
        task_info,
        spark_task.id_,
        [{'output_segments_path': '//home/path', 'param2': '123456'}],
    )


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_submit(stq3_context, mockserver, patch):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json == {
            'queue_name': 'segment_splitter_run_spark',
            'eta': '1970-01-01T00:00:00.000000Z',
            'task_id': 'campaign_1_task_1',
        }
        return {}

    @patch('crm_common.spark_submit.SparkSubmit.spark_submit_no_wait')
    async def _submit_spark(*args, **kwargs):
        return TASK_ID

    task_storage = storage.DbTask(stq3_context)
    spark_task = await task_storage.create(TASK_ID)

    await run_stq(stq3_context, spark_task, mockserver)

    assert _stq_reschedule.times_called == 1

    # task is updated
    spark_task = await task_storage.fetch(spark_task.id_)
    assert spark_task.instance_id == TASK_ID
    assert spark_task.state == entity.TaskState.STARTED


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_poll(stq3_context, mockserver, patch):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'segment_splitter_run_spark'
        assert request.json['task_id'] == 'campaign_1_task_1'
        return {}

    @patch('crm_common.spark_submit.SparkSubmit.poll')
    async def _poll_spark(*args, **kwargs):
        return 'RUNNING'

    task_storage = storage.DbTask(stq3_context)
    spark_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        spark_task, instance_id=TASK_ID, state=entity.TaskState.STARTED,
    )

    await run_stq(stq3_context, spark_task, mockserver)

    assert len(_poll_spark.calls) == 1
    assert _stq_reschedule.times_called == 1

    # task is updated
    spark_task = await task_storage.fetch(spark_task.id_)
    assert spark_task.state == entity.TaskState.STARTED


@pytest.mark.config(SEGMENT_SPLITTER_SETTINGS=SEGMENT_SPLITTER_SETTINGS)
async def test_finish(stq, stq3_context, stq_runner, mockserver, patch):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        assert request.json['queue_name'] == 'segment_splitter_run_spark'
        assert request.json['task_id'] == 'campaign_1_task_1'
        return {}

    @patch('crm_common.spark_submit.SparkSubmit.poll')
    async def _poll_spark(*args, **kwargs):
        return 'FINISHED'

    task_storage = storage.DbTask(stq3_context)
    spark_task = await task_storage.create(TASK_ID)
    await task_storage.update(
        spark_task, instance_id=TASK_ID, state=entity.TaskState.STARTED,
    )

    await run_stq(stq3_context, spark_task, mockserver)

    assert len(_poll_spark.calls) == 1
    assert _stq_reschedule.times_called == 1

    # task is updated
    spark_task = await task_storage.fetch(spark_task.id_)
    assert spark_task.state == entity.TaskState.FINISHED
