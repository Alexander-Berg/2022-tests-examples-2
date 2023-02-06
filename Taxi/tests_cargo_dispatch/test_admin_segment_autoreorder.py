import pytest

from testsuite.utils import matching


@pytest.fixture(name='mock_claims_full')
def _mock_claims_full(mockserver, load_json):
    def _wrapper(cargo_order_id: str, claim_point_id: int):
        @mockserver.json_handler('/cargo-claims/v2/claims/full')
        def _handler(request):
            data = load_json('claims/default.json')
            data['cargo_order_id'] = cargo_order_id
            data['current_point_id'] = claim_point_id
            return data

    return _wrapper


async def test_driver_changed(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mockserver,
        mock_claims_full,
        read_waybill_info,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
):

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg3')
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'old_driver',
                'park_id': 'old_park',
            },
            'reason': 'Стоял на месте',
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'driver_already_changed',
        'message': 'Исполнитель уже изменился',
    }


async def test_no_performer_for_order(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        set_up_order_admin_cancel_menu_v2,
        read_waybill_info,
        mockserver,
        mock_order_cancel,
        mock_claims_full,
        happy_path_claims_segment_db,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg3')
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    reason_ids_chain = ['performer_mistake', 'reject_by_courier']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    mock_order_cancel.expected_request = {
        'order_id': matching.AnyString(),
        'cancel_state': 'free',
        'cancel_reason': 'admin_reorder_required',
        'reason_ids_chain': reason_ids_chain,
    }

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'reason': 'Стоял на месте',
            'reason_ids_chain': reason_ids_chain,
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'result': 'Успех. Теперь будет создан новый маршрутный лист',
    }

    assert mock_order_cancel.handler.times_called == 1


async def test_cancel_taxi_order(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        set_up_order_admin_cancel_menu_v2,
        mock_order_cancel,
        read_waybill_info,
        get_segment_info,
        mockserver,
        mock_claims_full,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
):
    mock_order_cancel.expected_request = {
        'order_id': matching.AnyString(),
        'cancel_state': 'free',
        'cancel_reason': 'admin_reorder_required',
        'reason_ids_chain': ['1', '2'],
    }

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg3')
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'reason_ids_chain': ['1', '2'],
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {'result': 'Заявка отменена'}

    assert mock_order_cancel.handler.times_called == 1

    segment = await get_segment_info('seg3')
    assert 'dynamic_context' not in segment['segment']


async def test_autoreorder_by_experiment(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        set_up_order_admin_cancel_menu_v2,
        experiments3,
        mock_order_cancel,
        read_waybill_info,
        mock_claims_full,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
        reason_id='some',
        reason_id_child='reason',
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_dispatch_reorder',
        consumers=['cargo-dispatch/mark-order-fail'],
        clauses=[
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'admin_cancel_reason',
                                    'arg_type': 'string',
                                    'value': f'{reason_id}.{reason_id_child}',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'is_reorder_required': True,
                    'reason': 'matched_common_clause',
                },
            },
        ],
        default_value={
            'is_reorder_required': False,
            'reason': 'no_clauses_matched',
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg3')
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'reason_ids_chain': [reason_id, reason_id_child],
        },
        params={'claim_id': claim_id},
    )

    assert mock_order_cancel.handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'result': 'Успех. Теперь будет создан новый маршрутный лист',
    }


async def test_cancel_forbidden(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        mock_order_cancel,
        read_waybill_info,
        mockserver,
        mock_claims_full,
        happy_path_claims_segment_db,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
):

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg3')
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    mock_order_cancel.status_code = 409

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 500


async def test_some_point_visited(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        read_waybill_info,
        mock_claims_full,
        mockserver,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
):
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 409
    assert response.json() == {
        'message': 'Исполнитель уже забрал груз',
        'code': 'some_point_already_visited',
    }


