# pylint: disable=C0302
from typing import Dict
from typing import Tuple

import pytest

from tests_united_dispatch.plugins import cargo_dispatch_manager


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
    'waybill_segment_kwargs, waybill_segment_delivery_flags, '
    'waybill_segment_place_id, new_segment_kwargs, '
    'new_segment_delivery_flags, new_segment_place_id, settings, '
    'pre_filtered, batch_proposed, batch_path',
    [
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.43, 55.73],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.43, 55.71],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {},
            2,
            {
                'route_backwards_allowance': 10000,
                'route_sideways_allowance': 10000,
            },
            False,
            True,
            [
                [37.4, 55.7],
                [37.43, 55.71],
                [37.4, 55.72],
                [37.43, 55.73],
                [37.4, 55.7],
                [37.43, 55.71],
            ],
            id='negative score ok',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.43, 55.73],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.43, 55.71],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {},
            2,
            {
                'route_backwards_allowance': 0,
                'route_sideways_allowance': 10000,
            },
            False,
            False,
            None,
            id='no negative score',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.43, 55.73],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.43, 55.71],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {},
            2,
            {
                'linear_backwards_allowance': 0,
                'linear_sideways_allowance': 10000,
            },
            True,
            False,
            None,
            id='prefiltered negative score',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.43, 55.73],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.4, 55.71],
                'dropoff_coordinates': [37.43, 55.72],
            },
            {},
            2,
            {
                'route_backwards_allowance': 0,
                'route_sideways_allowance': 10000,
            },
            False,
            True,
            [
                [37.4, 55.7],
                [37.4, 55.71],
                [37.43, 55.72],
                [37.43, 55.73],
                [37.4, 55.7],
                [37.4, 55.71],
            ],
            id='positive score',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.43, 55.73],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.4, 55.71],
                'dropoff_coordinates': [37.43, 55.72],
            },
            {},
            2,
            {'route_backwards_allowance': 0, 'route_sideways_allowance': 0},
            False,
            False,
            None,
            id='zero sideways allowance',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.43, 55.73],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.4, 55.71],
                'dropoff_coordinates': [37.43, 55.72],
            },
            {},
            2,
            {'linear_backwards_allowance': 0, 'linear_sideways_allowance': 0},
            True,
            False,
            None,
            id='prefiltered zero sideways allowance',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.4, 55.71],
                'dropoff_coordinates': [37.4, 55.73],
            },
            {},
            2,
            {'route_backwards_allowance': 0, 'route_sideways_allowance': 0},
            False,
            True,
            [
                [37.4, 55.7],
                [37.4, 55.71],
                [37.4, 55.72],
                [37.4, 55.73],
                [37.4, 55.7],
                [37.4, 55.71],
            ],
            id='zero sideways batch',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.4, 55.71],
                'dropoff_coordinates': [37.4, 55.73],
            },
            {},
            2,
            {'allow_distinct_places': False},
            True,
            False,
            None,
            id='distinct places not allowed',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.4, 55.73],
            },
            {},
            1,
            {'allow_distinct_places': False},
            False,
            True,
            [
                [37.4, 55.7],
                [37.4, 55.7],
                [37.4, 55.72],
                [37.4, 55.73],
                [37.4, 55.7],
                [37.4, 55.7],
            ],
            id='same place',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {'is_forbidden_to_be_in_batch': True},
            1,
            {
                'pickup_coordinates': [37.4, 55.71],
                'dropoff_coordinates': [37.4, 55.73],
            },
            {},
            2,
            {},
            True,
            False,
            None,
            id='forbidden to be in batch',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {},
            1,
            {
                'pickup_coordinates': [37.4, 55.71],
                'dropoff_coordinates': [37.4, 55.73],
            },
            {'is_forbidden_to_be_second_in_batch': True},
            2,
            {},
            False,
            True,
            [
                [37.4, 55.7],
                [37.4, 55.71],
                [37.4, 55.73],
                [37.4, 55.72],
                [37.4, 55.7],
                [37.4, 55.71],
            ],
            id='forbidden to be second in batch',
        ),
        pytest.param(
            {
                'pickup_coordinates': [37.4, 55.7],
                'dropoff_coordinates': [37.4, 55.73],
            },
            {'is_forbidden_to_be_second_in_batch': True},
            1,
            {
                'pickup_coordinates': [37.4, 55.71],
                'dropoff_coordinates': [37.4, 55.72],
            },
            {},
            2,
            {},
            False,
            True,
            [
                [37.4, 55.7],
                [37.4, 55.71],
                [37.4, 55.73],
                [37.4, 55.72],
                [37.4, 55.7],
                [37.4, 55.71],
            ],
            id='waybill segment forbidden to be second in batch',
        ),
    ],
)
async def test_eats_waybill_live_batch_filters(
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        scoring,
        candidates,
        testpoint,
        exp_eats_dispatch_settings,
        exp_eats_segment_scoring_method,
        exp_eats_scoring_coefficients,
        waybill_segment_kwargs,
        waybill_segment_delivery_flags,
        waybill_segment_place_id,
        new_segment_kwargs,
        new_segment_delivery_flags,
        new_segment_place_id,
        settings,
        pre_filtered,
        batch_proposed,
        batch_path,
):
    await exp_eats_dispatch_settings(**settings)

    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )
    await exp_eats_scoring_coefficients()

    @testpoint('eats_planner::assign_segment')
    def assign_single_segment(_):
        pass

    @testpoint('eats_planner::assign_live_batch')
    def assign_live_batch(_):
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

    segment1 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(
            delivery_flags=waybill_segment_delivery_flags,
            place_id=waybill_segment_place_id,
        ),
        **waybill_segment_kwargs,
    )
    await state_taxi_order_performer_found()

    segment2 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(
            delivery_flags=new_segment_delivery_flags,
            place_id=new_segment_place_id,
        ),
        **new_segment_kwargs,
    )
    await state_waybill_proposed()

    segment1_info = get_segment(segment1.id)
    segment2_info = get_segment(segment2.id)

    waybill1 = get_waybill(segment1_info['waybill_ref'])['waybill']
    waybill2 = get_waybill(segment2_info['waybill_ref'])['waybill']

    assert get_waybill_segment_ids(waybill1) == [segment1.id]
    if pre_filtered:
        assert candidates.order_satisfy.times_called == 0
    else:
        assert candidates.order_satisfy.times_called == 1
    if batch_proposed:
        assert assign_single_segment.times_called == 1
        assert assign_live_batch.times_called == 1
        assert len(propositions_manager.propositions) == 1
        assert len(propositions_manager.live_propositions) == 1
        assert get_waybill_segment_ids(waybill2) == [segment1.id, segment2.id]
        assert get_waybill_path(waybill2) == batch_path
    else:
        assert assign_single_segment.times_called == 2
        assert assign_live_batch.times_called == 0
        assert len(propositions_manager.propositions) == 2
        assert not propositions_manager.live_propositions
        assert get_waybill_segment_ids(waybill2) == [segment2.id]


