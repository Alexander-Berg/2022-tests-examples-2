import pytest


def _get_service_tags(service, pgsql):
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        f"""SELECT name FROM tags
            WHERE
              service_id = (
                SELECT id FROM services WHERE name = '{service}'
              );""",
    )
    return {row[0] for row in cursor}


def _get_request_tags(service, request_id, pgsql):
    cursor = pgsql['feeds-pg'].cursor()
    cursor.execute(
        f"""SELECT tags.name
            FROM (
               SELECT unnest(tags) as tag_id
               FROM feeds
               WHERE
                  service_id = (
                    SELECT id FROM services WHERE name = '{service}'
                  )
                  AND
                  request_id = '{request_id}'
            ) as feeds
            JOIN tags ON (tag_id = tags.id);""",
    )
    return {row[0] for row in cursor}


@pytest.mark.now('2019-12-01T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_create_with_tags.sql'])
async def test_create_with_tags(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/create',
        json={
            'service': 'service',
            'request_id': 'r',
            'payload': {},
            'channels': [{'channel': 'channel'}],
            'tags': ['a', 'b'],
        },
    )

    assert response.status_code == 200
    assert _get_service_tags('service', pgsql) == {'a', 'b'}
    assert _get_request_tags('service', 'r', pgsql) == {'a', 'b'}


@pytest.mark.now('2019-12-01T00:00:00Z')
@pytest.mark.pgsql('feeds-pg', files=['test_create_with_tags.sql'])
async def test_batch_create_with_tags(taxi_feeds, pgsql):
    response = await taxi_feeds.post(
        '/v1/batch/create',
        json={
            'items': [
                {
                    'service': 'service',
                    'request_id': 'r1',
                    'tags': ['a', 'b', 'x'],
                    'payload': {},
                    'channels': [{'channel': 'channel'}],
                },
                {
                    'service': 'service',
                    'request_id': 'r2',
                    'tags': ['b', 'c', 'd'],
                    'payload': {},
                    'channels': [{'channel': 'channel'}],
                },
                {
                    'service': 'other_service',
                    'request_id': 'r3',
                    'tags': ['a', 'b'],
                    'payload': {},
                    'channels': [{'channel': 'channel'}],
                },
            ],
        },
    )

    assert response.status_code == 200
    assert _get_service_tags('service', pgsql) == {'a', 'b', 'c', 'd', 'x'}
    assert _get_request_tags('service', 'r1', pgsql) == {'a', 'b', 'x'}
    assert _get_request_tags('service', 'r2', pgsql) == {'b', 'c', 'd'}

    assert _get_service_tags('other_service', pgsql) == {'a', 'b'}
    assert _get_request_tags('other_service', 'r3', pgsql) == {'a', 'b'}
