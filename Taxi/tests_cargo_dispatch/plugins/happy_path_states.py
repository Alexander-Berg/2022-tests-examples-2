import pytest

FALLBACK_ROUTER = 'fallback_router'
SMART_ROUTER = 'smart_router'


@pytest.fixture(name='happy_path_context')
async def _happy_path_context():
    class ProposalContext:
        def __init__(self):
            self.reverse_destinations = False

    class Context:
        def __init__(self):
            self.proposal = ProposalContext()

    return Context()


@pytest.fixture(name='happy_path_exp3')
async def _happy_path_exp3(taxi_cargo_dispatch, set_up_segment_routers_exp):
    await set_up_segment_routers_exp()


@pytest.fixture(name='happy_path_claims_segment_db')
def _happy_path_claims_segment_db(build_claims_segment_db):
    db = build_claims_segment_db()

    points1 = [
        ('p1', 'A1', ('pickup', ['i1', 'i2']), []),
        (
            'p2',
            'A2',
            ('pickup', ['i3', 'i4']),
            [
                {
                    'type': 'strict_match',
                    'from': '2020-01-01T00:00:00+00:00',
                    'to': '2020-01-02T00:00:00+00:00',
                },
            ],
        ),
        ('p3', 'B1', ('dropoff', ['i1', 'i3']), []),
        (
            'p4',
            'B2',
            ('dropoff', ['i2']),
            [
                {
                    'type': 'strict_match',
                    'from': '2020-01-03T00:00:00+00:00',
                    'to': '2020-01-06T00:00:00+00:00',
                },
                {
                    'type': 'perfect_match',
                    'from': '2020-01-04T00:00:00+00:00',
                    'to': '2020-01-05T00:00:00+00:00',
                },
            ],
        ),
        ('p5', 'B3', ('dropoff', ['i4']), []),
        ('p6', 'A2', ('return', ['i3', 'i4']), []),
        ('p7', 'A1', ('return', ['i1', 'i2']), []),
    ]
    db.add_segment(segment_number=1, points=points1)  # 'seg1'

    points2 = [
        ('p1', 'A1', ('pickup', ['i1']), []),
        ('p2', 'B1', ('dropoff', ['i1']), []),
        ('p3', 'C1', ('return', ['i1']), []),
    ]
    db.add_segment(segment_number=2, points=points2)  # 'seg2'

    points3 = [
        ('p1', 'A1', ('pickup', ['i1']), []),
        ('p2', 'B1', ('dropoff', ['i1']), []),
        ('p3', 'A1', ('return', ['i1']), []),
    ]
    db.add_segment(segment_number=3, points=points3)  # 'seg3'

    db.add_segment(segment_number=5, points=points1)  # 'seg5'
    db.add_segment(segment_number=6, points=points2)  # 'seg6'

    return db


@pytest.fixture(name='happy_path_claims_segment_journal_handler')
def _happy_path_claims_segment_journal_handler(
        happy_path_claims_segment_db, mockserver,
):
    @mockserver.json_handler('/cargo-claims/v1/segments/journal')
    def handler(request):
        cursor = request.json.get('cursor')
        resp_body = happy_path_claims_segment_db.read_claims_journal(cursor)
        resp_headers = {'X-Polling-Delay-Ms': '0'}
        return mockserver.make_response(headers=resp_headers, json=resp_body)

    return handler


@pytest.fixture(name='happy_path_claims_segment_bulk_info_handler')
def _happy_path_claims_segment_bulk_info_handler(
        happy_path_claims_segment_db, mockserver,
):
    @mockserver.json_handler('/cargo-claims/v1/segments/bulk-info')
    def handler(request):
        response = {'segments': []}
        for obj in request.json['segment_ids']:
            segment_id = obj['segment_id']
            segment = happy_path_claims_segment_db.get_segment(segment_id)
            if segment is not None:
                response['segments'].append(segment.json)
        return response

    return handler


@pytest.fixture(name='happy_path_admin_claims_segment_bulk_info')
def _happy_path_admin_segment_bulk_info_handler(
        happy_path_claims_segment_db, mockserver,
):
    @mockserver.json_handler('/cargo-claims/v1/admin/segments/bulk-info')
    def handler(request):
        response = {'segments': []}
        for segment_id in request.json['segment_ids']:
            segment = happy_path_claims_segment_db.get_segment(segment_id)
            if segment is not None:
                response['segments'].append(segment.json)
        return response

    return handler


@pytest.fixture(name='happy_path_claims_segment_info_handler')
def _happy_path_claims_segment_info_handler(
        happy_path_claims_segment_db, mockserver,
):
    @mockserver.json_handler('/cargo-claims/v1/segments/info')
    def handler(request):
        segment_id = request.query['segment_id']
        segment = happy_path_claims_segment_db.get_segment(segment_id)
        if segment is None:
            return mockserver.make_response(status=404, json={})
        return segment.json

    return handler


