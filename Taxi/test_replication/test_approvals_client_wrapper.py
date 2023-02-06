import pytest

import generated.clients.taxi_approvals

from replication.drafts import approvals_client_wrapper as wrapper
from replication.generated.cron import cron_context as cron_context_module


async def test_call_applying_drafts_list(
        mockserver, replication_cron_ctx: cron_context_module.Context,
):
    passed_statuses = None

    @mockserver.json_handler('/taxi-approvals/drafts/list/')
    def _handle(request):
        nonlocal passed_statuses
        passed_statuses = request.json['statuses']
        return mockserver.make_response(status=500)

    raw_client = replication_cron_ctx.clients.taxi_approvals
    client = wrapper.ApprovalsClientWrapper(raw_client)
    with pytest.raises(generated.clients.taxi_approvals.NotDefinedResponse):
        await client.applying_drafts_list()
    assert _handle.times_called > 0  # not ==1 because of retries
    assert passed_statuses == [wrapper.APPLYING_STATUS]


async def test_call_finish(
        mockserver, replication_cron_ctx: cron_context_module.Context,
):
    passed_draft_id = None
    passed_final_status = None

    @mockserver.json_handler(
        '/taxi-approvals/drafts/(?P<draft_id>[^/]+)/finish/', regex=True,
    )
    async def _handle(request, draft_id):
        nonlocal passed_draft_id
        nonlocal passed_final_status
        passed_draft_id = draft_id
        passed_final_status = request.json['final_status']
        return mockserver.make_response(status=500)

    raw_client = replication_cron_ctx.clients.taxi_approvals
    client = wrapper.ApprovalsClientWrapper(raw_client)
    with pytest.raises(generated.clients.taxi_approvals.NotDefinedResponse):
        await client.finish(
            'someid',
            final_status=wrapper.FinalStatuses.SUCCEEDED,
            x_yandex_login='dummy',
        )
    assert _handle.times_called > 0  # not ==1 because of retries
    assert passed_draft_id == 'someid'
    assert passed_final_status == wrapper.FinalStatuses.SUCCEEDED.value
