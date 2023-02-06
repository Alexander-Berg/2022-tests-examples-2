import pytest

from crm_efficiency.generated.cron import run_monrun
from crm_efficiency.generated.stq3 import stq_context

CRM_EFFICIENCY_MONRUN = {
    'processing_limit_in_minutes': 30,
    'last_time_execution_limit_in_minutes': 30,
    'number_of_failures_limit_in_24hours': 1,
}


@pytest.mark.now('2021-05-26 12:00:00')
@pytest.mark.pgsql('crm_efficiency', files=['started.sql'])
@pytest.mark.config(CRM_EFFICIENCY_MONRUN=CRM_EFFICIENCY_MONRUN)
async def test_success_no_timeout():
    msg = await run_monrun.run(['crm_efficiency.monrun_checks.check_timeout'])
    assert msg == '0; Monrun: Check done.'


@pytest.mark.now('2021-05-26 13:00:00')
@pytest.mark.pgsql('crm_efficiency', files=['finished.sql'])
@pytest.mark.config(CRM_EFFICIENCY_MONRUN=CRM_EFFICIENCY_MONRUN)
async def test_monrun_delay(stq3_context: stq_context.Context):
    msg = await run_monrun.run(
        ['crm_efficiency.monrun_checks.check_last_success'],
    )
    assert (
        msg == '1; Monrun failed: '
        'last success execution accepted 30, but it was 63 minutes ago'
    )


@pytest.mark.now('2021-05-26 13:00:00')
@pytest.mark.pgsql('crm_efficiency', files=['failed.sql'])
@pytest.mark.config(CRM_EFFICIENCY_MONRUN=CRM_EFFICIENCY_MONRUN)
async def test_num_of_failures(stq3_context: stq_context.Context):
    msg = await run_monrun.run(['crm_efficiency.monrun_checks.check_failures'])
    assert (
        msg == '1; Monrun failed: '
        'Number of accepted failures in 24 hours: 1, current: 2'
    )


@pytest.mark.now('2021-05-26 13:00:00')
@pytest.mark.pgsql('crm_efficiency', files=['started.sql'])
@pytest.mark.config(CRM_EFFICIENCY_MONRUN=CRM_EFFICIENCY_MONRUN)
async def test_monrun_timeout(stq3_context: stq_context.Context):
    msg = await run_monrun.run(['crm_efficiency.monrun_checks.check_timeout'])
    assert (
        msg == '1; Monrun failed: '
        'accepted timeout: 30, but current processing takes 73'
    )
