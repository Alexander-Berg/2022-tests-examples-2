import pytest

from crm_admin.stq import calculations_processing


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_stq_was_not_started(stq3_context, patch, mock):
    class TaskInfo:
        id = 'task_id'  # pylint: disable=invalid-name
        exec_tries = 0

    calculations_processing.get_operation_by_stage = mock(
        lambda *args, **kwargs: ...,
    )

    campaign_id = 4
    operation_id = 1

    await calculations_processing.task(
        context=stq3_context,
        task_info=TaskInfo(),
        campaign_id=campaign_id,
        operation_id=operation_id,
        mode='something',
        stage='something',
    )

    assert not calculations_processing.get_operation_by_stage.calls
