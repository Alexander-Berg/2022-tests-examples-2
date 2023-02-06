import pytest


@pytest.mark.pgsql('feeds-pg', files=['insert_feed.sql'])
async def test_upload(taxi_feeds, pgsql):
    lon1, lat1, priority = -111, 48, 123
    lon2, lat2 = -112, 49
    response = await taxi_feeds.post(
        '/v1/upload_geo',
        {
            'service': 'service',
            'feed_id': '75e46d20e0d941c1af604d354dd46ca0',
            'points': [
                {
                    'point': {'latitude': lat1, 'longitude': lon1},
                    'priority': priority,
                },
                {'point': {'latitude': lat2, 'longitude': lon2}},
            ],
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT lon, lat, priority FROM geo_markers;')
    assert set(cursor) == set(((lon1, lat1, priority), (lon2, lat2, 0)))
