import pytest

import tests_feeds.feeds_common as fc


@pytest.mark.pgsql('feeds-pg', files=['remove_feeds.sql'])
@pytest.mark.parametrize('is_recursive', [True, False, None])
@pytest.mark.now('2018-12-01T01:00:00Z')
async def test_remove(taxi_feeds, pgsql, is_recursive):
    response = await taxi_feeds.post(
        '/v1/remove_by_request_id',
        json={
            'service': 'service',
            'request_id': 'req_1',
            'recursive': is_recursive,
        },
    )
    assert response.status_code == 200

    recursive = is_recursive if is_recursive is not None else True

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        'SELECT service_id, request_id, recursive, max_created '
        'FROM remove_requests_by_request_id',
    )
    assert cursor.fetchall() == [
        (1, 'req_1', recursive, fc.make_msk_datetime(2018, 12, 1, 4, 0)),
    ]

    response = await taxi_feeds.post(
        '/v1/fetch',
        json={'service': 'service', 'channels': ['user:1', 'user:2']},
    )
    request_ids = set(feed['request_id'] for feed in response.json()['feed'])
    assert 'req_1' not in request_ids
    assert 'req_2' in request_ids


@pytest.mark.pgsql('feeds-pg', files=['remove_feeds.sql'])
@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': 'description',
            'max_feed_ttl_hours': 1,
            'polling_delay_sec': 60,
            'max_sync_delete': 2,
        },
    },
)
@pytest.mark.parametrize('is_recursive', [True, False, None])
@pytest.mark.now('2018-12-01T01:00:00Z')
async def test_sync_remove(taxi_feeds, pgsql, is_recursive):
    response = await taxi_feeds.post(
        '/v1/remove_by_request_id',
        json={
            'service': 'service',
            'request_id': 'req_1',
            'recursive': is_recursive,
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """SELECT count(*) FROM feeds WHERE request_id = 'req_1';""",
    )
    assert cursor.fetchone()[0] == 0

    response = await taxi_feeds.post(
        '/v1/remove_by_request_id',
        json={
            'service': 'service',
            'request_id': 'req_3',
            'recursive': is_recursive,
        },
    )
    assert response.status_code == 200

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        """SELECT count(*) FROM feeds WHERE request_id = 'req_3';""",
    )
    assert cursor.fetchone()[0] == 3


@pytest.mark.pgsql('feeds-pg', files=['remove_feeds.sql'])
@pytest.mark.parametrize(
    'channels,expected_user1_request_ids,expected_user2_request_ids',
    [
        ([], {'req_1', 'req_2', 'req_3'}, {'req_1', 'req_2'}),
        (['user:1'], {'req_2', 'req_3'}, {'req_1', 'req_2'}),
        (['user:2'], {'req_1', 'req_2', 'req_3'}, {'req_2'}),
        (['user:1', 'user:2'], {'req_2', 'req_3'}, {'req_2'}),
    ],
    ids=['no_users', 'user_1', 'user_2', 'all_users'],
)
@pytest.mark.now('2018-12-01T01:00:00Z')
async def test_remove_with_channels(
        taxi_feeds,
        pgsql,
        channels,
        expected_user1_request_ids,
        expected_user2_request_ids,
):
    async def _get_request_ids(channel):
        response = await taxi_feeds.post(
            '/v1/fetch', json={'service': 'service', 'channels': [channel]},
        )
        assert response.status_code == 200
        return set(feed['request_id'] for feed in response.json()['feed'])

    assert await _get_request_ids('user:1') == {'req_1', 'req_2', 'req_3'}
    assert await _get_request_ids('user:2') == {'req_1', 'req_2'}

    response = await taxi_feeds.post(
        '/v1/remove_by_request_id',
        json={
            'service': 'service',
            'request_id': 'req_1',
            'channels': channels,
        },
    )
    assert response.status_code == 200

    # Sync delete - no remove requests created
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute('SELECT * FROM remove_requests_by_request_id')
    assert cursor.fetchall() == []

    assert await _get_request_ids('user:1') == expected_user1_request_ids
    assert await _get_request_ids('user:2') == expected_user2_request_ids
