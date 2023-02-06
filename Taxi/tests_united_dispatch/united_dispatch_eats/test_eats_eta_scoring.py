from typing import Dict
from typing import Tuple

import pytest

from tests_united_dispatch.plugins import cargo_dispatch_manager


@pytest.mark.parametrize(
    'arrival_distance, delivery_distance, scoring_coefficients, '
    'expected_score',
    [
        [
            1000,
            1000,
            {
                'pickup_cost': 10,
                'dropoff_cost': 15,
                'long_arrival_cost': 20,
                'long_arrival_distance_km': 1.5,
                'arrival_kilometer_payment': 11,
                'delivery_kilometer_payment': 12,
                'additional_cost': 100,
            },
            148,  # 10 + 15 + 11 * 1 + 12 * 1 + 100
        ],
        [
            2000,
            3000,
            {
                'pickup_cost': 10,
                'dropoff_cost': 15,
                'long_arrival_cost': 20,
                'long_arrival_distance_km': 1.5,
                'arrival_kilometer_payment': 11,
                'delivery_kilometer_payment': 12,
                'additional_cost': 100,
            },
            203,  # 10 + 15 + 20 + 11 * 2 + 12 * 3 + 100
        ],
    ],
)
async def test_eats_eta_scoring(
        load_json,
        candidates,
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        scoring,
        testpoint,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
        mock_eats_eta,
        arrival_distance,
        delivery_distance,
        scoring_coefficients,
        expected_score,
):
    candidates_json = load_json('candidates.json')
    del candidates_json['candidates'][1]
    candidates(candidates_json)

    await exp_eats_dispatch_settings()
    await exp_eats_scoring_coefficients(**scoring_coefficients)
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )

    @testpoint('eats_planner::score_segment_candidate')
    def score_segment_candidate(data):
        assert data['score'] == expected_score
        assert data['is_precise']

    @testpoint('eats_planner::assign_segment')
    def eats_assign(_):
        pass

    mock_eats_eta(
        arrival_distance=arrival_distance, delivery_distance=delivery_distance,
    )

    segment1 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[37.0, 55.01],
        dropoff_coordinates=[37.01, 55.01],
    )

    await state_waybill_proposed()

    segment1_info = get_segment(segment1.id)

    waybill1 = get_waybill(segment1_info['waybill_ref'])

    assert not scoring.requests
    assert len(propositions_manager.propositions) == 1
    assert eats_assign.times_called == 1
    assert score_segment_candidate.times_called == 1
    assert waybill1['candidate']['info']['id'] == 'dbid1_uuid1'


async def test_eats_eta_batch_scoring(
        mocked_time,
        load_json,
        create_segment,
        state_taxi_order_performer_found,
        state_waybill_proposed,
        make_eats_custom_context,
        scoring,
        testpoint,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
        mockserver,
):
    testcase = load_json('eats_eta_batch_estimation.json')
    mocked_time.set(testcase['now'])
    await exp_eats_dispatch_settings(linear_sideways_allowance=0)
    await exp_eats_scoring_coefficients(
        pickup_cost=35,
        dropoff_cost=35,
        long_arrival_cost=20,
        long_arrival_distance_km=2,
        arrival_kilometer_payment=5,
        delivery_kilometer_payment=25,
    )
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=True,
    )

    score: Dict[Tuple[str, str], float] = {}

    @testpoint('eats_planner::score_segment_candidate')
    def _score_segment_candidate(data):
        key = data['segment_id'], data['candidate_id']
        if key not in score or score[key] > data['score']:
            score[key] = data['score']

    @testpoint('eats_planner::assign_segment')
    def assign_single_segment(_):
        pass

    @testpoint('eats_planner::assign_live_batch')
    def assign_live_batch(_):
        pass

    @testpoint('eats_planner::courier_dropoff_expected_timing')
    def _get_estimated_batch_dropoff_time(data):
        assert data['estimated_visit_time_ms'] == '2022-04-13T09:24:00+00:00'

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100000},
                    'candidates': [{'id': 'dbid1_uuid1', 'score': 99000}],
                },
            ],
        },
    )

    segment1 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        **testcase['first_segment'],
    )

    await state_taxi_order_performer_found()

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100000},
                    'candidates': [{'id': 'dbid1_uuid1', 'score': 101000}],
                },
            ],
        },
    )

    segment2 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        **testcase['second_segment'],
    )

    @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
    def _mock_eats_eta(request):
        estimations = []
        for estimation_request in request.json['routes']:
            route_id = estimation_request.pop('id')
            if (
                    estimation_request
                    == testcase['prev_waybill_estimation_request']
            ):
                estimations.append(
                    dict(
                        testcase['prev_waybill_estimation'], route_id=route_id,
                    ),
                )
            elif estimation_request == testcase['batch_estimation_request']:
                estimations.append(
                    dict(testcase['batch_estimation'], route_id=route_id),
                )
        return {'routes_estimations': estimations}

    await state_waybill_proposed()

    expected_score = {
        (segment1.id, 'dbid1_uuid1'): 99000.0,
        (segment2.id, 'dbid1_uuid1'): 72.5,
    }
    assert score == expected_score

    assert assign_single_segment.times_called == 1
    assert assign_live_batch.times_called == 1


