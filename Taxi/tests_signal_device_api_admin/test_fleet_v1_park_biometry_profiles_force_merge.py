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
    'driver_profile_id, expected_code, expected_response',
    [
        pytest.param('d1', 200, {}, id='ok test'),
        pytest.param(
            'd2',
            404,
            {
                'code': 'driver_not_found',
                'message': 'driver not found in park',
            },
            id='not found test',
        ),
    ],
)
async def test_force_merge(
        taxi_signal_device_api_admin,
        mockserver,
        parks,
        pgsql,
        driver_profile_id,
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
        '/biometry-etalons/internal/biometry-etalons/v1/profile/force-merge',
    )
    def _force_merge(request):
        assert request.json == {
            'provider': 'signalq',
            'merge_from_profile_id': 'pr1',
            'merge_to_profile_id': f'p1_{driver_profile_id}',
        }
        return mockserver.make_response(json={}, status=200)

    parks.set_driver_profiles_response(DRIVER_PROFILES_LIST_RESPONSE)

    response = await taxi_signal_device_api_admin.post(
        'fleet/signal-device-api-admin/v1/park/biometry-profiles/force-merge',
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={'profile_id': 'pr1', 'driver_profile_id': driver_profile_id},
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response

    if expected_code != 200:
        return

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT driver_profile_id, driver_name '
        'FROM signal_device_api.events ',
    )
    db_rows = list(db)
    assert db_rows == [('d1', 'Ivanov Petr D`')]

    db.execute(
        'SELECT driver_detected, driver_detected_name '
        'FROM signal_device_api.status_history '
        'ORDER BY driver_detected ASC',
    )
    db_rows = list(db)
    assert db_rows == [
        ('anonymous_pr2', None),
        ('d1', 'Ivanov Petr D`'),
        ('d1', 'Ivanov Petr D`'),
    ]

    db.execute(
        'SELECT driver_detected, driver_detected_name '
        'FROM signal_device_api.statuses ',
    )
    db_rows = list(db)
    assert db_rows == [('d1', 'Ivanov Petr D`')]
