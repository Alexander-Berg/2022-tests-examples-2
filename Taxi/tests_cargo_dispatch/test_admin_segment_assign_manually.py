FALLBACK_ROUTER = 'fallback_router'


async def test_happy_path(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mockserver,
        segment_id='seg3',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        return {
            'order_id': request.json['order_id'],
            'replica': 'secondary',
            'version': 'xxx',
            'fields': {'manual_dispatch': {'mirror_only': True}},
        }

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_add_fallback_router(
        taxi_cargo_dispatch,
        happy_path_state_first_import,
        mockserver,
        get_segment_info,
        read_segment_journal,
        run_segments_journal_mover,
        segment_id='seg1',
):
    """
    Manual assign for segment which does not chooses fallback_router
    Add fallback_router
    """

    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    # Check data before action
    seginfo = await get_segment_info('seg1')
    assert 'waybill_building_deadline' not in seginfo['dispatch']
    assert seginfo['dispatch']['status'] == 'new'

    await run_segments_journal_mover()
    response = await read_segment_journal(FALLBACK_ROUTER, cursor=None)
    assert not response['events']

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    # Check data after action
    seginfo = await get_segment_info('seg1')
    assert 'waybill_building_deadline' in seginfo['dispatch']

    await run_segments_journal_mover()
    response = await read_segment_journal(FALLBACK_ROUTER, cursor=None)
    assert len(response['events']) == 1


async def test_change_fallback_router_priority(
        taxi_cargo_dispatch,
        happy_path_state_fallback_waybills_proposed,
        mockserver,
        get_segment_info,
        read_waybill_info,
        segment_id='seg2',
):
    """
    Best router is logistic-dispatch
    Change it to 'fallback_router' if order does not created yet
    """

    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['best_router_id'] == 'smart_router'

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['best_router_id'] == 'fallback_router'


async def test_segment_in_batch(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mockserver,
        segment_id='seg1',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        return {
            'order_id': request.json['order_id'],
            'replica': 'secondary',
            'version': 'xxx',
            'fields': {'manual_dispatch': {'mirror_only': True}},
        }

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_performer_already_assigned(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        segment_id='seg3',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'performer_already_assigned',
        'message': 'Исполнитель уже назначен',
    }


async def test_manual_dispatch_disabled_for_corp(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mockserver,
        segment_id='seg3',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        return {
            'order_id': request.json['order_id'],
            'replica': 'secondary',
            'version': 'xxx',
            'fields': {},
        }

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'manual_dispatch_disabled_for_corp',
        'message': 'Ручной диспатч недоступен для этого корп клиента',
    }


async def test_segment_resolved(
        taxi_cargo_dispatch, happy_path_cancelled_by_user, segment_id='seg3',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'segment_already_resolved',
        'message': 'Обработка этого сегмента завершена',
    }


async def test_unknown_segment(
        taxi_cargo_dispatch, happy_path_failed_once, segment_id='unknown',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/assign-manually', params={'segment_id': segment_id},
    )
    assert response.status_code == 404
