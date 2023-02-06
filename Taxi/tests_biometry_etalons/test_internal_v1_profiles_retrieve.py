import pytest


@pytest.mark.pgsql('biometry_etalons', files=['profiles.sql'])
async def test_internal_v1_profiles_retrieve(
        taxi_biometry_etalons, media_storage,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profiles/retrieve',
        json={
            'provider': 'signalq',
            'profile_ids': ['xxx_yyy', 'yyy_yyy'],
            'urls': {'ttl': 15},
        },
    )

    assert response.status_code == 200

    profiles = response.json()['profiles']
    profiles.sort(key=lambda profile: profile['profile']['id'])

    assert 'temporary_url' in profiles[0]['profile_media']['photo'][0]
    assert 'temporary_url' in profiles[0]['profile_media']['photo'][1]
    assert 'temporary_url' in profiles[1]['profile_media']['photo'][0]

    profiles[0]['profile_media']['photo'][0].pop('temporary_url')
    profiles[0]['profile_media']['photo'][1].pop('temporary_url')
    profiles[1]['profile_media']['photo'][0].pop('temporary_url')

    assert profiles == [
        {
            'profile': {'id': 'xxx_yyy', 'type': 'park_driver_profile_id'},
            'provider': 'signalq',
            'version': 1,
            'profile_meta': {'park_id': '123'},
            'profile_media': {
                'photo': [
                    {
                        'media_id': '1',
                        'meta': {
                            'meta_key_1': 'meta_value_1',
                            'meta_key_2': 'meta_value_2',
                        },
                        'storage_bucket': 'yyy',
                        'storage_id': 'xxx',
                        'storage_type': 'signalq-s3',
                    },
                    {
                        'media_id': '3',
                        'meta': {'meta_key_3': 'meta_value_3'},
                        'storage_bucket': 'yyy2',
                        'storage_id': 'xxx2',
                        'storage_type': 'signalq-s3',
                    },
                ],
            },
        },
        {
            'profile': {'id': 'yyy_yyy', 'type': 'park_driver_profile_id'},
            'provider': 'signalq',
            'version': 2,
            'profile_meta': {'park_id': '123'},
            'profile_media': {
                'photo': [
                    {
                        'media_id': '2',
                        'storage_bucket': 'driver_photo',
                        'storage_id': 'ms0000000000000000000001',
                        'storage_type': 'media-storage',
                    },
                ],
            },
        },
    ]


@pytest.mark.pgsql('biometry_etalons', files=['profiles.sql'])
async def test_internal_v1_profiles_retrieve_with_features(
        taxi_biometry_etalons, media_storage,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profiles/retrieve',
        json={
            'with_features': True,
            'provider': 'signalq',
            'profile_ids': ['xxx_yyy', 'yyy_yyy'],
            'urls': {'ttl': 15},
        },
    )

    assert response.status_code == 200
    profiles = response.json()['profiles']
    assert len(profiles) == 2

    profiles.sort(key=lambda profile: profile['profile']['id'])

    photo = profiles[0]['profile_media']['photo']
    assert len(photo) == 2
    assert photo[0]['face_features'] == {'signalq': [1.1, 1.1, 1.1]}
    assert photo[1]['face_features'] == {
        '/biometrics_features/v1': [4.4, 4.4, 4.4],
        'signalq': [3.3, 3.3, 3.3],
    }

    photo = profiles[1]['profile_media']['photo']
    assert len(photo) == 1
    assert photo[0]['face_features'] == {
        '/biometrics_features/v1': [2.2, 2.2, 2.2],
    }


@pytest.mark.pgsql('biometry_etalons', files=['profiles.sql'])
async def test_internal_v1_profiles_retrieve_without_features(
        taxi_biometry_etalons, media_storage,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profiles/retrieve',
        json={
            'with_features': True,
            'provider': 'signalq',
            'profile_ids': ['www_ttt'],
            'urls': {'ttl': 15},
        },
    )

    assert response.status_code == 200
    profiles = response.json()['profiles']
    assert len(profiles) == 1

    photo = profiles[0]['profile_media']['photo']
    assert len(photo) == 1
    assert 'face_features' not in photo[0]
    assert photo[0]['media_id'] == '5'


@pytest.mark.pgsql('biometry_etalons', files=['profiles.sql'])
async def test_internal_v1_profiles_retrieve_without_media(
        taxi_biometry_etalons, media_storage,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profiles/retrieve',
        json={
            'with_features': True,
            'provider': 'signalq',
            'profile_ids': ['nnn_mmm'],
            'urls': {'ttl': 15},
        },
    )

    assert response.status_code == 200
    profiles = response.json()['profiles']
    assert len(profiles) == 1

    assert 'profile_media' not in profiles[0]
