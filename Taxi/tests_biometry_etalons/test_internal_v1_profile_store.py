import copy
import hashlib

import numpy as np
import pytest


FACE = hashlib.md5(b'face').hexdigest()

FACE_ROTATED = hashlib.md5(b'face_rotated').hexdigest()

NO_FACE = hashlib.md5(b'NO_FACE').hexdigest()

BASE_RESPONSE = {'cbirdaemon': {'info': '853x480', 'info_orig': '853x480'}}

FACE_FEATURES = {
    'CenterX': 0.793369,
    'CenterY': 0.525597,
    'Width': 0.265323,
    'Height': 0.51058,
    'Confidence': 1.68036,
    'Angle': -0.8321325183,
    'Features': np.full((256,), 1 / np.sqrt(256)).tolist(),
    'Landmarks': [
        {'Y': 147.8375244, 'X': 440.8726807},
        {'Y': 146.7093964, 'X': 360.7087097},
        {'Y': 338.6501465, 'X': 408.8861694},
        {'Y': 480.0557251, 'X': 457.8555298},
        {'Y': 482.3573608, 'X': 350.3559875},
    ],
}

FACE_FEATURES_ROTATED = {
    'CenterX': 0.793369,
    'CenterY': 0.525597,
    'Width': 0.265323,
    'Height': 0.51058,
    'Confidence': 1.68036,
    'Angle': -0.8321325183,
    'Features': np.full((256,), 1 / np.sqrt(256)).tolist(),
    'Landmarks': [
        {'Y': 480.0557251, 'X': 457.8555298},
        {'Y': 482.3573608, 'X': 350.3559875},
        {'Y': 338.6501465, 'X': 408.8861694},
        {'Y': 147.8375244, 'X': 440.8726807},
        {'Y': 146.7093964, 'X': 360.7087097},
    ],
}

BIOMETRICS_FEATURES_V1_RESPONSE_DETECTED = {
    'is_face_ok': True,
    'is_face_detected': True,
    'feature': np.full((256,), 1 / np.sqrt(256)).tolist(),
}

BIOMETRICS_FEATURES_V1_RESPONSE_NOT_DETECTED = {
    'is_face_ok': True,
    'is_face_detected': False,
    'feature': None,
}


def _insert_profile():
    return (
        'INSERT INTO biometry_etalons.profiles ('
        'id, profile_id, profile_type, provider, '
        'idempotency_token, etalon_id'
        ') VALUES ('
        '\'x\', \'xxx_yyy\', \'park_driver_profile_id\','
        '\'signalq\', \'unique_token\', \'000000000000000000000002\');'
    )


@pytest.fixture(autouse=True)
def cbir_features_service(mockserver):
    @mockserver.json_handler('/cbir-features/images-apphost/cbir-features')
    # pylint: disable=unused-variable
    def cbir_features_handler(request):
        request_data = str(request.get_data())
        response = copy.deepcopy(BASE_RESPONSE)

        if FACE_ROTATED in request_data:
            response['cbirdaemon']['similarnn'] = {
                'FaceFeatures': [FACE_FEATURES_ROTATED],
            }
        elif FACE in request_data:
            response['cbirdaemon']['similarnn'] = {
                'FaceFeatures': [FACE_FEATURES],
            }

        return response


@pytest.fixture(autouse=True)
def biometrics_features_v1_service(mockserver):
    @mockserver.json_handler(
        '/biometrics-features/images-apphost/biometrics-features',
    )
    # pylint: disable=unused-variable
    def biometrics_features_v1_handler(request):
        request_data = str(request.get_data())
        if NO_FACE in request_data:
            return BIOMETRICS_FEATURES_V1_RESPONSE_NOT_DETECTED
        return BIOMETRICS_FEATURES_V1_RESPONSE_DETECTED


