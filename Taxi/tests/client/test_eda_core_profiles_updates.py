import asyncio

import aiohttp
import pytest
from aiohttp import web

from stall.client.eda_core import EdaCoreError


async def test_common(tap, ext_api):
    with tap.plan(8, 'получаем курсор и данные'):
        profiles = [{
            'gender': 'male',
            'birthday': '2000-04-01',
            'is_storekeeper': None,
            'is_rover': None,
        }, {
            'gender': 'female',
            'birthday': None,
            'is_storekeeper': False,
            'is_rover': None,
        }, {
            'gender': None,
            'birthday': '2022-01-01',
            'is_storekeeper': True,
            'is_rover': None,
        }, {
            'gender': None,
            'birthday': None,
            'is_storekeeper': None,
            'is_rover': True,
        }, {
            'gender': None,
            'birthday': None,
            'is_storekeeper': None,
            'is_rover': False,
        }]

        async def handle(request):
            cursor = int(request.query['cursor'] or '0')
            limit = int(request.query.get('limit', 1))

            return {
                'cursor': str(cursor + limit),
                'profiles': profiles[cursor:cursor+limit],
            }

        async with await ext_api('eda_core', handle) as client:
            cursor, profiles = await client.profiles_updates(
                cursor='0', limit=1,
            )
            tap.eq(cursor, '1', 'cursor ok')
            tap.eq(profiles, profiles[0:1], 'profiles ok')

            cursor, profiles = await client.profiles_updates(
                cursor='0', limit=2,
            )
            tap.eq(cursor, '2', 'cursor ok')
            tap.eq(profiles, profiles[0:2], 'profiles ok')

            cursor, profiles = await client.profiles_updates(
                cursor='2', limit=1,
            )
            tap.eq(cursor, '3', 'cursor ok')
            tap.eq(profiles, profiles[2:3], 'profiles ok')

            cursor, profiles = await client.profiles_updates(
                cursor='3', limit=2,
            )
            tap.eq(cursor, '5', 'cursor ok')
            tap.eq(profiles, profiles[3:5], 'profiles ok')


@pytest.mark.parametrize('client_error', [
        aiohttp.ClientError,
        asyncio.TimeoutError,
])
async def test_client_error(tap, ext_api, client_error):
    # pylint: disable=unused-argument
    async def handle(request):
        raise client_error

    with tap.plan(1, f'EdaCoreError при {client_error.__name__}'):
        async with await ext_api('eda_core', handle) as client:
            with tap.raises(EdaCoreError):
                await client.profiles_updates(cursor='0', limit=1)


@pytest.mark.parametrize('status', [400, 401, 403, 500, 504])
async def test_response_error(tap, ext_api, status):
    # pylint: disable=unused-argument
    async def handle(request):
        return web.Response(status=status)

    with tap.plan(1, f'EdaCoreError при status={status}'):
        async with await ext_api('eda_core', handle) as client:
            with tap.raises(EdaCoreError):
                await client.profiles_updates(cursor='0', limit=1)


async def test_wrong_format(tap, ext_api):
    # pylint: disable=unused-argument
    async def handle(request):
        return web.Response(text='1. not_json')

    with tap.plan(1, 'EdaCoreError при некорректном json'):
        async with await ext_api('eda_core', handle) as client:
            with tap.raises(EdaCoreError):
                await client.profiles_updates(cursor='0', limit=1)


@pytest.mark.parametrize('response', [
    {'cursor': ''},
    {'profiles': []},
    {'cursor': None, 'profiles': []},
    {'profiles': None},
    {},
])
async def test_wrong_data(tap, ext_api, response):
    # pylint: disable=unused-argument
    async def handle(request):
        return response

    with tap.plan(1, 'EdaCoreError при некорректных данных'):
        async with await ext_api('eda_core', handle) as client:
            with tap.raises(EdaCoreError):
                await client.profiles_updates(cursor='0', limit=1)
