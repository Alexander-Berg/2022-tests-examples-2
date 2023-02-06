# pylint: disable=unused-argument

import pytest

from crm_admin.generated.cron import run_cron


CRM_ADMIN_SETTINGS = {
    'UserActivationSettings': {'yql_share_url': '//some/url/xxx'},
}

CRM_ADMIN_SETTINGS_DISABLED = {
    'UserActivationSettings': {
        'disabled': True,
        'yql_share_url': '//some/url/xxx',
    },
}


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_start_task(cron_context, patch):
    @patch(
        'crm_admin.crontasks.user_activation.pollable_operation.PollableOperation.start_stq_task',  # noqa: E501
    )
    async def start_stq_task(*args, **kwargs):
        pass

    await run_cron.main(['crm_admin.crontasks.user_activation', '-t', '0'])
    assert start_stq_task.calls


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS_DISABLED)
async def test_disabled_task(cron_context, patch):
    @patch(
        'crm_admin.crontasks.user_activation.pollable_operation.PollableOperation.start_stq_task',  # noqa: E501
    )
    async def start_stq_task(*args, **kwargs):
        pass

    await run_cron.main(['crm_admin.crontasks.user_activation', '-t', '0'])
    assert not start_stq_task.calls
