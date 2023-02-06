import pytest


async def test_only_finished_requests_in_decisions(
        load_json, get_admin_fines_state, inject_events, expected_decisions,
):
    inject_events()
    expected = expected_decisions()

    state = await get_admin_fines_state()
    assert state['decisions'] == expected['decisions']


async def test_recent_finished_operations_in_pending_list(
        recently, get_admin_fines_state, inject_events, expected_decisions,
):
    inject_events()
    expected = expected_decisions()

    state = await get_admin_fines_state()
    assert state['pending_decisions'] == expected['pending_decisions']


@pytest.mark.now('2021-02-13T12:00:00+00:00')
async def test_only_recent_operations_in_pending(
        get_admin_fines_state, inject_events, expected_decisions,
):
    inject_events()
    expected = expected_decisions()
    del expected['pending_decisions'][0]

    state = await get_admin_fines_state()
    assert state['pending_decisions'] == expected['pending_decisions']
