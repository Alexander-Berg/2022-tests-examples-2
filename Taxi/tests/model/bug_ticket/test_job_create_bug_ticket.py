import asyncio
from aiohttp import web

from stall.model.bug_ticket import BugTicket, job_create_bug_ticket
from stall.client.tracker import tracker


# pylint: disable=unused-argument
async def test_job_create_bug_ticket(tap, dataset, ext_api, s3_stubber):
    store = await dataset.store(
        address='address',
    )
    product = await dataset.product(
        images=['https://xxx.com/bad.png', 'https://extra.com/wow.png']
    )

    new_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'creation',
            'vars': {
                'store_id': store.store_id,
                'comment': 'хочу снимать тик токи под подлую еврейскую музыку, '
                           'а не вот это вот все',
                'images': [],
                's3_attachments': [{'bucket': 'bucket_1',
                                    'key': 'test/key_1.pdf'},
                                   {'bucket': 'bucket_2',
                                    'key': 'test/key_2.pdf'}]
            }
        }
    ).save()

    requests = []

    async def handler(request):
        requests.append(request)
        if len(requests) == 1 and request.message.path == '/':
            return web.json_response(status=201,
                                     data={'key': 'LAVKACONTENT-1'})
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_1.pdf':
            return web.json_response(
                status=201, data={'id': 'file1', 'name': 'key_1.pdf'})
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_2.pdf':
            return web.json_response(
                status=201, data={'id': 'file2', 'name': 'key_2.pdf'})

        return web.json_response(
            {}
        )

    data = {'test/key_1.pdf': 'test_1',
            'test/key_2.pdf': 'test_2'}
    for attachment in new_ticket.vars['s3_attachments']:
        s3_stubber.for_get_object_ok(
            bucket=attachment['bucket'],
            key=attachment['key'],
            data=data[attachment['key']].encode('utf-8')
        )
        s3_stubber.for_delete_object_ok(
            bucket=attachment['bucket'], key=attachment['key'],
        )
    s3_stubber.activate()

    with tap.plan(9, 'Успешное создание тикета и работа с клиентом'):
        async with await ext_api(tracker, handler):
            await job_create_bug_ticket(new_ticket.bug_ticket_id)

        bug_tickets = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', product.product_id),
                ('bug_type', 'other_product'),
                ('status', 'active')
            ],
            limit=5,
        )
        tap.ok(bug_tickets, 'В бд 1 запись')
        tap.eq_ok(len(bug_tickets.list), 1, 'Новые записи не создались')

        await new_ticket.reload()
        tap.eq_ok(new_ticket.status, 'active', 'статус проставился')
        tap.eq_ok(new_ticket.bug_type, 'other_product',
                  'тип баги проставился')
        tap.eq_ok(new_ticket.product_id, product.product_id,
                  'продукт прикрепился')
        tap.eq_ok(new_ticket.ticket_key, 'LAVKACONTENT-1',
                  'от клиента получне ключ')
        tap.eq_ok(new_ticket.vars['store_id'], store.store_id,
                  'в варсы проставился стор')
        tap.eq_ok(new_ticket.vars.get('st_attachments'),
                  {'key_1.pdf': 'file1', 'key_2.pdf': 'file2'},
                  'Изображения прикреплены')
        tap.eq_ok(new_ticket.vars.get('s3_attachments'), [],
                  'Ссылки на s3 удалены')


async def test_err_tracker_ticket(tap, dataset, ext_api):
    store = await dataset.store(
        address='address',
    )
    product = await dataset.product()

    new_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'creation',
            'vars': {
                'store_id': store.store_id,
                'comment': 'комментарий',
                'images': [],
                's3_attachments': [{'bucket': 'bucket_1',
                                    'key': 'test/key_1.pdf'}]
            }
        }
    ).save()

    async def handler(request):
        return web.json_response(status=400)

    with tap.plan(2, 'При ошибке подключения к трекеру exception, '
                     'что тикет не создан в треке'):
        async with await ext_api(tracker, handler):
            with tap.raises(Exception):
                await job_create_bug_ticket(new_ticket.bug_ticket_id)

        await new_ticket.reload()
        tap.eq_ok(new_ticket.status, 'creation', 'статус тикета не поменялся')


