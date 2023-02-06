async def test_events_bulk_retrieve_ok(taxi_pro_business_events):
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
    assert response.status == 200
    event_id = response.json()['id']
    response_events = await taxi_pro_business_events.post(
        'internal/events/bulk-retrieve/v1',
        json={'ids': [response.json()['id']]},
    )
    assert response_events.status == 200

    events = response_events.json()['events']
    assert len(events) == 1
    assert events[0] == {
        'id': event_id,
        'profile_id': '12',
        'title': 'Courier Shift',
        'deeplink': 'sample/link',
        'external_id': 'market_123',
        'event_date': '2001-12-12T10:00:00+00:00',
        'platform_consumer': 'Market',
    }


async def test_events_bulk_retrieve_invalid_request(taxi_pro_business_events):
    response_events = await taxi_pro_business_events.post(
        'internal/events/bulk-retrieve/v1', json={'ids': 'invalid_ids'},
    )
    assert response_events.status == 400


async def test_events_bulk_retrieve_multiple_ids(taxi_pro_business_events):
    response_events = await taxi_pro_business_events.post(
        'internal/events/bulk-retrieve/v1',
        json={'ids': ['id_1', 'id_2', 'id_3']},
    )
    assert response_events.status == 200

    events = response_events.json()['events']
    assert len(events) == 3
    assert events[0]['id'] == 'id_1'
    assert events[1]['id'] == 'id_2'
    assert events[2]['id'] == 'id_3'


async def test_events_bulk_retrieve_non_existent_id(taxi_pro_business_events):
    response_events = await taxi_pro_business_events.post(
        'internal/events/bulk-retrieve/v1', json={'ids': ['id_5']},
    )
    assert response_events.status == 200

    events = response_events.json()['events']
    assert events == []


async def test_events_bulk_retrieve_multiple_ids_with_non_existent(
        taxi_pro_business_events,
):
    response_events = await taxi_pro_business_events.post(
        'internal/events/bulk-retrieve/v1',
        json={'ids': ['id_1', 'id_2', 'id_5']},
    )
    assert response_events.status == 200

    events = response_events.json()['events']
    assert len(events) == 2
    assert events[0]['id'] == 'id_1'
    assert events[1]['id'] == 'id_2'
