import pytest


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 2,
    },
)
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
        (12, 'delivered', 'delivered_finish', 'success', 'visited', 'skipped'),
        (14, 'returned', 'returned_finish', 'failed', 'skipped', 'visited'),
    ),
)
async def test_c2c_claim_processing_event_statuses(
        procaas_send_settings,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        state_controller,
        taxi_cargo_claims,
        query_processing_events,
        current_status_index,
        current_status,
        expected_status,
        resolution,
        point_2_status,
        point_3_status,
):
    await procaas_send_settings()
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    state_controller.use_create_version('v2_cargo_c2c')
    state_controller.set_options(multipoints=False)
    claim_info = await state_controller.apply(target_status=current_status)
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

    c2c_claim_origin = 'yandexgo'
    events = query_processing_events(claim_id)
    assert len(events) == current_status_index
    assert events[0].payload == {
        'data': {
            'claim_uuid': claim_id,
            'is_terminal': False,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'new',
    }
    assert events[1].payload['data'].pop('claim_revision') > 0
    assert events[1].payload == {
        'data': {
            'calc_id': 'cargo-pricing/v1/123',
            'total_price': '999.001',
            'phoenix_claim': False,
        },
        'kind': 'price-changed',
        'status': 'accepted',
    }
    assert events[2].payload['data'].pop('claim_revision') > 0
    assert events[2].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'claim_origin': c2c_claim_origin,
            'claim_accepted': True,
            'skip_client_notify': False,
            'accept_as_create_event': False,
            'accept_language': 'ru',
            'claim_version': 1,
            'offer_id': 'cargo-pricing/v1/123',
            'notify_pricing_claim_accepted': True,
        },
        'kind': 'status-change-requested',
        'status': 'accepted',
    }
    assert events[3].payload['data'].pop('claim_revision') > 0
    assert events[3].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_lookup',
    }
    assert events[4].payload['data'].pop('claim_revision') > 0
    assert events[4].payload == {
        'data': {
            'driver_profile_id': 'driver_id1',
            'park_id': 'park_id1',
            'is_terminal': False,
            'current_point_id': 1,
            'phoenix_claim': False,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_found',
    }
    assert events[5].payload['data'].pop('claim_revision') > 0
    assert events[5].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'pickup_arrived',
    }
    assert events[6].payload['data'].pop('claim_revision') > 0
    assert events[6].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'ready_for_pickup_confirmation',
    }
    assert events[7].payload['data'].pop('claim_revision') > 0
    assert events[7].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 1,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'pickuped',
    }
    assert events[8].payload['data'].pop('claim_revision') > 0
    assert events[8].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 2,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'delivery_arrived',
    }

    status = (
        'returning'
        if current_status == 'returned'
        else 'ready_for_delivery_confirmation'
    )
    assert events[9].payload['data'].pop('claim_revision') > 0
    assert events[9].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 2,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': status,
    }

    status = 'return_arrived' if current_status == 'returned' else 'delivered'
    assert events[10].payload['data'].pop('claim_revision') > 0
    assert events[10].payload == {
        'data': {
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 3 if current_status == 'returned' else 2,
            'claim_origin': c2c_claim_origin,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': status,
    }

    if current_status == 'returned':
        assert events[11].payload['data'].pop('claim_revision') > 0
        assert events[11].payload == {
            'data': {
                'phoenix_claim': False,
                'is_terminal': False,
                'current_point_id': 3,
                'claim_origin': c2c_claim_origin,
                'skip_client_notify': False,
            },
            'kind': 'status-change-succeeded',
            'status': 'ready_for_return_confirmation',
        }
        assert events[12].payload['data'].pop('claim_revision') > 0
        assert events[12].payload == {
            'data': {
                'phoenix_claim': False,
                'is_terminal': False,
                'current_point_id': 3,
                'claim_origin': c2c_claim_origin,
                'skip_client_notify': False,
            },
            'kind': 'status-change-succeeded',
            'status': 'returned',
        }

    assert (
        events[current_status_index - 1].payload['data'].pop('claim_revision')
        > 0
    )
    assert events[current_status_index - 1].payload == {
        'data': {
            'park_id': 'park_id1',
            'phoenix_claim': False,
            'is_terminal': True,
            'resolution': resolution,
            'driver_profile_id': 'driver_id1',
            'claim_origin': c2c_claim_origin,
            'route_points': [
                {
                    'claim_point_id': 1,
                    'id': 1000,
                    'coordinates': {'lat': 55.8, 'lon': 37.2},
                    'visit_status': 'visited',
                    'point_type': 'source',
                },
                {
                    'claim_point_id': 2,
                    'id': 1001,
                    'coordinates': {'lat': 55.8, 'lon': 37.0},
                    'visit_status': point_2_status,
                    'point_type': 'destination',
                },
                {
                    'claim_point_id': 3,
                    'id': 1002,
                    'coordinates': {'lat': 55.5, 'lon': 37.0},
                    'visit_status': point_3_status,
                    'point_type': 'return',
                },
            ],
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': expected_status,
    }