async def test_disable_batching(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        set_up_order_admin_cancel_menu_v2,
        read_waybill_info,
        get_segment_info,
        mockserver,
        mock_order_cancel,
        happy_path_claims_segment_db,
        mock_claims_full,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg3')
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    reason_ids_chain = ['performer_mistake', 'reject_by_courier']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    mock_order_cancel.expected_request = {
        'order_id': matching.AnyString(),
        'cancel_state': 'free',
        'cancel_reason': 'admin_reorder_required',
        'reason_ids_chain': reason_ids_chain,
    }

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'reason': 'Стоял на месте',
            'disable_batching': True,
            'reason_ids_chain': reason_ids_chain,
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'result': 'Успех. Теперь будет создан новый маршрутный лист',
    }

    assert mock_order_cancel.handler.times_called == 1
    segment = await get_segment_info('seg3')
    expected = {'delivery_flags': {'is_forbidden_to_be_in_batch': True}}
    assert segment['segment']['dynamic_context'] == expected


async def test_batch_order(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mock_claims_full,
        happy_path_claims_segment_db,
        read_waybill_info,
        mockserver,
        mock_order_cancel,
        waybill_id='waybill_smart_1',
        claim_id='test_claim_1',
):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {'performers': []}

    segment = happy_path_claims_segment_db.get_segment('seg1')

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={'reason': 'Стоял на месте'},
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {'result': 'Сегмент успешно отменен'}
    assert not mock_order_cancel.handler.times_called


@pytest.mark.parametrize(
    'admin_segment_reorders_enabled',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    CARGO_DISPATCH_ADMIN_SEGMENT_REORDERS_ENABLED=True,
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    CARGO_DISPATCH_ADMIN_SEGMENT_REORDERS_ENABLED=False,
                ),
            ],
        ),
    ],
)
async def test_autoreorder_segment_in_batch_1(
        mock_order_change_destination,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_notify_orders,
        read_waybill_info,
        stq,
        mock_claims_full,
        taxi_cargo_dispatch,
        admin_segment_reorders_enabled,
        pgsql,
        waybill_id='waybill_smart_1',
        claim_id='test_claim_1',
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_A2_p6 (16) -> seg1_A1_p7 (17) ->
        seg2_C1_p3 (23)

    Here autoreorder for seq1.
    """
    segment_id = 'seg1'

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']
    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    reason_ids_chain = ['1', '2']
    ticket = 'CHATTERBOX-22'
    # Support made autoreorder for seg1
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'reason_ids_chain': reason_ids_chain,
            'ticket': ticket,
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {'result': 'Сегмент успешно отменен'}
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""select segment_id, reason, ticket, source
            from cargo_dispatch.admin_segment_reorders
            where segment_id = \'{segment_id}\'""",
    )
    admin_segment_reorders = list(cursor)
    if admin_segment_reorders_enabled:
        assert admin_segment_reorders[0] == (
            segment_id,
            '.'.join(reason_ids_chain),
            ticket,
            'segment_autoreorder.autoreorder_unknown_service',
        )
    else:
        assert not admin_segment_reorders

    # Change destination
    result = await run_notify_orders()
    assert result['stats']['waybills-for-handling'] == 1
    assert mock_order_change_destination.times_called == 1
    assert mock_order_change_destination.next_call()['request'].json == {
        'order_id': matching.any_string,
        'dispatch_version': 2,
        'claim_id': 'claim_seg2',
        'segment_id': 'seg2',
        'claim_point_id': 21,
        'idempotency_token': 'waybill_smart_1_21_3',
    }

    # Change taxi status to transporting
    assert stq.cargo_claims_xservice_change_status.times_called == 1
    stq_call = stq.cargo_claims_xservice_change_status.next_call()
    assert stq_call['kwargs']['new_status'] == 'transporting'
    assert stq_call['kwargs']['driver_id'] == 'driver_id_1'


async def test_same_day_order_kwarg(
        happy_path_state_first_import,
        set_up_segment_routers_exp,
        propose_from_segments,
        experiments3,
        run_choose_routers,
        run_choose_waybills,
        run_create_orders,
        mock_claim_bulk_update_state,
        run_notify_claims,
        read_waybill_info,
        mock_claims_full,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        mock_order_cancel,
        claim_id='test_claim_1',
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_dispatch_reorder',
        consumers=['cargo-dispatch/mark-order-fail'],
        clauses=[
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {'arg_name': 'is_same_day_order'},
                                'type': 'bool',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'is_reorder_required': True,
                    'reason': 'matched_common_clause',
                },
            },
        ],
        default_value={
            'is_reorder_required': False,
            'reason': 'no_clauses_matched',
        },
    )

    await set_up_segment_routers_exp(
        smart_router='cargo_same_day_delivery_router',
    )
    await run_choose_routers()
    await propose_from_segments(
        'cargo_same_day_delivery_router', 'waybill_sdd_1', 'seg1',
    )

    await run_choose_waybills()
    await run_create_orders(should_set_stq=True)
    await run_notify_claims()

    waybill = await read_waybill_info('waybill_sdd_1')
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg1')
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
        },
        params={'claim_id': claim_id},
    )

    assert mock_order_cancel.handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'result': 'Успех. Теперь будет создан новый маршрутный лист',
    }


