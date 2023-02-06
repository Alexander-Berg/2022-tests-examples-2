# pylint: disable=invalid-name, no-self-use, protected-access
import concurrent.futures

import pytest

from chatterbox.internal import logbroker


_MESSAGES = b'msg_pt1_%d'


@pytest.mark.parametrize(
    ('expected_retries', 'is_success'), [(4, True), (5, False)],
)
async def test_logbroker_write_error(
        cbox, monkeypatch, expected_retries, is_success,
):
    sent = []

    class _DummyProducer:
        retries = 0

        def __new__(cls):
            if not hasattr(cls, 'instance'):
                cls.instance = super(_DummyProducer, cls).__new__(cls)
            return cls.instance

        def start(self):
            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            return future

        def __init__(self):
            self._to_send = []

        def stop(self):
            pass

        def write(self, seq_no, message):
            if self.retries < expected_retries:
                self.retries += 1
                raise logbroker.ProducerError

            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            sent.append(message)
            return future

    class _DummyApi:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result('start result')
            return future

        def create_retrying_producer(self, *args, **kwargs):
            return _DummyProducer()

    async def _create_api(*args, **kwargs):
        return _DummyApi

    monkeypatch.setattr(
        logbroker.LogbrokerAsyncWrapper, '_create_api', _create_api,
    )

    lb = logbroker.LogbrokerAsyncWrapper(cbox.app.tvm)
    if is_success:
        await lb.write(_MESSAGES, '', b'', max_tries=5, retry_timeout=0)
        assert sent == [_MESSAGES]
    else:
        with pytest.raises(logbroker.ProducerError):
            await lb.write(_MESSAGES, '', b'', max_tries=5, retry_timeout=0)
        assert not sent


async def test_logbroker_async_wrapper(cbox, monkeypatch):
    sent = []

    class _DummyProducer:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            return future

        def __init__(self):
            self._to_send = []

        def stop(self):
            pass

        def write(self, seq_no, message):
            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            sent.append(message)
            return future

    class _DummyApi:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result('start result')
            return future

        def create_retrying_producer(self, *args, **kwargs):
            return _DummyProducer()

    async def _create_api(*args, **kwargs):
        return _DummyApi

    monkeypatch.setattr(
        logbroker.LogbrokerAsyncWrapper, '_create_api', _create_api,
    )

    lb = logbroker.LogbrokerAsyncWrapper(cbox.app.tvm)
    await lb.write(_MESSAGES, '', b'', 1)
    assert sent == [_MESSAGES]

    sent = []

    await lb.write(_MESSAGES, '', b'', 2)
    assert sent == [_MESSAGES]


class _DummyFutureResult:
    @staticmethod
    def HasField(field):
        return True

    class init:
        max_seq_no = 0
