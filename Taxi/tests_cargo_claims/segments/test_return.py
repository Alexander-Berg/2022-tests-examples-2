import typing

import pytest

from .. import conftest


def get_segment_point(segment, claim_point_id):
    for point in segment['points']:
        if point['claim_point_id'] == claim_point_id:
            return point
    raise pytest.fail(
        f'No such claim_point_id {claim_point_id} in segment: {segment}',
    )


def get_claim_point(claim, claim_point_id):
    for point in claim['route_points']:
        if point['id'] == claim_point_id:
            return point
    raise pytest.fail(
        f'No such claim_point_id {claim_point_id} in claim: {claim}',
    )


@pytest.mark.parametrize('is_support_request', [False, True])
@pytest.mark.parametrize(
    (
        'visit_order',
        'post_segment_status',
        'expect_taximter_status',
        # pickup code is used to force multipoint segment
        'pickup_code',
        'need_return_items',
    ),
    [
        (2, 'returning', 'returning', None, None),
        (2, 'pickuped', 'delivering', '123456', None),
        (2, 'pickuped', 'delivering', '123456', False),
        (3, 'returning', 'returning', '123456', True),
        (3, 'delivered', 'complete', '123456', False),
    ],
)
async def test_return(
        taxi_cargo_claims,
        mock_create_event,
        prepare_state,
        get_segment,
        get_claim_v2,
        pgsql,
        check_audit,
        is_support_request: bool,
        visit_order: int,
        post_segment_status: str,
        expect_taximter_status: str,
        pickup_code: typing.Optional[str],
        need_return_items: bool,
        expect_current_point: bool = True,
):
    mock_create_event()

    segment_id = await prepare_state(
        visit_order=visit_order, pickup_code=pickup_code,
    )

    segment = await get_segment(segment_id)

    claim_point_id = conftest.get_claim_point_id_by_order(segment, visit_order)

    json = {
        'point_id': claim_point_id,
        'last_known_status': conftest.TAXIMETER_STATUS_BY_STATUS[
            segment['status']
        ],
        'reasons': ['reason_a', 'reason_b'],
    }
    if is_support_request:
        json['support'] = {
            'comment': 'some comment',
            'ticket': 'CHATTERBOX-123',
        }
    else:
        json['driver'] = conftest.DRIVER_INFO
    json['need_return_items'] = need_return_items
    for _ in range(2):  # call twice to check idempotency
        segment = await get_segment(segment_id)
        response = await taxi_cargo_claims.post(
            '/v1/segments/return',
            params={'segment_id': segment_id},
            json=json,
            headers=conftest.get_headers(),
        )

        assert response.status_code == 200

        return_response = response.json()
        assert return_response['new_status'] == expect_taximter_status

        segment = await get_segment(segment_id)

        point = get_segment_point(segment, claim_point_id)
        no_need_return_items = need_return_items is False
        assert point['type'] == 'dropoff'
        assert point['visit_status'] == 'skipped'
        assert point['resolution']['is_skipped']
        assert point['is_return_required'] is not no_need_return_items
        assert segment['status'] == post_segment_status

        claim = await get_claim_v2(segment['diagnostics']['claim_id'])
        assert claim['status'] == post_segment_status

        claim_point = get_claim_point(claim, claim_point_id)
        assert claim_point['visit_status'] == 'skipped'

        if expect_current_point:
            assert claim['current_point_id'] == claim_point_id + 1
        else:
            assert 'current_point_id' not in claim

        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            'SELECT return_reasons '
            'FROM cargo_claims.claim_points '
            f'WHERE id = {claim_point_id}',
        )
        assert list(cursor) == [(['reason_a', 'reason_b'],)]

    if is_support_request:
        await check_audit(
            segment['diagnostics']['claim_id'],
            ticket='CHATTERBOX-123',
            comment='some comment',
        )


