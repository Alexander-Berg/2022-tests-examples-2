import hashlib

import numpy as np
import pytest


FACE = hashlib.md5(b'face').hexdigest()

FACE_FEATURES = {
    'CenterX': 0.793369,
    'CenterY': 0.525597,
    'Width': 0.265323,
    'Height': 0.51058,
    'Confidence': 1.68036,
    'Angle': -0.8321325183,
    'Features': np.full((4,), 1 / np.sqrt(256)).tolist(),
    'Landmarks': [
        {'Y': 147.8375244, 'X': 440.8726807},
        {'Y': 146.7093964, 'X': 360.7087097},
        {'Y': 480.0557251, 'X': 457.8555298},
        {'Y': 482.3573608, 'X': 350.3559875},
        {'Y': 338.6501465, 'X': 408.8861694},
    ],
}

CBIR_RESPONSE = {
    'cbirdaemon': {
        'info': '853x480',
        'info_orig': '853x480',
        'similarnn': {'FaceFeatures': [FACE_FEATURES]},
    },
}

BIOMETRICS_FEATURES_V1_RESPONSE = {
    'is_face_ok': True,
    'is_face_detected': True,
    'feature': np.full((4,), 1 / np.sqrt(256)).tolist(),
}

PROFILE = [
    {
        'profile': {'id': 'xxx_yyy', 'type': 'park_driver_profile_id'},
        'provider': 'signalq',
        'profile_meta': {'park_id': '123'},
    },
]

NOT_SIMILAR_PROFILE = [
    {
        'profile': {'id': 'zzz_yyy', 'type': 'park_driver_profile_id'},
        'profile_meta': {'park_id': '1234'},
        'provider': 'nesignalq',
    },
]


@pytest.mark.parametrize(
    'provider, meta, is_image_ok, expected_response',
    [
        (
            None,
            None,
            True,
            {
                'etalons_profiles': [
                    {
                        'etalon': {
                            'id': '33d56564727d43a986318d1df5188df1',
                            'version': 13,
                        },
                        'profiles': PROFILE,
                        'similarity': 0.9999743460353643,
                    },
                    {
                        'etalon': {
                            'id': '21d56564727d43a986318d1df5188df1',
                            'version': 4,
                        },
                        'profiles': [],
                        'similarity': 0.726401925,
                    },
                ],
            },
        ),
        (
            'signalq',
            None,
            True,
            {
                'etalons_profiles': [
                    {
                        'etalon': {
                            'id': '33d56564727d43a986318d1df5188df1',
                            'version': 13,
                        },
                        'profiles': PROFILE,
                        'similarity': 0.9999743460353643,
                    },
                    {
                        'etalon': {
                            'id': '44d56564727d43a986318d1df5188df1',
                            'version': 132,
                        },
                        'profiles': [
                            {
                                'profile': {
                                    'id': 'kkk_yyy',
                                    'type': 'park_driver_profile_id',
                                },
                                'profile_meta': {'park_id': '123'},
                                'provider': 'signalq',
                            },
                        ],
                        'similarity': 0.2088467416742222,
                    },
                ],
            },
        ),
        ('signalq1337', None, True, {'etalons_profiles': []}),
        (
            'nesignalq',
            {'park_id': '1234'},
            True,
            {
                'etalons_profiles': [
                    {
                        'etalon': {
                            'id': '44d56564727d43a986318d1df5188df1',
                            'version': 132,
                        },
                        'profiles': NOT_SIMILAR_PROFILE,
                        'similarity': 0.2088467416742222,
                    },
                ],
            },
        ),
        ('signalq', {'park_id': 'new_park'}, True, {'etalons_profiles': []}),
        ('signalq', {'park_id': 'new_park'}, True, {'etalons_profiles': []}),
        pytest.param(None, None, False, None, id='image_not_ok'),
    ],
)
@pytest.mark.config(
    TVM_ENABLED=False,
    TVM_RULES=[
        {'src': 'mock', 'dst': 'biometry-etalons'},
        {'src': 'biometry-etalons', 'dst': 'plotva-ml'},
    ],
    TVM_SERVICES={
        'mock': 111,
        'biometry-etalons': 2345,
        'plotva-ml': 2016315,
        'statistics': 3434,
        'media-storage': 4324,
        'saas-searchproxy': 766,
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
@pytest.mark.pgsql('biometry_etalons', files=['etalons_face_features.sql'])
async def test_internal_v1_profiles_identify(
        taxi_biometry_etalons,
        pgsql,
        mockserver,
        load_json,
        provider,
        meta,
        is_image_ok,
        expected_response,
):
    @mockserver.handler('/v1/xxx/photos/123', prefix=True)
    def _mock_s3(request):
        return mockserver.make_response(FACE, 200)

    @mockserver.json_handler('/saas-search-proxy/')
    def _mock_saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        '/biometrics-features/images-apphost/biometrics-features',
    )
    # pylint: disable=unused-variable
    def biometrics_features_v1_handler(request):
        if not is_image_ok:
            return mockserver.make_response(status=400)
        return BIOMETRICS_FEATURES_V1_RESPONSE

    @mockserver.json_handler('/cbir-features/images-apphost/cbir-features')
    # pylint: disable=unused-variable
    def cbir_features_handler(request):
        if not is_image_ok:
            return mockserver.make_response(status=400)
        return CBIR_RESPONSE

    json = {
        'media': {
            'storage_id': 'v1/xxx/photos/123',
            'storage_type': 'signalq-s3',
            'storage_bucket': 'sda-photos',
        },
        'limit': 2,
    }
    if provider is not None:
        json['filter'] = {'providers': [provider]}
    if meta is not None:
        json['filter']['meta'] = meta
    response = await taxi_biometry_etalons.post(
        '/internal/biometry-etalons/v1/profiles/identify', json=json,
    )

    if not is_image_ok:
        assert response.status_code == 400
        return
    assert response.status_code == 200
    assert response.json() == expected_response
