import pytest

URL = '/internal/v2/profiles/updates'

DEPTRANS_PROFILE_1 = {
    'deptrans_pd_id': '1',
    'driver_id': 'driver1',
    'park_id': 'park1',
    'status': 'approved',
    'updated_ts': '2020-12-30T11:00:00+00:00',
}
DEPTRANS_PROFILE_2 = {
    'driver_id': 'driver1',
    'park_id': 'park3',
    'status': 'temporary_requested',
    'updated_ts': '2020-12-30T11:00:02+00:00',
}
DEPTRANS_PROFILE_3 = {
    'deptrans_pd_id': '3',
    'driver_id': 'driver1',
    'park_id': 'park2',
    'status': 'temporary',
    'updated_ts': '2020-12-30T11:00:02+00:00',
}
DEPTRANS_PROFILE_4 = {
    'deptrans_pd_id': '33',
    'driver_id': 'driver2',
    'park_id': 'park3',
    'status': 'approved',
    'updated_ts': '2020-12-30T11:00:02+00:00',
}
DEPTRANS_PROFILE_5 = {
    'deptrans_pd_id': '33',
    'driver_id': 'driver2',
    'park_id': 'park2',
    'status': 'approved',
    'updated_ts': '2020-12-30T11:00:02+00:00',
}
DEPTRANS_PROFILE_6 = {
    'deptrans_pd_id': '4',
    'driver_id': 'driver1',
    'park_id': 'park3',
    'status': 'temporary',
    'updated_ts': '2020-12-30T11:00:03+00:00',
}
DEPTRANS_PROFILE_7 = {
    'driver_id': 'driver2',
    'park_id': 'park3',
    'status': 'temporary_requested',
    'updated_ts': '2020-12-30T11:00:05+00:00',
}


@pytest.mark.pgsql(
    'deptrans_driver_status',
    files=['deptrans_profiles.sql', 'deptrans_temp_profile_requests.sql'],
)
async def test_basic(taxi_deptrans_driver_status):
    response = await taxi_deptrans_driver_status.get(URL, params={})

    assert response.status_code == 200
    data = response.json()
    assert data['binding'] == [
        DEPTRANS_PROFILE_1,
        DEPTRANS_PROFILE_2,
        DEPTRANS_PROFILE_3,
        DEPTRANS_PROFILE_4,
        DEPTRANS_PROFILE_5,
        DEPTRANS_PROFILE_6,
        DEPTRANS_PROFILE_7,
    ]


@pytest.mark.pgsql(
    'deptrans_driver_status',
    files=['deptrans_profiles.sql', 'deptrans_temp_profile_requests.sql'],
)
async def test_several_calls(taxi_deptrans_driver_status):
    response = await taxi_deptrans_driver_status.get(URL, params={'limit': 4})
    assert response.status_code == 200
    data = response.json()
    assert data['binding'] == [
        DEPTRANS_PROFILE_1,
        DEPTRANS_PROFILE_2,
        DEPTRANS_PROFILE_3,
        DEPTRANS_PROFILE_4,
        DEPTRANS_PROFILE_5,
    ]

    # Second call, use cursor from previous data
    response = await taxi_deptrans_driver_status.get(
        URL, params={'limit': 4, 'cursor': data['cursor']},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['binding'] == [DEPTRANS_PROFILE_6, DEPTRANS_PROFILE_7]

    # Third call, check that cursor not changed
    prev_cursor = data['cursor']
    response = await taxi_deptrans_driver_status.get(
        URL, params={'cursor': prev_cursor},
    )
    assert response.status_code == 200
    data = response.json()
    assert not data['binding']
    assert data['cursor'] == prev_cursor


async def test_invalid_cursor(taxi_deptrans_driver_status):
    response = await taxi_deptrans_driver_status.get(
        URL, params={'cursor': 'random0string'},
    )
    assert response.status_code == 400
    assert 'Invalid cursor' in response.json()['message']
