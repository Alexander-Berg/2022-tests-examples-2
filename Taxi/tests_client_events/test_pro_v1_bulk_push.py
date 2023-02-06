UNIQUE_DRIVERS_RESPONSE = {
    'profiles': [
        {
            'unique_driver_id': 'udid1',
            'data': [
                {
                    'park_id': 'dbid',
                    'driver_profile_id': 'uuid1',
                    'park_driver_profile_id': 'dbid_uuid1',
                },
                {
                    'park_id': 'dbid',
                    'driver_profile_id': 'uuid2',
                    'park_driver_profile_id': 'dbid_uuid2',
                },
            ],
        },
        {
            'unique_driver_id': 'udid3',
            'data': [
                {
                    'park_id': 'dbid',
                    'driver_profile_id': 'uuid3',
                    'park_driver_profile_id': 'dbid_uuid3',
                },
            ],
        },
    ],
}


async def test_bulk_push_contractor_ids(taxi_client_events, mongodb):
    response = await taxi_client_events.post(
        'pro/v1/bulk-push',
        json={
            'service': 'yandex.pro',
            'event': 'status_changed',
            'event_id': 'hex',
            'ttl': 30,
            'payload': {'hello': 'world'},
            'channels': {'contractor_ids': ['dbid_uuid1', 'dbid_uuid2']},
        },
    )
    assert response.status_code == 200

    event_channels = {
        item['channel']
        for item in mongodb.client_events_events.find(
            {}, {'channel': 1, '_id': 0},
        )
    }
    assert event_channels == {'contractor:dbid_uuid1', 'contractor:dbid_uuid2'}


async def test_bulk_push_unique_contractor_ids(
        taxi_client_events, mockserver, mongodb,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _unique_drivers_retrieve_by_uniques(request):
        assert request.json == {'id_in_set': ['udid1', 'udid3', 'badudid']}

        return UNIQUE_DRIVERS_RESPONSE

    response = await taxi_client_events.post(
        'pro/v1/bulk-push',
        json={
            'service': 'yandex.pro',
            'event': 'status_changed',
            'event_id': 'hex',
            'ttl': 30,
            'payload': {'hello': 'world'},
            'channels': {
                'unique_contractor_ids': ['udid1', 'udid3', 'badudid'],
            },
        },
    )
    assert response.status_code == 200

    event_channels = {
        item['channel']
        for item in mongodb.client_events_events.find(
            {}, {'channel': 1, '_id': 0},
        )
    }
    assert event_channels == {
        'contractor:dbid_uuid1',
        'contractor:dbid_uuid2',
        'contractor:dbid_uuid3',
    }


async def test_bulk_push_no_such_unique_contractor_id(
        taxi_client_events, mockserver, mongodb,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _unique_drivers_retrieve_by_uniques(request):
        assert request.json == {'id_in_set': ['udid']}

        return {'profiles': [{'unique_driver_id': 'udid', 'data': []}]}

    response = await taxi_client_events.post(
        'pro/v1/bulk-push',
        json={
            'service': 'yandex.pro',
            'event': 'status_changed',
            'event_id': 'hex',
            'ttl': 30,
            'payload': {'hello': 'world'},
            'channels': {'unique_contractor_ids': ['udid']},
        },
    )
    assert response.status_code == 200

    events = list(mongodb.client_events_events.find({}))
    assert events == []


async def test_bulk_push_duplicated_contractor_ids(
        taxi_client_events, mongodb, testpoint,
):
    @testpoint('push-event')
    def push_event(data):
        pass

    response = await taxi_client_events.post(
        'pro/v1/bulk-push',
        json={
            'service': 'yandex.pro',
            'event': 'status_changed',
            'event_id': 'hex',
            'ttl': 30,
            'payload': {'hello': 'world'},
            'channels': {'contractor_ids': ['dbid_uuid', 'dbid_uuid']},
        },
    )
    assert response.status_code == 200

    assert push_event.times_called == 1

    event_channels = [
        item['channel']
        for item in mongodb.client_events_events.find(
            {}, {'channel': 1, '_id': 0},
        )
    ]
    assert event_channels == ['contractor:dbid_uuid']