async def test_eats_eta_scoring_fallback(
        mockserver,
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        scoring,
        testpoint,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
):
    await exp_eats_dispatch_settings()
    await exp_eats_scoring_coefficients(
        pickup_cost=10,
        dropoff_cost=15,
        long_arrival_cost=20,
        long_arrival_distance_km=1.5,
        arrival_kilometer_payment=11,
        delivery_kilometer_payment=12,
        additional_cost=0,
    )
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )

    @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
    def _mock_eats_eta(_):
        return mockserver.make_response(status=499)

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 3},
                        {'id': 'dbid1_uuid2', 'score': 15},
                    ],
                },
            ],
        },
    )

    segment1 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[37.0, 55.01],
        dropoff_coordinates=[37.01, 55.01],
    )
    segment2 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[37.1, 55.09],
        dropoff_coordinates=[37.09, 55.09],
    )

    expected_score = {
        (segment1.id, 'dbid1_uuid1'): 44.865,
        (segment1.id, 'dbid1_uuid2'): 183.126,
        (segment2.id, 'dbid1_uuid1'): 183.125,
        (segment2.id, 'dbid1_uuid2'): 44.853,
    }

    @testpoint('eats_planner::score_segment_candidate')
    def score_segment_candidate(data):
        assert (
            expected_score[data['segment_id'], data['candidate_id']]
            == data['score']
        ), data
        assert not data['is_precise']

    @testpoint('eats_planner::assign_segment')
    def eats_assign(_):
        pass

    await state_waybill_proposed()

    segment1_info = get_segment(segment1.id)
    segment2_info = get_segment(segment2.id)

    waybill1 = get_waybill(segment1_info['waybill_ref'])
    waybill2 = get_waybill(segment2_info['waybill_ref'])

    assert len(propositions_manager.propositions) == 2
    assert eats_assign.times_called == 2
    assert score_segment_candidate.times_called == 4
    assert waybill1['candidate']['info']['id'] == 'dbid1_uuid1'
    assert waybill2['candidate']['info']['id'] == 'dbid1_uuid2'


def get_waybill_segment_ids(waybill):
    return [
        segment['segment']['segment']['id'] for segment in waybill['segments']
    ]


def get_segment_points_coordinates(segment):
    locations_coordinates = {
        location['id']: location['coordinates']
        for location in segment['locations']
    }
    return {
        point['point_id']: locations_coordinates[point['location_id']]
        for point in segment['points']
    }


def get_waybill_path(waybill):
    points_coordinates = {}
    for segment in waybill['segments']:
        points_coordinates.update(
            get_segment_points_coordinates(segment['segment']['segment']),
        )
    return [points_coordinates[point['point_id']] for point in waybill['path']]


