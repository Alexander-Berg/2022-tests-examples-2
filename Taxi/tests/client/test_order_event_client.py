# pylint: disable=redefined-outer-name,unused-argument,unused-variable

import pytest
from aiohttp import web_response, ClientResponseError

from libstall import cfg
from stall.client import order_event_client


async def test_get_client(tap):
    with tap:
        options = cfg('business.order_events')
        for option in options:
            order_event_client.get_client(option['source'])


async def test_client_singleton(tap):
    with tap:
        client_1 = order_event_client.get_client('external')
        client_2 = order_event_client.get_client('external')
        tap.is_ok(client_1, client_2, 'get_client is singleton')


async def test_500(tap, client, events_factory, ext_api):
    async def handle(request):
        return web_response.json_response(status=500)

    with tap:
        events = await events_factory(tap, 1)

        async with await ext_api(client, handle):
            with tap.raises(ClientResponseError):
                await client.send_bulk(events)


async def test_400(tap, client, events_factory, ext_api):
    async def handle(request):
        return web_response.json_response(status=400)

    with tap:
        events = await events_factory(tap, 1)

        async with await ext_api(client, handle):
            with tap.raises(ClientResponseError):
                await client.send_bulk(events)


async def test_send_empty(tap, client, ext_api):
    async def handle(request):
        return web_response.json_response(status=500)

    with tap:
        async with await ext_api(client, handle):
            await client.send_bulk([])
            tap.passed('empty request not proceeded')


async def test_send_bulk_common(tap, events_factory, client, ext_api):
    async def handle(request):
        data = await request.json()

        return web_response.json_response({
            'code': 'OK',
            'details': {
                'results': [{
                    'code': 'OK',
                    'event_id': event['event_id']
                } for event in data['events']]
            }
        })

    with tap:
        events = await events_factory(tap, 5)

        async with await ext_api(client, handle):
            result = await client.send_bulk(events)
            tap.eq(result, events, 'all events proceeded')


@pytest.mark.parametrize('code', ['ERROR', 'WARNING'])
async def test_failed_all(tap, client, events_factory, ext_api, code):
    async def handle(request):
        data = await request.json()

        return web_response.json_response({
            'code': code,
            'message': '__message__'
        })

    with tap:
        events = await events_factory(tap, 5)

        async with await ext_api(client, handle):
            result = await client.send_bulk(events)
            tap.eq(result, [], 'none events proceeded')


@pytest.mark.parametrize('code', ['ERROR', 'WARNING'])
async def test_failed_some(tap, client, events_factory, ext_api, code):
    async def handle(request):
        data = await request.json()

        return web_response.json_response({
            'code': 'OK',
            'details': {
                'results': [{
                    'code': code,
                    'event_id': event['event_id'],
                    'message': '__message__'
                } for event in data['events'][:1]] + [{
                    'code': 'OK',
                    'event_id': event['event_id'],
                } for event in data['events'][1:]]
            }
        })

    with tap:
        events = await events_factory(tap, 2)

        async with await ext_api(client, handle):
            result = await client.send_bulk(events)
            tap.eq(result, events[1:], 'only second event proceeded')


async def test_fallback(tap, client, events_factory, ext_api):
    async def handle(request):
        data = await request.json()

        return web_response.json_response({'code': 'OK'})

    with tap:
        events = await events_factory(tap, 5)

        async with await ext_api(client, handle):
            result = await client.send_bulk(events)
            tap.eq(result, events, 'all event proceeded by fallback')


@pytest.fixture()
async def events_factory(dataset, uuid):
    async def wrapper(tap, events_count):
        orders = [
            await dataset.order(store_job_event=True, external_id=uuid())
            for _ in range(events_count)
        ]
        tap.isa(orders, list, 'orders created')

        events = []
        for order in orders:
            events.extend(await dataset.OrderEvent.list_by_order(order))

        tap.isa(events, list, 'events created')
        tap.eq(len(events), len(orders), 'event for each order')

        return events

    yield wrapper


@pytest.fixture()
def client(tvm_ticket):
    client = order_event_client.get_client('external')
    yield client
