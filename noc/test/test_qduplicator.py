import asyncio
import pytest

from noc.grad.grad.lib.qduplicator import QDuplicator, AnyQueue
from typing import Dict, Any, List
from asyncio import Queue


class QDuplicatorControl:
    def __init__(self, cb):
        self.cb = cb

    def __call__(self, q_dup: QDuplicator):
        self.cb(q_dup)


async def qdup_run(q_dup: QDuplicator, in_data: List):
    per_q_data: Dict[AnyQueue, List[Any]] = {}
    qdup_runner = asyncio.ensure_future(q_dup.run())
    for item in in_data:
        if isinstance(item, QDuplicatorControl):
            await asyncio.sleep(0.01)  # time to process queue
            item(q_dup)
        else:
            await q_dup.source_queue.put(item)
    q_dup.source_queue.put_nowait(None)
    await qdup_runner
    for dst_q in q_dup.dst_queues:
        per_q_data[dst_q] = []
        while True:
            try:
                elem = dst_q.get_nowait()
                per_q_data[dst_q].append(elem)
            except asyncio.queues.QueueEmpty:
                break
    return per_q_data


def qdup(q_dup: QDuplicator, in_data: List) -> Dict[Queue, List]:
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(qdup_run(q_dup, in_data))
    return res


def make_qdup():
    q_dup = QDuplicator(Queue(), copy=True)
    return q_dup


def test_simple():
    q_dup = make_qdup()
    queue = q_dup.make_q(maxsize=1_000, name="testq")
    per_q_data = qdup(q_dup, [("test_exchange", "test_channel", "test_elem1", 12345)])
    assert per_q_data == {queue: [("test_exchange", "test_channel", "test_elem1", 12345)]}


PARALLEL_CASES = [[3, 5], [5, 30], [4, 120]]


@pytest.mark.parametrize("queue_count, data_count", PARALLEL_CASES)
def test_parallel(queue_count, data_count):
    q_dup = make_qdup()
    for i in range(queue_count):
        q_dup.make_q(maxsize=1_000, name="testq")

    in_data = []
    for i in range(data_count):
        in_data.append(("test_exchange", "test_channel", "test_elem%s" % i, 12345))
    per_q_data = qdup(q_dup, in_data)
    out_data = [e for d in per_q_data.values() for e in d]
    out_data.sort(key=lambda x: x[2])
    in_data.sort(key=lambda x: x[2])
    assert in_data == out_data
    elements_len = [len(e) for e in per_q_data.values()]
    assert max(elements_len) - min(elements_len) <= 1, "distribution is not fair"


def test_filter():
    q_dup = make_qdup()
    q1 = q_dup.make_q(maxsize=1_000, name="testq1")
    q2 = q_dup.make_q(maxsize=1_000, name="testq2", channel="test_channel")
    q3 = q_dup.make_q(maxsize=1_000, name="testq3", channel=("test_channel2", "test_channel3"))
    in_data = [
        ("test_exchange", "test_channel", "test_elem1", 12345),
        ("test_exchange", "test_channel2", "test_elem1", 12345),
        ("test_exchange", "test_channel3", "test_elem1", 12345),
    ]
    per_q_data = qdup(q_dup, in_data)

    assert per_q_data[q1] == [
        ("test_exchange", "test_channel", "test_elem1", 12345),
        ("test_exchange", "test_channel2", "test_elem1", 12345),
        ("test_exchange", "test_channel3", "test_elem1", 12345),
    ]
    assert per_q_data[q2] == [("test_exchange", "test_channel", "test_elem1", 12345)]
    assert per_q_data[q3] == [
        ("test_exchange", "test_channel2", "test_elem1", 12345),
        ("test_exchange", "test_channel3", "test_elem1", 12345),
    ]


def test_rebuild_q_filter():
    q_dup = make_qdup()
    q1 = q_dup.make_q(maxsize=1_000, name="testq1")
    in_data = [
        ("test_exchange", "test_channel", "test_elem1", 12345),
        QDuplicatorControl(lambda q_dup: q_dup.rebuild_q_filter(q1, channel="test_channel1")),
        ("test_exchange", "test_channel1", "test_elem2", 12345),
        ("test_exchange", "test_channel2", "test_elem3", 12345),
        QDuplicatorControl(lambda q_dup: q_dup.rebuild_q_filter(q1, channel=None)),
        ("test_exchange", "test_channel_any", "test_elem4", 12345),
    ]

    per_q_data = qdup(q_dup, in_data)
    assert per_q_data[q1] == [
        ("test_exchange", "test_channel", "test_elem1", 12345),
        ("test_exchange", "test_channel1", "test_elem2", 12345),
        ("test_exchange", "test_channel_any", "test_elem4", 12345),
    ]
