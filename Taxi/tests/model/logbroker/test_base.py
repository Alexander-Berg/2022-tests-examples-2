import datetime
import json

from mouse import Has

from libstall.model import coerces
from stall.model.logbroker.base import (
    add_store_external_id,
    add_depot_id,
    change_order_id,
    add_courier_delivery_type,
    add_supervisor,
    count_suggests,
    PreprocessMessageError,
    DEFAULT_TTL,
)
from stall.model.logbroker.base import TopicMessageBase
from stall.model.event_cache import EventLB


async def test_add_store_external_id(tap, dataset):
    with tap.plan(2, 'Получение external_id для лавки'):
        store = await dataset.store()
        event = await add_store_external_id({
            'store_id': store.store_id
        })

        tap.eq(event['store_id'], store.store_id, 'store_id')
        tap.eq(event['store_external_id'], store.external_id,
               'store_external_id')


async def test_add_depot_id(tap, dataset):
    with tap.plan(2, 'Получение external_id для лавки'):
        store = await dataset.store()
        event = await add_depot_id({
            'store_id': store.store_id
        })

        tap.eq(event['store_id'], store.store_id, 'store_id')
        tap.eq(event['depot_id'], store.external_id, 'depot_id')


async def test_add_courier_delivery_type(tap, dataset):
    with tap.plan(2, 'Получение типа доставки у курьера'):
        courier = await dataset.courier(
            delivery_type='yandex_taxi_remote'
        )
        event = await add_courier_delivery_type({
            'courier_id': courier.courier_id
        })

        tap.eq(event['courier_id'], courier.courier_id, 'courier_id')
        tap.eq(
            event['courier_delivery_type'],
            courier.delivery_type,
            'courier_delivery_type'
        )


async def test_add_delivery_type_fail(tap):
    with tap.plan(1, 'Нет курьера - нет типа доставки'):
        event = await add_courier_delivery_type({})
        tap.not_in_ok(
            'courier_delivery_type',
            event,
            'no courier_delivery_type'
        )


async def test_add_store_external_id_fail(tap, uuid):
    with tap.plan(1, 'Получение external_id для лавки'):
        with tap.raises(PreprocessMessageError, 'Неизвестная лавка'):
            await add_store_external_id({
                'store_id': uuid()
            })


async def test_change_order_id(tap, dataset):
    with tap.plan(1, 'Замена order_id на external'):
        order = await dataset.order()
        event = await change_order_id({
            'order_id': order.order_id,
            'order_external_id': order.external_id,
        })

        tap.eq(event['order_id'], order.external_id, 'order_id')


async def test_suggests_count(tap, dataset):
    with tap.plan(1, 'Количество саджестов в документе'):
        store = await dataset.store()
        order = await dataset.order(
            status='processing',
            estatus='begin',
            store=store
        )

        for x in range(3):
            await dataset.suggest(order, suggest_order=10 - x)

        event = await count_suggests({
            'order_id': order.order_id,
            'status': order.status,
            'estatus': order.estatus,
        })
        tap.eq(event['suggests_count'], 3, 'Саджесты посчитаны')


async def test_change_order_id_fail(tap, dataset):
    with tap.plan(1, 'Замена order_id на external'):
        order = await dataset.order()
        with tap.raises(PreprocessMessageError, 'Нет внешнего ид заказа'):
            await change_order_id({
                'order_id': order.order_id,
            })


async def test_create_topic_message(tap):
    with tap.plan(4, 'Создание сообщения для топика'):
        class TopicMessage(TopicMessageBase):
            topic = 'test-topic'
            attr1 = Has(types=str, required=True)
            attr2 = Has(types=str, required=True)

        message = TopicMessage(
            attr1='first',
            attr2='second'
        )

        tap.isa(message, TopicMessage, 'Верный тип')
        tap.eq(message.topic, 'test-topic', 'topic')
        tap.eq(message.attr1, 'first', 'attr1')
        tap.eq(message.attr2, 'second', 'attr2')


async def test_create_event_lb(tap):
    with tap.plan(2, 'Создание ивента для сохранения в бд'):
        message = TopicMessageBase()
        event = EventLB.create(message)
        tap.eq(
            event.topic_class,
            'stall.model.logbroker.base.TopicMessageBase',
            'topic'
        )
        tap.eq(event.data, message, 'data')


