# pylint: disable=too-many-lines
import datetime

import pytest

FALLBACK_ROUTER = 'fallback_router'
SMART_ROUTER = 'smart_router'
JOB_NAME = 'cargo-dispatch-choose-waybills'

ARRIVE_SETTINGS_EXPERIMENT_NAME = (
    'cargo_dispatch_stq_cargo_alive_batch_confirmation_arrive_settings'
)

ARRIVE_SETTINGS_CONSUMER_NAME = (
    'cargo_dispatch/stq-cargo-alive-batch-confirmation-arrive-settings'
)

CARGO_ARRIVE_AT_POINT_DELAY = datetime.timedelta(seconds=5)
CARGO_ARRIVE_AT_POINT_DELAY_MILLISECONDS = (
    CARGO_ARRIVE_AT_POINT_DELAY.total_seconds() * 1000
)


# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


async def test_driver_approve_allowed_uncounted(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        run_choose_waybills,
        mocked_time,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', 'seg3', 'seg2',
    )
    await request_waybill_update_proposition(waybill, 'waybill_fb_3')

    mocked_time.sleep(10)

    result = await run_choose_waybills()
    assert result['stats']['oldest-waybill-lag-ms'] == 0


async def test_happy_path_works(
        happy_path_state_waybills_chosen, get_chosen_ref,
):
    result = happy_path_state_waybills_chosen

    # time has not come, nothing to mark as ready
    assert result['stats']['marked-as-ready'] == 0

    # waybill_smart_1 and waybill_fb_3 was marked as ready on /waybill/propose
    assert result['stats']['processed-waybills'] == 2

    # waybill_smart_1 includes [seg1,seg2], waybill_fb_3 includes [seg3]
    assert result['stats']['segments-with-chosen-waybills'] == 3

    # all 3 segments were updated
    assert result['stats']['updated-segments'] == 3

    # both waybills were accepted
    assert result['stats']['accepted-waybills'] == 2

    # no resolved segments, so no resolved waybills
    assert result['stats']['cancelled-waybills'] == 0
    assert result['stats']['dispatch-failed-waybills'] == 0

    # waybill_fb_1 and waybill_fb_2 were declined in favor of waybill_smart_1
    assert result['stats']['declined-waybills'] == 2

    # no expired segments
    assert result['stats']['expired-segments'] == 0

    assert (await get_chosen_ref('seg1')) == 'waybill_smart_1'
    assert (await get_chosen_ref('seg2')) == 'waybill_smart_1'
    assert (await get_chosen_ref('seg3')) == 'waybill_fb_3'


async def test_fallback_marked_as_ready_when_time_is_come(
        happy_path_state_fallback_waybills_proposed,
        run_choose_waybills,
        now,
        mocked_time,
        get_chosen_ref,
):
    mocked_time.sleep(1800)
    result = await run_choose_waybills()
    assert result['stats']['marked-as-ready'] == 2
    assert (await get_chosen_ref('seg1')) == 'waybill_fb_1'
    assert (await get_chosen_ref('seg2')) == 'waybill_fb_2'


async def test_ready_on_proposal_when_deadline_has_come(
        happy_path_state_routers_chosen,
        propose_from_segments,
        run_choose_waybills,
        mocked_time,
        get_chosen_ref,
):
    mocked_time.sleep(1800)
    await propose_from_segments(FALLBACK_ROUTER, 'waybill_fb_1', 'seg1')
    result = await run_choose_waybills()
    assert result['stats']['marked-as-ready'] == 0
    assert (await get_chosen_ref('seg1')) == 'waybill_fb_1'


@pytest.fixture(name='get_chosen_ref')
def _get_chosen_ref(get_segment_info):
    async def _wrapper(segment_id):
        seginfo = await get_segment_info(segment_id)
        return seginfo['dispatch']['chosen_waybill']['external_ref']

    return _wrapper


