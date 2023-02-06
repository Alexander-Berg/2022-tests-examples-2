import argparse
import asyncio
from aiohttp import web

from stall.model.bug_ticket import BugTicket
from stall.client.tracker import tracker
from scripts.cron.update_bug_tickets import update_bug_ticket, main


# pylint: disable=unused-argument
async def test_update_bug_ticket(tap, dataset, ext_api):
    product = await dataset.product()
    ticket_1 = BugTicket(
        {
            'bug_type': 'not_valid',
            'product_id': product.product_id,
            'ticket_key': 'TESTIK-5',
        }
    )
    await ticket_1.save()
    ticket_2 = BugTicket(
        {
            'bug_type': 'barcode',
            'product_id': product.product_id,
            'ticket_key': 'TESTIK-7',
        }
    )
    await ticket_2.save()

    requests = []

    async def handler(request):
        requests.append(request)
        if len(requests) == 1:
            data = [
                {
                    'key': 'TESTIK-5',
                    'status': {'key': 'closed'}
                },
                {
                    'key': 'TESTIK-7',
                    'status': {'key': 'status'}
                }
            ]
            return web.json_response(status=200, data=data)

        return web.json_response(
            {}
        )

    with tap.plan(2, 'обновление тикетов'):
        async with await ext_api(tracker, handler) as client:
            tickets_data = await client.check_ticket_status(
                ['TESTIK-5', 'TESTIK-7']
            )

        bug_tickets = await BugTicket.list(
            by='look',
            conditions=[('product_id', product.product_id)],
        )

        await update_bug_ticket(bug_tickets, tickets_data, apply=True)

        await ticket_1.reload()
        await ticket_2.reload()

        tap.eq_ok(ticket_1.status, 'closed', 'проставился статус TESTIK-5')
        tap.eq_ok(ticket_2.status, 'active', 'статус не поменялся TESTIK-7')


async def test_update_one_ticket(tap, dataset, ext_api):
    product = await dataset.product()
    ticket = BugTicket(
        {
            'bug_type': 'not_valid',
            'product_id': product.product_id,
            'ticket_key': 'TESTIK-10',
        }
    )
    await ticket.save()

    async def handler(request):
        data = [
            {
                'key': 'TESTIK-10',
                'status': {'key': 'closed'}
            }
        ]
        return web.json_response(status=200, data=data)

    args = argparse.Namespace(apply=True, bug_ticket_id=ticket.bug_ticket_id,
                              mode='production')

    with tap.plan(1, 'обновлен тикет'):
        async with await ext_api(tracker, handler):
            await main(args)

        await ticket.reload()

        tap.eq_ok(ticket.status, 'closed', 'статус тикета обновлен')


async def test_can_not_connect(tap, dataset, ext_api):
    product = await dataset.product()
    ticket = BugTicket(
        {
            'bug_type': 'not_valid',
            'product_id': product.product_id,
            'ticket_key': 'TESTIK-10',
        }
    )
    await ticket.save()

    async def handler(request):
        return web.json_response(status=400)

    args = argparse.Namespace(apply=True, bug_ticket_id=ticket.bug_ticket_id,
                              mode='production')

    with tap.plan(1, 'тикет не был обновлен'):
        async with await ext_api(tracker, handler):
            await main(args)

        await ticket.reload()

        tap.eq_ok(ticket.status, 'active', 'статус тикета не изменился')


async def test_timeout(tap, ext_api):
    async def handler(request):
        await asyncio.sleep(100)
        return 1

    with tap.plan(1, 'тикет не был обновлен'):
        async with await ext_api(tracker, handler) as bad_client:
            res = await bad_client.check_ticket_status(['TESTIK-10'])

        tap.eq_ok(res, None, 'статус тикета не изменился')



