import pytest

from segment_splitter.generated.cron import run_monrun
from segment_splitter.generated.stq3 import stq_context


CRM_EFFICIENCY_MONRUN = {'number_of_failures_limit_in_24hours': 1}


@pytest.mark.now('2021-05-26 13:00:00')
@pytest.mark.pgsql('segment_splitter', files=['failed.sql'])
@pytest.mark.config(SEGMENT_SPLITTER_MONRUN=CRM_EFFICIENCY_MONRUN)
async def test_num_of_failures(stq3_context: stq_context.Context):
    msg = await run_monrun.run(
        ['segment_splitter.monrun_checks.check_failures'],
    )
    assert (
        msg == '1; Monrun failed: '
        'Number of accepted failures in 24 hours: 1, current: 2'
    )
