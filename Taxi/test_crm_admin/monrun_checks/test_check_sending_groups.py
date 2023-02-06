import pytest

from crm_admin.generated.cron import run_monrun
from crm_admin.monrun_checks.checkers import base

CRM_ADMIN_MONRUN = {'Limits': {'group_sending_limit_in_seconds': 600}}


@pytest.mark.now('2022-12-12 12:00:00')
@pytest.mark.pgsql('crm_admin', files=['frozen.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_frozen_sending_groups():
    msg = await run_monrun.run(
        ['crm_admin.monrun_checks.check_sending_groups', 'group_sending'],
    )

    assert (
        msg == '1; Frozen sending groups: '
        '(log id: 1, group id: 1, campaign id: 1), '
        '(log id: 2, group id: 2, campaign id: 2), '
        '(log id: 7, group id: 6, campaign id: 2).'
    )


@pytest.mark.now('2022-12-12 12:00:00')
@pytest.mark.pgsql('crm_admin', files=['not_frozen.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_not_frozen_sending_groups():
    msg = await run_monrun.run(
        ['crm_admin.monrun_checks.check_sending_groups', 'group_sending'],
    )

    assert msg == f'0; {base.BaseChecker.SUCCESS_DESCRIPTION}'