async def test_do_not_decline_old_version_waybill(
        happy_path_state_waybills_chosen,
        propose_from_segments,
        run_choose_routers,
        run_choose_waybills,
        get_chosen_ref,
        reorder_waybill,
        get_segment_info,
        read_waybill_info,
        mocked_time,
):
    """
    Waybill for seg3 was already proposed.
    Reorder was happened, and we incremented
    segment.waybill_building_version
    When we choose waybill for waybill_building_version=2, we
    do not need to decline old version waybills

    Actual for skips in Batch
    """

    # Check prepare data
    assert (await get_chosen_ref('seg1')) == 'waybill_smart_1'

    # Increment segment.waybill_building_version
    await reorder_waybill('waybill_smart_1')
    old_waybill = await read_waybill_info('waybill_smart_1')
    assert old_waybill['dispatch']['resolution'] == 'failed'
    segment = await get_segment_info('seg1')
    assert segment['dispatch']['waybill_building_version'] == 2
    assert segment['dispatch'].get('resolution') is None
    await run_choose_routers()

    # Propose waybill with new version:
    await propose_from_segments(FALLBACK_ROUTER, 'waybill_fb_new_1', 'seg1')
    waybill = await read_waybill_info('waybill_fb_new_1')
    assert not waybill['dispatch'].get('resolution')

    # Run job again and check that waybill with old version were not declined
    await run_choose_waybills()
    old_waybill = await read_waybill_info('waybill_smart_1')
    assert old_waybill['dispatch']['resolution'] == 'failed'


async def test_accept_waybill_update_proposition(
        happy_path_state_performer_found,
        run_choose_waybills,
        read_waybill_info,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'smart_router', 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        'update_propositions', wait_testpoint=False, call=True,
    )

    # Check waybills
    updated_waybill = await read_waybill_info(
        'waybill_smart_1', actual_waybill=False,
    )
    assert updated_waybill['dispatch']['status'] == 'resolved'
    assert updated_waybill['dispatch']['resolution'] == 'replaced'

    new_waybill = await read_waybill_info('update_propositions')
    assert new_waybill['dispatch']['status'] == 'processing'
    assert 'resolution' not in new_waybill['dispatch']


async def test_update_proposition_notify_taxi(
        happy_path_state_performer_found,
        run_choose_waybills,
        read_waybill_info,
        waybill_from_segments,
        request_waybill_update_proposition,
        stq,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'smart_router', 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()
    stq.cargo_route_watch.flush()

    # Test no field 'active_update_proposition' for half_alive_batch
    old_wayill = await read_waybill_info('waybill_smart_1')
    assert 'active_update_proposition' not in old_wayill['execution']

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        'update_propositions', wait_testpoint=False,
    )

    # Set new taximeter state version
    new_waybill = await read_waybill_info('update_propositions')
    assert new_waybill['execution']['state_version'] == 'v1_w_3_s_0_0_0'

    # Check stq was set
    assert stq.cargo_update_setcar_state_version.times_called == 1
    stq_call = stq.cargo_update_setcar_state_version.next_call()
    assert stq_call['kwargs']['driver_profile_id'] == 'driver_id_1'
    assert stq_call['kwargs']['park_id'] == 'park_id_1'
    assert stq_call['kwargs']['send_taximeter_push']

    assert stq.cargo_route_watch.times_called == 1
    assert (
        stq.cargo_route_watch.next_call()['kwargs']['reason']
        == 'waybill_changed'
    )


@pytest.mark.skip()
async def test_rejected_waybill_update_proposition(
        happy_path_state_performer_found,
        run_choose_waybills,
        read_waybill_info,
        waybill_from_segments,
        request_waybill_update_proposition,
        stq,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
):
    """
    Taxi class is not in [eda, lavka]
    """

    mock_cargo_orders_bulk_info(tariff_class='courier')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'smart_router', 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()
    stq.cargo_route_watch.flush()

    # Run job
    result = await run_choose_waybills()
    assert result['stats']['update-propositions-accepted'] == 0
    assert result['stats']['update-propositions-rejected'] == 1

    # Check waybills
    # Waybill was not updated
    updated_waybill = await read_waybill_info('waybill_smart_1')
    assert updated_waybill['dispatch']['status'] == 'processing'

    update_waybill = await read_waybill_info(
        'update_propositions', actual_waybill=False,
    )
    assert update_waybill['dispatch']['status'] == 'resolved'
    assert update_waybill['dispatch']['resolution'] == 'declined'

    # Check stq was not set
    assert stq.cargo_update_setcar_state_version.times_called == 0
    assert stq.cargo_route_watch.times_called == 0


