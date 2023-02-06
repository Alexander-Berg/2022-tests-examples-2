import pytest
from stall.model.event_cache import EventCache, EventLB
from stall.model.logbroker.order_message import (
    OrderMessageApprove,
    OrderMessageProcessing,
    OrderMessageComplete,
)


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


async def test_wms_order_create(tap, dataset, event_cache_lb):
    # pylint: disable=redefined-outer-name
    with tap.plan(7, 'Событие: создание заказа'):
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

        log = event_cache_lb.log('wms-order-create')
        tap.eq(len(log), 1, '1 запись в логе')
        _, messages = log[0]
        tap.eq(len(messages), 1, '1 сообщение')

        message: dict = messages[0]
        tap.isa(message, dict,
                'тип сообщения OrderMessageCreate')
        tap.eq(message['store_id'], store.store_id, 'store_id')
        tap.eq(message['depot_id'], store.external_id, 'depot_id')
        tap.eq(message['order_id'], order.external_id, 'order_id')
        tap.eq(message['executer_id'], None, 'executer_id')


async def test_wms_order_approve(tap, dataset, wait_order_status,
                                 event_cache_lb):
    # pylint: disable=redefined-outer-name
    with tap.plan(9, 'Событие: Подтверждение от лавки'):
        store = await dataset.store()
        order = await dataset.order(
            store_id=store.store_id,
            type='order',
            status='approving',
            estatus='waiting',
        )
        tap.ok(await order.approve(), 'Заказ подтвержден')
        await wait_order_status(order, ('request', 'begin'))

        await event_cache_lb.daemon_cycle(
            shard=order.shardno,
            ev_type='logbroker',
            conditions=[
                ('tbl', 'orders'),
                ('pk', order.order_id)
            ]
        )

        log = event_cache_lb.log('wms-order-approve')
        tap.eq(len(log), 1, '1 запись в логе')
        _, messages = log[0]
        tap.eq(len(messages), 1, '1 сообщение')

        message: OrderMessageApprove = messages[0]
        tap.isa(message, dict,
                'тип сообщения OrderMessageApprove')
        tap.eq(message['store_id'], store.store_id, 'store_id')
        tap.eq(message['depot_id'], store.external_id, 'depot_id')
        tap.eq(message['order_id'], order.external_id, 'order_id')
        tap.eq(message['executer_id'], None, 'executer_id')


async def test_wms_order_processing(tap, dataset, wait_order_status,
                                    event_cache_lb):
    # pylint: disable=redefined-outer-name
    with tap.plan(9, 'Событие: Начало сборки заказа'):
        store = await dataset.store()
        executer = await dataset.user(store_id=store.store_id)
        order = await dataset.order(
            store_id=store.store_id,
            type='order',
            status='request',
            estatus='waiting',
        )

        tap.ok(await order.ack(executer), 'Кладовщик взял заказ в работу')
        await wait_order_status(order, ('processing', 'begin'))

        await event_cache_lb.daemon_cycle(
            shard=order.shardno,
            ev_type='logbroker',
            conditions=[
                ('tbl', 'orders'),
                ('pk', order.order_id)
            ]
        )

        log = event_cache_lb.log('wms-order-processing')
        tap.eq(len(log), 1, '1 запись в логе')
        _, messages = log[0]
        tap.eq(len(messages), 1, '1 сообщение')

        message: OrderMessageProcessing = messages[0]
        tap.isa(message, dict,
                'тип сообщения OrderMessageProcessing')
        tap.eq(message['store_id'], store.store_id, 'store_id')
        tap.eq(message['depot_id'], store.external_id, 'depot_id')
        tap.eq(message['order_id'], order.external_id, 'order_id')
        tap.eq(message['executer_id'], executer.user_id, 'executer_id')


async def test_wms_order_complete(tap, dataset, wait_order_status,
                                  event_cache_lb):
    # pylint: disable=redefined-outer-name
    with tap.plan(9, 'Событие: заказ собран'):
        store = await dataset.store()
        executer = await dataset.user(store_id=store.store_id)
        order = await dataset.order(
            store_id=store.store_id,
            type='order',
            status='processing',
            estatus='waiting',
        )

        tap.ok(await order.done('complete', user=executer), 'Завершение заказа')
        await wait_order_status(order, ('complete', 'done'))

        await event_cache_lb.daemon_cycle(
            shard=order.shardno,
            ev_type='logbroker',
            conditions=[
                ('tbl', 'orders'),
                ('pk', order.order_id)
            ]
        )

        log = event_cache_lb.log('wms-order-complete')
        tap.eq(len(log), 1, '1 запись в логе')
        _, messages = log[0]
        tap.eq(len(messages), 1, '1 сообщение')

        message: OrderMessageComplete = messages[0]
        tap.isa(message, dict,
                'тип сообщения OrderMessageComplete')
        tap.eq(message['store_id'], store.store_id, 'store_id')
        tap.eq(message['depot_id'], store.external_id, 'depot_id')
        tap.eq(message['order_id'], order.external_id, 'order_id')
        tap.eq(message['executer_id'], executer.user_id, 'executer_id')
