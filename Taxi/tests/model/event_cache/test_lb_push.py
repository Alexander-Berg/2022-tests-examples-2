import asyncio
from concurrent.futures import Future
import kikimr.public.sdk.python.persqueue.grpc_pq_streaming_api as pqlib

from stall.logbroker import CreateProducerTimeoutError
from stall.model.logbroker.base import TopicMessageBase
from stall.model.event_cache import EventLB


async def test_push_fail_create_producer(tap, monkeypatch, setup_topic):
    # pylint: disable=protected-access
    with tap.plan(4, 'Обработка ошибки создания producer при пуше'):
        target = await setup_topic('t/ec_1')

        monkeypatch.setattr(TopicMessageBase.topic, 'default', lambda: target)
        event = EventLB.create(TopicMessageBase())

        __create_future = Future()
        async def response():
            await asyncio.sleep(6)
            __create_future.set_result(True)

        def start(self):
            # pylint: disable=unused-argument
            return __create_future
        monkeypatch.setattr(pqlib.PQStreamingProducer, 'start', start)

        tap.ok(
            await EventLB.writer.api(target),
            'принудительно создадим grpc'
        )
        tap.eq(len(EventLB.writer._api), 1, '1 Объект grpc')

        asyncio.create_task(response())
        with tap.raises(CreateProducerTimeoutError):
            await EventLB.push([event.pure_python()])

        tap.eq(
            len(EventLB.writer._api),
            0,
            'При ошибке CreateProducerTimeoutError - убиваем grpc'
        )


async def test_push_fail_on_write(tap, monkeypatch, setup_topic):
    # pylint: disable=protected-access
    with tap.plan(4, 'Обработка ошибки записи при пуше'):
        target = await setup_topic('t/ec_2')

        monkeypatch.setattr(TopicMessageBase.topic, 'default', lambda: target)
        event = EventLB.create(TopicMessageBase())

        class ErrorForTest(Exception):
            pass

        __write_future = Future()
        async def response():
            await asyncio.sleep(0.1)
            __write_future.set_exception(ErrorForTest())

        def write(*args, **kwargs):
            # pylint: disable=unused-argument
            return __write_future
        monkeypatch.setattr(pqlib.PQStreamingProducer, 'write', write)

        tap.ok(
            await EventLB.writer.api(target),
            'принудительно создадим grpc'
        )
        tap.eq(len(EventLB.writer._api), 1, '1 Объект grpc')

        asyncio.create_task(response())
        with tap.raises(ErrorForTest):
            await EventLB.push([event.pure_python()])

        tap.eq(
            len(EventLB.writer._api),
            1,
            'Если ошибка не CreateProducerTimeoutError, то оставим grpc'
        )

