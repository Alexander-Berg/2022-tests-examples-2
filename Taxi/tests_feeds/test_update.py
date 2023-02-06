import tests_feeds.feeds_common as fc


async def test_empty_create(taxi_feeds, pgsql):
    feed_id = '606b4d46-5889-465e-9c89-c6dd9737f9c4'
    channel = 'user:1'

    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'request_id': 'request_id_0',
            'service': 'service',
            'payload': {'text': 'Very important feed'},
            'feed_id': feed_id,
        },
    )

    assert response.status_code == 200
    updated_payload = {'text': 'Not very important feed'}
    await taxi_feeds.invalidate_caches()

    response = await taxi_feeds.post(
        '/v1/update',
        json={
            'service': 'service',
            'feed_id': feed_id,
            'channels': [
                {'channel': channel, 'payload_overrides': updated_payload},
            ],
        },
    )

    assert response.status_code == 200

    [(db_feed_id, db_channel)] = fc.run_script(
        pgsql,
        """
        SELECT feed_id, channels.name
        FROM feed_channel_status
        INNER JOIN channels ON channels.id = feed_channel_status.channel_id""",
    )
    assert db_feed_id == feed_id and db_channel == channel
