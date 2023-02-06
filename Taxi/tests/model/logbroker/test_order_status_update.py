from collections import defaultdict
import pytest
from stall.model.event_cache import EventCache, EventLB
from stall.model.suggest import Suggest


@pytest.fixture()
async def event_cache_lb():
    class WriterMock():
        def __init__(self):
            self.log = []

        async def write_messages(self, topic, messages):
            self.log.append((topic, messages))

    class EventLbWithLog(EventLB):
        writer = WriterMock()

    class EventCacheMock(EventCache):
        @classmethod
        async def daemon_cycle(cls, *args, **kwargs):
            EventLbWithLog.writer.log = []
            return await super().daemon_cycle(*args, **kwargs)

        @classmethod
        async def _logbroker_push(cls, events):
            await EventLbWithLog.push(events)

        @staticmethod
        def log(filter_topic=None):
            if filter_topic is None:
                return EventLbWithLog.writer.log

            topic_log = []
            for topic, message in EventLbWithLog.writer.log:
                if topic == filter_topic:
                    topic_log.append((topic, message))
            return topic_log

    setattr(EventCacheMock, '__name__', EventCache.__name__)
    yield EventCacheMock


async def test_change_order_status(tap, dataset, wait_order_status,
                                        event_cache_lb):
    # pylint: disable=redefined-outer-name, too-many-statements
    with tap.plan(7, 'Событие: изменение статуса заказа'):
        store = await dataset.store()
        order = await dataset.order(
            store_id=store.store_id,
            type='order',
            status='approving',
            estatus='begin',
        )

        await event_cache_lb.daemon_cycle(
            shard=order.shardno,
            ev_type='logbroker',
            conditions=[
                ('tbl', 'orders'),
                ('pk', order.order_id)
            ]
        )

        with tap.subtest(21, 'Сообщение содержит верные данные') as taps:
            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 1, '1 запись в логе')
            _, messages = log[0]
            taps.eq(len(messages), 1, '1 сообщение')

            message: dict = messages[0]
            taps.note('тип сообщения MessageOrderStatusUpdated')
            taps.eq(message['store_id'], store.store_id, 'store_id')
            taps.eq(message['type'], order.type, 'type')
            taps.eq(message['order_id'], order.order_id, 'order_id')
            taps.eq(message['order_external_id'], order.external_id,
                    'order_external_id')
            taps.eq(message['lsn'], 0, 'lsn')
            taps.eq(message['status'], order.status, 'status')
            taps.eq(message['estatus'], order.estatus, 'estatus')
            taps.eq(message['eda_status'], order.eda_status, 'eda_status')
            taps.eq(message['source'], order.source, 'source')
            taps.eq(message['store_external_id'], store.external_id,
                    'store_external_id')
            taps.eq(message['company_id'], order.company_id, 'company_id')
            taps.eq(message['cluster_id'], store.cluster_id, 'cluster_id')
            taps.eq(message['supervisor_id'], None, 'supervisor_id')
            taps.eq(message['head_supervisor_id'], None, 'head_supervisor_id')
            taps.eq(message['user_id'], None, 'user_id')
            taps.eq(message['courier_id'], None, 'courier_id')
            taps.eq(message['total_pause'], 0, 'total_pause')
            taps.eq(message['items_count'], 0, 'items_count')
            taps.eq(message['items_uniq'], 0, 'items_uniq')

        await wait_order_status(order, ('approving', 'waiting'))
        with tap.subtest(1, 'Смена сабстатуса не триггерит сообщение') as taps:
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )
            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 0, 'Смена сабстатуса не триггерит сообщение')

        tap.ok(await order.approve(), 'Заказ подтвержден')
        with tap.subtest(1, 'Апрув не триггерит сообщение') as taps:
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )
            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 0, 'Апрув не триггерит сообщение')

        order.vars['total_pause'] = 32
        await order.save()
        await wait_order_status(order, ('request', 'waiting'))
        with tap.subtest(14, 'Сменился статус - отправили сообщение') as taps:
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )
            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 1, 'Сменился статус - отправили сообщение')
            _, messages = log[0]
            taps.eq(len(messages), 1, '1 сообщение')

            message: dict = messages[0]
            taps.note('тип сообщения MessageOrderStatusUpdated')
            taps.eq(message['store_id'], store.store_id, 'store_id')
            taps.eq(message['store_external_id'], store.external_id,
                    'store_external_id')
            taps.eq(message['type'], order.type, 'type')
            taps.eq(message['order_id'], order.order_id, 'order_id')
            taps.eq(message['order_external_id'], order.external_id,
                    'order_external_id')
            taps.ok(message['lsn'] > 0, 'lsn > 0')
            taps.ok(message['lsn'] < order.lsn, 'lsn')
            taps.eq(message['status'], 'request', 'status')
            taps.eq(message['estatus'], 'begin', 'estatus')
            taps.eq(message['eda_status'], order.eda_status, 'eda_status')
            taps.eq(message['user_id'], order.user_done, 'user_id')
            taps.eq(message['total_pause'], 32, 'total_pause')


