import pytest

from tests_driver_weariness import weariness_tools


UNIQUE_DRIVERS_SOME_ARE_INCORRECT = {
    'licenses_by_unique_drivers': {
        'last_revision': '777_1',
        'items': [
            {
                'id': 'udriver',
                'is_deleted': False,
                'revision': '777_1',
                'data': {'license_ids': ['license_1', 'license_2']},
            },
            # Don't know why, but the second udid needed to load first to cache
            {
                'id': 'udriver2',
                'is_deleted': False,
                'revision': '776_2',
                'data': {'license_ids': ['license_3']},
            },
        ],
    },
    'license_by_driver_profile': {
        'last_revision': '779_2',
        'items': [
            {
                'id': 'parkid_driverid',
                'is_deleted': False,
                'revision': '776_2',
                'data': {'license_id': 'license_1'},
            },
            {
                'id': 'parkid_driverid_INCORRECT',
                'is_deleted': False,
                'revision': '777_1',
                'data': {'license_id': 'license_2'},
            },
            {
                'id': 'parkid_driveridother',
                'is_deleted': False,
                'revision': '775_3',
                'data': {'license_id': 'license_3'},
            },
        ],
    },
}


@pytest.mark.now('2021-02-19T19:00:00+0300')
@pytest.mark.unique_drivers(stream=UNIQUE_DRIVERS_SOME_ARE_INCORRECT)
@pytest.mark.pgsql(
    'drivers_status_ranges', files=['pg_working_ranges_with_incorrect.sql'],
)
@pytest.mark.experiments3(filename='exp3_config_default.json')
async def test_drivers_profiles_filtration(
        taxi_driver_weariness, mockserver, experiments3,
):
    profiles_sent = []

    @mockserver.json_handler('/contractor-status-history/extended-events')
    def _mock_csh_events(request):
        for contractor in request.json['contractors']:
            profiles_sent.append(
                contractor['park_id'] + '_' + contractor['profile_id'],
            )
        return {'contractors': []}

    weariness_tools.add_experiment(
        experiments3, weariness_tools.WearinessConfig(20, 19, 13),
    )
    await taxi_driver_weariness.invalidate_caches(clean_update=True)

    response = await taxi_driver_weariness.get(
        'v1/admin/driver-weariness', params={'unique_driver_id': 'udriver'},
    )
    assert response.status_code == 200
    assert profiles_sent == ['parkid_driverid']