async def test_err_tracker_ticket_409(tap, dataset, ext_api):
    with tap.plan(5, 'Тикет уже был создан '):
        store = await dataset.store(
            address='address',
        )
        product = await dataset.product()

        new_ticket = await BugTicket(
            {
                'bug_type': 'other_product',
                'product_id': product.product_id,
                'status': 'creation',
                'vars': {
                    'store_id': store.store_id,
                    'comment': 'комментарий',
                    'images': []
                }
            }
        ).save()

        async def handler(request):
            if request.message.path == '/':
                return web.json_response(status=409)
            if request.message.path == '/_search':
                return web.json_response(
                    status=200, data=[{'key': 'LAVKACONTENT-1'}])

        async with await ext_api(tracker, handler):
            await job_create_bug_ticket(new_ticket.bug_ticket_id)

        await new_ticket.reload()
        tap.eq_ok(new_ticket.status, 'active', 'статус проставился')
        tap.eq_ok(new_ticket.bug_type, 'other_product',
                  'тип баги проставился')
        tap.eq_ok(new_ticket.product_id, product.product_id,
                  'продукт прикрепился')
        tap.eq_ok(new_ticket.ticket_key, 'LAVKACONTENT-1',
                  'от клиента получне ключ')
        tap.eq_ok(new_ticket.vars['store_id'], store.store_id,
                  'в варсы проставился стор')


async def test_err_s3_get(tap, dataset, ext_api, s3_stubber):
    store = await dataset.store(
        address='address',
    )
    product = await dataset.product()
    s3_attachments = [{'bucket': 'bucket_1',
                       'key': 'test/key_1.pdf'},
                      {'bucket': 'bucket_2',
                       'key': 'test/key_2.pdf'},
                      {'bucket': 'bucket_3',
                       'key': 'test/key_3.pdf'}]

    new_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'creation',
            'vars': {
                'store_id': store.store_id,
                'comment': 'комментарий',
                'images': [],
                's3_attachments': s3_attachments
            }
        }
    ).save()

    async def handler(request):
        if request.message.path == '/':
            return web.json_response(status=201, data={
                'key': 'LAVKACONTENT-1'
            })
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_1.pdf':
            return web.json_response(
                status=201, data={'id': 'file1', 'name': 'key_1.pdf'})
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_2.pdf':
            return web.json_response(
                status=201, data={'id': 'file2', 'name': 'key_2.pdf'})
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_3.pdf':
            return web.json_response(
                status=201, data={'id': 'file3', 'name': 'key_3.pdf'})

    data = {'test/key_1.pdf': 'test_1', 'test/key_3.pdf': 'test_3'}
    for attachment in s3_attachments:
        if attachment['bucket'] != 'bucket_2':
            s3_stubber.for_get_object_ok(
                bucket=attachment['bucket'],
                key=attachment['key'],
                data=data[attachment['key']].encode('utf-8')
            )
            s3_stubber.for_delete_object_ok(
                bucket=attachment['bucket'],
                key=attachment['key'],
            )
        else:
            s3_stubber.for_get_object_error(
                bucket=attachment['bucket'],
                key=attachment['key'],
                error='NoSuchKey'
            )
    s3_stubber.activate()

    with tap.plan(7, 'Ошибка от s3 при получении изображений'):
        async with await ext_api(tracker, handler):
            await job_create_bug_ticket(new_ticket.bug_ticket_id)

        await new_ticket.reload()
        tap.eq_ok(new_ticket.status, 'active', 'статус проставился')
        tap.eq_ok(new_ticket.bug_type, 'other_product',
                  'тип баги проставился')
        tap.eq_ok(new_ticket.product_id, product.product_id,
                  'продукт прикрепился')
        tap.eq_ok(new_ticket.ticket_key, 'LAVKACONTENT-1',
                  'от клиента получне ключ')
        tap.eq_ok(new_ticket.vars['store_id'], store.store_id,
                  'в варсы проставился стор')
        tap.eq_ok(new_ticket.vars('st_attachments', None),
                  {'key_1.pdf': 'file1', 'key_3.pdf': 'file3'},
                  'Изображения не прикреплены')
        tap.eq_ok(new_ticket.vars.get('s3_attachments'),
                  [s3_attachments[1]],
                  'Ссылки на s3 не удалены')


