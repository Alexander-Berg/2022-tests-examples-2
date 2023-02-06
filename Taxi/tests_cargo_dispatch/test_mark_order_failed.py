import pytest


FALLBACK_ROUTER = 'fallback_router'


# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


async def test_basic(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_fallback_waybills_proposed,
        stq,
        default_order_fail_request,
        waybill_id='waybill_fb_1',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'resolved'

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert waybill['dispatch']['resolution'] == 'failed'

    assert stq.cargo_route_watch.times_called == 1
    assert (
        stq.cargo_route_watch.next_call()['kwargs']['reason'] == 'order_cancel'
    )


async def test_reorder_required_by_counter(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_performer_found,
        set_up_cargo_dispatch_reorder_exp,
        pgsql,
        default_order_fail_request,
        waybill_id='waybill_fb_3',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id),
    )
    assert response.status_code == 200

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert not waybill['dispatch']['is_performer_assigned']
    assert waybill['dispatch']['resolution'] == 'failed'


async def test_reorder_not_required_by_counter(
        taxi_cargo_dispatch,
        read_waybill_info,
        set_up_cargo_dispatch_reorder_exp,
        happy_path_state_performer_found,
        default_order_fail_request,
        waybill_id='waybill_fb_3',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id),
    )
    assert response.status_code == 200

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert waybill['dispatch']['resolution'] == 'failed'


async def test_reorder_required_by_fail_reason(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_performer_found,
        set_up_cargo_dispatch_reorder_exp,
        default_order_fail_request,
        waybill_id='waybill_fb_3',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(
            waybill_id, fail_reason='provider_cancel',
        ),
    )
    assert response.status_code == 200

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert waybill['dispatch']['resolution'] == 'failed'


async def test_waybill_already_resolved(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_fallback_waybills_proposed,
        default_order_fail_request,
        waybill_id='waybill_fb_1',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id),
    )
    assert response.status_code == 200

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert waybill['dispatch']['resolution'] == 'failed'


async def test_performer_not_found(
        taxi_cargo_dispatch,
        happy_path_state_fallback_waybills_proposed,
        read_waybill_info,
        default_order_fail_request,
):
    waybill_id = 'waybill_fb_1'
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(
            waybill_id, fail_reason='performer_not_found',
        ),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'resolved'

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert waybill['dispatch']['resolution'] == 'performer_not_found'


async def test_early_hold(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        set_up_cargo_dispatch_reorder_exp,
        read_waybill_info,
        run_notify_claims,
        mockserver,
        default_order_fail_request,
        pgsql,
        waybill_id='waybill_fb_3',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(
            waybill_id, fail_reason='cancelled_by_early_hold',
        ),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'resolved'

    @mockserver.json_handler(
        '/cargo-claims/v1/segments/dispatch/bulk-update-state',
    )
    def bulk_handler(request):
        assert len(request.json['segments']) == 1
        assert request.json['segments'][0]['id'] == 'seg3'
        assert (
            request.json['segments'][0]['resolution']
            == 'cancelled_by_early_hold'
        )
        return {
            'processed_segment_ids': [
                seg['id'] for seg in request.json['segments']
            ],
        }

    await run_notify_claims()
    assert bulk_handler.times_called == 1

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert waybill['dispatch']['resolution'] == 'cancelled_by_early_hold'


async def test_update_claims_after_not_found(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mockserver,
        run_notify_claims,
        default_order_fail_request,
):
    waybill_id = 'waybill_fb_3'
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(
            waybill_id, fail_reason='performer_not_found',
        ),
    )
    assert response.status_code == 200

    @mockserver.json_handler(
        '/cargo-claims/v1/segments/dispatch/bulk-update-state',
    )
    def bulk_handler(request):
        assert len(request.json['segments']) == 1
        assert request.json['segments'][0]['id'] == 'seg3'
        assert (
            request.json['segments'][0]['resolution'] == 'performer_not_found'
        )
        return {
            'processed_segment_ids': [
                seg['id'] for seg in request.json['segments']
            ],
        }

    await run_notify_claims()
    assert bulk_handler.times_called == 1


