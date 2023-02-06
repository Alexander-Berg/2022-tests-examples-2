# flake8: noqa
# pylint: disable=W0621,E0102,R1705,E1101
import copy
import hashlib
import logging
import io
import json

import cv2
import numpy as np
import pytest

from taxi_plotva_ml.api import thermobags_check_v1

BASE_PATH = '/quality_control/z_detect'
PATH = BASE_PATH + '/v1'
PING_PATH = BASE_PATH + '/ping'

VIA_PATH = '/quality_control/router/v1?handler_name=z_detect'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=PATH),
    pytest.mark.download_ml_resource(
        attrs={'type': 'z_detector', 'version_maj': '2'},
    ),
]

logger = logging.getLogger(__name__)


@pytest.fixture
def mds_service(mockserver):
    @mockserver.json_handler('/test_photo.jpg')
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        arr = np.random.randint(0, 255, (480, 640, 3))
        is_success, buffer = cv2.imencode('.jpg', arr)
        io_buf = io.BytesIO(buffer).read()
        return mockserver.make_response(io_buf)


async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


async def test_empty_request(web_app_client):
    response = await web_app_client.post(PATH, data={})
    assert response.status == 400


async def test_noise(web_app_client, mockserver, mds_service):
    request = {
        'media': [
            {'code': 'front', 'url': (mockserver.url('/test_photo.jpg'))},
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert 'front_z_presence_confidence' in {d['field'] for d in data['data']}
    assert 'front_response' in {d['field'] for d in data['data']}


async def test_via(web_app_client, mockserver, mds_service):
    request = {
        'media': [
            {'code': 'front', 'url': (mockserver.url('/test_photo.jpg'))},
            {'code': 'back', 'url': (mockserver.url('/test_photo.jpg'))},
        ],
    }
    response = await web_app_client.post(VIA_PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert len(data['data']) == 4
    assert 'front_z_presence_confidence' in {d['field'] for d in data['data']}
    assert 'front_response' in {d['field'] for d in data['data']}
