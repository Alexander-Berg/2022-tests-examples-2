import pytest

URL = '/internal/v1/profiles/bulk-retrieve'

DEPTRANS_PROFILE_1 = {
    'deptrans_pd_id': '1',
    'driver_id': 'driver1',
    'park_id': 'park1',
    'status': 'approved',
    'updated_ts': '2020-12-30T11:00:08+00:00',
}
DEPTRANS_PROFILE_2 = {
    'deptrans_pd_id': '2',
    'driver_id': 'driver2',
    'park_id': 'park1',
    'status': 'missing',
    'updated_ts': '2020-12-30T11:00:01+00:00',
}
DEPTRANS_PROFILE_3 = {
    'deptrans_pd_id': '3',
    'driver_id': 'driver1',
    'park_id': 'park2',
    'status': 'temporary',
    'updated_ts': '2020-12-30T11:00:03+00:00',
}
DEPTRANS_PROFILE_4 = {
    'driver_id': 'driver2',
    'park_id': 'park2',
    'status': 'missing',
}
DEPTRANS_PROFILE_5 = {
    'driver_id': 'driver2',
    'park_id': 'park3',
    'status': 'temporary_requested',
    'updated_ts': '2020-12-30T11:00:05+00:00',
}
DEPTRANS_PROFILE_6 = {
    'driver_id': 'driver_without_license_pd_id',
    'park_id': 'park3',
    'status': 'not_needed',
}


@pytest.mark.pgsql(
    'deptrans_driver_status',
    files=['deptrans_profiles.sql', 'deptrans_temp_profile_requests.sql'],
)
@pytest.mark.parametrize(
    'park_id,driver_id,expected',
    [
        ('park1', 'driver1', {'items': [DEPTRANS_PROFILE_1]}),
        ('park1', 'driver2', {'items': [DEPTRANS_PROFILE_2]}),
        ('park2', 'driver1', {'items': [DEPTRANS_PROFILE_3]}),
        ('park2', 'driver2', {'items': [DEPTRANS_PROFILE_4]}),
        ('park3', 'driver2', {'items': [DEPTRANS_PROFILE_5]}),
        (
            'park3',
            'driver_without_license_pd_id',
            {'items': [DEPTRANS_PROFILE_6]},
        ),
    ],
)
async def test_status(
        taxi_deptrans_driver_status, park_id, driver_id, expected,
):
    response = await taxi_deptrans_driver_status.post(
        URL, json={'items': [{'park_id': park_id, 'driver_id': driver_id}]},
    )

    assert response.status_code == 200
    assert response.json() == expected
