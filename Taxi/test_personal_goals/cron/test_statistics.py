# pylint: disable=redefined-outer-name
import pytest

from personal_goals.crontasks.modules import statistics as module
from personal_goals.generated.cron import run_cron


async def run_statistics():
    await run_cron.main(['personal_goals.crontasks.statistics', '-t', '0'])


@pytest.mark.pgsql('personal_goals', files=['cleanup_goals.sql'])
async def test_default_statistics(cron_context):
    await run_statistics()

    result = await module.statistics.collect_metrics(cron_context)

    dict_result = {m.name: m.value for m in result}
    assert dict_result == {
        'active_goals': 1,
        'done_goals': 3,
        'missed_goals': 1,
        'rewarded_goals': 1,
        'visible_goals': 1,
    }
