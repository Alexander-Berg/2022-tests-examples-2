# pylint: disable=unused-variable

import datetime

import asynctest
import pytest

from crm_admin import entity
from crm_admin import settings
from crm_admin import storage
from crm_admin.entity import error
from crm_admin.utils import pollable_operation


CRM_ADMIN_TEST_SETTINGS = {
    'SparkSettings': {
        'discovery_path': 'discovery_path',
        'spark3_discovery_path': 'spark3_discovery_path',
    },
}


class DummyPollableOp(pollable_operation.PollableOperation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_started_called = False
        self.on_finished_called = False
        self.status_ok = False

    async def _on_started(self):
        self.on_started_called = True

    async def _on_finished(self, ok, result):
        self.on_finished_called = True
        self.status_ok = ok


class DummyPollableYqlOp(DummyPollableOp):
    async def _on_started(self):
        await super()._on_started()
        await self._submit_pollable_yql_query('query')


class DummyPollableSparkOp(DummyPollableOp):
    async def _on_started(self):
        await super()._on_started()
        await self._submit_pollable_spark_job('spark-job.py')


class DummyPollableSplitterOp(DummyPollableOp):
    async def _on_started(self):
        await super()._on_started()
        await self._submit_pollable_splitter_job(
            {
                'unique_entity_attr': 'user_id',
                'input_table': '//table',
                'output_table': '//table_out',
                'groups': [],
                'sub_segment_id': 'group_id',
                'salt': 'salt',
                'split_col_name': 'split_col_name',
                'metrics': ['metric #1'],
            },
        )


class DummyNonPollableOp(DummyPollableYqlOp):
    async def _on_started(self):
        self.on_started_called = True


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_stq_task(stq3_context):
    campaign_id = 1
    operation_name = 'operation_name'
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.call = asynctest.CoroutineMock()

    await pollable_operation.PollableOperation.start_stq_task(
        context=stq3_context,
        campaign_id=campaign_id,
        operation_name=operation_name,
        stq_queue_caller=stq_queue_caller,
        stq_task_id=stq_task_id,
    )

    stq_queue_caller.call.assert_awaited_once()
    _, kwargs = stq_queue_caller.call.call_args

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(kwargs['kwargs']['operation_id'])
    assert operation.campaign_id == campaign_id
    assert operation.operation_name == operation_name


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_stq_task_later(stq3_context):
    campaign_id = 1
    operation_name = 'operation_name'
    stq_task_id = 'stq_task_id'
    eta = datetime.datetime.now()

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.call_later = asynctest.CoroutineMock()

    await pollable_operation.PollableOperation.start_stq_task(
        context=stq3_context,
        campaign_id=campaign_id,
        operation_name=operation_name,
        stq_queue_caller=stq_queue_caller,
        stq_task_id=stq_task_id,
        eta=eta,
    )

    stq_queue_caller.call_later.assert_awaited_once()
    _, kwargs = stq_queue_caller.call_later.call_args

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(kwargs['kwargs']['operation_id'])
    assert operation.campaign_id == campaign_id
    assert operation.operation_name == operation_name


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_yql_operation(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.yql.YqlSqlOperationRequest')
    class YqlSqlOperationRequest:
        operation_id = 'opeartion_id'
        status = 'RUNNING'
        share_url = 'YQL shared URL'

        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            pass

    operation_id = 1
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableYqlOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    assert task.on_started_called
    assert not task.on_finished_called
    stq_queue_caller.reschedule.assert_awaited_once()

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == YqlSqlOperationRequest.status
    assert operation.submission_id == YqlSqlOperationRequest.operation_id
    assert operation.operation_type == entity.OperationType.YQL
    assert operation.extra_data == {
        'yql_shared_url': YqlSqlOperationRequest.share_url,
    }


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_spark_operation(stq3_context, patch):
    @patch(
        'crm_admin.utils.pollable_operation.spark_submit.spark_submit_no_wait',
    )
    async def spark_submit_no_wait(*args, **kwargs):
        return 'submission_id'

    @patch(
        'crm_admin.utils.pollable_operation.spark_submit.spark_discovery_path',
    )
    def spark_discovery_path(*args, **kwargs):
        return CRM_ADMIN_TEST_SETTINGS['SparkSettings'][
            'spark3_discovery_path'
        ]

    @patch(
        'crm_admin.utils.pollable_operation.spark_submit.get_driver_logs_address',  # noqa: E501
    )
    async def get_driver_logs_address(*args, **kwargs):
        return 'http://...'

    operation_id = 1
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableSparkOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    assert task.on_started_called
    assert not task.on_finished_called
    stq_queue_caller.reschedule.assert_awaited_once()

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == 'OP_SUBMITTED'
    assert operation.submission_id == 'submission_id'
    assert operation.operation_type == entity.OperationType.SPARK
    assert operation.extra_data == {'discovery_path': spark_discovery_path()}


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_splitter_operation(stq3_context, mockserver):
    @mockserver.json_handler('segment-splitter/v1/splitting/create')
    def _create_splitting(request):
        return {
            'id': '00000000-0000-0000-0000-000000000000',
            'status': 'random_status',
        }

    operation_id = 1
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableSplitterOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    assert task.on_started_called
    assert not task.on_finished_called
    stq_queue_caller.reschedule.assert_awaited_once()

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == 'OP_SUBMITTED'
    assert operation.operation_type == entity.OperationType.SPLITTER


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_yql_operation_error(stq3_context, patch):
    class ErrorTask(DummyNonPollableOp):
        def _on_started(self):
            raise error.OperationFailure('some error')

    operation_id = 1
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = ErrorTask(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    assert task.on_finished_called
    assert not task.status_ok

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == entity.OperationStatus.OP_FAILURE.value
    assert operation.finished_at is not None


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_yql_operation_general_error(stq3_context, patch):
    class ErrorTask(DummyNonPollableOp):
        def _on_started(self):
            raise RuntimeError('some error')

    operation_id = 1
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = ErrorTask(stq3_context, operation_id)
    with pytest.raises(RuntimeError):
        await task.execute(
            stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
        )

    assert not task.on_finished_called
    assert not task.status_ok

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == 'OP_ERROR'
    assert operation.finished_at is None


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_operation_non_pollable(stq3_context, patch):
    operation_id = 1
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.call = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyNonPollableOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    stq_queue_caller.call.assert_not_called()
    stq_queue_caller.reschedule.assert_not_called()
    assert task.on_started_called
    assert task.on_finished_called
    assert task.status_ok

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status is None
    assert operation.submission_id is None
    assert operation.finished_at is not None


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_poll_yql_operation(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.yql.YqlOperationResultsRequest')
    class YqlOperationResultsRequest:
        status = 'ABORTING'

        IN_PROGRESS_STATUSES = ['RUNNING', 'ABORTING']

        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            pass

    operation_id = 2
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableYqlOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    stq_queue_caller.reschedule.assert_awaited_once()
    assert not task.on_started_called
    assert not task.on_finished_called

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == YqlOperationResultsRequest.status
    assert operation.finished_at is None


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_poll_spark_operation(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.spark_submit.poll')
    async def poll(*args, **kwargs):
        return 'RUNNING'

    operation_id = 4
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableSparkOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    stq_queue_caller.reschedule.assert_awaited_once()
    assert not task.on_started_called
    assert not task.on_finished_called

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == await poll()
    assert operation.finished_at is None


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_poll_splitter_operation(stq3_context, mockserver):
    @mockserver.json_handler('segment-splitter/v1/splitting/status')
    def _splitting_status(request):
        return {
            'id': '00000000-0000-0000-0000-000000000000',
            'status': 'STARTED',
            'segment_path': '//table',
            'output_path': '//table_out',
            'resalt_count': 0,
            'group_metrics_path': '//path',
        }

    operation_id = 8
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableSplitterOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    stq_queue_caller.reschedule.assert_awaited_once()
    assert not task.on_started_called
    assert not task.on_finished_called

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == entity.OperationStatus.RUNNING.value
    assert operation.finished_at is None


@pytest.mark.parametrize(
    'op_status, is_ok',
    [('COMPLETED', True), ('ERROR', False), ('NOT_FOUND', False)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_yql_operation(stq3_context, patch, op_status, is_ok):
    @patch('crm_admin.utils.pollable_operation.yql.YqlOperationResultsRequest')
    class YqlOperationResultsRequest:
        status = op_status
        result = 'result'

        IN_PROGRESS_STATUSES = ['RUNNING', 'ABORTING']

        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            pass

    operation_id = 2
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.call = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableYqlOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    stq_queue_caller.call.assert_not_called()
    stq_queue_caller.reschedule.assert_not_called()
    assert task.on_finished_called
    assert task.status_ok == is_ok


@pytest.mark.parametrize(
    'op_status, is_ok',
    [('FINISHED', True), ('FAILED', False), ('NOT_FOUND', False)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_spark_operation(stq3_context, patch, op_status, is_ok):
    @patch('crm_admin.utils.pollable_operation.spark_submit.poll')
    async def poll(*args, **kwargs):
        return op_status

    operation_id = 4
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.call = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableYqlOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    stq_queue_caller.call.assert_not_called()
    stq_queue_caller.reschedule.assert_not_called()
    assert task.on_finished_called
    assert task.status_ok == is_ok


@pytest.mark.parametrize(
    'op_status, is_ok', [('FINISHED', True), ('FAILED', False)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_splitter_operation(
        stq3_context, mockserver, op_status, is_ok,
):
    @mockserver.json_handler('segment-splitter/v1/splitting/status')
    def _splitting_status(request):
        return {
            'id': '00000000-0000-0000-0000-000000000000',
            'status': op_status,
            'segment_path': '//table',
            'output_path': '//table_out',
            'resalt_count': 0,
            'group_metrics_path': '//path',
        }

    operation_id = 8
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.call = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableSplitterOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    stq_queue_caller.call.assert_not_called()
    stq_queue_caller.reschedule.assert_not_called()
    assert task.on_finished_called
    assert task.status_ok == is_ok


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_already_finished_operation(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.yql.YqlOperationResultsRequest')
    class YqlOperationResultsRequest:
        status = 'FINISHED'

        IN_PROGRESS_STATUSES = ['RUNNING', 'ABORTING']

        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            pass

    operation_id = 3
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.call = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = DummyPollableOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    stq_queue_caller.call.assert_not_called()
    stq_queue_caller.reschedule.assert_not_called()
    assert not task.on_finished_called


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_abort_at_start(stq3_context, patch):
    class Operation(DummyPollableOp):
        def _on_started(self):
            raise error.OperationFailure('error')

    operation_id = 1
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.reschedule = asynctest.CoroutineMock()

    task = Operation(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == entity.OperationStatus.OP_FAILURE.value
    stq_queue_caller.reschedule.assert_not_called()


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_abort_at_finish(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.spark_submit.poll')
    async def poll(*args, **kwargs):
        return 'FINISHED'

    class Operation(DummyPollableOp):
        async def _on_finished(self, ok, result):
            raise error.OperationFailure('error')

    operation_id = 4
    stq_task_id = 'stq_task_id'
    stq_queue_caller = asynctest.CoroutineMock()

    task = Operation(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == entity.OperationStatus.OP_FAILURE.value
    assert operation.finished_at is not None


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_error_at_finish(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.spark_submit.poll')
    async def poll(*args, **kwargs):
        return 'FINISHED'

    class Operation(DummyPollableOp):
        def _on_finished(self, ok, result):
            raise RuntimeError('-')

    operation_id = 4
    stq_task_id = 'stq_task_id'
    stq_queue_caller = asynctest.CoroutineMock()

    task = Operation(stq3_context, operation_id)
    with pytest.raises(RuntimeError):
        await task.execute(
            stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
        )

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.finished_at is None


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_cancel(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.spark_submit.poll')
    async def poll(*args, **kwargs):
        return 'KILLED'

    class Operation(DummyPollableOp):
        on_canceled_called = 0
        on_finished_called = 0

        async def _on_finished(self, ok, result):
            self.on_finished_called += 1
            raise error.OperationFailure('error')

        async def _on_canceled(self):
            self.on_canceled_called += 1

    operation_id = 4
    stq_task_id = 'stq_task_id'
    stq_queue_caller = asynctest.CoroutineMock()

    db_operations = storage.DbOperations(stq3_context)
    await db_operations.abort(operation_id)

    task = Operation(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    assert task.on_finished_called == 0
    assert task.on_canceled_called == 1

    operation = await db_operations.fetch(operation_id)
    assert operation.status == 'KILLED'


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_cancel_default_handler(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.spark_submit.poll')
    async def poll(*args, **kwargs):
        return 'KILLED'

    class Operation(DummyPollableOp):
        on_finished_called = 0

        async def _on_finished(self, ok, result):
            self.on_finished_called += 1

    operation_id = 4
    stq_task_id = 'stq_task_id'
    stq_queue_caller = asynctest.CoroutineMock()

    task = Operation(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    assert task.on_finished_called == 1

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == 'KILLED'


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_abort_pollable_operation(stq3_context, patch):
    @patch('crm_admin.utils.startrek.trigger.try_to_terminate')
    async def try_to_terminate(*args, **kwargs):
        pass

    campaign_id = 4

    await pollable_operation.PollableOperation.abort(
        stq3_context,
        campaign_id,
        expected_states=[settings.SEGMENT_PROCESSING_STATE],
        aborting_state=settings.SEGMENT_CANCELLING,
        target_state=settings.SEGMENT_EXPECTED_STATE,
    )

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch_last_by_campaign_id(campaign_id)
    assert operation.is_aborted

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_CANCELLING


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_chained_operations(stq3_context):
    campaign_id = 4
    parent_id = 7
    operation_name = 'operation_name'
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()
    stq_queue_caller.call = asynctest.CoroutineMock()

    await pollable_operation.PollableOperation.start_stq_task(
        context=stq3_context,
        campaign_id=campaign_id,
        operation_name=operation_name,
        stq_queue_caller=stq_queue_caller,
        stq_task_id=stq_task_id,
        parent_id=parent_id,
    )

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch_last_by_campaign_id(campaign_id)
    assert operation.chain_id == parent_id
    assert operation.operation_id != parent_id


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_lost_submission(stq3_context, patch):
    @patch('crm_admin.utils.pollable_operation.spark_submit.poll')
    async def poll(*args, **kwargs):
        return 'NOT_FOUND'

    operation_id = 4
    stq_task_id = 'stq_task_id'

    stq_queue_caller = asynctest.CoroutineMock()

    task = DummyPollableSparkOp(stq3_context, operation_id)
    await task.execute(
        stq_queue_caller=stq_queue_caller, stq_task_id=stq_task_id,
    )

    assert task.on_finished_called
    assert task.info['status'] == await poll()

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(operation_id)
    assert operation.status == await poll()
    assert operation.finished_at
