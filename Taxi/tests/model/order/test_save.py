from decimal import Decimal

from libstall.model.storable.exception import EmptyRowsetError
from libstall.util import now
from stall.model.order import Order, ORDER_STATUS
from stall.model.order_log import OrderLog


async def test_save(tap, uuid):
    with tap.plan(13):
        order = Order({
            'company_id': uuid(),
            'store_id': uuid(),
            'status': 'request',
        })

        tap.ok(await order.save(), 'Сохранён')
        tap.eq(order.version, 1, 'версия')
        tap.eq(order.revision, 1, 'ревизия')

        lsn = order.lsn

        tap.ok(await order.save(), 'Сохранён повторно')
        tap.eq(order.version, 1, 'Версия не поменялась')
        tap.eq(order.revision, 2, 'Ревизия проинкрементировалась')
        tap.ok(order.lsn > lsn, 'lsn растёт')

        lsn = order.lsn
        order.version = None
        tap.ok(await order.save(), 'Сохранён еще раз со сброшенной версией')
        tap.eq(order.version, 2, 'Версия проинкрементировалась')
        tap.eq(order.revision, 3, 'Ревизия проинкрементировалась')
        tap.ok(order.lsn > lsn, 'lsn растёт')
        tap.eq(order.timeout_approving, None, 'timeout_approving не заполнен')

        with tap.subtest(None, 'Получение логов') as taps:
            cursor = None
            while True:
                logs = await OrderLog.list_by_order(order,
                                                    limit=3,
                                                    cursor_str=cursor)
                taps.ok(logs, f'Порция логов получена len={len(logs.list)}')
                for l in logs:
                    taps.in_ok(l.status, ORDER_STATUS, f'статус {l.status}')
                    taps.eq(l.source, 'save', f'source {l.source}')
                    taps.eq(l.order_id,
                            order.order_id,
                            f'order_id {l.order_id}')

                cursor = logs.cursor_str
                if cursor is None:
                    break


async def test_shelves(tap, dataset):
    with tap.plan(4):

        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store)
        shelf2 = await dataset.shelf(store=store)

        order = Order({
            'company_id': store.company_id,
            'store_id': store.store_id,
            'status': 'request',
            'shelves': [shelf1.shelf_id, shelf2.shelf_id],
        })

        tap.ok(await order.save(), 'Сохранён')
        tap.eq(
            order.shelves,
            [shelf1.shelf_id, shelf2.shelf_id],
            'Полки сохранены',
        )

        tap.ok(await order.reload(), 'Перезабрали')
        tap.eq(
            order.shelves,
            [shelf1.shelf_id, shelf2.shelf_id],
            'Полки восстановлены',
        )


async def test_doc_number(tap, uuid, dataset):
    with tap.plan(2):

        with await dataset.order(external_id='200101-000001') as order:
            tap.eq(order.attr['doc_number'], order.external_id, 'тот же')

        with await dataset.order(external_id=uuid()) as order:
            tap.like(
                order.attr['doc_number'],
                r'^\d{6}-\w{6}',
                f'создан {order.attr["doc_number"]}'
            )


async def test_order_save_condition(tap, dataset, uuid):
    with tap.plan(5, 'conditions при сохранении ордера'):
        order = await dataset.order()
        tap.ok(order, 'ордер сгенерирован')
        order.estatus = uuid()
        tap.ok(await order.save(), 'сохранено')

        lsn = order.lsn

        order.estatus = uuid()
        with tap.raises(EmptyRowsetError,
                        'исключение при несовпадении условий'):
            await order.save(conditions=[('lsn', '=', -1)])
        tap.ok(await order.reload(), 'перегружен')
        tap.eq(order.lsn, lsn, 'lsn не менялся')


