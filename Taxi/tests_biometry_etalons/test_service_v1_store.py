import pytest


@pytest.mark.parametrize(
    'json, expected_code, expected_response, expected_etalon',
    [
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 1,
                'etalon_media': {
                    'photo': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000005',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            200,
            {},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    2,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    2,
                    'selfie',
                    False,
                ),
                (
                    'ms0000000000000000000003',
                    'driver_photo',
                    2,
                    'voice',
                    False,
                ),
                ('ms0000000000000000000005', 'driver_photo', 2, 'voice', True),
            ],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000002',
                'version': 0,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000012',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            200,
            {},
            [('ms0000000000000000000012', 'driver_photo', 1, 'selfie', True)],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 2,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            409,
            {'code': '409', 'message': 'Conflict by etalon version'},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    1,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    1,
                    'selfie',
                    False,
                ),
                ('ms0000000000000000000003', 'driver_photo', 1, 'voice', True),
            ],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 1,
                'etalon_media': {
                    'photo': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                        },
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            400,
            {'code': '400', 'message': 'Media list contains duplicates'},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    1,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    1,
                    'selfie',
                    False,
                ),
                ('ms0000000000000000000003', 'driver_photo', 1, 'voice', True),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'biometry_etalons', files=['etalons.sql', 'drivers.sql', 'media.sql'],
)
async def test_service_v1_store(
        taxi_biometry_etalons,
        pgsql,
        json,
        expected_code,
        expected_response,
        expected_etalon,
):
    def select_etalon(park_id, driver_profile_id):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT m.media_storage_id, m.media_storage_bucket, e.version, '
            'm.type, m.is_active FROM biometry_etalons.drivers d '
            'INNER JOIN biometry_etalons.etalons e ON e.id = d.etalon_set_id '
            'INNER JOIN biometry_etalons.media m ON '
            'm.etalon_set_id = d.etalon_set_id '
            'WHERE d.park_id = \'{}\' AND d.driver_profile_id = \'{}\' '
            'ORDER BY m.media_storage_id ASC'.format(
                park_id, driver_profile_id,
            ),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_biometry_etalons.post('service/v1/store', json=json)

    assert response.status_code == expected_code
    assert response.json() == expected_response

    pg_etalon = select_etalon(json['park_id'], json['driver_profile_id'])
    assert pg_etalon == expected_etalon


@pytest.mark.parametrize(
    'json, expected_code, expected_response, expected_etalon',
    [
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 1,
                'etalon_media': {
                    'photo': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000005',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            200,
            {},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    2,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    2,
                    'selfie',
                    False,
                ),
                (
                    'ms0000000000000000000003',
                    'driver_photo',
                    2,
                    'voice',
                    False,
                ),
                ('ms0000000000000000000005', 'driver_photo', 2, 'voice', True),
            ],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000002',
                'version': 0,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000012',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            200,
            {},
            [('ms0000000000000000000012', 'driver_photo', 1, 'selfie', True)],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 2,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            409,
            {'code': '409', 'message': 'Conflict by etalon version'},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    1,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    1,
                    'selfie',
                    False,
                ),
                ('ms0000000000000000000003', 'driver_photo', 1, 'voice', True),
            ],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 1,
                'etalon_media': {
                    'photo': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                        },
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            400,
            {'code': '400', 'message': 'Media list contains duplicates'},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    1,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    1,
                    'selfie',
                    False,
                ),
                ('ms0000000000000000000003', 'driver_photo', 1, 'voice', True),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'biometry_etalons', files=['profiles.sql', 'drivers_fake.sql'],
)
@pytest.mark.config(BIOMETRY_ETALONS_PROFILES_DB_USAGE_ENABLE='on')
async def test_service_v1_store_profiles_only(
        taxi_biometry_etalons,
        pgsql,
        json,
        expected_code,
        expected_response,
        expected_etalon,
):
    def select_etalon(park_id, driver_profile_id):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT m.media_storage_id, m.media_storage_bucket, e.version, '
            'm.type, m.is_active FROM biometry_etalons.profiles p '
            'INNER JOIN biometry_etalons.etalons e ON e.id = p.etalon_id '
            'INNER JOIN biometry_etalons.media m ON '
            'm.etalon_set_id = p.etalon_id '
            'WHERE p.profile_id = \'{}_{}\''
            'ORDER BY m.media_storage_id ASC'.format(
                park_id, driver_profile_id,
            ),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_biometry_etalons.post('service/v1/store', json=json)

    assert response.status_code == expected_code
    assert response.json() == expected_response

    pg_etalon = select_etalon(json['park_id'], json['driver_profile_id'])
    assert pg_etalon == expected_etalon


