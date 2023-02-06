async def test_stq_call(stq_runner, mockserver):
    @mockserver.json_handler(
        '/cargo-dispatch/v1/internal/segment/force-router',
    )
    async def _handler_info(request):
        assert request.json['segment_id'] in ['seg1', 'seg2', 'seg3']
        assert request.json['router_id'] == 'fallback_router'
        return mockserver.make_response(status=200)

    await stq_runner.cargo_sdd_fallback_dropped_locations.call(
        task_id='12345', kwargs={'segment_ids': ['seg1', 'seg2', 'seg3']},
    )

    assert _handler_info.times_called == 3