async def test_eats_waybill_live_batch_invalid_candidate(
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        scoring,
        candidates,
        load_json,
        testpoint,
        exp_eats_dispatch_settings,
):
    candidates_json = load_json('candidates.json')
    for candidate in candidates_json['candidates']:
        if candidate['id'] == 'dbid1_uuid1':
            candidate['classes'].remove('eda')

    candidates(candidates_json)

    await exp_eats_dispatch_settings(manually_filter_candidates=False)

    @testpoint('eats_planner::assign_segment')
    def assign_single_segment(_):
        pass

    @testpoint('eats_planner::assign_live_batch')
    def assign_live_batch(_):
        pass

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 10},
                    ],
                },
            ],
        },
    )

    segment1 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )
    await state_taxi_order_performer_found()

    await exp_eats_dispatch_settings(manually_filter_candidates=True)

    segment2 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )
    await state_waybill_proposed()

    segment1_info = get_segment(segment1.id)
    segment2_info = get_segment(segment2.id)

    waybill1 = get_waybill(segment1_info['waybill_ref'])['waybill']
    waybill2 = get_waybill(segment2_info['waybill_ref'])['waybill']

    assert get_waybill_segment_ids(waybill1) == [segment1.id]
    assert candidates.order_satisfy.times_called == 0
    assert assign_single_segment.times_called == 2
    assert assign_live_batch.times_called == 0
    assert len(propositions_manager.propositions) == 2
    assert not propositions_manager.live_propositions
    assert get_waybill_segment_ids(waybill2) == [segment2.id]


