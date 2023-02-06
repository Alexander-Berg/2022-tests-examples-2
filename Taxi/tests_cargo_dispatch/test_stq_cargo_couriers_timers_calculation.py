import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_next_point_eta_settings',
    consumers=['cargo-dispatch/taximeter-actions'],
    clauses=[],
    default_value={
        'enable': True,
        'allow_no_eta_on_error': True,
        'async_eta_calculation_enabled': True,
    },
)
@pytest.mark.now('2020-07-20T11:09:40+00:00')
async def test_async_timers_calculation(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq_runner,
        mockserver,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    """
        Async timers calculation in stq
    """

    @mockserver.json_handler('/logistic-dispatcher/employee/timer')
    def mock_employee_timer(request):
        assert request.json == {
            'point_from': [37.111, 55.111],
            'point_to': [37.222, 55.222],
            'employer': 'eda',
            'park_driver_profile_id': 'park_id_1_driver_id_1',
        }
        return {
            'estimation_time_of_arrival': '2021-01-26T13:55:00+00:00',
            'estimation_distance': 7.77,
            'is_approximate': False,
        }

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    # set p1 visited (and set field 'eta_calculation_awaited' = True)
    segment.set_point_coordinates('p1', [37.111, 55.111])
    segment.set_point_coordinates('p2', [37.222, 55.222])
    response = await dispatch_confirm_point(
        waybill_ref,
        visit_order=1,
        driver_id='driver_id_1',
        async_timer_supported=True,
    )
    assert response.status_code == 200

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert 'eta' not in next_point
    assert next_point['eta_calculation_awaited']

    await stq_runner.cargo_courier_timers_calculation.call(
        task_id='test',
        kwargs={
            'waybill_ref': waybill_ref,
            'next_point_id': next_point['claim_point_id'],
            'last_known_waybill_revision': 0,
        },
    )

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert next_point['eta'] == '2021-01-26T13:55:00+00:00'
    assert not next_point['eta_calculation_awaited']

    assert mock_employee_timer.times_called == 1


async def test_outdated_waybill_revisions(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq_runner,
        mockserver,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    await stq_runner.cargo_courier_timers_calculation.call(
        task_id='test',
        kwargs={
            'waybill_ref': waybill_ref,
            'next_point_id': next_point['claim_point_id'],
            'last_known_waybill_revision': 100,
        },
        expect_fail=True,
    )


async def test_closed_with_equal_revision_and_resolved(
        state_cancelled_resolved,
        get_point_execution_by_visit_order,
        stq_runner,
        mockserver,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    @mockserver.json_handler('/logistic-dispatcher/employee/timer')
    def mock_employee_timer(request):
        return {}

    await stq_runner.cargo_courier_timers_calculation.call(
        task_id='test',
        kwargs={
            'waybill_ref': waybill_ref,
            'next_point_id': next_point['claim_point_id'],
            'last_known_waybill_revision': 6,
        },
    )

    assert mock_employee_timer.times_called == 0


async def test_cancelled_waybill(
        state_cancelled_resolved,
        get_point_execution_by_visit_order,
        stq_runner,
        mockserver,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    @mockserver.json_handler('/logistic-dispatcher/employee/timer')
    def mock_employee_timer(request):
        return {}

    await stq_runner.cargo_courier_timers_calculation.call(
        task_id='test',
        kwargs={
            'waybill_ref': waybill_ref,
            'next_point_id': next_point['claim_point_id'],
            'last_known_waybill_revision': 0,
        },
    )

    assert mock_employee_timer.times_called == 0


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_next_point_eta_settings',
    consumers=['cargo-dispatch/taximeter-actions'],
    clauses=[],
    default_value={
        'enable': True,
        'allow_no_eta_on_error': True,
        'async_eta_calculation_enabled': True,
    },
)
@pytest.mark.now('2020-07-20T11:09:40+00:00')
@pytest.mark.parametrize(
    'calc_eta_from,return_eta_from',
    [
        (['logistic-dispatcher'], 'logistic-dispatcher'),
        (['logistic-dispatcher', 'eats-eta'], 'logistic-dispatcher'),
        (['logistic-dispatcher', 'eats-eta'], 'eats-eta'),
        (['cargo-eta'], 'cargo-eta'),
        (['eats-eta'], 'eats-eta'),
    ],
)
async def test_eta_flow(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq_runner,
        mockserver,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        calc_eta_from,
        return_eta_from,
        experiments3,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    @mockserver.json_handler('/logistic-dispatcher/employee/timer')
    def mock_employee_timer(request):
        assert request.json == {
            'point_from': [37.111, 55.111],
            'point_to': [37.222, 55.222],
            'employer': 'eda',
            'park_driver_profile_id': 'park_id_1_driver_id_1',
        }
        return {
            'estimation_time_of_arrival': '2021-01-26T13:55:00+00:00',
            'estimation_distance': 7.77,
            'is_approximate': False,
        }

    @mockserver.json_handler('/cargo-eta/v1/calculate-eta')
    def mock_cargo_eta_v1_calculate_eta(request):
        assert request.json == {
            'source': [37.111, 55.111],
            'destination': [37.222, 55.222],
            'transport_type': 'car',
            'zone_id': 'moscow',
            'cargo_ref_id': 'seg3',
        }
        return {'eta': {'time': 3600, 'distance': 6000}}

    @mockserver.json_handler('/eats-eta/v2/eta')
    def mock_eats_eta_v2_eta(request):
        assert request.json == {
            'sources': [
                {
                    'position': [37.111, 55.111],
                    'transport_type': 'car',
                    'zone_id': 'moscow',
                },
            ],
            'destination': {'position': [37.222, 55.222], 'type': 'dropoff'},
            'apply-correctors': True,
        }
        return {'etas': [{'time': 3600, 'distance': 6000}]}

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eta_flow',
        consumers=[
            'cargo-dispatch/cargo_dispatch_couriers_timers_calculation',
        ],
        clauses=[],
        default_value={
            'cargo': {
                'calc_eta_from': calc_eta_from,
                'return_eta_from': return_eta_from,
            },
        },
    )

    await taxi_cargo_dispatch.invalidate_caches()

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    # set p1 visited (and set field 'eta_calculation_awaited' = True)
    segment.set_point_coordinates('p1', [37.111, 55.111])
    segment.set_point_coordinates('p2', [37.222, 55.222])
    response = await dispatch_confirm_point(
        waybill_ref,
        visit_order=1,
        driver_id='driver_id_1',
        async_timer_supported=True,
    )
    assert response.status_code == 200

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert 'eta' not in next_point
    assert next_point['eta_calculation_awaited']

    await stq_runner.cargo_courier_timers_calculation.call(
        task_id='test',
        kwargs={
            'waybill_ref': waybill_ref,
            'next_point_id': next_point['claim_point_id'],
            'last_known_waybill_revision': 0,
        },
    )

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert not next_point['eta_calculation_awaited']

    assert mock_employee_timer.times_called == int(
        'logistic-dispatcher' in calc_eta_from,
    )
    assert mock_cargo_eta_v1_calculate_eta.times_called == int(
        'cargo-eta' in calc_eta_from,
    )
    assert mock_eats_eta_v2_eta.times_called == int(
        'eats-eta' in calc_eta_from,
    )

    if return_eta_from == 'logistic-dispatcher':
        assert next_point['eta'] == '2021-01-26T13:55:00+00:00'
    else:
        assert (
            next_point['eta'] == '2020-07-20T12:09:40+00:00'
        )  # value in pytest.mark.now plus 1 hour


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_next_point_eta_settings',
    consumers=['cargo-dispatch/taximeter-actions'],
    clauses=[],
    default_value={
        'enable': True,
        'allow_no_eta_on_error': True,
        'async_eta_calculation_enabled': True,
    },
)
@pytest.mark.now('2020-07-20T11:09:40+00:00')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eta_flow',
    consumers=['cargo-dispatch/cargo_dispatch_couriers_timers_calculation'],
    clauses=[],
    default_value={
        'cargo': {
            'calc_eta_from': ['cargo-eta'],
            'return_eta_from': 'cargo-eta',
        },
    },
)
@pytest.mark.parametrize(
    'start_from_performer_position, expected_eta',
    [
        (True, '2020-07-20T12:03:00+00:00'),
        (False, '2020-07-20T12:09:40+00:00'),
    ],
)
async def test_eta_flow_settings(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq_runner,
        mockserver,
        stq,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        experiments3,
        start_from_performer_position,
        expected_eta,
        segment_id='seg3',
        waybill_ref='waybill_fb_3',
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eta_flow_settings',
        consumers=[
            'cargo-dispatch/cargo_dispatch_couriers_timers_calculation',
        ],
        clauses=[],
        default_value={
            'calculate_eta_from_performer_position': (
                start_from_performer_position
            ),
        },
    )

    @mockserver.json_handler('/cargo-eta/v1/calculate-eta')
    def mock_cargo_eta_v1_calculate_eta(request):
        if request.json['source'] == [37.57839202, 55.7350642]:
            return {'eta': {'time': 3200, 'distance': 5000}}
        return {'eta': {'time': 3600, 'distance': 6000}}

    @mockserver.json_handler('/driver-trackstory/position')
    def mock_driver_trackstory_position(request):
        return {
            'position': {
                'direction': 0,
                'lat': 55.7350642,
                'lon': 37.57839202,
                'speed': 0,
                'timestamp': 1595243280,
            },
            'type': 'raw',
        }

    await taxi_cargo_dispatch.invalidate_caches()

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_point_coordinates('p1', [37.111, 55.111])
    segment.set_point_coordinates('p2', [37.222, 55.222])
    response = await dispatch_confirm_point(
        waybill_ref,
        visit_order=1,
        driver_id='driver_id_1',
        async_timer_supported=True,
    )
    assert response.status_code == 200

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert 'eta' not in next_point
    assert next_point['eta_calculation_awaited']

    assert stq.cargo_courier_timers_calculation.times_called
    stq_call = stq.cargo_courier_timers_calculation.next_call()
    assert (
        stq_call['kwargs']['start_from_performer_position']
        == start_from_performer_position
    )

    await stq_runner.cargo_courier_timers_calculation.call(
        task_id='test', kwargs=stq_call['kwargs'],
    )
    assert mock_cargo_eta_v1_calculate_eta.times_called
    assert mock_driver_trackstory_position.times_called == int(
        start_from_performer_position,
    )

    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    assert next_point['eta'] == expected_eta
    assert not next_point['eta_calculation_awaited']


@pytest.mark.parametrize(
    'claim_point_id, previous_claim_point_id', [(21, 12), (12, 11), (15, 14)],
)
async def test_batch_with_skipped_segment(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        dispatch_return_point,
        read_waybill_info,
        stq_runner,
        testpoint,
        claim_point_id,
        previous_claim_point_id,
        waybill_ref='waybill_smart_1',
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_A2_p6 (12) -> seg1_A1_p7 (11) ->
        seg2_C1_p3 (23)

    """
    # Skip segment
    response = await dispatch_return_point(waybill_ref, visit_order=1)
    assert response.status_code == 200

    @testpoint('previous point was found')
    def test_point(result):
        assert result['claim_point_id'] == previous_claim_point_id

    await stq_runner.cargo_courier_timers_calculation.call(
        task_id='test',
        kwargs={
            'waybill_ref': waybill_ref,
            'next_point_id': claim_point_id,
            'last_known_waybill_revision': 0,
        },
    )
    assert test_point.times_called == 1