@pytest.mark.skip()
async def test_alive_batch_with_new_segment_success(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_choose_waybills,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        run_claims_segment_replication,
        run_choose_routers,
        get_segment_info,
        happy_path_state_seg4_routers_chosen,
):
    """
    Waybill has 1 segment seg3.
    New segment seg4 was created. And LD proposes update waybill
    on segments [seg3, seg4]. Seg4 choses new waybill
    New waybill was accepted, and old waybill was replaced
    """
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'fallback_router', 'waybill_on_seg3_seg4', 'seg3', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_fb_3',
    )
    assert response.status_code == 200

    # Check segments before
    seg3 = await get_segment_info('seg3')
    assert seg3['dispatch']['chosen_waybill']['external_ref'] == 'waybill_fb_3'

    seg4 = await get_segment_info('seg4')
    assert 'chosen_waybill' not in seg4['dispatch']

    # Run job to choose waybill 'waybill_on_seg3_seg4' for 'seg4'
    result = await run_choose_waybills()
    assert result['stats']['update-propositions-accepted'] == 1
    assert result['stats']['update-propositions-rejected'] == 0

    # Check segments after
    seg3 = await get_segment_info('seg3')
    assert (
        seg3['dispatch']['chosen_waybill']['external_ref']
        == 'waybill_on_seg3_seg4'
    )
    assert seg3['dispatch']['status'] == 'wait_for_resolution'

    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['status'] == 'wait_for_resolution'
    assert (
        seg4['dispatch']['chosen_waybill']['external_ref']
        == 'waybill_on_seg3_seg4'
    )


@pytest.mark.skip()
async def test_alive_batch_with_new_segment_reject(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_choose_waybills,
        read_waybill_info,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        run_claims_segment_replication,
        run_choose_routers,
        get_segment_info,
        propose_from_segments,
):
    """
    Waybill has 1 segment seg3.
    New segment seg5 was created. And LD proposes update waybill
    on segments [seg3, seg5]. But Seg5 chooses another waybill
    New waybill was rejected, and old waybill was not changed
    """
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Create seg5
    points5 = [
        ('p1', 'A1', ('pickup', ['i1']), []),
        ('p2', 'B1', ('dropoff', ['i1']), []),
        ('p3', 'A1', ('return', ['i1']), []),
    ]
    happy_path_claims_segment_db.add_segment(
        segment_number=5, points=points5,
    )  # 'seg5'
    await run_claims_segment_replication()
    await run_choose_routers()

    # Another waybill was proposed on segment seg5
    await propose_from_segments(FALLBACK_ROUTER, 'waybill_fb_5', 'seg5')
    result = await run_choose_waybills()
    assert result['stats']['accepted-waybills'] == 1

    # Propose waybill waybill_fb_3 update
    proposition = await waybill_from_segments(
        'fallback_router', 'waybill_on_seg3_seg5', 'seg3', 'seg5',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_fb_3',
    )
    assert response.status_code == 200

    # Check segments before
    seg3 = await get_segment_info('seg3')
    assert seg3['dispatch']['chosen_waybill']['external_ref'] == 'waybill_fb_3'

    seg5 = await get_segment_info('seg5')
    assert seg5['dispatch']['chosen_waybill']['external_ref'] == 'waybill_fb_5'

    # Run job to try accept waybill update
    result = await run_choose_waybills()
    assert result['stats']['update-propositions-accepted'] == 0
    assert result['stats']['update-propositions-rejected'] == 1

    # Check segments after
    seg3 = await get_segment_info('seg3')
    assert seg3['dispatch']['chosen_waybill']['external_ref'] == 'waybill_fb_3'
    assert seg3['dispatch']['status'] == 'wait_for_resolution'

    seg5 = await get_segment_info('seg5')
    assert seg5['dispatch']['chosen_waybill']['external_ref'] == 'waybill_fb_5'
    assert seg5['dispatch']['status'] == 'wait_for_resolution'

    # Check waybill status
    update_proposition = await read_waybill_info(
        'waybill_on_seg3_seg5', actual_waybill=False,
    )
    assert update_proposition['dispatch']['resolution'] == 'declined'


def drop_value_by_key(key: str, objects_to_drop_key: list):
    for obj_to_drop in objects_to_drop_key:
        obj_to_drop.pop(key, None)


def increment_field_by_key(key: str, objects_to_incr: list):
    for obj_to_incr in objects_to_incr:
        obj_to_incr[key] += 1


