async def test_add_fallback_router(
        taxi_cargo_dispatch,
        happy_path_state_first_import,
        mockserver,
        get_segment_info,
        read_segment_journal,
        run_segments_journal_mover,
        segment_id='seg1',
        router_id='fallback_router',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    # Check data before action
    seginfo = await get_segment_info('seg1')
    assert 'waybill_building_deadline' not in seginfo['dispatch']
    assert seginfo['dispatch']['status'] == 'new'

    await run_segments_journal_mover()
    response = await read_segment_journal(router_id, cursor=None)
    assert not response['events']

    response = await taxi_cargo_dispatch.post(
        '/v1/internal/segment/force-router',
        json={'segment_id': segment_id, 'router_id': router_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # Check data after action
    seginfo = await get_segment_info('seg1')
    assert 'waybill_building_deadline' in seginfo['dispatch']

    await run_segments_journal_mover()
    response = await read_segment_journal(router_id, cursor=None)
    assert len(response['events']) == 1


async def test_change_fallback_router_priority(
        taxi_cargo_dispatch,
        happy_path_state_fallback_waybills_proposed,
        mockserver,
        get_segment_info,
        read_waybill_info,
        segment_id='seg2',
        router_id='logistic-dispatch',
):
    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['best_router_id'] == 'smart_router'

    response = await taxi_cargo_dispatch.post(
        '/v1/internal/segment/force-router',
        json={'segment_id': segment_id, 'router_id': router_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['best_router_id'] == router_id


async def test_segment_resolved(
        taxi_cargo_dispatch,
        happy_path_cancelled_by_user,
        segment_id='seg3',
        router_id='best_router',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/internal/segment/force-router',
        json={'segment_id': segment_id, 'router_id': router_id},
    )
    assert response.status_code == 409


async def test_unknown_segment(
        taxi_cargo_dispatch,
        happy_path_failed_once,
        segment_id='unknown',
        router_id='smart_router',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/internal/segment/force-router',
        json={'segment_id': segment_id, 'router_id': router_id},
    )
    assert response.status_code == 404
