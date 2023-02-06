import datetime

import pytest

from testsuite.utils import matching

# FALLBACK_ROUTER = 'fallback_router'

ARRIVE_SETTINGS_EXPERIMENT_NAME = (
    'cargo_dispatch_stq_cargo_alive_batch_confirmation_arrive_settings'
)

ARRIVE_SETTINGS_CONSUMER_NAME = (
    'cargo_dispatch/stq-cargo-alive-batch-confirmation-arrive-settings'
)

MOCK_TIME = '2021-01-01T00:00:00+00:00'
CARGO_ARRIVE_AT_POINT_DELAY = datetime.timedelta(seconds=5)
CARGO_ARRIVE_AT_POINT_DELAY_MILLISECONDS = (
    CARGO_ARRIVE_AT_POINT_DELAY.total_seconds() * 1000
)

MOCK_TIME_EXPECTED_ETA = (
    datetime.datetime.fromisoformat(MOCK_TIME) + CARGO_ARRIVE_AT_POINT_DELAY
).replace(tzinfo=None)


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.usefixtures('set_up_alive_batch_exp'),
    pytest.mark.parametrize(
        '',
        [
            pytest.param(
                marks=pytest.mark.experiments3(
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
                ),
            ),
            pytest.param(
                marks=pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    is_config=True,
                    name=ARRIVE_SETTINGS_EXPERIMENT_NAME,
                    consumers=[ARRIVE_SETTINGS_CONSUMER_NAME],
                    clauses=[],
                    default_value={
                        'mark_identical_source_points_as_arrived': False,
                        'cargo_arrive_at_point_delay': (
                            CARGO_ARRIVE_AT_POINT_DELAY_MILLISECONDS
                        ),
                    },
                ),
            ),
        ],
    ),
]


async def test_accept_offer(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        get_segment_info,
        mock_cargo_orders_bulk_info,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()
    stq.cargo_route_watch.flush()
    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'driver_approval_awaited'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    seg4 = await get_segment_info('seg4')
    assert 'chosen_waybill' not in seg4['dispatch']

    await update_proposition_alive_batch_stq(
        'my_waybill', wait_testpoint=False, call=True,
    )
    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['chosen_waybill']['external_ref'] == 'my_waybill'

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'processing'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    # Check driver notification
    assert stq.cargo_update_setcar_state_version.times_called == 1
    stq_call = stq.cargo_update_setcar_state_version.next_call()
    assert stq_call['kwargs'] == {
        'cargo_order_id': matching.AnyString(),
        'driver_notification_tanker_key': 'alive_batch.acceptance_success',
        'driver_notification_tanker_keyset': 'cargo',
        'driver_profile_id': 'driver_id_1',
        'park_id': 'park_id_1',
        'send_taximeter_push': True,
        'log_extra': {'_link': matching.AnyString()},
    }


async def test_reject_offer(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        pgsql,
):
    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'driver_approval_awaited'

    await update_proposition_alive_batch_stq(
        'my_waybill', times_called=0, call=False,
    )

    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='test_1',
        kwargs={
            'new_waybill_ref': 'my_waybill',
            'waybill_revision': 1,
            'is_offer_accepted': False,
        },
    )

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'resolved'
    assert new_wb['dispatch']['resolution'] == 'declined'

    # Check no driver notification
    assert not stq.cargo_update_setcar_state_version.times_called

    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        f"""select segment_id, reason, ticket, source
            from cargo_dispatch.admin_segment_reorders""",
    )
    reorders = list(cursor)
    assert reorders
    for reorder in reorders:
        assert reorder[1] == 'alive_batch_reject_autoreorder'


@pytest.mark.parametrize(
    ('is_first_racer_accept', 'is_second_racer_accept'),
    ((True, False), (False, True), (False, False)),
)
async def test_race_condition(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        is_first_racer_accept,
        is_second_racer_accept,
        get_segment_info,
        mock_cargo_orders_bulk_info,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()

    seg4 = await get_segment_info('seg4')
    assert 'chosen_waybill' not in seg4['dispatch']

    old_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert old_wb['dispatch']['is_waybill_accepted']

    seg4 = await get_segment_info('seg4')
    assert 'chosen_waybill' not in seg4['dispatch']

    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='first_racer',
        kwargs={
            'new_waybill_ref': 'my_waybill',
            'waybill_revision': 1,
            'is_offer_accepted': is_first_racer_accept,
        },
    )
    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['is_waybill_accepted'] == is_first_racer_accept

    assert (
        old_wb['waybill']['external_ref'] == new_wb['waybill']['external_ref']
    )
    assert old_wb['dispatch']['revision'] != new_wb['dispatch']['revision']

    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='second_racer',
        kwargs={
            'new_waybill_ref': 'my_waybill',
            'waybill_revision': 1,
            'is_offer_accepted': is_second_racer_accept,
        },
    )
    not_updated_wb = await read_waybill_info(
        'my_waybill', actual_waybill=False,
    )
    assert (
        not_updated_wb['dispatch']['is_waybill_accepted']
        == new_wb['dispatch']['is_waybill_accepted']
    )
    assert (
        new_wb['waybill']['external_ref']
        == not_updated_wb['waybill']['external_ref']
    )
    assert (
        new_wb['dispatch']['revision']
        == not_updated_wb['dispatch']['revision']
    )


