import pytest

from testsuite.utils import matching


_REQUEST_TIMESTAMP = '2021-09-23T15:30:47.185337+00:00'


async def test_admin_handler(
        segment_diagnostics,
        exp_planner_shard,
        state_initialized,
        create_segment,
        mock_dispatch_admin_segment_info,
        exp_delivery_configs,
        exp_segment_executors_selector,
        mock_units_diagnostics_responses,
):
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'testsuite-candidates', 'is_active': False},
        ],
    )
    await exp_delivery_configs()
    await exp_planner_shard()
    await state_initialized()

    # creates default 'delivery' segment
    seg = create_segment()

    response = await segment_diagnostics(segment_id=seg.id)

    assert response['pipeline'] == [
        {'planner_id': 'crutches', 'planner_shard': 'default'},
        {'planner_id': 'testsuite-candidates', 'planner_shard': 'default'},
    ]

    assert response['planners'] == [
        {
            'planner_id': 'crutches',
            'recorded_requests': [],
            'result': {'kind': 'add_proposition'},
        },
        {
            'planner_id': 'testsuite-candidates',
            'recorded_requests': [],
            'result': {'kind': 'add_proposition'},
        },
    ]

    assert response['candidate'] == {
        'performer_id': matching.any_string,
        'planners_satisfy': [
            {'planner_id': 'crutches', 'response': {'foo': 'bar'}},
        ],
    }


@pytest.mark.now(_REQUEST_TIMESTAMP)
async def test_candidates_diagnostics(
        planner_diagnostics,
        state_initialized,
        create_candidates_segment,
        mock_dispatch_admin_segment_info,
        exp_delivery_configs,
        exp_segment_executors_selector,
        exp_planner_shard,
        performer_for_order,
):
    """
        Check basic launch diagnostics context.
    """
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'testsuite-candidates', 'is_active': True},
            {'planner_type': 'fallback', 'is_active': False},
        ],
    )
    await exp_delivery_configs()
    await exp_planner_shard()
    await state_initialized()

    # creates default 'candidates' segment
    seg = create_candidates_segment('greedy')

    response_fallback = await planner_diagnostics(
        segment_id=seg.id, planner_type='fallback',
    )
    response_testsuite = await planner_diagnostics(
        segment_id=seg.id, planner_type='testsuite-candidates',
    )
    planners_fallback = response_fallback['planner']
    planners_testsuite = response_testsuite['planner']

    assert planners_testsuite == {
        'planner_id': 'testsuite-candidates',
        'recorded_requests': [
            {
                'destination': 'candidates/order-search',
                'timestamp': _REQUEST_TIMESTAMP,
                'request_body': {
                    'allowed_classes': matching.IsInstance(list),
                    'order': {
                        'cargo_ref_ids': [seg.id],
                        'nearest_zone': 'moscow',
                        'request': {
                            'check_new_logistic_contract': False,
                            'corp': {'client_id': matching.any_string},
                            'destinations': [
                                {'geopoint': [33.5, 55.5]},
                                {'geopoint': [33.5, 55.5]},
                            ],
                            'source': {'geopoint': [33.5, 55.5]},
                        },
                        'virtual_tariffs': [
                            {
                                'class': 'cargo',
                                'special_requirements': [
                                    {'id': 'cargo_pickup_points'},
                                ],
                            },
                        ],
                    },
                    'order_id': f'ud/{seg.id}',
                    'point': [33.5, 55.5],
                    'requirements': {'some_requirement': True},
                    'timeout': 200,
                    'zone_id': 'moscow',
                },
                'response_body': {'candidates': matching.IsInstance(list)},
            },
        ],
        'result': {'kind': 'add_proposition'},
    }

    assert planners_fallback == {
        'planner_id': 'fallback',
        'recorded_requests': [],
        'result': {'kind': 'add_proposition'},
    }


async def test_satisfy(
        planner_diagnostics,
        state_initialized,
        create_candidates_segment,
        mock_dispatch_admin_segment_info,
        exp_delivery_configs,
        exp_segment_executors_selector,
        exp_planner_shard,
        performer_for_order,
):
    """
        Check basic launch diagnostics context.
    """
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'testsuite-candidates', 'is_active': True},
        ],
    )
    await exp_delivery_configs()
    await exp_planner_shard()
    await state_initialized()

    # creates default 'candidates' segment
    seg = create_candidates_segment('greedy')

    response = await planner_diagnostics(
        segment_id=seg.id,
        planner_type='testsuite-candidates',
        performer_id='dbid1_uuid1',
    )

    assert response['candidate'] == {
        'candidate_id': 'dbid1_uuid1',
        'planner_satisfy': {
            'planner_id': 'testsuite-candidates',
            'response': {
                'classes': ['courier'],
                'dbid': 'dbid1',
                'id': 'dbid1_uuid1',
                'position': [37.0, 55.0],
                'route_info': {
                    'approximate': False,
                    'distance': 120,
                    'time': 10,
                },
                'status': {'orders': [], 'status': 'online'},
                'transport': {'type': 'pedestrian'},
                'uuid': 'uuid1',
            },
        },
    }


async def test_unknown_segment(
        segment_diagnostics,
        state_initialized,
        mock_dispatch_admin_segment_info,
        exp_segment_executors_selector,
        exp_planner_shard,
):
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )
    await exp_planner_shard()
    await state_initialized()

    await segment_diagnostics(
        segment_id='unknown_segment', expected_status=404,
    )