# Not checking 501-s
@pytest.mark.parametrize(
    'has_face, rotated, provider, calculator, expected_code, expected_error',
    [
        (True, False, 'signalq', '/biometrics_features/v1', 200, {}),
        (
            False,
            False,
            'signalq',
            '/biometrics_features/v1',
            400,
            {
                'code': 'NO_FACE',
                'message': (
                    'Couldn\'t extract face features. '
                    'Is there an ok face on the photo?'
                ),
            },
        ),
        (
            True,
            True,
            'signalq',
            'cbir',
            400,
            {'code': 'IMAGE_ROTATED', 'message': 'Image rotated'},
        ),
    ],
)
@pytest.mark.config(
    TVM_ENABLED=False,
    TVM_RULES=[{'src': 'biometry-etalons', 'dst': 'plotva-ml'}],
    TVM_SERVICES={
        'biometry-etalons': 2345,
        'plotva-ml': 2016315,
        'statistics': 1337,
        'media-storage': 228,
        'saas-searchproxy': 322,
    },
    BIOMETRY_ETALONS_S3_URLS={
        's3_internal_url': {'$mockserver': ''},
        's3_private_url': {'$mockserver': ''},
    },
    BIOMETRY_ETALONS_CBIR_URL={
        '$mockserver': '/cbir-features/images-apphost/cbir-features',
    },
    BIOMETRY_ETALONS_BIOMETRICS_FEATURES_V1_URL={
        '$mockserver': (
            '/biometrics-features/images-apphost/biometrics-features'
        ),
    },
    BIOMETRY_ETALONS_FACE_FEATURES_HANDLERS={
        '__default__': 'cbir',
        'signalq': '/biometrics_features/v1',
    },
)
async def test_internal_v1_profile_store(
        taxi_biometry_etalons,
        taxi_config,
        pgsql,
        mockserver,
        has_face,
        rotated,
        provider,
        calculator,
        expected_code,
        expected_error,
):
    taxi_config.set_values(
        {
            'BIOMETRY_ETALONS_FACE_FEATURES_HANDLERS': {
                '__default__': calculator,
            },
        },
    )
    await taxi_biometry_etalons.invalidate_caches()

    @mockserver.handler('/v1/xxx/photos/123', prefix=True)
    def _mock_s3(request):
        if has_face:
            if rotated:
                return mockserver.make_response(FACE_ROTATED, 200)
            return mockserver.make_response(FACE, 200)
        return mockserver.make_response(NO_FACE, 200)

    def _select_profile(idempotency_token):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT p.profile_id, p.profile_type, p.provider, p.meta, '
            'm.media_storage_id, m.media_storage_bucket, '
            'm.media_storage_type, e.version FROM biometry_etalons.profiles p '
            'INNER JOIN biometry_etalons.etalons e ON p.etalon_id = e.id '
            'INNER JOIN biometry_etalons.face_features f ON '
            'f.etalon_id = e.id '
            'INNER JOIN biometry_etalons.media m ON '
            'm.id = f.media_id',
        )
        result = list(row for row in cursor)
        cursor.close()
        assert len(result) == 1
        return result[0]

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/store',
        headers={'X-Idempotency-Token': 'someCorrectToken'},
        json={
            'provider': provider,
            'profile_meta': {'park_id': '123', 'test': 45},
            'media': {
                'photo': [
                    {
                        'storage_id': 'v1/xxx/photos/123',
                        'storage_type': 'signalq-s3',
                        'storage_bucket': 'sda-photos',
                        'calculate_cbir_features': True,
                    },
                ],
            },
        },
    )
    assert response.status_code == expected_code
    if expected_code == 400:
        assert response.json() == expected_error
        return
    if expected_code == 200:
        profile = _select_profile('someCorrectToken')
        profile_id = profile[0]
        profile_type = profile[1]
        provider = profile[2]
        meta = profile[3]
        storage_id = profile[4]
        storage_bucket = profile[5]
        storage_type = profile[6]
        etalon_version = profile[7]
        assert profile_type == 'anonymous'
        assert provider == 'signalq'
        assert meta == {'park_id': '123', 'test': 45}
        assert storage_id == 'v1/xxx/photos/123'
        assert storage_bucket == 'sda-photos'
        assert storage_type == 'signalq-s3'
        assert etalon_version == 1
        assert response.json() == {
            'profile': {'id': profile_id, 'type': profile_type},
        }