async def test_reorder_update_segment(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_performer_found,
        get_segment_info,
        set_up_cargo_dispatch_reorder_exp,
        default_order_fail_request,
        waybill_id='waybill_fb_3',
):
    segment_id = 'seg3'
    segment = await get_segment_info(segment_id)
    old_waybill_building_version = 1
    old_segment_revision = 6
    assert (
        segment['dispatch']['waybill_building_version']
        == old_waybill_building_version
    )
    assert segment['dispatch']['revision'] == old_segment_revision

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id),
    )
    assert response.status_code == 200

    segment = await get_segment_info(segment_id)
    assert (
        segment['dispatch']['waybill_building_version']
        == old_waybill_building_version + 1
    )
    assert segment['dispatch']['revision'] == old_segment_revision + 1
    assert segment['dispatch']['status'] == 'new'
    assert not segment['dispatch']['resolved']


async def test_do_not_reorder_cancelled_segment(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_performer_found,
        get_segment_info,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        set_up_cargo_dispatch_reorder_exp,
        default_order_fail_request,
):
    """
    Waybill waybill_smart_1 includes [seg1, seg2]
    Client cancel seg2.
    Do not reorder this segment on /v1/waybill/mark/order-fail
    """
    waybill_id = 'waybill_smart_1'

    # Client cancels seg2
    happy_path_claims_segment_db.cancel_segment_by_user('seg2')
    await run_claims_segment_replication()

    # Driver cancels order. Make reorder
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id),
    )
    assert response.status_code == 200

    # Check segments statuses
    reordered_segment = await get_segment_info('seg1')
    assert reordered_segment['dispatch']['status'] == 'new'

    cancelled_segment = await get_segment_info('seg2')
    assert cancelled_segment['dispatch']['status'] == 'resolved'


@pytest.mark.parametrize('autoreorder_flow', ['oldway', 'newway'])
async def test_no_autoreorder_oldflow(
        taxi_cargo_dispatch,
        happy_path_state_first_import,
        run_choose_routers,
        propose_from_segments,
        run_choose_waybills,
        run_create_orders,
        run_notify_claims,
        happy_path_find_performer,
        get_segment_info,
        mock_claim_bulk_update_state,
        set_up_cargo_dispatch_reorder_exp,
        set_up_segment_routers_exp,
        autoreorder_flow: str,
        segment_id='seg3',
        waybill_id='waybill_fb_3',
):
    await set_up_segment_routers_exp(autoreorder_flow=autoreorder_flow)

    await run_choose_routers()
    await propose_from_segments('fallback_router', waybill_id, segment_id)
    await run_choose_waybills()
    await run_create_orders(should_set_stq=True)
    await run_notify_claims()
    await happy_path_find_performer()

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': 'performer_cancel',
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200

    segment = await get_segment_info(segment_id)
    if autoreorder_flow == 'oldway':
        expect_building_version = 1
    else:
        expect_building_version = 2
    assert (
        segment['dispatch']['waybill_building_version']
        == expect_building_version
    )


@pytest.mark.parametrize(
    ['autoreorder_expected'],
    [
        pytest.param(
            True,
            id="""
                Lookup started recently, autoreorder enabled.
            """,
        ),
        pytest.param(
            False,
            marks=pytest.mark.now('2000-01-01T10:35:00+0000'),
            id="""
                Lookup started long ago in the future,
                no need to autoreorder by exp.
            """,
        ),
    ],
)
async def test_autoreorder_lookup_started_time(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        get_segment_info,
        set_up_cargo_dispatch_reorder_exp,
        default_order_fail_request,
        autoreorder_expected: bool,
        waybill_id='waybill_fb_3',
        segment_id='seg3',
):
    segment = await get_segment_info(segment_id)

    old_waybill_building_version = segment['dispatch'][
        'waybill_building_version'
    ]

    await set_up_cargo_dispatch_reorder_exp(
        with_seconds_since_first_lookup=True,
    )
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id),
    )
    assert response.status_code == 200

    segment = await get_segment_info(segment_id)

    if autoreorder_expected:
        assert (
            segment['dispatch']['waybill_building_version']
            == old_waybill_building_version + 1
        )
    else:
        assert (
            segment['dispatch']['waybill_building_version']
            == old_waybill_building_version
        )