async def test_dragon_next_point_scheduled(
        taxi_cargo_claims, prepare_state, get_segment, stq, mock_create_event,
):
    mock_create_event()

    segment_id = await prepare_state(visit_order=2)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=2,
    )
    stq.cargo_dragon_next_point.flush()

    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json={
            'point_id': claim_point_id,
            'last_known_status': conftest.TAXIMETER_STATUS_BY_STATUS[
                segment['status']
            ],
            'driver': conftest.DRIVER_INFO,
        },
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200

    assert stq.cargo_dragon_next_point.times_called == 2
    for _ in range(2):
        call = stq.cargo_dragon_next_point.next_call()
        assert call['kwargs']['segment_id'] == segment_id
        assert call['kwargs']['claim_point_id'] == claim_point_id
        assert call['kwargs']['notify_taxi'] is False


@pytest.mark.parametrize(
    'last_known_status, expected_response_code', [('new', 409), (None, 200)],
)
async def test_no_last_known_status_validation_for_batch(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        last_known_status,
        expected_response_code,
        mock_create_event,
):
    mock_create_event()

    segment_id = await prepare_state(visit_order=2)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=2,
    )

    request_body = {'point_id': claim_point_id, 'driver': conftest.DRIVER_INFO}
    if last_known_status:
        request_body['last_known_status'] = last_known_status
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == expected_response_code


@pytest.mark.skip()
async def test_skip_segment(
        taxi_cargo_claims,
        testpoint,
        prepare_state,
        get_segment,
        get_default_cargo_order_id,
        build_segment_update_request,
        mock_create_event,
):
    mock_create_event()

    @testpoint('reset-segment-execution')
    def reset(data):
        pass

    segment_id = await prepare_state(visit_order=1)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=1,
    )

    request_body = {
        'cargo_order_id': get_default_cargo_order_id,
        'point_id': claim_point_id,
        'last_known_status': conftest.TAXIMETER_STATUS_BY_STATUS[
            segment['status']
        ],
        'driver': conftest.DRIVER_INFO,
    }

    # call twice to check idempotency
    for _ in range(2):
        response = await taxi_cargo_claims.post(
            '/v1/segments/return',
            params={'segment_id': segment_id},
            json=request_body,
            headers=conftest.get_headers(),
        )
        assert response.status_code == 200

        segment = await get_segment(segment_id)
        for point in segment['points']:
            assert point['visit_status'] == 'pending'
            assert not point['is_resolved']

        assert segment['status'] == 'performer_lookup'

    assert reset.next_call()['data'] == {
        'cleared_claim_points_count': 3,
        'cleared_claim_segment_points_count': 3,
        'cleared_claim_segments_count': 1,
        'cleared_claims_count': 1,
        'deleted_documents_count': 0,
        'deleted_performer_info_count': 1,
        'deleted_points_ready_for_interact_notifications_count': 0,
    }


async def test_skip_point_after_current(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        stq,
        get_claim_v2,
        mock_create_event,
):
    mock_create_event()
    # Driver arriver at point A

    # Pickup code is used to force multipoint segment
    segment_id = await prepare_state(visit_order=1, pickup_code='123456')
    segment = await get_segment(segment_id)
    assert len(segment['points']) == 4, 'Need multipoints segment'

    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=3,
    )
    request_body = {
        'point_id': claim_point_id,
        'support': {'comment': 'some comment', 'ticket': 'CHATTERBOX-123'},
        'last_known_status': 'pickup_confirmation',
    }
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'result': 'confirmed',
        'new_status': 'pickup_confirmation',
        'new_claim_status': 'ready_for_pickup_confirmation',
    }
    assert stq.cargo_dragon_next_point.times_called == 0

    current_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=1,
    )
    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    assert claim['current_point_id'] == current_point_id


async def test_confirm_after_skip(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        stq,
        get_claim_v2,
        exchange_confirm,
        mock_create_event,
):
    mock_create_event()

    # A -> *B1 -> B2 -> C
    # 1. Skip point B2
    # 2. Confirm point B1.
    # Check 'claim.current_point' == C

    # Pickup code is used to force multipoint segment
    segment_id = await prepare_state(visit_order=2, pickup_code='123456')
    segment = await get_segment(segment_id)
    assert len(segment['points']) == 4, 'Need multipoints segment'

    # 1
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=3,
    )
    request_body = {
        'point_id': claim_point_id,
        'support': {'comment': 'some comment', 'ticket': 'CHATTERBOX-123'},
        'last_known_status': 'droppof_confirmation',
    }
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200

    # 2
    point_b1 = conftest.get_claim_point_id_by_order(segment, visit_order=2)
    await exchange_confirm(
        segment_id, claim_point_id=point_b1, response_code=200,
    )

    # 3
    point_c = conftest.get_claim_point_id_by_order(segment, visit_order=4)
    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    assert claim['current_point_id'] == point_c


