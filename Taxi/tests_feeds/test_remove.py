import pytest


FEED_ID = '3fac69c8afe947ba887fd6404428b31c'


@pytest.mark.pgsql('feeds-pg', files=['remove_feeds.sql'])
async def test_remove_from_channels(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': 'service',
            'feed_id': FEED_ID,
            'channels': ['park:1', 'park:2'],
            'meta': {'reason': 'closed'},
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'statuses': {'3fac69c8afe947ba887fd6404428b31c': 200},
    }

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        f"""SELECT C.name, S.status, S.meta
         FROM feed_channel_status S JOIN channels C ON (C.id = S.channel_id)
         WHERE S.feed_id = '{FEED_ID}'
         ORDER BY C.name;""",
    )
    assert cursor.fetchall() == [
        ('city:moscow', 'published', None),
        ('park:1', 'removed', {'reason': 'closed'}),
        ('park:2', 'removed', {'reason': 'closed'}),
    ]


@pytest.mark.pgsql('feeds-pg', files=['remove_feeds.sql'])
async def test_remove_feed_from_other_service(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': 'other_service',
            'feed_id': FEED_ID,
            'channels': ['city:moscow', 'park:100500'],
        },
    )
    assert response.status_code == 404


@pytest.mark.pgsql('feeds-pg', files=['remove_feeds.sql'])
async def test_remove_feed_not_exist(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': 'other_service',
            'feed_id': FEED_ID,
            'channels': ['city:moscow', 'park:100500'],
        },
    )
    assert response.status_code == 404


@pytest.mark.pgsql('feeds-pg', files=['remove_feeds.sql'])
async def test_remove_feed_from_other_service_many_feeds(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': 'other_service',
            'feed_ids': ['111111c8afe947ba887fd6404428b31c'],
            'channels': ['city:moscow', 'park:100500'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'statuses': {'111111c8afe947ba887fd6404428b31c': 404},
    }

    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': 'other_service',
            'feed_id': '111111c8afe947ba887fd6404428b31c',
            'channels': ['city:moscow', 'park:100500'],
        },
    )
    assert response.status_code == 404


@pytest.mark.pgsql('feeds-pg', files=['remove_feeds.sql'])
async def test_remove_feed_bad_request(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': 'other_service',
            'channels': ['city:moscow', 'park:100500'],
        },
    )
    assert response.status_code == 400

    response = await taxi_feeds.post(
        '/v1/remove',
        json={
            'service': 'other_service',
            'feed_id': '111111c8afe947ba887fd6404428b31c',
            'feed_ids': ['111111c8afe947ba887fd6404428b31c'],
            'channels': ['city:moscow', 'park:100500'],
        },
    )
    assert response.status_code == 400
