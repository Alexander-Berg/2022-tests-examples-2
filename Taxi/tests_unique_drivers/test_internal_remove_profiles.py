import bson


async def test_remove_unique(taxi_unique_drivers, mongodb):
    unique_driver = mongodb.unique_drivers.find_one(
        {'_id': bson.ObjectId('000000000000000000000100')},
    )
    assert unique_driver

    response = await taxi_unique_drivers.post(
        '/internal/unique-drivers/v1/remove-profiles',
        json={'profile_id_in_set': ['park111_driver111']},
        headers={'X-Yandex-Login': 'd-ulitin'},
        params={'consumer': 'pro-profiles-removal'},
    )
    assert response.status_code == 200

    unique_driver = mongodb.unique_drivers.find_one(
        {'_id': bson.ObjectId('000000000000000000000100')},
    )
    assert not unique_driver

    # try to remove removed unique
    response = await taxi_unique_drivers.post(
        '/internal/unique-drivers/v1/remove-profiles',
        json={'profile_id_in_set': ['park111_driver111']},
        headers={'X-Yandex-Login': 'd-ulitin'},
        params={'consumer': 'pro-profiles-removal'},
    )
    assert response.status_code == 200


async def test_do_nothing(taxi_unique_drivers, mongodb):
    unique_driver = mongodb.unique_drivers.find_one(
        {'_id': bson.ObjectId('000000000000000000000200')},
    )
    assert unique_driver

    response = await taxi_unique_drivers.post(
        '/internal/unique-drivers/v1/remove-profiles',
        json={'profile_id_in_set': ['park211_driver211']},
        headers={'X-Yandex-Login': 'd-ulitin'},
        params={'consumer': 'pro-profiles-removal'},
    )
    assert response.status_code == 200

    unique_driver = mongodb.unique_drivers.find_one(
        {'_id': bson.ObjectId('000000000000000000000200')},
    )
    assert unique_driver


async def test_divide_unique(taxi_unique_drivers, mongodb):
    unique_driver = mongodb.unique_drivers.find_one(
        {'_id': bson.ObjectId('000000000000000000000300')},
    )
    assert unique_driver
    assert unique_driver['license_ids'] == [
        {'id': 'driver_license_pd_id_311'},
        {'id': 'driver_license_pd_id_312'},
    ]

    response = await taxi_unique_drivers.post(
        '/internal/unique-drivers/v1/remove-profiles',
        json={'profile_id_in_set': ['park311_driver311']},
        headers={'X-Yandex-Login': 'd-ulitin'},
        params={'consumer': 'pro-profiles-removal'},
    )
    assert response.status_code == 200

    unique_driver = mongodb.unique_drivers.find_one(
        {'_id': bson.ObjectId('000000000000000000000300')},
    )
    assert unique_driver
    assert unique_driver['license_ids'] == [{'id': 'driver_license_pd_id_312'}]
    assert len([*mongodb.unique_drivers.find({})]) == 3

    # try to divide or remove divided unique
    response = await taxi_unique_drivers.post(
        '/internal/unique-drivers/v1/remove-profiles',
        json={'profile_id_in_set': ['park311_driver311']},
        headers={'X-Yandex-Login': 'd-ulitin'},
        params={'consumer': 'pro-profiles-removal'},
    )
    assert response.status_code == 200


async def test_all_together(taxi_unique_drivers, mongodb):
    response = await taxi_unique_drivers.post(
        '/internal/unique-drivers/v1/remove-profiles',
        json={
            'profile_id_in_set': [
                'park111_driver111',
                'park211_driver211',
                'park311_driver311',
            ],
        },
        headers={'X-Yandex-Login': 'd-ulitin'},
        params={'consumer': 'pro-profiles-removal'},
    )
    assert response.status_code == 200

    unique_driver = mongodb.unique_drivers.find_one(
        {'_id': bson.ObjectId('000000000000000000000100')},
    )
    assert not unique_driver