async def test_paid_order_cancel_in_cargo_orders(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mockserver,
        read_waybill_info,
        mock_claims_full,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
):
    @mockserver.json_handler('/cargo-orders/v1/order/cancel')
    def mock_order_cancel(request):
        if request.json['cancel_state'] == 'free':
            return mockserver.make_response(
                json={'code': 'bad_state', 'message': 'free is not allowed'},
                status=409,
            )
        return {'cancel_state': request.json['cancel_state']}

    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment('seg3')
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']

    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
        },
        params={'claim_id': claim_id},
    )

    assert response.status_code == 200
    assert mock_order_cancel.times_called == 2


@pytest.mark.config(CARGO_DISPATCH_ADMIN_SEGMENT_REORDERS_ENABLED=True)
@pytest.mark.parametrize(
    'forced_action', ['cancel_by_support_logics', 'reorder_by_support_logics'],
)
async def test_forced_action_in_batch(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        read_waybill_info,
        mock_claims_full,
        taxi_cargo_dispatch,
        fetch_admin_segment_reorder,
        forced_action,
        waybill_id='waybill_smart_1',
        claim_id='test_claim_1',
        segment_id='seg1',
):
    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']
    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    reason_ids_chain = ['1', '2']
    ticket = 'CHATTERBOX-22'

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'reason_ids_chain': reason_ids_chain,
            'ticket': ticket,
            'forced_action': forced_action,
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200

    admin_segment_reorder = fetch_admin_segment_reorder(segment_id, 1)
    assert admin_segment_reorder.reason == '.'.join(reason_ids_chain)
    assert admin_segment_reorder.ticket == ticket
    assert (
        admin_segment_reorder.source
        == 'segment_autoreorder.autoreorder_unknown_service'
    )
    assert admin_segment_reorder.forced_action == forced_action
    assert admin_segment_reorder.cancel_request_token is not None


@pytest.mark.config(CARGO_DISPATCH_ADMIN_SEGMENT_REORDERS_ENABLED=True)
@pytest.mark.parametrize(
    'forced_action', ['cancel_by_support_logics', 'reorder_by_support_logics'],
)
async def test_forced_action_not_in_batch(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        read_waybill_info,
        mockserver,
        mock_claims_full,
        taxi_cargo_dispatch,
        fetch_admin_segment_reorder,
        forced_action,
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
        segment_id='seg3',
):
    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']
    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    reason_ids_chain = ['1', '2']
    ticket = 'CHATTERBOX-22'

    cancel_request_token = ''

    @mockserver.json_handler('/cargo-orders/v1/order/cancel')
    def mock_order_cancel(request):
        nonlocal cancel_request_token
        cancel_request_token = request.json['cancel_request_token']
        assert cancel_request_token is not None

        assert request.json['reason_ids_chain'] == reason_ids_chain
        return {'cancel_state': 'free'}

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'reason_ids_chain': reason_ids_chain,
            'ticket': ticket,
            'forced_action': forced_action,
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200

    assert mock_order_cancel.times_called == 1

    admin_segment_reorder = fetch_admin_segment_reorder(segment_id, 1)
    assert admin_segment_reorder.reason == '.'.join(reason_ids_chain)
    assert admin_segment_reorder.ticket == ticket
    assert (
        admin_segment_reorder.source
        == 'segment_autoreorder.autoreorder_unknown_service'
    )
    assert admin_segment_reorder.forced_action == forced_action
    assert admin_segment_reorder.cancel_request_token == cancel_request_token


