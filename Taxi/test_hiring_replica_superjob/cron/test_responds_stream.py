# pylint: disable=redefined-outer-name


import pytest


@pytest.mark.config(HIRING_REPLICA_SUPERJOB_RESPONDS_STREAM_ENABLED=True)
async def test_create_responds(
        simple_secdist,
        superjob_mockserver_responds,
        superjob_mockserver_password,
        run_crontask,
        get_all_resumes,
):
    handler_password = superjob_mockserver_password()
    handler_resumes = superjob_mockserver_responds()
    await run_crontask('responds_stream')
    rows = await get_all_resumes()

    assert len(rows) == 20
    assert handler_password.has_calls
    assert handler_resumes.has_calls


@pytest.mark.config(HIRING_REPLICA_SUPERJOB_RESPONDS_STREAM_ENABLED=False)
async def test_responds_disabled(
        simple_secdist,
        superjob_mockserver_responds,
        superjob_mockserver_password,
        run_crontask,
):
    handler_password = superjob_mockserver_password()
    handler_resumes = superjob_mockserver_responds()
    await run_crontask('responds_stream')

    assert not handler_password.has_calls
    assert not handler_resumes.has_calls
