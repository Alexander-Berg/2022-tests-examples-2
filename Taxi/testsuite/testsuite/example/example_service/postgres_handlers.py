from aiohttp import web
import asyncpg

ROUTES = web.RouteTableDef()


@ROUTES.post('/postgres/create')
async def post(request):
    row = await request.json()
    value = row['payload']
    connection: asyncpg.connection.Connection
    async with _pg_connection(request) as connection:
        row_id = await connection.fetchval(
            'INSERT INTO example_table(payload) VALUES ($1) RETURNING id',
            value,
        )
    return web.json_response({'id': row_id})


@ROUTES.get('/postgres/{id}')
async def get(request):
    row_id = int(request.match_info['id'])
    connection: asyncpg.connection.Connection
    async with _pg_connection(request) as connection:
        record: asyncpg.protocol.Record = await connection.fetchrow(
            'SELECT id, payload FROM example_table WHERE id = $1', row_id,
        )
    json = {**record}
    return web.json_response(json)


def _pg_connection(request) -> asyncpg.connection.Connection:
    pool: asyncpg.pool.Pool = request.app['postgres_connection_pool']
    return pool.acquire()