async def test_err_s3_delete(tap, dataset, ext_api, s3_stubber):
    store = await dataset.store(
        address='address',
    )
    product = await dataset.product()
    s3_attachments = [{'bucket': 'bucket_1',
                       'key': 'test/key_1.pdf'},
                      {'bucket': 'bucket_2',
                       'key': 'test/key_2.pdf'},
                      {'bucket': 'bucket_3',
                       'key': 'test/key_3.pdf'}]

    new_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'creation',
            'vars': {
                'store_id': store.store_id,
                'comment': 'комментарий',
                'images': [],
                's3_attachments': s3_attachments
            }
        }
    ).save()

    async def handler(request):
        if request.message.path == '/':
            return web.json_response(status=201, data={
                'key': 'LAVKACONTENT-1'
            })
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_1.pdf':
            return web.json_response(
                status=201, data={'id': 'file1', 'name': 'key_1.pdf'})
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_2.pdf':
            return web.json_response(
                status=201, data={'id': 'file2', 'name': 'key_2.pdf'})
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_3.pdf':
            return web.json_response(
                status=201, data={'id': 'file3', 'name': 'key_3.pdf'})

    data = {'test/key_1.pdf': 'test_1',
            'test/key_2.pdf': 'test_2',
            'test/key_3.pdf': 'test_3'}
    for attachment in s3_attachments:
        s3_stubber.for_get_object_ok(
            bucket=attachment['bucket'],
            key=attachment['key'],
            data=data[attachment['key']].encode('utf-8')
        )
        if attachment['bucket'] != 'bucket_2':
            s3_stubber.for_delete_object_ok(
                bucket=attachment['bucket'],
                key=attachment['key'],
            )
        else:
            s3_stubber.for_delete_object_error(
                bucket=attachment['bucket'],
                key=attachment['key'],
                error='NoSuchKey'
            )
    s3_stubber.activate()

    with tap.plan(7, 'Ошибка от s3 при получении изображений'):
        async with await ext_api(tracker, handler):
            await job_create_bug_ticket(new_ticket.bug_ticket_id)

        await new_ticket.reload()
        tap.eq_ok(new_ticket.status, 'active', 'статус проставился')
        tap.eq_ok(new_ticket.bug_type, 'other_product',
                  'тип баги проставился')
        tap.eq_ok(new_ticket.product_id, product.product_id,
                  'продукт прикрепился')
        tap.eq_ok(new_ticket.ticket_key, 'LAVKACONTENT-1',
                  'от клиента получне ключ')
        tap.eq_ok(new_ticket.vars['store_id'], store.store_id,
                  'в варсы проставился стор')
        tap.eq_ok(new_ticket.vars('st_attachments', None),
                  {'key_1.pdf': 'file1',
                   'key_2.pdf': 'file2',
                   'key_3.pdf': 'file3'},
                  'Изображения прикреплены')
        tap.eq_ok(new_ticket.vars.get('s3_attachments'), [],
                  'Ссылки на s3 удалены')


async def test_restart(tap, dataset, ext_api, s3_stubber):
    store = await dataset.store(
        address='address',
    )
    product = await dataset.product(
        images=['https://xxx.com/bad.png', 'https://extra.com/wow.png']
    )
    s3_attachments = [{'bucket': 'bucket_1',
                       'key': 'test/key_1.pdf'},
                      {'bucket': 'bucket_2',
                       'key': 'test/key_2.pdf'},
                      {'bucket': 'bucket_3',
                       'key': 'test/key_3.pdf'}]

    new_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'active',
            'ticket_key': 'LAVKACONTENT-1',
            'vars': {
                'store_id': store.store_id,
                'comment': 'comment_',
                'images': [],
                's3_attachments': s3_attachments[1:],
                'st_attachments': {'key_1.pdf': 'file1'}
            }
        }
    ).save()

    async def handler(request):
        if request.message.path == '/LAVKACONTENT-1/attachments':
            return web.json_response(
                status=200,
                data=[{'id': 'file1', 'name': 'key_1.pdf'},
                      {'id': 'file2', 'name': 'key_2.pdf'}])
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_3.pdf':
            return web.json_response(
                status=201, data={'id': 'file3', 'name': 'key_3.pdf'})

        return web.json_response(
            {}
        )

    s3_stubber.for_get_object_ok(
        bucket='bucket_3',
        key='test/key_3.pdf',
        data='test_3'.encode('utf-8')
    )
    s3_stubber.for_delete_object_ok(
        bucket='bucket_3', key='test/key_3.pdf'
    )
    s3_stubber.activate()

    with tap.plan(9, 'Успешное создание тикета и работа с клиентом'):
        async with await ext_api(tracker, handler):
            await job_create_bug_ticket(new_ticket.bug_ticket_id)

        bug_tickets = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', product.product_id),
                ('bug_type', 'other_product'),
                ('status', 'active')
            ],
            limit=5,
        )
        tap.ok(bug_tickets, 'В бд 1 запись')
        tap.eq_ok(len(bug_tickets.list), 1, 'Новые записи не создались')

        await new_ticket.reload()
        tap.eq_ok(new_ticket.status, 'active', 'статус проставился')
        tap.eq_ok(new_ticket.bug_type, 'other_product',
                  'тип баги проставился')
        tap.eq_ok(new_ticket.product_id, product.product_id,
                  'продукт прикрепился')
        tap.eq_ok(new_ticket.ticket_key, 'LAVKACONTENT-1',
                  'от клиента получне ключ')
        tap.eq_ok(new_ticket.vars['store_id'], store.store_id,
                  'в варсы проставился стор')
        tap.eq_ok(new_ticket.vars.get('st_attachments'),
                  {'key_1.pdf': 'file1',
                   'key_2.pdf': 'file2',
                   'key_3.pdf': 'file3'},
                  'Изображения прикреплены')
        tap.eq_ok(new_ticket.vars.get('s3_attachments'), [],
                  'Ссылки на s3 удалены')


