from aiohttp import web

from scripts.sync_repair_tasks import RepairTaskDaemon
from stall.client.lavkach import client
from stall.model.repair_task import RepairTask

BASE_RESULT = {
    'status': 'IN_PROGRESS',
    'type': 'REPAIR',
}


# pylint: disable=protected-access
async def test_create(ext_api, tap, uuid, dataset):
    with tap.plan(16, 'Создаем копии заявок на ремонт из Лавкача'):
        store = await dataset.store()
        store_id = store.store_id
        ids = [uuid() for _ in range(6)]
        tasks_data = {
            'no-cursor': {
                'result': [{'id': ids[0], 'warehouse_id': store_id,
                            **BASE_RESULT},
                           {'id': ids[1], 'warehouse_id': store_id,
                            **BASE_RESULT}],
                'cursor': 'cursor1',
            },
            'cursor1': {
                'result': [{'id': ids[2], 'warehouse_id': store_id,
                            **BASE_RESULT},
                           {'id': ids[3], 'warehouse_id': store_id,
                            **BASE_RESULT}],
                'cursor': 'cursor2',
            },
            'cursor2': {
                'result': [{'id': ids[4], 'warehouse_id': store_id,
                            **BASE_RESULT},
                           {'id': ids[5], 'warehouse_id': store_id,
                            **BASE_RESULT}],
                'cursor': 'cursor3',
            },
            'cursor3': {
                'result': [],
                'cursor': 'cursor3',
            },
        }

        async def handler(request):
            req_data = await request.json()
            if not req_data.get('cursor'):
                return tasks_data['no-cursor']
            return web.json_response(status=200,
                                     data=tasks_data[req_data['cursor']])

        async with await ext_api(client, handler=handler):
            tap.eq(await RepairTaskDaemon()._process(None), 'cursor1',
                   'cursor1')
            tap.eq(await RepairTaskDaemon()._process('cursor1'), 'cursor2',
                   'cursor2')
            tap.eq(await RepairTaskDaemon()._process('cursor2'), 'cursor3',
                   'cursor3')
            tap.eq(await RepairTaskDaemon()._process('cursor3'), 'cursor3',
                   'cursor3 again')

        for external_id in ids:
            task = await RepairTask.load(['lavkach', external_id],
                                         by='external')
            tap.ok(task, 'Task present')
            tap.eq(task.vars['lavkach_type'], 'REPAIR', 'lavkach type correct')


async def test_update(ext_api, tap, uuid, dataset):
    with tap.plan(12, 'Обновление заявок из Лавкача'):
        ids = [uuid() for _ in range(6)]
        store = await dataset.store()
        store_id = store.store_id
        tasks_data1 = {
            'no-cursor': {
                'result': [{'id': ids[0], 'status': 'NEW',
                            'warehouse_id': store_id, 'type': 'REPAIR'},
                           {'id': ids[1], 'status': 'NEW',
                            'warehouse_id': store_id, 'type': 'REPAIR'}],
                'cursor': 'cursor1',
            },
            'cursor1': {
                'result': [],
                'cursor': 'cursor1',
            },
        }

        async def handler1(request):
            req_data = await request.json()
            if not req_data.get('cursor'):
                return tasks_data1['no-cursor']
            return web.json_response(status=200,
                                     data=tasks_data1[req_data['cursor']])

        async with await ext_api(client, handler=handler1):
            tap.eq(await RepairTaskDaemon()._process(None), 'cursor1',
                   'cursor1')
            tap.eq(await RepairTaskDaemon()._process('cursor1'), 'cursor1',
                   'cursor1 again')

        task = await RepairTask.load(['lavkach', ids[0]], by='external')
        tap.eq(task.status, 'NEW', 'Task0 present')
        task = await RepairTask.load(['lavkach', ids[1]], by='external')
        tap.eq(task.status, 'NEW', 'Task1 present')

        tasks_data2 = {
            'cursor1': {
                'result': [{'id': ids[1], 'warehouse_id': store_id,
                            **BASE_RESULT},
                           {'id': ids[2], 'warehouse_id': store_id,
                            **BASE_RESULT}],
                'cursor': 'cursor2',
            },
            'cursor2': {
                'result': [],
                'cursor': 'cursor2',
            },
        }

        async def handler2(request):
            req_data = await request.json()
            if not req_data.get('cursor'):
                return tasks_data2['no-cursor']
            return web.json_response(status=200,
                                     data=tasks_data2[req_data['cursor']])

        async with await ext_api(client, handler=handler2):
            tap.eq(await RepairTaskDaemon()._process('cursor1'), 'cursor2',
                   'cursor2')
            tap.eq(await RepairTaskDaemon()._process('cursor2'), 'cursor2',
                   'cursor2 again')

        task = await RepairTask.load(['lavkach', ids[0]], by='external')
        tap.eq(task.status, 'NEW', 'task0, status unchanged')
        tap.eq(task.vars['lavkach_type'], 'REPAIR', 'lavkach type correct')
        task = await RepairTask.load(['lavkach', ids[1]], by='external')
        tap.eq(task.status, 'IN_PROGRESS', 'task1, status changed')
        tap.eq(task.vars['lavkach_type'], 'REPAIR', 'lavkach type correct')
        task = await RepairTask.load(['lavkach', ids[2]], by='external')
        tap.eq(task.status, 'IN_PROGRESS', 'Task2 present')
        tap.eq(task.vars['lavkach_type'], 'REPAIR', 'lavkach type correct')
