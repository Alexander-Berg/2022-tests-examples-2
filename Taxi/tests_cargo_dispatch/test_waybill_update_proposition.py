import datetime

import pytest

from testsuite.utils import matching

SMART_ROUTER = 'smart_router'
FALLBACK_ROUTER = 'fallback_router'

# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


@pytest.mark.parametrize(
    'added_segments',
    [
        (['seg6']),
        pytest.param(
            ['seg6', 'seg5'],
            marks=pytest.mark.experiments3(
                filename='exp3_cargo_alive_batch_add_segments.json',
            ),
        ),
    ],
)
async def test_happy_path(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        added_segments,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', 'seg3', *added_segments,
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 200

    new_proposed_waybill = await read_waybill_info(
        'my_waybill', actual_waybill=False,
    )
    assert (
        new_proposed_waybill['dispatch']['status'] == 'driver_approval_awaited'
    )
    assert (
        new_proposed_waybill['dispatch']['previous_waybill_ref']
        == 'waybill_fb_3'
    )
    assert (
        new_proposed_waybill['dispatch']['initial_waybill_ref']
        == 'waybill_fb_3'
    )
    assert new_proposed_waybill['dispatch']['revision'] == 1

    initial_waybill = await read_waybill_info('waybill_fb_3')
    assert initial_waybill['dispatch']['status'] == 'processing'
    assert 'previous_waybill_ref' not in initial_waybill['dispatch']
    assert 'initial_waybill_ref' not in initial_waybill['dispatch']

    # Test field 'active_update_proposition' for alive_batch
    assert initial_waybill['execution']['active_update_proposition'] == {
        'revision': 1,
        'waybill_ref': 'my_waybill',
    }
    assert initial_waybill['dispatch']['revision'] == 5


async def test_happy_path_with_forbidden_segment_router(
        happy_path_state_performer_found,
        happy_path_state_seg4_routers_chosen,
        get_segment_info,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        stq,
        stq_runner,
        run_choose_waybills,
):
    seginfo = await get_segment_info('seg4')
    assert seginfo['dispatch']['best_router_id'] == SMART_ROUTER

    waybill = await waybill_from_segments(
        SMART_ROUTER, 'my_waybill', 'seg3', 'seg4',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 200

    new_proposed_waybill = await read_waybill_info(
        'my_waybill', actual_waybill=False,
    )
    assert (
        new_proposed_waybill['dispatch']['status'] == 'driver_approval_awaited'
    )
    assert (
        new_proposed_waybill['dispatch']['previous_waybill_ref']
        == 'waybill_fb_3'
    )
    assert (
        new_proposed_waybill['dispatch']['initial_waybill_ref']
        == 'waybill_fb_3'
    )
    assert new_proposed_waybill['dispatch']['revision'] == 1

    initial_waybill = await read_waybill_info('waybill_fb_3')
    assert initial_waybill['dispatch']['status'] == 'processing'
    assert 'previous_waybill_ref' not in initial_waybill['dispatch']
    assert 'initial_waybill_ref' not in initial_waybill['dispatch']
    assert initial_waybill['execution']['state_version'] == 'v1_w_2_s_0'

    # Test field 'active_update_proposition' for alive_batch
    assert initial_waybill['execution']['active_update_proposition'] == {
        'revision': 1,
        'waybill_ref': 'my_waybill',
    }
    assert initial_waybill['dispatch']['revision'] == 5

    # Now driver accepted offer and stq 'cargo_alive_batch_confirmation'
    # was set in cargo-orders
    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='test_01',
        kwargs={
            'new_waybill_ref': 'my_waybill',
            'waybill_revision': 1,
            'is_offer_accepted': True,
        },
    )

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'processing'
    assert 'resolution' not in new_wb['dispatch']

    old_wb = await read_waybill_info('waybill_fb_3', actual_waybill=False)
    assert old_wb['dispatch']['status'] == 'resolved'
    assert old_wb['dispatch']['resolution'] == 'declined'


async def test_propose_on_resolved_waybill(
        happy_path_cancelled_by_user,
        waybill_from_segments,
        request_waybill_propose,
        request_waybill_update_proposition,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'proposition_on_resolved_segment', 'seg3', 'seg2',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_1',
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'nonexistent_segment',
        'message': 'Waybill arderady resolved: declined',
    }


async def test_updated_waybill_not_found(
        happy_path_state_all_waybills_proposed,
        waybill_from_segments,
        request_waybill_update_proposition,
):
    waybill = await waybill_from_segments(SMART_ROUTER, 'proposition', 'seg3')
    response = await request_waybill_update_proposition(
        waybill, 'unknown_waybill',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'Not Found',
        'message': 'Waybill unknown_waybill was not found',
    }


async def test_updated_the_same_external_ref(
        happy_path_state_all_waybills_proposed,
        waybill_from_segments,
        request_waybill_update_proposition,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'waybill_fb_3', 'seg3',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'waybill_ref_not_unique',
        'message': (
            'Trying to update waybill by waybill with the same external ref'
        ),
    }


async def test_no_performer(
        happy_path_state_all_waybills_proposed,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill_1', 'seg3', 'seg2',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'no_taxi_performer',
        'message': (
            'Taxi performer does not exists yet. Can not update waybill'
        ),
    }


async def test_wrong_points_prefix(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        mock_cargo_orders_bulk_info,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill_1', 'seg3', 'seg2',
    )
    waybill['points'][0]['point_id'] = 'unknown'
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_path',
        'message': (
            'Next order point is not represents '
            'in update proposition on right position: seg3_A1_p1'
        ),
    }