async def test_attr(tap, uuid):
    with tap.plan(18):
        order = Order({
            'company_id': uuid(),
            'store_id': uuid(),
            'status': 'request',
            'external_id': '200101-000002',
            'attr': {'some_key': 'some_value'},
        })
        tap.eq(order.attr.get('doc_number'), order.external_id,
               'номер документа равен external_id')
        tap.eq(order.attr.get('doc_date'), now().strftime('%F'),
               'дата документа - сегодня')
        tap.eq(order.attr.get('some_key'), 'some_value',
               'прочие данные сохранены')

        order = Order({
            'company_id': uuid(),
            'store_id': uuid(),
            'status': 'request',
            'external_id': '00' + str(uuid())[1:],
            'attr': {'some_key': 'some_value'},
        })
        tap.like(
            order.attr['doc_number'],
            r'^\d{6}-\w{6}',
            'выставлен doc_number'
        )
        tap.eq(order.attr.get('doc_date'), now().strftime('%F'),
               'дата документа - сегодня')
        tap.eq(order.attr.get('some_key'), 'some_value',
               'прочие данные сохранены')

        order = Order({
            'company_id': uuid(),
            'store_id': uuid(),
            'status': 'request',
            'external_id': uuid(),
            'attr': {'some_key': 'some_value'},
        })
        tap.like(
            order.attr['doc_number'],
            r'^\d{6}-\w{6}',
            'выставлен doc_number'
        )
        tap.eq(order.attr.get('doc_date'), now().strftime('%F'),
               'дата документа - сегодня')
        tap.eq(order.attr.get('some_key'), 'some_value',
               'прочие данные сохранены')

        order = Order({
            'company_id': uuid(),
            'store_id': uuid(),
            'status': 'request',
            'external_id': uuid(),
            'attr': {'some_key': 'some_value', 'doc_number': 'some_number'},
        })
        tap.eq(order.attr.get('doc_number'), 'some_number',
               'doc_number такой, как указан')
        tap.eq(order.attr.get('doc_date'), now().strftime('%F'),
               'дата документа - сегодня')
        tap.eq(order.attr.get('some_key'), 'some_value',
               'прочие данные сохранены')

        order = Order({
            'company_id': uuid(),
            'store_id': uuid(),
            'status': 'request',
            'external_id': '200101-000002',
            'attr': {'some_key': 'some_value', 'doc_date': '1966-10-13'},
        })
        tap.eq(order.attr.get('doc_number'), order.external_id,
               'номер документа равен external_id')
        tap.eq(order.attr.get('doc_date'), '1966-10-13',
               'дата такая, как указана')
        tap.eq(order.attr.get('some_key'), 'some_value',
               'прочие данные сохранены')

        order = Order({
            'company_id': uuid(),
            'store_id': uuid(),
            'status': 'request',
            'external_id': '200101-000002',
            'attr': {'some_key': 'some_value',
                     'doc_date': '1966-10-14',
                     'doc_number': '200101-000005'},
        })
        tap.eq(order.attr.get('doc_number'), '200101-000005',
               'doc_number такой, как указан')
        tap.eq(order.attr.get('doc_date'), '1966-10-14',
               'дата такая, как указана')
        tap.eq(order.attr.get('some_key'), 'some_value',
               'прочие данные сохранены')


async def test_save_address(tap, dataset):
    with tap.plan(10, 'Сохранение адресов клиентов'):
        order = await dataset.order()
        tap.ok(order, 'ордер сгенерирован')

        tap.eq(order.rehashed('-check'), set(), 'нет изменений')

        order.client_address = {
            'fullname': 'Москва, Парк культуры',
            'lon': 37,
            'lat': 55,
        }
        tap.ok(order.rehashed('client_address'), 'rehashed')
        tap.eq(
            order.rehashed('-check'),
            {'client_address'},
            'rehashed'
        )
        tap.ok(await order.save(), 'сохранён')


        order.client_address = {
            'fullname': 'Москва, Парк культуры',
            'lon': 37,
            'lat': 55,
        }
        tap.eq(order.rehashed('-check'), set(), 'нет изменений')

        order.client_address = {
            'fullname': 'Москва, Парк культуры',
            'lon': None,
            'lat': None,
        }
        tap.eq(
            order.rehashed('-check'),
            {'client_address'},
            'rehashed'
        )
        tap.ok(await order.save(), 'сохранён')

        order.client_address = {
            'fullname': 'Москва, Парк культуры',
            'lon': Decimal('37.22'),
            'lat': Decimal('55.32'),
        }
        tap.eq(
            order.rehashed('-check'),
            {'client_address'},
            'rehashed'
        )
        tap.ok(await order.save(), 'сохранён')

async def test_clean_save(tap, dataset):
    with tap.plan(2, 'сохранение без событий'):
        order = await dataset.order()
        tap.ok(order, 'ордер сгенерирован')

        tap.ok(
            await order.save(store_job_event=False, store_lp_event=False),
            'сохранено без событий'
        )
