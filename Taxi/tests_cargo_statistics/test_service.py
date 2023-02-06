import datetime
NOW = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
NOW_STR = '2020-01-01T00:00:00+00:00'
IN_20_MINUTES = NOW + datetime.timedelta(minutes=20)
IN_20_MINUTES_STR = '2020-01-01T00:20:00+00:00'


async def test_last_timestamp(taxi_cargo_statistics):
    response = await taxi_cargo_statistics.get(
        '/v1/events/last-timestamp?event_group=manual-dispatch/orders',
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_last_timestamp_with_data(
        taxi_cargo_statistics, manual_dispatch_orders,
):
    manual_dispatch_orders.insert_events(
        {
            'corp_client_id': 'corp_client_id',
            'status': 'pending',
            'order_id': 'order_id_1',
            'event_time': '2020-01-01T00:00:00+00:00',
            'event_id': 1,
            'features': {'foo': 'bar'},
            'extra_fields': {'foo_int': 123456},
        },
    )
    assert manual_dispatch_orders.get_events()[0]['event_time'] == NOW
    response = await taxi_cargo_statistics.get(
        '/v1/events/last-timestamp?event_group=manual-dispatch/orders',
    )
    assert response.status_code == 200
    assert response.json() == {'last_timestamp': NOW_STR}


async def test_events_push(taxi_cargo_statistics, manual_dispatch_orders):
    events = [
        {
            'corp_client_id': 'corp_id_1',
            'order_id': 'order_id_1',
            'status': 'pending',
            'event_time': NOW_STR,
            'event_id': 1,
            'features': {'foo': 'bar'},
            'extra_fields': {'foo_int': 123456},
        },
    ]
    response = await taxi_cargo_statistics.post(
        '/v1/events/push?event_group=manual-dispatch/orders',
        json={'events': events},
    )
    assert response.status_code == 200
    manual_dispatch_orders.expect_events(events)

    events = [
        {
            'corp_client_id': None,
            'order_id': 'some_other_order_id',
            'status': 'pending',
            'event_time': IN_20_MINUTES_STR,
            'event_id': 1,
            'features': {'spam': 'eggs'},
            'extra_fields': {'bar_int': 654321, 'foo_int': 654321},
        },
        {
            'corp_client_id': 'corp_id_2',
            'order_id': 'order_id_2',
            'status': 'assigned',
            'event_time': NOW_STR,
            'event_id': 2,
            'features': {'foo': 'bar'},
            'extra_fields': {'foo_int': 123456},
        },
    ]
    response = await taxi_cargo_statistics.post(
        '/v1/events/push?event_group=manual-dispatch/orders',
        json={'events': events},
    )
    assert response.status_code == 200

    events[0]['features']['foo'] = 'bar'
    events[0]['corp_client_id'] = 'corp_id_1'
    manual_dispatch_orders.expect_events(events)
