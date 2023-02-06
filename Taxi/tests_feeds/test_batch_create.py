import pytest

import tests_feeds.feeds_common as fc


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_batch_create(taxi_feeds, pgsql):
    now = fc.make_msk_datetime(2019, 12, 1, 3, 0, 0)
    expire1 = fc.make_msk_datetime(2019, 12, 2, 3, 0, 0)
    expire2 = fc.make_msk_datetime(2019, 12, 3, 3, 0, 0)

    response = await taxi_feeds.post(
        '/v1/batch/create',
        json={
            'items': [
                {
                    'package_id': 'pack1',
                    'request_id': 'my_news',
                    'service': 'service',
                    'expire': expire1.strftime('%Y-%m-%dT%H:%M:%S%z'),
                    'payload': {
                        'title': 'Hello, {name}!',
                        'text': 'How do you do?',
                    },
                    'channels': [
                        {
                            'channel': 'user:1',
                            'payload_params': {'name': 'Vladimir'},
                        },
                        {
                            'channel': 'user:2',
                            'payload_params': {'name': 'Ivan'},
                            'payload_overrides': {'cost': 10.2},
                        },
                        {
                            'channel': 'city:omsk',
                            'payload_params': {'name': 'Omsk'},
                        },
                    ],
                    'status': 'read',
                    'meta': {'data': 'news_meta'},
                },
                {
                    'package_id': 'pack2',
                    'request_id': 'my_notification',
                    'service': 'other_service',
                    'expire': expire2.strftime('%Y-%m-%dT%H:%M:%S%z'),
                    'payload': {'title': '{name}, you have new message'},
                    'channels': [
                        {
                            'channel': 'user:1',
                            'payload_params': {'name': 'Vladimir'},
                        },
                        {
                            'channel': 'user:2',
                            'payload_params': {'name': 'Ivan'},
                        },
                    ],
                    'status': 'viewed',
                    'meta': {'data': 'notification_meta'},
                },
            ],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """SELECT
               Sv.name, C.name,
               F.package_id, F.request_id, F.created, F.publish_at, F.expire,
               F.payload,
               FP.payload_overrides,
               FP.payload_params
           FROM feeds F
           JOIN services Sv ON (Sv.id = F.service_id)
           JOIN feed_channel_status S ON (S.feed_id = F.feed_id)
           JOIN channels C ON (C.id = S.channel_id)
           JOIN feed_payload FP ON (S.feed_id = FP.feed_id
                                    AND S.channel_id = FP.channel_id)
           ORDER BY Sv.name DESC, C.name""",
    )

    feeds = list(cursor)
    print(feeds[0])
    assert feeds == [
        (
            'service',
            'city:omsk',
            'pack1',
            'my_news',
            now,
            now,
            expire1,
            {'title': 'Hello, {name}!', 'text': 'How do you do?'},
            None,
            '{"(name,Omsk)"}',
        ),
        (
            'service',
            'user:1',
            'pack1',
            'my_news',
            now,
            now,
            expire1,
            {'title': 'Hello, {name}!', 'text': 'How do you do?'},
            None,
            '{"(name,Vladimir)"}',
        ),
        (
            'service',
            'user:2',
            'pack1',
            'my_news',
            now,
            now,
            expire1,
            {'title': 'Hello, {name}!', 'text': 'How do you do?'},
            {'cost': 10.2},
            '{"(name,Ivan)"}',
        ),
        (
            'other_service',
            'user:1',
            'pack2',
            'my_notification',
            now,
            now,
            expire2,
            {'title': '{name}, you have new message'},
            None,
            '{"(name,Vladimir)"}',
        ),
        (
            'other_service',
            'user:2',
            'pack2',
            'my_notification',
            now,
            now,
            expire2,
            {'title': '{name}, you have new message'},
            None,
            '{"(name,Ivan)"}',
        ),
    ]

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT status, meta FROM feed_channel_status')

    channel_statuses = list(cursor)
    assert len(channel_statuses) == 5
    for row in channel_statuses:
        status, meta = row
        assert status in {'read', 'viewed'}
        assert meta['data'] in {'notification_meta', 'news_meta'}


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_same_service_and_channel(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/batch/create',
        json={
            'items': [
                {
                    'package_id': 'p1',
                    'request_id': 'r1',
                    'service': 'service',
                    'payload': {'title': 'Request 1'},
                    'channels': [{'channel': 'user:1'}],
                },
                {
                    'package_id': 'p2',
                    'request_id': 'r2',
                    'service': 'service',
                    'payload': {'title': 'Request 2'},
                    'channels': [{'channel': 'user:1'}],
                },
            ],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """SELECT
               Sv.name, C.name, F.package_id, F.request_id, F.payload
           FROM feeds F
           JOIN services Sv ON (Sv.id = F.service_id)
           JOIN feed_channel_status S ON (S.feed_id = F.feed_id)
           JOIN channels C ON (C.id = S.channel_id)
           ORDER BY Sv.name DESC, C.name""",
    )

    feeds = list(cursor)
    assert feeds == [
        ('service', 'user:1', 'p1', 'r1', {'title': 'Request 1'}),
        ('service', 'user:1', 'p2', 'r2', {'title': 'Request 2'}),
    ]


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_client_provided_feed_id(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/batch/create',
        json={
            'items': [
                {
                    'service': 'service',
                    'request_id': 'request_id',
                    'payload': {'text': 'text'},
                    'channels': [
                        {
                            'channel': 'has_feed_id',
                            'feed_id': 'b78a4c19beec418d9ec091ef1d146952',
                        },
                        {'channel': 'no_feed_id'},
                    ],
                },
                {
                    'service': 'other_service',
                    'request_id': 'request_id',
                    'payload': {'text': 'text'},
                    'channels': [
                        {
                            'channel': 'has_feed_id',
                            'feed_id': 'ab29b1f7479b407ab9d2cb18fc1e34e4',
                        },
                        {'channel': 'no_feed_id'},
                    ],
                },
            ],
        },
    )

    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """SELECT Sv.name, C.name, F.feed_id
           FROM feeds F
           JOIN services Sv ON (Sv.id = F.service_id)
           JOIN feed_channel_status S ON (S.feed_id = F.feed_id)
           JOIN channels C ON (C.id = S.channel_id)
           ORDER BY Sv.name DESC, C.name""",
    )

    feeds = list(cursor)
    assert len(feeds) == 4
    assert feeds[0] == (
        'service',
        'has_feed_id',
        'b78a4c19-beec-418d-9ec0-91ef1d146952',
    )
    assert feeds[1][0:2] == ('service', 'no_feed_id')
    assert feeds[1][2] != 'b78a4c19-beec-418d-9ec0-91ef1d146952'

    assert feeds[2] == (
        'other_service',
        'has_feed_id',
        'ab29b1f7-479b-407a-b9d2-cb18fc1e34e4',
    )
    assert feeds[3][0:2] == ('other_service', 'no_feed_id')
    assert feeds[3][2] != 'ab29b1f7-479b-407a-b9d2-cb18fc1e34e4'


@pytest.mark.now('2019-12-01T00:00:00Z')
async def test_get_id(taxi_feeds, pgsql):
    expire = fc.make_msk_datetime(2019, 12, 2, 3, 0, 0)

    response = await taxi_feeds.post(
        '/v1/batch/create',
        json={
            'items': [
                {
                    'package_id': 'pack1',
                    'request_id': 'my_news',
                    'service': 'service',
                    'expire': expire.strftime('%Y-%m-%dT%H:%M:%S%z'),
                    'payload': {
                        'title': 'Hello, {name}!',
                        'text': 'How do you do?',
                    },
                    'channels': [
                        {
                            'channel': 'user:1',
                            'payload_params': {'name': 'Vladimir'},
                        },
                        {
                            'channel': 'user:2',
                            'payload_params': {'name': 'Ivan'},
                            'payload_overrides': {'cost': 10.2},
                        },
                        {
                            'channel': 'city:omsk',
                            'payload_params': {'name': 'Omsk'},
                        },
                    ],
                    'meta': {'data': 'news_meta'},
                },
                {
                    'package_id': 'pack2',
                    'request_id': 'my_notification',
                    'service': 'other_service',
                    'expire': expire.strftime('%Y-%m-%dT%H:%M:%S%z'),
                    'payload': {'title': '{name}, you have new message'},
                    'channels': [
                        {
                            'channel': 'user:1',
                            'payload_params': {'name': 'Vladimir'},
                        },
                        {
                            'channel': 'user:2',
                            'payload_params': {'name': 'Ivan'},
                        },
                    ],
                    'meta': {'data': 'notification_meta'},
                },
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data['items']) == 2

    response_pairs = []
    for item in data['items']:
        for channel, feed_id in item['feed_ids'].items():
            response_pairs.append((feed_id, channel))

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """SELECT f.feed_id, ch.name FROM feed_channel_status f
        JOIN channels ch  ON f.channel_id = ch.id""",
    )
    values_from_db = set()
    for row in cursor:
        feed_id, channel = row
        values_from_db.add((feed_id.replace('-', ''), channel))
    assert values_from_db == set(response_pairs)
