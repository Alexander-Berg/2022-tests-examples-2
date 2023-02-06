import pytest


@pytest.mark.pgsql(
    'example_db',
    queries=['INSERT INTO example_table(id, payload) VALUES (10, \'mark\')'],
)
async def test_read_preexisting_using_mark(server_client, pgsql):
    response = await server_client.get('postgres/10')
    assert response.status_code == 200
    json = response.json()
    assert json == {'id': 10, 'payload': 'mark'}


async def test_read_preexisting_using_static_file(server_client, pgsql):
    # static/test_postgres_handlers/pg_example_db.sql
    response = await server_client.get('postgres/20')
    assert response.status_code == 200
    json = response.json()
    assert json == {'id': 20, 'payload': 'static_file'}


async def test_create(server_client, pgsql):
    response = await server_client.post(
        'postgres/create', json={'payload': 'foo'},
    )
    assert response.status_code == 200
    json = response.json()
    assert 'id' in json
    row_id = json['id']
    assert isinstance(row_id, int)
    cursor = pgsql['example_db'].cursor()
    cursor.execute(
        'SELECT payload from example_table WHERE id = %s', (row_id,),
    )
    result = list(row[0] for row in cursor)
    assert result == ['foo']