async def test_courier_changed(tap, dataset, uuid, event_cache_lb):
    # pylint: disable=redefined-outer-name
    with tap.plan(2, 'Изменение курьера'):
        store = await dataset.store()
        order = await dataset.order(
            store_id=store.store_id,
            type='order',
            dispatch_delivery_type='taxi',
        )

        with tap.subtest(6, 'Пустой курьер') as taps:
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )

            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 1, '1 запись в логе')
            _, messages = log[0]
            taps.eq(len(messages), 1, '1 сообщение')

            message: dict = messages[0]
            taps.note('тип сообщения MessageOrderStatusUpdated')
            taps.eq(message['courier_id'], None, 'courier_id')
            taps.eq(message['courier_shift_id'], None, 'courier_shift_id')
            taps.eq(
                message['courier_delivery_type'],
                None,
                'courier_delivery_type'
            )
            taps.eq(
                message['dispatch_delivery_type'],
                order.dispatch_delivery_type,
                'dispatch_delivery_type'
            )

        courier = await dataset.courier(delivery_type='car')
        order.courier_id = courier.courier_id
        order.courier_shift_id = uuid()
        await order.save()

        with tap.subtest(6, 'Курьер изменился') as taps:
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )

            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 1, '1 запись в логе')
            _, messages = log[0]
            taps.eq(len(messages), 1, '1 сообщение')

            message: dict = messages[0]
            taps.note('тип сообщения MessageOrderStatusUpdated')
            taps.eq(message['courier_id'], courier.courier_id, 'courier_id')
            taps.eq(
                message['courier_shift_id'],
                order.courier_shift_id,
                'courier_shift_id'
            )
            taps.eq(
                message['courier_delivery_type'],
                courier.delivery_type,
                'courier_delivery_type'
            )
            taps.eq(
                message['dispatch_delivery_type'],
                order.dispatch_delivery_type,
                'dispatch_delivery_type'
            )


async def test_status_updated_asks(tap, dataset, event_cache_lb):
    # pylint: disable=redefined-outer-name, too-many-statements
    with tap.plan(3, 'Событие: изменение статуса заказа'):
        store = await dataset.store()
        executer = await dataset.user(store_id=store.store_id)
        order = await dataset.order(
            store_id=store.store_id,
            type='order',
            status='request',
            estatus='waiting',
        )

        with tap.subtest(2, 'При создании отправляем один ивент') as taps:
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )

            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 1, '1 запись в логе')
            _, messages = log[0]
            taps.eq(len(messages), 1, '1 сообщение')

        tap.ok(await order.ack(executer), 'Кладовщик взял заказ в работу')
        await order.business.order_changed()

        with tap.subtest(8, 'Отправляем ивент с юзером') as taps:
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )

            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 1, '1 запись в логе')
            _, messages = log[0]
            taps.eq(len(messages), 1, '1 сообщение')

            message: dict = messages[0]
            taps.note('тип сообщения MessageOrderStatusUpdated')
            taps.eq(message['type'], order.type, 'type')
            taps.eq(message['order_id'], order.order_id, 'order_id')
            taps.eq(message['status'], 'processing', 'status')
            taps.eq(message['estatus'], 'begin', 'estatus')
            taps.eq(message['eda_status'], order.eda_status, 'eda_status')
            taps.eq(message['user_id'], executer.user_id, 'user_id')


async def test_count(tap, dataset, uuid, event_cache_lb):
    # pylint: disable=redefined-outer-name, too-many-statements
    with tap.plan(1, 'Прокинем в событие количество SKU'):
        store = await dataset.store()
        order = await dataset.order(
            store=store,
            type='order',
            status='approving',
            estatus='begin',
            required=[
                {
                    'product_id': uuid(),
                    'count': 2
                },
                {
                    'product_id': uuid(),
                    'count': 3
                },
                {
                    'item_id': uuid(),
                    'count': 5
                },
            ],
        )

        with tap.subtest(4, 'Верное количество') as taps:
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )

            log = event_cache_lb.log('wms-order-status-updated')
            taps.eq(len(log), 1, '1 запись в логе')
            _, messages = log[0]
            taps.eq(len(messages), 1, '1 сообщение')

            message: dict = messages[0]
            taps.note('тип сообщения MessageOrderStatusUpdated')
            taps.eq(message['items_uniq'], 3, 'items_uniq')
            taps.eq(message['items_count'], 10, 'items_count')


