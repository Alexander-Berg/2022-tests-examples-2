import pytest

URL = '/internal/v3/profiles/updates'

DEPTRANS_PROFILE_1 = {
    'deptrans_pd_id': '1',
    'license_pd_id': 'driver_license_pd_id_1',
    'status': 'approved',
    'updated_ts': '2020-12-30T11:00:00+00:00',
}
DEPTRANS_PROFILE_3 = {
    'deptrans_pd_id': '3',
    'license_pd_id': 'driver_license_pd_id_3',
    'status': 'temporary',
    'updated_ts': '2020-12-30T11:00:03+00:00',
}
DEPTRANS_PROFILE_5 = {
    'deptrans_pd_id': '5',
    'license_pd_id': 'driver_license_pd_id_5',
    'status': 'temporary',
    'updated_ts': '2020-12-30T11:00:05+00:00',
}
DEPTRANS_PROFILE_6 = {
    'license_pd_id': 'driver_license_pd_id_4',
    'status': 'temporary_requested',
    'updated_ts': '2020-12-30T11:00:06+00:00',
}
DEPTRANS_PROFILE_8 = {
    'deptrans_pd_id': '8',
    'license_pd_id': 'driver_license_pd_id_8',
    'status': 'approved',
    'updated_ts': '2020-12-30T11:00:08+00:00',
}
DEPTRANS_PROFILE_9 = {
    'license_pd_id': 'driver_license_pd_id_9',
    'status': 'temporary_requested',
    'updated_ts': '2020-12-30T11:00:09+00:00',
}
DEPTRANS_PROFILE_8_UPDATED = {
    'deptrans_pd_id': '8',
    'license_pd_id': 'driver_license_pd_id_8',
    'status': 'temporary_outdated',
    'updated_ts': '2020-12-30T11:00:10+00:00',
}


@pytest.mark.pgsql(
    'deptrans_driver_status',
    files=['deptrans_profiles.sql', 'deptrans_temp_profile_requests.sql'],
)
async def test_basic(taxi_deptrans_driver_status):
    await taxi_deptrans_driver_status.invalidate_caches()
    response = await taxi_deptrans_driver_status.get(URL, params={})

    assert response.status_code == 200
    data = response.json()
    assert data['binding'] == [
        DEPTRANS_PROFILE_1,
        DEPTRANS_PROFILE_3,
        DEPTRANS_PROFILE_5,
        DEPTRANS_PROFILE_6,
    ]


@pytest.mark.pgsql(
    'deptrans_driver_status',
    files=['deptrans_profiles.sql', 'deptrans_temp_profile_requests.sql'],
)
async def test_several_calls(taxi_deptrans_driver_status):
    await taxi_deptrans_driver_status.invalidate_caches()
    response = await taxi_deptrans_driver_status.get(URL, params={'limit': 2})
    assert response.status_code == 200
    data = response.json()
    assert data['binding'] == [DEPTRANS_PROFILE_1, DEPTRANS_PROFILE_3]

    # Second call, use cursor from previous data
    response = await taxi_deptrans_driver_status.get(
        URL, params={'limit': 2, 'cursor': data['cursor']},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['binding'] == [DEPTRANS_PROFILE_5, DEPTRANS_PROFILE_6]

    # Third call, check that cursor not changed
    prev_cursor = data['cursor']
    response = await taxi_deptrans_driver_status.get(
        URL, params={'cursor': data['cursor']},
    )
    assert response.status_code == 200
    data = response.json()
    assert not data['binding']
    assert data['cursor'] == prev_cursor


async def test_invalid_cursor(taxi_deptrans_driver_status):
    await taxi_deptrans_driver_status.invalidate_caches()
    response = await taxi_deptrans_driver_status.get(
        URL, params={'cursor': 'random0string'},
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'deptrans_driver_status',
    files=['deptrans_profiles.sql', 'deptrans_temp_profile_requests.sql'],
)
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_PROFILES_CACHE_SETTINGS={
        'profiles_limit': 1,
        'requests_limit': 1,
    },
)
async def test_small_limits(taxi_deptrans_driver_status):
    await taxi_deptrans_driver_status.invalidate_caches()
    response = await taxi_deptrans_driver_status.get(URL, params={})

    assert response.status_code == 200
    data = response.json()
    assert data['binding'] == [
        DEPTRANS_PROFILE_1,
        DEPTRANS_PROFILE_3,
        DEPTRANS_PROFILE_5,
        DEPTRANS_PROFILE_6,
    ]


async def invalidate_then_get(taxi_deptrans_driver_status, is_full):
    await taxi_deptrans_driver_status.invalidate_caches(clean_update=is_full)
    response = await taxi_deptrans_driver_status.get(URL, params={})
    assert response.status_code == 200
    return response.json()['binding']


@pytest.mark.parametrize('is_full', [True, False])
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_PROFILES_CACHE_SETTINGS={
        'profiles_limit': 2,
        'requests_limit': 2,
    },
)
async def test_update_cache(
        taxi_deptrans_driver_status, is_full, pg_deptrans_driver_status, pgsql,
):
    assert (
        await invalidate_then_get(taxi_deptrans_driver_status, is_full) == []
    )

    pg_deptrans_driver_status.insert_deptrans_profile(
        'driver_license_pd_id_8',
        '8',
        '2020-12-30 14:00:08',
        'approved',
        pgsql,
    )

    assert await invalidate_then_get(taxi_deptrans_driver_status, is_full) == [
        DEPTRANS_PROFILE_8,
    ]

    pg_deptrans_driver_status.insert_request_for_profile(
        'park3', 'driver5', '2020-12-30 14:00:09', pgsql,
    )

    assert await invalidate_then_get(taxi_deptrans_driver_status, is_full) == [
        DEPTRANS_PROFILE_8,
        DEPTRANS_PROFILE_9,
    ]

    pg_deptrans_driver_status.update_deptrans_profile(
        'driver_license_pd_id_8',
        '8',
        '2020-12-30 14:00:10',
        'temporary_outdated',
        pgsql,
    )

    assert await invalidate_then_get(taxi_deptrans_driver_status, is_full) == [
        DEPTRANS_PROFILE_9,
        DEPTRANS_PROFILE_8_UPDATED,
    ]
