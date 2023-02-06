import pytest

import tests_feeds.feeds_common as fc


@pytest.mark.pgsql('feeds-pg', files=['test_log_status.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_smoke(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/log_status',
        json={
            'service': 'service',
            'feed_id': '111c69c8afe947ba887fd6404428b31c',
            'channel': 'user:123',
            'status': 'read',
            'meta': {'page_id': 'news'},
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        f"""SELECT count(*) FROM channels WHERE name = 'user:123';""",
    )
    assert list(cursor) == [(1,)]

    cursor.execute(
        """SELECT S.feed_id, S.status, S.created
         FROM feed_channel_status S JOIN channels C ON (S.channel_id = C.id)
         WHERE C.name = 'user:123';
    """,
    )
    assert list(cursor) == [
        (
            '111c69c8-afe9-47ba-887f-d6404428b31c',
            'read',
            fc.make_msk_datetime(2018, 12, 2, 3, 0, 0),
        ),
    ]


@pytest.mark.pgsql('feeds-pg', files=['test_log_status.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_viewed_status(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/log_status',
        json={
            'service': 'service',
            'feed_id': '111c69c8afe947ba887fd6404428b31c',
            'channel': 'user:123',
            'status': 'viewed',
            'meta': {'page_id': 'news'},
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        f"""SELECT count(*) FROM channels WHERE name = 'user:123';""",
    )
    assert list(cursor) == [(1,)]

    cursor.execute(
        """SELECT S.feed_id, S.status, S.created
         FROM feed_channel_status S JOIN channels C ON (S.channel_id = C.id)
         WHERE C.name = 'user:123';
    """,
    )
    assert list(cursor) == [
        (
            '111c69c8-afe9-47ba-887f-d6404428b31c',
            'viewed',
            fc.make_msk_datetime(2018, 12, 2, 3, 0, 0),
        ),
    ]


@pytest.mark.pgsql('feeds-pg', files=['test_log_status.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.parametrize(
    'feed_id,status,expected_code',
    [
        ('111c69c8afe947ba887fd6404428b31c', 'confirmed', 400),
        ('222c69c8afe947ba887fd6404428b31c', 'read', 404),
    ],
    ids=['bad status', 'feed not exists'],
)
async def test_bad_requests(taxi_feeds, feed_id, status, expected_code):
    response = await taxi_feeds.post(
        '/v1/log_status',
        json={
            'service': 'service',
            'feed_id': f'{feed_id}',
            'channel': 'user:123',
            'status': f'{status}',
        },
    )
    assert response.status_code == expected_code


@pytest.mark.pgsql('feeds-pg', files=['test_log_status.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
@pytest.mark.parametrize(
    'feed_ids,status,expected_code',
    [
        (['111c69c8afe947ba887fd6404428b31c'], 'confirmed', 400),
        (
            [
                '222c69c8afe947ba887fd6404428b31c',
                '332c69c8afe947ba887fd6404428b31c',
            ],
            'read',
            200,
        ),
    ],
    ids=['bad status', 'feed not exists'],
)
async def test_bad_requests_many_feeds(
        taxi_feeds, feed_ids, status, expected_code,
):
    response = await taxi_feeds.post(
        '/v1/log_status',
        json={
            'service': 'service',
            'feed_ids': feed_ids,
            'channel': 'user:123',
            'status': f'{status}',
        },
    )
    assert response.status_code == expected_code


@pytest.mark.pgsql('feeds-pg', files=['test_log_status.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_bad_requests_no_feed_id_and_no_feed_ids(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/log_status',
        json={'service': 'service', 'channel': 'user:123', 'status': 'read'},
    )
    assert response.status_code == 400


@pytest.mark.pgsql('feeds-pg', files=['test_log_status.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_bad_requests_feed_id_and_feed_ids(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/log_status',
        json={
            'service': 'service',
            'channel': 'user:123',
            'status': 'read',
            'feed_id': '111c69c8afe947ba887fd6404428b31c',
            'feed_ids': ['111c69c8afe947ba887fd6404428b31c'],
        },
    )
    assert response.status_code == 400


@pytest.mark.pgsql('feeds-pg', files=['test_log_status.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_not_found_and_found_feed_id_and_existed_feed_ids(taxi_feeds):
    response = await taxi_feeds.post(
        '/v1/log_status',
        json={
            'service': 'service',
            'channel': 'user:123',
            'status': 'read',
            'feed_ids': [
                '111c69c8afe947ba887fd6404428b31c',
                '222c69c8afe947ba887fd6404428b31c',
            ],
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'meta,expected_meta',
    [
        (None, {'info': 'feed1 for moscow'}),
        ({'page_id': 'news'}, {'page_id': 'news'}),
    ],
)
@pytest.mark.pgsql('feeds-pg', files=['test_meta.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_meta(taxi_feeds, pgsql, meta, expected_meta):
    request_data = {
        'service': 'service',
        'feed_id': '111c69c8afe947ba887fd6404428b31c',
        'channel': 'city:moscow',
        'status': 'read',
    }
    if meta:
        request_data['meta'] = meta
    response = await taxi_feeds.post('/v1/log_status', json=request_data)

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """
        SELECT meta, status FROM feed_channel_status
        WHERE feed_id = '111c69c8afe947ba887fd6404428b31c'
        AND channel_id = 0
    """,
    )
    feed_statuses = list(cursor)
    assert len(feed_statuses) == 1
    feed_status = feed_statuses[0]
    meta, status = feed_status
    assert meta == expected_meta
    assert status == 'read'


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'Service for test',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'statistics': {'enable': True, 'remove_delay_sec': 120},
        },
    },
)
@pytest.mark.pgsql('feeds-pg', files=['test_meta_statistics.sql'])
@pytest.mark.now('2018-12-02T00:00:00Z')
async def test_meta_statistics(taxi_feeds, testpoint, pgsql):
    @testpoint('update-statistics')
    def update_statistics(data):
        pass

    request_data = {
        'service': 'service',
        'feed_id': '111c69c8afe947ba887fd6404428b31c',
        'channel': 'driver:1',
        'status': 'read',
        'meta': {'actions': ['like']},
    }
    response = await taxi_feeds.post('/v1/log_status', json=request_data)

    assert response.status_code == 200

    await update_statistics.wait_call()

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """
        SELECT meta_counters FROM feeds_statistics
        WHERE request_id = 'request_1'
        AND service_id = 1
    """,
    )
    meta_counters = list(cursor)[0]
    assert meta_counters[0] == {'like': 2}

    request_data = {
        'service': 'service',
        'feed_id': '111c69c8afe947ba887fd6404428b31c',
        'channel': 'driver:2',
        'status': 'read',
        'meta': {'actions': ['like', 'dislike']},
    }
    response = await taxi_feeds.post('/v1/log_status', json=request_data)

    assert response.status_code == 200

    await update_statistics.wait_call()

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """
        SELECT meta_counters FROM feeds_statistics
        WHERE request_id = 'request_1'
        AND service_id = 1
    """,
    )
    meta_counters = list(cursor)[0]
    assert meta_counters[0] == {'like': 2, 'dislike': 1}

    request_data = {
        'service': 'service',
        'feed_id': '111c69c8afe947ba887fd6404428b31c',
        'channel': 'driver:2',
        'status': 'read',
        'meta': {},
    }
    response = await taxi_feeds.post('/v1/log_status', json=request_data)

    assert response.status_code == 200

    await update_statistics.wait_call()

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """
        SELECT meta_counters FROM feeds_statistics
        WHERE request_id = 'request_1'
        AND service_id = 1
    """,
    )
    meta_counters = list(cursor)[0]
    assert meta_counters[0] == {'like': 1, 'dislike': 0}

    request_data = {
        'service': 'service',
        'feed_id': '111c69c8afe947ba887fd6404428b31c',
        'channel': 'driver:2',
        'status': 'read',
        'meta': {'actions': 1},
    }
    response = await taxi_feeds.post('/v1/log_status', json=request_data)

    assert response.status_code == 200

    await update_statistics.wait_call()

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """
        SELECT meta_counters FROM feeds_statistics
        WHERE request_id = 'request_1'
        AND service_id = 1
    """,
    )
    meta_counters = list(cursor)[0]
    assert meta_counters[0] == {'like': 1, 'dislike': 0}

    request_data = {
        'service': 'service',
        'feed_id': '222c69c8afe947ba887fd6404428b31c',
        'channel': 'driver:2',
        'status': 'read',
        'meta': {'actions': ['like']},
    }
    response = await taxi_feeds.post('/v1/log_status', json=request_data)

    assert response.status_code == 200

    await update_statistics.wait_call()

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """
        SELECT meta_counters FROM feeds_statistics
        WHERE request_id = 'request_2'
        AND service_id = 1
    """,
    )
    meta_counters = list(cursor)[0]
    assert meta_counters[0] == {'like': 1}
