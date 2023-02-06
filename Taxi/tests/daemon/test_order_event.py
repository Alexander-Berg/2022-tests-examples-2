# pylint: disable=redefined-outer-name,unused-argument,unused-variable

import pytest
from aiohttp import web_response, ClientResponseError

from stall.client import order_event_client
from stall.daemon.order_event import Daemon


async def test_send_list(tap, events_factory, client, ext_api):
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
            daemon = Daemon()
            result = await daemon.send_list('external', events)
            tap.eq(result, events, 'all events proceeded')


async def test_send_list_500(tap, events_factory, client, ext_api):
    async def handle(request):
        data = await request.json()

        return web_response.json_response(status=500)

    with tap:
        events = await events_factory(tap, 1)

        async with await ext_api(client, handle):
            daemon = Daemon()
            with tap.raises(ClientResponseError):
                await daemon.send_list('external', events)


async def test_send_list_runtime(tap, events_factory, client, ext_api):
    async def handle(request):
        data = await request.json()

        return web_response.json_response({
            'code': 'ERROR',
            'message': '__message__'
        })

    with tap:
        events = await events_factory(tap, 1)

        async with await ext_api(client, handle):
            daemon = Daemon()
            with tap.raises(RuntimeError):
                await daemon.send_list('external', events)


async def test_send_list_unknown_source(tap, events_factory, client, ext_api):
    async def handle(request):
        data = await request.json()

        return web_response.json_response(status=500)

    with tap:
        events = await events_factory(tap, 1)

        async with await ext_api(client, handle):
            daemon = Daemon()
            result = await daemon.send_list('__unknown__', events)
            tap.eq(result, events, 'unknown source returns all items')


async def test_process_items(tap, events_factory, client, ext_api):
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
            daemon = Daemon()
            result = await daemon.process_items(events)
            tap.eq(result, events, 'all events proceeded')


async def test_process_items_500(tap, events_factory, client, ext_api):
    async def handle(request):
        data = await request.json()

        return web_response.json_response(status=500)

    with tap:
        events = await events_factory(tap, 5)

        async with await ext_api(client, handle):
            daemon = Daemon()
            result = await daemon.process_items(events)
            tap.eq(result, [], 'none events proceeded')


async def test_process_items_runtime(tap, events_factory, client, ext_api):
    async def handle(request):
        data = await request.json()

        return web_response.json_response({
            'code': 'ERROR',
            'message': '__message__'
        })

    with tap:
        events = await events_factory(tap, 5)

        async with await ext_api(client, handle):
            daemon = Daemon()
            result = await daemon.process_items(events)
            tap.eq(result, [], 'none events proceeded')


async def test_process_items_limit(tap, events_factory, client, ext_api, cfg):
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
        cfg.set('business.daemon.order_events.items_limit', 2)
        events = await events_factory(tap, 5)

        async with await ext_api(client, handle):
            daemon = Daemon()
            result = await daemon.process_items(events)
            tap.eq(result, events[:2], 'first two events proceeded')


@pytest.fixture()
async def events_factory(dataset, uuid):
    async def wrapper(tap, events_count):
        store = await dataset.store()
        orders = [
            await dataset.order(
                store_job_event=True,
                store_id=store.store_id,
                external_id=uuid(),
                source='external',
            )
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
