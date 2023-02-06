# pylint: disable=redefined-outer-name
import pytest


@pytest.mark.config(ZARPLATARU_FETCH_RESPONDS_ENABLED=True)
async def test_fetch_responds(
        simple_secdist,
        run_crontask,
        zarplataru_responds_handler,
        zarplataru_auth_handler,
        get_all_responds,
):

    auth_handler = zarplataru_auth_handler()
    responds_handler = zarplataru_responds_handler()
    await run_crontask('get_latest_responds')
    rows = await get_all_responds()

    assert len(rows) == 3
    assert responds_handler.has_calls
    assert auth_handler.has_calls


@pytest.mark.config(ZARPLATARU_FETCH_RESPONDS_ENABLED=False)
async def test_fetch_responds_disabled(
        simple_secdist,
        run_crontask,
        zarplataru_responds_handler,
        zarplataru_auth_handler,
        get_all_responds,
):

    auth_handler = zarplataru_auth_handler()
    responds_handler = zarplataru_responds_handler()
    await run_crontask('get_latest_responds')
    rows = await get_all_responds()

    assert not rows
    assert not responds_handler.has_calls
    assert not auth_handler.has_calls
