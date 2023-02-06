async def test_2can_request(
        state_performer_found,
        stq_runner,
        mock_web_api_agent_update,
        get_performer_tid_info,
):
    """
        Check tid update request.
    """
    state = await state_performer_found()

    tid_info = get_performer_tid_info('parkid1', 'driverid1')
    assert tid_info['tid'] in state.default_tids

    assert mock_web_api_agent_update.handler.times_called == 1
    assert mock_web_api_agent_update.last_request.json == {
        'TID': tid_info['tid'],
    }