@pytest.mark.parametrize(
    'first_candidate_position, second_candidate_position, '
    'first_segment_pickup_position, first_segment_dropoff_position, '
    'new_segment_pickup_position, new_segment_dropoff_position, '
    'first_segment_candidate, new_segment_candidate, '
    'new_waybill_segments_count',
    [
        pytest.param(
            [0, 0],
            [0.04, 0],
            [0, 0.04],
            [0.04, 0.04],
            [0, 0.05],
            [0, 0.06],
            'dbid1_uuid1',
            'dbid1_uuid1',
            2,
            id='batch',
        ),
        pytest.param(
            [0, 0],
            [0.04, 0],
            [0, 0.04],
            [0.04, 0.04],
            [0.04, 0.09],
            [0.04, 0.14],
            'dbid1_uuid1',
            'dbid1_uuid1',
            1,
            id='chain',
        ),
        pytest.param(
            [0, 0],
            [0.04, 0],
            [0, 0.04],
            [0.04, 0.04],
            [0.04, -0.01],
            [0.04, -0.02],
            'dbid1_uuid1',
            'dbid1_uuid2',
            1,
            id='single assignment',
        ),
    ],
)
async def test_eats_eta_complex_scoring(
        mockserver,
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        scoring,
        load_json,
        candidates,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
        first_candidate_position,
        second_candidate_position,
        first_segment_pickup_position,
        first_segment_dropoff_position,
        new_segment_pickup_position,
        new_segment_dropoff_position,
        first_segment_candidate,
        new_segment_candidate,
        new_waybill_segments_count,
):
    candidates_json = load_json('candidates.json')
    candidates_json['candidates'][0]['position'] = first_candidate_position
    candidates_json['candidates'][1]['position'] = second_candidate_position

    candidates(candidates_json)

    await exp_eats_dispatch_settings(
        linear_sideways_allowance=1000000,
        linear_backwards_allowance=1000000,
        route_sideways_allowance=1000000,
        route_backwards_allowance=1000000,
    )
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )

    @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
    def _mock_eats_eta(request):
        return mockserver.make_response(status=499)

    await exp_eats_scoring_coefficients(
        pickup_cost=0,
        dropoff_cost=0,
        long_arrival_cost=0,
        long_arrival_distance_km=0,
        arrival_kilometer_payment=1000,
        delivery_kilometer_payment=1000,
        additional_cost=0,
    )

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 3},
                        {'id': 'dbid1_uuid2', 'score': 15},
                    ],
                },
            ],
        },
    )

    segments = [
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=first_segment_pickup_position,
            dropoff_coordinates=first_segment_dropoff_position,
        ),
    ]

    await state_taxi_order_performer_found()

    segment_info = get_segment(segments[0].id)

    waybill = get_waybill(segment_info['waybill_ref'])

    assert waybill['candidate']['info']['id'] == first_segment_candidate
    assert len(waybill['waybill']['segments']) == 1

    for candidate in candidates_json['candidates']:
        if candidate['id'] == first_segment_candidate:
            candidate['chain_info'] = {
                'destination': first_segment_dropoff_position,
                'left_dist': 0,
                'left_time': 0,
                'order_id': '0',
            }

    candidates(candidates_json)

    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=new_segment_pickup_position,
            dropoff_coordinates=new_segment_dropoff_position,
        ),
    )

    await state_waybill_proposed()

    segments_info = [get_segment(segment.id) for segment in segments]

    waybills = [
        get_waybill(segment_info['waybill_ref'])
        for segment_info in segments_info
    ]

    assert waybills[0]['candidate']['info']['id'] == first_segment_candidate
    assert len(waybills[0]['waybill']['segments']) == 1
    assert waybills[1]['candidate']['info']['id'] == new_segment_candidate
    assert (
        len(waybills[1]['waybill']['segments']) == new_waybill_segments_count
    ), get_waybill_path(waybills[1]['waybill'])


