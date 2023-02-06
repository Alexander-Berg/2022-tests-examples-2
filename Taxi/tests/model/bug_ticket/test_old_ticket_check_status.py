import pytest
from aiohttp import web

from stall.model.bug_ticket import BugTicket
from stall.client.tracker import tracker


async def test_old_ticket_closed(tap, dataset, ext_api):
    store1 = await dataset.store(
        address='address',
    )
    store2 = await dataset.store()

    product = await dataset.product(
        images=['https://xxx.com/bad.png', 'https://extra.com/wow.png']
    )

    old_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'active',
            'ticket_key': 'KEY-333',
            'vars': {
                'store_id': store1.store_id,
                'comment': 'сегодня мой последний день в яндексе',
                'images': [],
                'new_ticket_data': {
                    'store_id': store2.store_id,
                    'comment': 'я вас очень люблю <3',
                    'images': [],
                }
            }
        }
    ).save()

    # pylint: disable=unused-argument
    async def handler(request):
        data = [
            {
                'key': 'KEY-333',
                'status': {'key': 'closed'}
            }
        ]
        return web.json_response(status=200, data=data)

    with tap.plan(6, 'в трекере подобный тикет уже закрыт, создаем новый'):
        async with await ext_api(tracker, handler):
            new_ticket = await old_ticket.old_ticket_check_status()

        await old_ticket.reload()
        tap.eq_ok(old_ticket.status, 'closed', 'закрылся старый тикет')

        tap.ok(new_ticket, 'новый тикет')
        tap.eq_ok(new_ticket.product_id, product.product_id, 'product_id')
        tap.eq_ok(new_ticket.status, 'creation', 'status == creation')
        tap.eq_ok(new_ticket.vars['store_id'], store2.store_id, 'store_id')
        tap.eq_ok(new_ticket.vars['comment'], 'я вас очень люблю <3', 'правда')


@pytest.mark.parametrize('data', [
    [
        {
            'key': 'KEY-333',
            'status': {'key': 'open'}
        }
    ],
    []
])
async def test_old_ticket_open(tap, ext_api, data):
    old_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': '123',
            'status': 'active',
            'ticket_key': 'KEY-333'
        }
    ).save()

    # pylint: disable=unused-argument
    async def handler(request):
        return web.json_response(status=200, data=data)

    with tap.plan(2, 'старый тикет еще не закрыт или не найден, '
                     'новый не создается'):
        async with await ext_api(tracker, handler):
            new_ticket = await old_ticket.old_ticket_check_status()

        await old_ticket.reload()

        tap.eq_ok(old_ticket.status, 'active',
                  'Статус старого тикета не поменялся')
        tap.eq_ok(new_ticket, None, 'Новый тикет не создавался')


async def test_old_ticket_no_answer(tap, ext_api):
    old_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': '123',
            'status': 'active',
            'ticket_key': 'KEY-333'
        }
    ).save()

    # pylint: disable=unused-argument
    async def handler(request):
        return web.json_response(status=404)

    with tap.plan(2, 'Нет ответа от трекера - не создаем тикет'):
        async with await ext_api(tracker, handler):
            with tap.raises(Exception):
                await old_ticket.old_ticket_check_status()

        await old_ticket.reload()

        tap.eq_ok(old_ticket.status, 'active',
                  'Статус старого тикета не поменялся')


async def test_restart_job(tap):
    old_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': '123',
            'status': 'closed',
            'ticket_key': 'KEY-333'
        }
    ).save()
    new_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': '123',
            'status': 'creation',
            'ticket_key': 'KEY-444'
        }
    ).save()
    with tap.plan(1, 'если джоба со старым тикетом перезапустилась, а новый '
                     'тикет уже был создан, вернен уже созданный тикет'):
        new = await old_ticket.old_ticket_check_status()
        tap.eq_ok(new.bug_ticket_id, new_ticket.bug_ticket_id,
                  'возвращает уже созданный тикет')


async def test_no_new_tickets(tap):
    with tap.plan(1, 'если джоба со старым тикетом перезапустилась, а нового '
                     'тикета нет, ничего не вернет'):
        old_ticket = await BugTicket(
            {
                'bug_type': 'other_product',
                'product_id': '345',
                'status': 'closed',
                'ticket_key': 'KEY-345'
            }
        ).save()
        new = await old_ticket.old_ticket_check_status()
        tap.is_ok(new, None, 'new ticket not found')
