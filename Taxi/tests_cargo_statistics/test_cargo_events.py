NOW_STR = '2020-01-01T12:00:00+00:00'


async def test_cargo_orders(taxi_cargo_statistics, cargo_orders_orders):
    events = [
        {
            'event_time': NOW_STR,
            'event_id': 1,
            'order_id': 'order_id_1',
            'provider_order_id': 'order-uuid-1',
            'provider_user_id': 'user_id_1',
            'features': {'foo': 'bar'},
            'extra_fields': {'foo_int': 123456},
        },
    ]
    response = await taxi_cargo_statistics.post(
        '/v1/events/push?event_group=cargo-orders/orders',
        json={'events': events},
    )
    assert response.status_code == 200
    cargo_orders_orders.expect_events(events)


async def test_cargo_claims_claims(taxi_cargo_statistics, cargo_claims_claims):
    events = [
        {
            'event_time': NOW_STR,
            'event_id': 1,
            'claim_uuid': 'claim_uuid_1',
            'corp_client_id': 'corp_client_id_1',
            'status': 'some_status',
            'features': {'foo': 'bar'},
            'extra_fields': {'foo_int': 123456},
        },
    ]
    response = await taxi_cargo_statistics.post(
        '/v1/events/push?event_group=cargo-claims/claims',
        json={'events': events},
    )
    assert response.status_code == 200
    cargo_claims_claims.expect_events(events)


async def test_cargo_claims_segments(
        taxi_cargo_statistics, cargo_claims_segments,
):
    events = [
        {
            'claim_uuid': 'claim_uuid_2',
            'event_id': 1,
            'event_time': NOW_STR,
            'extra_fields': {},
            'features': {},
            'segment_id': 1,
            'segment_uuid': 'segment_1',
            'status': 'new',
        },
        {
            'claim_uuid': 'claim_uuid_2',
            'event_id': 2,
            'event_time': NOW_STR,
            'extra_fields': {},
            'features': {},
            'segment_id': 2,
            'segment_uuid': 'segment_2',
            'status': 'new',
        },
    ]
    response = await taxi_cargo_statistics.post(
        '/v1/events/push?event_group=cargo-claims/segments',
        json={'events': events},
    )
    assert response.status_code == 200
    cargo_claims_segments.expect_events(events)


async def test_cargo_dispatch_segments(
        taxi_cargo_statistics, cargo_dispatch_segments,
):
    events = [
        {
            'event_time': NOW_STR,
            'event_id': 1,
            'claim_id': 'claim_uuid_1',
            'segment_id': 'segment_id_1',
            'waybill_building_version': 1,
            'status': 'some_status',
            'chosen_waybill': 'waybill_1',
            'features': {'foo': 'bar'},
            'extra_fields': {'foo_int': 123456},
        },
    ]
    response = await taxi_cargo_statistics.post(
        '/v1/events/push?event_group=cargo-dispatch/segments',
        json={'events': events},
    )
    assert response.status_code == 200
    cargo_dispatch_segments.expect_events(events)


async def test_cargo_dispatch_waybills(
        taxi_cargo_statistics, cargo_dispatch_waybills,
):
    events = [
        {
            'event_time': NOW_STR,
            'event_id': 1,
            'cargo_order_id': '"9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
            'taxi_order_id': 'claim_uuid_1',
            'external_ref': 'segment_id_1',
            'status': 'some_status',
            'features': {'foo': 'bar'},
            'extra_fields': {'foo_int': 123456},
        },
    ]
    response = await taxi_cargo_statistics.post(
        '/v1/events/push?event_group=cargo-dispatch/waybills',
        json={'events': events},
    )
    assert response.status_code == 200
    cargo_dispatch_waybills.expect_events(events)