async def test_alive_batch_check_waybill_fields(
        happy_path_state_performer_found,
        mock_cargo_orders_bulk_info,
        waybill_from_segments,
        request_waybill_update_proposition,
        pgsql,
        run_choose_waybills,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
):
    mock_cargo_orders_bulk_info(tariff_class='lavka')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'smart_router', 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    # Run job
    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        'update_propositions', wait_testpoint=False,
    )

    cursor = pgsql['cargo_dispatch'].dict_cursor()
    cursor.execute(
        """
        SELECT *
        FROM cargo_dispatch.waybills
        WHERE external_ref IN (%s, %s)
        ORDER BY created_ts ASC
        """,
        ('waybill_smart_1', 'update_propositions'),
    )

    old_waybill = dict(cursor.fetchone())
    new_waybill = dict(cursor.fetchone())

    drop_value_by_key('external_ref', [old_waybill, new_waybill])
    drop_value_by_key('created_ts', [old_waybill, new_waybill])
    drop_value_by_key('updated_ts', [old_waybill, new_waybill])
    drop_value_by_key('initial_waybill_ref', [old_waybill, new_waybill])
    drop_value_by_key('previous_waybill_ref', [old_waybill, new_waybill])
    drop_value_by_key('status', [old_waybill, new_waybill])
    drop_value_by_key('resolution', [old_waybill, new_waybill])
    drop_value_by_key('resolved_at', [old_waybill, new_waybill])
    drop_value_by_key('taximeter_state_version', [old_waybill, new_waybill])
    drop_value_by_key('revision', [old_waybill, new_waybill])
    drop_value_by_key('order_id', [old_waybill, new_waybill])
    drop_value_by_key('taxi_order_id', [old_waybill, new_waybill])
    drop_value_by_key('is_actual_waybill', [old_waybill, new_waybill])
    drop_value_by_key(
        'order_last_segment_updated_ts', [old_waybill, new_waybill],
    )
    drop_value_by_key('stq_create_orders_was_set', [old_waybill, new_waybill])
    increment_field_by_key('claims_changes_version', [old_waybill])

    assert (
        old_waybill == new_waybill
    ), 'Not all required fields were copied in alive batch'


async def test_rejected_proposed(
        happy_path_state_routers_chosen,
        propose_from_segments,
        run_choose_waybills,
        run_notify_claims,
        mock_claim_bulk_update_state,
        read_waybill_info,
        waybill_id='waybill_smart_1',
):
    await propose_from_segments(
        'smart_router', waybill_id, 'seg1', 'seg2', kind='fail_segments',
    )
    result = await run_choose_waybills()

    # time has not come, nothing to mark as ready
    assert result['stats']['marked-as-ready'] == 0

    # waybill_smart_1 as ready on /waybill/propose
    assert result['stats']['processed-waybills'] == 1

    # waybill_smart_1 includes [seg1,seg2]
    assert result['stats']['segments-with-chosen-waybills'] == 2

    # all 2 segments were updated
    assert result['stats']['updated-segments'] == 2

    # waybill was not accepted
    assert result['stats']['accepted-waybills'] == 0

    # waybill_smart_1 was proposed with kind fail_segments
    assert result['stats']['dispatch-failed-waybills'] == 1

    # waybill_smart_1 was resolved, check resolution
    waybill = await read_waybill_info(waybill_id)
    assert waybill['dispatch']['resolution'] == 'performer_not_found'

    # waybill_smart_1 was resolved, check resolution is sent to cargo-claims
    await run_notify_claims()
    assert mock_claim_bulk_update_state.last_request is not None
    for segment in mock_claim_bulk_update_state.last_request['segments']:
        assert segment['resolution'] == 'performer_not_found'


