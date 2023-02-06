import base64
import pytest

from stall import lp
from stall.model.printer_task import PrinterTask
from stall.model.printer_task_payload import PrinterTaskPayload


async def test_wrong_token(api, tap, dataset, uuid):
    with tap.plan(4):
        t = await api()

        store = await dataset.store()

        await t.post_ok('api_print_push',
                        json={
                            'store_id': store.store_id,
                            'type': 'txt',
                            'document': 'Hello, world',
                            'target': 'printer',
                        },
                        headers={
                            'Authorization': f'token {uuid()}',
                            # 'token ' + cfg('print.push.token.0'),
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


async def test_wrong_store_id(api, tap, uuid, cfg):
    with tap.plan(4):
        t = await api()

        await t.post_ok('api_print_push',
                        json={
                            'store_id': uuid(),
                            'type': 'txt',
                            'document': 'Hello, world',
                            'target': 'sticker',
                        },
                        headers={
                            'Authorization':
                                f'token {cfg("print.push.token.0")}',
                        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_like('message', r'^Store not found: [0-9a-f]{32}$')


@pytest.mark.parametrize('by', ['store_id', 'external_id'])
async def test_push(api, tap, cfg, dataset, by):
    with tap.plan(10):
        t = await api()

        store = await dataset.store()

        await t.post_ok('api_print_push',
                        json={
                            'store_id': getattr(store, by),
                            'type': 'txt',
                            'document':
                                base64.b64encode(b'Hello, world').decode(),
                            'target': 'sticker',
                        },
                        headers={
                            'Authorization':
                                f'token {cfg("print.push.token.0")}',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Task was sent')
        t.json_has('details.message', 'id таски сделан')

        task_id = t.res['json']['details']['message']

        task = await PrinterTask.load(task_id)
        tap.isa_ok(task, PrinterTask, 'таска прочитана')
        tap.ok(task.payload_id, 'данные записаны')

        data = await PrinterTaskPayload.load(task.payload_id)
        tap.isa_ok(data, PrinterTaskPayload, 'сами данные')
        tap.eq(data.data,
               base64.b64encode(b'Hello, world').decode(),
               'данные в записи данных')
        tap.ok(lp.exists(['print', 'store', store.store_id]),
               'сообщение о печати отправлено')


async def test_push_repeat(api, tap, cfg, dataset, uuid):
    with tap.plan(15):
        t = await api()

        store = await dataset.store()

        request_id = uuid()

        await t.post_ok('api_print_push',
                        json={
                            'store_id': store.store_id,
                            'type': 'txt',
                            'document':
                                base64.b64encode(b'Hello, world').decode(),
                            'target': 'sticker',
                            'id': request_id,
                        },
                        headers={
                            'Authorization':
                                f'token {cfg("print.push.token.0")}',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Task was sent')
        t.json_has('details.message', 'id таски сделан')

        task_id = t.res['json']['details']['message']

        task = await PrinterTask.load(task_id)
        tap.isa_ok(task, PrinterTask, 'таска прочитана')
        tap.ok(task.payload_id, 'данные записаны')
        tap.eq(task.target, 'sticker', 'тип задания')

        data = await PrinterTaskPayload.load(task.payload_id)
        tap.isa_ok(data, PrinterTaskPayload, 'сами данные')
        tap.eq(data.data,
               base64.b64encode(b'Hello, world').decode(),
               'данные в записи данных')

        await t.post_ok('api_print_push',
                        json={
                            'store_id': store.store_id,
                            'type': 'txt',
                            'target': 'sticker',
                            'document': 'Hello, world11',
                            'id': request_id,
                        },
                        headers={
                            'Authorization':
                                f'token {cfg("print.push.token.0")}',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'Task was sent')
        t.json_is('details.message', task.task_id, 'id таски сделан')