@pytest.mark.parametrize(
    'first_candidate_position, second_candidate_position, '
    'first_segment_pickup_position, first_segment_dropoff_position, '
    'new_segment_pickup_position, new_segment_dropoff_position',
    [
        [
            # при совместном назначении батчей и отдельных сегментов
            # получили бы батч
            [0, 0],
            [0.04, 0],
            [0, 0.04],
            [0.04, 0.04],
            [0, 0.05],
            [0, 0.06],
        ],
        [
            # при совместном назначении получили бы цепочку
            [0, 0],
            [0.04, 0],
            [0, 0.04],
            [0.04, 0.04],
            [0.04, 0.09],
            [0.04, 0.14],
        ],
        [
            # при совместном назначении получили бы одиночное назначение
            [0, 0],
            [0.04, 0],
            [0, 0.04],
            [0.04, 0.04],
            [0.04, -0.01],
            [0.04, -0.02],
        ],
    ],
)
async def test_eats_eta_separate_solving(
        mockserver,
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        scoring,
        load_json,
        candidates,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
        first_candidate_position,
        second_candidate_position,
        first_segment_pickup_position,
        first_segment_dropoff_position,
        new_segment_pickup_position,
        new_segment_dropoff_position,
):
    candidates_json = load_json('candidates.json')
    candidates_json['candidates'][0]['position'] = first_candidate_position
    candidates_json['candidates'][1]['position'] = second_candidate_position

    candidates(candidates_json)

    await exp_eats_dispatch_settings(
        separate_batches_solving=True,
        linear_sideways_allowance=1000000,
        linear_backwards_allowance=1000000,
        route_sideways_allowance=1000000,
        route_backwards_allowance=1000000,
    )
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )

    @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
    def _mock_eats_eta(request):
        return mockserver.make_response(status=499)

    await exp_eats_scoring_coefficients(
        pickup_cost=0,
        dropoff_cost=0,
        long_arrival_cost=0,
        long_arrival_distance_km=0,
        arrival_kilometer_payment=1000,
        delivery_kilometer_payment=1000,
        additional_cost=0,
    )

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 3},
                        {'id': 'dbid1_uuid2', 'score': 15},
                    ],
                },
            ],
        },
    )

    segments = [
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=first_segment_pickup_position,
            dropoff_coordinates=first_segment_dropoff_position,
        ),
    ]

    await state_taxi_order_performer_found()

    segment_info = get_segment(segments[0].id)

    waybill = get_waybill(segment_info['waybill_ref'])

    assert waybill['candidate']['info']['id'] == 'dbid1_uuid1'
    assert len(waybill['waybill']['segments']) == 1

    candidates_json['candidates'][0]['chain_info'] = {
        'destination': first_segment_dropoff_position,
        'left_dist': 0,
        'left_time': 0,
        'order_id': '0',
    }

    candidates(candidates_json)

    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=new_segment_pickup_position,
            dropoff_coordinates=new_segment_dropoff_position,
        ),
    )

    await state_waybill_proposed()

    segments_info = [get_segment(segment.id) for segment in segments]

    waybills = [
        get_waybill(segment_info['waybill_ref'])
        for segment_info in segments_info
    ]

    assert waybills[0]['candidate']['info']['id'] == 'dbid1_uuid1'
    assert len(waybills[0]['waybill']['segments']) == 1
    assert waybills[1]['candidate']['info']['id'] == 'dbid1_uuid1'
    assert len(waybills[1]['waybill']['segments']) == 2, get_waybill_path(
        waybills[1]['waybill'],
    )


async def test_eats_eta_scoring_invalid_candidate(
        load_json,
        candidates,
        mockserver,
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        scoring,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
):
    await exp_eats_dispatch_settings(manually_filter_candidates=True)
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )
    await exp_eats_scoring_coefficients(
        pickup_cost=10,
        dropoff_cost=15,
        long_arrival_cost=20,
        long_arrival_distance_km=1.5,
        arrival_kilometer_payment=11,
        delivery_kilometer_payment=12,
        additional_cost=0,
    )

    candidates_json = load_json('candidates.json')
    for candidate in candidates_json['candidates']:
        candidate['classes'].remove('eda')

    candidates(candidates_json)

    @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
    def mock_eats_eta(_):
        return mockserver.make_response(status=499)

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
            ],
        },
    )

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[37.0, 55.01],
        dropoff_coordinates=[37.01, 55.01],
    )

    await state_waybill_proposed()

    assert mock_eats_eta.times_called == 0


async def test_eats_eta_scoring_candidate_late_for_dropoff(
        mocked_time,
        load_json,
        create_segment,
        state_taxi_order_performer_found,
        state_waybill_proposed,
        make_eats_custom_context,
        scoring,
        testpoint,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
        mockserver,
):
    testcase = load_json('eats_eta_batch_estimation.json')
    mocked_time.set(testcase['now'])
    await exp_eats_dispatch_settings(linear_sideways_allowance=0)
    await exp_eats_scoring_coefficients()
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )

    @testpoint('eats_planner::assign_segment')
    def assign_single_segment(_):
        pass

    @testpoint('eats_planner::assign_live_batch')
    def assign_live_batch(_):
        pass

    @testpoint('eats_planner::courier_dropoff_timing_error')
    def timing_error(_):
        pass

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100000},
                    'candidates': [{'id': 'dbid1_uuid1', 'score': 99000}],
                },
            ],
        },
    )

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        **testcase['first_segment'],
    )

    await state_taxi_order_performer_found()

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        dropoff_time_intervals=[
            {
                'type': 'strict_match',
                'from': '2020-01-01T00:00:00+00:00',
                'to': '2020-01-02T00:00:00+00:00',
            },
        ],
        **testcase['second_segment'],
    )

    await state_waybill_proposed()
    assert assign_single_segment.times_called == 2
    assert assign_live_batch.times_called == 0
    assert timing_error.times_called == 1
