import pytest


@pytest.fixture(name='binding_event_mock')
def _binding_event_mock(testpoint):
    @testpoint('yt-logger-passport-binding-event')
    def _mock(data):
        assert data.pop('timestamp')
        assert data.pop('park_id') in ['p1', 'p2']
        assert data == {
            'event_type': 'binding',
            'driver_profile_id': 'd1',
            'phone_pd_id': '1111',
            'passport_uid': '123456789',
            'performer': 'testsuite',
            'reason': 'test',
        }

    return _mock


async def test_empty(taxi_driver_profiles):
    response = await taxi_driver_profiles.put(
        '/v1/driver/platform-uid-bulk',
        params={'consumer': 'testsuite'},
        json={
            'phone_pd_id': '1111',
            'platform_uid': '123456789',
            'profiles': [],
        },
    )

    assert response.status == 200
    assert response.json() == {'profiles': []}


async def test_not_found(taxi_driver_profiles):
    response = await taxi_driver_profiles.put(
        '/v1/driver/platform-uid-bulk',
        params={'consumer': 'testsuite'},
        json={
            'phone_pd_id': '1111',
            'platform_uid': '123456789',
            'profiles': [
                {'park_id': 'nonexisent', 'driver_profile_id': 'nonexistent'},
            ],
        },
    )

    assert response.status == 200
    assert response.json() == {'profiles': []}


async def test_ok(taxi_driver_profiles, mongodb, binding_event_mock):
    old_mongo_entry = mongodb.dbdrivers.find_one(
        {'park_id': 'p1', 'driver_id': 'd1'},
    )

    response = await taxi_driver_profiles.put(
        '/v1/driver/platform-uid-bulk',
        params={'consumer': 'testsuite'},
        json={
            'phone_pd_id': '1111',
            'platform_uid': '123456789',
            'reason': 'test',
            'profiles': [
                {'park_id': 'p1', 'driver_profile_id': 'd1'},
                {'park_id': 'p2', 'driver_profile_id': 'd1'},
                {'park_id': 'p3', 'driver_profile_id': 'd1'},
                {'park_id': 'p4', 'driver_profile_id': 'd1'},
            ],
        },
    )

    assert response.status == 200
    data = response.json()
    assert data['profiles']
    assert sorted(data['profiles'], key=lambda x: x['park_id']) == [
        {'park_id': 'p1', 'driver_profile_id': 'd1'},
        {'park_id': 'p2', 'driver_profile_id': 'd1'},
    ]

    mongo_entry = mongodb.dbdrivers.find_one(
        {'park_id': 'p1', 'driver_id': 'd1'},
    )
    assert mongo_entry['platform_uid'] == '123456789'
    assert mongo_entry['modified_date'] != old_mongo_entry['modified_date']
    assert mongo_entry['updated_ts'] != old_mongo_entry['updated_ts']
    assert binding_event_mock.has_calls


@pytest.mark.filldb(dbdrivers='all')
async def test_all_updated(taxi_driver_profiles, mongodb, binding_event_mock):
    response = await taxi_driver_profiles.put(
        '/v1/driver/platform-uid-bulk',
        params={'consumer': 'testsuite'},
        json={
            'phone_pd_id': '1111',
            'platform_uid': '123456789',
            'reason': 'test',
            'profiles': [
                {'park_id': 'p1', 'driver_profile_id': 'd1'},
                {'park_id': 'p2', 'driver_profile_id': 'd1'},
            ],
        },
    )

    assert response.status == 200
    assert response.json() == {
        'profiles': [
            {'park_id': 'p1', 'driver_profile_id': 'd1'},
            {'park_id': 'p2', 'driver_profile_id': 'd1'},
        ],
    }
    assert binding_event_mock.has_calls
