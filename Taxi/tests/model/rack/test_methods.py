async def test_reserve(tap, dataset):
    with tap.plan(15, 'Резерв места в стеллаже'):
        rack = await dataset.rack(capacity=2)
        tap.eq(rack.reserve, 0, 'Резерва нет')
        order = await dataset.order()
        user = await dataset.user(
            company_id=rack.company_id,
            store_id=rack.store_id
        )
        tap.ok(
            await rack.do_reserve(order=order, user_id=user.user_id),
            'Сделали резерв места на стеллаже'
        )
        tap.eq(rack.reserve, 1, 'Резерв появился')
        tap.eq(
            rack.reserves.get(order.order_id),
            1,
            'Зарезервировали заказом'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ]
        )).list
        tap.eq(len(rack_logs), 1, 'Одна запись в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'reserve', 'Резерв')
        tap.eq(rack_log.user_id, user.user_id, 'Пользователь')
        tap.eq(rack_log.delta_reserve, 1, 'Изменение резерва')
        tap.eq(rack_log.reserve, 1, 'Резерв новый')
        tap.eq(rack_log.capacity, 2, 'Емкость проросла')
        tap.ok(
            await rack.do_reserve(order=order, user_id=user.user_id),
            'Сделали резерв повторно'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ]
        )).list
        tap.eq(len(rack_logs), 1, 'Одна запись в логе все еще')
        tap.eq(
            await rack.do_reserve(order=order, count=3),
            None,
            'Не смогли сделать резерв больше емкости'
        )
        tap.ok(await rack.reload(), 'Перезабрали стеллаж')
        tap.eq(rack.reserve, 1, 'Резерв остался в 1')


async def test_unreserve(tap, dataset):
    with tap.plan(13, 'Разрезерв места в стеллаже'):
        rack = await dataset.rack(capacity=3)
        tap.eq(rack.reserve, 0, 'Резерва нет')
        order = await dataset.order()
        user = await dataset.user(
            company_id=rack.company_id,
            store_id=rack.store_id
        )
        tap.ok(
            await rack.do_reserve(order=order, user_id=user.user_id, count=3),
            'Сделали резерв места на стеллаже'
        )
        old_rack = await dataset.Rack.load(rack.rack_id)
        tap.ok(
            await rack.do_unreserve(order=order, user_id=user.user_id),
            'Сделали разрезерв'
        )
        tap.eq(rack.count, 0, 'Количество')
        tap.eq(rack.reserve, 0, 'Резерв')
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 2, 'Две записи в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'reserve', 'Резерв')
        rack_log = rack_logs[1]
        tap.eq(rack_log.type, 'unreserve', 'Резерв')
        tap.eq(rack_log.user_id, user.user_id, 'Пользователь')
        tap.eq(rack_log.delta_reserve, -3, 'Изменение резерва')
        tap.eq(rack_log.reserve, 0, 'Резерв новый')
        tap.ok(
            await old_rack.do_unreserve(order=order, user_id=user.user_id),
            'Сделали снятие резерва повторно'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ]
        )).list
        tap.eq(len(rack_logs), 2, 'Все еще две записи')


async def test_link_cargo(tap, dataset):
    with tap.plan(17, 'Свяжем груз со стеллажом'):
        rack = await dataset.rack()
        shelf = await dataset.shelf(type='cargo', store_id=rack.store_id)
        order = await dataset.order(store_id=rack.store_id)
        tap.ok(
            await rack.do_reserve(order=order),
            'Сделали резерв места на стеллаже'
        )
        old_rack = await dataset.Rack.load(rack.rack_id)
        tap.ok(
            await rack.do_link_cargo(cargo=shelf, order=order),
            'Добавили связь'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 2, 'Две записи в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'reserve', 'Резерв')
        rack_log = rack_logs[1]
        tap.eq(rack_log.type, 'link_cargo', 'Связывание')
        tap.eq(rack_log.shelf_id, shelf.shelf_id, 'Груз пророс')
        tap.eq(rack_log.delta_reserve, -1, 'Изменение резерва')
        tap.eq(rack_log.delta_count, 1, 'Изменение количества')
        tap.eq(rack_log.reserve, 0, 'Резерв новый')
        tap.eq(rack_log.count, 1, 'Количество новое')
        tap.eq(rack.count, 1, 'Количество')
        tap.eq(rack.reserve, 0, 'Резерв')
        shelf.rack_id = None
        tap.ok(
            await old_rack.do_link_cargo(cargo=shelf, order=order),
            'Добавили связь снова'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ]
        )).list
        tap.eq(len(rack_logs), 2, 'Все еще две записи')
        tap.ok(await old_rack.reload(), 'Перезабрали')
        tap.eq(old_rack.count, 1, 'Количество')
        tap.eq(old_rack.reserve, 0, 'Резерв')


