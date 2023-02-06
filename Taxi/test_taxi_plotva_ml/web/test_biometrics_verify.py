# flake8: noqa
# pylint: disable=W0621,E0102,R1705
import copy
import hashlib
import json

import numpy as np
import pytest

from taxi_pyml.biometrics import common
from taxi_plotva_ml.api import biometrics_verify_v1

BASE_PATH = '/biometrics/verify'
PATH = BASE_PATH + '/v1'
PING_PATH = BASE_PATH + '/ping'

FACE = hashlib.md5(b'face').hexdigest()
NO_FACE = hashlib.md5(b'no_face').hexdigest()
MDS_400 = hashlib.md5(b'mds_400').hexdigest()
FF_400 = hashlib.md5(b'ff_400').hexdigest()
MDS_500 = hashlib.md5(b'mds_500').hexdigest()
FF_500 = hashlib.md5(b'ff_500').hexdigest()

BASE_RESPONSE = {'cbirdaemon': {'info': '853x480', 'info_orig': '853x480'}}
FACE_FEATURES = {
    'CenterX': 0.793369,
    'CenterY': 0.525597,
    'Width': 0.265323,
    'Height': 0.51058,
    'Confidence': 1.68036,
    'Angle': -0.8321325183,
    'Features': np.full((256,), 1 / np.sqrt(256)).tolist(),
}
IMAGE_FEATURES = {
    'Features': np.full((96,), 1 / np.sqrt(96)).tolist(),
    'Dimension': [1, 96],
    'Version': '8',
}

EXPERIMENT_ARGS = {
    'consumer': biometrics_verify_v1.EXP3_BIOMETRICS_VERIFY_CONSUMER,
    'experiment_name': 'biometrics_ml',
    'args': [{'name': 'id', 'type': 'string', 'value': 'deadbeef'}],
}

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'biometrics_verify'}),
]


@pytest.fixture
def mds_service(mockserver):
    @mockserver.json_handler('/get-taximeter/' + FACE)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return FACE

    @mockserver.json_handler('/get-taximeter/' + NO_FACE)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return NO_FACE

    @mockserver.json_handler('/get-taximeter/' + MDS_400)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return mockserver.make_response('Bad Rquest', status=400)

    @mockserver.json_handler('/get-taximeter/' + FF_400)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return FF_400

    @mockserver.json_handler('/get-taximeter/' + MDS_500)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return mockserver.make_response('Internal Server Error', status=500)

    @mockserver.json_handler('/get-taximeter/' + FF_500)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return FF_500


@pytest.fixture
def cbir_features_service(mockserver):
    @mockserver.json_handler('/cbir-features/images-apphost/cbir-features')
    # pylint: disable=unused-variable
    def cbir_features_handler(request):
        request_data = str(request.get_data())
        response = copy.deepcopy(BASE_RESPONSE)
        face_features_v4 = {'LayerName': common.FACE_MODEL_V4, **FACE_FEATURES}
        face_features_v5 = {'LayerName': common.FACE_MODEL_V5, **FACE_FEATURES}
        image_features_v8 = {
            'LayerName': common.IMAGE_MODEL_V8,
            **IMAGE_FEATURES,
        }

        if FACE in request_data:
            response['cbirdaemon']['similarnn'] = {
                'FaceFeatures': [face_features_v4, face_features_v5],
                'ImageFeatures': [image_features_v8],
            }
            return response
        elif NO_FACE in request_data:
            return response
        elif FF_400 in request_data:
            return mockserver.make_response('Bad Request', status=400)
        elif FF_500 in request_data:
            return mockserver.make_response(
                'Internal Server Error', status=500,
            )
        return mockserver.make_response('Unexpected Error', status=500)


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_empty_request(web_app_client):
    response = await web_app_client.post(PATH, data={})
    assert response.status == 400


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_empty_history(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [{'code': 'selfie', 'type': 'image', 'items': []}],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))

    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'success'
    assert data['reference_media']
    assert data['reference_media'][0]['items']


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_valid_request(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))

    assert response.status == 200
    data = json.loads(await response.text())
    assert len(data['reference_media'][0]['items']) >= len(
        request['reference_media'],
    )


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_fail_load_image(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + MDS_400),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'success'


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_flap_mds(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + MDS_500),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'unknown'


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_corrupted_image(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + FF_400),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'success'


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_flap_cbir_features(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + FF_500),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'unknown'


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_no_face(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + NO_FACE),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))

    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'unknown'
    assert len(data['reference_media'][0]['items']) == 2


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_no_faces_in_history(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + NO_FACE),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + NO_FACE),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))

    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'success'
    assert data['reference_media']
    assert data['reference_media'][0]['items']


@pytest.mark.client_experiments3(
    value={'double_check': False}, **EXPERIMENT_ARGS,
)
async def test_equal_faces(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))

    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'success'
    assert len(data['reference_media'][0]['items']) == 3


@pytest.mark.client_experiments3(
    value={'double_check': True}, **EXPERIMENT_ARGS,
)
async def test_equal_faces_double_check(
        web_app_client, mockserver, cbir_features_service, mds_service,
):
    request = {
        'target_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'deadbeef',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
        'reference_media': [
            {
                'code': 'selfie',
                'type': 'image',
                'items': [
                    {
                        'id': 'c0ffee',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:46:00',
                        'expired_at': '2012-12-12',
                    },
                    {
                        'id': 'c0c0a',
                        'url': (mockserver.url('/get-taximeter/') + FACE),
                        'referenced_at': '2019-11-26T16:47:00',
                        'expired_at': '2012-12-12',
                    },
                ],
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))

    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution']['status'] == 'unknown'
    assert len(data['reference_media'][0]['items']) == 2
    assert common.DOUBLE_CHECK in data['resolution']['info']['experiments']