async def test_alive_batch_with_new_segment_success_race(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        get_segment_info,
        happy_path_state_seg4_routers_chosen,
        testpoint,
        taxi_cargo_dispatch,
):
    """
    Waybill has 1 segment seg3.
    -- Job 'choose_waybills' started
    -- Job reached function 'ProcessUpdateWaybillPropositions'
    New segment seg4 was created. And LD proposes update waybill
    on segments [seg3, seg4]. Seg4 has no chosen waybill
    Do not make actions with new waybill. Do it on next job iteration
    """
    mock_cargo_orders_bulk_info(tariff_class='eda')

    @testpoint(f'{JOB_NAME}::intermediate-result')
    async def job_intemediate_result(data):
        # Propose waybill update
        proposition = await waybill_from_segments(
            'fallback_router', 'waybill_on_seg3_seg4', 'seg3', 'seg4',
        )
        response = await request_waybill_update_proposition(
            proposition, 'waybill_fb_3',
        )
        assert response.status_code == 200

    # Process job before function  'ProcessUpdateWaybillPropositions'
    await taxi_cargo_dispatch.run_task(JOB_NAME)
    assert job_intemediate_result.times_called == 1

    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['status'] == 'routers_chosen'
    assert 'chosen_waybill' not in seg4['dispatch']

    # Check segments after
    seg3 = await get_segment_info('seg3')
    assert seg3['dispatch']['chosen_waybill']['external_ref'] == 'waybill_fb_3'
    assert seg3['dispatch']['status'] == 'wait_for_resolution'

    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['status'] == 'routers_chosen'
    assert 'chosen_waybill' not in seg4['dispatch']


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_decline_outdated_waybills(
        set_up_segment_routers_exp,
        happy_path_state_fallback_waybills_proposed,
        propose_from_segments,
        run_choose_waybills,
        mocked_time,
        waybill_id='waybill_smart_1_too_late',
):
    """
    If router send waybill after deadline it should be declined.
    """
    mocked_time.sleep(500)

    result = await run_choose_waybills()

    # time has come, choose fallback waybills
    assert result['stats']['marked-as-ready'] == 2

    # smart router proposes waybills
    await propose_from_segments(SMART_ROUTER, 'waybill_smart_1', 'seg1')

    # it is ready and declined
    result = await run_choose_waybills()
    assert result['stats']['declined-waybills'] == 1


@pytest.fixture(name='add_eta_to_point')
async def _add_eta_to_point(pgsql):
    def wrapper(*, waybill_ref, visit_order):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            """
            UPDATE cargo_dispatch.waybill_points
            SET
                estimated_time_of_arrival = '2020-07-20T11:08:00+00:00',
                estimated_distance_of_arrival = 100,
                is_approximate = true
            WHERE waybill_external_ref=%s and visit_order=%s
            RETURNING point_id
            """,
            (waybill_ref, visit_order),
        )
        assert cursor.fetchall(), 'Point was not updated'

    return wrapper


async def test_eta_on_update_proposition(
        happy_path_state_performer_found,
        run_choose_waybills,
        read_waybill_info,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
        get_point_execution_by_visit_order,
        add_eta_to_point,
        update_proposition_alive_batch_stq,
        waybill_ref='waybill_smart_1',
):
    mock_cargo_orders_bulk_info(tariff_class='eda')

    add_eta_to_point(waybill_ref=waybill_ref, visit_order=1)
    # Propose waybill update
    proposition = await waybill_from_segments(
        'smart_router', 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        'update_propositions', wait_testpoint=False, call=True,
    )

    # check for eta was not lost on proposition
    point = await get_point_execution_by_visit_order(
        waybill_ref='update_propositions', visit_order=1,
    )
    assert point['eta'] == '2020-07-20T11:08:00+00:00'