@pytest.mark.pgsql(
    'biometry_etalons', files=['etalons.sql', 'drivers.sql', 'media.sql'],
)
@pytest.mark.parametrize(
    'etalon, expected_code, expected_error',
    [
        ({'id': '000000000000000000000001', 'version': 1}, 200, {}),
        (
            {'id': 'my_etalon42', 'version': 1},
            400,
            {
                'code': 'unknown_etalon',
                'message': 'Etalon with specified id not found',
            },
        ),
        (
            {'id': '000000000000000000000001', 'version': 0},
            400,
            {
                'code': 'etalon_version_changed',
                'message': 'Requested version: 0 differs from actual: 1',
            },
        ),
    ],
)
async def test_internal_v1_profile_add_to_etalon(
        taxi_biometry_etalons,
        pgsql,
        mockserver,
        etalon,
        expected_code,
        expected_error,
):
    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/store',
        headers={'X-Idempotency-Token': 'someCorrectToken'},
        json={
            'provider': 'signalq',
            'profile_meta': {'park_id': '123', 'test': 45},
            'etalon': etalon,
            'profile': {'id': 'test', 'type': 'lol'},
        },
    )
    assert response.status_code == expected_code
    if expected_code == 400:
        assert response.json() == expected_error
        return
    if expected_code == 200:
        cursor = pgsql['biometry_etalons'].cursor()
        etalon_id = etalon['id']
        cursor.execute(
            'SELECT profile_id, profile_type FROM '
            'biometry_etalons.profiles '
            f'WHERE etalon_id=\'{etalon_id}\'',
        )
        result = list(row for row in cursor)
        cursor.close()
        assert result[0][0] == 'test'
        assert result[0][1] == 'lol'


@pytest.mark.pgsql(
    'biometry_etalons', files=['etalons.sql', 'drivers.sql', 'media.sql'],
)
@pytest.mark.parametrize(
    'etalon, expected_code, expected_error',
    [({'id': '000000000000000000000001', 'version': 1}, 200, {})],
)
async def test_internal_v1_profile_add_to_etalon_idemp_violation(
        taxi_biometry_etalons,
        pgsql,
        mockserver,
        etalon,
        expected_code,
        expected_error,
):
    cursor = pgsql['biometry_etalons'].cursor()
    cursor.execute(_insert_profile())
    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/store',
        headers={'X-Idempotency-Token': 'unique_token'},
        json={
            'provider': 'signalq',
            'profile_meta': {'park_id': '123', 'test': 45},
            'etalon': etalon,
            'profile': {'id': 'test', 'type': 'lol'},
        },
    )
    assert response.status_code == expected_code
    assert response.json() == {
        'profile': {'id': 'xxx_yyy', 'type': 'park_driver_profile_id'},
    }


@pytest.mark.pgsql(
    'biometry_etalons', files=['etalons.sql', 'drivers.sql', 'media.sql'],
)
async def test_internal_v1_profile_created_with_another_data(
        taxi_biometry_etalons, pgsql, mockserver,
):
    request_body = {
        'provider': 'signalq',
        'profile': {'id': 'test', 'type': 'lol'},
        'media': {},
    }

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/store',
        headers={'X-Idempotency-Token': 'unique_token'},
        json=request_body,
    )
    assert response.status_code == 200

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/store',
        headers={'X-Idempotency-Token': 'unique_token'},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {'profile': {'id': 'test', 'type': 'lol'}}

    request_body['profile']['id'] = 'test-fake-dupl'
    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/store',
        headers={'X-Idempotency-Token': 'unique_token'},
        json=request_body,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'BAD_REQUEST',
        'message': (
            'Request profile field=profile_id mismatched '
            'with the stored one. field value from request: '
            'test-fake-dupl, stored field value: test'
        ),
    }