async def test_order_fail(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_fallback_waybills_proposed,
        default_order_fail_request,
        waybill_id='waybill_fb_1',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id, fail_reason='failed'),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'resolved'

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert waybill['dispatch']['resolution'] == 'technical_fail'


async def test_update_proposition_initial_waybill(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        set_up_cargo_dispatch_reorder_exp,
        taxi_cargo_dispatch,
        default_order_fail_request,
        initial_waybill_ref='waybill_fb_3',
        replace_waybill_ref='my_waybill',
):
    """
    Test /order-fail expects initial_waybill_ref instead of external_ref.
    And also check replaced waybills doesn't account in reorders count.
    """
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, replace_waybill_ref, 'seg3', 'seg6',
    )
    response = await request_waybill_update_proposition(
        waybill, initial_waybill_ref,
    )
    assert response.status_code == 200

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(
            initial_waybill_ref, fail_reason='performer_cancel',
        ),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'new'


async def test_admin_autoreorder_oldway(
        taxi_cargo_dispatch,
        happy_path_state_first_import,
        run_choose_routers,
        propose_from_segments,
        run_choose_waybills,
        run_create_orders,
        run_notify_claims,
        happy_path_find_performer,
        get_segment_info,
        mock_claim_bulk_update_state,
        set_up_cargo_dispatch_reorder_exp,
        set_up_segment_routers_exp,
        segment_id='seg3',
        waybill_id='waybill_fb_3',
):
    await set_up_segment_routers_exp(autoreorder_flow='oldway')
    await set_up_cargo_dispatch_reorder_exp(fail_reason='admin_reorder')

    await run_choose_routers()
    await propose_from_segments('fallback_router', waybill_id, segment_id)
    await run_choose_waybills()
    await run_create_orders(should_set_stq=True)
    await run_notify_claims()
    await happy_path_find_performer()

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': 'admin_reorder',
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200

    segment = await get_segment_info(segment_id)
    assert segment['dispatch']['waybill_building_version'] == 2
    assert segment['dispatch']['status'] == 'new'


@pytest.mark.config(
    CARGO_DISPATCH_PHOENIX_AUTOREORDER_SETTINGS={'disable_autoreorder': True},
)
async def test_reorder_disabled_for_phoenix(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_performer_found,
        set_up_cargo_dispatch_reorder_exp,
        pgsql,
        default_order_fail_request,
        mock_phoenix_traits,
        get_segment_info,
        waybill_id='waybill_fb_3',
):
    mock_phoenix_traits.expected_request = {
        'cargo_ref_id': 'order/b66b2650-31b5-46d2-95dc-5ff80f865c6f',
    }
    mock_phoenix_traits.use_phoenix_flow = True

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json=default_order_fail_request(waybill_id),
    )
    assert response.status_code == 200

    segment = await get_segment_info('seg3')
    # If reorder happened, status will be 'new'
    assert segment['dispatch']['status'] == 'wait_for_resolution'


