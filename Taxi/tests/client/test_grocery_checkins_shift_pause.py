import asyncio

import aiohttp
import pytest
from aiohttp import web

from stall.client.grocery_checkins import GroceryCheckinsClient
from stall.client.grocery_checkins import GroceryCheckinsError


async def test_common(tap, dataset, ext_api, now, time2iso):
    with tap.plan(1, 'вызов ручки с корректными параметрами'):
        _calls = []

        async def handle(request):
            data = await request.json()
            _calls.append(data)
            return {}

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(store=store, courier=courier)

        paused_at = now()

        async with await ext_api('grocery_checkins', handle) as cli:
            cli: GroceryCheckinsClient
            await cli.shift_pause(
                shift.courier_shift_id,
                courier.courier_id,
                paused_at,
            )
            tap.eq(_calls, [{
                'performer_id': courier.courier_id,
                'shift_id': shift.courier_shift_id,
                'paused_at': time2iso(paused_at),
            }], 'one call has been handled')


@pytest.mark.parametrize('client_error', [
        aiohttp.ClientError,
        asyncio.TimeoutError,
])
async def test_client_error(tap, ext_api, now, uuid, client_error):
    with tap.plan(1, f'GroceryCheckinsError при {client_error.__name__}'):
        # pylint: disable=unused-argument
        async def handle(request):
            raise client_error

        async with await ext_api('grocery_checkins', handle) as cli:
            cli: GroceryCheckinsClient
            with tap.raises(GroceryCheckinsError):
                await cli.shift_pause(uuid(), uuid(), now())


@pytest.mark.parametrize('status', [400, 401, 403, 500, 504])
async def test_response_error(tap, ext_api, now, uuid, status):
    with tap.plan(1, f'GroceryCheckinsError при status={status}'):
        # pylint: disable=unused-argument
        async def handle(request):
            return web.Response(status=status)

        async with await ext_api('grocery_checkins', handle) as cli:
            cli: GroceryCheckinsClient
            with tap.raises(GroceryCheckinsError):
                await cli.shift_pause(uuid(), uuid(), now())
