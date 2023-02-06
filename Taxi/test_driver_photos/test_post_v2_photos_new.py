import io

import aiohttp
import aiohttp.web
from PIL import Image
import pytest

from test_taxi_driver_photos.stubs import avatars_mds_upload_response


# pylint: disable=too-many-locals
@pytest.mark.parametrize(
    [
        'unique_driver_id',
        'return_code',
        'stq_put_called',
        'mds_fails_times',
        'image_format',
        'image_mode',
        'is_image_file',
    ],
    (
        pytest.param(
            '5bc702f995572fa0df26e0e2',
            200,
            True,
            None,
            'JPEG',
            'RGB',
            True,
            id='Execution with unique_driver_id',
        ),
        pytest.param(
            '5bc702f995572fa0df26e0e2',
            200,
            True,
            2,
            'JPEG',
            'RGB',
            True,
            id='Several retries - should work',
        ),
        pytest.param(
            None,
            400,
            False,
            None,
            'JPEG',
            'RGB',
            True,
            id='unique_driver_id is missing',
        ),
        pytest.param(
            '5bc702f995572fa0df26e0e2',
            400,
            True,
            None,
            'PNG',
            'RGBA',
            True,
            id='Wrong photo format error (image mode RGBA)',
        ),
        pytest.param(
            '5bc702f995572fa0df26e0e2',
            400,
            True,
            None,
            'PNG',
            'RGBA',
            False,
            id='Wrong photo format error (not an image)',
        ),
    ),
)
async def test_add_driver_photo(
        web_app_client,
        mock,
        mockserver,
        patch_aiohttp_session,
        patch,
        stub,
        response_mock,
        unique_driver_id,
        return_code,
        stq_put_called,
        mds_fails_times,
        image_format,
        image_mode,
        is_image_file,
):
    @mock
    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    # Mock face detection
    @patch('face_recognition.face_locations')
    def _patched_face_locations(*args):
        return [(500, 500, 1000, 1000), (0, 0, 10, 10)]

    @mockserver.handler('/mds_avatars/put-driver-photos', prefix=True)
    def _patched_request(request: aiohttp.web.Request, **kwargs):
        return aiohttp.web.json_response(data=avatars_mds_upload_response())

    input_params = {
        'unique_driver_id': unique_driver_id,
        'source_type': 'byte_file',
        'idempotency_key': '123456',
    }
    if not unique_driver_id:
        input_params.pop('unique_driver_id', None)

    with aiohttp.MultipartWriter('form-data') as mpwriter:
        mpwriter.append_json(input_params)
        fp = None
        if is_image_file:
            test_image = Image.new(image_mode, (6000, 4000))
            fp = io.BytesIO()
            test_image.save(fp, image_format)
        else:
            fp = io.BytesIO(b'1234')
        fp.seek(0)
        content_type = f'image/{image_format.lower()}'
        mpwriter.append(fp, {'Content-Type': content_type})

        headers = dict()
        headers['X-File-Name'] = 'hello.' + image_format.lower()

        response = await web_app_client.post(
            f'/driver-photos/v2/photos/new', data=mpwriter, headers=headers,
        )
        assert response.status == return_code
        if unique_driver_id is None:
            return
        content = await response.json()
        if return_code == 200:
            assert content == {
                'code': 'ok',
                'message': 'Photo uploaded successfully',
            }
        elif is_image_file:
            assert content == {
                'code': 'WRONG_PHOTO_FORMAT',
                'message': (
                    'image cannot be saved in jpeg (image mode: RGBA).'
                    ' Caused by OSError (cannot write mode RGBA as JPEG)'
                ),
            }
        elif not is_image_file:
            assert content.get('code') == 'WRONG_PHOTO_FORMAT'


@pytest.mark.parametrize(
    ['unique_driver_id', 'return_code', 'stq_put_called'],
    (
        pytest.param(
            '5bc702f995572fa0df26e0e2', 200, True, id='Normal execution',
        ),
        pytest.param(None, 400, False, id='unique_driver_id missing'),
    ),
)
async def test_add_driver_photo_mds(
        web_app_client,
        mock,
        patch_aiohttp_session,
        patch,
        mockserver,
        stub,
        response_mock,
        unique_driver_id,
        return_code,
        stq_put_called,
):
    @mock
    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    # Mock MDS
    @patch('taxi.clients.mds.MDSClient.download')
    async def _patched_download(path):
        test_image = Image.new('RGB', (6000, 4000))
        fp = io.BytesIO()
        test_image.save(fp, 'JPEG')
        fp.seek(0)
        return fp.read()

    # Mock face detection
    @patch('face_recognition.face_locations')
    def _patched_face_locations(*args):
        return [(500, 500, 1000, 1000), (0, 0, 10, 10)]

    # Mock avatars-mds

    @mockserver.handler('/mds_avatars/put-driver-photos', prefix=True)
    def _patched_request(request: aiohttp.web.Request, **kwargs):
        return aiohttp.web.json_response(data=avatars_mds_upload_response())

    input_params = {
        'unique_driver_id': unique_driver_id,
        'source_type': 'MDS',
        'source': '1138/bc4be874-757b-44bc-a10d-17bb7420f2b7',
        'idempotency_key': '123456',
    }
    if not unique_driver_id:
        input_params.pop('unique_driver_id', None)

    response = await web_app_client.post(
        f'/driver-photos/v2/photos/new', json=input_params,
    )
    assert response.status == return_code
    if return_code == 200:
        content = await response.json()
        assert content == {
            'code': 'ok',
            'message': 'Photo uploaded successfully',
        }
