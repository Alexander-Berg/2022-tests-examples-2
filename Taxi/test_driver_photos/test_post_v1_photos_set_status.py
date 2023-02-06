import pytest


@pytest.mark.parametrize(
    ['status', 'reason'],
    (
        pytest.param('approved', None, id='approved'),
        pytest.param('rejected', 'face_not_visible', id='rejected'),
    ),
)
async def test_set_status(web_app_client, pgsql, status, reason):
    photo = {'photo_name': 'nirvana', 'status': status}
    if reason:
        photo['reason'] = reason

    response = await web_app_client.post(
        '/driver-photos/v1/photos/set_status', json={'photos': [photo]},
    )
    assert response.status == 200

    cursor = pgsql['driver_photos'].cursor()
    cursor.execute(
        'SELECT photo_status, reason FROM driver_photos '
        'WHERE photo_name = %s',
        ('nirvana',),
    )
    for photo in cursor:
        (status_db, reason_db) = photo

        assert status_db == status
        if reason:
            assert reason_db == reason
