from aiohttp import web

from stall.client.tracker import tracker
from stall.model.bug_ticket import BugTicket


# pylint: disable=unused-argument,too-many-locals
async def test_product_bug(tap, dataset, api, job, uuid, ext_api,
                           push_events_cache, s3_stubber):
    with tap.plan(15, 'Успешное создание джобы и ее выполнение'):
        product = await dataset.product(
            description='описание продукта',
            images=['https://localhost'],
            valid=9999,
            barcode=[uuid()],
        )
        store = await dataset.store(address='адрес')
        user = await dataset.user(store=store)
        s3_attachments = [
            {'bucket': 'bucket_123',
             'key': 'test/key_123.pdf'},
            {'bucket': 'bucket_234',
             'key': 'test/key_234.pdf'},
        ]
        data = {s3_attachments[0]['key']: 'test_123',
                s3_attachments[1]['key']: 'test_234'}

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_support_product_bug',
            json={
                'product_id': product.product_id,
                'bug_type': 'not_valid',
                'images': ['https://localhost/1', 'https://localhost/2'],
                'comment': 'Проблемы со сроком годности',
                's3_attachments': s3_attachments
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        bug_ticket = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', product.product_id),
                ('bug_type', 'not_valid'),
                ('status', 'creation')
            ],
            limit=5,
        )

        tap.ok(bug_ticket.list, 'Тикет создался')
        tap.eq_ok(len(bug_ticket.list), 1, 'Один тикет')
        ticket = bug_ticket.list[0]
        tap.eq_ok(ticket.vars['store_id'], store.store_id,
                  'В тикет проставился store_id')
        tap.eq_ok(ticket.bug_type, 'not_valid',
                  'bug_type')
        tap.eq_ok(ticket.product_id, product.product_id,
                  'product_id')
        tap.eq_ok(ticket.vars['comment'], 'Проблемы со сроком годности',
                  'comment')
        tap.eq_ok(ticket.vars['s3_attachments'], s3_attachments,
                  's3_attachments')
        tap.eq_ok(ticket.vars['images'],
                  ['https://localhost/1', 'https://localhost/2'],
                  'images')

        async def handler(request):
            if request.message.path == '/':
                return web.json_response(
                    status=201, data={'key': 'LAVKACONTENT-5'})
            if request.message.path == '/LAVKACONTENT-5/' \
                                       'attachments?filename=key_123.pdf':
                return web.json_response(
                    status=201, data={'id': 'file123'})
            if request.message.path == '/LAVKACONTENT-5/' \
                                       'attachments?filename=key_234.pdf':
                return web.json_response(
                    status=201, data={'id': 'file234'})
            return web.json_response(
                status=404, data={})

        for attachment in s3_attachments:
            s3_stubber.for_get_object_ok(
                bucket=attachment['bucket'],
                key=attachment['key'],
                data=data[attachment['key']].encode('utf-8')
            )
            s3_stubber.for_delete_object_ok(
                bucket=attachment['bucket'], key=attachment['key'],
            )
        s3_stubber.activate()

        await push_events_cache(ticket, job_method='job_create_bug_ticket')

        async with await ext_api(tracker, handler):
            await job.call(await job.take())

        await ticket.reload()
        tap.eq_ok(ticket.ticket_key, 'LAVKACONTENT-5', 'ticket_key')
        tap.eq_ok(ticket.status, 'active', 'Статус поменялся')
        tap.eq_ok(ticket.vars['st_attachments'],
                  {'key_123.pdf': 'file123', 'key_234.pdf': 'file234'},
                  'Изображения прикреплены')
        tap.eq_ok(ticket.vars['s3_attachments'], [],
                  'Ссылки на s3 удалены')


async def test_wrong_product(tap, api, dataset):
    with tap.plan(3, 'несуществующий продукт'):
        user = await dataset.user()
        t = await api(user=user)

        await t.post_ok(
            'api_tsd_support_product_bug',
            json={
                'product_id': '123',
                'bug_type': 'not_valid'
            },
        )

        t.status_is(403, diag=True)
        bug_ticket = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', '123'),
                ('bug_type', 'not_valid'),
                ('status', 'creation')
            ],
            limit=5,
        )

        tap.eq_ok(bug_ticket.list, [],
                  'для несуществующего продукта не создается тикет')