async def test_skip_point_after_returned(
        prepare_state,
        get_segment,
        exchange_confirm,
        get_claim_v2,
        taxi_cargo_claims,
        mock_create_event,
):
    mock_create_event()

    segment_id = await prepare_state(visit_order=2, pickup_code='123456')
    segment = await get_segment(segment_id)
    assert len(segment['points']) == 4, 'Need multipoints segment'

    point_a = conftest.get_claim_point_id_by_order(segment, visit_order=1)
    point_b1 = conftest.get_claim_point_id_by_order(segment, visit_order=2)
    await exchange_confirm(
        segment_id, claim_point_id=point_a, response_code=200,
    )
    await exchange_confirm(
        segment_id, claim_point_id=point_b1, response_code=200,
    )

    point_b2 = conftest.get_claim_point_id_by_order(segment, visit_order=3)
    request_body = {
        'point_id': point_b2,
        'support': {'comment': 'some comment', 'ticket': 'CHATTERBOX-123'},
    }
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200

    point_c = conftest.get_claim_point_id_by_order(segment, visit_order=4)
    await exchange_confirm(
        segment_id, claim_point_id=point_c, response_code=200,
    )

    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    assert claim['route_points'][0]['visit_status'] == 'visited'
    assert claim['route_points'][1]['visit_status'] == 'visited'
    assert claim['route_points'][2]['visit_status'] == 'skipped'
    assert claim['route_points'][3]['visit_status'] == 'visited'
    assert claim['status'] == 'returned'
    assert 'current_point_id' not in claim

    # fail /v1/segments/return with current_point_id is null
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200
    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    assert claim['route_points'][0]['visit_status'] == 'visited'
    assert claim['route_points'][1]['visit_status'] == 'visited'
    assert claim['route_points'][2]['visit_status'] == 'skipped'
    assert claim['route_points'][3]['visit_status'] == 'visited'
    assert claim['status'] == 'returned'


@pytest.mark.parametrize(
    ('need_return_items_b2', 'need_return_items_b1'),
    [(None, None), (None, False), (False, True), (False, False)],
)
async def test_return_twice(
        need_return_items_b2,
        need_return_items_b1,
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        stq,
        get_claim_v2,
        exchange_confirm,
        mock_create_event,
):
    mock_create_event()

    # *A -> B1 -> B2 -> C
    # 1. Skip point B2
    # 2. Confirm point A
    # 3. Skip point B1
    # Check 'claim.current_point' == C

    # Pickup code is used to force multipoint segment
    segment_id = await prepare_state(visit_order=1, pickup_code='123456')
    segment = await get_segment(segment_id)
    assert len(segment['points']) == 4, 'Need multipoints segment'

    # 1
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=3,
    )
    request_body = {
        'point_id': claim_point_id,
        'support': {'comment': 'some comment', 'ticket': 'CHATTERBOX-123'},
        'last_known_status': 'pickup_confirmation',
        'need_return_items': need_return_items_b2,
    }
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200
    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    assert claim['route_points'][0]['visit_status'] == 'arrived'
    assert claim['route_points'][1]['visit_status'] == 'pending'
    assert claim['route_points'][2]['visit_status'] == 'skipped'
    assert claim['route_points'][3]['visit_status'] == 'pending'
    assert claim['status'] == 'ready_for_pickup_confirmation'

    # 2
    point_a = conftest.get_claim_point_id_by_order(segment, visit_order=1)
    await exchange_confirm(
        segment_id, claim_point_id=point_a, response_code=200,
    )

    # 3
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=2,
    )
    request_body = {
        'point_id': claim_point_id,
        'support': {'comment': 'some comment', 'ticket': 'CHATTERBOX-123'},
        'last_known_status': 'delivering',
        'need_return_items': need_return_items_b1,
    }
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200

    # 3
    point_c = conftest.get_claim_point_id_by_order(segment, visit_order=4)
    no_return = False
    if need_return_items_b1 is False and need_return_items_b2 is False:
        no_return = True

    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    return_visit_status = 'skipped' if no_return else 'pending'
    assert claim['route_points'][0]['visit_status'] == 'visited'
    assert claim['route_points'][1]['visit_status'] == 'skipped'
    assert claim['route_points'][2]['visit_status'] == 'skipped'
    assert claim['route_points'][3]['visit_status'] == return_visit_status

    assert claim['current_point_id'] == point_c
    assert claim['status'] == 'delivered' if no_return else 'returning'


