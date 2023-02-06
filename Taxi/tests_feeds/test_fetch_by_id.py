import pytest


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_one_feed(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'feed_id': '111c69c8afe947ba887fd6404428b31c',
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        'feed': [
            {
                'feed_id': '111c69c8afe947ba887fd6404428b31c',
                'package_id': 'p1',
                'request_id': 'request_1',
                'created': '2018-12-01T00:00:00+0000',
                'expire': '2019-12-01T00:00:00+0000',
                'last_status': {
                    'status': 'read',
                    'created': '2018-12-02T00:00:00+0000',
                },
                'payload': {'text': 'feed1'},
            },
        ],
    }


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_not_found_feed(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['channel:1'],
            'feed_id': 'aaac69c8afe947ba887fd6404428b31c',
        },
    )

    assert response.status_code == 404


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_many_feed(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['channel:1'],
            'feed_ids': [
                '111c69c8afe947ba887fd6404428b31c',
                '222c69c8afe947ba887fd6404428b31c',
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()
    feed_1 = {
        'feed_id': '111c69c8afe947ba887fd6404428b31c',
        'created': '2018-12-01T00:00:00+0000',
        'expire': '2019-12-01T00:00:00+0000',
        'package_id': 'p1',
        'request_id': 'request_1',
        'last_status': {
            'status': 'published',
            'created': '2018-12-01T00:00:00+0000',
        },
        'payload': {'text': 'feed1'},
    }
    feed_2 = {
        'feed_id': '222c69c8afe947ba887fd6404428b31c',
        'package_id': 'p1',
        'request_id': 'request_1',
        'created': '2018-12-01T00:00:00+0000',
        'expire': '2019-12-01T00:00:00+0000',
        'last_status': {
            'status': 'read',
            'created': '2018-12-01T00:00:00+0000',
        },
        'payload': {'text': 'feed2'},
    }
    assert feed_1 in data['feed']
    assert feed_2 in data['feed']
    assert len(data['feed']) == 2


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_feed_from_other_service(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'other_service',
            'channels': ['channel:1'],
            'feed_id': '111c69c8afe947ba887fd6404428b31c',
        },
    )

    assert response.status_code == 404


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_removed_feed(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'feed_id': '333c69c8afe947ba887fd6404428b31c',
        },
    )

    assert response.status_code == 404


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_id.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_not_published_feed(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'feed_id': '555c69c8afe947ba887fd6404428b31c',
        },
    )

    assert response.status_code == 404


@pytest.mark.pgsql('feeds-pg', files=['test_fetch_by_id.sql'])
@pytest.mark.now('2019-01-02T00:00:00Z')
async def test_expire_feed(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['channel:1', 'channel:2'],
            'feed_id': '666c69c8afe947ba887fd6404428b31c',
        },
    )

    assert response.status_code == 404


@pytest.mark.pgsql('feeds-pg', files=['test_meta.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_fetch_meta(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['city:moscow', 'driver:1'],
            'feed_ids': [
                '111c69c8afe947ba887fd6404428b31c',
                '222c69c8afe947ba887fd6404428b31c',
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['feed'] == [
        {
            'feed_id': '222c69c8afe947ba887fd6404428b31c',
            'package_id': 'p1',
            'request_id': 'request_1',
            'created': '2018-12-01T00:00:00+0000',
            'expire': '2019-12-01T00:00:00+0000',
            'last_status': {
                'status': 'published',
                'created': '2018-12-02T00:00:00+0000',
            },
            'payload': {'text': 'feed2'},
            'meta': {'info': 'feed2 for driver:1'},
        },
    ]


@pytest.mark.pgsql('feeds-pg', files=['test_meta_statistics.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_fetch_meta_statistics(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['city:moscow', 'driver:2'],
            'feed_ids': ['111c69c8afe947ba887fd6404428b31c'],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['feed'] == [
        {
            'feed_id': '111c69c8afe947ba887fd6404428b31c',
            'package_id': 'p1',
            'request_id': 'request_1',
            'created': '2018-12-01T00:00:00+0000',
            'expire': '2019-12-01T00:00:00+0000',
            'last_status': {
                'status': 'viewed',
                'created': '2018-12-02T00:00:00+0000',
            },
            'payload': {'text': 'feed1'},
            'meta': {'actions': ['like']},
            'statistics': {'meta': {'like': 1}},
        },
    ]


@pytest.mark.pgsql('feeds-pg', files=['test_payload_args.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_payload_args(taxi_feeds, load_json):
    response = await taxi_feeds.post(
        '/v1/fetch_by_id',
        json={
            'service': 'service',
            'channels': ['user:1', 'user:2'],
            'feed_ids': [
                '75e46d20e0d941c1af604d354dd46ca0',
                '38672090b4ef4a3382d064c6d9642971',
                '57422b02229e42bdac084c589c4024c2',
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()
    feeds = {feed['feed_id']: feed for feed in data['feed']}

    assert feeds == load_json('payload_args_feeds.json')
