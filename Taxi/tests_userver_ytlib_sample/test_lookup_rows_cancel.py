import asyncio

import pytest


@pytest.mark.parametrize('cancel_requested', [True, False])
async def test_lookup_rows_cancel(
        taxi_userver_ytlib_sample, yt_apply, testpoint, cancel_requested,
):
    @testpoint('ytlib_cancel_data')
    def ytlib_cancel_data(data):
        return {'cancel_poll_milliseconds': 0}

    handler_cancel_event = asyncio.Event()
    in_arcadia_yt_wrapper_event = asyncio.Event()

    @testpoint('ytlib_handler_cancel_waiting')
    async def ytlib_handler_cancel_waiting(data):
        assert await asyncio.wait_for(in_arcadia_yt_wrapper_event.wait(), 10)

    @testpoint('ytlib_handler_cancel_sent')
    async def ytlib_handler_cancel_sent(data):
        handler_cancel_event.set()

    @testpoint('in_arcadia_yt_wrapper')
    async def in_arcadia_yt_wrapper(data):
        if not cancel_requested:
            return
        in_arcadia_yt_wrapper_event.set()
        assert await asyncio.wait_for(handler_cancel_event.wait(), 10)

    arcadia_error_set = set()

    @testpoint('ytlib_arcadia_error')
    def ytlib_arcadia_error(data):
        arcadia_error_set.add(data)

    response = await taxi_userver_ytlib_sample.post(
        'ytlib/lookup-rows-cancel',
        json={'cancel_requested': cancel_requested},
    )

    assert ytlib_arcadia_error.times_called == 1

    # cancel_poll_milliseconds too small in this test
    assert in_arcadia_yt_wrapper.times_called >= 1
    if cancel_requested:
        assert ytlib_handler_cancel_waiting.times_called == 1
        assert ytlib_handler_cancel_sent.times_called == 1
        assert arcadia_error_set == {'CANCELLED'}
    else:
        assert ytlib_handler_cancel_waiting.times_called == 0
        assert ytlib_handler_cancel_sent.times_called == 0
        # Got internal YT error
        assert len(arcadia_error_set) == 1 and (
            arcadia_error_set != {'CANCELLED'}
        )

    assert response.status_code == 200
    assert response.text == 'Got exception at lookup_rows'
    assert ytlib_cancel_data.times_called == 1
