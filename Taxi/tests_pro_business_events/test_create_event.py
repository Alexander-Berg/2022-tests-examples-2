async def test_create_event_ok(taxi_pro_business_events):
    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1?external_id=market_123',
        json={
            'profile_id': '12',
            'title': 'Courier Shift',
            'deeplink': 'sample/link',
            'event_date': '2001-12-12T10:00:00Z',
        },
        headers={'X-Platform-Consumer': 'Market'},
    )
    assert 'id' in response.json()


async def test_create_event_ok_empty_deeplink(taxi_pro_business_events):
    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1?external_id=market_123',
        json={
            'profile_id': '12',
            'title': 'Courier Shift',
            'event_date': '2001-12-12T10:00:00Z',
        },
        headers={'X-Platform-Consumer': 'Market'},
    )
    assert 'id' in response.json()


async def test_create_event_invalid_request(taxi_pro_business_events):
    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1?external_id=market_123',
        json={'profile_id': '12', 'invalid_field': 'invalid_value'},
        headers={'X-Platform-Consumer': 'Market'},
    )
    assert response.status == 400


async def test_create_event_no_query_param(taxi_pro_business_events):
    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1',
        json={
            'profile_id': '12',
            'title': 'Courier Shift',
            'deeplink': 'sample/link',
            'event_date': '2001-12-12T10:00:00Z',
        },
        headers={'X-Platform-Consumer': 'Market'},
    )
    assert response.status == 400


async def test_create_event_invalid_date(taxi_pro_business_events):
    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1?external_id=market_123',
        json={
            'profile_id': '12',
            'title': 'Courier Shift',
            'deeplink': 'sample/link',
            'event_date': 'invalid_date',
        },
        headers={'X-Platform-Consumer': 'Market'},
    )
    assert response.status == 400


async def test_create_event_change_event(taxi_pro_business_events, pgsql):
    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1?external_id=market_123',
        json={
            'profile_id': '12',
            'title': 'Courier Shift',
            'deeplink': 'sample/link',
            'event_date': '2001-12-12T10:00:00Z',
        },
        headers={'X-Platform-Consumer': 'Market'},
    )
    assert 'id' in response.json()

    cursor = pgsql['pro_business_events'].cursor()
    cursor.execute('SELECT * from pro_business_events.events')
    db_events = list(row for row in cursor)
    inserted_event = db_events[0]
    assert inserted_event[1] == '12'
    assert inserted_event[2] == 'Courier Shift'

    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1?external_id=market_123',
        json={
            'profile_id': '13',
            'title': 'New Courier Shift',
            'deeplink': 'sample/link',
            'event_date': '2001-12-12T10:00:00Z',
        },
        headers={'X-Platform-Consumer': 'Market'},
    )
    assert 'id' in response.json()

    cursor.execute('SELECT * from pro_business_events.events')
    db_events = list(row for row in cursor)
    inserted_event = db_events[0]
    assert inserted_event[1] == '13'
    assert inserted_event[2] == 'New Courier Shift'


async def test_create_event_different_platform_consumers(
        taxi_pro_business_events, pgsql,
):
    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1?external_id=123',
        json={
            'profile_id': '12',
            'title': 'Courier Shift',
            'deeplink': 'sample/link',
            'event_date': '2001-12-12T10:00:00Z',
        },
        headers={'X-Platform-Consumer': 'Market'},
    )

    assert 'id' in response.json()

    response = await taxi_pro_business_events.put(
        'platform/v1/events/v1?external_id=123',
        json={
            'profile_id': '13',
            'title': 'New Courier Shift',
            'deeplink': 'sample/link',
            'event_date': '2001-12-12T10:00:00Z',
        },
        headers={'X-Platform-Consumer': 'Lavka'},
    )

    assert 'id' in response.json()
