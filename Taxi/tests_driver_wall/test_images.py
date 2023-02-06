import base64
import re

import pytest


def _make_image_path(image_id, size=0):
    size_str = f'_{size}' if size else ''
    return f'{image_id}{size_str}.png'


async def test_upload_bad_request(taxi_driver_wall, mockserver, load_binary):
    response = await taxi_driver_wall.post(
        'internal/driver-wall/v1/upload-image',
        data=base64.b64encode(load_binary('too_big.png')),
    )
    assert response.status_code == 400

    response = await taxi_driver_wall.post(
        'internal/driver-wall/v1/upload-image',
        data=base64.b64encode(load_binary('corrupt.png')),
    )
    assert response.status_code == 400


@pytest.mark.now('2021-03-03T00:00:00Z')
async def test_upload_image(taxi_driver_wall, mockserver, load_binary):
    @mockserver.handler('/s3mds', prefix=True)
    def _mock_mds(request):
        return mockserver.make_response('', 200)

    response = await taxi_driver_wall.post(
        'internal/driver-wall/v1/upload-image',
        headers={'Content-Type': 'image/png'},
        data=base64.b64encode(load_binary('ya_taxi.png')),
    )

    assert response.status_code == 200
    image_id = response.json()['id']
    assert image_id.split('/')[0] == '20210303'


async def test_image(taxi_driver_wall, mockserver, load_binary):
    valid_sizes = (0, 320, 480, 800, 1024)
    invalid_size = 123
    img = load_binary('ya_taxi.png')

    @mockserver.handler('/s3mds', prefix=True)
    def _mock_mds(request):
        if re.match(
                '[a-f0-9]{32}(?:[_-](320|480|800|1024))?.png',
                request.path.split('/')[-1],
        ):
            return mockserver.make_response(img, 200)
        return mockserver.make_response('', 404)

    response = await taxi_driver_wall.post(
        'internal/driver-wall/v1/upload-image',
        headers={'Content-Type': 'image/png'},
        data=base64.b64encode(img),
    )
    assert response.status_code == 200

    for size in valid_sizes:
        image_id = '20210302/f89bc690409244e0b6cb8158b06d719c'
        response = await taxi_driver_wall.get(
            '/driver/v1/driver-wall/image/{}'.format(
                _make_image_path(image_id, size),
            ),
        )
        assert response.status_code == 200

    image_id = '20210302/f89bc690409244e0b6cb8158b06d719c'
    response = await taxi_driver_wall.get(
        '/driver/v1/driver-wall/image/{}'.format(
            _make_image_path(image_id, invalid_size),
        ),
    )
    assert response.status_code == 404


async def test_image_404(taxi_driver_wall, mockserver, load_binary):
    @mockserver.handler('/s3mds', prefix=True)
    def _mock_mds(request):
        return mockserver.make_response('', 404)

    image_id = '20210302/f89bc690409244e0b6cb8158b06d719c'

    response = await taxi_driver_wall.get(
        '/driver/v1/driver-wall/image/{}'.format(
            _make_image_path(image_id, 320),
        ),
    )
    assert response.status_code == 404
