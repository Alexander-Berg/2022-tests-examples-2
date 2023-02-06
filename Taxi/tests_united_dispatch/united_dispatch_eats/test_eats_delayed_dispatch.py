import pytest


async def test_eats_delayed_close_deadline(
        taxi_united_dispatch_eats,
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        testpoint,
        scoring,
        get_segment,
        get_waybill,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_delayed_dispatch',
        consumers=['united-dispatch/eats-delayed-kwargs'],
        clauses=[],
        default_value={
            'enabled': True,
            'time_before_deadline': 20 * 60 * 1000,
            'wait_time_in_restaraunt': 1000,
            'current_order_left_time': 20 * 60 * 1000,
            'live_batching': {
                'enabled': False,
                'time_before_deadline': 5 * 60 * 1000,
                'time_to_point_a': 5 * 60 * 1000,
            },
        },
    )
    exp3_recorder = experiments3.record_match_tries(
        'united_dispatch_eats_delayed_dispatch',
    )

    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 10},
                        {'id': 'dbid1_uuid2', 'score': 1},
                    ],
                },
            ],
        },
    )

    @testpoint('eats_planner::assign_segment')
    def eats_assign(data):
        pass

    @testpoint('eats_planner::close_deadline')
    def close_deadline(data):
        pass

    segment = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )

    await state_waybill_proposed()

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    segment_id_from_kwarg = match_tries[0].kwargs['segment_id']

    assert segment_id_from_kwarg == segment.id

    assert close_deadline.times_called == 1
    assert eats_assign.times_called == 1

    segment_info = get_segment(segment.id)
    waybill = get_waybill(segment_info['waybill_ref'])
    assert waybill['candidate']['info']['id'] == 'dbid1_uuid2'


@pytest.mark.now('2021-09-23T15:30:47.185337+00:00')
async def test_eats_delayed_not_close_deadline(
        taxi_united_dispatch_eats,
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        testpoint,
        scoring,
        get_segment,
        get_waybill,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_delayed_dispatch',
        consumers=['united-dispatch/eats-delayed-kwargs'],
        clauses=[],
        default_value={
            'enabled': True,
            'time_before_deadline': 5 * 60 * 1000,
            'wait_time_in_restaraunt': 20 * 60 * 1000,
            'current_order_left_time': 20 * 60 * 1000,
            'live_batching': {
                'enabled': False,
                'time_before_deadline': 5 * 60 * 1000,
                'time_to_point_a': 5 * 60 * 1000,
            },
        },
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 10},
                        {'id': 'dbid1_uuid2', 'score': 1},
                    ],
                },
            ],
        },
    )

    @testpoint('eats_planner::assign_segment')
    def eats_assign(data):
        pass

    @testpoint('eats_planner::close_deadline')
    def close_deadline(data):
        pass

    segment = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )

    await state_waybill_proposed()

    assert not close_deadline.times_called
    assert eats_assign.times_called == 1

    segment_info = get_segment(segment.id)
    waybill = get_waybill(segment_info['waybill_ref'])
    assert waybill['candidate']['info']['id'] == 'dbid1_uuid2'


@pytest.mark.now('2021-09-23T15:30:47.185337+00:00')
async def test_eats_delayed_large_left_time(
        taxi_united_dispatch_eats,
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        testpoint,
        scoring,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_delayed_dispatch',
        consumers=['united-dispatch/eats-delayed-kwargs'],
        clauses=[],
        default_value={
            'enabled': True,
            'time_before_deadline': 5 * 60 * 1000,
            'wait_time_in_restaraunt': 20 * 60 * 1000,
            'current_order_left_time': 1000,
            'live_batching': {
                'enabled': False,
                'time_before_deadline': 5 * 60 * 1000,
                'time_to_point_a': 5 * 60 * 1000,
            },
        },
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 10},
                        {'id': 'dbid1_uuid2', 'score': 3},
                        {'id': 'dbid1_uuid3', 'score': 2},
                        {'id': 'dbid1_uuid4', 'score': 1},
                    ],
                },
            ],
        },
    )

    @testpoint('eats_planner::left_time_skip')
    def left_time_skip(data):
        pass

    @testpoint('eats_planner::close_deadline')
    def close_deadline(data):
        pass

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        due='2021-09-23T15:40:47.185337+00:00',
    )

    await state_waybill_proposed()

    assert not close_deadline.times_called
    assert left_time_skip.times_called > 0


