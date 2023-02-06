import pytest

from crm_admin.generated.cron import run_monrun
from crm_admin.monrun_checks.checkers import base

CRM_ADMIN_MONRUN = {
    'EmptyErrors': {'statuses': ['VERIFY_ERROR', 'SEGMENT_CALCULATING_ERROR']},
}


@pytest.mark.now('2022-02-14 16:00:00')
@pytest.mark.pgsql('crm_admin', files=['without_error_code.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN={'EmptyErrors': {'statuses': []}})
async def test_with_no_statuses():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_empty_errors',
            'campaign_empty_errors',
        ],
    )

    assert msg == f'0; {base.BaseChecker.SUCCESS_DESCRIPTION}'


@pytest.mark.now('2022-02-14 16:00:00')
@pytest.mark.pgsql('crm_admin', files=['has_error_code.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_with_error_code():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_empty_errors',
            'campaign_empty_errors',
        ],
    )

    assert msg == f'0; {base.BaseChecker.SUCCESS_DESCRIPTION}'


@pytest.mark.now('2022-02-14 16:00:00')
@pytest.mark.pgsql('crm_admin', files=['without_error_code.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_without_error_code():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_empty_errors',
            'campaign_empty_errors',
        ],
    )
    assert (
        msg == '1; Campaigns have error status, but have no error_code '
        'or error_description: (log id: 1, campaign id: 1234).'
    )


@pytest.mark.now('2022-02-14 16:00:00')
@pytest.mark.pgsql('crm_admin', files=['different_codes.sql'])
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
async def test_different_codes():
    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_empty_errors',
            'campaign_empty_errors',
        ],
    )
    assert (
        msg == '1; Campaigns have error status, but have no error_code '
        'or error_description: (log id: 1, campaign id: 1234), '
        '(log id: 2, campaign id: 1234).'
    )
