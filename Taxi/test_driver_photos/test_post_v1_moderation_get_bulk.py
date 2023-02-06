import pytest


@pytest.mark.parametrize(
    ['max_photos'],
    (
        pytest.param(0, id='Get empty list first'),
        pytest.param(2, id='Get 2 photos first'),
        pytest.param(3, id='Get all photos first'),
    ),
)
async def test_get_bulk_for_moderation(
        web_app_client, pgsql, load_json, max_photos,
):
    photos_answer = load_json('response_get_bulk.json')

    response = await web_app_client.post(
        f'/driver-photos/v1/moderation/get_bulk?max_photos={max_photos}',
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'photos': photos_answer[:max_photos]}

    response = await web_app_client.post(
        f'/driver-photos/v1/moderation/get_bulk?max_photos=10',
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'photos': photos_answer[max_photos:]}

    cursor = pgsql['driver_photos'].cursor()
    cursor.execute(
        'SELECT photo_status FROM driver_photos WHERE photo_name = \'216\'',
    )
    for photo in cursor:
        (photo_status,) = photo
        assert photo_status == 'on_moderation'


async def test_get_bulk_for_moderation_404(web_app_client):
    response = await web_app_client.post(
        f'/driver-photos/v1/moderation/get_bulk',
    )
    assert response.status == 400
