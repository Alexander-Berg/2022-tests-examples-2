import asyncio
import logging
import pytest

from log.base import LogQueueConsumer

logging.basicConfig(level=logging.DEBUG)


class DummyLogConsumer(LogQueueConsumer):
    def __init__(self, max_batch_size, write_seconds=0.1):
        super(DummyLogConsumer, self).__init__(max_batch_size)
        self.batches_written = []
        self.write_seconds = write_seconds

    async def write(self, batch):
        await asyncio.sleep(self.write_seconds)
        self.batches_written.append(len(batch))
        logging.info("%d records written", len(batch))


@pytest.mark.asyncio
async def test_service_scenario():
    dummy_consumer = DummyLogConsumer(max_batch_size=4)

    q1 = asyncio.Queue()

    task = asyncio.ensure_future(
        dummy_consumer.consume_queue(q1)
    )

    for i in range(10):
        await q1.put({"idx": i})

    logging.debug("join queue")
    await q1.join()
    for i in range(10):
        await q1.put({"idx": i + 10})

    task.cancel()

    logging.debug("join queue 2")
    await q1.join()
    logging.debug("wait consumer")
    await task

    assert dummy_consumer.batches_written == [4, 4, 2, 4, 4, 2]


@pytest.mark.asyncio
async def test_script_scenario():
    dummy_consumer = DummyLogConsumer(max_batch_size=100)
    q1 = asyncio.Queue(10)
    task = asyncio.ensure_future(
        dummy_consumer.consume_queue(q1)
    )
    for i in range(20):
        await q1.put({"idx": i})
    await q1.put(None)
    logging.debug("join queue")
    await q1.join()
    logging.debug("wait consumer")
    await task
    assert dummy_consumer.batches_written == [10, 10]

@pytest.mark.asyncio
async def test_extra_columns():
    dummy_consumer = DummyLogConsumer(max_batch_size=10)
    q1 = asyncio.Queue(10)
    task = asyncio.ensure_future(
        dummy_consumer.consume_queue(q1)
    )
    await q1.put({"idx": 0})
    await q1.put({"idx": 1})
    await q1.put({"idx": 2})
    await q1.put({"idx": 3, "extra": "some info"})
    await q1.put({"idx": 4})
    await q1.put({"idx": 5})
    await q1.put({"idx": 6})
    await q1.put(None)
    logging.debug("join queue")
    await q1.join()
    logging.debug("wait consumer")
    await task
    assert dummy_consumer.batches_written == [3, 1, 3]

@pytest.mark.asyncio
async def test_wrong_type():
    dummy_consumer = DummyLogConsumer(max_batch_size=10)
    q1 = asyncio.Queue(10)
    task = asyncio.ensure_future(
        dummy_consumer.consume_queue(q1)
    )
    await q1.put([1,2,3])
    logging.debug("join queue")
    await q1.join()
    logging.debug("wait consumer")
    await task
    assert dummy_consumer.batches_written == []
