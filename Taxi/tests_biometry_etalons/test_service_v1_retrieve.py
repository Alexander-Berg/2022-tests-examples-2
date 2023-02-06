import pytest


@pytest.mark.parametrize(
    'json, expected_response',
    [
        (
            {
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
            },
            {
                'version': 1,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                },
            },
        ),
        (
            {
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'urls': {'ttl': 5},
            },
            {
                'version': 1,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                            'url': 'http://selfie/001',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                            'url': 'http://voice/003',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                },
            },
        ),
        (
            {
                'park_id': 'park00000000000000000002',
                'driver_profile_id': 'driver000000000000000002',
            },
            {'version': 1, 'etalon_media': {}},
        ),
        (
            {
                'park_id': 'park00000000000000000003',
                'driver_profile_id': 'driver000000000000000003',
            },
            {'version': 0, 'etalon_media': {}},
        ),
    ],
)
@pytest.mark.pgsql(
    'biometry_etalons', files=['etalons.sql', 'drivers.sql', 'media.sql'],
)
async def test_service_v1_retrieve(
        taxi_biometry_etalons, media_storage, json, expected_response,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')
    media_storage.set_url('ms0000000000000000000003', 'http://voice/003')

    response = await taxi_biometry_etalons.post(
        'service/v1/retrieve', json=json,
    )

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'json, expected_response',
    [
        (
            {
                'park_id': 'park00000000000000000003',
                'driver_profile_id': 'driver000000000000000003',
            },
            {
                'version': 2,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                },
            },
        ),
        (
            {
                'park_id': 'park00000000000000000003',
                'driver_profile_id': 'driver000000000000000003',
                'urls': {'ttl': 5},
            },
            {
                'version': 2,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                            'url': 'http://selfie/001',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                            'url': 'http://voice/003',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                },
            },
        ),
        (
            {
                'park_id': 'park00000000000000000004',
                'driver_profile_id': 'driver000000000000000004',
            },
            {'version': 1, 'etalon_media': {}},
        ),
        (
            {
                'park_id': 'park00000000000000000002',
                'driver_profile_id': 'driver000000000000000002',
            },
            {'version': 0, 'etalon_media': {}},
        ),
    ],
)
@pytest.mark.pgsql(
    'biometry_etalons', files=['drivers_fake.sql', 'profiles.sql'],
)
async def test_service_v1_retrieve_dry_run(
        taxi_biometry_etalons, media_storage, json, expected_response,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')
    media_storage.set_url('ms0000000000000000000003', 'http://voice/003')

    response = await taxi_biometry_etalons.post(
        'service/v1/retrieve', json=json,
    )

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'json, expected_response',
    [
        (
            {
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
            },
            {
                'version': 1,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                },
            },
        ),
        (
            {
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'urls': {'ttl': 5},
            },
            {
                'version': 1,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                            'url': 'http://selfie/001',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                            'url': 'http://voice/003',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                },
            },
        ),
        (
            {
                'park_id': 'park00000000000000000002',
                'driver_profile_id': 'driver000000000000000002',
            },
            {'version': 1, 'etalon_media': {}},
        ),
        (
            {
                'park_id': 'park00000000000000000003',
                'driver_profile_id': 'driver000000000000000003',
            },
            {'version': 0, 'etalon_media': {}},
        ),
    ],
)
@pytest.mark.pgsql(
    'biometry_etalons', files=['drivers_fake.sql', 'profiles.sql'],
)
@pytest.mark.config(BIOMETRY_ETALONS_PROFILES_DB_USAGE_ENABLE='on')
async def test_service_v1_retrieve_from_profiles(
        taxi_biometry_etalons, media_storage, json, expected_response,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')
    media_storage.set_url('ms0000000000000000000003', 'http://voice/003')

    response = await taxi_biometry_etalons.post(
        'service/v1/retrieve', json=json,
    )

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'json, expected_response',
    [
        (
            {
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
            },
            {
                'version': 1,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                },
            },
        ),
        (
            {
                'park_id': 'park00000000000000000001',
                'driver_profile_id': 'driver000000000000000001',
                'urls': {'ttl': 5},
            },
            {
                'version': 1,
                'etalon_media': {
                    'selfie': [
                        {
                            'storage_id': 'ms0000000000000000000001',
                            'storage_bucket': 'driver_photo',
                            'url': 'http://selfie/001',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                    'voice': [
                        {
                            'storage_id': 'ms0000000000000000000003',
                            'storage_bucket': 'driver_photo',
                            'url': 'http://voice/003',
                            'created': '2019-04-10T07:00:00+00:00',
                        },
                    ],
                },
            },
        ),
        (
            {
                'park_id': 'park00000000000000000002',
                'driver_profile_id': 'driver000000000000000002',
            },
            {'version': 1, 'etalon_media': {}},
        ),
        (
            {
                'park_id': 'park00000000000000000003',
                'driver_profile_id': 'driver000000000000000003',
            },
            {'version': 0, 'etalon_media': {}},
        ),
    ],
)
@pytest.mark.pgsql(
    'biometry_etalons', files=['drivers_fake.sql', 'profiles.sql'],
)
@pytest.mark.config(BIOMETRY_ETALONS_PROFILES_DB_USAGE_ENABLE='tryout')
async def test_service_v1_retrieve_tryout(
        taxi_biometry_etalons, media_storage, json, expected_response,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')
    media_storage.set_url('ms0000000000000000000003', 'http://voice/003')

    response = await taxi_biometry_etalons.post(
        'service/v1/retrieve', json=json,
    )

    assert response.status_code == 200
    assert response.json() == expected_response