@pytest.mark.parametrize(
    'response_json',
    [
        pytest.param(
            {
                'code': 'invalid_path',
                'message': 'Not 1 segment were added in update proposition',
            },
        ),
        pytest.param(
            {
                'code': 'invalid_path',
                'message': (
                    'At least one base waybill segment '
                    'does not exists in update proposition: seg3'
                ),
            },
            marks=pytest.mark.experiments3(
                filename='exp3_cargo_alive_batch_add_segments.json',
            ),
        ),
    ],
)
async def test_no_old_segments(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        response_json,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill_1', 'seg2',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 400
    assert response.json() == response_json


async def test_proposal_kind(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', 'seg3', 'seg2', kind='fail_segments',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'invalid_kind'


async def test_update_setcar_state_version(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        stq,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', 'seg3', 'seg6',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 200

    assert stq.cargo_update_setcar_state_version.times_called == 1
    stq_call = stq.cargo_update_setcar_state_version.next_call()
    assert stq_call['kwargs'] == {
        'cargo_order_id': matching.AnyString(),
        'driver_profile_id': 'driver_id_1',
        'park_id': 'park_id_1',
        'send_taximeter_push': True,
        'log_extra': {'_link': matching.AnyString()},
    }


@pytest.mark.parametrize('is_first_point_visited', [True, False])
async def test_alive_batch_happy_path(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_claims_segment_db,
        stq,
        stq_runner,
        happy_path_state_seg4_routers_chosen,
        run_choose_waybills,
        experiments3,
        taxi_cargo_dispatch,
        run_notify_orders,
        mock_order_change_destination,
        is_first_point_visited,
):
    """
    Test full alive batch flow
    Monster test
    Use 'waybill_fb_3' as base waybill. Segment 'seg3'
    """

    # Set up experiment to 'skip_full_alive_batch_in_job'
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_alive_batch_settings',
        consumers=['cargo-dispatch/alive-batch'],
        clauses=[],
        default_value={
            'process_update_propositions_limit': 10,
            'receive_update_proposition': True,
            'skip_full_alive_batch_in_job': True,
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    if is_first_point_visited:
        # Set first point visited. Driver already visited it
        # (A1) and drive to B1
        segment = happy_path_claims_segment_db.get_segment('seg3')
        segment.set_point_visit_status('p1', 'visited')

    # LD proposed alive batch on 'waybill_fb_3'
    proposition = await waybill_from_segments(
        'fallback_router', 'waybill_on_seg3_seg4', 'seg3', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_fb_3',
    )
    assert response.status_code == 200

    # Check:
    # 1) state_version was updates, so taximeter will update state
    # 2) Field 'active_update_proposition' has info about offer
    old_wb = await read_waybill_info('waybill_fb_3')
    assert old_wb['dispatch']['status'] == 'processing'
    assert old_wb['execution']['state_version'] == 'v1_w_2_s_0'
    assert old_wb['execution']['active_update_proposition'] == {
        'revision': 1,
        'waybill_ref': 'waybill_on_seg3_seg4',
    }

    # Run job, because we need 'seg4' to choose waybill 'waybill_on_seg3_seg4'
    await run_choose_waybills()

    # Now driver accepted offer and stq 'cargo_alive_batch_confirmation'
    # was set in cargo-orders
    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='test_1',
        kwargs={
            'new_waybill_ref': 'waybill_on_seg3_seg4',
            'waybill_revision': 1,
            'is_offer_accepted': True,
        },
    )

    new_wb = await read_waybill_info(
        'waybill_on_seg3_seg4', actual_waybill=False,
    )
    assert new_wb['dispatch']['status'] == 'processing'

    if is_first_point_visited:
        # Check request to /changedestinations
        result = await run_notify_orders()
        assert result['stats']['waybills-for-handling'] == 1
        assert mock_order_change_destination.times_called == 1
        assert mock_order_change_destination.next_call()['request'].json == {
            'order_id': matching.any_string,
            'dispatch_version': 2,
            'claim_id': 'claim_seg4',
            'segment_id': 'seg4',
            'claim_point_id': 41,
            'idempotency_token': 'waybill_on_seg3_seg4_41_2',
        }


async def test_half_alive_batch_revision_mismatch(
        happy_path_state_performer_found,
        run_choose_waybills,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        pgsql,
        testpoint,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        SMART_ROUTER, 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    await run_choose_waybills()

    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        'UPDATE cargo_dispatch.waybills '
        'SET revision = revision + 1 '
        'WHERE external_ref=%s',
        ('update_propositions',),
    )

    @testpoint('batch-confirm-offer-outdated-revision-mismatch')
    def test_point(data):
        assert data['new_waybill_ref'] == 'update_propositions'
        assert data['db_revision'] == 2
        assert data['task_revision'] == 1

    await update_proposition_alive_batch_stq(
        'update_propositions', wait_testpoint=False, call=True,
    )

    await test_point.wait_call()


async def test_half_alive_batch_prev_order_id_null(
        happy_path_state_performer_found,
        run_choose_waybills,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        pgsql,
        testpoint,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        SMART_ROUTER, 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    await run_choose_waybills()
    await update_proposition_alive_batch_stq('update_propositions')

    @testpoint('batch-confirmation-initial-waybill-replaced')
    def test_point(data):
        assert data['new_waybill_ref'] == 'update_propositions'

    await update_proposition_alive_batch_stq(
        'update_propositions', wait_testpoint=False, call=True,
    )

    await test_point.wait_call()


@pytest.mark.now('2021-08-09T12:00:00.00+00:00')
async def test_alive_batch_auto_set_decline_stq(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        stq,
        happy_path_state_seg4_routers_chosen,
        experiments3,
        taxi_cargo_dispatch,
        stq_runner,
        read_waybill_info,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_alive_batch_settings',
        consumers=['cargo-dispatch/alive-batch'],
        clauses=[],
        default_value={
            'process_update_propositions_limit': 10,
            'receive_update_proposition': True,
            'autoreject_delay_seconds': 30,
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    proposition = await waybill_from_segments(
        'fallback_router', 'waybill_on_seg3_seg4', 'seg3', 'seg4',
    )

    response = await request_waybill_update_proposition(
        proposition, 'waybill_fb_3',
    )
    assert response.status_code == 200

    old_wb = await read_waybill_info('waybill_fb_3', actual_waybill=False)
    assert old_wb['dispatch']['is_waybill_accepted']

    assert stq.cargo_alive_batch_confirmation.times_called == 1
    stq_call = stq.cargo_alive_batch_confirmation.next_call()
    assert stq_call['id'] == 'autoreject_waybill_on_seg3_seg4_1'

    assert stq_call['eta'] == datetime.datetime(2021, 8, 9, 12, 0, 30)

    kwargs = stq_call['kwargs']
    assert kwargs['new_waybill_ref'] == 'waybill_on_seg3_seg4'
    assert kwargs['waybill_revision'] == 1
    assert not kwargs['is_offer_accepted']
    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='autoreject_waybill_on_seg3_seg4_1',
        kwargs={
            'new_waybill_ref': 'waybill_on_seg3_seg4',
            'waybill_revision': 1,
            'is_offer_accepted': False,
        },
    )
    new_wb = await read_waybill_info(
        'waybill_on_seg3_seg4', actual_waybill=False,
    )
    assert not new_wb['dispatch']['is_waybill_accepted']

    assert (
        old_wb['waybill']['external_ref'] != new_wb['waybill']['external_ref']
    )
    assert old_wb['dispatch']['revision'] != new_wb['dispatch']['revision']

    not_updated_wb = await read_waybill_info(
        'waybill_fb_3', actual_waybill=False,
    )
    assert not_updated_wb['dispatch']['is_waybill_accepted']
    assert (
        old_wb['dispatch']['revision']
        == not_updated_wb['dispatch']['revision']
    )


async def test_update_proposition_idempotency(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        pgsql,
        testpoint,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', 'seg3', 'seg6',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 200

    new_proposed_waybill = await read_waybill_info(
        'my_waybill', actual_waybill=False,
    )
    assert (
        new_proposed_waybill['dispatch']['status'] == 'driver_approval_awaited'
    )
    assert (
        new_proposed_waybill['dispatch']['previous_waybill_ref']
        == 'waybill_fb_3'
    )
    assert (
        new_proposed_waybill['dispatch']['initial_waybill_ref']
        == 'waybill_fb_3'
    )

    @testpoint('update-proposition-test-idempotency')
    def test_point(data):
        assert data['updated_waybill_ref'] == 'waybill_fb_3'
        assert data['new_waybill_ref'] == 'my_waybill'

    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 200
    assert test_point.times_called == 1


async def test_skip_resolved_point(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_claims_segment_db,
        mock_claims_bulk_info,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', 'seg3', 'seg6',
    )
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')
    segment.set_point_visit_status('p2', 'visited')

    del waybill['points'][0]
    del waybill['points'][1]

    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 200

    new_proposed_waybill = await read_waybill_info(
        'my_waybill', actual_waybill=False,
    )
    assert (
        new_proposed_waybill['dispatch']['status'] == 'driver_approval_awaited'
    )

    initial_waybill = await read_waybill_info('waybill_fb_3')
    assert initial_waybill['dispatch']['status'] == 'processing'

    # Test field 'active_update_proposition' for alive_batch
    assert initial_waybill['execution']['active_update_proposition'] == {
        'revision': 1,
        'waybill_ref': 'my_waybill',
    }

    initial_points = [
        point['point_id'] for point in initial_waybill['execution']['points']
    ]
    assert initial_points == ['seg3_A1_p1', 'seg3_B1_p2', 'seg3_A1_p3']

    new_points = [
        point['point_id']
        for point in new_proposed_waybill['execution']['points']
    ]
    assert new_points == [
        'seg3_A1_p1',
        'seg3_B1_p2',
        'seg6_A1_p1',
        'seg6_B1_p2',
        'seg3_A1_p3',
        'seg6_C1_p3',
    ]


async def test_alive_batch_get_route(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        happy_path_claims_segment_db,
        stq_runner,
        happy_path_state_seg4_routers_chosen,
        run_choose_waybills,
        taxi_cargo_dispatch,
):
    # LD proposed alive batch on 'waybill_fb_3'
    proposition = await waybill_from_segments(
        'fallback_router', 'waybill_on_seg3_seg4', 'seg3', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_fb_3',
    )
    assert response.status_code == 200

    # Run job, because we need 'seg4' to choose waybill 'waybill_on_seg3_seg4'
    await run_choose_waybills()

    # Now driver accepted offer and stq 'cargo_alive_batch_confirmation'
    # was set in cargo-orders
    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='test_1',
        kwargs={
            'new_waybill_ref': 'waybill_on_seg3_seg4',
            'waybill_revision': 1,
            'is_offer_accepted': True,
        },
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/segment/route', json={'segment_id': 'seg3'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'route': [
            {'point_id': 'seg3_A1_p1'},
            {'point_id': 'seg4_A1_p1'},
            {'point_id': 'seg3_B1_p2'},
            {'point_id': 'seg4_B1_p2'},
            {'point_id': 'seg3_A1_p3'},
            {'point_id': 'seg4_A1_p3'},
        ],
    }


async def test_incorrect_request(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', 'seg3', 'seg1',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_fb_3',
    )
    assert response.status_code == 409
