# pylint: disable=redefined-outer-name
import pytest


@pytest.mark.config(
    HIRING_REPLICA_SUPERJOB_CONTACTS_PURCHASE_ENABLED=True,
    HIRING_REPLICA_SUPERJOB_WIDE_FUNNEL=False,
)
async def test_buy_resumes(
        simple_secdist,
        superjob_mockserver_buy,
        superjob_mockserver_resumes,
        superjob_mockserver_password,
        run_crontask,
        get_all_resumes,
        get_purchased_resumes,
):
    handler_password = superjob_mockserver_password()
    handler_resumes = superjob_mockserver_resumes()
    await run_crontask('resumes_stream')
    all_resumes = await get_all_resumes()
    handler_buy = superjob_mockserver_buy()
    await run_crontask('resumes_broker')
    purchased_resumes = await get_purchased_resumes()

    assert len(all_resumes) == 3
    assert len(purchased_resumes) == 1
    assert handler_buy.has_calls
    assert handler_resumes.has_calls
    assert handler_password.has_calls


@pytest.mark.config(
    HIRING_REPLICA_SUPERJOB_CONTACTS_PURCHASE_ENABLED=True,
    HIRING_REPLICA_SUPERJOB_WIDE_FUNNEL=True,
)
async def test_wide_funnel(
        simple_secdist,
        superjob_mockserver_buy,
        superjob_mockserver_resumes,
        superjob_mockserver_password,
        run_crontask,
        get_all_resumes,
        get_purchased_resumes,
):
    handler_password = superjob_mockserver_password()
    handler_resumes = superjob_mockserver_resumes()
    await run_crontask('resumes_stream')
    all_resumes = await get_all_resumes()
    handler_buy = superjob_mockserver_buy()
    await run_crontask('resumes_broker')
    purchased_resumes = await get_purchased_resumes()

    assert len(all_resumes) == 3
    assert len(purchased_resumes) == 1
    assert handler_buy.has_calls
    assert handler_resumes.has_calls
    assert handler_password.has_calls
