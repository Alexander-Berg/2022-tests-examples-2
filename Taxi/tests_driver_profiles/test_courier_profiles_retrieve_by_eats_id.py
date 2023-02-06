async def test_no_request_in_projection(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        '/v1/courier/profiles/retrieve_by_eats_id',
        json={'eats_courier_id_in_set': ['eats_id_1', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'courier_by_eats_id': [
            {
                'eats_courier_id': 'eats_id_1',
                'profiles': [
                    {
                        'data': {
                            'email_pd_ids': [],
                            'external_ids': {'eats': 'eats_id_1'},
                            'full_name': {
                                'first_name': 'Иван',
                                'last_name': 'Иванов',
                                'middle_name': 'Иванович',
                            },
                            'orders_provider': {
                                'eda': True,
                                'lavka': False,
                                'taxi': False,
                                'taxi_walking_courier': False,
                            },
                            'park_id': 'park_id_1',
                            'phone_pd_ids': [],
                            'uuid': 'driver_id_1',
                            'is_readonly': True,
                        },
                        'park_driver_profile_id': 'park_id_1_driver_id_1',
                        'revision': '0_1_1',
                    },
                ],
            },
            {'eats_courier_id': 'unknown', 'profiles': []},
        ],
    }


async def test_is_readonly_in_projection(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        '/v1/courier/profiles/retrieve_by_eats_id',
        json={
            'eats_courier_id_in_set': ['eats_id_1', 'unknown'],
            'projection': ['data.is_readonly'],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'courier_by_eats_id': [
            {
                'eats_courier_id': 'eats_id_1',
                'profiles': [
                    {
                        'data': {'is_readonly': True},
                        'park_driver_profile_id': 'park_id_1_driver_id_1',
                    },
                ],
            },
            {'eats_courier_id': 'unknown', 'profiles': []},
        ],
    }
