import pytest

from testsuite.utils import matching


async def test_arrive_at_point_success(
        taxi_cargo_claims,
        pgsql,
        create_segment_with_performer,
        get_db_segment_ids,
        get_segment,
        state_controller,
        get_current_claim_point,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )

    current_claim_point = await get_current_claim_point(claim_info.claim_id)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'last_known_status': 'new',
            'point_id': current_claim_point,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )

    assert response.status_code == 200
    assert response.json()['new_status'] == 'new'

    segment = await get_segment(segment_id)
    assert segment['status'] == 'pickup_arrived'

    for point in segment['points']:
        if point['claim_point_id'] != current_claim_point:
            continue
        assert point['visit_status'] == 'arrived'

    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'pickup_arrived'


async def test_arrive_bad_point(
        taxi_cargo_claims,
        create_segment,
        get_db_segment_ids,
        state_controller,
):
    await create_segment()
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]
    await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )

    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'last_known_status': 'new',
            'idempotency_token': '100500',
            'point_id': 1300,
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )

    assert response.status_code == 409


async def test_segment_arrive_dont_seted(
        get_segment, testpoint, prepare_state, arrive_at_point,
):
    """
        Check visit status doesnt change from visited to arrived
    """

    segment_id = await prepare_state(
        visit_order=2, last_arrive_at_point=False, last_exchange_init=False,
    )

    @testpoint('mark_point_visit_status')
    def mark_point_visited(data):
        return 'visited'

    await arrive_at_point(segment_id, point_visit_order=2)

    assert mark_point_visited.has_calls

    segment = await get_segment(segment_id)
    for i in range(0, 2):
        assert segment['points'][i]['visit_status'] == 'visited'
    assert segment['points'][2]['visit_status'] == 'pending'


@pytest.mark.parametrize(
    'last_known_status, expected_response_code',
    [('delivering', 409), (None, 200)],
)
async def test_no_last_known_status_validation_for_batch(
        taxi_cargo_claims,
        create_segment_with_performer,
        state_controller,
        get_current_claim_point,
        get_db_segment_ids,
        last_known_status,
        expected_response_code,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )
    current_claim_point = await get_current_claim_point(claim_info.claim_id)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    request_body = {
        'idempotency_token': '100500',
        'point_id': current_claim_point,
        'driver': {'park_id': 'park_id1', 'driver_profile_id': 'driver_id1'},
    }
    if last_known_status:
        request_body['last_known_status'] = last_known_status
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json=request_body,
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == expected_response_code


