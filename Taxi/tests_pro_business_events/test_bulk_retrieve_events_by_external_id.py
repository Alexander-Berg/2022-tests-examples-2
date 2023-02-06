async def test_events_bulk_retrieve_ok(taxi_pro_business_events):
    response = await taxi_pro_business_events.post(
        'internal/events/bulk-retrieve/by-external-ids/v1',
        json={
            'external_ids': [
                {'platform_consumer': 'Market', 'external_id': 'external_id1'},
                {'platform_consumer': 'Market', 'external_id': 'external_id2'},
            ],
        },
    )
    assert response.status == 200
    assert response.json() == {
        'events': [
            {
                'deeplink': 'deeplink_1',
                'event_date': '2001-12-12T10:00:00+00:00',
                'external_id': 'external_id1',
                'id': 'id_1',
                'platform_consumer': 'Market',
                'profile_id': 'profile_id_1',
                'title': 'title_1',
            },
            {
                'deeplink': 'deeplink_2',
                'event_date': '2001-12-12T10:00:00+00:00',
                'external_id': 'external_id2',
                'id': 'id_2',
                'platform_consumer': 'Market',
                'profile_id': 'profile_id_2',
                'title': 'title_2',
            },
        ],
    }


async def test_events_bulk_retrieve_ok_invalid_request(
        taxi_pro_business_events,
):
    response = await taxi_pro_business_events.post(
        'internal/events/bulk-retrieve/by-external-ids/v1',
        json={
            'external_ids': [
                {'external_id': 'external_id1'},
                {'external_id': 'external_id2'},
            ],
        },
    )
    assert response.status == 400


async def test_events_bulk_retrieve_non_existent_ids(taxi_pro_business_events):
    response = await taxi_pro_business_events.post(
        'internal/events/bulk-retrieve/by-external-ids/v1',
        json={
            'external_ids': [
                {'platform_consumer': 'Market', 'external_id': 'Nonexistent'},
                {'platform_consumer': 'Lavka', 'external_id': 'Nonexistent2'},
                {
                    'platform_consumer': 'Nonexistent',
                    'external_id': 'Nonexistent2',
                },
            ],
        },
    )
    assert response.status == 200
    assert response.json() == {'events': []}