async def test_ticket_exist(tap, api, dataset, ext_api, job,
                            push_events_cache):
    with tap.plan(4, 'если есть старый незакрытый тикет, новый не создается'):
        store = await dataset.store(
            address='адрес'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        old_ticket = await BugTicket(
            {
                'bug_type': 'not_valid',
                'product_id': product.product_id,
                'ticket_key': 'LAVKACONTENT-5',
            }
        ).save()

        async def handler(request):
            data = [
                {
                    'key': 'LAVKACONTENT-5',
                    'status': {'key': 'active'}
                }
            ]
            return web.json_response(status=200, data=data)

        t = await api(user=user)
        async with await ext_api(tracker, handler):
            await t.post_ok(
                'api_tsd_support_product_bug',
                json={
                    'product_id': product.product_id,
                    'bug_type': 'not_valid'
                },
            )
        t.status_is(200, diag=True)

        await push_events_cache(old_ticket, job_method='job_create_bug_ticket')

        async with await ext_api(tracker, handler):
            await job.call(await job.take())

        bug_ticket = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', product.product_id),
                ('bug_type', 'not_valid'),
                ('status', 'active')
            ],
            limit=5,
        )

        tap.eq_ok(len(bug_ticket.list), 1, 'только 1 тикет в работе')
        tap.eq_ok(bug_ticket.list[0].bug_ticket_id,
                  old_ticket.bug_ticket_id, 'только старый тикет остался')


async def test_old_ticket_exist(tap, api, dataset, ext_api, job,
                                push_events_cache):
    with tap.plan(10, 'старый тикет закроется, создастся новый'):
        store = await dataset.store(
            address='адрес'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        ticket = await BugTicket(
            {
                'bug_type': 'not_valid',
                'product_id': product.product_id,
                'ticket_key': 'LAVKACONTENT-5',
            }
        ).save()

        requests = []
        async def handler(request):
            requests.append(request)
            if len(requests) == 1:
                data = [
                    {
                        'key': 'LAVKACONTENT-5',
                        'status': {'key': 'closed'}
                    }
                ]
                return web.json_response(status=200, data=data)

            data = {
                'key': 'LAVKACONTENT-6'
            }
            return web.json_response(status=201, data=data)

        t = await api(user=user)
        async with await ext_api(tracker, handler):
            await t.post_ok(
                'api_tsd_support_product_bug',
                json={
                    'product_id': product.product_id,
                    'bug_type': 'not_valid',
                    'comment': 'test_comment'
                },
            )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await push_events_cache(ticket, job_method='job_create_bug_ticket')

        async with await ext_api(tracker, handler):
            await job.call(await job.take())

        bug_ticket = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', product.product_id),
                ('bug_type', 'not_valid'),
                ('status', 'active')
            ],
            limit=5,
        )

        tap.ok(bug_ticket.list, 'Тикет создался')
        tap.eq_ok(len(bug_ticket.list), 1, 'Один тикет')
        tap.eq_ok(bug_ticket.list[0].bug_type, 'not_valid', 'bug_type')
        tap.eq_ok(bug_ticket.list[0].product_id, product.product_id,
                  'product_id')
        tap.eq_ok(bug_ticket.list[0].ticket_key, 'LAVKACONTENT-6',
                  'Информация из трекера проставилась')
        tap.eq_ok(bug_ticket.list[0].vars['comment'], 'test_comment', 'comment')

        await ticket.reload()
        tap.eq_ok(ticket.status, 'closed',
                  'статус устаревшего тикета изменился')


async def test_ticket_processing(tap, api, dataset):
    with tap.plan(4, 'Тикет уже в процессе'):
        product = await dataset.product()
        await BugTicket(
            {
                'bug_type': 'not_valid',
                'product_id': product.product_id,
                'status': 'creation'
            }
        ).save()

        store = await dataset.store(
            address='адрес'
        )
        user = await dataset.user(
            store=store
        )

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_support_product_bug',
            json={
                'product_id': product.product_id,
                'bug_type': 'not_valid'
            },
        )

        t.status_is(429, diag=True)
        t.json_has('message')
        t.json_is('message', 'Already processing')