@pytest.mark.parametrize(
    'claim_features, expected_building_version',
    [
        (
            # Not phoenix claim. Use oldway autoreorder
            [],
            1,
        ),
        (
            # Phoenix claim. Force newway autoreorder
            [{'id': 'phoenix_claim'}, {'id': 'agent_scheme'}],
            2,
        ),
    ],
)
async def test_autoreorder_flow_for_phoenix(
        taxi_cargo_dispatch,
        happy_path_state_first_import,
        run_choose_routers,
        propose_from_segments,
        run_choose_waybills,
        run_create_orders,
        run_notify_claims,
        happy_path_find_performer,
        get_segment_info,
        mock_claim_bulk_update_state,
        set_up_cargo_dispatch_reorder_exp,
        set_up_segment_routers_exp,
        happy_path_claims_segment_db,
        claim_features: list,
        expected_building_version: int,
        segment_id='seg3',
        waybill_id='waybill_fb_3',
):
    await set_up_segment_routers_exp(autoreorder_flow='oldway')

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_claim_features(claim_features)

    await run_choose_routers()
    await propose_from_segments('fallback_router', waybill_id, segment_id)
    await run_choose_waybills()
    await run_create_orders(should_set_stq=True)
    await run_notify_claims()
    await happy_path_find_performer()

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': 'performer_cancel',
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200

    segment = await get_segment_info(segment_id)
    assert (
        segment['dispatch']['waybill_building_version']
        == expected_building_version
    )


async def test_same_day_order_kwarg(
        happy_path_state_first_import,
        set_up_segment_routers_exp,
        propose_from_segments,
        experiments3,
        run_choose_routers,
        run_choose_waybills,
        run_create_orders,
        run_notify_claims,
        taxi_cargo_dispatch,
        mock_order_cancel,
        mock_claim_bulk_update_state,
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

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': '6dac297a-33ed-42e7-9101-af81ddf59602',
            'waybill_id': 'waybill_sdd_1',
            'taxi_order_id': 'taxi-order',
            'reason': 'performer_cancel',
            'lookup_version': 0,
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'new'


async def test_waybill_rebuild_reoder_required(
        taxi_cargo_dispatch,
        read_waybill_info,
        happy_path_state_performer_found,
        set_up_cargo_dispatch_reorder_exp,
        pgsql,
        default_order_fail_request,
        waybill_id='waybill_fb_3',
):
    order_fail_request = default_order_fail_request(waybill_id)
    order_fail_request['reason'] = 'waybill_rebuild_reorder_required'
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail', json=order_fail_request,
    )
    assert response.status_code == 200

    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['status'] == 'resolved'
    assert not waybill['dispatch']['is_performer_assigned']

    assert waybill['dispatch']['resolution'] == 'failed'

    cursor = pgsql['cargo_dispatch'].dict_cursor()
    cursor.execute(
        'select order_fail_reason from cargo_dispatch.waybills'
        + f' where external_ref= \'{waybill_id}\'',
    )

    waybill_data = dict(cursor.fetchone())
    assert (
        waybill_data['order_fail_reason'] == 'waybill_rebuild_reorder_required'
    )


@pytest.mark.parametrize(
    ['forced_action', 'expected_status'],
    [
        ('cancel_by_support_logics', 'resolved'),
        ('reorder_by_support_logics', 'new'),
    ],
)
async def test_admin_autoreorder_with_token(
        taxi_cargo_dispatch,
        happy_path_state_fallback_waybills_proposed,
        prepare_admin_segment_reorder,
        forced_action,
        expected_status,
        waybill_id='waybill_fb_1',
        segment_id='seg1',
        cancel_request_token='cargo-dispatch/12345',
):
    prepare_admin_segment_reorder(
        segment_id,
        1,
        reason='admin_reason_1',
        forced_action=forced_action,
        cancel_request_token=cancel_request_token,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/order-fail',
        json={
            'order_id': 'b66b2650-31b5-46d2-95dc-5ff80f865c6f',
            'waybill_id': waybill_id,
            'taxi_order_id': 'taxi-order',
            'reason': 'performer_cancel',
            'lookup_version': 0,
            'admin_cancel_reason': 'admin_reason_2',
            'cancel_request_token': cancel_request_token,
        },
    )
    assert response.status_code == 200
    assert response.json()['status'] == expected_status
