import pytest

from crm_admin.generated.cron import run_monrun
from crm_admin.monrun_checks.checkers import base

CRM_ADMIN_MONRUN = {
    'Limits': {
        'campaign_sending_processing_limit_in_seconds': 600,
        'campaign_segment_calculating_limit_in_seconds': 600,
    },
}


@pytest.mark.now('2022-12-12 09:00:00')
@pytest.mark.pgsql('crm_admin', files=['frozen.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_frozen_campaigns_states():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_campaigns_states',
            'campaign_sending_processing',
        ],
    )

    assert (
        msg == '1; Frozen campaigns in status SENDING_PROCESSING: '
        '(log id: 5, campaign id: 2), '
        '(log id: 8, campaign id: 2), '
        '(log id: 10, campaign id: 3), '
        '(log id: 17, campaign id: 5).'
    )


@pytest.mark.now('2022-12-12 09:00:00')
@pytest.mark.pgsql('crm_admin', files=['not_frozen.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_not_frozen_campaigns_states():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_campaigns_states',
            'campaign_segment_calculating',
        ],
    )

    assert msg == f'0; {base.BaseChecker.SUCCESS_DESCRIPTION}'
