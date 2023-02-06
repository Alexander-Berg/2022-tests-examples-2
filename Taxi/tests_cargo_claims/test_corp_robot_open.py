import datetime

from testsuite.utils import matching


async def test_happy_path(
        taxi_cargo_claims,
        get_default_headers,
        prepare_state,
        get_segment,
        stq,
        mocked_time,
):
    segment_id = await prepare_state(
        visit_order=1, last_exchange_init=False, transport_type='rover',
    )
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/robot/open-request',
        params={'claim_id': claim_id},
        json={'point_id': 1, 'delay': 10},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    assert stq.cargo_orders_open_rover.times_called == 1
    stq_params = stq.cargo_orders_open_rover.next_call()
    assert stq_params['kwargs']['cargo_order_id'] == matching.AnyString()
    assert stq_params['eta'] == mocked_time.now() + datetime.timedelta(
        milliseconds=10000,
    )


async def test_no_performer(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        create_segment,
        get_segment,
):
    claim_info = await create_segment()

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/robot/open-request',
        params={'claim_id': claim_info.claim_id},
        json={'point_id': 1, 'delay': 10},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'no_performer_info',
        'message': 'Исполнитель еще не найден',
    }


async def test_performer_is_not_rover(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        get_segment,
        prepare_state,
):
    segment_id = await prepare_state(
        visit_order=1, last_exchange_init=False, transport_type='car',
    )
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/robot/open-request',
        params={'claim_id': claim_id},
        json={'point_id': 1, 'delay': 10},
        headers=get_default_headers(),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'not_allowed',
        'message': 'Заказ везет не ровер',
    }


async def test_rover_not_arrived_yet(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        get_segment,
        prepare_state,
):
    segment_id = await prepare_state(
        visit_order=1,
        last_exchange_init=False,
        last_arrive_at_point=False,
        transport_type='rover',
    )
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/robot/open-request',
        params={'claim_id': claim_id},
        json={'point_id': 1, 'delay': 10},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'state_mismatch',
        'message': 'Invalid claim action, refresh the page (state_mismatch)',
    }


async def test_wrong_point_id(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        create_segment_with_performer,
        prepare_state,
        get_segment,
        stq,
):
    segment_id = await prepare_state(
        visit_order=1, last_exchange_init=False, transport_type='rover',
    )
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/robot/open-request',
        params={'claim_id': claim_id},
        json={'point_id': 100, 'delay': 10},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'inappropriate_point',
        'message': 'Error occurred. Try to refresh the page',
    }
