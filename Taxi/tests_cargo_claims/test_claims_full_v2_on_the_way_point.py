from testsuite.utils import matching


async def test_in_terminal_status(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(target_status='cancelled')

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={
            'claim_id': claim_info.claim_id,
            'check_on_the_way_state': False,
        },
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert 'on_the_way_state' not in response.json()

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert 'on_the_way_state' not in response.json()


async def test_in_status_without_performer(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(target_status='new')

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={
            'claim_id': claim_info.claim_id,
            'check_on_the_way_state': True,
        },
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert response.json()['on_the_way_state'] == {}


async def test_route_not_found(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        create_segment_with_performer,
):
    claim_info = await create_segment_with_performer(claim_index=0)

    @mockserver.json_handler('/cargo-dispatch/v1/segment/route')
    def _mock_segment_route():
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'Segment not found'},
        )

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={
            'claim_id': claim_info.claim_id,
            'check_on_the_way_state': True,
        },
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['on_the_way_state'] == {}


async def test_in_not_terminal_status(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        create_segment_with_performer,
        get_db_segment_ids,
        get_segment_points_by_segment_id,
):
    claim_1 = await create_segment_with_performer(claim_index=0)
    claim_2 = await create_segment_with_performer(claim_index=1)
    seg1, seg2 = await get_db_segment_ids()

    claim_1_points = await get_segment_points_by_segment_id(seg1)
    claim_2_points = await get_segment_points_by_segment_id(seg2)

    @mockserver.json_handler('/cargo-dispatch/v1/segment/route')
    def _mock_segment_route():
        return mockserver.make_response(
            status=200,
            json={
                'route': [
                    {'point_id': claim_1_points[0]['point_id']},
                    {'point_id': claim_1_points[1]['point_id']},
                    {'point_id': claim_1_points[2]['point_id']},
                    {'point_id': claim_2_points[0]['point_id']},
                    {'point_id': claim_2_points[1]['point_id']},
                    {'point_id': claim_2_points[2]['point_id']},
                ],
            },
        )

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={'claim_id': claim_1.claim_id, 'check_on_the_way_state': True},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['on_the_way_state'] == {
        'current_point': {
            'claim_point_id': claim_1_points[0]['claim_point_id'],
            'last_status_change_ts': matching.datetime_string,
            'visit_status': 'pending',
        },
    }

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={'claim_id': claim_2.claim_id, 'check_on_the_way_state': True},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['on_the_way_state'] == {}
