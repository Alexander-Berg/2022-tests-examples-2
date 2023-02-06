import pytest

import tests_feeds.feeds_common as fc

SELECT_FEEDS = """SELECT
       Sv.name, C.name,
       F.request_id, F.payload
   FROM feeds F
   JOIN services Sv ON (Sv.id = F.service_id)
   JOIN feed_channel_status S ON (S.feed_id = F.feed_id)
   JOIN channels C ON (C.id = S.channel_id)
   ORDER BY Sv.name DESC, C.name"""


@pytest.mark.pgsql('feeds-pg', files=['feeds_db.sql'])
@pytest.mark.parametrize(
    'url', ['/v1/batch/remove', '/v1/batch/remove_by_request_id'],
)
@pytest.mark.now('2019-12-12T00:00:00Z')
async def test_remove_feed_by_request_id(taxi_feeds, pgsql, url):
    response = await taxi_feeds.post(
        url,
        json={
            'items': [
                {'service': 'service', 'request_id': 'my_notification'},
                {'service': 'other_service', 'request_id': 'my_news'},
            ],
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        'SELECT service_id, request_id, recursive, max_created '
        'FROM remove_requests_by_request_id ORDER BY service_id',
    )
    assert cursor.fetchall() == [
        (1, 'my_notification', True, fc.make_msk_datetime(2019, 12, 12, 3, 0)),
        (2, 'my_news', True, fc.make_msk_datetime(2019, 12, 12, 3, 0)),
    ]


@pytest.mark.parametrize(
    'items,code',
    [
        (
            [
                {'service': 'service', 'request_id': 'my_notification'},
                {'service': 'other_service', 'request_id': 'my_news'},
                {'service': 'other_service', 'request_id': 'my_news'},
            ],
            200,
        ),
        (
            [
                {'service': 'service', 'request_id': 'my_notification'},
                {'service': 'other_service', 'request_id': 'my_news'},
                {'service': 'new_service', 'request_id': 'my_news'},
            ],
            400,
        ),
    ],
)
@pytest.mark.parametrize(
    'url', ['/v1/batch/remove', '/v1/batch/remove_by_request_id'],
)
@pytest.mark.pgsql('feeds-pg', files=['feeds_db.sql'])
async def test_unknown_service(taxi_feeds, pgsql, items, code, url):
    response = await taxi_feeds.post(url, json={'items': items})
    assert response.status_code == code


@pytest.mark.pgsql('feeds-pg', files=['feeds_db.sql'])
async def test_batch_hide_feeds(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/batch/remove',
        json={
            'items': [
                {
                    'service': 'other_service',
                    'feed_id': '75e46d20e0d941c1af604d354dd46ca0',
                    'channels': ['user:1'],
                    'meta': {'id': 1},
                },
                {
                    'service': 'service',
                    'feed_id': '36f29b888314418fb8836d7400eb3c43',
                    'channels': ['user:1'],
                    'meta': {'id': 2},
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'statuses': {
            '36f29b888314418fb8836d7400eb3c43': 200,
            '75e46d20e0d941c1af604d354dd46ca0': 200,
        },
    }
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """
       SELECT feed_id, status, meta FROM feed_channel_status
       WHERE feed_id IN (
           '36f29b888314418fb8836d7400eb3c43',
           '75e46d20e0d941c1af604d354dd46ca0'
       )
       ORDER BY feed_id;
    """,
    )
    assert list(cursor) == [
        ('36f29b88-8314-418f-b883-6d7400eb3c43', 'removed', {'id': 2}),
        ('75e46d20-e0d9-41c1-af60-4d354dd46ca0', 'removed', {'id': 1}),
    ]


@pytest.mark.pgsql('feeds-pg', files=['feeds_db.sql'])
async def test_batch_hide_feeds_404(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/batch/remove',
        json={
            'items': [
                {
                    'service': 'other_service',
                    'feed_id': '75e46d20e0d941c1af604d354dd46ca0',
                    'channels': ['user:1'],
                },
                {
                    'service': 'service',
                    'feed_id': '45916989c7154d6285c2bd1c13533f26',
                    'channels': ['user:1'],
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'statuses': {
            '45916989c7154d6285c2bd1c13533f26': 404,
            '75e46d20e0d941c1af604d354dd46ca0': 200,
        },
    }


@pytest.mark.pgsql('feeds-pg', files=['feeds_db.sql'])
async def test_batch_hide_feeds_duplicate(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/batch/remove',
        json={
            'items': [
                {
                    'service': 'other_service',
                    'feed_id': '75e46d20e0d941c1af604d354dd46ca0',
                    'channels': ['user:1'],
                },
                {
                    'service': 'other_service',
                    'feed_id': '75e46d20e0d941c1af604d354dd46ca0',
                    'channels': ['user:1'],
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'statuses': {'75e46d20e0d941c1af604d354dd46ca0': 200},
    }


@pytest.mark.pgsql('feeds-pg', files=['test_batch_parent_feed.sql'])
@pytest.mark.now('2019-12-12T00:00:00Z')
async def test_remove_feed_by_request_id_parent_feeds(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/batch/remove_by_request_id',
        json={
            'items': [
                {
                    'service': 'service',
                    'request_id': 'my_news',
                    'recursive': True,
                },
                {
                    'service': 'other_service',
                    'request_id': 'my_news',
                    'recursive': False,
                },
            ],
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(SELECT_FEEDS)
    cursor.execute(
        'SELECT service_id, request_id, recursive, max_created '
        'FROM remove_requests_by_request_id ORDER BY service_id',
    )
    assert cursor.fetchall() == [
        (1, 'my_news', True, fc.make_msk_datetime(2019, 12, 12, 3, 0)),
        (2, 'my_news', False, fc.make_msk_datetime(2019, 12, 12, 3, 0)),
    ]
