URI = '/admin/promotions/create_media_tag/'
MEDIA_TAG_ID = 'media_tag_123'
CREATE_MEDIA_TAG_DATA = {
    'id': MEDIA_TAG_ID,
    'type': 'image',
    'resize_mode': 'original_only',
}


async def test_create_media_tag_ok(web_app_client, patch, pgsql):
    response = await web_app_client.post(URI, json=CREATE_MEDIA_TAG_DATA)
    assert response.status == 200
    data = await response.json()
    assert data['id'] == MEDIA_TAG_ID
    with pgsql['promotions'].cursor() as cursor:
        cursor.execute(
            f'SELECT id, type, resize_mode FROM promotions.media_tags '
            f'WHERE id = \'{MEDIA_TAG_ID}\'',
        )
        assert cursor.fetchone() == tuple(CREATE_MEDIA_TAG_DATA.values())


async def test_create_media_tag_already_exists(web_app_client, patch):
    await web_app_client.post(URI, json=CREATE_MEDIA_TAG_DATA)
    response = await web_app_client.post(URI, json=CREATE_MEDIA_TAG_DATA)
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'already_exists',
        'message': 'media_tag с таким идентификатором уже существует',
    }