async def test_point_changelog_cargo_order_id(
        create_segment_with_performer,
        taxi_cargo_claims,
        get_segment,
        get_segment_id,
        claim_point_id_by_visit_order,
        get_default_cargo_order_id,
):
    await create_segment_with_performer()
    segment_id = await get_segment_id()

    # set first point arrived
    claim_point_id = await claim_point_id_by_visit_order(
        segment_id=segment_id, visit_order=1,
    )
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'cargo_order_id': get_default_cargo_order_id,
            'last_known_status': 'new',
            'point_id': claim_point_id,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == 200

    # check cargo_order_id is set for arrived status
    segment = await get_segment(segment_id)
    first_point_changelog = next(
        p['changelog'] for p in segment['points'] if p['visit_order'] == 1
    )
    assert first_point_changelog == [
        {'status': 'pending', 'timestamp': matching.AnyString()},
        {
            'status': 'arrived',
            'driver_id': 'driver_id1',
            'cargo_order_id': get_default_cargo_order_id,
            'timestamp': matching.AnyString(),
        },
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_execution_reset',
    consumers=['cargo-claims/geocoder'],
    clauses=[],
    default_value={
        'reset_points_on_new_driver_found': True,
        'validate_driver_on_arrive_at_point': False,
    },
    is_config=True,
)
async def test_arrive_from_different_drivers(
        create_segment_with_performer,
        taxi_cargo_claims,
        get_segment,
        get_segment_id,
        claim_point_id_by_visit_order,
        get_default_cargo_order_id,
        build_segment_update_request,
):
    """
    1) First driver arrived at point
    2) Taxi autoreorder was happened
    3) New driver arrived at point

    Check point changelog
    """

    await create_segment_with_performer()
    segment_id = await get_segment_id()

    # First driver arrived
    claim_point_id = await claim_point_id_by_visit_order(
        segment_id=segment_id, visit_order=1,
    )
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'cargo_order_id': get_default_cargo_order_id,
            'last_known_status': 'new',
            'point_id': claim_point_id,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == 200

    # New driver was found
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    'taxi_order_id_1',
                    with_performer=True,
                    driver_id='new_driver_132',
                    revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200

    # New driver arrived at point
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'cargo_order_id': get_default_cargo_order_id,
            'last_known_status': 'new',
            'point_id': claim_point_id,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'new_driver_132',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == 200

    # Check changelog
    segment = await get_segment(segment_id)
    first_point_changelog = next(
        p['changelog'] for p in segment['points'] if p['visit_order'] == 1
    )
    assert first_point_changelog == [
        {'status': 'pending', 'timestamp': matching.AnyString()},
        {
            'status': 'arrived',
            'driver_id': 'driver_id1',
            'cargo_order_id': get_default_cargo_order_id,
            'timestamp': matching.AnyString(),
        },
        {
            'status': 'pending',
            'timestamp': matching.AnyString(),
            'cargo_order_id': get_default_cargo_order_id,
        },
        {
            'status': 'arrived',
            'driver_id': 'new_driver_132',
            'cargo_order_id': get_default_cargo_order_id,
            'timestamp': matching.AnyString(),
        },
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_execution_reset',
    consumers=['cargo-claims/geocoder'],
    clauses=[],
    default_value={
        'reset_points_on_new_driver_found': True,
        'validate_driver_on_arrive_at_point': True,
    },
    is_config=True,
)
async def test_arrive_validation(
        create_segment_with_performer,
        taxi_cargo_claims,
        get_segment,
        get_segment_id,
        claim_point_id_by_visit_order,
        get_default_cargo_order_id,
        build_segment_update_request,
):
    """
    1) First driver arrived at point
    2) Taxi autoreorder was happened
    3) New driver arrived at point

    Wait event 3
    """

    await create_segment_with_performer()
    segment_id = await get_segment_id()

    # First driver arrived
    claim_point_id = await claim_point_id_by_visit_order(
        segment_id=segment_id, visit_order=1,
    )
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'cargo_order_id': get_default_cargo_order_id,
            'last_known_status': 'new',
            'point_id': claim_point_id,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == 200

    # Fail, we do not know new driver
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'cargo_order_id': get_default_cargo_order_id,
            'last_known_status': 'new',
            'point_id': claim_point_id,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'new_driver_132',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'state_mismatch',
        'message': 'Недопустимое действие',
    }

    # New driver was found
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    'taxi_order_id_1',
                    with_performer=True,
                    driver_id='new_driver_132',
                    revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200

    # Success
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'cargo_order_id': get_default_cargo_order_id,
            'last_known_status': 'new',
            'point_id': claim_point_id,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'new_driver_132',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == 200

    # Check changelog
    segment = await get_segment(segment_id)
    first_point_changelog = next(
        p['changelog'] for p in segment['points'] if p['visit_order'] == 1
    )
    assert first_point_changelog == [
        {'status': 'pending', 'timestamp': matching.AnyString()},
        {
            'status': 'arrived',
            'driver_id': 'driver_id1',
            'cargo_order_id': get_default_cargo_order_id,
            'timestamp': matching.AnyString(),
        },
        {
            'status': 'pending',
            'timestamp': matching.AnyString(),
            'cargo_order_id': get_default_cargo_order_id,
        },
        {
            'status': 'arrived',
            'driver_id': 'new_driver_132',
            'cargo_order_id': get_default_cargo_order_id,
            'timestamp': matching.AnyString(),
        },
    ]


async def test_arrive_at_point_support_audit(
        create_segment_with_performer,
        state_controller,
        taxi_cargo_claims,
        get_current_claim_point,
        get_db_segment_ids,
        check_audit,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )

    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]
    claim_id = claim_info.claim_id
    current_claim_point = await get_current_claim_point(claim_id)

    ticket = 'TICKET-123'
    comment = 'some comment'
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'last_known_status': 'new',
            'point_id': current_claim_point,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            },
            'support': {'ticket': ticket, 'comment': comment},
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )

    assert response.status_code == 200

    await check_audit(claim_id, ticket, comment)
