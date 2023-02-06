import json

from aiohttp import web
from aiohttp.web_request import Request

from stall.model.event_cache import EventSTQ


async def test_push(tap, dataset, uuid, ext_api, push_events_cache):
    # pylint: disable=protected-access
    with tap.plan(4, 'Обработка ошибки создания producer при пуше'):
        task_id = uuid()
        courier = await dataset.courier()

        await courier.save(events=[
            EventSTQ(
                queue='grocery_performer_communications_common_message',
                task_id=task_id,
                args=['arg1'],
                kwargs={
                    'some_key': 'some_value',
                }
            ),
        ])

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

        async with await ext_api('stq', handler):
            await push_events_cache(courier, event_type='stq')

        tap.eq(len(log_sent_tasks), 1, 'Запрос к stq ушел')
        tap.eq(log_sent_tasks[0]['task_id'], task_id, 'task_id')
        tap.eq(log_sent_tasks[0]['args'], ['arg1'], 'args')
        tap.eq(
            log_sent_tasks[0]['kwargs'],
            {'some_key': 'some_value'},
            'kwargs'
        )
