# pylint: disable=redefined-outer-name
import pytest

from pricing_modifications_validator.generated.cron import run_cron
from ..plugins.mock_pricing_admin import mock_pricing_admin  # noqa: F401


@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
@pytest.mark.config(PMV_TASK_CLEANUP_PERIOD=24 * 7)
async def test_do_cleanup(
        mockserver, mock_pricing_admin, select_named,  # noqa F811
):
    await run_cron.main(
        ['pricing_modifications_validator.crontasks.cleanup', '-t', '0'],
    )
    script_tasks = select_named('SELECT id FROM db.script_tasks')
    assert set(script_task['id'] for script_task in script_tasks) == set(
        [1, 2, 4],
    )
    checks = select_named('SELECT script_id FROM db.checks')
    assert set(check['script_id'] for check in checks) == set([1, 2, 4])