@pytest.fixture(name='happy_path_claims_admin_segment_info_handler')
def _happy_path_admin_segment_info_handler(
        happy_path_claims_segment_db, mockserver,
):
    @mockserver.json_handler('/cargo-claims/v1/admin/segments/info')
    def handler(request):
        segment_id = request.query['segment_id']
        segment = happy_path_claims_segment_db.get_segment(segment_id)
        if segment is None:
            return mockserver.make_response(status=404, json={})
        return segment.json

    return handler


@pytest.fixture(name='happy_path_state_init')
def _happy_path_state_init(
        happy_path_exp3,
        happy_path_claims_segment_journal_handler,
        happy_path_claims_segment_info_handler,
        happy_path_claims_admin_segment_info_handler,
        happy_path_claims_segment_bulk_info_handler,
        happy_path_admin_claims_segment_bulk_info,
        cargo_orders_draft_handler,
        cargo_orders_commit_handler,
):
    # new segments in claims added, but journal has not been read
    pass


@pytest.fixture(name='happy_path_state_first_import')
async def _happy_path_state_first_import(
        happy_path_state_init, run_claims_segment_replication,
):
    result = await run_claims_segment_replication()
    return result


@pytest.fixture(name='happy_path_state_routers_chosen')
async def _happy_path_state_routers_chosen(
        happy_path_state_first_import, run_choose_routers,
):
    return await run_choose_routers()


@pytest.fixture(name='create_seg')
async def _create_seg(
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_choose_routers,
):
    async def _wrapper(num):
        # Create seg
        points = [
            ('p1', 'A1', ('pickup', ['i1']), []),
            ('p2', 'B1', ('dropoff', ['i1']), []),
            ('p3', 'A1', ('return', ['i1']), []),
        ]
        happy_path_claims_segment_db.add_segment(
            segment_number=num, points=points,
        )  # 'segnum'
        await run_claims_segment_replication()
        await run_choose_routers()

    return _wrapper


@pytest.fixture(name='create_seg_pull_dispatch')
async def _create_seg_pull_dispatch(
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_choose_routers,
):
    async def _wrapper(num):
        # Create seg
        points = [
            ('p1', 'A1', ('pickup', ['i1', 'i2']), []),
            ('p2', 'B1', ('dropoff', ['i1']), []),
            ('p3', 'B2', ('dropoff', ['i2']), []),
            ('p4', 'A1', ('return', ['i1', 'i2']), []),
        ]

        happy_path_claims_segment_db.add_segment(
            segment_number=num, points=points,
        )  # 'segnum'
        await run_claims_segment_replication()
        await run_choose_routers()

    return _wrapper


@pytest.fixture(name='create_seg4')
async def _create_seg4(create_seg):
    async def _wrapper():
        await create_seg(4)

    return _wrapper


@pytest.fixture(name='happy_path_state_seg4_routers_chosen')
async def _happy_path_state_seg4_routers_chosen(
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_choose_routers,
        create_seg4,
):
    await create_seg4()


@pytest.fixture(name='happy_path_state_seg7_routers_chosen')
async def _happy_path_state_seg7_routers_chosen(
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        run_choose_routers,
        create_seg,
):
    await create_seg(7)


@pytest.fixture(name='happy_path_state_fallback_waybills_proposed')
async def _happy_path_state_fallback_waybills_proposed(
        happy_path_state_routers_chosen, propose_from_segments,
):
    await propose_from_segments(FALLBACK_ROUTER, 'waybill_fb_1', 'seg1')
    await propose_from_segments(FALLBACK_ROUTER, 'waybill_fb_2', 'seg2')
    await propose_from_segments(FALLBACK_ROUTER, 'waybill_fb_3', 'seg3')


@pytest.fixture(name='happy_path_state_fallback_proposed_args')
async def _happy_path_state_fallback_proposed_args(
        happy_path_state_routers_chosen, propose_from_segments,
):
    async def _wrapper(taxi_requirements):
        await propose_from_segments(
            FALLBACK_ROUTER,
            'waybill_fb_1',
            'seg1',
            taxi_requirements=taxi_requirements,
        )
        await propose_from_segments(
            FALLBACK_ROUTER,
            'waybill_fb_2',
            'seg2',
            taxi_requirements=taxi_requirements,
        )
        await propose_from_segments(
            FALLBACK_ROUTER,
            'waybill_fb_3',
            'seg3',
            taxi_requirements=taxi_requirements,
        )

    return _wrapper


@pytest.fixture(name='happy_path_state_smart_waybills_proposed')
async def _happy_path_state_smart_waybills_proposed(
        happy_path_context,
        happy_path_state_routers_chosen,
        propose_from_segments,
):
    context = happy_path_context.proposal
    await propose_from_segments(
        SMART_ROUTER,
        'waybill_smart_1',
        'seg1',
        'seg2',
        reverse_destinations=context.reverse_destinations,
    )


@pytest.fixture(name='happy_path_state_all_waybills_proposed')
def _happy_path_state_all_waybills_proposed(
        happy_path_state_fallback_waybills_proposed,
        happy_path_state_smart_waybills_proposed,
):
    pass


