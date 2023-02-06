async def test_exams_retrieve_by_profiles(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        'v1/driver/exams/retrieve-by-profiles',
        params={'consumer': 'service'},
        json={
            'profile_id_in_set': [
                'park1_driver1',
                'park2_driver2',
                'park_driver_non',
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'exams': [
            {
                'park_driver_profile_id': 'park1_driver1',
                'data': [
                    {'course': 'econom', 'result': 5, 'updated_by': 'support'},
                    {'course': 'business', 'result': 2},
                ],
            },
            {'park_driver_profile_id': 'park2_driver2', 'data': []},
            {'park_driver_profile_id': 'park_driver_non'},
        ],
    }
