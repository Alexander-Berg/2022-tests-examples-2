# pylint: disable=redefined-outer-name
import pytest


@pytest.mark.config(HIRING_REPLICA_SUPERJOB_ZENDESK_EXPORT_ENABLED=True)
async def test_superjob2zendesk(
        simple_secdist,
        infranaim_mockserver_submit,
        replica_superjob_mockserver,
        run_crontask,
        cron_context,
):
    handler_superjob = replica_superjob_mockserver()
    handler_infranaim = infranaim_mockserver_submit()
    await run_crontask('superjob2zendesk')
    assert handler_superjob.has_calls
    assert handler_infranaim.has_calls