async def test_send_driver_notification_message(
        happy_path_state_performer_found,
        run_choose_waybills,
        waybill_from_segments,
        request_waybill_update_proposition,
        stq,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
        taxi_cargo_dispatch,
        update_proposition_alive_batch_stq,
):
    await taxi_cargo_dispatch.invalidate_caches()

    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'smart_router', 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        'update_propositions', wait_testpoint=False, call=True,
    )

    # Check stq was set
    assert stq.cargo_update_setcar_state_version.times_called == 1
    stq_call = stq.cargo_update_setcar_state_version.next_call()
    assert (
        stq_call['kwargs']['driver_notification_tanker_key']
        == 'alive_batch.acceptance_success'
    )
    assert stq_call['kwargs']['driver_notification_tanker_keyset'] == 'cargo'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_next_point_eta_settings',
    consumers=['cargo-dispatch/taximeter-actions'],
    clauses=[],
    default_value={'enable': True, 'allow_no_eta_on_error': False},
)
async def test_next_point_eta_after_update_proposition(
        happy_path_state_performer_found,
        run_choose_waybills,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        get_point_execution_by_visit_order,
        mockserver,
        dispatch_confirm_point,
        mock_claims_exchange_confirm,
        add_eta_to_point,
        mock_employee_timer,
        waybill_ref='waybill_smart_1',
        updated_waybill_ref='update_propositions',
):
    mock_cargo_orders_bulk_info(tariff_class='eda')

    add_eta_to_point(waybill_ref=waybill_ref, visit_order=2)
    proposition = await waybill_from_segments(
        'smart_router', updated_waybill_ref, 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, waybill_ref,
    )
    assert response.status_code == 200

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(updated_waybill_ref, call=True)

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=updated_waybill_ref, visit_order=2,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'

    mock_employee_timer.eta = '2020-07-20T11:09:00+00:00'
    response = await dispatch_confirm_point(updated_waybill_ref)
    assert response.status_code == 200

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=updated_waybill_ref, visit_order=2,
    )
    assert next_point['eta'] == '2020-07-20T11:09:00+00:00'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_next_point_eta_settings',
    consumers=['cargo-dispatch/taximeter-actions'],
    clauses=[],
    default_value={'enable': True, 'allow_no_eta_on_error': False},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name=ARRIVE_SETTINGS_EXPERIMENT_NAME,
    consumers=[ARRIVE_SETTINGS_CONSUMER_NAME],
    clauses=[],
    default_value={
        'mark_identical_source_points_as_arrived': True,
        'cargo_arrive_at_point_delay': (
            CARGO_ARRIVE_AT_POINT_DELAY_MILLISECONDS
        ),
    },
)
@pytest.mark.config(
    CARGO_DISPATCH_COMPUTE_ETA_WHEN_ACCEPT_PROPOSITION_ENABLED=True,
)
@pytest.mark.config(
    CARGO_DISPATCH_OVERWRITE_ETA_WHEN_ACCEPT_PROPOSITION_ENABLED=True,
)
async def test_compute_eta_when_update_proposition(
        happy_path_state_performer_found,
        run_choose_waybills,
        happy_path_claims_segment_db,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        get_point_execution_by_visit_order,
        mockserver,
        dispatch_confirm_point,
        mock_claims_exchange_confirm,
        add_eta_to_point,
        experiments3,
        taxi_cargo_dispatch,
        mocked_time,
        mock_employee_timer,
        read_waybill_info,
        mock_driver_trackstory,
        stq_runner,
        stq,
):
    # Arrive at point A1
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    # Make update proposition
    proposition = await waybill_from_segments(
        'fallback_router', 'waybill_on_seg3_seg4', 'seg3', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_fb_3',
    )
    assert response.status_code == 200
    await run_choose_waybills()

    for seg in ['seg3', 'seg4']:
        segment = happy_path_claims_segment_db.get_segment(seg)
        segment.json['custom_context'] = {'place_id': 123, 'region_id': 345}

    # Make accept update proposition
    mock_employee_timer.eta = '2020-07-20T11:09:00+00:00'
    mock_employee_timer.expected_request = None
    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='test_1',
        kwargs={
            'new_waybill_ref': 'waybill_on_seg3_seg4',
            'waybill_revision': 1,
            'is_offer_accepted': True,
        },
    )

    next_point = await get_point_execution_by_visit_order(
        waybill_ref='waybill_on_seg3_seg4', visit_order=2,
    )
    assert next_point['eta'] == '2020-07-20T11:09:00+00:00'


@pytest.mark.skip()
async def test_alive_batch_with_old_segment_resolved_race(
        happy_path_claims_segment_db,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        mock_cargo_orders_bulk_info,
        get_segment_info,
        happy_path_state_seg4_routers_chosen,
        testpoint,
        taxi_cargo_dispatch,
        run_claims_segment_replication,
):
    """
    Waybill has 1 segment seg3.
    New segment seg4 was created.
    And LD proposes update waybill on segments [seg3, seg4]
    -- Job 'choose_waybills' started
    -- Job reached function 'ProcessUpdateWaybillPropositions'
    Seg3 was cancelled by user
    Reject update proposition
    """
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'fallback_router', 'waybill_on_seg3_seg4', 'seg3', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_fb_3',
    )
    assert response.status_code == 200

    @testpoint(f'{JOB_NAME}::intermediate-result')
    async def job_intemediate_result(data):
        # Resolve seg3
        happy_path_claims_segment_db.cancel_segment_by_user('seg3')
        repl_res = await run_claims_segment_replication()
        assert repl_res['stats']['updated-waybills'] == 1

    @testpoint(f'{JOB_NAME}::result')
    def job_result(data):
        pass

    # Process job before function  'ProcessUpdateWaybillPropositions'
    await taxi_cargo_dispatch.run_task(JOB_NAME)
    assert job_intemediate_result.times_called == 1

    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['status'] == 'new'
    assert 'chosen_waybill' not in seg4['dispatch']
    assert seg4['dispatch']['waybill_building_version'] == 2

    # Finish task. Check that proposition process was delayed
    result = job_result.next_call()
    assert result['data']['stats']['update-propositions-accepted'] == 0
    assert result['data']['stats']['update-propositions-rejected'] == 1
    assert result['data']['stats']['update-propositions-delayed'] == 0

    # Check segments after
    seg3 = await get_segment_info('seg3')
    assert seg3['dispatch']['chosen_waybill']['external_ref'] == 'waybill_fb_3'
    assert seg3['dispatch']['status'] == 'resolved'

    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['status'] == 'new'