async def test_eats_waybill_driver_scoring_score(
        candidates,
        load_json,
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        mockserver,
        testpoint,
        exp_eats_dispatch_settings,
        exp_eats_segment_scoring_method,
):
    candidates_json = load_json('candidates.json')
    candidates_json['candidates'][0]['position'] = [0.01, -0.01]
    candidates_json['candidates'][1]['position'] = [0.04, -0.02]
    candidates(candidates_json)

    await exp_eats_dispatch_settings(exclude_return_points=True)
    await exp_eats_segment_scoring_method()

    @testpoint('eats_planner::pass')
    def pass_segment(_):
        pass

    @testpoint('eats_planner::assign_segment')
    def assign_single_segment(_):
        pass

    @testpoint('eats_planner::assign_live_batch')
    def assign_live_batch(_):
        pass

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_scoring(request):
        response = {'responses': []}
        for req in request.json['requests']:
            candidates = []
            for candidate in req['candidates']:
                points = candidate['batch_route_info']['route_points']
                candidates.append(
                    {
                        'id': candidate['id'],
                        'score': points[-1]['distance_m'] / 100,
                    },
                )
            response['responses'].append({'candidates': candidates})
        return response

    score: Dict[Tuple[str, str], float] = {}

    @testpoint('eats_planner::score_segment_candidate')
    def _score_segment_candidate(data):
        key = data['segment_id'], data['candidate_id']
        if key not in score or score[key] > data['score']:
            score[key] = data['score']

    segments = [
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.01, 0],
            dropoff_coordinates=[0.01, 0.08],
        ),
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.04, 0],
            dropoff_coordinates=[0.04, 0.08],
        ),
    ]

    await state_taxi_order_performer_found()

    segments_info = [get_segment(segment.id) for segment in segments]

    old_waybills = [
        get_waybill(segment_info['waybill_ref'])
        for segment_info in segments_info
    ]
    _remove_infrastructure_fields(old_waybills)

    assert old_waybills[0]['candidate']['info']['id'] == 'dbid1_uuid1'
    assert old_waybills[1]['candidate']['info']['id'] == 'dbid1_uuid2'

    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.02, 0],
            dropoff_coordinates=[0.02, 0.08],
        ),
    )
    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.01, 0.04],
            dropoff_coordinates=[0.01, 0.12],
        ),
    )
    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.03, 0.1],
            dropoff_coordinates=[0.03, 0.18],
        ),
    )
    await state_waybill_proposed()

    segments_info = [get_segment(segment.id) for segment in segments]

    waybills = [
        get_waybill(segment_info['waybill_ref'])
        for segment_info in segments_info
        if segment_info['waybill_ref']
    ]
    _remove_infrastructure_fields(waybills)

    assert waybills[:2] == old_waybills
    assert get_waybill_segment_ids(waybills[2]['waybill']) == [
        segments[1].id,
        segments[2].id,
    ]
    assert get_waybill_segment_ids(waybills[3]['waybill']) == [
        segments[0].id,
        segments[3].id,
    ]
    assert segments_info[4]['waybill_ref'] is None

    assert get_waybill_path(waybills[2]['waybill']) == [
        [0.04, 0],
        [0.02, 0],
        [0.02, 0.08],
        [0.04, 0.08],
        [0.04, 0],
        [0.02, 0],
    ]
    assert get_waybill_path(waybills[3]['waybill']) == [
        [0.01, 0],
        [0.01, 0.04],
        [0.01, 0.08],
        [0.01, 0.12],
        [0.01, 0],
        [0.01, 0.04],
    ]
    assert waybills[2]['candidate']['info']['id'] == 'dbid1_uuid2'
    assert waybills[3]['candidate']['info']['id'] == 'dbid1_uuid1'

    expected_score = {
        (segments[0].id, 'dbid1_uuid1'): 100.0,
        (segments[0].id, 'dbid1_uuid2'): 129.0,
        (segments[1].id, 'dbid1_uuid1'): 124.0,
        (segments[1].id, 'dbid1_uuid2'): 111.0,
        (segments[2].id, 'dbid1_uuid1'): 22.0,
        (segments[2].id, 'dbid1_uuid2'): 44.0,
        (segments[3].id, 'dbid1_uuid1'): 44.0,
        (segments[3].id, 'dbid1_uuid2'): 78.0,
        (segments[4].id, 'dbid1_uuid1'): 213.0,
        (segments[4].id, 'dbid1_uuid2'): 222.0,
    }
    assert score == expected_score
    assert assign_single_segment.times_called == 2
    assert assign_live_batch.times_called == 2
    assert pass_segment.times_called == 1  # segment 4 passed
    assert len(propositions_manager.propositions) == 2
    assert len(propositions_manager.live_propositions) == 2


