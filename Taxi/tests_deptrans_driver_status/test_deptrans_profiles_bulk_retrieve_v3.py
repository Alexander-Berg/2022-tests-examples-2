import pytest

URL = '/internal/v3/profiles/bulk-retrieve'

DEPTRANS_PROFILE_1_DID_NOT_NEEDED = {
    'license_pd_id': 'driver_license_pd_id_1',
    'status': 'not_needed',
}
DEPTRANS_PROFILE_1 = {
    'deptrans_pd_id': '1',
    'license_pd_id': 'driver_license_pd_id_1',
    'status': 'approved',
    'updated_ts': '2020-12-30T11:00:08+00:00',
}
DEPTRANS_PROFILE_1_UPDATED = {
    'deptrans_pd_id': '1',
    'license_pd_id': 'driver_license_pd_id_1',
    'status': 'temporary_outdated',
    'updated_ts': '2020-12-30T11:00:10+00:00',
}
DEPTRANS_PROFILE_2 = {
    'license_pd_id': 'driver_license_pd_id_2',
    'status': 'not_needed',
}
DEPTRANS_PROFILE_3 = {
    'deptrans_pd_id': '3',
    'license_pd_id': 'driver_license_pd_id_3',
    'status': 'temporary',
    'updated_ts': '2020-12-30T11:00:03+00:00',
}
DEPTRANS_PROFILE_5 = {
    'license_pd_id': 'driver_license_pd_id_4',
    'status': 'temporary_requested',
    'updated_ts': '2020-12-30T11:00:05+00:00',
}
DEPTRANS_PROFILE_6 = {
    'license_pd_id': 'driver_without_license_pd_id',
    'status': 'not_needed',
}


@pytest.mark.pgsql(
    'deptrans_driver_status',
    files=['deptrans_profiles.sql', 'deptrans_temp_profile_requests.sql'],
)
@pytest.mark.parametrize(
    'license_pd_id,expected',
    [
        ('driver_license_pd_id_1', {'items': [DEPTRANS_PROFILE_1]}),
        ('driver_license_pd_id_2', {'items': [DEPTRANS_PROFILE_2]}),
        ('driver_license_pd_id_3', {'items': [DEPTRANS_PROFILE_3]}),
        ('driver_license_pd_id_4', {'items': [DEPTRANS_PROFILE_5]}),
        ('driver_without_license_pd_id', {'items': [DEPTRANS_PROFILE_6]}),
    ],
)
async def test_status(taxi_deptrans_driver_status, license_pd_id, expected):
    await taxi_deptrans_driver_status.invalidate_caches()
    response = await taxi_deptrans_driver_status.post(
        URL, json={'license_pd_ids': [license_pd_id]},
    )

    assert response.status_code == 200
    assert response.json() == expected


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
    response = await taxi_deptrans_driver_status.post(
        URL,
        json={
            'license_pd_ids': [
                'driver_license_pd_id_1',
                'driver_license_pd_id_2',
                'driver_license_pd_id_3',
                'driver_license_pd_id_4',
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'items': [
            DEPTRANS_PROFILE_1,
            DEPTRANS_PROFILE_2,
            DEPTRANS_PROFILE_3,
            DEPTRANS_PROFILE_5,
        ],
    }


async def invalidate_then_post(taxi_deptrans_driver_status, is_full):
    await taxi_deptrans_driver_status.invalidate_caches(clean_update=is_full)
    response = await taxi_deptrans_driver_status.post(
        URL, json={'license_pd_ids': ['driver_license_pd_id_1']},
    )
    assert response.status_code == 200
    return response.json()


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
    assert await invalidate_then_post(
        taxi_deptrans_driver_status, is_full,
    ) == {'items': [DEPTRANS_PROFILE_1_DID_NOT_NEEDED]}

    pg_deptrans_driver_status.insert_deptrans_profile(
        'driver_license_pd_id_1',
        '1',
        '2020-12-30 14:00:08',
        'approved',
        pgsql,
    )

    assert await invalidate_then_post(
        taxi_deptrans_driver_status, is_full,
    ) == {'items': [DEPTRANS_PROFILE_1]}

    pg_deptrans_driver_status.insert_request_for_profile(
        'park1', 'driver1', '2020-12-30 14:00:09', pgsql,
    )

    assert await invalidate_then_post(
        taxi_deptrans_driver_status, is_full,
    ) == {'items': [DEPTRANS_PROFILE_1]}

    pg_deptrans_driver_status.update_deptrans_profile(
        'driver_license_pd_id_1',
        '1',
        '2020-12-30 14:00:10',
        'temporary_outdated',
        pgsql,
    )

    assert await invalidate_then_post(
        taxi_deptrans_driver_status, is_full,
    ) == {'items': [DEPTRANS_PROFILE_1_UPDATED]}
