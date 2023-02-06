import typing

import pytest

from crm_admin.generated.cron import run_monrun
from crm_admin.monrun_checks.checkers import base

CRM_ADMIN_MONRUN: typing.Dict[str, typing.Dict] = {
    'Limits': {},
    'RegularCampaign': {'enabled': True},
}


@pytest.mark.now('2022-12-28 12:00:00')
@pytest.mark.pgsql('crm_admin', files=['not_frozen.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_not_frozen():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_frozen_regular_campaigns',
            'frozen_regular_campaigns',
        ],
    )
    assert msg == f'0; {base.BaseChecker.SUCCESS_DESCRIPTION}'


@pytest.mark.now('2022-12-28 12:00:00')
@pytest.mark.pgsql('crm_admin', files=['frozen.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_frozen():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_frozen_regular_campaigns',
            'frozen_regular_campaigns',
        ],
    )

    assert (
        msg == '1; Frozen regular campaigns in finished states: '
        '(log_id: 7 campaign_id: 2 state: GROUPS_FINISHED).\n'
        'Frozen scheduled campaigns: '
        '(log_id: 3 campaign_id: 3).'
    )


@pytest.mark.now('2022-12-28 12:00:00')
@pytest.mark.pgsql('crm_admin', files=['sending_ended.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_sending_ended():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_frozen_regular_campaigns',
            'frozen_regular_campaigns',
        ],
    )
    assert msg == '1; Frozen scheduled campaigns: (log_id: 1 campaign_id: 1).'
