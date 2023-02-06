import pytest


@pytest.mark.parametrize(
    'params, xaccel',
    [
        (
            {'image_id': '123/456', 'width': '300', 'height': '300'},
            '/_avatars-mds-testsuite/grocery-goods/123/456/300x300',
        ),
        (
            {'image_id': '123/456', 'width': '301', 'height': '301'},
            '/_avatars-mds-testsuite/grocery-goods/123/456/400x400',
        ),
        (
            {'image_id': '123/456', 'width': '3000', 'height': '3000'},
            '/_avatars-mds-testsuite/grocery-goods/123/456/1920x1080',
        ),
        (
            {'image_id': '123/456', 'width': '1', 'height': '1'},
            '/_avatars-mds-testsuite/grocery-goods/123/456/100x100',
        ),
    ],
)
async def test_basic(taxi_grocery_pics, params, xaccel):
    response = await taxi_grocery_pics.get(
        '/v2/images/retrieve', params=params,
    )
    assert response.status_code == 200
    assert response.content == b''
    assert response.headers['x-accel-redirect'] == xaccel


@pytest.mark.config(
    GROCERY_PICS_THUMBNAILS={
        'sizes': [
            {'name': '300x300', 'width': 300, 'height': 300, 'blur': True},
            {'name': '400x400', 'width': 400, 'height': 400},
        ],
    },
)
@pytest.mark.parametrize(
    'params, xaccel',
    [
        (
            {
                'image_id': '123/456',
                'width': '300',
                'height': '300',
                'filter': 'blur',
            },
            '/_avatars-mds-testsuite/grocery-goods/123/456/300x300blur',
        ),
        (
            {
                'image_id': '123/456',
                'width': '300',
                'height': '300',
                'filter': '',
            },
            '/_avatars-mds-testsuite/grocery-goods/123/456/300x300',
        ),
        (
            {
                'image_id': '123/456',
                'width': '400',
                'height': '400',
                'filter': 'blur',
            },
            '/_avatars-mds-testsuite/grocery-goods/123/456/300x300blur',
        ),
        (
            {
                'image_id': '123/456',
                'width': '400',
                'height': '400',
                'filter': '',
            },
            '/_avatars-mds-testsuite/grocery-goods/123/456/400x400',
        ),
    ],
)
async def test_blur(taxi_grocery_pics, params, xaccel):
    response = await taxi_grocery_pics.get(
        '/v2/images/retrieve', params=params,
    )
    assert response.status_code == 200
    assert response.content == b''
    assert response.headers['x-accel-redirect'] == xaccel