@pytest.fixture(name='happy_path_state_waybills_chosen')
async def _happy_path_state_waybills_chosen(
        happy_path_state_all_waybills_proposed, run_choose_waybills,
):
    return await run_choose_waybills()


@pytest.fixture(name='happy_path_state_orders_created')
async def _happy_path_state_orders_created(
        happy_path_state_waybills_chosen,
        run_create_orders,
        mock_claim_bulk_update_state,
        run_notify_claims,
        taxi_cargo_dispatch_monitor,
):
    await run_create_orders(should_set_stq=True)
    creation_result = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-create-orders',
    )
    await run_notify_claims()

    assert mock_claim_bulk_update_state.handler.times_called >= 1
    mock_claim_bulk_update_state.handler.flush()

    return creation_result


@pytest.fixture(name='happy_path_find_performer')
async def _happy_path_find_performer(
        read_waybill_journal,
        taxi_cargo_dispatch,
        mark_performer_found,
        run_waybills_journal_mover,
):
    async def wrapper():
        # Move events from buffer to journal
        await run_waybills_journal_mover()
        response = await read_waybill_journal(FALLBACK_ROUTER)

        for event in response['events']:
            provider_order_id = event['current'].get('taxi_order_id')
            waybill_ref = event['external_ref']

            if provider_order_id is not None:
                await mark_performer_found(waybill_ref, provider_order_id)

    return wrapper


@pytest.fixture(name='happy_path_state_performer_found')
async def _happy_path_state_performer_found(
        happy_path_state_orders_created, happy_path_find_performer,
):
    await happy_path_find_performer()


@pytest.fixture(name='happy_path_failed_once')
async def _happy_path_failed_once(
        happy_path_state_performer_found, taxi_cargo_dispatch,
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': 'waybill_fb_3',
            'taxi_order_id': 'taxi-order',
            'reason': 'performer_cancel',
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200


@pytest.fixture(name='happy_path_reorder_exp')
async def _happy_path_reorder_exp(
        taxi_cargo_dispatch, set_up_cargo_dispatch_reorder_exp,
):
    pass


@pytest.fixture(name='reorder_waybill')
async def _reorder_waybill(taxi_cargo_dispatch, happy_path_reorder_exp):
    async def _wrapper(waybill_ref: str):
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/mark/order-fail',
            json={
                'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
                'waybill_id': waybill_ref,
                'taxi_order_id': 'taxi-order',
                'reason': 'performer_cancel',
                'lookup_version': 0,
            },
        )
        assert response.status_code == 200
        return response

    return _wrapper


@pytest.fixture(name='happy_path_segment_after_reorder')
async def _happy_path_segment_after_reorder(
        happy_path_state_performer_found, taxi_cargo_dispatch, reorder_waybill,
):
    return await reorder_waybill('waybill_fb_3')


@pytest.fixture(name='happy_path_performer_found_reorder')
async def _happy_path_performer_found_reorder(
        happy_path_failed_once,
        run_create_orders,
        taxi_cargo_dispatch,
        read_waybill_journal,
        run_waybills_journal_mover,
        mark_performer_found,
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    await run_create_orders(should_set_stq=True)

    # Move events from buffer to journal
    await run_waybills_journal_mover()
    response = await read_waybill_journal(FALLBACK_ROUTER)

    for event in response['events']:
        provider_order_id = event['current'].get('taxi_order_id')
        waybill_ref = event['external_ref']

        if provider_order_id is not None:
            await mark_performer_found(waybill_ref, provider_order_id)


@pytest.fixture(name='happy_path_cancelled_by_user')
async def _happy_path_cancelled_by_user(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_order_cancel,
        run_claims_segment_replication,
        run_notify_orders,
        taxi_cargo_dispatch,
        taxi_cargo_dispatch_monitor,
        *,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    await taxi_cargo_dispatch.tests_control(reset_metrics=True)
    happy_path_claims_segment_db.cancel_segment_by_user(segment_id)
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 1

    result = await run_notify_orders()
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-handle-processing',
    )
    assert result['stats']['waybills-for-handling'] == 1
    assert stats['stats']['resolved'] == 1
    await run_notify_orders()


@pytest.fixture(name='happy_path_chain_order')
async def _happy_path_chain_order(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        mark_performer_found,
        read_waybill_info,
        first_waybill_ref='waybill_fb_3',
        second_waybill_ref='waybill_smart_1',
):
    first_waybill = await read_waybill_info(first_waybill_ref)
    second_waybill = await read_waybill_info(second_waybill_ref)

    chain_parent_cargo_order_id = first_waybill['diagnostics']['order_id']
    taxi_order_id = second_waybill['execution']['taxi_order_info']['order_id']
    await mark_performer_found(
        second_waybill_ref,
        taxi_order_id,
        chain_parent_cargo_order_id=chain_parent_cargo_order_id,
    )
