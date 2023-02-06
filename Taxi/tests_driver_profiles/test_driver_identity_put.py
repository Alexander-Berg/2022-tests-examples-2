async def test_upsert(taxi_driver_profiles, mongodb):

    park_id = 'p1'
    driver_profile_id = 'd1'

    response = await taxi_driver_profiles.put(
        '/v1/driver/identity',
        params={'park_id': park_id, 'driver_profile_id': driver_profile_id},
        json={
            'author': {
                'consumer': 'qc',
                'identity': {'type': 'job', 'job_name': 'identity_job'},
            },
            'identity': {
                'type': 'passport_rus',
                'data_pd_id': 'data_pd_id_1',
                'number_pd_id': 'number_pd_id_1',
            },
        },
    )

    assert response.status == 200
    assert response.json() == {}

    mongo_entry = list(
        mongodb.identity_docs.find(
            {'park_id': park_id, 'driver_id': driver_profile_id},
        ),
    )

    assert len(mongo_entry) == 1
    assert mongo_entry[0]['number_pd_id'] == 'number_pd_id_1'
    assert mongo_entry[0]['data_pd_id'] == 'data_pd_id_1'

    response = await taxi_driver_profiles.put(
        '/v1/driver/identity',
        params={'park_id': park_id, 'driver_profile_id': driver_profile_id},
        json={
            'author': {
                'consumer': 'qc',
                'identity': {'type': 'job', 'job_name': 'identity_job'},
            },
            'identity': {
                'type': 'passport_rus',
                'data_pd_id': 'data_pd_id_2',
                'number_pd_id': 'number_pd_id_2',
            },
        },
    )

    assert response.status == 200
    assert response.json() == {}

    mongo_entry = list(
        mongodb.identity_docs.find(
            {'park_id': park_id, 'driver_id': driver_profile_id},
        ),
    )

    assert len(mongo_entry) == 1
    assert mongo_entry[0]['number_pd_id'] == 'number_pd_id_2'
    assert mongo_entry[0]['data_pd_id'] == 'data_pd_id_2'


async def test_upsert_different_types(taxi_driver_profiles, mongodb):

    park_id = 'p1'
    driver_profile_id = 'd1'

    response = await taxi_driver_profiles.put(
        '/v1/driver/identity',
        params={'park_id': park_id, 'driver_profile_id': driver_profile_id},
        json={
            'author': {
                'consumer': 'qc',
                'identity': {'type': 'job', 'job_name': 'identity_job'},
            },
            'identity': {
                'type': 'passport_rus',
                'data_pd_id': 'data_pd_id_1',
                'number_pd_id': 'number_pd_id_1',
            },
        },
    )

    assert response.status == 200
    assert response.json() == {}

    mongo_entry = list(
        mongodb.identity_docs.find(
            {'park_id': park_id, 'driver_id': driver_profile_id},
        ),
    )

    assert len(mongo_entry) == 1
    assert mongo_entry[0]['number_pd_id'] == 'number_pd_id_1'
    assert mongo_entry[0]['data_pd_id'] == 'data_pd_id_1'

    response = await taxi_driver_profiles.put(
        '/v1/driver/identity',
        params={'park_id': park_id, 'driver_profile_id': driver_profile_id},
        json={
            'author': {
                'consumer': 'qc',
                'identity': {'type': 'job', 'job_name': 'identity_job'},
            },
            'identity': {
                'type': 'passport_foreign',
                'data_pd_id': 'data_pd_id_2',
                'number_pd_id': 'number_pd_id_2',
            },
        },
    )

    assert response.status == 200
    assert response.json() == {}

    mongo_entry = list(
        mongodb.identity_docs.find(
            {'park_id': park_id, 'driver_id': driver_profile_id},
        ),
    )

    assert len(mongo_entry) == 2