async def test_link_cargo_no_order(tap, dataset):
    with tap.plan(15, 'Свяжем груз со стеллажом без документа'):
        rack = await dataset.rack()
        shelf = await dataset.shelf(type='cargo', store_id=rack.store_id)
        tap.ok(
            await rack.do_link_cargo_no_order(cargo=shelf),
            'Добавили связь'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 1, 'Одна запись в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'link_cargo', 'Связывание')
        tap.eq(rack_log.shelf_id, shelf.shelf_id, 'Груз пророс')
        tap.eq(rack_log.delta_reserve, 0, 'Изменение резерва нет')
        tap.eq(rack_log.delta_count, 1, 'Изменение количества')
        tap.eq(rack_log.reserve, 0, 'Резерв новый')
        tap.eq(rack_log.count, 1, 'Количество новое')
        tap.eq(rack.count, 1, 'Количество')
        tap.eq(rack.reserve, 0, 'Резерв')
        shelf.rack_id = None
        tap.ok(
            await rack.do_link_cargo_no_order(cargo=shelf),
            'Добавили связь снова'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ]
        )).list
        tap.eq(len(rack_logs), 1, 'Все еще две записи')
        tap.ok(await rack.reload(), 'Перезабрали')
        tap.eq(rack.count, 1, 'Количество')
        tap.eq(rack.reserve, 0, 'Резерв')


async def test_unlink_cargo(tap, dataset):
    with tap.plan(17, 'Отвяжем груз от стеллажа'):
        rack = await dataset.rack()
        shelf = await dataset.shelf(
            type='cargo',
            store_id=rack.store_id,
            rack_id=rack.rack_id
        )
        tap.eq(shelf.rack_id, rack.rack_id, 'Стеллаж был')
        order = await dataset.order(store_id=rack.store_id)
        tap.ok(
            await rack.do_unlink_cargo(cargo=shelf, order=order),
            'Оторвали груз'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 2, 'Две записи в логе')
        rack_log = next(
            (
                record
                for record in rack_logs
                if record.type == 'unlink_cargo'
            ),
            None
        )
        tap.ok(rack_log, 'Есть такой лог')
        tap.eq(rack_log.type, 'unlink_cargo', 'Отвязывание')
        tap.eq(rack_log.shelf_id, shelf.shelf_id, 'Груз пророс')
        tap.eq(rack_log.delta_reserve, 0, 'Изменение резерва')
        tap.eq(rack_log.delta_count, -1, 'Изменение количества')
        tap.eq(rack_log.reserve, 0, 'Резерв новый')
        tap.eq(rack_log.count, 0, 'Количество новое')
        tap.eq(rack.count, 0, 'Количество')
        tap.eq(rack.reserve, 0, 'Резерв')
        shelf.rack_id = rack.rack_id
        tap.ok(
            await rack.do_unlink_cargo(cargo=shelf, order=order),
            'Отвязали снова'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ]
        )).list
        tap.eq(len(rack_logs), 2, 'Все еще две записи')
        tap.ok(await rack.reload(), 'Перезабрали')
        tap.eq(rack.count, 0, 'Количество')
        tap.eq(rack.reserve, 0, 'Резерв')


async def test_rollback(tap, dataset):
    with tap.plan(16, 'Откат резерва перенакатыванием'):
        rack = await dataset.rack(capacity=2)
        tap.eq(rack.reserve, 0, 'Резерва нет')
        order = await dataset.order()
        tap.ok(
            await rack.do_reserve(order=order, count=2),
            'Сделали резерв места на стеллаже'
        )
        tap.eq(rack.reserve, 2, 'Резерв появился')
        tap.eq(
            rack.reserves.get(order.order_id),
            2,
            'Зарезервировали заказом'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ]
        )).list
        tap.eq(len(rack_logs), 1, 'Одна запись в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'reserve', 'Резерв')
        tap.ok(
            await rack.do_reserve(order=order, count=0),
            'Сделали резерв повторно на 0'
        )
        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id)
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 3, 'Теперь три записи')
        tap.eq(rack_logs[0].type, 'reserve', 'Резерв сначала')
        tap.eq(rack_logs[1].type, 'reserve', 'Резерв второй')
        tap.eq(
            rack_logs[1].recount,
            rack_logs[0].log_id,
            'Пересчет первой записи'
        )
        tap.eq(rack_logs[1].delta_reserve, -2, 'Дельта резерв второй')
        tap.eq(rack_logs[2].type, 'reserve', 'Резерв третий')
        tap.eq(rack_logs[2].delta_reserve, 0, 'Дельта резерв третий')
        tap.ok(await rack.reload(), 'Перезабрали стеллаж')
        tap.eq(rack.reserve, 0, 'Резерв в 0')
