import aiohttp
import pytest

SAVE_BINARY_URL = '/cc/v1/callcenter-qa/v1/binary/save'


def make_multipart_request(image=None, sip_log=None):
    with aiohttp.MultipartWriter('form-data') as data:
        if image:
            if not isinstance(image, bytes):
                image = str(image).encode('utf-8')
            payload = aiohttp.payload.BytesPayload(
                image, headers={'Content-Type': 'image/jpeg'},
            )
            payload.set_content_disposition('form-data', name='image')
            data.append_payload(payload)

        if sip_log:
            if not isinstance(sip_log, bytes):
                sip_log = str(sip_log).encode('utf-8')
            payload = aiohttp.payload.BytesPayload(
                sip_log, headers={'Content-Type': 'text/plain'},
            )
            payload.set_content_disposition('form-data', name='sip_log')
            data.append_payload(payload)

    headers = {
        'Content-Type': 'multipart/form-data; boundary=' + data.boundary,
    }
    return {'data': data, 'headers': headers}


@pytest.mark.parametrize(
    ['request_body', 'expected_status'],
    (
        pytest.param(
            {'image': 'image_content', 'sip_log': 'some log'},
            200,
            id='simple_request',
        ),
        pytest.param({'image': 'image_content'}, 200, id='no_log'),
        pytest.param({'sip_log': 'some log'}, 200, id='no_image'),
        pytest.param({}, 400, id='no_data'),
    ),
)
async def test_base(
        taxi_callcenter_qa, request_body, expected_status, mockserver,
):
    @mockserver.handler('/mds-s3-internal', prefix=True)
    def _mock_s3(request):
        return mockserver.make_response('mds_link', 200)

    response = await taxi_callcenter_qa.post(
        SAVE_BINARY_URL, **make_multipart_request(**request_body),
    )
    assert response.status_code == expected_status

    if 'image' in request_body:
        image = response.json()['image']
        assert image['mds_link'].startswith('images/')
        assert image['type'] == 'image'

    if 'sip_log' in request_body:
        sip_log = response.json()['sip_log']
        assert sip_log['mds_link'].startswith('sip_logs/')
        assert sip_log['type'] == 'sip_log'


@pytest.mark.parametrize(
    ['request_body', 'expected_status'],
    (
        pytest.param(
            {'image': 'image_content', 'sip_log': 'some log'},
            409,
            id='request_with_log',
        ),
        pytest.param(
            {'image': 'image_content'}, 500, id='request_without_log',
        ),
    ),
)
async def test_s3_failed_saving_image(
        taxi_callcenter_qa, request_body, expected_status, mockserver,
):
    @mockserver.handler('/mds-s3-internal', prefix=True)
    def _mock_s3(request):
        if request.path.startswith('/mds-s3-internal/sip_logs/'):
            return mockserver.make_response('mds_link', 200)
        return mockserver.make_response('internal server error', 500)

    response = await taxi_callcenter_qa.post(
        SAVE_BINARY_URL, **make_multipart_request(**request_body),
    )
    assert response.status_code == expected_status

    if 'sip_log' in request_body:
        assert response.json()['failed'] == ['image']
        sip_log = response.json()['sip_log']
        assert sip_log['mds_link'].startswith('sip_logs/')
        assert sip_log['type'] == 'sip_log'


@pytest.mark.parametrize(
    ['request_body', 'expected_status'],
    (
        pytest.param(
            {'image': 'image_content', 'sip_log': 'some log'},
            409,
            id='request_with_image',
        ),
        pytest.param({'sip_log': 'some log'}, 500, id='request_without_image'),
    ),
)
async def test_s3_failed_saving_sip_log(
        taxi_callcenter_qa, request_body, expected_status, mockserver,
):
    @mockserver.handler('/mds-s3-internal', prefix=True)
    def _mock_s3(request):
        if request.path.startswith('/mds-s3-internal/images/'):
            return mockserver.make_response('mds_link', 200)
        return mockserver.make_response('internal server error', 500)

    response = await taxi_callcenter_qa.post(
        SAVE_BINARY_URL, **make_multipart_request(**request_body),
    )
    assert response.status_code == expected_status

    if 'image' in request_body:
        assert response.json()['failed'] == ['sip_log']
        sip_log = response.json()['image']
        assert sip_log['mds_link'].startswith('images/')
        assert sip_log['type'] == 'image'


@pytest.mark.parametrize(
    ['request_body', 'expected_status'],
    (
        pytest.param(
            {'image': 'image_content', 'sip_log': 'some log'},
            500,
            id='mds_full_failed',
        ),
    ),
)
async def test_s3_failed_saving_files(
        taxi_callcenter_qa, request_body, expected_status, mockserver,
):
    @mockserver.handler('/mds-s3-internal', prefix=True)
    def _mock_s3(request):
        return mockserver.make_response('internal server error', 500)

    response = await taxi_callcenter_qa.post(
        SAVE_BINARY_URL, **make_multipart_request(**request_body),
    )
    assert response.status_code == expected_status
