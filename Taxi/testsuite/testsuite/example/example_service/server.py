import argparse
import asyncio

import aiohttp
from aiohttp import web
import asyncpg
from motor import motor_asyncio

from . import mongo_handlers
from . import postgres_handlers

HTTP_TIMEOUT = 10
ROUTES = web.RouteTableDef()


def main():
    parser = argparse.ArgumentParser(
        description='Testsuite service integration example.',
    )
    parser.add_argument(
        '--service-baseurl',
        default='http://localhost/',
        help='Test service base url',
    )
    parser.add_argument(
        '--mongo-uri',
        default='http://localhost:27017/',
        help='mongodb connection uri',
    )
    parser.add_argument('--postgresql', help='PostgreSQL connection string')
    args = parser.parse_args()

    @ROUTES.get('/ping')
    async def handle_ping(request):
        return web.Response(text='OK.')

    @ROUTES.get('/hello')
    async def handle_hello(request):
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                args.service_baseurl + 'test', timeout=HTTP_TIMEOUT,
            )
            response.raise_for_status()
            who = await response.text()
        return web.Response(text=f'Hello, {who}')

    app = web.Application()
    app.add_routes(mongo_handlers.ROUTES)
    app.add_routes(postgres_handlers.ROUTES)
    app.add_routes(ROUTES)
    app['mongo_collection'] = _mongo_collection(args.mongo_uri)
    app['postgres_connection_pool'] = _pg_connection_pool(args.postgresql)
    web.run_app(app)


def _mongo_collection(mongo_uri: str) -> motor_asyncio.AsyncIOMotorCollection:
    connection = motor_asyncio.AsyncIOMotorClient(mongo_uri)
    database = connection['example_db']
    collection = database['example_collection']
    return collection


def _pg_connection_pool(connection_string) -> asyncpg.pool.Pool:
    connection_params = _pg_connection_params(connection_string)
    pool = asyncio.get_event_loop().run_until_complete(
        asyncpg.create_pool(**connection_params),
    )
    return pool


def _pg_connection_params(postgres_conn_str: str) -> dict:
    postgres_conn_str += 'service_name_example_db'
    params = {
        'database' if key == 'dbname' else key: value
        for key, value in (
            substring.strip().split('=', maxsplit=1)
            for substring in postgres_conn_str.split()
        )
    }
    return params


if __name__ == '__main__':
    main()
