import argparse
from datetime import timedelta

from scripts.cron.create_orders.create_checks_from_projects import lock_main
from tests.model.check_project.test_create_checks import get_orders_by_project


async def test_create_checks_job(tap, dataset, job, time_mock):
    with tap.plan(6, 'тестируем честное создание джобы'):
        store = await dataset.store(options={'exp_big_brother': True})
        stock = await dataset.stock(store=store)
        _now = time_mock.now()

        cp = await dataset.check_project(
            product_id=stock.product_id,
            store_id=store.store_id,
            schedule={
                'timetable': [{
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }],
                'begin': _now,
                'end': _now + timedelta(days=2),
            }
        )

        args = argparse.Namespace(
            check_project_id=[cp.check_project_id],
            mode='spawn_job',
        )
        task_id = await lock_main(args, job.name)

        task = await job.take()
        tap.eq(task.id, task_id, 'нужный айди')
        tap.ok(await job.call(task), 'Задание выполнено')

        created_order = await get_orders_by_project(
            cp.check_project_id, store.store_id,
        )
        tap.eq(len(created_order), 1, 'найден один ордер')
        created_order = created_order[0]

        tap.eq(created_order.type, 'check', 'нужный тип')
        tap.eq(created_order.source, 'internal', 'нужный сорс')
        tap.eq(
            created_order.required,
            [{'product_id': stock.product_id}],
            'нужный required',
        )
