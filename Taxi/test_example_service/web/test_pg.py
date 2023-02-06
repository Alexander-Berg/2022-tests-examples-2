import pytest


@pytest.mark.parametrize(
    '_id, code, answer',
    [
        (2387, 200, 'b'),
        (
            10,
            404,
            {
                'code': 'not-found',
                'message': 'Rows with required key are not found',
            },
        ),
    ],
)
async def test_postgresql_get_by_id(_id, code, answer, web_app_client):
    response = await web_app_client.get(
        '/postgresql/get_by_id', params={'id': _id},
    )
    assert response.status == code
    if code == 200:
        assert await response.text() == answer
    else:
        assert await response.json() == answer


async def test_postgresql_insert_once(web_app_client, pgsql):
    key = 'simple_key'
    name = 'Beta'
    shard = (hash(key) + hash(name)) % 2
    body = {'key': key, 'name': name}
    response = await web_app_client.post('/postgresql/insert_row', json=body)
    assert response.status == 200
    content = await response.text()
    assert content == 'OK'

    cursor = pgsql['database_3@%s' % shard].cursor()
    cursor.execute(
        """
        SELECT key
        FROM test.test_table_3
        WHERE name = %s
    """,
        ('Beta',),
    )

    assert list(cursor) == [('simple_key',)]


async def test_postgresql_insert_twice(web_app_client, pgsql):
    body = {'key': 'simple_key', 'name': 'Beta'}
    await web_app_client.post('/postgresql/insert_row', json=body)
    response = await web_app_client.post('/postgresql/insert_row', json=body)
    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'conflict',
        'message': 'Trying to insert already added row',
    }


async def test_insert(web_app_client):
    response = await web_app_client.post('/pg/insert')
    assert response.status == 200


async def test_fetch(web_app_client):
    response = await web_app_client.get('/pg/fetch')
    assert response.status == 200


async def test_fetch_fastest(web_app_client):
    response = await web_app_client.get('/pg/fetch-fastest')
    assert response.status == 200