async def test_err_get_st_attachments(tap, dataset, ext_api, s3_stubber):
    store = await dataset.store(
        address='address',
    )
    product = await dataset.product(
        images=['https://xxx.com/bad.png', 'https://extra.com/wow.png']
    )
    s3_attachments = [{'bucket': 'bucket_1',
                       'key': 'test/key_1.pdf'},
                      {'bucket': 'bucket_2',
                       'key': 'test/key_2.pdf'}]

    new_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'active',
            'ticket_key': 'LAVKACONTENT-1',
            'vars': {
                'store_id': store.store_id,
                'comment': 'comment_',
                'images': [],
                's3_attachments': s3_attachments[1:],
                'st_attachments': {'key_1.pdf': 'file1'}
            }
        }
    ).save()

    async def handler(request):
        if request.message.path == '/LAVKACONTENT-1/attachments':
            return web.json_response(status=400)
        if request.message.path == '/LAVKACONTENT-1/' \
                                   'attachments?filename=key_2.pdf':
            return web.json_response(
                status=201, data={'id': 'file2', 'name': 'key_2.pdf'})

        return web.json_response(
            {}
        )

    s3_stubber.for_get_object_ok(
        bucket='bucket_2',
        key='test/key_2.pdf',
        data='test_2'.encode('utf-8')
    )
    s3_stubber.for_delete_object_ok(
        bucket='bucket_2', key='test/key_2.pdf'
    )
    s3_stubber.activate()

    with tap.plan(9, 'Успешное создание тикета и работа с клиентом'):
        async with await ext_api(tracker, handler):
            await job_create_bug_ticket(new_ticket.bug_ticket_id)

        bug_tickets = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', product.product_id),
                ('bug_type', 'other_product'),
                ('status', 'active')
            ],
            limit=5,
        )
        tap.ok(bug_tickets, 'В бд 1 запись')
        tap.eq_ok(len(bug_tickets.list), 1, 'Новые записи не создались')

        await new_ticket.reload()
        tap.eq_ok(new_ticket.status, 'active', 'статус проставился')
        tap.eq_ok(new_ticket.bug_type, 'other_product',
                  'тип баги проставился')
        tap.eq_ok(new_ticket.product_id, product.product_id,
                  'продукт прикрепился')
        tap.eq_ok(new_ticket.ticket_key, 'LAVKACONTENT-1',
                  'от клиента получне ключ')
        tap.eq_ok(new_ticket.vars['store_id'], store.store_id,
                  'в варсы проставился стор')
        tap.eq_ok(new_ticket.vars.get('st_attachments'),
                  {'key_1.pdf': 'file1',
                   'key_2.pdf': 'file2'},
                  'Изображения прикреплены')
        tap.eq_ok(new_ticket.vars.get('s3_attachments'), [],
                  'Ссылки на s3 удалены')


