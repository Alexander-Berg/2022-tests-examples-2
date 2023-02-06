import argparse
import asyncio

from aiohttp import web
import aiomysql

HTTP_TIMEOUT = 10


def main():
    parser = argparse.ArgumentParser(
        description='Testsuite service integration example.',
    )
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument(
        '--mysql-host', help='MySQL hostname', default='localhost',
    )
    parser.add_argument(
        '--mysql-port', help='MySQL port', type=int, default=3306,
    )
    parser.add_argument('--mysql-user', help='MySQL user', default='root')
    parser.add_argument(
        '--mysql-dbname', help='MySQL database', default='chat_messages',
    )
    args = parser.parse_args()
    routes = web.RouteTableDef()

    @routes.get('/ping')
    async def handle_ping(request):
        return web.Response(text='OK.')

    @routes.post('/messages/send')
    async def post(request):
        data = await request.json()
        async with app['pool'].acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    'INSERT INTO messages(username, text) VALUES (%s, %s) ',
                    (data['username'], data['text']),
                )
            await connection.commit()
        return web.json_response({'id': cursor.lastrowid})

    @routes.post('/messages/retrieve')
    async def get(request):
        async with app['pool'].acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    'SELECT created, username, text FROM messages '
                    'ORDER BY created DESC LIMIT 20',
                )
                messages = [
                    {
                        'created': record[0].isoformat(),
                        'username': record[1],
                        'text': record[2],
                    }
                    for record in await cursor.fetchall()
                ]
        return web.json_response({'messages': messages})

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(_init_app(args))
    app.add_routes(routes)
    web.run_app(app, port=args.port)


async def _init_app(args):
    app = web.Application()
    app['pool'] = await aiomysql.create_pool(
        host=args.mysql_host,
        port=args.mysql_port,
        user=args.mysql_user,
        db=args.mysql_dbname,
    )
    app.on_shutdown.append(on_shutdown)
    return app


async def on_shutdown(app):
    app['pool'].close()
    await app['pool'].wait_closed()


if __name__ == '__main__':
    main()
