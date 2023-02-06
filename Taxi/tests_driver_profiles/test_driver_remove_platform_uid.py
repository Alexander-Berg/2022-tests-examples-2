import pytest


@pytest.fixture(name='binding_event_mock')
def _binding_event_mock(testpoint):
    @testpoint('yt-logger-passport-binding-event')
    def _mock(data):
        assert data.pop('timestamp')
        assert data == {
            'event_type': 'unbinding',
            'park_id': 'p1',
            'driver_profile_id': 'd1',
            'passport_uid': '1122334455',
            'performer': 'tech',
            'reason': 'https://st.yandex-team.ru/DUTYTICKET-12345',
        }

    return _mock


async def test_not_found(taxi_driver_profiles):
    response = await taxi_driver_profiles.put(
        '/admin/v1/driver/remove-platform-uid',
        headers={'X-Yandex-Login': 'tech'},
        json={'park_id': 'nonexisent', 'driver_profile_id': 'nonexistent'},
    )

    assert response.status == 404
    assert response.json() == {'code': '404', 'message': 'profile not found'}


async def test_ok(
        taxi_driver_profiles, mockserver, mongodb, binding_event_mock,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        assert body == {
            'park_id': 'p1',
            'change_info': {
                'object_id': 'd1',
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': [
                    {'field': 'platform_uid', 'old': '1122334455', 'new': ''},
                ],
            },
            'author': {
                'dispatch_user_id': '',
                'display_name': 'Techsupport',
                'user_ip': '',
            },
        }
        return {}

    old_mongo_entry = mongodb.dbdrivers.find_one(
        {'park_id': 'p1', 'driver_id': 'd1'},
    )

    response = await taxi_driver_profiles.put(
        '/admin/v1/driver/remove-platform-uid',
        headers={'X-Yandex-Login': 'tech'},
        json={
            'park_id': 'p1',
            'driver_profile_id': 'd1',
            'ticket_url': 'https://st.yandex-team.ru/DUTYTICKET-12345',
        },
    )

    assert response.status == 200

    mongo_entry = mongodb.dbdrivers.find_one(
        {'park_id': 'p1', 'driver_id': 'd1'},
    )
    assert 'platform_uid' not in mongo_entry
    assert mongo_entry['modified_date'] != old_mongo_entry['modified_date']
    assert mongo_entry['updated_ts'] != old_mongo_entry['updated_ts']
    assert binding_event_mock.has_calls


async def test_no_platform_uid(taxi_driver_profiles):
    response = await taxi_driver_profiles.put(
        '/admin/v1/driver/remove-platform-uid',
        headers={'X-Yandex-Login': 'tech'},
        json={'park_id': 'p2', 'driver_profile_id': 'd2'},
    )
    assert response.status == 200