async def test_timeout_tracker(tap, dataset, ext_api):
    store = await dataset.store(
        address='address',
    )
    product = await dataset.product()

    new_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'creation',
            'vars': {
                'store_id': store.store_id,
                'comment': 'как жить без инстаграмма',
                'images': []
            }
        }
    ).save()

    async def handler(request):
        await asyncio.sleep(30)
        return 1

    with tap.plan(2, 'При ошибке подключения к '
                     'трекеру не создается BugTicket'):
        async with await ext_api(tracker, handler):
            with tap.raises(Exception):
                await job_create_bug_ticket(new_ticket.bug_ticket_id)

        await new_ticket.reload()
        tap.eq_ok(new_ticket.status, 'creation', 'статус тикета не поменялся')


async def test_job_old_ticket_open(tap, dataset, ext_api):
    product = await dataset.product()
    old_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'active',
            'ticket_key': 'KEY-333',
            'vars': {
                'store_id': '123',
                'comment': 'old_',
                'images': [],
                'new_ticket_data': {
                    'comment': 'тест',
                }
            }
        }
    ).save()

    async def handler(request):
        data = [
            {
                'key': 'KEY-333',
                'status': {'key': 'open'}
            }
        ]
        return web.json_response(status=200, data=data)

    with tap.plan(4, 'если существует страый незакрытый тикет, '
                     'новый не создается'):
        async with await ext_api(tracker, handler):
            await job_create_bug_ticket(old_ticket.bug_ticket_id)

        await old_ticket.reload()
        tap.eq_ok(old_ticket.status, 'active',
                  'status старого тикета не поменялся')

        bug_ticket = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', product.product_id),
                ('bug_type', 'other_product'),
                ('status', ['active', 'creation'])
            ],
            limit=5,
        )

        tap.ok(bug_ticket, 'Была создана запись в бд')
        tap.eq_ok(len(bug_ticket.list), 1,
                  'существует только один подходящий тикет')
        tap.eq_ok(bug_ticket.list[0].bug_ticket_id, old_ticket.bug_ticket_id,
                  'только старый тикет остался')


async def test_job_old_ticket_closed(tap, dataset, ext_api):
    product = await dataset.product()
    store1 = await dataset.store(
        address='address1',
    )
    store2 = await dataset.store(
        address='address2',
    )
    old_ticket = await BugTicket(
        {
            'bug_type': 'other_product',
            'product_id': product.product_id,
            'status': 'active',
            'ticket_key': 'KEY-333',
            'vars': {
                'store_id': store1.store_id,
                'comment': 'old_comment',
                'images': [],
                'new_ticket_data': {
                    'comment': 'new_comment',
                    'store_id': store2.store_id,
                    'images': ['https://xxx.com/bad.png',
                               'https://extra.com/wow.png'],
                }
            }
        }
    ).save()

    requests = []
    async def handler(request):
        requests.append(request)
        if len(requests) == 1:
            data = [
                {
                    'key': 'KEY-333',
                    'status': {'key': 'closed'}
                }
            ]
            return web.json_response(status=200, data=data)
        data = {
            'key': 'KEY-444'
        }
        return web.json_response(status=201, data=data)

    with tap.plan(9, 'если старый тикет закрыт, новый создастся'):
        async with await ext_api(tracker, handler):
            await job_create_bug_ticket(old_ticket.bug_ticket_id)

        await old_ticket.reload()
        tap.eq_ok(old_ticket.status, 'closed',
                  'status старого тикета изменился')

        bug_tickets = await BugTicket.list(
            by='full',
            conditions=[
                ('product_id', product.product_id),
                ('bug_type', 'other_product'),
                ('status', ['active', 'creation'])
            ],
            limit=5,
        )
        bug_tickets = bug_tickets.list

        tap.eq_ok(len(bug_tickets), 1, 'один открытый тикет')
        tap.eq_ok(bug_tickets[0].status, 'active', 'status')
        tap.eq_ok(bug_tickets[0].product_id, product.product_id,
                  'product_id прежний')
        tap.eq_ok(bug_tickets[0].bug_type, 'other_product', 'bug_type')
        tap.eq_ok(bug_tickets[0].ticket_key, 'KEY-444', 'ticket_key')
        tap.eq_ok(bug_tickets[0].vars['store_id'], store2.store_id, 'store_id')
        tap.eq_ok(bug_tickets[0].vars['images'],
                  ['https://xxx.com/bad.png', 'https://extra.com/wow.png'],
                  'images')
        tap.eq_ok(bug_tickets[0].vars['comment'], 'new_comment', 'comment')


