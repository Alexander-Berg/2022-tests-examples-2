import pytest

from .. import utils_v2


@pytest.mark.parametrize(
    ('current_status', 'expected_status'),
    (('delivered', 'delivered_finish'), ('returned', 'returned_finish')),
)
async def test_success_mark(
        taxi_cargo_claims,
        state_controller,
        check_taxi_order_change,
        current_status: str,
        expected_status: str,
):
    claim_info = await state_controller.apply(target_status=current_status)
    claim_uuid = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-complete',
        params={'claim_id': claim_uuid},
        json={
            'taxi_order_id': 'taxi_order_id_1',
            'reason': 'some_reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'id': claim_uuid, 'status': expected_status}

    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == expected_status

    check_taxi_order_change(
        claim_uuid=claim_uuid,
        taxi_order_id='taxi_order_id_1',
        reason='some_reason',
        new_status=expected_status,
    )


async def test_old_taxi_order_id(taxi_cargo_claims, create_default_claim):
    response = await taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-complete',
        params={'claim_id': create_default_claim.claim_id},
        json={
            'taxi_order_id': 'taxi_order_id_old',
            'reason': 'reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 409


async def test_not_found(taxi_cargo_claims):
    response = await taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-complete',
        params={'claim_id': '1'},
        json={
            'taxi_order_id': '12345',
            'reason': 'reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 404


async def test_dragon_order(
        taxi_cargo_claims, create_segment_with_performer, state_controller,
):
    segment = await create_segment_with_performer()
    await state_controller.apply(target_status='delivered', fresh_claim=False)
    response = await taxi_cargo_claims.post(
        '/v1/claims/mark/taxi-order-complete',
        params={'claim_id': f'order/{segment.cargo_order_id}'},
        json={
            'taxi_order_id': 'taxi_order_id',
            'reason': 'some_reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'current_status',
    (
        'delivered_finish',
        'returned_finish',
        'cancelled_with_items_on_hands',
        'cancelled',
        'cancelled_with_payment',
    ),
)
async def test_terminal_statuses(
        taxi_cargo_claims,
        state_controller,
        get_default_headers,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        current_status: str,
):
    state_controller.use_create_version('v2')
    if current_status == 'cancelled_with_items_on_hands':
        state_controller.handlers().create.request = (
            utils_v2.get_create_request(optional_return=True)
        )
        claim_info = await state_controller.apply(
            target_status=current_status, next_point_order=2,
        )
    else:
        claim_info = await state_controller.apply(target_status=current_status)

    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        '/v1/claims/mark/taxi-order-complete',
        params={'claim_id': claim_id},
        json={
            'taxi_order_id': 'taxi_order_id_1',
            'reason': 'some_reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'terminal_status'


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.parametrize(
    (
        'current_status_index',
        'current_status',
        'expected_status',
        'resolution',
        'point_2_status',
        'point_3_status',
    ),
    (
        (11, 'delivered', 'delivered_finish', 'success', 'visited', 'skipped'),
        (13, 'returned', 'returned_finish', 'failed', 'skipped', 'visited'),
    ),
)
async def test_complete_status_procaas_event(
        taxi_cargo_claims,
        state_controller,
        create_segment_with_performer,
        pgsql,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        changedestinations,
        current_status_index: int,
        current_status: str,
        expected_status: str,
        resolution: str,
        point_2_status: str,
        point_3_status: str,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    changedestinations(taxi_order_id='taxi_order_id')
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        DELETE FROM cargo_claims.processing_events
        """,
    )

    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status=current_status, fresh_claim=False,
    )
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-complete',
        params={'claim_id': claim_id},
        json={
            'taxi_order_id': 'taxi_order_id',
            'reason': 'some_reason',
            'lookup_version': 1,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'id': claim_id, 'status': expected_status}

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT id, payload FROM cargo_claims.processing_events
        WHERE item_id = '{claim_id}'
        """,
    )

    data = list(cursor)
    assert len(data) == current_status_index
    (new_index, new_payload) = data[0]
    assert new_index == 1
    assert new_payload == {
        'data': {
            'claim_uuid': claim_id,
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'is_terminal': False,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'new',
    }

    (terminal_index, terminal_payload) = data[current_status_index - 1]
    assert terminal_index == current_status_index
    assert 'claim_revision' in terminal_payload['data']
    del terminal_payload['data']['claim_revision']
    assert terminal_payload == {
        'data': {
            'cargo_order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'park_id': 'park_id1',
            'phoenix_claim': False,
            'is_terminal': True,
            'resolution': resolution,
            'route_points': [
                {
                    'claim_point_id': 1,
                    'id': 1000,
                    'coordinates': {'lat': 55.7, 'lon': 37.5},
                    'visit_status': 'visited',
                    'point_type': 'source',
                },
                {
                    'claim_point_id': 2,
                    'id': 1001,
                    'coordinates': {'lat': 55.6, 'lon': 37.6},
                    'visit_status': point_2_status,
                    'point_type': 'destination',
                },
                {
                    'claim_point_id': 3,
                    'id': 1002,
                    'coordinates': {'lat': 55.4, 'lon': 37.8},
                    'visit_status': point_3_status,
                    'point_type': 'return',
                },
            ],
            'driver_profile_id': 'driver_id1',
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': expected_status,
    }


@pytest.mark.config(
    CARGO_TAXI_ORDER_COMPLETE_SETTINGS={'use_master_after_wrong_status': True},
)
@pytest.mark.parametrize(
    ('use_master', 'current_status'),
    ((True, 'performer_found'), (False, 'delivered')),
)
async def test_use_master_field(
        taxi_cargo_claims,
        testpoint,
        state_controller,
        use_master: bool,
        current_status: str,
):
    claim_info = await state_controller.apply(target_status=current_status)
    claim_id = claim_info.claim_id

    @testpoint('select-cut-claim-use-master')
    def should_use_master(data):
        return data

    await taxi_cargo_claims.post(
        '/v1/claims/mark/taxi-order-complete',
        params={'claim_id': claim_id},
        json={
            'taxi_order_id': 'taxi_order_id',
            'reason': 'some_reason',
            'lookup_version': 1,
        },
    )
    assert should_use_master.times_called == use_master