async def test_event_lb_push(tap):
    with tap.plan(4, 'Создание сообщения в топик из ивента'):
        class WriterMock():
            def __init__(self):
                self.log = []

            async def write_messages(self, topic, messages):
                self.log.append((topic, messages))

        class EventLBMock(EventLB):
            writer = WriterMock()

        event = EventLBMock.create(TopicMessageBase())
        await EventLBMock.push([event.pure_python()])

        tap.eq(len(EventLBMock.writer.log), 1, '1 запись в логе')
        topic, messages = EventLBMock.writer.log[0]
        tap.eq(topic, 'undefined', 'topic')

        tap.eq(len(messages), 1, '1 сообщение')
        tap.eq(messages[0], {}, 'topic')


async def test_message_serialize(tap, now, tzone):
    with tap.plan(4, 'Сериализация сообщения'):

        class TopicMessage(TopicMessageBase):
            timestamp = Has(
                types=datetime.datetime,
                required=True,
                coerce=coerces.date_time
            )

        event_time = now(tz=tzone('UTC')).replace(2021, 6, 5, 4, 3, 2, 1)
        message = TopicMessage(timestamp=event_time)
        tap.isa(message, TopicMessage, 'тип сообщения TopicMessage')
        tap.eq(message.timestamp, event_time, 'timestamp')

        serialized = await message.serialize()
        tap.eq(serialized['timestamp'], '2021-06-05T04:03:02+00:00',
               'timestamp')
        tap.ok(json.dumps(serialized), 'Сериализовано')


async def test_no_supervisor(tap, dataset):
    with tap.plan(2, 'У лавки нет супервайзера'):
        store = await dataset.store()
        event = await add_supervisor({
            'store_id': store.store_id
        })

        tap.eq(event['supervisor_id'], None, 'supervisor_id')
        tap.eq(event['head_supervisor_id'], None, 'head_supervisor_id')


async def test_add_supervisor(tap, dataset):
    with tap.plan(2, 'Получение supervisor_id для лавки'):
        store = await dataset.store()
        supervisor = await dataset.user(
            role='supervisor',
            store=store,
            stores_allow=[store.store_id]
        )
        event = await add_supervisor({
            'store_id': store.store_id
        })

        tap.eq(event['supervisor_id'], supervisor.user_id, 'supervisor_id')
        tap.eq(event['head_supervisor_id'], None, 'head_supervisor_id')


async def test_add_supervisor_and_head(tap, dataset):
    with tap.plan(2, 'Получение supervisor_id для лавки'):
        store = await dataset.store()
        supervisor = await dataset.user(
            role='supervisor',
            store=store,
            stores_allow=[store.store_id]
        )
        head_supervisor = await dataset.user(
            role='head_supervisor',
            store=store,
            stores_allow=[store.store_id]
        )
        event = await add_supervisor({
            'store_id': store.store_id
        })

        tap.eq(event['supervisor_id'], supervisor.user_id, 'supervisor_id')
        tap.eq(
            event['head_supervisor_id'],
            head_supervisor.user_id,
            'head_supervisor_id'
        )


async def test_add_only_head_supervisor(tap, dataset):
    with tap.plan(2, 'Получение supervisor_id для лавки'):
        store = await dataset.store()
        head_supervisor = await dataset.user(
            role='head_supervisor',
            store=store,
            stores_allow=[store.store_id]
        )
        event = await add_supervisor({
            'store_id': store.store_id
        })

        tap.eq(
            event['supervisor_id'],
            head_supervisor.user_id,
            'supervisor_id'
        )
        tap.eq(
            event['head_supervisor_id'],
            head_supervisor.user_id,
            'head_supervisor_id'
        )


async def test_add_supervisor_ttl(tap, dataset, time_mock):
    with tap.plan(5, 'Получение supervisor_id для лавки'):
        time_mock.set(
            round(time_mock.now().timestamp() / DEFAULT_TTL) * DEFAULT_TTL
        )
        store = await dataset.store()
        supervisor = await dataset.user(
            role='supervisor',
            store=store,
            stores_allow=[store.store_id]
        )
        event = await add_supervisor({
            'store_id': store.store_id
        })

        tap.eq(event['supervisor_id'], supervisor.user_id, 'supervisor_id')
        tap.eq(event['head_supervisor_id'], None, 'head_supervisor_id')

        supervisor.stores_allow = []
        tap.ok(await supervisor.save(), 'Удалим супервайзера')
        tap.note('Поспим половину ttl')
        time_mock.sleep(seconds=DEFAULT_TTL // 2)

        event = await add_supervisor({
            'store_id': store.store_id
        })
        tap.eq(
            event['supervisor_id'], supervisor.user_id, 'same supervisor_id'
        )

        tap.note('Поспим ttl')
        time_mock.sleep(seconds=DEFAULT_TTL + 1)

        event = await add_supervisor({
            'store_id': store.store_id
        })
        tap.eq(event['supervisor_id'], None, 'new supervisor_id')
