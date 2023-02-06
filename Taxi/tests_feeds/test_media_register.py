import pytest

import tests_feeds.feeds_common as fc


@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.parametrize(
    'media_type,storage_type,storage_settings',
    [
        (
            'image',
            'avatars',
            {'storage_media_id': 'e5bb399de4e9493b9cec21f6430b4fec'},
        ),
        ('video', 's3', {'bucket_name': 'feeds', 'service': 'taxi'}),
        ('binary', 's3', {'bucket_name': 'feeds', 'service': 'taxi'}),
    ],
    ids=('avatars', 's3-video', 's3-binary'),
)
async def test_insert(
        taxi_feeds, pgsql, media_type, storage_type, storage_settings,
):
    response = await taxi_feeds.post(
        '/v1/media/register',
        json={
            'media_id': '4fa4ea41013449edbce5429f3ac8f1b2',
            'media_type': media_type,
            'storage_type': storage_type,
            'storage_settings': storage_settings,
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT * FROM media')
    assert list(cursor) == [
        (
            '4fa4ea41013449edbce5429f3ac8f1b2',
            media_type,
            storage_type,
            storage_settings,
            fc.make_msk_datetime(2018, 12, 2, 3, 0),
        ),
    ]


@pytest.mark.pgsql('feeds-pg', files=['test_media_register.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_update(taxi_feeds, pgsql):
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT * FROM media')
    assert len(list(cursor)) == 1

    response = await taxi_feeds.post(
        '/v1/media/register',
        json={
            'media_id': 'media_1',
            'media_type': 'video',
            'storage_type': 'avatars',
            'storage_settings': {
                'storage_media_id': 'e5bb399de4e9493b9cec21f6430b4fec',
            },
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT * FROM media')
    rows = list(cursor)
    assert len(rows) == 1
    assert rows[0] == (
        'media_1',
        'video',
        'avatars',
        {'storage_media_id': 'e5bb399de4e9493b9cec21f6430b4fec'},
        fc.make_msk_datetime(2018, 12, 2, 3, 0),
    )
