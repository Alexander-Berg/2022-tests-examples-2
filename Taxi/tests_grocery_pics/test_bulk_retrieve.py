import datetime

import pytest

from tests_grocery_pics import models


@pytest.mark.config(GROCERY_PICS_BASE64_SIZE_THRESHOLD_BYTES=10000)
async def test_basic(taxi_grocery_pics, mockserver, avatar_mds):
    image = models.Image(base64_size_bytes=3000)

    avatar_mds.mock_image(image=image)

    json = _get_json([image], mockserver)

    response = await taxi_grocery_pics.post(
        '/v1/images/bulk-retrieve', json=json,
    )
    assert response.status_code == 200
    assert response.json() == {
        'images': [
            {
                'data_uri': image.base64,
                'url_template': image.get_url_template(mockserver),
                'dimensions': {'height': image.height, 'width': image.width},
            },
        ],
    }


@pytest.mark.config(GROCERY_PICS_BASE64_SIZE_THRESHOLD_BYTES=2000)
@pytest.mark.config(GROCERY_PICS_BASE64_REQUEST_THRESHOLD=50 * 50)
@pytest.mark.parametrize(
    'width,height,base64_size,base64_available',
    [(100, 100, 3000, False), (30, 30, 1500, True)],
)
async def test_big_image(
        taxi_grocery_pics,
        mockserver,
        avatar_mds,
        width,
        height,
        base64_size,
        base64_available,
):
    image = models.Image(
        base64_size_bytes=base64_size, width=width, height=height,
    )

    avatar_mds.mock_image(image=image)

    json = _get_json([image], mockserver)

    response = await taxi_grocery_pics.post(
        '/v1/images/bulk-retrieve', json=json,
    )
    assert response.status_code == 200

    if base64_available:
        data_uri = image.base64
    else:
        data_uri = image.get_url(mockserver)

    assert response.json() == {
        'images': [
            {
                'data_uri': data_uri,
                'url_template': image.get_url_template(mockserver),
                'dimensions': {'height': image.height, 'width': image.width},
            },
        ],
    }

    if base64_available:
        assert avatar_mds.times_called(handler='size', image=image) == 0
        assert avatar_mds.times_called(handler='base64', image=image) == 1
    else:
        assert avatar_mds.times_called(handler='size', image=image) == 1
        assert avatar_mds.times_called(handler='base64', image=image) == 0


@pytest.mark.config(GROCERY_PICS_BASE64_SIZE_THRESHOLD_BYTES=10000)
async def test_threshold(taxi_grocery_pics, mockserver, avatar_mds):
    image_1 = models.Image(base64_size_bytes=3000)
    image_2 = models.Image(base64_size_bytes=30000)

    avatar_mds.mock_image(image=image_1)
    avatar_mds.mock_image(image=image_2)

    json = _get_json([image_1, image_2], mockserver)

    response = await taxi_grocery_pics.post(
        '/v1/images/bulk-retrieve', json=json,
    )
    assert response.status_code == 200
    assert response.json() == {
        'images': [
            {
                'dimensions': {
                    'height': image_1.height,
                    'width': image_1.width,
                },
                'data_uri': image_1.base64,
                'url_template': image_1.get_url_template(mockserver),
            },
            {
                'dimensions': {
                    'height': image_2.height,
                    'width': image_2.width,
                },
                'data_uri': image_2.get_url(mockserver),
                'url_template': image_2.get_url_template(mockserver),
            },
        ],
    }


@pytest.mark.config(GROCERY_PICS_BASE64_SIZE_THRESHOLD_BYTES=10000)
async def test_cache(taxi_grocery_pics, mockserver, avatar_mds):
    image = models.Image(base64_size_bytes=3000)

    avatar_mds.mock_image(image=image)

    json = _get_json([image], mockserver)

    response = await taxi_grocery_pics.post(
        '/v1/images/bulk-retrieve', json=json,
    )
    assert response.status_code == 200
    assert response.json() == {
        'images': [
            {
                'dimensions': {'height': image.height, 'width': image.width},
                'data_uri': image.base64,
                'url_template': image.get_url_template(mockserver),
            },
        ],
    }

    assert avatar_mds.times_called(handler='size', image=image) == 0
    assert avatar_mds.times_called(handler='base64', image=image) == 1

    avatar_mds.flush(image=image)

    response = await taxi_grocery_pics.post(
        '/v1/images/bulk-retrieve', json=json,
    )
    assert response.status_code == 200
    assert response.json() == {
        'images': [
            {
                'dimensions': {'height': image.height, 'width': image.width},
                'data_uri': image.base64,
                'url_template': image.get_url_template(mockserver),
            },
        ],
    }

    # Use cache
    assert avatar_mds.times_called(handler='size', image=image) == 0
    assert avatar_mds.times_called(handler='base64', image=image) == 0


@pytest.mark.config(GROCERY_PICS_BASE64_SIZE_THRESHOLD_BYTES=10000)
async def test_500_and_retry(
        taxi_grocery_pics, mockserver, avatar_mds, mocked_time,
):
    image = models.Image(base64_size_bytes=3000)

    avatar_mds.mock_image(image=image)

    now = datetime.datetime.now()
    mocked_time.set(now)

    @mockserver.json_handler(
        f'/avatars-mds-get/get-grocery-goods/{image.group_id}/{image.name}/'
        f'{image.width}x{image.height}',
    )
    def _mock_base64(request):
        return mockserver.make_response('', 500)

    json = _get_json([image], mockserver)

    response = await taxi_grocery_pics.post(
        '/v1/images/bulk-retrieve', json=json,
    )
    assert response.status_code == 200

    response_with_url = {
        'images': [
            {
                'dimensions': {'height': image.height, 'width': image.width},
                'data_uri': image.get_url(mockserver),
                'url_template': image.get_url_template(mockserver),
            },
        ],
    }
    assert response.json() == response_with_url

    assert avatar_mds.times_called(handler='size', image=image) == 0
    assert _mock_base64.times_called == 1

    # override 500 mock
    avatar_mds.mock_image(image=image)

    # Not expired yet
    mocked_time.set(now + datetime.timedelta(minutes=20))

    avatar_mds.flush(image=image)

    response = await taxi_grocery_pics.post(
        '/v1/images/bulk-retrieve', json=json,
    )
    assert response.status_code == 200
    assert response.json() == response_with_url

    # Use cache
    assert avatar_mds.times_called(handler='size', image=image) == 0
    assert avatar_mds.times_called(handler='base64', image=image) == 0

    # Check fetch again after LRU cache expired
    mocked_time.set(now + datetime.timedelta(minutes=35))

    avatar_mds.flush(image=image)

    response = await taxi_grocery_pics.post(
        '/v1/images/bulk-retrieve', json=json,
    )
    assert response.status_code == 200
    assert response.json() == {
        'images': [
            {
                'dimensions': {'height': image.height, 'width': image.width},
                'data_uri': image.base64,
                'url_template': image.get_url_template(mockserver),
            },
        ],
    }

    assert avatar_mds.times_called(handler='size', image=image) == 0
    assert avatar_mds.times_called(handler='base64', image=image) == 1


def _get_json(images, mockserver):
    json = {'images': []}

    for image in images:
        json['images'].append(
            {
                'url_template': image.get_url_template(mockserver),
                'dimensions': {'width': image.width, 'height': image.height},
            },
        )

    return json
