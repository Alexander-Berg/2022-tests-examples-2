import pytest

from tests_signal_device_api_admin import web_common


DRIVER_PROFILES_LIST_RESPONSE = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': 'Petr',
                'middle_name': 'D`',
                'last_name': 'Ivanov',
                'driver_license': {
                    'expiration_date': '2025-08-07T00:00:00+0000',
                    'issue_date': '2015-08-07T00:00:00+0000',
                    'normalized_number': '7723306794',
                    'number': '7723306794',
                },
                'id': 'd1',
                'phones': ['+79265975310'],
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 1,
}


@pytest.mark.pgsql('signal_device_api_meta_db', files=['statuses.sql'])
@pytest.mark.parametrize(
    'driver_profile_id, is_unbound, expected_code, expected_response',
    [
        ('d1', False, 200, {}),
        (
            'd2',
            False,
            400,
            {
                'code': 'driver_not_found',
                'message': 'driver not found in park',
            },
        ),
        ('d1', True, 200, {}),
    ],
)
async def test_unassign(
        taxi_signal_device_api_admin,
        mockserver,
        parks,
        pgsql,
        stq,
        stq_runner,
        driver_profile_id,
        is_unbound,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profile/assign',
    )
    def _assign(request):
        request_parsed = request.json

        assert request_parsed['provider'] == 'signalq'

        assert request_parsed['old_profile'] == {
            'type': 'park_driver_profile',
            'id': 'p1',
        }
        assert request_parsed['new_profile']['type'] == 'anonymous'

        return mockserver.make_response(json={}, status=200)

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/retrieve',
    )
    def _retrieve(request):
        request_parsed = request.json
        assert request_parsed == {'provider': 'signalq', 'profile_ids': ['p1']}

        resp = {
            'profiles': [
                {
                    'provider': 'signalq',
                    'profile': {'id': 'bound_id', 'type': 'anonymous'},
                },
            ],
        }
        if not is_unbound:
            resp['profiles'][0]['profile']['type'] = 'park_driver'
        return resp

    parks.set_driver_profiles_response(DRIVER_PROFILES_LIST_RESPONSE)

    response = await taxi_signal_device_api_admin.post(
        'fleet/signal-device-api-admin/v1/park/biometry-profiles/unassign',
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={'profile_id': 'p1', 'driver_profile_id': driver_profile_id},
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response

    if expected_code != 200:
        assert (
            stq.signal_device_api_admin_unassign_biometry_profile.times_called
            == 0
        )
        return

    assert (
        stq.signal_device_api_admin_unassign_biometry_profile.times_called == 1
    )

    stq_call = (
        stq.signal_device_api_admin_unassign_biometry_profile.next_call()
    )
    await stq_runner.signal_device_api_admin_unassign_biometry_profile.call(
        task_id=stq_call['id'],
        args=stq_call['args'],
        kwargs=stq_call['kwargs'],
    )

    if is_unbound:
        assert _assign.times_called == 0
        return

    assert _assign.times_called == 1

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT driver_profile_id, driver_name '
        'FROM signal_device_api.events ',
    )
    db_rows = list(db)
    assert db_rows == [('anonymous_p1', None)]

    db.execute(
        'SELECT driver_detected, driver_detected_name '
        'FROM signal_device_api.status_history '
        'ORDER BY driver_detected ASC',
    )
    db_rows = list(db)
    assert db_rows == [
        ('anonymous_p1', None),
        ('anonymous_p1', None),
        ('anonymous_p2', None),
    ]

    db.execute(
        'SELECT driver_detected, driver_detected_name '
        'FROM signal_device_api.statuses ',
    )
    db_rows = list(db)
    assert db_rows == [('anonymous_p1', None)]
