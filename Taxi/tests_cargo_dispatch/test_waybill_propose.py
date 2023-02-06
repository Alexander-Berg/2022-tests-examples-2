import pytest

SMART_ROUTER = 'smart_router'
FALLBACK_ROUTER = 'fallback_router'


def test_happy_path_works(happy_path_state_all_waybills_proposed):
    pass


async def test_change_points_in_array_without_changing_visit_order_is_ok(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
):
    waybill = await waybill_from_segments(SMART_ROUTER, 'my_waybill', 'seg1')
    waybill['points'].append(waybill['points'].pop(0))
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200


async def test_waybill_ref_uniqueness(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        propose_from_segments,
        request_waybill_propose,
):
    unique_ref = 'waybill_unique_ref'
    await propose_from_segments(FALLBACK_ROUTER, unique_ref, 'seg1')

    waybill = await waybill_from_segments(SMART_ROUTER, unique_ref, 'seg2')
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400
    assert response.json()['code'] == 'waybill_ref_not_unique'


async def test_forbidden_for_segment_router_not_accepted(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
):
    waybill = await waybill_from_segments(SMART_ROUTER, 'my_waybill', 'seg3')
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400
    assert response.json()['code'] == 'nonexistent_segment'


@pytest.mark.parametrize(
    'segments, new_order',
    [
        (('seg2',), ['seg2_A1_p1', 'seg2_B1_p2', 'seg2_C1_p3']),
        (
            ('seg1', 'seg2'),
            [
                # complete first
                'seg2_A1_p1',
                'seg2_B1_p2',
                'seg2_C1_p3',
                # complete second
                'seg1_A1_p1',
                'seg1_A2_p2',
                'seg1_B1_p3',
                'seg1_B2_p4',
                'seg1_B3_p5',
                'seg1_A2_p6',
                'seg1_A1_p7',
            ],
        ),
        (
            ('seg1', 'seg2'),
            [
                'seg2_A1_p1',
                'seg1_A1_p1',
                'seg2_B1_p2',
                'seg1_A2_p2',
                'seg1_B1_p3',
                'seg2_C1_p3',
                'seg1_B2_p4',
                'seg1_B3_p5',
                'seg1_A2_p6',
                'seg1_A1_p7',
            ],
        ),
        (
            ('seg7',),
            [
                'seg7_A1_p1',
                'seg7_A2_p2',
                'seg7_B1_p3',
                'seg7_B2_p4',
                'seg7_A2_p5',
                'seg7_A1_p6',
            ],
        ),
    ],
)
async def test_valid_graph_accepted(
        segments,
        new_order,
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
        state_seg7_ready,
):
    waybill = await waybill_from_segments(
        FALLBACK_ROUTER, 'my_waybill', *segments,
    )
    waybill['points'] = _change_points_order(waybill['points'], new_order)
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'segments, new_order',
    [
        (
            ('seg1',),
            [
                # change pickup points order
                'seg1_A2_p2',
                'seg1_A1_p1',
                # change dropoff points order
                'seg1_B3_p5',
                'seg1_B1_p3',
                'seg1_B2_p4',
                # change return points order
                'seg1_A1_p7',
                'seg1_A2_p6',
            ],
        ),
        (
            ('seg1',),
            # dropoff before pickup
            [
                'seg1_B1_p3',
                'seg1_A1_p1',
                'seg1_A2_p2',
                'seg1_B2_p4',
                'seg1_B3_p5',
                'seg1_A2_p6',
                'seg1_A1_p7',
            ],
        ),
        (
            ('seg1',),
            # return before dropoff
            [
                'seg1_A1_p1',
                'seg1_A2_p2',
                'seg1_A2_p6',
                'seg1_B1_p3',
                'seg1_B2_p4',
                'seg1_B3_p5',
                'seg1_A1_p7',
            ],
        ),
        (
            ('seg1',),
            # return before pickup
            [
                'seg1_A2_p6',
                'seg1_A1_p1',
                'seg1_A2_p2',
                'seg1_B1_p3',
                'seg1_B2_p4',
                'seg1_B3_p5',
                'seg1_A1_p7',
            ],
        ),
        (
            ('seg1', 'seg2'),
            [
                # complete first
                'seg2_A1_p1',
                'seg1_B2_p4',
                'seg2_B1_p2',
                'seg1_A2_p2',
                'seg2_C1_p3',
                # complete second
                'seg1_A1_p1',
                'seg1_B1_p3',
                'seg1_B3_p5',
                'seg1_A2_p6',
                'seg1_A1_p7',
            ],
        ),
    ],
)
async def test_invalid_graph(
        segments,
        new_order,
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
):
    waybill = await waybill_from_segments(
        SMART_ROUTER, 'my_waybill', *segments,
    )
    waybill['points'] = _change_points_order(waybill['points'], new_order)
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'new_order',
    [
        [
            'seg1_A2_p2',
            'seg1_B1_p3',
            'seg1_B2_p4',
            'seg1_B3_p5',
            'seg1_A2_p6',
            'seg1_A1_p7',
        ],
    ],
)
async def test_proposition_without_one_point(
        new_order,
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
):
    waybill = await waybill_from_segments(SMART_ROUTER, 'my_waybill', 'seg1')
    waybill['points'] = _change_points_order(
        waybill['points'], new_order, False,
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400


def _change_points_order(old_points, new_order, forbid_loosing_points=True):
    points_map = {}
    for point_obj in old_points:
        points_map[point_obj['point_id']] = point_obj

    new_points = []
    for visit_order, point_id in enumerate(new_order, start=1):
        point_obj = points_map.pop(point_id)
        assert 'visit_order' in point_obj
        point_obj['visit_order'] = visit_order
        new_points.append(point_obj)

    if points_map and forbid_loosing_points:
        raise ValueError(
            'new_order must contain all point ids from old points: '
            'new_order=%s old_points=%s' % (new_order, old_points),
        )

    return new_points


@pytest.fixture(name='state_seg7_ready')
async def _state_seg7_ready(
        happy_path_claims_segment_db,
        happy_path_state_init,
        run_claims_segment_replication,
        run_choose_routers,
):
    points = [
        ('p1', 'A1', ('pickup', ['i1']), None),
        ('p2', 'A2', ('pickup', ['i2']), None),
        ('p3', 'B1', ('dropoff', ['i1']), None),
        ('p4', 'B2', ('dropoff', ['i2']), None),
        ('p5', 'A2', ('return', ['i2']), None),
        ('p6', 'A1', ('return', ['i1']), None),
    ]
    happy_path_claims_segment_db.add_segment(segment_number=7, points=points)

    result_repl = await run_claims_segment_replication()
    assert result_repl['stats']['inserted-segments'] == 1

    result_choosing = await run_choose_routers()
    assert result_choosing['stats']['updated-segments'] == 1


async def test_check_taxi_order_requirements(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
        mockserver,
):
    @mockserver.json_handler('/cargo-orders/v1/check-taxi-requirements')
    def _mock(request):
        assert request.json == {
            'taxi_classes': ['express', 'courier'],
            'door_to_door': True,
        }
        return mockserver.make_response(
            status=400,
            json={'code': 'Bad request', 'message': 'Wrong requirements'},
        )

    waybill = await waybill_from_segments(SMART_ROUTER, 'my_waybill', 'seg1')
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400


async def test_propose_special_requirements(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
):
    waybill = await waybill_from_segments(SMART_ROUTER, 'my_waybill', 'seg1')
    waybill['special_requirements'] = {'virtual_tariffs': []}
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200


async def test_propose_on_resolved_segment(
        happy_path_cancelled_by_user,
        waybill_from_segments,
        request_waybill_propose,
):
    waybill = await waybill_from_segments(
        SMART_ROUTER, 'my_waybill_on_resolved_segment', 'seg3',
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400
    assert response.json() == {
        'code': 'nonexistent_segment',
        'message': 'Segment seg3 already resolved. Do not accept proposition',
    }


async def test_propose_two_waybills_same_router(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
        run_choose_waybills,
):
    waybill = await waybill_from_segments(
        SMART_ROUTER, 'first_waybill', 'seg1',
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200

    await run_choose_waybills()

    waybill = await waybill_from_segments(
        SMART_ROUTER, 'second_waybill', 'seg1',
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400
    assert response.json() == {
        'code': 'segment_already_choses_this_routers_waybill',
        'message': (
            'Segment seg1 already choses waybill by router_id smart_router'
        ),
    }


@pytest.mark.config(
    CARGO_DISPATCH_WAYBILL_REF_IDEMPOTENCY_IN_PROPOSE={
        'router': {'__default__': False},
    },
)
async def test_propose_two_waybills_same_router_idempotency_disabled(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
        run_choose_waybills,
):
    waybill = await waybill_from_segments(
        SMART_ROUTER, 'first_waybill', 'seg1',
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200

    await run_choose_waybills()

    waybill = await waybill_from_segments(
        SMART_ROUTER, 'first_waybill', 'seg1',
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400
    assert response.json() == {
        'code': 'segment_already_choses_this_routers_waybill',
        'message': (
            'Segment seg1 already choses waybill by router_id smart_router'
        ),
    }


@pytest.mark.config(
    CARGO_DISPATCH_WAYBILL_REF_IDEMPOTENCY_IN_PROPOSE={
        'router': {'__default__': False, SMART_ROUTER: True},
    },
)
async def test_propose_two_waybills_same_router_idempotency(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
        run_choose_waybills,
):
    waybill = await waybill_from_segments(
        SMART_ROUTER, 'first_waybill', 'seg1',
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200

    await run_choose_waybills()

    waybill = await waybill_from_segments(
        SMART_ROUTER, 'first_waybill', 'seg1',
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200


async def test_proposed_batch_with_old_version(
        happy_path_state_waybills_chosen,
        propose_from_segments,
        run_choose_routers,
        reorder_waybill,
        get_segment_info,
):
    # Increment segment.waybill_building_version
    await reorder_waybill('waybill_smart_1')
    segment = await get_segment_info('seg1')
    assert segment['dispatch']['waybill_building_version'] == 2
    await run_choose_routers()

    # Propose waybill with old version:
    response_body = await propose_from_segments(
        SMART_ROUTER,
        'waybill_smart_2',
        'seg1',
        'seg2',
        segment_building_versions={'seg1': 1},
        status_code=400,
    )
    assert response_body['code'] == 'invalid_segment_waybill_building_version'


async def test_propose_taxi_lookup_extra(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
        get_waybill_info,
):
    waybill_ref = 'my_waybill'
    extra = {'intent': 'grocery-manual', 'performer_id': 'performer_hash'}
    waybill = await waybill_from_segments(SMART_ROUTER, waybill_ref, 'seg1')

    waybill['taxi_lookup_extra'] = extra
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200
    updated_waybill = await get_waybill_info(waybill_ref)
    assert updated_waybill.status_code == 200
    assert updated_waybill.json()['waybill']['taxi_lookup_extra'] == extra


async def test_propose_forced_soon(
        happy_path_state_routers_chosen,
        waybill_from_segments,
        request_waybill_propose,
        get_waybill_info,
):
    taxi_order_requirements = {
        'forced_soon': True,
        'taxi_classes': ['foo', 'bar'],
    }
    waybill_ref = 'my_waybill'
    waybill = await waybill_from_segments(SMART_ROUTER, waybill_ref, 'seg1')
    waybill['taxi_order_requirements'] = taxi_order_requirements
    response = await request_waybill_propose(waybill)
    assert response.status_code == 200
    updated_waybill = await get_waybill_info(waybill_ref)
    assert updated_waybill.status_code == 200
    assert (
        updated_waybill.json()['waybill']['taxi_order_requirements']
        == taxi_order_requirements
    )