@pytest.mark.config(
    CARGO_DISPATCH_CHOOSE_WAYBILLS_SETTINGS={
        'enabled': True,
        'unprocessed_limit': 1000,
        'segments_without_waybills_expiration_min': 0,
    },
)
@pytest.mark.now('2020-12-28T18:37:00.00+00:00')
async def test_expire_segments(
        happy_path_state_routers_chosen,
        run_choose_waybills,
        get_segment_info,
        create_seg4,
        propose_from_segments,
):
    """
    Fail segments if there is no chosen_waybill too long
    """

    # Do it to execute db request
    # (because there is an optimization to reduce empty db requests)
    await create_seg4()
    await propose_from_segments(SMART_ROUTER, 'waybill_fb_4', 'seg4')

    seg3 = await get_segment_info('seg3')
    assert seg3['dispatch']['status'] == 'routers_chosen'

    result = await run_choose_waybills()
    assert result['stats']['expired-segments'] == 5

    seg3 = await get_segment_info('seg3')
    assert seg3['dispatch']['status'] == 'resolved'
    assert seg3['dispatch']['resolved']


@pytest.mark.config(
    CARGO_DISPATCH_CHOOSE_WAYBILLS_SETTINGS={
        'enabled': True,
        'unprocessed_limit': 1000,
        'segments_without_waybills_expiration_min': 0,
    },
)
@pytest.mark.now('2020-12-28T18:37:00.00+00:00')
async def test_notify_claims_on_expired_segment(
        happy_path_state_routers_chosen,
        run_choose_waybills,
        run_notify_claims,
        mock_claim_bulk_update_state,
        create_seg4,
        propose_from_segments,
        stq_runner,
        taxi_cargo_dispatch_monitor,
):
    """
    Fail segments if there is no chosen_waybill too long
    """

    # Do it to execute db request
    # (because there is an optimization to reduce empty db requests)
    await create_seg4()
    await propose_from_segments(SMART_ROUTER, 'waybill_fb_4', 'seg4')

    await run_notify_claims()
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats']['segments-notified-count'] == 0

    result = await run_choose_waybills()
    assert result['stats']['expired-segments'] == 5

    await run_notify_claims(should_set_stq=False)
    updated_segments = []
    for segment_id in range(1, 7):
        await stq_runner.cargo_dispatch_notify_claims.call(
            task_id='test', kwargs={'segment_id': 'seg' + str(segment_id)},
        )
        assert mock_claim_bulk_update_state.handler.times_called == 1
        update_request = mock_claim_bulk_update_state.handler.next_call()[
            'request'
        ].json
        updated_segments.append(update_request['segments'][0])

    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats']['segments-notified-count'] == 6

    assert updated_segments == [
        {'id': 'seg1', 'resolution': 'performer_not_found', 'revision': 2},
        {'id': 'seg2', 'resolution': 'performer_not_found', 'revision': 2},
        {'id': 'seg3', 'resolution': 'performer_not_found', 'revision': 2},
        {
            'id': 'seg4',
            'autoreorder_flow': 'newway',
            'revision': 2,
            'router_id': 'smart_router',
        },
        {'id': 'seg5', 'resolution': 'performer_not_found', 'revision': 2},
        {'id': 'seg6', 'resolution': 'performer_not_found', 'revision': 2},
    ]


