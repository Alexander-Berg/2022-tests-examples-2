import pytest

URI = '/admin/promotions/resize_modes/{media_type}/{resize_mode}/'
_ADMIN_IMAGE_RESIZE_MODES = {
    'image': {
        'scale_factor': [
            {'field': 'original', 'value': 0},
            {'field': 'scale_factor', 'value': 0.75},
            {'field': 'scale_factor', 'value': 3},
        ],
    },
}


@pytest.mark.config(ADMIN_IMAGE_RESIZE_MODES=_ADMIN_IMAGE_RESIZE_MODES)
async def test_resize_modes_ok(web_app_client, patch):
    response = await web_app_client.get(
        URI.format(media_type='image', resize_mode='scale_factor'),
    )
    assert response.status == 200
    data = await response.json()
    assert data == _ADMIN_IMAGE_RESIZE_MODES['image']['scale_factor']


@pytest.mark.config(ADMIN_IMAGE_RESIZE_MODES=_ADMIN_IMAGE_RESIZE_MODES)
async def test_resize_modes_not_found(web_app_client, patch):
    response = await web_app_client.get(
        URI.format(media_type='video', resize_mode='scale_factor'),
    )
    assert response.status == 404

    response = await web_app_client.get(
        URI.format(media_type='image', resize_mode='width_fit'),
    )
    assert response.status == 404
