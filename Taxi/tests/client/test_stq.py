import json
from aiohttp import web
from aiohttp.web_request import Request
from stall.client.stq import STQClient, STQClientError


async def test_happy(tap, ext_api, uuid):
    with tap.plan(1, 'Простой запрос ответ'):
        client = STQClient()
        task_id = uuid()

        async def handler(req: Request):
            # pylint: disable=unused-argument
            return web.Response(
                status=200,
                text=json.dumps({
                    'tasks': [{
                        'task_id': task_id,
                        'add_result': {
                            'code': 200,
                        },
                    }]
                }),
                content_type='application/json'
            )

        async with await ext_api(client, handler) as client:
            client: STQClient
            res = await client.push_tasks('queue_name', [{'task_id': task_id}])

        tap.ok(res, '200')


async def test_invalid_count(tap, ext_api):
    with tap.plan(1, 'Отправили 1 таску, в ответ получили 2'):
        client = STQClient()

        async def handler(req: Request):
            # pylint: disable=unused-argument
            return web.Response(
                status=200,
                text=json.dumps({
                    'tasks': [{}, {}]
                }),
                content_type='application/json'
            )

        with tap.raises(
            STQClientError,
            'Количество тасок в ответе должно совпадать с отправленным'
        ):
            async with await ext_api(client, handler) as client:
                client: STQClient
                await client.push_tasks('queue_name', [{}])


async def test_error_with_concrete_task(tap, ext_api, uuid):
    with tap.plan(1, 'Не получилось выставить конкретную таску'):
        client = STQClient()
        task_id = uuid()

        async def handler(req: Request):
            # pylint: disable=unused-argument
            return web.Response(
                status=200,
                text=json.dumps({
                    'tasks': [{
                        'task_id': task_id,
                        'add_result': {
                            'code': 500,
                            'description': 'some_failure',
                        },
                    }]
                }),
                content_type='application/json'
            )

        with tap.raises(
            STQClientError,
            'Пришло 200, но не получилось выставить таску'
        ):
            async with await ext_api(client, handler) as client:
                client: STQClient
                await client.push_tasks('queue_name', [{'task_id': task_id}])


async def test_error(tap, ext_api, uuid):
    with tap.plan(1, 'STQ ответил не 200'):
        client = STQClient()
        task_id = uuid()

        async def handler(req: Request):
            # pylint: disable=unused-argument
            return web.Response(
                status=500,
                text='Some error',
                content_type='application/json'
            )

        with tap.raises(STQClientError, 'Пришло 500'):
            async with await ext_api(client, handler) as client:
                client: STQClient
                await client.push_tasks('queue_name', [{'task_id': task_id}])


async def test_invalid_response(tap, ext_api, uuid):
    with tap.plan(1, 'Обрабатываем невалидный ответ'):
        client = STQClient()
        task_id = uuid()

        async def handler(req: Request):
            # pylint: disable=unused-argument
            return web.Response(
                status=200,
                text=json.dumps({
                    'some_key': 'some_value',
                }),
                content_type='application/json'
            )

        with tap.raises(
            STQClientError,
            'Пришло 200, но мы не понимаем что'
        ):
            async with await ext_api(client, handler) as client:
                client: STQClient
                await client.push_tasks('queue_name', [{'task_id': task_id}])


async def test_default_values(tap, ext_api, uuid):
    with tap.plan(5, 'Проставляем defaults'):
        client = STQClient()
        task_id = uuid()
        log_sent_tasks = []

        async def handler(req: Request):
            # pylint: disable=unused-argument
            log_sent_tasks.extend((await req.json()).get('tasks', []))
            return web.Response(
                status=200,
                text=json.dumps({
                    'tasks': [{
                        'task_id': task_id,
                        'add_result': {
                            'code': 200,
                        },
                    }]
                }),
                content_type='application/json'
            )

        async with await ext_api(client, handler) as client:
            client: STQClient
            await client.push_tasks('queue_name', [{'task_id': task_id}])

        tap.eq(len(log_sent_tasks), 1, 'Запрос к stq ушел')
        tap.eq(log_sent_tasks[0]['task_id'], task_id, 'task_id')
        tap.eq(log_sent_tasks[0]['args'], [], 'args')
        tap.eq(log_sent_tasks[0]['kwargs'], {}, 'kwargs')
        tap.eq(log_sent_tasks[0]['eta'], '1970-01-01T00:00:00.000000Z', 'eta')


async def test_default_task_id(tap, ext_api, uuid):
    with tap.plan(2, 'Нет task_id - нет таски'):
        client = STQClient()
        log_sent_tasks = []

        async def handler(req: Request):
            # pylint: disable=unused-argument
            log_sent_tasks.extend((await req.json()).get('tasks', []))
            return web.Response(
                status=200,
                text=json.dumps({
                    'tasks': [{
                        'task_id': uuid(),
                        'add_result': {
                            'code': 200,
                        },
                    }]
                }),
                content_type='application/json'
            )
        async with await ext_api(client, handler) as client:
            client: STQClient
            with tap.raises(STQClientError, 'task_id должен быть указан'):
                await client.push_tasks('queue_name', [{}])

        tap.eq(len(log_sent_tasks), 0, 'Запрос к stq не ушел')