async def test_eats_waybill_eats_eta_batch_score(
        mockserver,
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        scoring,
        testpoint,
        load_json,
        candidates,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
):
    candidates_json = load_json('candidates.json')
    candidates_json['candidates'][0]['position'] = [0.01, -0.01]
    candidates_json['candidates'][1]['position'] = [0.04, -0.02]

    candidates(candidates_json)

    await exp_eats_dispatch_settings()
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )

    @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
    def _mock_eats_eta(_):
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

    @testpoint('eats_planner::assign_segment')
    def assign_single_segment(_):
        pass

    @testpoint('eats_planner::assign_live_batch')
    def assign_live_batch(_):
        pass

    score: Dict[Tuple[str, str], float] = {}

    @testpoint('eats_planner::score_segment_candidate')
    def _score_segment_candidate(data):
        key = data['segment_id'], data['candidate_id']
        if key not in score or score[key] > data['score']:
            score[key] = data['score']

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
            pickup_coordinates=[0.01, 0],
            dropoff_coordinates=[0.01, 0.08],
        ),
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.04, 0],
            dropoff_coordinates=[0.04, 0.08],
        ),
    ]

    await state_taxi_order_performer_found()

    segments_info = [get_segment(segment.id) for segment in segments]

    old_waybills = [
        get_waybill(segment_info['waybill_ref'])
        for segment_info in segments_info
        if segment_info['waybill_ref']
    ]
    _remove_infrastructure_fields(old_waybills)

    assert old_waybills[0]['candidate']['info']['id'] == 'dbid1_uuid1'
    assert old_waybills[1]['candidate']['info']['id'] == 'dbid1_uuid2'

    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.02, 0],
            dropoff_coordinates=[0.02, 0.08],
        ),
    )
    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.01, 0.04],
            dropoff_coordinates=[0.01, 0.12],
        ),
    )
    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.03, 0.1],
            dropoff_coordinates=[0.03, 0.18],
        ),
    )
    await state_waybill_proposed()

    segments_info = [get_segment(segment.id) for segment in segments]

    waybills = [
        get_waybill(segment_info['waybill_ref'])
        for segment_info in segments_info
        if segment_info['waybill_ref']
    ]
    _remove_infrastructure_fields(waybills)

    assert waybills[:2] == old_waybills
    assert get_waybill_segment_ids(waybills[2]['waybill']) == [
        segments[1].id,
        segments[2].id,
    ]
    assert get_waybill_segment_ids(waybills[3]['waybill']) == [
        segments[0].id,
        segments[3].id,
    ]

    expected_score = {
        (segments[0].id, 'dbid1_uuid1'): 10006.0,
        (segments[0].id, 'dbid1_uuid2'): 12904.0,
        (segments[1].id, 'dbid1_uuid1'): 12411.0,
        (segments[1].id, 'dbid1_uuid2'): 11118.0,
        (segments[2].id, 'dbid1_uuid1'): 2222.0,
        (segments[2].id, 'dbid1_uuid2'): 4445.999999999998,
        (segments[3].id, 'dbid1_uuid1'): 4446.0,
        (segments[3].id, 'dbid1_uuid2'): 7782.0,
        (segments[4].id, 'dbid1_uuid1'): 21326.0,
        (segments[4].id, 'dbid1_uuid2'): 22284.0,
    }
    assert score == expected_score
    assert assign_single_segment.times_called == 2
    assert assign_live_batch.times_called == 2
    assert len(propositions_manager.propositions) == 2
    assert len(propositions_manager.live_propositions) == 2