@pytest.mark.config(
    EATS_PERFORMERS_NOTIFICATION_ALLOWLIST=[
        'corp_client_id_56789012345678912',
    ],
    EATS_PERFORMERS_NOTIFICATION_ENABLED=True,
)
async def test_update_proposition_notify_tg(
        happy_path_state_performer_found,
        run_choose_waybills,
        waybill_from_segments,
        request_waybill_update_proposition,
        stq,
        mock_cargo_orders_bulk_info,
        mockserver,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
):
    claim_ids = ['claim_seg1', 'claim_seg2', 'claim_seg4']

    @mockserver.json_handler('/cargo-claims/v1/segments/bulk-info/cut')
    def _handler(request):
        return {
            'segments': [
                {
                    'id': segment['segment_id'],
                    'allow_batch': True,
                    'claim_revision': 1,
                    'claim_version': 0,
                    'status': 'segment_status',
                    'corp_client_id': 'corp_client_id_56789012345678912',
                    'claim_id': claim_id,
                }
                for segment, claim_id in zip(
                    request.json['segment_ids'], claim_ids,
                )
            ],
        }

    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'smart_router', 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        'update_propositions', wait_testpoint=False,
    )

    # Check stq was called
    assert stq.eats_logistics_performer_pre_assign.times_called == 3

    for claim_id in claim_ids:
        kwargs = stq.eats_logistics_performer_pre_assign.next_call()['kwargs']
        assert kwargs['claim_id'] == claim_id
        assert kwargs['park_driver_profile_id'] == 'park_id_1_driver_id_1'


@pytest.mark.now('2020-04-01T10:35:01+0000')
async def test_lag(
        happy_path_state_all_waybills_proposed,
        run_choose_waybills,
        get_chosen_ref,
        pgsql,
):
    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
            UPDATE cargo_dispatch.waybills
            SET updated_ts='2020-04-01T10:35:00+0000'
        """,
    )

    result = await run_choose_waybills()
    assert result['stats']['processed-waybills'] == 2

    # lag
    assert result['stats']['oldest-waybill-lag-ms'] == 1000


@pytest.mark.config(
    CARGO_DISPATCH_CHOOSE_WAYBILLS_SETTINGS={
        'enabled': True,
        'unprocessed_limit': 1000,
        'rate_limit': {'limit': 10, 'interval': 1, 'burst': 20},
    },
)
@pytest.mark.parametrize(
    'quota, expected_waybills_count', [(10, 2), (2, 2), (1, 1)],
)
async def test_rate_limit(
        happy_path_state_all_waybills_proposed,
        taxi_cargo_dispatch_monitor,
        run_choose_waybills,
        rps_limiter,
        quota,
        expected_waybills_count,
        testpoint,
):
    @testpoint('choose-waybills-check-limits')
    def _test_point(data):
        assert data['limit'] == quota

    rps_limiter.set_budget('cargo-dispatch-choose-waybills', quota)

    result = await run_choose_waybills()
    assert result['stats']['processed-waybills'] == expected_waybills_count

    statistics = await taxi_cargo_dispatch_monitor.get_metric('rps-limiter')
    limiter = statistics['cargo-dispatch-distlocks-limiter']
    assert limiter['quota-requests-failed'] == 0

    resource = limiter['resource_stat']['cargo-dispatch-choose-waybills']
    assert resource['decision']['rejected'] == 0
    assert resource['quota-assigned'] == quota
    assert resource['limit'] == 10


async def test_resolved_waybill_will_not_be_accepted(
        happy_path_state_all_waybills_proposed,
        run_choose_waybills,
        testpoint,
        pgsql,
        read_waybill_info,
        waybill='waybill_fb_3',
):
    @testpoint('decline-waybill-before-write-gambling-result')
    def test_point(data):
        cursor = pgsql['cargo_dispatch'].cursor()
        cursor.execute(
            f"""
        UPDATE cargo_dispatch.waybills
        SET status = 'resolved',
            resolution = 'declined'
        where external_ref = 'waybill_fb_3';
        """,
        )

    result = await run_choose_waybills()

    # waybill_fb_3 weren't accepted because it is resolved
    assert result['stats']['accepted-waybills'] == 1

    assert test_point.times_called == 1

    # check status
    info = await read_waybill_info(waybill)
    assert info['dispatch']['status'] == 'resolved'
