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


# TODO: mock http request performing
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


@pytest.fixture(autouse=True)
def mock_http(mockserver):
    @mockserver.json_handler('/stackoverflow.com/questions')
    def _mock_http(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            hashlib.md5(b'PHOTO').hexdigest(), status=200,
        )


@pytest.mark.parametrize(
    'has_face, rotated', [(True, False), (False, False), (True, True)],
)
@pytest.mark.pgsql('biometry_etalons', files=['media_profiles_etalons.sql'])
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
    BIOMETRY_ETALONS_FEATURE_CALCULATOR_SETTINGS={
        'enabled': True,
        'period_ms': 1000,
        'limit': 10,
        'threads_num': 1,
    },
)
async def test_calculation_features(
        taxi_biometry_etalons, pgsql, mockserver, testpoint, has_face, rotated,
):
    @mockserver.handler('ms0000000000000000000002', prefix=True)
    def _mock_s3(request):
        if has_face:
            if rotated:
                return mockserver.make_response(FACE_ROTATED, 200)

            return mockserver.make_response(FACE, 200)

        return mockserver.make_response(NO_FACE, 200)

    @mockserver.json_handler(
        '/media-storage/service/media-storage/v1/retrieve',
    )
    def _mock_media_storage(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'url': '/stackoverflow.com/questions', 'version': '1'},
            status=200,
        )

    media_without_features_count = 1

    @testpoint('etalon-feature-calculator::media_without_features_count')
    def _media_without_features_count_tp(process_data):
        count = process_data['media_without_features']
        assert count == media_without_features_count

    def _biometry_etalons_psql_query(query):
        cursor = pgsql['biometry_etalons'].cursor()
        cursor.execute(query)
        result = list(row for row in cursor)
        cursor.close()

        return result

    await taxi_biometry_etalons.run_periodic_task('etalon-feature-calculator')

    if has_face:
        result = _biometry_etalons_psql_query(
            'SELECT etalon_id, media_id, features_handler, features '
            'FROM biometry_etalons.face_features ',
        )
        expected_result = (
            '000000000000000000000002',
            '2',
            '/biometrics_features/v1',
            BIOMETRICS_FEATURES_V1_RESPONSE_DETECTED['feature'],
        )
        assert result == [expected_result]
    else:
        result = _biometry_etalons_psql_query(
            'SELECT f.calculation_problem '
            'FROM biometry_etalons.media m '
            'INNER JOIN biometry_etalons.face_features f '
            'ON f.media_id = m.id '
            'WHERE m.id = \'2\'',
        )
        expected_result = ('NO_FACE',)
        assert result == [expected_result]

    # Проверим, что повторно медиа обрабатываться не станет
    media_without_features_count = 0
    await taxi_biometry_etalons.run_periodic_task('etalon-feature-calculator')

    # TODO: проверить подгрузку сразу для нескольких фоток + бросание ошибки