@pytest.mark.now('2021-09-23T15:30:47.185337+00:00')
async def test_eats_delayed_large_wait_time(
        taxi_united_dispatch_eats,
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        testpoint,
        scoring,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_delayed_dispatch',
        consumers=['united-dispatch/eats-delayed-kwargs'],
        clauses=[],
        default_value={
            'enabled': True,
            'time_before_deadline': 5 * 60 * 1000,
            'wait_time_in_restaraunt': 1000,
            'current_order_left_time': 20 * 60 * 1000,
            'live_batching': {
                'enabled': False,
                'time_before_deadline': 5 * 60 * 1000,
                'time_to_point_a': 5 * 60 * 1000,
            },
        },
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 10},
                        {'id': 'dbid1_uuid2', 'score': 2},
                        {'id': 'dbid1_uuid3', 'score': 1},
                    ],
                },
            ],
        },
    )

    @testpoint('eats_planner::wait_time_skip')
    def wait_time_skip(data):
        pass

    @testpoint('eats_planner::close_deadline')
    def close_deadline(data):
        pass

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        due='2021-09-23T15:40:47.185337+00:00',
    )

    await state_waybill_proposed()

    assert not close_deadline.times_called
    assert wait_time_skip.times_called > 0


@pytest.mark.parametrize(
    'live_batching,'
    + 'second_segment_deadline,'
    + 'close_deadline_times_called,'
    + 'batch_time_to_point_a_skip_times_called',
    [
        pytest.param(
            {'enabled': True, 'time_to_point_a': 500 * 60 * 60 * 1000},
            '2021-09-23T16:40:47.185337+00:00',
            1,  # first segment
            0,
            id='batching',
        ),
        pytest.param(
            {'enabled': True, 'time_to_point_a': 1},
            '2021-09-23T16:40:47.185337+00:00',
            1,  # first segment
            1,
            id='delay_batching',
        ),
        pytest.param(
            {'enabled': True, 'time_to_point_a': 5 * 60 * 1000},
            '2021-09-23T15:40:47.185337+00:00',
            2,  # first segment + batch
            0,
            id='close_deadline',
        ),
    ],
)
@pytest.mark.now('2021-09-23T15:30:47.185337+00:00')
async def test_eats_delayed_batching(
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        scoring,
        testpoint,
        exp_eats_dispatch_settings,
        make_eats_custom_context,
        experiments3,
        taxi_united_dispatch_eats,
        live_batching,
        second_segment_deadline,
        close_deadline_times_called,
        batch_time_to_point_a_skip_times_called,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_delayed_dispatch',
        consumers=['united-dispatch/eats-delayed-kwargs'],
        clauses=[],
        default_value={
            'enabled': True,
            'time_before_deadline': 20 * 60 * 1000,
            'wait_time_in_restaraunt': 1000,
            'current_order_left_time': 20 * 60 * 1000,
            'live_batching': live_batching,
        },
    )

    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    await exp_eats_dispatch_settings(enable_segments_filtration=True)

    @testpoint('eats_planner::close_deadline')
    def close_deadline(data):
        pass

    @testpoint('eats_planner::batch_time_to_point_a_skip')
    def batch_time_to_point_a_skip(data):
        pass

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [{'id': 'dbid1_uuid1', 'score': 8}],
                },
            ],
        },
    )

    custom_context = make_eats_custom_context()
    custom_context['delivery_flags'] = None

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=custom_context,
        pickup_coordinates=[0.01, 0],
        dropoff_coordinates=[0.01, 0.08],
        waybill_building_deadline='2021-09-23T15:40:47.185337+00:00',
    )

    await state_taxi_order_performer_found()

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=custom_context,
        pickup_coordinates=[0.02, 0],
        dropoff_coordinates=[0.02, 0.08],
        waybill_building_deadline=second_segment_deadline,
    )

    await state_waybill_proposed()

    assert close_deadline.times_called == close_deadline_times_called
    assert (
        batch_time_to_point_a_skip.times_called
        == batch_time_to_point_a_skip_times_called
    )


def _remove_infrastructure_fields(waybills):
    for waybill in waybills:
        waybill.pop('revision')
        waybill.pop('update_proposition_id')
        waybill.pop('rebuilt_at')
        waybill.pop('updated_ts')
        waybill.pop('created_ts')