@pytest.mark.parametrize(
    'json, expected_code, expected_response, expected_etalon',
    [
        (
            {
                'provider': 'taxi',
                'profile': {
                    'id': 'park00000000000000000001_driver000000000000000001',
                    'type': 'park_driver_profile_id',
                },
                'version': 1,
                'media': {
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
                'provider': 'taxi',
                'profile': {
                    'id': 'park00000000000000000001_driver000000000000000002',
                    'type': 'park_driver_profile_id',
                },
                'version': 0,
                'media': {
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
                'provider': 'taxi',
                'profile': {
                    'id': 'park00000000000000000001_driver000000000000000001',
                    'type': 'park_driver_profile_id',
                },
                'version': 2,
                'media': {
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
                'provider': 'taxi',
                'profile': {
                    'id': 'park00000000000000000001_driver000000000000000001',
                    'type': 'park_driver_profile_id',
                },
                'version': 1,
                'media': {
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
@pytest.mark.pgsql('biometry_etalons', files=['profiles.sql'])
async def test_internal_profile_store(
        taxi_biometry_etalons,
        pgsql,
        json,
        expected_code,
        expected_response,
        expected_etalon,
):
    def select_etalon(profile_id):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(
            'SELECT m.media_storage_id, m.media_storage_bucket, e.version, '
            'm.type, m.is_active FROM biometry_etalons.profiles p '
            'INNER JOIN biometry_etalons.etalons e ON e.id = p.etalon_id '
            'INNER JOIN biometry_etalons.media m ON '
            'm.etalon_set_id = p.etalon_id '
            'WHERE p.profile_id = \'{}\''
            'ORDER BY m.media_storage_id ASC'.format(profile_id),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/store',
        headers={'X-Idempotency-Token': 'very_unique_token'},
        json=json,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'profile': json['profile']}

    pg_etalon = select_etalon(json['profile']['id'])
    assert pg_etalon == expected_etalon


@pytest.mark.pgsql('biometry_etalons', files=['profiles.sql'])
async def test_internal_v1_profile_store_media_meta(
        taxi_biometry_etalons, pgsql, mockserver,
):
    @mockserver.handler('/v1/xxx/photos/123', prefix=True)
    def _mock_s3(request):
        return mockserver.make_response(FACE, 200)

    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profile/store',
        headers={'X-Idempotency-Token': 'someCorrectToken'},
        json={
            'provider': 'taxi',
            'profile': {
                'id': 'park00000000000000000001_driver000000000000000001',
                'type': 'park_driver_profile_id',
            },
            'version': 1,
            'media': {
                'photo': [
                    {
                        'storage_id': 'storage_id_1',
                        'storage_bucket': 'bucket_photos',
                        'meta': {
                            'meta_key_3': 'meta_value_3',
                            'meta_key_1': 'meta_value_1',
                            'meta_key_2': 'meta_value_2',
                        },
                    },
                    {
                        'storage_id': 'storage_id_2',
                        'storage_bucket': 'bucket_photos',
                        'meta': {
                            'meta_key_5': 'meta_value_5',
                            'meta_key_4': 'meta_value_4',
                        },
                    },
                    {
                        'storage_id': 'storage_id_3',
                        'storage_bucket': 'bucket_photos',
                    },
                ],
            },
        },
    )

    assert response.status_code == 200

    cursor = pgsql['biometry_etalons'].cursor()
    cursor.execute(
        'SELECT ARRAY_AGG(key), ARRAY_AGG(value)'
        ' FROM biometry_etalons.media_meta GROUP BY media_id',
    )
    result = list(cursor)
    assert len(result) == 2

    result.sort(key=lambda result: len(result[0]))

    assert set(result[0][0]) == {'meta_key_4', 'meta_key_5'}
    assert set(result[0][1]) == {'meta_value_4', 'meta_value_5'}
    assert set(result[1][0]) == {'meta_key_1', 'meta_key_2', 'meta_key_3'}
    assert set(result[1][1]) == {
        'meta_value_1',
        'meta_value_2',
        'meta_value_3',
    }