@pytest.mark.parametrize(
    'json, expected_code, expected_response, expected_etalon',
    [
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 1,
                'etalon_media': {
                    'photo': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000005',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            200,
            {},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    2,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    2,
                    'selfie',
                    False,
                ),
                (
                    'ms0000000000000000000003',
                    'driver_photo',
                    2,
                    'voice',
                    False,
                ),
                ('ms0000000000000000000005', 'driver_photo', 2, 'voice', True),
            ],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000002',
                'version': 0,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000012',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            200,
            {},
            [('ms0000000000000000000012', 'driver_photo', 1, 'selfie', True)],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 2,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            409,
            {'code': '409', 'message': 'Conflict by etalon version'},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    1,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    1,
                    'selfie',
                    False,
                ),
                ('ms0000000000000000000003', 'driver_photo', 1, 'voice', True),
            ],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 1,
                'etalon_media': {
                    'photo': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                        },
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            400,
            {'code': '400', 'message': 'Media list contains duplicates'},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    1,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    1,
                    'selfie',
                    False,
                ),
                ('ms0000000000000000000003', 'driver_photo', 1, 'voice', True),
            ],
        ),
    ],
)
@pytest.mark.pgsql('biometry_etalons', files=['drivers_profiles.sql'])
@pytest.mark.config(BIOMETRY_ETALONS_PROFILES_DB_USAGE_ENABLE='tryout')
async def test_service_v1_store_tryout(
        taxi_biometry_etalons,
        pgsql,
        json,
        expected_code,
        expected_response,
        expected_etalon,
):
    def select_etalon_from_profiles(park_id, driver_profile_id):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT m.media_storage_id, m.media_storage_bucket, e.version, '
            'm.type, m.is_active FROM biometry_etalons.profiles p '
            'INNER JOIN biometry_etalons.etalons e ON e.id = p.etalon_id '
            'INNER JOIN biometry_etalons.media m ON '
            'm.etalon_set_id = p.etalon_id '
            'WHERE p.profile_id = \'{}_{}\''
            'ORDER BY m.media_storage_id ASC'.format(
                park_id, driver_profile_id,
            ),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    def select_etalon_from_drivers(park_id, driver_profile_id):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT m.media_storage_id, m.media_storage_bucket, e.version, '
            'm.type, m.is_active FROM biometry_etalons.drivers d '
            'INNER JOIN biometry_etalons.etalons e ON e.id = d.etalon_set_id '
            'INNER JOIN biometry_etalons.media m ON '
            'm.etalon_set_id = d.etalon_set_id '
            'WHERE d.park_id = \'{}\' AND d.driver_profile_id = \'{}\' '
            'ORDER BY m.media_storage_id ASC'.format(
                park_id, driver_profile_id,
            ),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_biometry_etalons.post('service/v1/store', json=json)

    assert response.status_code == expected_code
    assert response.json() == expected_response

    pg_etalon_drivers = select_etalon_from_drivers(
        json['park_id'], json['driver_profile_id'],
    )
    assert pg_etalon_drivers == expected_etalon

    pg_etalon_profiles = select_etalon_from_profiles(
        json['park_id'], json['driver_profile_id'],
    )
    assert pg_etalon_profiles == expected_etalon


@pytest.mark.parametrize(
    'json, expected_code, expected_response, expected_etalon',
    [
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 1,
                'etalon_media': {
                    'photo': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000005',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            200,
            {},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    2,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    2,
                    'selfie',
                    False,
                ),
                (
                    'ms0000000000000000000003',
                    'driver_photo',
                    2,
                    'voice',
                    False,
                ),
                ('ms0000000000000000000005', 'driver_photo', 2, 'voice', True),
            ],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000002',
                'version': 0,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000012',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            200,
            {},
            [('ms0000000000000000000012', 'driver_photo', 1, 'selfie', True)],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 2,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            409,
            {'code': '409', 'message': 'Conflict by etalon version'},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    1,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    1,
                    'selfie',
                    False,
                ),
                ('ms0000000000000000000003', 'driver_photo', 1, 'voice', True),
            ],
        ),
        (
            {
                'source': 'test',
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'version': 1,
                'etalon_media': {
                    'photo': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                        },
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                        },
                    ],
                },
            },
            400,
            {'code': '400', 'message': 'Media list contains duplicates'},
            [
                (
                    'ms0000000000000000000001',
                    'driver_photo',
                    1,
                    'selfie',
                    True,
                ),
                (
                    'ms0000000000000000000002',
                    'driver_photo',
                    1,
                    'selfie',
                    False,
                ),
                ('ms0000000000000000000003', 'driver_photo', 1, 'voice', True),
            ],
        ),
    ],
)
@pytest.mark.pgsql('biometry_etalons', files=['drivers_profiles.sql'])
@pytest.mark.config(BIOMETRY_ETALONS_PROFILES_DB_USAGE_ENABLE='dry-run')
async def test_service_v1_store_dry_run(
        taxi_biometry_etalons,
        pgsql,
        json,
        expected_code,
        expected_response,
        expected_etalon,
):
    def select_etalon_from_profiles(park_id, driver_profile_id):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT m.media_storage_id, m.media_storage_bucket, e.version, '
            'm.type, m.is_active FROM biometry_etalons.profiles p '
            'INNER JOIN biometry_etalons.etalons e ON e.id = p.etalon_id '
            'INNER JOIN biometry_etalons.media m ON '
            'm.etalon_set_id = p.etalon_id '
            'WHERE p.profile_id = \'{}_{}\''
            'ORDER BY m.media_storage_id ASC'.format(
                park_id, driver_profile_id,
            ),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    def select_etalon_from_drivers(park_id, driver_profile_id):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT m.media_storage_id, m.media_storage_bucket, e.version, '
            'm.type, m.is_active FROM biometry_etalons.drivers d '
            'INNER JOIN biometry_etalons.etalons e ON e.id = d.etalon_set_id '
            'INNER JOIN biometry_etalons.media m ON '
            'm.etalon_set_id = d.etalon_set_id '
            'WHERE d.park_id = \'{}\' AND d.driver_profile_id = \'{}\' '
            'ORDER BY m.media_storage_id ASC'.format(
                park_id, driver_profile_id,
            ),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_biometry_etalons.post('service/v1/store', json=json)

    assert response.status_code == expected_code
    assert response.json() == expected_response

    pg_etalon_drivers = select_etalon_from_drivers(
        json['park_id'], json['driver_profile_id'],
    )
    assert pg_etalon_drivers == expected_etalon

    pg_etalon_profiles = select_etalon_from_profiles(
        json['park_id'], json['driver_profile_id'],
    )
    assert pg_etalon_profiles == expected_etalon
