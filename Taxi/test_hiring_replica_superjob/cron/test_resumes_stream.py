# pylint: disable=redefined-outer-name


import pytest


@pytest.mark.config(HIRING_REPLICA_SUPERJOB_RESUMES_STREAM_ENABLED=True)
async def test_create_resumes(
        simple_secdist,
        superjob_mockserver_resumes,
        superjob_mockserver_password,
        run_crontask,
        get_all_resumes,
):
    handler_password = superjob_mockserver_password()
    handler_resumes = superjob_mockserver_resumes()
    await run_crontask('resumes_stream')
    rows = await get_all_resumes()

    assert len(rows) == 3
    assert handler_password.has_calls
    assert handler_resumes.has_calls


@pytest.mark.config(HIRING_REPLICA_SUPERJOB_RESUMES_STREAM_ENABLED=True)
async def test_update_resumes(
        simple_secdist,
        superjob_mockserver_resumes,
        superjob_mockserver_password,
        run_crontask,
        get_all_resumes,
):
    handler_password = superjob_mockserver_password()
    handler_resumes = superjob_mockserver_resumes()
    await run_crontask('resumes_stream')
    await run_crontask('resumes_stream')
    await run_crontask('resumes_stream')
    rows = await get_all_resumes()

    assert len(rows) == 3
    assert handler_password.has_calls
    assert handler_resumes.has_calls
