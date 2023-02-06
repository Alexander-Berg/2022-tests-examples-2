import pytest

from taxi.stq import async_worker_ng
from taxi.util import dates

from mayak_inspector.common import constants
from mayak_inspector.common.utils import stq as stq_utils
from mayak_inspector.storage.ydb import extractors
from mayak_inspector.stq import setup_jobs


@pytest.mark.yt(static_table_data=['yt_metrics_sample.yaml'])
@pytest.mark.parametrize(
    'kwargs',
    [
        pytest.param(
            {
                'extra': {
                    'source_id': 1,
                    'name': '//home/testsuite/metrics',
                    'original_entity_field': 'unique_driver_id',
                    'reason_suffix': '_order_ids',
                    'mayak_import_uuid': 1,
                },
                'job_type': constants.JobTypes.import_yt_metrics.value,
            },
            id='default',
        ),
    ],
)
async def test_trigger_setup_job(stq3_context, stq, kwargs, patch):
    # TODO: replace with better mock EFFICIENCYDEV-18210
    @patch('mayak_inspector.storage.ydb.metrics.MetricsRepo.get_import')
    async def _execute(*args, **kwargs):
        return extractors.ImportRecord(
            mayak_import_uuid=1,
            name=str(),
            locked=False,
            loaded=False,
            created_at=dates.localize(),
            updated_at=dates.localize(),
        )

    # test setup
    job_id = await stq_utils.setup_job(
        stq3_context, **kwargs, queue_name=constants.StqQueueNames.setup_jobs,
    )
    task = stq.mayak_inspector_setup_jobs.next_call()
    assert task['kwargs'] == kwargs

    # stq_runner call ignores patches
    task_info = async_worker_ng.TaskInfo(
        job_id, 0, 0, queue=constants.StqQueueNames.setup_jobs.value,
    )
    await setup_jobs.task(stq3_context, task_info, **kwargs)