@pytest.mark.config(CARGO_DISPATCH_ADMIN_SEGMENT_REORDERS_ENABLED=True)
async def test_existing_reorder_record(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        read_waybill_info,
        mockserver,
        mock_claims_full,
        taxi_cargo_dispatch,
        prepare_admin_segment_reorder,
        fetch_admin_segment_reorder,
        forced_action='reorder_by_support_logics',
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
        segment_id='seg3',
):
    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']
    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    reason_ids_chain = ['1', '2']
    ticket = 'CHATTERBOX-22'

    # Existing token must be loaded from DB,
    # but other parameters must be overwritten in DB.
    cancel_request_token = 'cargo-dispatch/12345'
    prepare_admin_segment_reorder(
        segment_id,
        1,
        reason='another_reason',
        ticket='another_ticket',
        forced_action=None,
        cancel_request_token=cancel_request_token,
    )

    @mockserver.json_handler('/cargo-orders/v1/order/cancel')
    def mock_order_cancel(request):
        assert request.json['cancel_request_token'] == cancel_request_token
        assert request.json['reason_ids_chain'] == reason_ids_chain
        return {'cancel_state': 'free'}

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'reason_ids_chain': reason_ids_chain,
            'ticket': ticket,
            'forced_action': forced_action,
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200

    assert mock_order_cancel.times_called == 1

    admin_segment_reorder = fetch_admin_segment_reorder(segment_id, 1)
    assert admin_segment_reorder.reason == '.'.join(reason_ids_chain)
    assert admin_segment_reorder.ticket == ticket
    assert (
        admin_segment_reorder.source
        == 'segment_autoreorder.autoreorder_unknown_service'
    )
    assert admin_segment_reorder.forced_action == forced_action
    assert admin_segment_reorder.cancel_request_token == cancel_request_token


@pytest.mark.config(CARGO_DISPATCH_ADMIN_SEGMENT_REORDERS_ENABLED=True)
async def test_token_collision(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        read_waybill_info,
        mockserver,
        testpoint,
        mock_claims_full,
        taxi_cargo_dispatch,
        prepare_admin_segment_reorder,
        fetch_admin_segment_reorder,
        forced_action='reorder_by_support_logics',
        waybill_id='waybill_fb_3',
        claim_id='test_claim_1',
        segment_id='seg3',
):
    waybill = await read_waybill_info(waybill_id)
    cargo_order_id = waybill['diagnostics']['order_id']

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    point = segment.get_point('p1')
    claim_point_id = point['claim_point_id']
    mock_claims_full(
        cargo_order_id=cargo_order_id, claim_point_id=claim_point_id,
    )

    reason_ids_chain = ['1', '2']
    ticket = 'CHATTERBOX-22'

    token_1 = None
    token_2 = None

    @testpoint('generated-cancel-request-token')
    def _testpoint(json):
        # При первой итерации сохраняем токен в базе другому сегменту,
        # чтобы произошла коллизия.
        nonlocal token_1
        nonlocal token_2
        if token_1 is None:
            token_1 = json['generated_token']
            prepare_admin_segment_reorder(
                'seg1', 1, cancel_request_token=token_1,
            )
        else:
            assert token_2 is None
            token_2 = json['generated_token']
            assert token_2 != token_1

    @mockserver.json_handler('/cargo-orders/v1/order/cancel')
    def mock_order_cancel(request):
        assert request.json['cancel_request_token'] == token_2
        assert request.json['reason_ids_chain'] == reason_ids_chain
        return {'cancel_state': 'free'}

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/segment/autoreorder',
        json={
            'performer_info': {
                'driver_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'reason': 'Стоял на месте',
            'reason_ids_chain': reason_ids_chain,
            'ticket': ticket,
            'forced_action': forced_action,
        },
        params={'claim_id': claim_id},
    )
    assert response.status_code == 200

    assert mock_order_cancel.times_called == 1

    admin_segment_reorder = fetch_admin_segment_reorder(segment_id, 1)
    assert admin_segment_reorder.reason == '.'.join(reason_ids_chain)
    assert admin_segment_reorder.ticket == ticket
    assert (
        admin_segment_reorder.source
        == 'segment_autoreorder.autoreorder_unknown_service'
    )
    assert admin_segment_reorder.forced_action == forced_action
    assert admin_segment_reorder.cancel_request_token == token_2
