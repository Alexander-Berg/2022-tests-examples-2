import asyncio
import time
import logging
import pytest

from noc.grad.grad.lib.grad_client import DumpPusher
from noc.grad.grad.lib.qduplicator import MPQueueWrapper

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s"
)

TEST_ROUTING_KEY = "routing.key"
TEST_SERIES_CONF = {
    TEST_ROUTING_KEY: {"min_interval": 60, "keys": ("host", "index"), "values": ("value",), "client": {None: {}}}
}


async def _async_pusher_runner(pusher, q, in_data):
    asyncio.ensure_future(pusher.loop())
    last = None
    for i in in_data:
        q.put_nowait(i)
        last = i
    pusher._end = tuple(last[2][-1])

    await asyncio.sleep(pusher.chunk_max_duration)
    for i in range(pusher.chunk_max_duration * 100):
        if pusher._collector_task.cancelled():
            break
        await asyncio.sleep(0.1)


class DumpPusherCallBack:
    def __init__(self):
        self.result = []

    def __call__(self, url, data, headers, series):
        self.result.append((url, data, headers, series))

    def get_data(self):
        ret = []
        for item in self.result:
            for data in item[1]:
                ret.append((item[3], *data))
        return ret

    def get_data_chunks(self):
        ret = []
        for item in self.result:
            tmp = []
            for data in item[1]:
                tmp.append((item[3], *data))
            ret.append(tmp)
        return ret


def test_dump_pusher():
    q = MPQueueWrapper()

    in_data = []
    expected_data = []
    ts = int(time.time()) - 200
    keys = {"host": "testhost", "index": "testindex"}
    values = {"value": 0}

    cb = DumpPusherCallBack()
    pusher = DumpPusher(q, TEST_SERIES_CONF, max_metrics=100, cb=cb)

    for i in range(100):
        data_ts = ts + i
        in_data.append(("exchange", TEST_ROUTING_KEY, [[data_ts, keys.copy(), values.copy()]], 12345))
        expected_data.append((TEST_ROUTING_KEY, data_ts, keys.copy(), values.copy()))

    asyncio.get_event_loop().run_until_complete(_async_pusher_runner(pusher, q, in_data))
    out_data = cb.get_data()
    assert out_data == expected_data


def _test_dump_pusher_s_precision():
    q = MPQueueWrapper()
    in_data = []
    expected_data = []
    ts = int(time.time()) - 200
    keys = {"host": "testhost", "index": "testindex"}
    values = {"value": 0}

    cb = DumpPusherCallBack()
    pusher = DumpPusher(q, TEST_SERIES_CONF, max_metrics=100, cb=cb)
    pusher.precision = "s"

    for i in range(100):
        data_ts = ts + i
        in_ts = data_ts
        if i > 50:
            in_ts *= 1000
        in_data.append(("exchange", TEST_ROUTING_KEY, [[in_ts, keys.copy(), values.copy()]]))
        expected_data.append((TEST_ROUTING_KEY, data_ts, keys.copy(), values.copy()))

    asyncio.get_event_loop().run_until_complete(_async_pusher_runner(pusher, q, in_data))
    out_data = cb.get_data()
    assert out_data == expected_data


def _test_dump_pusher_ms_precision():
    q = MPQueueWrapper()
    in_data = []
    expected_data = []
    ts = int(time.time()) - 200
    keys = {"host": "testhost", "index": "testindex"}
    values = {"value": 0}

    cb = DumpPusherCallBack()
    pusher = DumpPusher(q, TEST_SERIES_CONF, max_metrics=100, cb=cb)
    pusher.precision = "ms"

    for i in range(100):
        data_ts = ts + i
        in_ts = data_ts
        if i > 50:
            in_ts *= 1000
        in_data.append(("exchange", TEST_ROUTING_KEY, [[in_ts, keys.copy(), values.copy()]], 12345))
        expected_data.append((TEST_ROUTING_KEY, data_ts * 1000, keys.copy(), values.copy()))

    asyncio.get_event_loop().run_until_complete(_async_pusher_runner(pusher, q, in_data))
    out_data = cb.get_data()
    assert out_data == expected_data


MAX_METRICS_CASES = [
    [2, 2, 1, 10],
    [20, 20, 1, 10],
    [11, 11, 8, 10],
    [271, 271, 8, 10],
    [40, 30, 10, 21],
    [159, 1230, 5, 100],
    [1, 1, 9, 10],
]
# import random
# for _ in range(100):
#     MAX_METRICS_CASES.append([int(random.uniform(1, 300)),
#                               int(random.uniform(1, 300)),
#                               int(random.uniform(1, 9))])


@pytest.mark.parametrize("chunks_count, per_chunk_count, values_count, max_metrics", MAX_METRICS_CASES)
def test_dump_pusher_max_metrics(chunks_count, per_chunk_count, values_count, max_metrics):
    q = MPQueueWrapper()
    in_data = []
    expected_data = []
    ts = int(time.time()) - 2000
    keys = {"host": "testhost", "index": "testindex"}
    values = {"value%s" % i: 0 for i in range(values_count)}
    assert values_count <= max_metrics  # not realized
    series_conf = TEST_SERIES_CONF.copy()
    series_conf[TEST_ROUTING_KEY]["values"] = ["value%s" % i for i in range(values_count)]

    for i in range(chunks_count):
        data_ts = ts + i
        tmp_data = []
        tmp_data_exp = []
        for key_val in range(per_chunk_count):
            new_keys = keys.copy()
            new_keys["index"] = "testindex%s" % key_val
            tmp_data.append([data_ts, new_keys, values.copy()])
            tmp_data_exp.append((TEST_ROUTING_KEY, data_ts, new_keys.copy(), values.copy()))

        in_data.append(("exchange", TEST_ROUTING_KEY, tmp_data, 12345))
        expected_data += tmp_data_exp

    cb = DumpPusherCallBack()
    pusher = DumpPusher(q, series_conf, max_metrics=max_metrics, cb=cb)
    pusher.send_q = asyncio.Queue(maxsize=len(expected_data) * 2)
    pusher.chunk_max_duration = 1

    asyncio.get_event_loop().run_until_complete(_async_pusher_runner(pusher, q, in_data))
    out_data = cb.get_data()
    out_data_chunks = cb.get_data_chunks()
    for i in range(len(out_data_chunks)):
        out_data_chunk = out_data_chunks[i]
        metrics_count = sum(len(item[3]) for item in out_data_chunk)
        assert metrics_count <= max_metrics
        # if i < len(out_data_chunks) - 1:  # except last
        #     assert len(out_data_chunk) > max_metrics - 1
    assert out_data == expected_data