@pytest.mark.parametrize(
    'third_segment_kwargs, batch_allowed',
    [
        pytest.param(
            {
                'pickup_coordinates': [0.01, 0],
                'dropoff_coordinates': [0.01, 0.08],
            },
            False,
            id='not allowed',
        ),
        pytest.param(
            {
                'pickup_coordinates': [0.07, 0],
                'dropoff_coordinates': [0.07, 0.08],
            },
            True,
            id='allowed',
        ),
    ],
)
async def test_eats_waybill_batch_in_chain(
        mockserver,
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        load_json,
        candidates,
        exp_eats_dispatch_settings,
        exp_eats_scoring_coefficients,
        exp_eats_segment_scoring_method,
        third_segment_kwargs,
        batch_allowed,
):
    candidates_json = load_json('candidates.json')
    candidates_json['candidates'][0]['position'] = [0.01, -0.01]
    candidates_json['candidates'] = candidates_json['candidates'][:1]

    candidates(candidates_json)

    await exp_eats_dispatch_settings()
    await exp_eats_segment_scoring_method(
        use_driver_scoring_score_for_batches=False,
        use_driver_scoring_score_for_segments=False,
    )

    @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
    def _mock_eats_eta(_):
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

    segments = [
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.01, 0],
            dropoff_coordinates=[0.01, 0.08],
        ),
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            pickup_coordinates=[0.07, 0],
            dropoff_coordinates=[0.07, 0.08],
        ),
    ]
    await state_taxi_order_performer_found()
    await state_taxi_order_performer_found()

    segments_info = [get_segment(segment.id) for segment in segments]

    old_waybills = [
        get_waybill(segment_info['waybill_ref'])
        for segment_info in segments_info
        if segment_info['waybill_ref']
    ]
    _remove_infrastructure_fields(old_waybills)

    assert len(old_waybills[0]['waybill']['segments']) == 1
    assert len(old_waybills[1]['waybill']['segments']) == 1

    candidates_json['candidates'][0]['chain_info'] = {
        'destination': [0.01, 0.08],
        'left_time': 500,
        'left_dist': 1000,
        'order_id': old_waybills[0]['waybill']['taxi_order_id'],
    }
    candidates(candidates_json)

    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=make_eats_custom_context(),
            **third_segment_kwargs,
        ),
    )
    await state_waybill_proposed()

    segments_info = [get_segment(segment.id) for segment in segments]

    waybills = [
        get_waybill(segment_info['waybill_ref'])
        for segment_info in segments_info
        if segment_info['waybill_ref']
    ]
    _remove_infrastructure_fields(waybills)

    if batch_allowed:
        assert len(waybills[0]['waybill']['segments']) == 1
        assert len(waybills[1]['waybill']['segments']) == 1
        assert len(waybills[2]['waybill']['segments']) == 2
        assert (
            waybills[1]['waybill']['segments'][0]
            == waybills[2]['waybill']['segments'][0]
        )
    else:
        assert len(waybills[0]['waybill']['segments']) == 1
        assert len(waybills[1]['waybill']['segments']) == 1
        assert len(waybills[2]['waybill']['segments']) == 1


