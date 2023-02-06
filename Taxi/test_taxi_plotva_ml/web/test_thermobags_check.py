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

BASE_PATH = '/quality_control/thermobags_check'
VIA_PATH = '/quality_control/router/v1?handler_name=thermobags_check'
PATH = BASE_PATH + '/v1'
PING_PATH = BASE_PATH + '/ping'

TEXT = hashlib.md5(b'text').hexdigest()
IMAGE_ARR = np.zeros((512, 512, 3))
NO_TEXT = hashlib.md5(b'no_text').hexdigest()
MDS_400 = hashlib.md5(b'mds_400').hexdigest()
OCR_400 = hashlib.md5(b'ff_400').hexdigest()
MDS_500 = hashlib.md5(b'mds_500').hexdigest()
OCR_500 = hashlib.md5(b'ff_500').hexdigest()

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'thermobags_check'}),
]

logger = logging.getLogger(__name__)

OCR_RESPONSE = {
    'data': {
        'blocks': [],
        'rotate': 270,
        'imgsize': {'h': 480, 'w': 853},
        'lang': 'rus',
        'entities': None,
        'fulltext': [
            {
                'LineSizeCategory': 1,
                'Confidence': 0.756934762,
                'Type': 'text',
                'Text': 'Яндекс Go\n\n',
            },
            {
                'LineSizeCategory': 1,
                'Confidence': 0.6903019547,
                'Type': 'text',
                'Text': 'ставка',
            },
            {
                'LineSizeCategory': 1,
                'Confidence': 0.72461766,
                'Type': 'text',
                'Text': ' роста\n\n',
            },
            {
                'LineSizeCategory': 0,
                'Confidence': 0.7085744739,
                'Type': 'text',
                'Text': 'B9901\n',
            },
        ],
        'timeLimit': {'percent': 100, 'stopped_by_timeout': False},
        'aggregated_stat': 763,
        'max_line_confidence': 0.9130237103,
        'istext': 0,
    },
    'status': 'success',
}


@pytest.fixture
def mds_service(mockserver):
    @mockserver.json_handler('/get-taximeter/' + TEXT)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        is_success, buffer = cv2.imencode('.jpg', IMAGE_ARR)
        io_buf = io.BytesIO(buffer).read()
        return mockserver.make_response(io_buf)

    @mockserver.json_handler('/get-taximeter/' + NO_TEXT)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return NO_TEXT

    @mockserver.json_handler('/get-taximeter/' + MDS_400)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return mockserver.make_response('Bad Rquest', status=400)

    @mockserver.json_handler('/get-taximeter/' + OCR_400)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return OCR_400

    @mockserver.json_handler('/get-taximeter/' + MDS_500)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return mockserver.make_response('Internal Server Error', status=500)

    @mockserver.json_handler('/get-taximeter/' + OCR_500)
    # pylint: disable=unused-variable
    def get_taximeter_handler(request):
        return OCR_500


@pytest.fixture
def ocr_translate_service(mockserver):
    @mockserver.json_handler('/ocr-translate/recognize')
    # pylint: disable=unused-variable
    def ocr_translate_handler(request):
        request_data = str(request.get_data())
        response = copy.deepcopy(OCR_RESPONSE)
        return response


async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


async def test_empty_request(web_app_client):
    response = await web_app_client.post(PATH, data={})
    assert response.status == 400


async def test_flap_mds(web_app_client, mockserver, mds_service):
    request = {
        'media': [
            {
                'code': 'thermobag',
                'url': (mockserver.url('/get-taximeter/') + MDS_500),
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert len(data['data']) == 1


async def test_text_ocr(
        web_app_client, mockserver, ocr_translate_service, mds_service,
):
    request = {
        'media': [
            {
                'code': 'thermobag',
                'url': (mockserver.url('/get-taximeter/') + TEXT),
            },
        ],
    }
    response = await web_app_client.post(PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['data'][-2]['value'] == 'number_recognized'
    assert data['data'][-1]['value'] == 'b9901'


async def test_via(
        web_app_client, mockserver, ocr_translate_service, mds_service,
):
    request = {
        'media': [
            {
                'code': 'thermobag',
                'url': (mockserver.url('/get-taximeter/') + TEXT),
            },
        ],
    }
    response = await web_app_client.post(VIA_PATH, data=json.dumps(request))
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['data'][-2]['value'] == 'number_recognized'
    assert data['data'][-1]['value'] == 'b9901'

    kv_mapping = {module['field']: module['value'] for module in data['data']}

    assert 'yandex_and_other_brand_confidence' in kv_mapping
