import pytest

SELECT_STATUSES = 'SELECT feed_id, status, meta FROM feed_channel_status'


@pytest.mark.pgsql('feeds-pg', files=['feeds_db.sql'])
async def test_batch_log_status(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/batch/log_status',
        json={
            'items': [
                {
                    'service': 'other_service',
                    'feed_id': '75e46d20e0d941c1af604d354dd46ca0',
                    'channel': 'user:1',
                    'status': 'read',
                    'meta': {'info': 'new'},
                },
                {
                    'service': 'service',
                    'feed_id': '36f29b888314418fb8836d7400eb3c43',
                    'channel': 'user:1',
                    'status': 'read',
                },
                {
                    'service': 'other_service',  # wrong service
                    'feed_id': '36f29b888314418fb8836d7400eb3c43',
                    'channel': 'user:1',
                    'status': 'read',
                },
                {
                    'service': 'service',
                    # not in db
                    'feed_id': 'ca21113e4dd543e39a76d2e03d862043',
                    'channel': 'user:1',
                    'status': 'read',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'75e46d20e0d941c1af604d354dd46ca0': 200},
            {'36f29b888314418fb8836d7400eb3c43': 200},
            {'36f29b888314418fb8836d7400eb3c43': 404},
            {'ca21113e4dd543e39a76d2e03d862043': 404},
        ],
    }

    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(SELECT_STATUSES)
    for row in cursor:
        feed_id, status, meta = row
        feed_id = feed_id.replace('-', '')
        if feed_id == '75e46d20e0d941c1af604d354dd46ca0':
            assert status == 'read'
            assert meta == {'info': 'new'}
        elif feed_id == '36f29b888314418fb8836d7400eb3c43':
            assert status == 'read'
            assert meta == {'v': 2}
        else:
            assert status == 'published'
            assert not meta