@pytest.mark.now('2021-09-23T15:30:47.185337+00:00')
@pytest.mark.parametrize(
    'config_params, batch_allowed',
    [
        pytest.param(
            {
                'max_carrying_linear_distance': 100000,
                'max_carrying_route_distance': 100000,
                'max_carrying_time': 100000,
                'distinct_places_settings': {'allow': True},
                'weight_restrictions': {'limit': 100000},
                'due_threshold': 100000,
                'max_late_dropoff': 100000,
            },
            True,
            id='batch_allowed',
        ),
        pytest.param(
            {
                'max_carrying_linear_distance': 1,
                'max_carrying_route_distance': 1,
                'max_carrying_time': 100000,
                'distinct_places_settings': {'allow': True},
                'weight_restrictions': {'limit': 100000},
                'due_threshold': 100000,
                'max_late_dropoff': 100000,
            },
            False,
            id='distance_check',
        ),
        pytest.param(
            {
                'max_carrying_linear_distance': 100000,
                'max_carrying_route_distance': 100000,
                'max_carrying_time': 1,
                'distinct_places_settings': {'allow': True},
                'weight_restrictions': {'limit': 100000},
                'due_threshold': 100000,
                'max_late_dropoff': 100000,
            },
            False,
            id='time_check',
        ),
        pytest.param(
            {
                'max_carrying_linear_distance': 100000,
                'max_carrying_route_distance': 100000,
                'max_carrying_time': 100000,
                'distinct_places_settings': {'allow': True},
                'weight_restrictions': {'limit': 0},
                'due_threshold': 100000,
                'max_late_dropoff': 100000,
            },
            False,
            id='weight_check',
        ),
        pytest.param(
            {
                'max_carrying_linear_distance': 100000,
                'max_carrying_route_distance': 100000,
                'max_carrying_time': 100000,
                'distinct_places_settings': {'allow': True},
                'weight_restrictions': {'limit': 100000},
                'due_threshold': 0,
                'max_late_dropoff': 100000,
            },
            False,
            id='due_threshold_check',
        ),
        pytest.param(
            {
                'max_carrying_linear_distance': 100000,
                'max_carrying_route_distance': 100000,
                'max_carrying_time': 100000,
                'distinct_places_settings': {'allow': True},
                'weight_restrictions': {'limit': 100000},
                'due_threshold': 100000,
                'max_late_dropoff': 0,
            },
            False,
            id='max_late_dropoff_check',
        ),
    ],
)
async def test_eats_waybill_batch_configs(
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        scoring,
        testpoint,
        experiments3,
        exp_eats_dispatch_settings,
        make_eats_custom_context,
        taxi_united_dispatch_eats,
        config_params,
        batch_allowed,
):
    experiments3.add_config(
        name='united_dispatch_eats_segment_live_batches',
        consumers=['united-dispatch/eats_segment_live_batches'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'predicate': {
                    'init': {
                        'arg_name': 'place_id',
                        'set': [9998, 9999],
                        'set_elem_type': 'int',
                    },
                    'type': 'in_set',
                },
                'value': config_params,
            },
        ],
        default_value={
            'max_carrying_linear_distance': 0,
            'max_carrying_route_distance': 0,
            'max_carrying_time': 0,
            'distinct_places_settings': {'allow': False},
            'weight_restrictions': {'limit': 0},
            'due_threshold': 0,
            'max_late_dropoff': 0,
        },
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    await exp_eats_dispatch_settings(enable_segments_filtration=True)

    @testpoint('eats_planner::assign_segment')
    def assign_single_segment(_):
        pass

    @testpoint('eats_planner::assign_live_batch')
    def assign_live_batch(_):
        pass

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

    custom_context = make_eats_custom_context()
    custom_context['delivery_flags'] = None

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        due='2021-09-23T15:35:47.185337+00:00',
        custom_context=dict(custom_context, place_id=9998),
        pickup_coordinates=[0.01, 0],
        dropoff_coordinates=[0.01, 0.08],
        dropoff_time_intervals=[
            {
                'type': 'strict_match',
                'from': '2021-09-23T15:00:47.185337+00:00',
                'to': '2021-11-15T01:20:47.185337+00:00',
            },
        ],
    )
    await state_taxi_order_performer_found()

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        due='2021-09-23T15:36:47.185337+00:00',
        custom_context=dict(custom_context, place_id=9999),
        pickup_coordinates=[0.02, 0],
        dropoff_coordinates=[0.02, 0.08],
        dropoff_time_intervals=[
            {
                'type': 'strict_match',
                'from': '2021-09-23T15:00:47.185337+00:00',
                'to': '2021-11-15T01:20:47.185337+00:00',
            },
        ],
    )
    await state_waybill_proposed()

    if batch_allowed:
        assert assign_live_batch.times_called == 1
        assert assign_single_segment.times_called == 1
    else:
        assert assign_live_batch.times_called == 0
        assert assign_single_segment.times_called == 2