async def test_suggests_count(
        tap, dataset, cfg, wait_order_status, event_cache_lb
):
    # pylint: disable=redefined-outer-name, too-many-statements
    # pylint: disable=too-many-locals
    with tap.plan(5, 'Прокинем в событие количество саджестов'):
        cfg.set('business.suggest.clear', False)
        messages_by_status = {}
        async def push_lb(order):
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )
            log = event_cache_lb.log('wms-order-status-updated')
            if not log:
                return

            _, messages = log[0]
            for m in messages:
                messages_by_status[(m['status'], m['estatus'])] = m
            return

        store = await dataset.store()
        executer = await dataset.user(store_id=store.store_id)
        product1 = await dataset.product()
        product2 = await dataset.product()
        await dataset.stock(product=product1, store=store, count=10)
        await dataset.stock(product=product2, store=store, count=20)
        order = await dataset.order(
            store=store,
            type='order',
            status='approving',
            estatus='begin',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1
                },
                {
                    'product_id': product2.product_id,
                    'count': 2
                },
            ],
        )

        await push_lb(order)
        await wait_order_status(order, ('approving', 'waiting'))
        await push_lb(order)
        await order.approve()
        await wait_order_status(order, ('request', 'waiting'))
        await push_lb(order)
        await order.ack(executer)
        await order.business.order_changed()
        await push_lb(order)
        await wait_order_status(order, ('processing', 'waiting'))
        await push_lb(order)
        suggests = await Suggest.list_by_order(order)
        for suggest in suggests:
            await suggest.done('done', user=executer)
        await order.done('complete', user=executer)
        await push_lb(order)
        await wait_order_status(order, ('complete', 'done'))
        await push_lb(order)

        with tap.subtest(4, 'suggests_count в разных статусах') as taps:
            taps.eq(
                messages_by_status[('request', 'begin')]['suggests_count'],
                0,
                'request - begin'
            )
            taps.eq(
                messages_by_status[('processing', 'begin')]['suggests_count'],
                0,
                'processing - begin'
            )
            taps.eq(
                messages_by_status[('processing', 'waiting')]['suggests_count'],
                2,
                'processing - waiting'
            )
            taps.eq(
                messages_by_status[('complete', 'begin')]['suggests_count'],
                0,
                'complete - begin'
            )


async def test_suggests_count_stowage(
        tap, dataset, cfg, wait_order_status, event_cache_lb
):
    # pylint: disable=redefined-outer-name, too-many-statements
    # pylint: disable=too-many-locals
    with tap.plan(3, 'Догенерация саджестов триггерит событие'):
        cfg.set('business.suggest.clear', False)
        messages_by_status = defaultdict(list)

        async def push_lb(order):
            await event_cache_lb.daemon_cycle(
                shard=order.shardno,
                ev_type='logbroker',
                conditions=[
                    ('tbl', 'orders'),
                    ('pk', order.order_id)
                ]
            )
            log = event_cache_lb.log('wms-order-status-updated')
            if not log:
                return

            _, messages = log[0]
            for m in messages:
                messages_by_status[(m['status'], m['estatus'])].append(m)
            return

        store = await dataset.full_store(options={'exp_chicken_run': True})
        user = await dataset.user(store=store)
        child_weights = [
            [0, 10],
            [10, 20],
            [20, 30]
        ]
        products = await dataset.weight_products(children=child_weights)
        for _ in range(5):
            await dataset.shelf(store=store)
        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': products[0].product_id,
                    'weight': 5000,
                    'count': 3,
                }
            ],
        )
        await push_lb(order)

        await wait_order_status(order, ('processing', 'waiting'))
        await push_lb(order)

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',
        )
        for s in suggests:
            await s.done(weight=20, count=3)
        await push_lb(order)

        tap.note('Догенерация саджестов')
        await wait_order_status(order, ('processing', 'waiting'))
        await push_lb(order)

        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',
        )
        for s in suggests:
            await s.done(weight=20, count=3)
        await push_lb(order)

        with tap.subtest(3, 'Несколько событий для waiting') as taps:
            messages = messages_by_status[('processing', 'waiting')]
            taps.eq(len(messages), 2, '2 раза были в processing waiting')
            taps.eq(
                messages[0]['suggests_count'],
                1,
                'В первом сообщении 1 событие'
            )
            taps.eq(
                messages[1]['suggests_count'],
                2,
                'Во втором сообщении 2 события'
            )