async def test_accept_without_job_running(
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        get_segment_info,
        mock_cargo_orders_bulk_info,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_smart_1',
    )
    assert response.status_code == 200
    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'driver_approval_awaited'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    seg4 = await get_segment_info('seg4')
    assert 'chosen_waybill' not in seg4['dispatch']

    await update_proposition_alive_batch_stq(
        'my_waybill', wait_testpoint=False, call=True,
    )
    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['chosen_waybill']['external_ref'] == 'my_waybill'

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'processing'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'


async def test_reject_without_job_running(
        stq_runner,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        mock_cargo_orders_bulk_info,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_smart_1',
    )
    assert response.status_code == 200

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'driver_approval_awaited'

    await stq_runner.cargo_alive_batch_confirmation.call(
        task_id='test_1',
        kwargs={
            'new_waybill_ref': 'my_waybill',
            'waybill_revision': 1,
            'is_offer_accepted': False,
        },
    )

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'resolved'
    assert new_wb['dispatch']['resolution'] == 'declined'


async def test_cargo_alive_batch_confirmation_retry(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        run_choose_waybills,
        update_proposition_alive_batch_stq,
        mock_cargo_orders_bulk_info,
        get_segment_info,
        testpoint,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()
    stq.cargo_route_watch.flush()
    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'driver_approval_awaited'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    seg4 = await get_segment_info('seg4')
    assert 'chosen_waybill' not in seg4['dispatch']

    await update_proposition_alive_batch_stq(
        'my_waybill', wait_testpoint=False, call=True,
    )
    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['chosen_waybill']['external_ref'] == 'my_waybill'

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'processing'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    @testpoint('batch-confirm-offer-notify-driver-already-confirmed')
    def testpoint_retry(result):
        assert result['waybill_ref'] == 'my_waybill'
        assert result['status'] == 'processing'

    await update_proposition_alive_batch_stq(
        'my_waybill', wait_testpoint=False, call=True, exec_tries=1,
    )
    await testpoint_retry.wait_call()


async def test_update_proposition_for_batch(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        happy_path_state_seg7_routers_chosen,
        run_choose_waybills,
        mock_cargo_orders_bulk_info,
        update_proposition_alive_batch_stq,
        get_segment_info,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill', 'seg1', 'seg4', 'seg2',
    )
    response = await request_waybill_update_proposition(
        waybill, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()
    stq.cargo_route_watch.flush()
    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'driver_approval_awaited'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    seg4 = await get_segment_info('seg4')
    assert 'chosen_waybill' not in seg4['dispatch']

    await update_proposition_alive_batch_stq(
        'my_waybill', wait_testpoint=False, call=True,
    )
    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['chosen_waybill']['external_ref'] == 'my_waybill'

    new_wb = await read_waybill_info('my_waybill', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'processing'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill-2', 'seg1', 'seg2', 'seg7', 'seg4',
    )
    response = await request_waybill_update_proposition(waybill, 'my_waybill')
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()
    stq.cargo_route_watch.flush()

    new_wb = await read_waybill_info('my_waybill-2', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'driver_approval_awaited'
    assert 'chosen_waybill' not in new_wb['dispatch']
    assert new_wb['dispatch']['previous_waybill_ref'] == 'my_waybill'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    seg6 = await get_segment_info('seg7')
    assert 'chosen_waybill' not in seg6['dispatch']

    await update_proposition_alive_batch_stq(
        'my_waybill-2', wait_testpoint=False, call=True,
    )
    seg6 = await get_segment_info('seg7')
    assert seg6['dispatch']['chosen_waybill']['external_ref'] == 'my_waybill-2'
    seg4 = await get_segment_info('seg4')
    assert seg4['dispatch']['chosen_waybill']['external_ref'] == 'my_waybill-2'

    new_wb = await read_waybill_info('my_waybill-2', actual_waybill=False)
    assert new_wb['dispatch']['status'] == 'processing'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'my_waybill'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'


@pytest.fixture
def __mark_identical_source_points_as_arrived_enabled(get_experiment):
    def inner():
        exp = get_experiment(
            ARRIVE_SETTINGS_CONSUMER_NAME, ARRIVE_SETTINGS_EXPERIMENT_NAME,
        )
        return exp['default_value']['mark_identical_source_points_as_arrived']

    return inner


@pytest.mark.now(MOCK_TIME)
async def test_set_stq_cargo_waybill_auto_arrive(
        stq,
        stq_runner,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        update_proposition_alive_batch_stq,
        get_segment_info,
        happy_path_claims_segment_db,
        mock_claims_arrive_at_point,
        mock_claim_bulk_update_state,
        mock_cargo_orders_bulk_info,
        __mark_identical_source_points_as_arrived_enabled,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill = await waybill_from_segments(
        'smart_router', 'my_waybill', 'seg1', 'seg2', 'seg4',
    )
    arrived_point_info = {'segment_id': 'seg2', 'point_id': 'p1'}
    custom_context = {'place_id': 11534}
    point_ids = []
    expected_segment_points = []
    for segment_id in ['seg1', 'seg2', 'seg4']:
        segment = happy_path_claims_segment_db.get_segment(segment_id)
        segment.json['custom_context'].update(custom_context)
        for point in segment.json['points']:
            if point['segment_point_type'] == 'source':
                point_ids.append(point['claim_point_id'])
                expected_segment_points.append(
                    {
                        'claim_point_id': point['claim_point_id'],
                        'segment_id': segment_id,
                    },
                )

    segment = happy_path_claims_segment_db.get_segment(
        arrived_point_info['segment_id'],
    )
    segment.set_point_visit_status(arrived_point_info['point_id'], 'arrived')
    point = segment.get_point(arrived_point_info['point_id'])
    point_ids.remove(point['claim_point_id'])
    expected_segment_points.remove(
        {
            'claim_point_id': point['claim_point_id'],
            'segment_id': arrived_point_info['segment_id'],
        },
    )

    response = await request_waybill_update_proposition(
        waybill, 'waybill_smart_1',
    )

    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()
    stq.cargo_route_watch.flush()

    await update_proposition_alive_batch_stq(
        'my_waybill', wait_testpoint=False, call=True,
    )
    if __mark_identical_source_points_as_arrived_enabled():
        assert stq.cargo_waybill_auto_arrive.times_called == 1
        stq_call = stq.cargo_waybill_auto_arrive.next_call()
        assert stq_call == {
            'args': [],
            'eta': MOCK_TIME_EXPECTED_ETA,
            'id': matching.AnyString(),
            'kwargs': {
                'cargo_order_id': matching.AnyString(),
                'log_extra': {'_link': matching.AnyString()},
                'performer_info': {
                    'driver_id': 'driver_id_1',
                    'park_id': 'park_id_1',
                },
                'segment_points': expected_segment_points,
            },
            'queue': 'cargo_waybill_auto_arrive',
        }
    else:
        assert stq.cargo_waybill_auto_arrive.times_called == 0


async def test_update_proposition_idempotency(
        stq_runner,
        stq,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
        happy_path_state_seg7_routers_chosen,
        mock_cargo_orders_bulk_info,
        update_proposition_alive_batch_stq,
        get_segment_info,
        testpoint,
        pgsql,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')
    waybill_1 = await waybill_from_segments(
        'smart_router', 'w1', 'seg1', 'seg2', 'seg4',
    )
    waybill_2 = await waybill_from_segments(
        'smart_router', 'w2', 'seg1', 'seg2', 'seg7',
    )
    response = await request_waybill_update_proposition(
        waybill_1, 'waybill_smart_1',
    )
    assert response.status_code == 200
    stq.cargo_update_setcar_state_version.flush()
    stq.cargo_route_watch.flush()
    new_wb = await read_waybill_info(
        waybill_1['external_ref'], actual_waybill=False,
    )
    assert new_wb['dispatch']['status'] == 'driver_approval_awaited'
    assert new_wb['dispatch']['previous_waybill_ref'] == 'waybill_smart_1'
    assert new_wb['dispatch']['initial_waybill_ref'] == 'waybill_smart_1'

    @testpoint('update-proposition-test-idempotency')
    def test_point(data):
        assert data['updated_waybill_ref'] == 'waybill_smart_1'
        assert data['new_waybill_ref'] == waybill_2['external_ref']

    response = await request_waybill_update_proposition(
        waybill_2, 'waybill_smart_1',
    )
    assert response.status_code == 200
    assert test_point.times_called == 0

    await update_proposition_alive_batch_stq(
        'w1', wait_testpoint=False, call=True, times_called=1,
    )

    await update_proposition_alive_batch_stq(
        'w2', wait_testpoint=False, call=False, times_called=0,
    )