@pytest.mark.experiments3(
    name='united_dispatch_eats_segment_allowed_for_batching',
    consumers=['united-dispatch/eats_segment_allowed_for_batching'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'place_id',
                    'set': [9998],
                    'set_elem_type': 'int',
                },
                'type': 'in_set',
            },
            'value': {'allowed': True},
        },
    ],
    default_value={'allowed': False},
    is_config=True,
)
async def test_live_batching_segments_filter(
        create_segment,
        state_waybill_proposed,
        state_taxi_order_performer_found,
        scoring,
        testpoint,
        exp_eats_dispatch_settings,
        make_eats_custom_context,
):
    await exp_eats_dispatch_settings(enable_segments_filtration=True)

    @testpoint('eats_planner::assign_segment')
    def assign_single_segment(_):
        pass

    @testpoint('eats_planner::assign_live_batch')
    def assign_live_batch(_):
        pass

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

    custom_context = make_eats_custom_context()
    custom_context['delivery_flags'] = None

    segments = [
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=custom_context,
            pickup_coordinates=[0.01, 0],
            dropoff_coordinates=[0.01, 0.08],
        ),
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=custom_context,
            pickup_coordinates=[0.04, 0],
            dropoff_coordinates=[0.04, 0.08],
        ),
    ]

    await state_taxi_order_performer_found()

    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            # allow for batching
            custom_context=dict(custom_context, place_id=9998),
            pickup_coordinates=[0.02, 0],
            dropoff_coordinates=[0.02, 0.08],
        ),
    )
    segments.append(
        create_segment(
            corp_client_id='eats_corp_id',
            taxi_classes={'eda'},
            custom_context=custom_context,
            pickup_coordinates=[0.01, 0.04],
            dropoff_coordinates=[0.01, 0.12],
        ),
    )
    await state_waybill_proposed()

    assert assign_live_batch.times_called == 1
    assert assign_single_segment.times_called == 3


def _remove_infrastructure_fields(waybills):
    for waybill in waybills:
        waybill.pop('revision')
        waybill.pop('update_proposition_id')
        waybill.pop('rebuilt_at')
        waybill.pop('updated_ts')
        waybill.pop('created_ts')
