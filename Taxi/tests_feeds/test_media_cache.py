import pytest


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'feed_count': 5,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
        },
    },
)
@pytest.mark.now('2018-12-05T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_media_cache.sql'])
async def test_cache(taxi_feeds, pgsql):
    data = {
        'service': 'service',
        'channels': ['driver:1', 'city:moscow'],
        'media_info': {'screen_height': 100, 'screen_width': 140},
    }

    response = await taxi_feeds.post('/v1/fetch', json=data)

    assert response.status_code == 200
    feed_ids = {feed['feed_id'] for feed in response.json()['feed']}
    assert '333c69c8afe947ba887fd6404428b31c' not in feed_ids
    assert len(feed_ids) == 5

    cursor = pgsql['feeds-pg'].cursor()
    query = """
    INSERT INTO media
        (media_id, media_type, storage_type, storage_settings, updated)
    VALUES
        (
            'media1',
            'image',
            'avatars',
            '{
                "group-id": 1396527,
                "sizes": {
                    "media-1000-750": {
                        "height": 750,
                        "path": "/get-feeds-media/media-1000-750",
                        "width": 702
                    }
                }
            }',
            '2018-12-01T00:00:00.0Z'
    );"""
    cursor.execute(query)

    await taxi_feeds.invalidate_caches()

    response = await taxi_feeds.post('/v1/fetch', json=data)

    assert response.status_code == 200
    feed_ids = {feed['feed_id'] for feed in response.json()['feed']}
    assert '333c69c8afe947ba887fd6404428b31c' in feed_ids
