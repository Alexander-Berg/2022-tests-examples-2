import pytest

ENDPOINT = 'v1/driver/profiles/retrieve_by_license_pd_ids'


@pytest.mark.config(TVM_ENABLED=False)
async def test_ok(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        ENDPOINT,
        params={'consumer': 'service'},
        json={'id_in_set': ['driver_license_pd_id_1']},
    )

    expected_response = {
        'profiles': [
            {
                'license_pd_id': 'driver_license_pd_id_1',
                'data': [
                    {
                        'park_driver_profile_id': 'park1_driver1',
                        'park_id': 'park1',
                        'driver_profile_id': 'driver1',
                    },
                ],
            },
        ],
    }
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(TVM_ENABLED=False)
async def test_with_unknown_license_id(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        ENDPOINT,
        params={'consumer': 'service'},
        json={
            'id_in_set': [
                'driver_license_pd_id_2',
                'unknown_driver_license_pd_id',
                'driver_license_pd_id_3',
            ],
        },
    )

    expected_response = {
        'profiles': [
            {
                'license_pd_id': 'driver_license_pd_id_2',
                'data': [
                    {
                        'park_driver_profile_id': 'park2_driver2',
                        'park_id': 'park2',
                        'driver_profile_id': 'driver2',
                    },
                ],
            },
            {'license_pd_id': 'unknown_driver_license_pd_id', 'data': []},
            {
                'license_pd_id': 'driver_license_pd_id_3',
                'data': [
                    {
                        'park_driver_profile_id': 'park2_driver3',
                        'park_id': 'park2',
                        'driver_profile_id': 'driver3',
                    },
                ],
            },
        ],
    }
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(TVM_ENABLED=False)
async def test_with_deleted_driver_profile(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        ENDPOINT,
        params={'consumer': 'service'},
        json={
            'id_in_set': [
                'driver_license_pd_id_1',
                'driver_license_pd_id_4',
                'driver_license_pd_id_2',
            ],
        },
    )

    expected_response = {
        'profiles': [
            {
                'license_pd_id': 'driver_license_pd_id_1',
                'data': [
                    {
                        'park_driver_profile_id': 'park1_driver1',
                        'park_id': 'park1',
                        'driver_profile_id': 'driver1',
                    },
                ],
            },
            {'license_pd_id': 'driver_license_pd_id_4', 'data': []},
            {
                'license_pd_id': 'driver_license_pd_id_2',
                'data': [
                    {
                        'park_driver_profile_id': 'park2_driver2',
                        'park_id': 'park2',
                        'driver_profile_id': 'driver2',
                    },
                ],
            },
        ],
    }
    assert response.status_code == 200
    assert response.json() == expected_response
