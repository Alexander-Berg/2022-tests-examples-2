import pytest

from crm_admin.generated.cron import run_monrun
from crm_admin.monrun_checks.checkers import base

CRM_ADMIN_EFFICIENCY_SETTINGS = {
    'efficiency_resolution_sla_in_hours': {'User': 72, 'Driver': 168},
}

OFF_CRM_ADMIN_EFFICIENCY_SETTINGS = {
    'efficiency_resolution_sla_in_hours': {'User': 0},
}


@pytest.mark.now('2022-12-12 09:00:00')
@pytest.mark.pgsql('crm_admin', files=['frozen.sql'])
@pytest.mark.config(
    CRM_ADMIN_EFFICIENCY_SETTINGS=CRM_ADMIN_EFFICIENCY_SETTINGS,
)
async def test_frozen_efficiency_campaigns():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_efficiency_campaigns_states',
            'campaign_efficiency_analysis',
        ],
    )

    assert (
        msg == '1; Frozen campaigns in status EFFICIENCY_ANALYSIS: '
        '(campaign id: 1), '
        '(campaign id: 2), '
        '(campaign id: 4).'
    )


@pytest.mark.now('2022-12-12 09:00:00')
@pytest.mark.pgsql('crm_admin', files=['frozen.sql'])
@pytest.mark.config(
    CRM_ADMIN_EFFICIENCY_SETTINGS=OFF_CRM_ADMIN_EFFICIENCY_SETTINGS,
)
async def test_efficiency_campaigns_check_is_off():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_efficiency_campaigns_states',
            'campaign_efficiency_analysis',
        ],
    )

    assert msg == f'0; {base.BaseChecker.SUCCESS_DESCRIPTION}'


@pytest.mark.now('2022-12-12 09:00:00')
@pytest.mark.pgsql('crm_admin', files=['not_frozen.sql'])
@pytest.mark.config(
    CRM_ADMIN_EFFICIENCY_SETTINGS=CRM_ADMIN_EFFICIENCY_SETTINGS,
)
async def test_not_frozen_efficiency_campaigns():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_efficiency_campaigns_states',
            'campaign_efficiency_analysis',
        ],
    )

    assert msg == f'0; {base.BaseChecker.SUCCESS_DESCRIPTION}'
