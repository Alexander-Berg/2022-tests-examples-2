import tests.dataset as dt
from libstall.util import time2iso

async def test_save_order_log(tap, dataset: dt, now):
    tap.plan(3)
    with tap.subtest(6, 'Дефолтное сохранение OrderLog') as taps:
        order = await dataset.order()

        cursor = await dataset.OrderLog.list_by_order(order)
        taps.eq_ok(len(cursor.list), 1, 'Запись о создании заказа')
        with cursor.list[-1] as order_log:
            taps.eq_ok(order_log.source, 'save',
                       'Источник для лога')
            taps.eq_ok(order_log.status, order.status,
                       'Статус заказа')
            taps.eq_ok(order_log.estatus, order.estatus,
                       'Подстатус заказа')
            taps.eq_ok(order_log.eda_status, None,
                       'Статуса заказа из еды нет')
            taps.eq_ok(order_log.vars, {},
                       'Дополнительных параметров не указано')

    now_datetime = now()
    with tap.subtest(8, 'Cохранение расширенного OrderLog') as taps:
        order.eda_status='UNCONFIRMED'
        await order.save(
            order_logs=[{
                'source': 'set_courier',
                'vars': {
                    'some-key': 'some-data',
                    'datetime': now_datetime
                },
            }]
        )

        cursor = await dataset.OrderLog.list_by_order(order)
        taps.eq_ok(len(cursor.list), 2, 'Запись об изменении заказа добавлена')
        with cursor.list[-1] as order_log:
            taps.eq_ok(order_log.source, 'set_courier',
                       'Источник для лога')
            taps.eq_ok(order_log.status, order.status,
                       'Статус заказа')
            taps.eq_ok(order_log.estatus, order.estatus,
                       'Подстатус заказа')
            taps.eq_ok(order_log.eda_status, 'UNCONFIRMED',
                       'Статус заказа из еды проставлен')
            taps.ok(order_log.vars, 'Дополнительные параметры сохраненны')
            taps.eq_ok(order_log.vars.get('some-key'), 'some-data',
                       'Строковое значение сохранено')
            taps.eq_ok(order_log.vars.get('datetime'), time2iso(now_datetime),
                       'Время сохранено')


    with tap.subtest(1, 'Cохранение пустого OrderLog') as taps:
        order.eda_status='UNCONFIRMED'
        await order.save(
            order_logs=[]
        )

        cursor = await dataset.OrderLog.list_by_order(order)
        taps.eq_ok(len(cursor.list), 2, 'Пустой лог не добавляет записей')
