import asyncio
import aiohttp
from aioresponses import aioresponses
import pytest
import logging
from logging import debug, info, error
import re

from channel.base import Push, AsyncSender, Batch, BatchSender


class DummyPush(Push):
    retry_period = 1
    retry_timeout = 2

    DEFAULTS = {
        "host": "default-host"
    }

    CHANNEL_PARAMS = ("deeplink",)

    def __init__(self, item_data):
        super(DummyPush, self).__init__(item_data, _id=item_data["idx"])

    def get_request_kwargs(self, push_id, **kwargs):
        text = kwargs.pop("text", "")
        return dict(method="POST", url="fake_url", json={"push_id": push_id,
                                                         "text": text})


class DummyBatch(Batch):
    retry_period = 1
    retry_timeout = 2

    def get_request_kwargs(self):
        return dict(method="POST", url="fake_url")


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


@pytest.fixture(autouse=True)
def dummy_push_cls_reset():
    try:
        yield
    finally:
        DummyPush.next_idx = 1


def verify_log_record(log_record, idx, status_code=200, **other):
    debug("verify idx %d log_record: %s", idx, log_record)
    error_reasons = {200: None, 500: "Internal Server Error"}
    # sent_dttm is a datetime
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d{1,6})?",
                    log_record["sent_dttm"])
    if status_code is not None:
        assert log_record["status_code"] == status_code
    error_reason = error_reasons.get(status_code)
    if error_reason is not None:
        assert log_record["error_reason"] == error_reason
    if other:
        for k, v in other.items():
            assert log_record[k] == v
    # input_data is logged
    assert log_record["idx"] == idx

def verify_push_log_record(log_record, idx, status_code=200, **other):
    verify_log_record(log_record, idx, status_code, **other)
    assert log_record["push_id"] == idx


class TestAsyncSender:
    test_data = [
        ([200], [200]),
        ([500, 200], [200]),
        ([500, 500], [500]),
        ([404], [404]),
        ([400], [400])
    ]

    @pytest.mark.parametrize("response_codes,log_records", test_data,
                             ids=["ok", "retry_ok", "retry_exceed", "not found", "bad request"])
    @pytest.mark.asyncio
    async def test_simple(self, mock_aioresponse, response_codes, log_records):
        log_queue = asyncio.Queue()
        send_queue = asyncio.Queue()
        await send_queue.put({"idx": 1})
        await send_queue.put(None)

        sender = AsyncSender(DummyPush, nworkers=1)

        for status in response_codes:
            mock_aioresponse.post("fake_url", status=status)

        await sender.send_from_queue(send_queue, log_queue)
        debug("send_from_queue complete")

        # class variable retry_period persists
        assert DummyPush.retry_period == 1

        for idx, status in enumerate(log_records, 1):
            log_record = await log_queue.get()
            verify_push_log_record(log_record, idx, status)

        assert None == await log_queue.get()

    @pytest.mark.asyncio
    async def test_send_error(self, mock_aioresponse, caplog):
        send_queue = asyncio.Queue()
        await send_queue.put({"idx": 0})
        log_queue = asyncio.Queue()

        sender = AsyncSender(DummyPush, nworkers=1)
        mock_aioresponse.post("fake_url", status=403,
                              payload={"error": {"text": "inner message"}})
        with pytest.raises(aiohttp.ClientResponseError) as exc_info:
            with caplog.at_level(logging.DEBUG):
                await sender.send_from_queue(send_queue, log_queue)
        assert exc_info.value.status == 403
        assert log_queue.empty()
        assert "inner message" in caplog.text

    @pytest.mark.asyncio
    async def test_cancel(self, mock_aioresponse):
        """Check that all pending futures are waited and logged when cancelled"""
        send_queue = asyncio.Queue(10)
        log_queue = asyncio.Queue(10)

        sender = AsyncSender(DummyPush, nworkers=10)

        send = asyncio.ensure_future(
            sender.send_from_queue(send_queue, log_queue)
        )

        for i in range(10):
            await send_queue.put({"idx": i})
            mock_aioresponse.post("fake_url", status=500)

        await send_queue.join()
        debug("send_queue = %d, futures_queue = %d, log_queue = %d",
              send_queue.qsize(), sender.futures_queue.qsize(), log_queue.qsize())
        assert sender.futures_queue.qsize() > 0
        send.cancel()

        with pytest.raises(asyncio.CancelledError):
            await send

        assert log_queue.qsize() == 10
        while not log_queue.empty():
            debug("log_record: %s", await log_queue.get())


class TestPush:
    def test_control_group(self):
        p = DummyPush({"idx": 1})
        log_record = p.get_log_record()
        verify_push_log_record(log_record, 1, status_code=None)

    def test_channel_params(self):
        p = DummyPush(dict(idx=1, text="какой-то текст", deeplink="deeeeplink"))
        log_record = p.get_log_record()
        verify_push_log_record(log_record, 1, status_code=None,
                          text="какой-то текст",
                          channel_params={"deeplink": "deeeeplink"})

    def test_configure(self):
        orig_params = dict(
            host=DummyPush.DEFAULTS["host"],
            retry_timeout=DummyPush.retry_timeout,
            retry_period=DummyPush.retry_period,
        )
        DummyPush.configure(host="custom-host", retry_timeout=100500,
                            retry_period=None)
        assert DummyPush.DEFAULTS["host"] == "custom-host"
        assert DummyPush.retry_timeout == 100500
        assert DummyPush.retry_period == orig_params["retry_period"]
        # revert
        DummyPush.configure(**orig_params)
        assert DummyPush.DEFAULTS["host"] == orig_params["host"]
        assert DummyPush.retry_timeout == orig_params["retry_timeout"]

class TestBatch:
    @pytest.mark.parametrize(
        "response_codes,n_items,bsize,result_codes",
        [
            ([200], 2, 10, [200]),
            ([500, 200], 2, 10, [200]),
            ([200, 500, 200, 200], 10, 4, [200, 200, 200]),
            ([404], 2, 10, [404]),
        ],
        ids=[
            "small_n",
            "retry_ok",
            "many_batches",
            "404"
        ]
    )
    @pytest.mark.asyncio
    async def test_scenario(
            self, mock_aioresponse,
            response_codes, n_items, bsize, result_codes
    ):
        log_queue = asyncio.Queue()
        send_queue = asyncio.Queue()
        for i in range(n_items):
            await send_queue.put({"idx": i})
        await send_queue.put(None)

        sender = BatchSender(DummyBatch, batch_size=bsize)

        for status in response_codes:
            mock_aioresponse.post("fake_url", status=status)

        await sender.send_from_queue(send_queue, log_queue)
        debug("send_from_queue complete")

        # class variable retry_period persists
        assert DummyBatch.retry_period == 1

        for idx in range(n_items):
            batch_number = idx // bsize
            result_code = result_codes[batch_number]
            log_record = await log_queue.get()
            verify_log_record(log_record, idx, result_code,
                              batch_number=batch_number)

        assert None == await log_queue.get()

    @pytest.mark.asyncio
    async def test_terminates(self, mock_aioresponse):
        for status in [500, 500]:
            mock_aioresponse.post("fake_url", status=status)
        send_queue = asyncio.Queue()
        for i in range(2):
            await send_queue.put({"idx": i})
        await send_queue.put(None)
        log_queue = asyncio.Queue()
        sender = BatchSender(DummyBatch, batch_size=10)
        with pytest.raises(TimeoutError):
            await sender.send_from_queue(send_queue, log_queue)
        assert log_queue.empty()