async def test_multipoints_return_by_support(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        stq,
        get_claim_v2,
        exchange_confirm,
        mock_create_event,
):
    mock_create_event()

    # A -> *B1 -> B2 -> C
    # 1. Confirm point B1 by driver
    # 2. ! Skip point B1! by support
    # Check 'claim.current_point' == B2
    # Check 'claim.status' == pickuped'

    # Pickup code is used to force multipoint segment
    segment_id = await prepare_state(visit_order=2, pickup_code='123456')
    segment = await get_segment(segment_id)
    assert len(segment['points']) == 4, 'Need multipoints segment'

    # 1
    point_b1 = conftest.get_claim_point_id_by_order(segment, visit_order=2)
    await exchange_confirm(
        segment_id, claim_point_id=point_b1, response_code=200,
    )

    # 2
    request_body = {
        'point_id': point_b1,
        'support': {'comment': 'some comment', 'ticket': 'CHATTERBOX-123'},
        'last_known_status': 'delivering',
    }
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200

    # 3
    point_b2 = conftest.get_claim_point_id_by_order(segment, visit_order=3)
    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    assert claim['current_point_id'] == point_b2
    assert claim['status'] == 'pickuped'


async def test_status_pickuped_to_pickuped(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        stq,
        get_claim_v2,
        exchange_confirm,
        mock_create_event,
):
    mock_create_event()

    # *A -> B1 -> B2 -> C
    # 1. Confirm point A
    # 2. Claim status is 'pickuped'
    # 3. Return point B1
    # 4. Check that claim status is 'pickuped'

    # Pickup code is used to force multipoint segment
    segment_id = await prepare_state(visit_order=1, pickup_code='123456')
    segment = await get_segment(segment_id)
    assert len(segment['points']) == 4, 'Need multipoints segment'

    # 1
    point_a = conftest.get_claim_point_id_by_order(segment, visit_order=1)
    await exchange_confirm(
        segment_id, claim_point_id=point_a, response_code=200,
    )
    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    assert claim['status'] == 'pickuped'

    # 2
    point_b1 = conftest.get_claim_point_id_by_order(segment, visit_order=2)
    request_body = {
        'point_id': point_b1,
        'support': {'comment': 'some comment', 'ticket': 'CHATTERBOX-123'},
        'last_known_status': 'delivering',
    }
    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=request_body,
        headers=conftest.get_headers(),
    )
    assert response.status_code == 200

    # 3
    point_b2 = conftest.get_claim_point_id_by_order(segment, visit_order=3)
    claim = await get_claim_v2(segment['diagnostics']['claim_id'])
    assert claim['current_point_id'] == point_b2
    assert claim['status'] == 'pickuped'


@pytest.mark.parametrize('visit_order', [1, 2])
async def test_single_destination_failed(
        taxi_cargo_claims,
        mock_create_event,
        prepare_state,
        get_segment,
        visit_order: int,
):
    mock_create_event()

    segment_id = await prepare_state(visit_order=visit_order)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(segment, visit_order)

    json = {
        'point_id': claim_point_id,
        'last_known_status': conftest.TAXIMETER_STATUS_BY_STATUS[
            segment['status']
        ],
        'reasons': ['reason_a', 'reason_b'],
        'support': {'comment': 'some comment', 'ticket': 'CHATTERBOX-123'},
        'need_return_items': False,
    }

    response = await taxi_cargo_claims.post(
        '/v1/segments/return',
        params={'segment_id': segment_id},
        json=json,
        headers=conftest.get_headers(),
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': 'not_allowed',
        'message': (
            'Недопустимое действие, в заказе всего одна точка назначения'
        ),
    }
