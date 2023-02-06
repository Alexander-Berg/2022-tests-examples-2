async def test_no_task(tap, dataset):
    with tap.plan(10, 'В ордере должен быть ID заявки'):
        order = await dataset.order(
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
        )
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали ордер')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'check_repair_task', 'check_repair_task')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(order.problems[0].type, 'repair_task_not_found',
               'problem type')


async def test_task_not_found(tap, dataset, uuid):
    with tap.plan(10, 'В ордере должен быть корректный ID заявки'):
        order = await dataset.order(
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            vars={
                'repair_task_external_id': uuid(),
                'repair_task_source': 'lavkach',
            }
        )
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали ордер')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'check_repair_task', 'check_repair_task')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(
            order.problems[0].type,
            'repair_task_not_found',
            'problem type'
        )


async def test_task_not_in_progress(tap, dataset):
    with tap.plan(10, 'В ордере должен быть ID заявки в статусе IN_PROGRESS'):
        store = await dataset.store()
        task = await dataset.repair_task(status='NEW', store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            }
        )
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали ордер')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'check_repair_task', 'check_repair_task')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(
            order.problems[0].type,
            'repair_task_not_in_progress',
            'problem type'
        )


async def test_task_ok(tap, dataset):
    with tap.plan(10, 'В ордере корректный ID заявки '
                      'в статусе IN_PROGRESS (успех)'):
        store = await dataset.store()
        task = await dataset.repair_task(status='IN_PROGRESS', store=store)
        order = await dataset.order(
            store=store,
            type='assets_writeoff',
            status='reserving',
            estatus='begin',
            vars={
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
            }
        )
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали ордер')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'check_repair_task', 'check_repair_task')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'reserve', 'reserve')

        tap.eq(len(order.problems), 0, 'Проблем нет')
