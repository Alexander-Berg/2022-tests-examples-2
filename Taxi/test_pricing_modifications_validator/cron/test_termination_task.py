# pylint: disable=redefined-outer-name
import pytest

from pricing_modifications_validator.generated.cron import run_cron
from ..plugins.mock_pricing_admin import mock_pricing_admin  # noqa: F401


@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
@pytest.mark.config(
    MAX_VALIDATION_TIME_FROM_START=30, MAX_VALIDATION_TIME_FROM_UPDATE=15,
)
async def test_termination_task(
        mockserver, mock_pricing_admin, select_named,  # noqa F811
):
    await run_cron.main(
        ['pricing_modifications_validator.crontasks.termination', '-t', '0'],
    )
    script_tasks = {
        task['id']: task
        for task in select_named(
            'SELECT id, task_state, message FROM db.script_tasks',
        )
    }
    assert script_tasks[1]['task_state'] == 'Terminated'
    assert (
        script_tasks[1]['message'] == 'max validation time from start expired'
    )
    assert script_tasks[2]['task_state'] == 'InProgress'
    assert script_tasks[3]['task_state'] == 'Terminated'
    assert (
        script_tasks[3]['message']
        == 'max validation time from last update expired'
    )
    assert script_tasks[4]['task_state'] == 'InProgress'
    assert script_tasks[5]['task_state'] == 'Finished'
